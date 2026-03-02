# TradingSignals AI

Predicción bursátil con Deep Learning usando LSTM y CNN-LSTM

## Descripción

Aplicación de trading signals que genera predicciones diarias (BUY, SELL, HOLD) para 8 acciones de alta capitalización:
- AAPL, MSFT, GOOGL, AMZN, TSLA, META, NVDA, JPM

**Nota importante:** Este es un proyecto académico (TT 2026-B164 - ESCOM IPN). Las señales son solo con fines educativos y de investigación, no constituyen asesoramiento financiero.

---

## Requisitos previos

- **Node.js** v18+ (https://nodejs.org/)
- **Python** v3.9+ (https://www.python.org/)
- **Git** (https://git-scm.com/)

---

## Instalación rápida

```bash
# 1. Clonar el repositorio
git clone https://github.com/barudust/TT.git
cd TT

# 2. Instalar dependencias de Node
npm install

# 3. Instalar dependencias de Python
cd api
pip install -r requirements.txt
cd ..
```

---

## Ejecución

Abrir 2 terminales:

**Terminal 1 - API (Python):**
```bash
cd api
python main.py
```
Verás: `[*] API iniciada en http://localhost:8000`

**Terminal 2 - App (React):**
```bash
npm run dev
```
Abre: http://localhost:5173

---

## Instalación como PWA en Android

La app está configurada como **Progressive Web App (PWA)**, funcionando como una app nativa en tu celular.

### Pasos para instalar en Android:

1. Abre la app en el navegador: **http://localhost:5173/**
2. Toca el **menú del navegador** (⋮ tres puntos arriba a la derecha)
3. Selecciona **"Instalar app"** o **"Añadir a pantalla de inicio"**
4. Confirma y la app aparecerá en tu pantalla de inicio

**Nota:** Si desplegaste en producción (no es localhost), el botón aparecerá automáticamente.

### Características de la PWA:

✅ Se instala como app nativa (sin App Store)
✅ Funciona offline (cachea los datos)
✅ Acceso rápido desde pantalla de inicio
✅ Interfaz a pantalla completa
✅ Notificaciones (preparadas para implementar)

---

## Estructura del proyecto

```
TT/
├── public/
│   ├── manifest.json          # Configuración PWA
│   └── service-worker.js      # Cache offline
├── src/
│   ├── app/
│   │   ├── pages/
│   │   │   ├── Home.tsx       # Lista de acciones
│   │   │   ├── StockDetail.tsx # Detalle + gráficos + métricas
│   │   │   ├── Performance.tsx # Comparativa de rendimiento
│   │   │   └── About.tsx      # Información del proyecto
│   │   ├── Root.tsx           # Layout principal
│   │   └── routes.ts          # Configuración de rutas
│   └── main.tsx               # Entrada React
├── api/
│   ├── main.py                # API Flask (11 endpoints)
│   ├── requirements.txt        # Dependencias Python
│   └── send_data.py           # Script para enviar datos simulados
├── index.html                 # PWA manifest + service worker
├── package.json               # Dependencias Node
├── vite.config.ts             # Config Vite
└── tailwind.config.ts         # Estilos Tailwind
```

---

## API Endpoints

- `GET /stocks` - Lista de todas las acciones con señales
- `GET /stocks/<symbol>` - Detalle de una acción específica
- `GET /stocks/<symbol>/history?days=30` - Histórico de precios
- `GET /stocks/<symbol>/metrics` - Métricas de rendimiento
- `GET /metrics` - Métricas globales de todas las acciones

---

## Tecnologías

**Frontend:**
- React 18 + TypeScript
- Vite (bundler)
- Tailwind CSS
- Recharts (gráficos)
- React Router v7

**Backend:**
- Flask (Python)
- CORS habilitado

**Deep Learning (modelos conceptuales):**
- LSTM (Long Short-Term Memory)
- CNN-LSTM (Arquitectura híbrida)
- Datos: Yahoo Finance

---

## Commits en español

Todos los commits están en español. Ejemplos:

```bash
git commit -m "Agregar navegación rápida de 8 acciones"
git commit -m "Mejorar tabla de historial de señales"
git commit -m "Actualizar métricas de estrategia"
```

---

## Desarrolladores

- Reyes Ramos David
- Polvo Cuatianquiz Jesús Baruc

**Directores:**
- Abdiel Reyes Vega
- Emmanuel Juarez Carvajal

**Institución:** Escuela Superior de Cómputo (ESCOM) - Instituto Politécnico Nacional (IPN)

---

## Licencia

Proyecto académico - 2026
