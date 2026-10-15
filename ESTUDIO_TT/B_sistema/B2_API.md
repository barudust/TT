# B2 — La API (backend)

> **Resumen.** Servicio web en **Flask** (Python) que, al arrancar y cada día
> hábil a las 16:30 de Nueva York, descarga datos reales de Yahoo Finance,
> calcula las 76 variables, corre la Regresión Logística, compara cada
> señal con lo que pasó el día siguiente, calcula métricas de 30/60/90 días,
> guarda todo en SQLite y lo sirve en JSON. Todo lo que responde sale del
> modelo o de datos reales; los endpoints de escritura manual están
> desactivados. Tiene 24 pruebas automáticas.
>
> Código: `api/main.py`, `api/ml/` (`features.py`, `model.py`,
> `target.py`), `api/database.py`, `api/models.py`, `api/db_ops.py`,
> `api/wsgi.py`. Documentación técnica: `docs/API.md`,
> `docs/API_FRONTEND_METRICS.md`, `docs/MODEL_INTEGRATION.md`.

---

## 1. Tecnologías y por qué

| Tecnología | Para qué | Por qué |
|---|---|---|
| **Flask 3** | Framework web | Mínimo y suficiente para una API de lectura con ~10 rutas; sin piezas que no se usan |
| **flask-cors** | Permitir que el frontend (otro dominio) llame a la API | El frontend y la API están en servicios distintos de Render |
| **yfinance** | Descargar precios | Misma fuente que el entrenamiento |
| **pandas / numpy** | Calcular variables | Mismo código que la investigación |
| **scikit-learn 1.7.2** | Cargar y correr el modelo; F1 | Misma versión con la que se entrenó (un `.pkl` puede no cargar en otra versión) |
| **SQLAlchemy 2** | Base de datos (ORM) | Código independiente del motor: SQLite hoy, PostgreSQL si hace falta |
| **APScheduler** | Tareas programadas | Actualización diaria y reintentos dentro del mismo proceso |
| **gunicorn** | Servidor de producción | El servidor de desarrollo de Flask no es para producción |
| **tzdata / zoneinfo** | Hora de Nueva York con horario de verano | El mercado se rige por hora de NY |
| **pytest** | Pruebas | Estándar en Python |

---

## 2. Endpoints

Todas las respuestas tienen la forma `{"success": true, "data": ...}` o
`{"success": false, "error": "..."}`.

### 2.1 Lectura

| Método y ruta | Devuelve |
|---|---|
| `GET /health` | `status: ok`, `stocksLoaded` y `stocksExpected` (cuántas acciones hay cargadas de 7). Render lo usa para saber si el servicio vive |
| `GET /model` | Ficha del modelo **leída del `.pkl`**: versión, algoritmo, penalización, C, pesos de clase, escalador, número de variables, rango y tamaño del entrenamiento; y la definición de la etiqueta (horizonte 1, percentiles 30/70, ventana 252) |
| `GET /market-status` | Si NYSE está abierto, si hoy es día hábil (con feriados 2026–2027), hora de NY y horario de actualización |
| `GET /stocks` | Las 7 acciones con precio, señal para el siguiente día hábil, confianza, las 3 probabilidades, fecha del cierre usado y hora de cálculo |
| `GET /stocks/:symbol` | Lo anterior + las últimas 10 señales con su resultado real + datos de la empresa |
| `GET /stocks/:symbol/history?days=30\|60\|90` | Una fila por día: OHLCV, predicción, confianza, probabilidades, señal real, retorno siguiente, acierto |
| `GET /stocks/:symbol/metrics?days=30\|60\|90` | Métricas de la ventana para una acción |
| `GET /metrics?days=30\|60\|90` | Métricas de las 7 acciones |
| `GET /stocks/:symbol/info` | Datos de la empresa (sector, capitalización, beta…) |

### 2.2 Escritura

| Método y ruta | Estado |
|---|---|
| `POST /admin/refresh` | Activo: fuerza la recarga completa sin reiniciar |
| `POST /stocks`, `POST /stocks/:symbol`, `.../history`, `.../metrics`, `.../signals` | **Desactivados (403)**. Permitirían escribir valores que no salen del modelo. Solo se activan con `ENABLE_MANUAL_OVERRIDES=1` para pruebas locales, y lo que escriben queda marcado `model_version="manual-override"` |

### 2.3 ¿Por qué REST y JSON?

Es el estándar para que un frontend web consuma datos: sin estado entre
peticiones, cacheable, fácil de probar con el navegador o `curl`, y
cualquier cliente (web, móvil) lo entiende.

---

## 3. El ciclo de actualización (`initialize_data`)

```
database.init_db()                    crea tablas si no existen
load_model()                          carga el .pkl (una sola vez, en caché)
descargar SPY y VIX (3 años)          con reintentos
para cada una de las 7 acciones:
    descargar OHLCV (3 años)          con reintentos; sin la vela en curso
    build_feature_frame()             61 + 15 = 76 variables
    model.predict_frame()             3 probabilidades por día
    etiquetas_reales()                qué pasó realmente el día siguiente
    rows_from_predictions()           une todo, marca aciertos o "pendiente"
    generate_metrics() × 3            ventanas 30, 60, 90
    guardar en memoria                STOCKS_DATA, HISTORICAL_DATA, METRICS_DATA…
    persist_to_db()                   upsert en SQLite
```

**Cuándo corre:**

1. Al arrancar el servidor (`wsgi.py` lo llama antes de servir).
2. Lunes a viernes a las **16:30 hora de Nueva York** (NYSE cierra a las
   16:00; se dejan 30 min para que Yahoo publique).
3. **Cada 2 minutos si falta alguna acción** (por ejemplo, si Yahoo falló
   en el arranque).
4. Con `POST /admin/refresh`.

Un candado (`threading.Lock`) evita que dos actualizaciones corran al mismo
tiempo.

### 3.1 Por qué se recalcula toda la ventana y no solo el día nuevo

- Cuesta segundos.
- Garantiza que todo lo que se muestra salió del **modelo actual**: si se
  reentrena, la historia se recalcula sola.
- Hace que la base sea reconstruible en cualquier momento.

### 3.2 Manejo de fallas

| Falla | Qué hace la API |
|---|---|
| Yahoo falla una vez | Reintenta 3 veces con 5 s de espera |
| Falla una acción | Se omite esa acción; **no se inventan datos** |
| Falla SPY/VIX | Se omiten todas (sin contexto de mercado no hay variables válidas) |
| Quedan acciones faltantes | El programador reintenta cada 2 minutos hasta completar las 7 |
| Falla la base de datos | Se revierte la transacción de esa acción; la API sigue sirviendo desde memoria |

---

## 4. El modelo dentro de la API

### 4.1 `ml/features.py`

Copia exacta de las fórmulas del entrenamiento. Agrega las 15 interacciones
leyendo los pares de `artifacts/interaction_pairs.json` (fuente única de
verdad). Descarta las filas iniciales sin historia suficiente.

### 4.2 `ml/model.py`

- Carga el `.pkl` **una sola vez** y lo deja en memoria.
- Verifica que el `.pkl` tenga todas las variables esperadas; si no, falla
  al arrancar (mejor fallar que predecir con datos incompletos).
- `predict_row`: escala con el escalador guardado → `predict_proba` →
  argmax → señal, confianza y las 3 probabilidades.
- `describe()`: arma la ficha de `GET /model` a partir de los metadatos del
  `.pkl`, no de texto fijo.
- `MODEL_VERSION = "LR-v8-interactions-holdw090"`: una prueba exige que
  coincida con el `.pkl`, para no servir un modelo con la etiqueta de otro.

### 4.3 `ml/target.py`

La etiqueta real de cada día con **la misma definición del entrenamiento**
(percentiles 30/70 de 252 días, `shift(1)`). Un día sin cierre siguiente o
sin historia suficiente queda como `None` ("pendiente"). Una prueba
verifica que coincide al 100 % con la etiqueta del dataset.

---

## 5. Las métricas que calcula (`generate_metrics`)

Misma metodología que la tesis, sobre los días cuyo resultado ya se
conoce:

| Métrica | Definición en la API |
|---|---|
| Exactitud y F1 por clase / F1-macro | Contra la etiqueta real (scikit-learn) |
| Retorno acumulado de la estrategia | COMPRAR +r, VENDER −r, MANTENER 0, con `r = ln(C_{t+1}/C_t)`, sin costos |
| Buy & hold | Retorno de mantener la acción, como referencia |
| Sharpe | `√252 · media / desv.` de la estrategia; **no se muestra con menos de 5 días con posición** |
| Máximo drawdown | Sobre la curva de capital de la estrategia |
| Win rate / profit factor | Solo días con posición |
| Exposición | % de días con posición |
| Capital final | De $1 000 iniciales |
| Distribución de señales | % COMPRAR / MANTENER / VENDER |

**Por qué no Sharpe con menos de 5 operaciones:** con una sola operación
en 29 días el Sharpe siempre da √(252/28) = 3.00 sin importar el
resultado. No es interpretable.

---

## 6. La auditoría del 30 de septiembre (qué estaba mal y se corrigió)

Antes de julio la API generaba precios y señales con `random`. En julio se
conectó el modelo real. En septiembre se revisó todo y se corrigió:

| Qué se veía | Problema | Corrección |
|---|---|---|
| "Correcta" ✓/✗ | Comparaba la señal de *t* con el movimiento de *t−1* a *t* (el pasado) y con umbrales fijos de ±1 % | Se compara con *t → t+1* con la etiqueta del entrenamiento; el último día queda "pendiente" |
| F1 por clase y F1 macro | Eran precisiones | F1 reales |
| Sharpe y drawdown | Se calculaban sobre el precio de la acción | Sobre la estrategia; buy & hold aparte |
| Retorno y win rate | Otra estrategia (solo largo) | La de la tesis |
| Ventanas de 60 y 90 días | No existían (siempre 30) | Parámetro `days` real |
| "Mercado cerrado" | Fijo en el código | `GET /market-status` con horario y feriados de NYSE |
| Señal durante el horario de mercado | Usaba el precio intradía como si fuera el cierre | Se descarta la vela en curso |
| Sharpe de 1 operación | Siempre 3.00 | Se omite con menos de 5 días con posición |
| "Acerca de" decía que las señales venían de una LSTM | Falso | Ficha leída de `GET /model` |
| Endpoints `POST` | Permitían escribir datos que no son del modelo | Desactivados (403) |

Esto es importante para la defensa: la plataforma ahora mide **exactamente
lo mismo** que la tesis.

---

## 7. Pruebas automáticas (23)

| Archivo | Qué verifica |
|---|---|
| `test_features.py` (6) | Que existan todas las columnas, que no haya vacíos después del calentamiento, que `ret_1d` sea el log-retorno, que el RSI esté en [0, 100], que `dist_ma10` sea positiva en una serie creciente, que se unan las variables de mercado |
| `test_model.py` (5) | Que el `.pkl` tenga las variables esperadas, la forma de la predicción, una predicción por fila, que `MODEL_VERSION` coincida con el `.pkl`, que `/model` reporte el peso de MANTENER |
| `test_main.py` (12) | Métricas con valores conocidos, días pendientes, que el acierto se evalúe contra el día siguiente, orden de las señales recientes, semántica de la etiqueta real, **que la etiqueta en vivo coincida con la del entrenamiento**, horario y feriados, descarte de la vela en curso, reintento del catálogo, overrides desactivados, y una corrida completa de `initialize_data` con datos simulados (sin red) |

Se corren con:

```bash
pip install -r api/requirements-dev.txt
cd api && pytest
```

`main.py` no arranca la actualización al importarse (solo `wsgi.py` lo
hace), justamente para que las pruebas puedan importarlo sin red.

---

## 8. Configuración (variables de entorno)

| Variable | Default | Para qué |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./trading_system.db` | Motor y ubicación de la base |
| `REFRESH_HOUR` / `REFRESH_MINUTE` | 16 / 30 | Hora de la actualización diaria (NY) |
| `FETCH_RETRY_ATTEMPTS` / `FETCH_RETRY_DELAY_SECONDS` | 3 / 5 | Reintentos ante fallas de Yahoo |
| `CATALOG_RETRY_MINUTES` | 2 | Cada cuánto reintentar si faltan acciones |
| `ENABLE_MANUAL_OVERRIDES` | 0 | Activar escritura manual (solo pruebas) |
| `MODEL_PATH` | `ml/artifacts/…pkl` | Usar otro modelo |
| `API_HOST` / `API_PORT` / `FLASK_DEBUG` | 127.0.0.1 / 8000 / 1 | Servidor local |

---

## 8b. Diferencias con la API descrita en el TT1

| TT1 (§4.3.2, Tabla 13) | Final |
|---|---|
| 7 GET (`/health`, `/metrics`, `/stocks`, `/stocks/<s>`, `/history`, `/metrics`, `/info`) | Los mismos + `GET /model` y `GET /market-status`; `history` y `metrics` aceptan `days=30/60/90` |
| El diagrama de secuencia del TT1 usa otras rutas (`/api/summary`, `/api/signals`, `/api/equity/{ticker}`) | No existen; las vigentes son las de §2. *Es una inconsistencia interna del TT1* |
| 5 POST internos para la carga del ETL | Existen pero **desactivados (403)**; el ETL corre dentro del proceso |
| Lectura desde `snapshots_90d` (< 50 ms) | Lectura desde la caché en memoria |
| Puerto 5000 | Puerto 8000 (local); el que asigne Render en producción |
| Respuesta `{status, data, message}` | `{success, data}` o `{success: false, error}` |

---

## 9. Limitaciones conocidas

- **CORS abierto** a cualquier origen: aceptable porque la API es de solo
  lectura y pública; en un sistema con datos privados habría que
  restringirlo.
- **Sin autenticación** en `POST /admin/refresh`: solo recalcula con datos
  públicos (no modifica nada que no se regenere), pero alguien podría
  forzar recálculos. Mejora futura: una llave para ese endpoint.
- **Feriados de NYSE escritos a mano** (2026–2027); hay que agregar los
  siguientes.
- **Un solo worker** por el programador en proceso (ver B5).

---

## Preguntas de este tema

Están desarrolladas en [D6](../D_defensa/D6_PREGUNTAS_SISTEMA.md).
