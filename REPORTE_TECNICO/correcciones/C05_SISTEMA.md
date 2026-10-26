# C05 — Capítulo 5: Diseño e implementación del sistema (p. 66–82)

> **Diagnóstico:** el capítulo describe el **diseño de TT1**: seis capas,
> PostgreSQL con 9 tablas, un ETL incremental en un proceso aparte con cron,
> una interfaz de tres niveles con consulta cada hora, tres puertos locales y
> el modelo "pendiente". El sistema real es otro: la actualización corre
> **dentro de la API** (APScheduler), la base es **SQLite con 4 tablas**, la
> interfaz tiene **7 pantallas**, está **desplegado en Render** y usa la LR
> `LR-v8-interactions-holdw090`. Además el capítulo mezcla dos juegos de rutas
> de la API (C-29). Hay que reescribirlo casi completo; las seis figuras se
> reemplazan por `diagramas/D01`–`D07`.
>
> Lo que **sí se conserva**: la separación entre entrenamiento fuera de
> línea y producción, el modelo cargado desde un archivo, la API REST de
> solo lectura para el frontend, el frontend desacoplado, la ejecución
> después del cierre, la justificación de Flask y React, y las lecciones de
> pruebas e integración (con tono impersonal).
>
> Borrador del capítulo: `textos/T05_sistema.md`. Tablas: `tablas/T-14`
> (endpoints), `T-15` (cambios respecto a TT1). Fuentes:
> `ESTUDIO_TT/B_sistema/B1`–`B5`, `docs/API.md`, `docs/DATABASE.md`,
> `docs/FRONTEND.md`, `docs/DEPLOY_RENDER.md`.

## Resumen de puntos

| ID | Página | Sección | Tema | Prioridad |
|---|---|---|---|---|
| 5-01 | 66 | 5 (intro) | Descripción general | IMPORTANTE |
| 5-02 | — | Nuevo | Requerimientos y casos de uso | IMPORTANTE |
| 5-03 | 67 | 5.1 | "Seis capas" de abajo hacia arriba | CRÍTICO |
| 5-04 | 67 | Fig. 1 | Puertos, PostgreSQL, 6 endpoints, modelos | CRÍTICO |
| 5-05 | 67–68 | Tabla 10 | Tecnologías de cada capa | CRÍTICO |
| 5-06 | 68 | 5.1.1 | Justificación de PostgreSQL | CRÍTICO |
| 5-07 | 69 | 5.2.1 | Scripts 01–03 con selección por modelo | CRÍTICO |
| 5-08 | 69 | Fig. 2 | Flujo fuera de línea | CRÍTICO |
| 5-09 | 70 | 5.2.2, Tabla 11 | ETL incremental, cron, tiempos | CRÍTICO |
| 5-10 | 70 | 5.2.2 | Días festivos | IMPORTANTE |
| 5-11 | 71 | Fig. 3 | "46 features", pasos semanales y mensuales | CRÍTICO |
| 5-12 | 71 | 5.3 | Backend = PostgreSQL + Flask | CRÍTICO |
| 5-13 | 71–72 | 5.3.1, Fig. 4 | Esquema de 9 tablas | CRÍTICO |
| 5-14 | 73–74 | Tabla 12 | Tablas y `snapshots_90d` | CRÍTICO |
| 5-15 | 74–75 | 5.3.2, Tabla 13 | Endpoints, formato, caché, CORS | CRÍTICO |
| 5-16 | 75–76 | 5.3.3 | Pruebas de estabilidad: PostgreSQL y tono | IMPORTANTE |
| 5-17 | 76 | 5.4 | Tres niveles | CRÍTICO |
| 5-18 | 76 | 5.4.1 | Nivel 1, 2 y 3 | CRÍTICO |
| 5-19 | 77 | Fig. 5 | Niveles y consulta cada hora | CRÍTICO |
| 5-20 | 77 | 5.4.2 | Gráfica de pastel y consulta cada hora | CRÍTICO |
| 5-21 | 77–78 | 5.4.3 | "Cliente", niveles de seguridad, tono | IMPORTANTE |
| 5-22 | — | Nuevo | Pantallas Modelos, Aprende, Ayuda | IMPORTANTE |
| 5-23 | 78 | 5.5.1, Fig. 6 | Rutas `/api/...` y PostgreSQL | CRÍTICO |
| 5-24 | 79–80 | 5.5.2, Tabla 14 | Solo despliegue local | CRÍTICO |
| 5-25 | 80 | 5.5.2 | ETL como script con cron | CRÍTICO |
| 5-26 | 80 | 5.5.3 | Vinculación: puertos y tono | IMPORTANTE |
| 5-27 | 80 | 5.5.4 | "Una función por cada endpoint" | IMPORTANTE |
| 5-28 | 81 | 5.5.4 | Fechas en UTC: conservar | FORMA |
| 5-29 | 81 | 5.5.5 | Manual de usuario y niveles | IMPORTANTE |
| 5-30 | 81–82 | 5.5.6 | "Integración pendiente"; `.pt` | CRÍTICO |
| 5-31 | — | Nuevo | Despliegue en Render | CRÍTICO |
| 5-32 | — | Nuevo | Pruebas automáticas y seguridad | IMPORTANTE |

---

### 5-01 · p. 66 · Introducción · IMPORTANTE
**Dice:** "…aplicación web desarrollada para visualizar y consultar las
señales de trading generadas por el modelo ganador. El sistema integra un
pipeline ETL…, una base de datos relacional, una API REST y una interfaz…".
**Debe decir:** "…plataforma web que, cada día hábil después del cierre,
descarga los datos, calcula la recomendación del modelo elegido para las
siete acciones, evalúa cada recomendación pasada contra lo que ocurrió y lo
publica en una aplicación pensada para usuarios sin conocimientos de
finanzas, junto con la comparación de los cinco modelos. Se compone de una
API en Flask que incluye la actualización diaria, una base SQLite y una
aplicación React, desplegadas en Render".

### 5-02 · Nuevo · Requerimientos y casos de uso · IMPORTANTE
El reporte de TT1 tenía requerimientos funcionales y no funcionales y tres
casos de uso (CU-01 consultar señales del día, CU-02 revisar el detalle de un
activo, CU-03 comparar el rendimiento); esta versión no los tiene. Para un
documento de ingeniería conviene recuperarlos y actualizarlos:
- CU-01 → pantalla «Hoy»; CU-02 → «Detalle»; CU-03 → «Resultados»
  (contra comprar y mantener **cada acción**, no contra el S&P 500).
- Casos nuevos: CU-04 comparar modelos («Modelos»), CU-05 aprender qué
  significa cada recomendación («Aprende»), CU-06 consultar la guía y el
  glosario («Ayuda»).
- No funcionales: actualización diaria después del cierre; sin datos
  simulados; diseño responsivo; respuesta inmediata después del primer
  arranque (en el plan gratuito, la primera carga tras dormir tarda 20–40 s).
Fuente: `ESTUDIO_TT/B_sistema/B4` §6b; `D1` §9.

### 5-03 · p. 67 · §5.1 · CRÍTICO
**Dice:** "El sistema se organiza en seis capas funcionales… una pila
vertical de capas en la que los datos fluyen de abajo hacia arriba".
**Debe decir:** dos partes con una sola interfaz entre ellas: **fuera de
línea** (investigación: dataset, comparación de los cinco modelos,
entrenamiento del modelo de producción) y **en línea** (plataforma: API con
actualización diaria, base de datos y aplicación web). Lo único que pasa de
una parte a la otra es el archivo `.pkl` del modelo y el código de las
características (copiado idéntico, con pruebas). Figura
`diagramas/D01_arquitectura.svg`.

### 5-04 · p. 67 · Figura 1 · CRÍTICO
Errores de la figura: "React… puerto 3000" (Vite usa 5173 en local y en
producción es un sitio estático); "Flask… 6 endpoints… puerto 5000" (son 9
GET y 1 POST; puerto 8000 en local); "PostgreSQL · 9 tablas 3FN + 1
desnorm. · JSONB · puerto 5432" (SQLite, 4 tablas); "Modelos ML/DL: LR ·
XGBoost · LSTM · CNN-LSTM" (falta la CNN 1D y en producción solo hay una
LR); "Pipeline ETL: Scripts 01–03 · Diario" (la actualización diaria está
dentro de la API). **Reemplazar** por `diagramas/D01_arquitectura.svg`.

### 5-05 · p. 67–68 · Tabla 10 · CRÍTICO

| Capa | Dice | Debe decir |
|---|---|---|
| Fuentes de datos | Yahoo Finance; OHLCV + SPY + VIX | Igual (yfinance 1.3.0 en producción) |
| Pipeline ETL | Python 3.12; scripts 01, 02, 03; offline y diario | **Investigación:** `scripts_v1/01` + `scripts_opt/` (fuera de línea). **Actualización diaria:** dentro de la API (`api/main.py`, APScheduler). Python 3.13 |
| Modelos | scikit-learn, XGBoost, PyTorch; `.pkl / .json / .pt` | Cinco modelos en la investigación; **en producción una LR** en `.pkl` con su escalador, la lista de 76 variables y sus metadatos (`lr_elasticnet_global_expB.pkl`, el nombre es histórico) |
| Base de datos | PostgreSQL 12+; 9 tablas 3FN + 1 desnorm.; índices (asset_id, date) | **SQLite** con SQLAlchemy 2; 4 tablas; restricciones únicas (asset_id, date) y (asset_id, window_days) |
| API REST | Flask; 6 endpoints GET; solo lectura, sin autenticación, CORS | Flask 3 + gunicorn; **9 GET + `POST /admin/refresh`**; los 5 POST de carga manual desactivados (403); CORS habilitado |
| Frontend | React + TypeScript; dashboard + tarjetas + vista de detalle | React 18 + TypeScript + **Vite + Tailwind CSS 4 + React Router 7** + Recharts; **7 pantallas** |
| (nueva) Despliegue | — | Render: API en Docker (1 worker) + sitio estático; despliegue automático desde GitHub |

### 5-06 · p. 68 · §5.1.1 · CRÍTICO
- Flask: "un sistema… con seis endpoints" → "con una decena de rutas de
  lectura". El resto del argumento se conserva.
- React: conservar; agregar Vite (compilación y servidor de desarrollo),
  Tailwind (estilos) y React Router (navegación). La frase "gráficas de línea
  para la curva de equity, barras para métricas comparativas y distribución
  de señales" está bien; **no** se implementó la gráfica de pastel.
- **PostgreSQL:** el párrafo completo justifica PostgreSQL contra SQLite con
  tres razones (ACID con dos procesos escribiendo, JSONB, índices
  compuestos). **Reemplazar** por la justificación de SQLite: la
  actualización corre en el mismo proceso que la API, así que hay **un solo
  escritor** (protegido con un candado) y la limitación de concurrencia de
  SQLite no aplica; SQLite también es ACID; no se guarda la matriz de
  confusión (no hace falta JSONB); las restricciones únicas crean los mismos
  índices; la base es reconstruible desde Yahoo + el modelo, lo que permite
  usar el plan gratuito de Render sin disco persistente; el esquema funciona
  igual en PostgreSQL (cambiar `DATABASE_URL`; hay un perfil en
  `docker-compose.yml`). Borrador: `textos/T05_sistema.md` §4.
**Por qué:** el documento afirma lo contrario de lo que se implementó; es una
de las contradicciones más visibles.

### 5-07 · p. 69 · §5.2.1 Fase fuera de línea · CRÍTICO
**Dice:** tres scripts: 01 (descarga y 54 características), 02 (selección
por modelo con Pearson+VIF, SHAP y Spearman), 03 (datasets por modelo con
escalado distinto y canales OHLCV); "cualquier investigador que ejecute los
tres scripts… obtendrá exactamente los mismos modelos".
**Debe decir:** el flujo de investigación a producción
(`diagramas/D02_investigacion_a_produccion.svg`):
1. `scripts_v1/01_build_raw_dataset.py`: descarga y calcula las 61
   características y la etiqueta → 7 archivos parquet.
2. `scripts_opt/` por etapa: comparación en igualdad (Etapa 3,
   `train_all_v4.py`), protocolo final con Optuna e intervalos (Etapa 4,
   `run_v5.py`), interacciones (Etapa 5, `via8_dataset.py`), ajuste de
   mantener (Etapa 6, `ajuste_hold_rolling.py`).
3. `scripts_opt/entrenar_produccion.py`: entrena la LR final con 2018–2025
   (14 063 filas) y escribe el `.pkl` en `api/ml/artifacts/`.
Reproducibilidad: la LR es determinista; el código de la Etapa 4 reproduce
18 de 18 celdas de la Etapa 3; las redes usan semillas fijas (en GPU puede
haber diferencias mínimas). Quitar "exactamente los mismos modelos" o
limitarlo a la LR.

### 5-08 · p. 69 · Figura 2 · CRÍTICO
Muestra "Calcula 54 características", el Script 02 de selección y el Script
03 con escalado por modelo. Reemplazar por
`diagramas/D02_investigacion_a_produccion.svg`.

### 5-09 · p. 70 · §5.2.2 y Tabla 11 · CRÍTICO

| Aspecto | Dice | Debe decir |
|---|---|---|
| Dónde corre | Script aparte, "puede automatizarse con cron en Linux" | Dentro del proceso de la API, con **APScheduler** |
| Cuándo | 16:30 EST | **16:30 hora de Nueva York** de lunes a viernes (con horario de verano), al arrancar el servidor, cada 2 minutos mientras falte alguna acción y con `POST /admin/refresh` |
| Qué procesa | "Incremental: únicamente el día en curso sin recalcular días pasados" | **Recalcula toda la ventana** (~3 años descargados) en cada actualización: cuesta segundos y garantiza que todo lo mostrado sale del modelo vigente |
| Duración | "entre 3 y 5 minutos" (y tiempos por paso en la Tabla 11) | No hay medición publicada; el cómputo es de segundos y la descarga depende de Yahoo. Quitar los tiempos o medirlos |
| Pasos | 7 pasos con tablas `features_daily`, `daily_returns`, `strategy_metrics_weekly` (lunes), `model_metrics_monthly` y `strategy_metrics_monthly` (fin de mes), `snapshots_90d` | Descargar 3 años de OHLCV (7 acciones + SPY + VIX, 3 reintentos) → descartar la vela en curso si el mercado está abierto → 76 características → 3 probabilidades por día → etiqueta real y acierto (el último día queda "pendiente") → métricas de 30, 60 y 90 días → caché en memoria y *upsert* en SQLite |
| "54 indicadores" | | 61 + 15 = 76 |

Reemplazar la Tabla 11 por una tabla de los pasos reales (o por la figura
`diagramas/D03_actualizacion_diaria.svg`). Fuente:
`ESTUDIO_TT/B_sistema/B2` §3.

### 5-10 · p. 70 · Días festivos · IMPORTANTE
**Dice:** "El pipeline detecta automáticamente los días festivos… cuando la
descarga devuelve un DataFrame vacío… la tabla snapshots_90d conserva el
último snapshot válido".
**Debe decir:** "La actualización corre de lunes a viernes; el calendario de
feriados de NYSE (2026–2027) está en la API (`GET /market-status`). Si no hay
una vela nueva, el recálculo produce los mismos datos. Si el mercado sigue
abierto, se descarta la vela del día porque su precio no es un cierre".
Limitación: los feriados están escritos a mano y hay que agregar los de
2028.

### 5-11 · p. 71 · Figura 3 · CRÍTICO
Dice "46 features del día actual" (contra 54 del texto y 61 reales; C-01),
"duración estimada 3–5 min" y los pasos semanales y mensuales. Reemplazar por
`diagramas/D03_actualizacion_diaria.svg`.

### 5-12 · p. 71 · §5.3 · CRÍTICO
**Dice:** "El backend se compone de dos partes: la base de datos PostgreSQL…
y la API REST en Flask… Ambas capas son independientes".
**Debe decir:** "El backend es un solo servicio: la API en Flask, que incluye
la actualización diaria, el cálculo de características, el modelo y una base
SQLite como registro persistente; las respuestas salen de una caché en
memoria que se llena en cada actualización".

### 5-13 · p. 71–72 · §5.3.1 y Figura 4 · CRÍTICO
**Dice:** 3FN con una excepción, `assets` como eje, `ON DELETE RESTRICT`,
nueve tablas.
**Debe decir:** cuatro tablas (`assets`, `ohlcv_daily`, `predictions`,
`metrics`) con `assets` como eje y llaves foráneas; restricciones únicas
(`asset_id`, `date`) y (`asset_id`, `window_days`); borrado en cascada; las
tablas base en 3FN y columnas derivadas **a propósito** en `predictions`
(`confidence`, `correct`, `actual_price`) y `metrics` (agregados): son el
registro de lo que la plataforma calculó y mostró con cada versión del
modelo; no hay anomalías de actualización porque hay un solo escritor que
recalcula todo. Análisis forma por forma en `ESTUDIO_TT/B_sistema/B3` §3.
Figura `diagramas/D04_entidad_relacion.svg`.
Conservar la idea de TT1 de la "desnormalización intencional como vista
materializada" (antes `snapshots_90d`, ahora `metrics`).

### 5-14 · p. 73–74 · Tabla 12 · CRÍTICO
Reemplazar por las cuatro tablas reales con sus columnas (`B3` §2) y una
nota con qué pasó con cada tabla de TT1 (`B3` §4.1): `features_daily`
eliminada (las 76 variables se recalculan en menos de un segundo),
`daily_returns` y las tres tablas de métricas absorbidas por `metrics`
(ventanas de 30/60/90 días), `snapshots_90d` sustituida por la caché en
memoria + `metrics`.

### 5-15 · p. 74–75 · §5.3.2 y Tabla 13 · CRÍTICO
- "Todos los endpoints son de lectura (método GET)" → 9 GET + `POST
  /admin/refresh` (fuerza el recálculo con datos públicos); los 5 `POST` de
  carga que tenía el diseño de TT1 existen pero están **desactivados (403)**
  porque permitirían escribir datos que no salen del modelo.
- "La API lee principalmente de la tabla snapshots_90d… menos de 50 ms" →
  "las respuestas salen de la caché en memoria"; quitar "50 ms" (no hay
  medición).
- Formato: "campo data…, campo status… y message" → `{"success": true,
  "data": …}` o `{"success": false, "error": "…"}`.
- Tabla 13: reemplazar por `tablas/T-14` (agrega `GET /model` y
  `GET /market-status`; `history` y `metrics` aceptan `days=30|60|90`).
- CORS: "En un entorno de producción se configuraría para aceptar
  únicamente solicitudes del dominio del frontend" → hoy está en producción
  con CORS abierto; justificarlo (API pública de solo lectura) o
  restringirlo. Ver 5-32.
- "probabilidades con cuatro decimales y retornos como porcentaje con dos" →
  verificar contra `docs/API.md` antes de dejarlo.

### 5-16 · p. 75–76 · §5.3.3 Pruebas de estabilidad · IMPORTANTE
El contenido es valioso (conexiones que no se cerraban, errores en HTML en
lugar de JSON). Ajustes:
- Pasar a tono impersonal ("se observó que…", no "nos dimos cuenta de que
  'funciona en mi computadora' no es lo mismo que 'es estable'").
- Si el problema de conexiones fue con la primera versión en PostgreSQL,
  decirlo así ("en la primera versión, con PostgreSQL y psycopg2, …"); la
  versión actual usa SQLAlchemy con sesiones que se cierran en cada
  operación.
- Agregar las **24 pruebas automáticas** (pytest) que existen hoy y qué
  verifican (`ESTUDIO_TT/B_sistema/B2` §7) — mejor en una sección de
  pruebas (5-32).

### 5-17 · p. 76 · §5.4 · CRÍTICO
**Dice:** "tres niveles de visualización accesibles de forma progresiva".
**Debe decir:** "siete pantallas" (`tablas/T-14b` o la tabla de B4 §2): Hoy,
Detalle, Resultados, Modelos, Aprende, Ayuda y Acerca de. Figura
`diagramas/D05_pantallas.svg` + capturas reales de la plataforma.

### 5-18 · p. 76 · §5.4.1 · CRÍTICO

| Nivel de TT1 | Lo que dice | Lo que existe |
|---|---|---|
| Nivel 1 — Panel general | Retorno acumulado 90 d, Sharpe promedio, win rate global, comparación contra el S&P 500 | Pantalla **«Resultados»**: resumen de las 7 empresas en ventanas de 30/60/90 días, ganancia por empresa contra comprar y esperar **esa acción** (no contra el S&P 500), calificación F1 por empresa contra el azar, tabla ordenable |
| Nivel 2 — Tarjetas | Retorno 90 d, Sharpe, win rate, retorno contra buy & hold, señal | Pantalla **«Hoy»**: una tarjeta por empresa con la recomendación, una frase que la explica, el precio y la seguridad en palabras; las métricas están en el detalle |
| Nivel 3 — Vista detallada expandible | Curva de equity de 90 días, historial de 30 días, F1 por clase, matriz de confusión | Pantalla **«Detalle»**: recomendación y seguridad, las 3 probabilidades, gráfica de precio con un punto por recomendación, «¿Qué habría pasado con $1,000?», aciertos, últimas 10 recomendaciones con su resultado; **no** hay matriz de confusión |

### 5-19 · p. 77 · Figura 5 · CRÍTICO
Muestra los tres niveles, "puerto 3000" y "Polling autónomo cada 1 hora a
GET /api/signals". No hay consulta automática cada hora (la página pide los
datos al abrirse o con «Actualizar»; la recomendación cambia una vez al día)
y la ruta `/api/signals` no existe. Reemplazar por
`diagramas/D05_pantallas.svg`.

### 5-20 · p. 77 · §5.4.2 · CRÍTICO
- "La distribución de señales del historial se representa mediante un
  PieChart" → no se implementó; la distribución se muestra como porcentajes.
- Colores: comprar verde, vender rojo, mantener ámbar (la seguridad usa
  barras azules para no confundirse con ellos).
- "El frontend realiza polling a la API cada hora… /api/signals…" → quitar
  (ver 5-19). Conservar el razonamiento de por qué no se usan WebSockets.
- Agregar la curva de capital «¿Qué habría pasado con $1,000?» (estrategia
  contra comprar y esperar), agregada el 14 de octubre.

### 5-21 · p. 77–78 · §5.4.3 Ajustes por retroalimentación · IMPORTANTE
- Definir quién es "el cliente" (¿asesor, usuarios de prueba, directores?).
- "Los nombres y valores que aparecen en la sección 5.4.1 y en la Figura 5
  corresponden a la primera versión" → una vez actualizada 5.4.1, esta
  sección pasa a ser "Decisiones de diseño a partir de la retroalimentación".
- **Niveles de seguridad:** "seguro", "mitad seguro" y "poco seguro" →
  **«Nada segura»** (acertó 37 de cada 100), **«Poco segura»** (38) y
  **«Medianamente segura»** (42), con el azar en 33; no hay nivel «Segura»
  porque ningún tramo acierta ni la mitad de las veces. Los cortes salen de
  siete años evaluados sin haberlos visto (`calibrar_niveles_confianza.py`).
  Explicar por qué un "36 %" se ve mal y por qué tres niveles en palabras es
  más honesto.
- Agregar: el tono de los textos (frases cortas: «Podría subir», «Podría
  bajar», «Mejor esperar»), las fechas como «jueves 15 de octubre», el ROI
  con su equivalente en dinero ("$1,000 → $1,043.97") y el aviso legal.
- Pasar a tono impersonal.
**Fuente:** `ESTUDIO_TT/B_sistema/B4` §3.

### 5-22 · Nuevo · Pantallas que no aparecen · IMPORTANTE
Agregar, con una captura cada una:
- **«Modelos»** (`/modelos`): qué modelo se eligió y por qué, tabla de
  igualdad de condiciones, prueba 2025 con selector A/B/C, intervalos, año
  por año, prueba ciega 2026, dinero con y sin comisión, global contra por
  acción y multicolinealidad. Responde a la observación de la sinodal de
  poner explícito el modelo y la comparación. Los datos vienen de un JSON
  generado por `scripts_opt/observaciones_sinodal.py exportar_web`.
- **«Aprende»** (`/aprende`): qué es comprar, vender en corto y mantener,
  con una barra interactiva, la venta en corto en cuatro pasos y un juego con
  los precios reales de los últimos 30 días hábiles.
- **«Ayuda»** (`/ayuda`): guía rápida por pantalla y glosario buscable; cada
  «?» de la interfaz lleva a su definición.
- **«Acerca de»**: ficha del modelo leída de `GET /model`, metodología y
  aviso legal.
- Tema claro/oscuro y diseño responsivo.

### 5-23 · p. 78–79 · §5.5.1 y Figura 6 · CRÍTICO
**Dice:** la carga inicial llama `GET /api/summary` y `GET /api/signals`; al
elegir una acción, `GET /api/equity/{ticker}` y `GET /api/metrics/{ticker}`;
la figura muestra PostgreSQL :5432, React :3000 y Flask :5000.
**Debe decir:** «Hoy» llama `GET /market-status` y `GET /stocks`; si la lista
llega vacía (la API acaba de despertar y Yahoo falló), llama una vez a
`POST /admin/refresh` y vuelve a pedir `GET /stocks`. «Detalle» llama
`GET /stocks/:s`, `GET /stocks/:s/history?days=` y
`GET /stocks/:s/metrics?days=`; «Resultados», `GET /metrics?days=`;
«Acerca de», `GET /model`. Las respuestas salen de la caché en memoria de la
API. Figura `diagramas/D06_secuencia.svg`. Las llamadas se hacen con `fetch`
dentro de `useEffect`, como dice el texto (eso se conserva).

### 5-24 · p. 79–80 · §5.5.2 y Tabla 14 · CRÍTICO
**Dice:** "En la configuración actual de desarrollo, los tres componentes…
se ejecutan en la misma máquina local" con PostgreSQL 5432, Flask 5000 y
React 3000.
**Debe decir:** "Ejecución local: la API en `http://localhost:8000`
(`python api/main.py`) y el frontend con Vite en `http://localhost:5173`;
con Docker Compose, la API en 8000 (con un volumen para la base) y el
frontend con nginx en 8080, más un perfil opcional con PostgreSQL 15". La
Tabla 14 se actualiza con esos valores o se elimina. La configuración de
producción va en la sección nueva de despliegue (5-31).

### 5-25 · p. 80 · §5.5.2, último párrafo · CRÍTICO
**Dice:** "El pipeline ETL diario se ejecuta como un script Python
independiente… o programarse mediante cron. Este script accede directamente
a la base de datos PostgreSQL por el mismo puerto 5432 sin pasar por la
API…".
**Debe decir:** la actualización corre dentro de la API (ver 5-09) y escribe
en SQLite en el mismo proceso. C-31, S-02.

### 5-26 · p. 80 · §5.5.3 Vinculación · IMPORTANTE
La lección es buena (probar de abajo hacia arriba; el error de CORS ocurre en
el navegador, no en el servidor). Ajustes: puertos reales (API 8000, Vite
5173), mencionar que la URL de la API ya se guarda en la variable de
compilación `VITE_API_URL` (`Frontend/src/config/api.ts`) y que en Render se
fija en el panel del sitio estático; tono impersonal.

### 5-27 · p. 80 · §5.5.4 Cliente HTTP · IMPORTANTE
**Dice:** "creamos una capa de cliente HTTP, un solo módulo que concentra la
dirección base de la API, una función por cada endpoint de la Tabla 13 y el
manejo común de errores".
**Verificar y corregir:** en el código actual solo la **dirección base**
está centralizada (`Frontend/src/config/api.ts`); las llamadas `fetch` están
en cada página. O se describe así, o se implementa el módulo antes de
entregar.

### 5-28 · p. 81 · §5.5.4, fechas · FORMA
El problema de las fechas en UTC (el 13 de octubre aparecía como 12) y su
solución (tratar la fecha como día de calendario) es correcto y vigente
(`Frontend/src/app/format.ts`). Conservar en tono impersonal.

### 5-29 · p. 81 · §5.5.5 Pruebas funcionales y manual · IMPORTANTE
- "Con la interfaz ya estable elaboramos el manual de usuario" → el manual
  vive dentro de la aplicación, en la pestaña «Ayuda» (Guía rápida); si
  además existe un PDF, indicar dónde está. Si la normativa de ESCOM pide un
  manual como anexo, se puede exportar la guía (Anexo D).
- Niveles "seguro", "mitad seguro", "poco seguro" → los reales (5-21).
- Actualizar lo que se prueba: «Hoy», «Detalle», «Resultados», «Modelos»,
  «Aprende», «Ayuda», estado de carga, error y arranque en frío.

### 5-30 · p. 81–82 · §5.5.6 Estado actual · CRÍTICO
**Dice:** "La integración completa del modelo ganador al pipeline de
inferencia está pendiente de la selección definitiva del modelo… (.pkl para
LR o XGBoost, .pt para LSTM o CNN-LSTM)".
**Debe decir:** "El modelo integrado es la Regresión Logística
`LR-v8-interactions-holdw090` (L2, C = 0.000165, RobustScaler, 76
características, pesos balanceados con mantener × 0.90, entrenada con
2018–2025). La API carga el `.pkl` una sola vez, verifica que contenga las
76 variables esperadas y expone su ficha en `GET /model`. El diseño sigue
siendo agnóstico al modelo: cambiarlo es sustituir el archivo y actualizar
`MODEL_VERSION`, y una prueba automática falla si ambos no coinciden".
Mover a 5.3 (del modelo de investigación al de producción).

### 5-31 · Nuevo · Despliegue · CRÍTICO
Agregar una sección de despliegue (hoy el documento dice que es trabajo
futuro): Render con dos servicios definidos en `render.yaml` (Blueprint): la
API en Docker (`python:3.13-slim`, gunicorn con **1 worker** porque el
programador vive en el proceso, `--timeout 300` para el primer arranque) y el
frontend como sitio estático con regla de reescritura a `index.html`;
despliegue automático con cada `push` a `main`; verificación con
`GET /health` (`stocksLoaded: 7`) y `GET /model`. Limitaciones del plan
gratuito: el servicio se duerme tras ~15 min sin tráfico (primera carga de
20–40 s) y la base es efímera (se reconstruye al arrancar, lo cual es
aceptable porque es reconstruible). URLs:
- Frontend: https://tt-frontend-womf.onrender.com
- API: https://tt-api-jc7n.onrender.com
Figura `diagramas/D07_despliegue.svg`. Fuente: `ESTUDIO_TT/B_sistema/B5`.

### 5-32 · Nuevo · Pruebas automáticas y seguridad · IMPORTANTE
- **Pruebas:** 24 pruebas de la API con pytest: características (columnas,
  sin vacíos tras el calentamiento, RSI en [0, 100]…), modelo (variables del
  `.pkl`, forma de la predicción, `MODEL_VERSION`), API y métricas (valores
  conocidos, días pendientes, acierto contra el día siguiente, **que la
  etiqueta en vivo coincida con la del entrenamiento**, horario y feriados,
  descarte de la vela en curso, escrituras manuales desactivadas, corrida
  completa con datos simulados sin red). No hay pruebas automáticas del
  frontend.
- **Seguridad:** secretos fuera del código (`.env`, variables de Render);
  HTTPS de Render; escritura manual desactivada; CORS abierto (API pública de
  solo lectura); `POST /admin/refresh` sin autenticación (solo recalcula con
  datos públicos; mejora futura: una llave).
- **Consistencia con la tesis (opcional):** la plataforma calcula las
  métricas con las mismas definiciones que la investigación; en la revisión
  del 30 de septiembre se corrigieron diferencias de definición (acierto
  contra el día siguiente, F1 reales, Sharpe sobre la estrategia). Detalle en
  `ESTUDIO_TT/B_sistema/B2` §6; valorar cuánto detalle incluir.
