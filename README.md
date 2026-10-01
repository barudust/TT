# TT 2026-B164 — Plataforma de Clasificación Bursátil

Trabajo Terminal: predicción de señales de trading (COMPRAR/VENDER/MANTENER)
para siete acciones tecnológicas de EE. UU. (AAPL, NVDA, TSLA, AMZN, MSFT,
GOOGL, META), comparando empíricamente cinco arquitecturas de ML/DL, y una
plataforma web que sirve las señales del modelo ganador con datos e
inferencia reales.

El modelo en producción es una **Regresión Logística** (L2, 61 indicadores
+ 15 interacciones, pesos de clase "balanced" con HOLD × 0.90), ganadora de la
comparación contra XGBoost, LSTM, CNN y CNN-LSTM. Detalle en
`docs/MODEL_INTEGRATION.md`; por qué no se puede mejorar más con estos datos,
en `RESULTADOS_OPTIMIZADOS/JUSTIFICACION_LIMITE_DEL_MODELO.md`.

**Para retomar el proyecto desde cero (contexto completo, decisiones y cifras): [`CONTEXTO.md`](CONTEXTO.md).**
Estado y pendientes: [`STATUS.md`](STATUS.md).

## Estructura del repositorio

```
.
├── CONTEXTO.md                 # Punto de entrada: todo el contexto del proyecto
├── paper_review/               # Paper MICAI 2026 (camera_ready/ = paquete final)
├── api/                        # API Flask (endpoints, modelo ML, SQLite)
├── Frontend/                   # SPA React + TypeScript (Vite, Tailwind, PWA)
├── docs/                       # Documentación técnica de la plataforma web
├── scripts_opt/                # Pipeline de optimización que generó RESULTADOS_OPTIMIZADOS/
├── RESULTADOS_OPTIMIZADOS/     # Resultados + documentos de tesis/defensa (ver su docs/README.md)
├── scripts_v1/                 # Primera iteración del pipeline (parcialmente superada)
├── tesis_ml_stocks/            # Datasets crudos y artefactos de datos (parquet)
├── docker-compose.yml          # Stack completo local (api + Frontend [+ postgres opcional])
├── render.yaml                 # Blueprint de despliegue (ver docs/DEPLOY_RENDER.md)
└── STATUS.md
```

## Tecnologías

- Frontend: React 18, TypeScript, Vite, Tailwind CSS 4, Recharts (`Frontend/`)
- Temas: next-themes, tokens CSS en `Frontend/src/styles/theme.css`
- Backend: Flask + CORS, Yahoo Finance (datos históricos reales), scikit-learn
  para inferencia (`api/`)
- Base de datos: SQLite vía SQLAlchemy 2.0 (`docs/DATABASE.md`)
- PWA: Manifest y Service Worker

## Requisitos

- Node.js 18+
- Python 3.9+

## Instalación y ejecución

### Frontend
```bash
cd Frontend
npm install
npm run dev
```
Compilación:
```bash
npm run build
npm run preview
```

### API local
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r api/requirements.txt
python api/main.py
```
Por defecto sirve en `http://localhost:8000`. Al arrancar descarga datos
reales, calcula las 76 variables (61 indicadores + 15 interacciones) y corre
el modelo (tarda ~20-60s para los 7 tickers; si falta alguna acción reintenta
cada 2 min); después se refresca solo cada día hábil a las 16:30 hora de
Nueva York (configurable, ver `api/.env.example`), o a demanda con
`POST /admin/refresh`.

### Tests de la API
```bash
pip install -r api/requirements-dev.txt
cd api && pytest
```
No hacen llamadas de red reales (Yahoo Finance se mockea) — cubren las
features, la carga/inferencia del modelo (incluido que `MODEL_VERSION` coincida
con el `.pkl`), la etiqueta real contra el dataset de entrenamiento, las
métricas de la página, el horario de NYSE y el flujo completo de
`initialize_data()`.

### Todo junto con Docker
```bash
docker compose up -d --build
```
Frontend en `http://localhost:8080`, API en `http://localhost:8000`.
SQLite se persiste en un volumen de Docker. Postgres es opcional (perfil
`postgres`), ver comentarios en `docker-compose.yml`.

### Configuración de API (Frontend)
El frontend usa la variable `VITE_API_URL` si está definida. Si no, intenta:
- `http://localhost:8000` en desarrollo local
- `https://<host>:8000` en otros entornos

Defínela en `Frontend/.env` si lo deseas:
```
VITE_API_URL=http://localhost:8000
```

## Dónde está cada cosa

- **Contexto completo del proyecto** → [`CONTEXTO.md`](CONTEXTO.md).
- **Defensa** → [`RESULTADOS_OPTIMIZADOS/GUIA_DEFENSA_TT.md`](RESULTADOS_OPTIMIZADOS/GUIA_DEFENSA_TT.md)
  (Cap. 15: banco de preguntas; Cap. 17: preguntas de una sinodal experta) y
  [`RESULTADOS_OPTIMIZADOS/JUSTIFICACION_LIMITE_DEL_MODELO.md`](RESULTADOS_OPTIMIZADOS/JUSTIFICACION_LIMITE_DEL_MODELO.md).
- **Redactar la tesis** → [`docs/THESIS_DOCUMENTATION.md`](docs/THESIS_DOCUMENTATION.md)
  (qué documento usar en cada capítulo y las cifras clave).
- **Paper** → [`paper_review/README.md`](paper_review/README.md); compilar desde
  `paper_review/camera_ready/`.
- **Todo lo que se probó en el modelado** →
  [`RESULTADOS_OPTIMIZADOS/INVESTIGACION_COMPLETA.md`](RESULTADOS_OPTIMIZADOS/INVESTIGACION_COMPLETA.md);
  índice de documentos de investigación en
  [`RESULTADOS_OPTIMIZADOS/docs/README.md`](RESULTADOS_OPTIMIZADOS/docs/README.md).
- **Reproducir el entrenamiento** → scripts en [`scripts_opt/`](scripts_opt)
  (configuración en `scripts_opt/common.py`, dependencias en
  `scripts_opt/requirements.txt`); leen de `tesis_ml_stocks/01_raw_datasets/` y
  escriben en `RESULTADOS_OPTIMIZADOS/`. Se corren desde la raíz del repo. Ver
  [`scripts_opt/README.md`](scripts_opt/README.md); el modelo de producción se
  regenera con `python scripts_opt/entrenar_produccion.py`.
- **`scripts_v1/`** → la primera pasada del pipeline. Ver
  [`scripts_v1/README.md`](scripts_v1/README.md).

## Documentación de la plataforma web

- Arquitectura del Frontend: `docs/FRONTEND.md`
- Especificación de la API: `docs/API.md`
- Modelo y base de datos: `docs/MODEL_INTEGRATION.md`, `docs/DATABASE.md`
- Definición de las métricas que muestra la página: `docs/API_FRONTEND_METRICS.md`
- Preguntas de defensa sobre la plataforma: `docs/THESIS_QA.md`
- Despliegue en Render (auto-deploy por push a `main`): `docs/DEPLOY_RENDER.md`
- Diagrama de arquitectura: `docs/system_architecture_diagram.svg`
  (`docs/system_architecture_diagram_propuesta_inicial.svg` es el de la propuesta original)

## PWA y Android
El proyecto conserva manifest y service worker (`Frontend/public/`). Para
Android puedes evaluar:
- Trusted Web Activity (TWA) si empaquetas la PWA
- Capacitor si requieres APIs nativas

## Resumen del hallazgo principal

Tras comparar Regresión Logística, XGBoost, LSTM, CNN 1D y CNN-LSTM (más
LightGBM) en tres particiones temporales, globales y por ticker, con búsqueda
de hiperparámetros simétrica (Optuna), la **Regresión Logística regularizada y
global** es la ganadora: F1-macro 0.404 y Sharpe +0.89 en el test 2025 del
protocolo corregido (v5), significativamente arriba de los otros cuatro.
El walk-forward 2020–2025 muestra el límite del problema: LR 0.350 y XGBoost
0.356 de F1 medio (azar = 0.33). En 2026, ya en producción y fuera de
muestra, el modelo desplegado da F1 0.354.

Documentos: `RESULTADOS_OPTIMIZADOS/INVESTIGACION_COMPLETA.md` (todo lo
probado), `RESULTADOS_OPTIMIZADOS/JUSTIFICACION_LIMITE_DEL_MODELO.md` (por
qué no se puede más), `RESULTADOS_OPTIMIZADOS/GUIA_DEFENSA_TT.md` (defensa)
y `paper_review/paper.tex` (paper MICAI).

## Licencia

Uso académico.
