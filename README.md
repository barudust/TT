# TT 2026-B164 — Plataforma de Clasificación Bursátil

Sistema web para clasificar señales de mercado (COMPRAR, VENDER, MANTENER) mediante modelos de Deep Learning. Incluye un frontend en React + TypeScript y una API en Flask. Preparado para PWA y futuro empaquetado Android.

## Tecnologías
- Frontend: React 18, TypeScript, Vite, Tailwind CSS 4, Recharts
- Temas: next-themes, tokens CSS en `src/styles/theme.css`
- Backend: Flask + CORS, Yahoo Finance (datos históricos), punto de integración de modelo ML
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
Por defecto sirve en `http://localhost:8000`.

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
│   ├── main.py                # Servidor Flask (punto de integración del modelo)
│   └── requirements.txt
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
│   ├── MODEL_INTEGRATION.md
│   └── THESIS_QA.md
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

