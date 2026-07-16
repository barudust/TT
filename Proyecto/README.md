# TT 2026-B164 — Plataforma de Clasificación Bursátil

Sistema web para clasificar señales de mercado (COMPRAR, VENDER, MANTENER)
usando un modelo de Machine Learning entrenado sobre datos reales de Yahoo
Finance. Incluye un frontend en React + TypeScript, una API en Flask y
persistencia en SQLite. Preparado para PWA y futuro empaquetado Android.

El modelo en producción es una **Regresión Logística elasticnet** (no
LSTM/CNN-LSTM): fue el ganador declarado tras comparar 4 familias de
modelos en `RESULTADOS_OPTIMIZADOS/docs/GUIA_PROGRESO.md` (F1-macro=0.417,
Sharpe test=1.25). Detalle completo en `docs/MODEL_INTEGRATION.md`.

## Tecnologías
- Frontend: React 18, TypeScript, Vite, Tailwind CSS 4, Recharts
- Temas: next-themes, tokens CSS en `src/styles/theme.css`
- Backend: Flask + CORS, Yahoo Finance (datos históricos reales), scikit-learn (inferencia)
- Base de datos: SQLite vía SQLAlchemy 2.0 (`docs/DATABASE.md`)
- PWA: Manifest y Service Worker

## Requisitos
- Node.js 18+
- Python 3.9+

## Instalación y Ejecución

### Frontend
```bash
npm install
npm run dev
```
Compilación:
```bash
npm run build
npm run preview
```

### API Local
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

Defínela en `.env` si lo deseas:
```
VITE_API_URL=http://localhost:8000
```

## Estructura del Proyecto (resumen)
```
.
├── api/
│   ├── main.py                # Servidor Flask: endpoints + orquestación + scheduler
│   ├── database.py            # Engine/sesión SQLAlchemy (lee DATABASE_URL de .env)
│   ├── models.py              # Esquema: Asset, OHLCVDaily, Prediction, Metric
│   ├── db_ops.py              # Upserts compartidos (refresco automático + overrides POST)
│   ├── ml/
│   │   ├── features.py        # Ingeniería de las 61 features (idéntica al entrenamiento)
│   │   ├── model.py           # Carga del modelo ganador + inferencia
│   │   └── artifacts/         # .pkl del modelo empaquetado con la API
│   ├── tests/                 # pytest, sin red real (yfinance mockeado)
│   ├── Dockerfile
│   └── requirements.txt / requirements-dev.txt
├── public/
│   ├── manifest.json          # PWA
│   └── service-worker.js      # PWA
├── src/
│   ├── app/
│   │   ├── pages/             # Home, StockDetail, Performance, About
│   │   ├── components/        # StockCard, MarketStatus, LoadingStates, ErrorState, ui/*
│   │   ├── Root.tsx           # Layout, navegación, toggle de tema
│   │   ├── App.tsx            # Toaster y Router
│   │   └── routes.ts          # Rutas
│   ├── config/api.ts          # Resolución de API base
│   ├── styles/                # Tailwind y tokens de tema
│   └── main.tsx               # Punto de entrada de React
├── docs/                      # Documentación técnica
│   ├── FRONTEND.md
│   ├── API.md
│   ├── DATABASE.md
│   ├── MODEL_INTEGRATION.md
│   └── THESIS_QA.md
├── Dockerfile / nginx.conf     # Imagen del frontend (build Vite + nginx)
├── docker-compose.yml          # Stack completo (api + frontend [+ postgres opcional])
└── vite.config.ts
```

## Documentación
- Arquitectura del Frontend: `docs/FRONTEND.md`
- Especificación de la API: `docs/API.md`
- Integración del Modelo en la API: `docs/MODEL_INTEGRATION.md`
- Guía de preguntas/respuestas para defensa: `docs/THESIS_QA.md`

## PWA y Android
El proyecto conserva manifest y service worker. Para Android puedes evaluar:
- Trusted Web Activity (TWA) si empaquetas la PWA
- Capacitor si requieres APIs nativas

## Licencia
Uso académico.

