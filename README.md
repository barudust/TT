# TT 2026-B164 — Plataforma de Clasificación Bursátil

Trabajo Terminal: predicción de señales de trading (COMPRAR/VENDER/MANTENER)
para siete acciones tecnológicas de EE. UU. (AAPL, NVDA, TSLA, AMZN, MSFT,
GOOGL, META), comparando empíricamente cinco arquitecturas de ML/DL, y una
plataforma web que sirve las señales del modelo ganador con datos e
inferencia reales.

El modelo en producción es una **Regresión Logística elasticnet** (no
LSTM/CNN-LSTM): fue el ganador declarado tras comparar 4 familias de
modelos en `RESULTADOS_OPTIMIZADOS/docs/GUIA_PROGRESO.md` (F1-macro=0.417,
Sharpe test=1.25). Detalle completo en `docs/MODEL_INTEGRATION.md`.

**Estado actual y qué falta**: ver [`STATUS.md`](STATUS.md).

## Estructura del repositorio

```
.
├── api/                        # API Flask (endpoints, modelo ML, SQLite)
├── Frontend/                   # SPA React + TypeScript (Vite, Tailwind, PWA)
├── docs/                       # Documentación técnica de la plataforma web
├── scripts_opt/                # Pipeline de optimización que generó RESULTADOS_OPTIMIZADOS/
├── RESULTADOS_OPTIMIZADOS/     # Resultados de todos los experimentos + papers/bitácora
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
reales, calcula las 61 features y corre el modelo (tarda ~20-40s para los
7 tickers); después se refresca solo cada día hábil a las 16:30 hora de
Nueva York (configurable, ver `api/.env.example`), o a demanda con
`POST /admin/refresh`.

### Tests de la API
```bash
pip install -r api/requirements-dev.txt
cd api && pytest
```
No hacen llamadas de red reales (Yahoo Finance se mockea) — cubren las 61
features, la carga/inferencia del modelo y el flujo completo de
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

- **¿Quiero entender qué modelo ganó y por qué?** →
  [`RESULTADOS_OPTIMIZADOS/docs/GUIA_PROGRESO.md`](RESULTADOS_OPTIMIZADOS/docs/GUIA_PROGRESO.md)
  (bitácora completa) o [`RESULTADOS_OPTIMIZADOS/docs/PAPER_FINAL.md`](RESULTADOS_OPTIMIZADOS/docs/PAPER_FINAL.md)
  (redacción tipo paper).
- **¿Quiero reproducir el entrenamiento?** → los scripts en
  [`scripts_opt/`](scripts_opt) (ver `scripts_opt/common.py` para configuración
  de tickers/splits/rutas) leen de `tesis_ml_stocks/01_raw_datasets/` y
  escriben en `RESULTADOS_OPTIMIZADOS/`. Se corren desde la raíz del repo.
  Ver [`scripts_opt/README.md`](scripts_opt/README.md) para qué scripts son
  la fuente de verdad (incl. el que generó el `.pkl` en producción) y
  cuáles son iteraciones (v2/v3/v4) ya superadas.
- **¿Qué es `scripts_v1/`?** → la primera pasada del pipeline (antes de la
  fase de optimización). Ver [`scripts_v1/README.md`](scripts_v1/README.md)
  para qué sigue vigente y qué quedó superado.

## Documentación de la plataforma web

- Arquitectura del Frontend: `docs/FRONTEND.md`
- Especificación de la API: `docs/API.md`
- Modelo y base de datos: `docs/MODEL_INTEGRATION.md`, `docs/DATABASE.md`
- Guía de preguntas/respuestas para defensa: `docs/THESIS_QA.md`
- Despliegue en Render (auto-deploy por push): `docs/DEPLOY_RENDER.md`

## PWA y Android
El proyecto conserva manifest y service worker (`Frontend/public/`). Para
Android puedes evaluar:
- Trusted Web Activity (TWA) si empaquetas la PWA
- Capacitor si requieres APIs nativas

## Resumen del hallazgo principal

El modelo con mejor desempeño, tras comparar Regresión Logística, XGBoost,
LightGBM, LSTM y CNN-LSTM en tres particiones temporales, es una
**Regresión Logística con regularización elasticnet** entrenada globalmente
sobre los 7 tickers (F1-macro = 0.417, Sharpe de backtest = 1.25 en el
experimento principal). Es el modelo que corre en producción en `api/`.
Detalle completo en `RESULTADOS_OPTIMIZADOS/docs/GUIA_PROGRESO.md`.

## Licencia

Uso académico.
