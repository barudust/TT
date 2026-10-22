# B1 — Arquitectura del sistema

> **Resumen.** El sistema tiene dos mundos separados. **Fuera de línea**
> (investigación): scripts de Python que construyen el dataset, entrenan y
> comparan los modelos, y al final producen un archivo `.pkl` con el modelo
> ganador. **En línea** (plataforma): una API en Flask que cada día descarga
> datos de Yahoo Finance, calcula las 76 variables con el mismo código del
> entrenamiento, corre el `.pkl`, evalúa las señales contra lo que pasó y
> guarda todo en SQLite; y una aplicación web en React que lo muestra. Lo
> único que pasa de un mundo al otro es el `.pkl` y el código de las
> variables.
>
> Diagrama: `docs/system_architecture_diagram.svg` (el
> `_propuesta_inicial.svg` es el diseño anterior).

---

## 1. Vista completa

```
╔══════════════════════ FUERA DE LÍNEA (investigación) ══════════════════════╗
║                                                                             ║
║  Yahoo Finance ─► scripts_v1/01_build_raw_dataset.py ─► 7 archivos parquet  ║
║                      (61 variables + etiqueta)          tesis_ml_stocks/    ║
║                                  │                                          ║
║                                  ▼                                          ║
║          scripts_opt/ (Etapa 3, Etapa 4, Etapa 5, Etapa 5, análisis de septiembre)              ║
║          5 modelos · Optuna · prueba año por año · bootstrap                      ║
║                                  │  ganador: LR                             ║
║                                  ▼                                          ║
║          scripts_opt/entrenar_produccion.py                                 ║
║                                  │                                          ║
╚══════════════════════════════════│══════════════════════════════════════════╝
                                   ▼
            api/ml/artifacts/lr_elasticnet_global_expB.pkl
            (modelo + escalador + lista de 76 variables + metadatos)
                                   │
╔══════════════════════════ EN LÍNEA (plataforma) ═══════════════════════════╗
║                                  ▼                                          ║
║  Yahoo Finance ──► API Flask (api/) ─────────────► SQLite                   ║
║   (3 años de        │ ml/features.py  76 variables    assets, ohlcv_daily,  ║
║    OHLCV, SPY,      │ ml/model.py     probabilidades  predictions, metrics  ║
║    VIX)             │ ml/target.py    resultado real                        ║
║                     │ métricas 30/60/90 días                                ║
║                     │ caché en memoria                                      ║
║                     ▼                                                       ║
║            JSON por HTTP (GET /stocks, /stocks/:s/history, /metrics…)       ║
║                     │                                                       ║
║                     ▼                                                       ║
║  Aplicación web (Frontend/) React + TypeScript ──► navegador                ║
╚═════════════════════════════════════════════════════════════════════════════╝
```

---

## 2. Componentes

| Componente | Tecnología | Responsabilidad | Detalle |
|---|---|---|---|
| Pipeline de investigación | Python, pandas, scikit-learn, XGBoost, PyTorch, Optuna | Datos, entrenamiento, comparación, análisis | Parte A |
| Artefacto del modelo | `.pkl` (pickle) + `.metrics.json` + `interaction_pairs.json` | Modelo entrenado y su evidencia | [B2 §4](B2_API.md#4-el-modelo-dentro-de-la-api) |
| API | Flask, gunicorn, APScheduler, yfinance, SQLAlchemy | Datos en vivo, inferencia, evaluación, servir JSON | [B2](B2_API.md) |
| Base de datos | SQLite (compatible con PostgreSQL) | Registro persistente de precios, señales y métricas | [B3](B3_BASE_DE_DATOS.md) |
| Frontend | React 18, TypeScript, Vite, Tailwind, Recharts | Mostrar recomendaciones y resultados | [B4](B4_FRONTEND.md) |
| Despliegue | Docker, Render (Blueprint), GitHub | Publicar API y frontend; despliegue automático | [B5](B5_DESPLIEGUE.md) |

---

## 3. El flujo de un día

1. **16:30 hora de Nueva York** (30 min después del cierre, para que Yahoo
   publique los datos), de lunes a viernes, el programador de tareas de la
   API lanza la actualización.
2. Descarga ~3 años de OHLCV de las 7 acciones, SPY y VIX (3 años porque
   la media de 200 días y la normalización del VIX de 252 días necesitan
   historia previa).
3. Si el mercado sigue abierto, descarta la vela del día (su "cierre" sería
   un precio intermedio).
4. Calcula las 61 variables + 15 interacciones (`api/ml/features.py`).
5. El modelo da 3 probabilidades por día y acción; la señal es la mayor.
6. Para cada día que ya tiene el cierre siguiente, calcula la etiqueta real
   (`api/ml/target.py`) y si la señal acertó; el último día queda
   "pendiente".
7. Calcula las métricas en ventanas de 30, 60 y 90 días.
8. Guarda todo en memoria (para responder rápido) y en SQLite (registro).
9. El frontend pide los datos por HTTP y los muestra.

---

## 4. Decisiones de arquitectura y su justificación

| Decisión | Alternativa | Por qué se eligió |
|---|---|---|
| **Separar investigación y plataforma** | Entrenar dentro de la API | Entrenar es pesado (GPU, horas de búsqueda) y se hace una vez; servir es ligero y diario. La API solo necesita el `.pkl` |
| **Mismo código de variables en ambos lados** | Reescribir las fórmulas | Si una fórmula difiere, el modelo recibe datos distintos a los de su entrenamiento y sus métricas dejan de valer. `features.py` es una copia exacta de `01_build_raw_dataset.py` y hay pruebas |
| **API REST en Flask** | FastAPI, Django | Flask es mínimo y suficiente para ~10 endpoints de lectura; el proyecto usa Flask desde su primera versión (marzo) y migrar no aportaba nada; Django sobraba (no hay usuarios ni panel de administración) |
| **Recalcular toda la ventana cada día** | Calcular solo el día nuevo | Es barato (segundos) y garantiza que todo lo mostrado sale del modelo vigente; si se reentrena el modelo, la historia se actualiza sola |
| **Caché en memoria + SQLite** | Leer siempre de la base | Las respuestas salen de memoria (rápido); la base es el registro persistente y auditable |
| **SQLite** | PostgreSQL | La base es pequeña y reconstruible desde Yahoo + el modelo; cero configuración. El esquema funciona igual en PostgreSQL (hay un perfil en `docker-compose.yml`) |
| **Actualización programada dentro del proceso (APScheduler)** | Cron externo | Un solo servicio que se encarga de todo; en Render gratuito no hay cron sin pagar. Exige 1 solo worker (ver B5) |
| **Frontend separado (SPA) que consume la API** | Páginas generadas por Flask | Separa responsabilidades; el frontend se sirve como sitio estático gratuito y siempre disponible |
| **Contenedor Docker** | Instalar en el servidor | La API corre igual en local y en la nube |

---

## 4b. La arquitectura del TT1 y por qué cambió

El reporte de TT1 (§4.1, Figura 1) organizaba el sistema en **6 capas**:
fuentes de datos → pipeline ETL → modelos → base de datos PostgreSQL → API
Flask → frontend React, con tres procesos independientes en la misma
máquina (PostgreSQL :5432, Flask :5000, React :3000) y un **ETL incremental**
(solo el día en curso, ~3–5 min, cron de Linux) que escribía directo en la
base.

| Decisión del TT1 | Decisión final | Por qué |
|---|---|---|
| ETL como script aparte, ejecutado por cron | ETL dentro de la API, con APScheduler | Un solo servicio que desplegar y operar; en el plan gratuito de Render no hay cron sin pagar; elimina la concurrencia entre dos procesos sobre la base |
| ETL incremental (solo el día nuevo) | Recalcular la ventana completa (~3 años) | Segundos de cómputo; todo lo mostrado sale del modelo vigente; si se reentrena, la historia se actualiza; no hay estados intermedios que reparar |
| Métricas semanales (lunes) y mensuales (fin de mes) | Métricas móviles de 30, 60 y 90 días recalculadas cada día | Siempre actuales y comparables; menos tablas |
| PostgreSQL, 9 tablas | SQLite, 4 tablas | Ver [B3 §4](B3_BASE_DE_DATOS.md#4-por-qué-sqlite-y-no-postgresql-como-decía-el-tt1) |
| 5 endpoints POST internos para que el ETL cargara datos | Desactivados (403) | El ETL ya no pasa por la API; abiertos permitirían escribir datos que no salen del modelo |
| Despliegue local; producción como trabajo futuro | Docker + Render con despliegue automático | Cumple el trabajo futuro del TT1 (§5.10) |
| Modelo "agnóstico": `.pkl` para clásicos o `.pt` para redes (§4.5.3) | `.pkl` de la LR | El diseño agnóstico se mantuvo (cambiar de modelo es cambiar el archivo y `MODEL_VERSION`) |

**Lo que se conserva:** la separación entre entrenamiento fuera de línea y
producción, el modelo cargado desde un archivo, la API REST de solo lectura
para el frontend, el frontend desacoplado que solo conoce el contrato de la
API y la ejecución después del cierre (16:30 Nueva York) para no usar
precios intermedios.

---

## 5. Atributos de calidad (cómo se cumplen)

| Atributo | Cómo |
|---|---|
| **Veracidad** | Nada simulado: precios de Yahoo, señales y probabilidades del modelo. Los endpoints de escritura manual están desactivados por defecto |
| **Consistencia con la tesis** | Misma etiqueta, mismas variables, misma estrategia de simulación; prueba automática que compara la etiqueta en vivo contra la del dataset |
| **Disponibilidad** | Reintentos ante fallas de Yahoo (3 intentos por descarga) y recarga automática cada 2 minutos si falta alguna acción |
| **Sin mirar el futuro** | Se descarta la vela en curso; el acierto de una señal solo se calcula con el cierre siguiente |
| **Mantenibilidad** | Modelo versionado (`MODEL_VERSION`), prueba que exige que coincida con el `.pkl`; `GET /model` describe el modelo cargado leyendo el `.pkl` |
| **Reproducibilidad** | Todo el código, semillas y versiones de bibliotecas en el repositorio |
| **Pruebas** | 24 pruebas automáticas de la API (pytest) |

---

## 6. Estructura del repositorio

```
TT_Proyecto/
├── api/                    plataforma: backend
│   ├── main.py             endpoints, actualización, métricas
│   ├── database.py         conexión SQLAlchemy
│   ├── models.py           tablas
│   ├── db_ops.py           inserción/actualización (upsert)
│   ├── wsgi.py             entrada para gunicorn
│   ├── ml/                 features.py, model.py, target.py, artifacts/
│   └── tests/              24 pruebas
├── Frontend/               plataforma: aplicación web (React)
├── docs/                   documentación técnica de la plataforma
├── scripts_v1/             pipeline inicial (01 construye el dataset)
├── scripts_opt/            investigación de las etapas 3–5 y análisis
├── tesis_ml_stocks/        datasets (parquet)
├── RESULTADOS_OPTIMIZADOS/ resultados, informes, guía de defensa
├── paper/, paper_review/   paper MICAI
├── docker-compose.yml      API + frontend (+ PostgreSQL opcional) en local
└── render.yaml             despliegue en Render
```

---

## Preguntas de este tema

Están desarrolladas en [D6](../D_defensa/D6_PREGUNTAS_SISTEMA.md).
