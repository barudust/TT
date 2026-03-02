# 🚀 Guía de Ejecución - TradingSignals AI (API Local)

Has convertido el proyecto para usar una **API local con FastAPI** en lugar de Supabase. Aquí está cómo ejecutar todo.

---

## 📋 Requisitos Previos

- **Python 3.8+** instalado
- **Node.js 16+** instalado
- **npm** instalado

---

## ⚙️ Setup Inicial (Una sola vez)

### 1. Instalar dependencias de Python (API)

Abre una terminal y navega a la carpeta del proyecto:

```bash
cd c:\Users\baruc\Documents\Escuela\TT-Fin\Proyecto
```

Instala las dependencias de la API:

```bash
cd api
pip install -r requirements.txt
```

O si usas `pip3`:

```bash
pip3 install -r requirements.txt
```

### 2. Instalar dependencias de Node (Frontend)

En otra terminal, navega a la raíz del proyecto:

```bash
cd c:\Users\baruc\Documents\Escuela\TT-Fin\Proyecto
npm install
```

---

## 🏃 Ejecutar la Aplicación (Cada vez que trabajes)

Necesitas **2 terminales abiertas simultáneamente**:

### Terminal 1: Ejecutar la API local

```bash
cd c:\Users\baruc\Documents\Escuela\TT-Fin\Proyecto\api
python main.py
```

O si usas Python 3:

```bash
python3 main.py
```

**✅ Resultado esperado:**
```
INFO:     Started server process [xxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

La API estará disponible en: **http://localhost:8000**

### Terminal 2: Ejecutar el Frontend

```bash
cd c:\Users\baruc\Documents\Escuela\TT-Fin\Proyecto
npm run dev
```

**✅ Resultado esperado:**
```
  VITE v6.3.5  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Press h + enter to show help
```

El frontend estará disponible en: **http://localhost:5173**

---

## 📱 Usar la Aplicación

1. Abre **http://localhost:5173** en tu navegador
2. Deberías ver la pantalla con las 8 acciones y sus señales de trading
3. Los datos se cargan automáticamente desde la API local

---

## 📤 Enviar Datos Simulados a la API

Una vez que **ambas terminales están corriendo**, puedes actualizar los datos en tiempo real.

Abre una **tercera terminal** y ejecuta:

```bash
cd c:\Users\baruc\Documents\Escuela\TT-Fin\Proyecto\api
python send_data.py
```

Verás un menú como este:

```
============================================================
🤖 TradingSignals AI - Generador de Datos Simulados
============================================================

Opciones:
1. Enviar datos de TODAS las acciones
2. Enviar datos de una acción específica
3. Enviar datos de múltiples acciones

Elige una opción (1-3):
```

**Opciones:**

- **Opción 1:** Actualiza las 8 acciones con nuevas señales (BUY, SELL, HOLD), precios y confianzas aleatorias
  ```
  Elige una opción (1-3): 1
  ```

- **Opción 2:** Actualiza una acción específica
  ```
  Elige una opción (1-3): 2
  Acciones disponibles: AAPL, MSFT, GOOGL, AMZN, TSLA, META, NVDA, JPM
  Ingresa el símbolo: AAPL
  ```

- **Opción 3:** Actualiza múltiples acciones
  ```
  Elige una opción (1-3): 3
  Acciones disponibles: AAPL, MSFT, GOOGL, AMZN, TSLA, META, NVDA, JPM
  Ingresa los símbolos separados por comas (ej: AAPL,MSFT,GOOGL): AAPL,MSFT,NVDA
  ```

**Después de enviar datos, actualiza la página en el navegador (F5) para ver los cambios.**

---

## 🔗 Endpoints Disponibles de la API

La API está documentada automáticamente en: **http://localhost:8000/docs**

### Endpoints principales:

#### **GET (Leer datos)**
- `GET /stocks` - Lista todas las acciones
- `GET /stocks/{symbol}` - Detalle de una acción
- `GET /stocks/{symbol}/history?days=30` - Histórico de precios
- `GET /stocks/{symbol}/metrics` - Métricas de rendimiento
- `GET /metrics` - Métricas de todas las acciones

#### **POST (Enviar datos)**
- `POST /stocks` - Actualizar todas las acciones
- `POST /stocks/{symbol}` - Actualizar una acción
- `POST /stocks/{symbol}/history` - Actualizar histórico
- `POST /stocks/{symbol}/metrics` - Actualizar métricas
- `POST /stocks/{symbol}/signals` - Actualizar señales

---

## 🐛 Solucionar Problemas

### "Error: Cannot find module 'fastapi'"
**Solución:** Asegúrate de haber instalado las dependencias:
```bash
cd api
pip install -r requirements.txt
```

### "Error: Cannot connect to http://localhost:8000"
**Solución:** La API no está corriendo. Ejecuta `python main.py` en la terminal 1.

### "Error: Cannot find module '@' in pages"
**Solución:** Asegúrate de haber ejecutado `npm install` en la raíz del proyecto.

### Los datos no se actualizan en la app
**Solución:** Después de ejecutar `send_data.py`, actualiza la página del navegador (Ctrl+R o F5).

---

## 📝 Estructura de Datos

### Endpoint: `POST /stocks`

Envía un array de acciones:

```json
[
  {
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "currentPrice": 175.30,
    "signal": "buy",
    "confidence": 0.78,
    "lastUpdate": "2026-03-02T18:00:00Z"
  }
]
```

**Campos:**
- `symbol`: Código de la acción (AAPL, MSFT, etc.)
- `name`: Nombre completo de la empresa
- `currentPrice`: Precio actual
- `signal`: "buy", "sell", o "hold"
- `confidence`: Confianza del modelo (0-1)
- `lastUpdate`: Timestamp de última actualización (ISO 8601)

---

## 💡 Próximos Pasos

Cuando tengas tus modelos de Deep Learning listos:

1. **Modifica `/api/main.py`** para que en lugar de generar datos simulados, llame a tus modelos
2. **Conecta tus modelos** (LSTM, CNN-LSTM) para que devuelvan predicciones reales
3. **Integra APIs financieras** (Yahoo Finance, Alpha Vantage) para obtener precios reales
4. **Configura un scheduler** (APScheduler) para actualizar predicciones automáticamente cada día

---

## 🎯 Resumen

```
Terminal 1:  python api/main.py          ← API en puerto 8000
Terminal 2:  npm run dev                 ← Frontend en puerto 5173
Terminal 3:  python api/send_data.py     ← Enviar datos (opcional)

Navegador:   http://localhost:5173       ← Abre la app aquí
```

¡Listo! 🚀
