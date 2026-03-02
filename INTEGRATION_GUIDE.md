# 📊 API de Señales de Trading - Documentación de Integración

## Descripción General

Esta documentación explica el formato de datos que tus modelos de Deep Learning deben generar y cómo almacenarlos en el sistema para que la aplicación web los consuma correctamente.

## 🔑 Sistema de Almacenamiento (KV Store)

Los datos se almacenan en un **Key-Value Store** de Supabase. Puedes usar las funciones del archivo `/supabase/functions/server/kv_store.tsx`:

```typescript
import * as kv from "./kv_store.tsx";

// Guardar datos
await kv.set("clave", valor);

// Obtener datos
const datos = await kv.get("clave");

// Eliminar datos
await kv.del("clave");
```

---

## 📋 Formato de Datos

### 1. Lista de Acciones con Señales Diarias

**Clave KV:** `"stocks:list"`

**Formato:**
```json
[
  {
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "currentPrice": 175.30,
    "signal": "buy",
    "confidence": 0.78,
    "lastUpdate": "2026-03-02T18:00:00Z"
  },
  {
    "symbol": "MSFT",
    "name": "Microsoft Corporation",
    "currentPrice": 412.50,
    "signal": "sell",
    "confidence": 0.65,
    "lastUpdate": "2026-03-02T18:00:00Z"
  }
  // ... resto de las 8 acciones
]
```

**Campos:**
- `symbol` (string): Ticker de la acción (ej. "AAPL")
- `name` (string): Nombre completo de la empresa
- `currentPrice` (number): Precio actual de cierre
- `signal` (string): Señal de trading: `"buy"`, `"sell"`, o `"hold"`
- `confidence` (number): Nivel de confianza del modelo (0-1, donde 1 = 100%)
- `lastUpdate` (string): Timestamp ISO 8601 de la última actualización

**Ejemplo de código para actualizar:**
```typescript
const signals = [
  {
    symbol: "AAPL",
    name: "Apple Inc.",
    currentPrice: 175.30,
    signal: "buy",
    confidence: 0.78,
    lastUpdate: new Date().toISOString()
  },
  // ... más acciones
];

await kv.set("stocks:list", signals);
```

---

### 2. Datos Históricos de Precios

**Clave KV:** `"stocks:{SYMBOL}:history:{DAYS}"`

Ejemplos:
- `"stocks:AAPL:history:30"` (últimos 30 días)
- `"stocks:AAPL:history:60"` (últimos 60 días)
- `"stocks:AAPL:history:90"` (últimos 90 días)

**Formato:**
```json
[
  {
    "date": "2025-12-01",
    "close": 170.50,
    "prediction": "buy",
    "actualDirection": "up"
  },
  {
    "date": "2025-12-02",
    "close": 172.30,
    "prediction": "buy",
    "actualDirection": "up"
  },
  {
    "date": "2025-12-03",
    "close": 171.80,
    "prediction": "hold",
    "actualDirection": "down"
  }
  // ... más días
]
```

**Campos:**
- `date` (string): Fecha en formato "YYYY-MM-DD"
- `close` (number): Precio de cierre del día
- `prediction` (string): Predicción que se hizo para ese día: `"buy"`, `"sell"`, o `"hold"`
- `actualDirection` (string): Dirección real del precio: `"up"`, `"down"`, o `"neutral"`

**Ejemplo de código:**
```typescript
const history30 = [
  { date: "2026-02-01", close: 170.50, prediction: "buy", actualDirection: "up" },
  { date: "2026-02-02", close: 172.30, prediction: "buy", actualDirection: "up" },
  // ... 28 días más
];

await kv.set("stocks:AAPL:history:30", history30);
await kv.set("stocks:AAPL:history:60", history60);
await kv.set("stocks:AAPL:history:90", history90);
```

---

### 3. Métricas de Rendimiento del Modelo

**Clave KV:** `"stocks:{SYMBOL}:metrics"`

Ejemplo: `"stocks:AAPL:metrics"`

**Formato:**
```json
{
  "accuracy": 0.72,
  "buyPrecision": 0.68,
  "sellPrecision": 0.75,
  "holdPrecision": 0.70,
  "f1Score": 0.71,
  "evaluationPeriod": 30,
  "totalPredictions": 150,
  "correctPredictions": 108
}
```

**Campos:**
- `accuracy` (number): Precisión global del modelo (0-1)
- `buyPrecision` (number): Precisión para señales de compra (0-1)
- `sellPrecision` (number): Precisión para señales de venta (0-1)
- `holdPrecision` (number): Precisión para señales de mantener (0-1)
- `f1Score` (number): F1-Score del modelo (0-1)
- `evaluationPeriod` (number): Número de días del período de evaluación
- `totalPredictions` (number): Total de predicciones realizadas
- `correctPredictions` (number): Número de predicciones correctas

**Ejemplo de código:**
```typescript
const metrics = {
  accuracy: 0.72,
  buyPrecision: 0.68,
  sellPrecision: 0.75,
  holdPrecision: 0.70,
  f1Score: 0.71,
  evaluationPeriod: 30,
  totalPredictions: 150,
  correctPredictions: 108
};

await kv.set("stocks:AAPL:metrics", metrics);
```

---

### 4. Historial de Señales con Resultados

**Clave KV:** `"stocks:{SYMBOL}:signals"`

Ejemplo: `"stocks:AAPL:signals"`

**Formato:**
```json
[
  {
    "date": "2026-03-01",
    "signal": "buy",
    "predictedPrice": 176.50,
    "actualPrice": 177.20,
    "correct": true
  },
  {
    "date": "2026-02-28",
    "signal": "hold",
    "predictedPrice": 175.80,
    "actualPrice": 175.30,
    "correct": true
  },
  {
    "date": "2026-02-27",
    "signal": "buy",
    "predictedPrice": 174.50,
    "actualPrice": 173.80,
    "correct": false
  }
  // ... más señales (últimos 10-20 días)
]
```

**Campos:**
- `date` (string): Fecha en formato "YYYY-MM-DD"
- `signal` (string): Señal emitida: `"buy"`, `"sell"`, o `"hold"`
- `predictedPrice` (number): Precio predicho para el siguiente día
- `actualPrice` (number): Precio real del siguiente día
- `correct` (boolean): Si la predicción fue correcta

**Ejemplo de código:**
```typescript
const recentSignals = [
  {
    date: "2026-03-01",
    signal: "buy",
    predictedPrice: 176.50,
    actualPrice: 177.20,
    correct: true
  },
  // ... más señales
];

await kv.set("stocks:AAPL:signals", recentSignals);
```

---

## 🤖 Script de Actualización Diaria

Aquí hay un ejemplo de cómo podrías estructurar tu script de Python que se ejecuta diariamente:

```python
import yfinance as yf
from datetime import datetime, timedelta
import requests

# Configuración
SUPABASE_URL = "https://tu-proyecto.supabase.co"
API_KEY = "tu-api-key"
STOCKS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM"]

def get_current_price(symbol):
    """Obtiene el precio actual de Yahoo Finance"""
    ticker = yf.Ticker(symbol)
    return ticker.history(period="1d")['Close'].iloc[-1]

def predict_signal(symbol, model):
    """
    Tu función de predicción usando LSTM/CNN-LSTM
    Debe devolver: signal ("buy"/"sell"/"hold") y confidence (0-1)
    """
    # ... tu código de predicción aquí ...
    return signal, confidence

def update_stock_signals():
    """Actualiza las señales diarias en Supabase"""
    signals = []
    
    for symbol in STOCKS:
        # Obtener precio actual
        current_price = get_current_price(symbol)
        
        # Generar predicción
        signal, confidence = predict_signal(symbol, model)
        
        # Agregar a la lista
        signals.append({
            "symbol": symbol,
            "name": get_company_name(symbol),
            "currentPrice": float(current_price),
            "signal": signal,
            "confidence": float(confidence),
            "lastUpdate": datetime.now().isoformat()
        })
    
    # Guardar en Supabase KV Store
    response = requests.post(
        f"{SUPABASE_URL}/functions/v1/make-server-8ca8c1f7/update-signals",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"key": "stocks:list", "value": signals}
    )
    
    print(f"Signals updated: {response.status_code}")

def update_historical_data(symbol, days=30):
    """Actualiza datos históricos con predicciones pasadas"""
    ticker = yf.Ticker(symbol)
    history = ticker.history(period=f"{days}d")
    
    historical_data = []
    for date, row in history.iterrows():
        # Obtener la predicción que hiciste para ese día (de tu base de datos)
        prediction = get_past_prediction(symbol, date)
        actual_direction = determine_direction(row['Close'], row['Open'])
        
        historical_data.append({
            "date": date.strftime("%Y-%m-%d"),
            "close": float(row['Close']),
            "prediction": prediction,
            "actualDirection": actual_direction
        })
    
    # Guardar en Supabase
    requests.post(
        f"{SUPABASE_URL}/functions/v1/update-history",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "key": f"stocks:{symbol}:history:{days}",
            "value": historical_data
        }
    )

def update_metrics(symbol):
    """Calcula y actualiza métricas del modelo"""
    # ... tu código para calcular métricas ...
    
    metrics = {
        "accuracy": accuracy,
        "buyPrecision": buy_precision,
        "sellPrecision": sell_precision,
        "holdPrecision": hold_precision,
        "f1Score": f1_score,
        "evaluationPeriod": 30,
        "totalPredictions": total,
        "correctPredictions": correct
    }
    
    # Guardar en Supabase
    requests.post(
        f"{SUPABASE_URL}/functions/v1/update-metrics",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"key": f"stocks:{symbol}:metrics", "value": metrics}
    )

# Ejecutar actualización diaria (ej. con cron job a las 6 PM)
if __name__ == "__main__":
    print("Starting daily update...")
    update_stock_signals()
    
    for symbol in STOCKS:
        update_historical_data(symbol, 30)
        update_historical_data(symbol, 60)
        update_historical_data(symbol, 90)
        update_metrics(symbol)
    
    print("Update completed!")
```

---

## 🔄 Endpoints de la API

La aplicación expone los siguientes endpoints:

### GET `/make-server-8ca8c1f7/stocks`
Obtiene la lista de todas las acciones con señales actuales.

**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "currentPrice": 175.30,
      "signal": "buy",
      "confidence": 0.78,
      "lastUpdate": "2026-03-02T18:00:00Z"
    }
    // ...
  ]
}
```

### GET `/make-server-8ca8c1f7/stocks/:symbol`
Obtiene detalles de una acción específica, incluyendo historial reciente de señales.

### GET `/make-server-8ca8c1f7/stocks/:symbol/history?days=30`
Obtiene datos históricos de precios (30, 60 o 90 días).

### GET `/make-server-8ca8c1f7/stocks/:symbol/metrics`
Obtiene métricas de rendimiento del modelo para una acción.

### GET `/make-server-8ca8c1f7/metrics`
Obtiene métricas de rendimiento de todas las acciones.

---

## 📌 Notas Importantes

1. **Actualización Diaria:** Las señales deben actualizarse después del cierre del mercado (aproximadamente 4:00 PM EST / 6:00 PM CST).

2. **Formato de Fechas:** Usa siempre ISO 8601 para timestamps (`YYYY-MM-DDTHH:mm:ssZ`) y formato `YYYY-MM-DD` para fechas simples.

3. **Valores Numéricos:** 
   - Precios: 2 decimales (ej. 175.30)
   - Confianza/Métricas: 2 decimales en escala 0-1 (ej. 0.78 = 78%)

4. **Señales Válidas:** Solo usa `"buy"`, `"sell"`, o `"hold"` (minúsculas).

5. **Direcciones Válidas:** Solo usa `"up"`, `"down"`, o `"neutral"` (minúsculas).

6. **Acciones Soportadas:** La app espera exactamente estas 8 acciones:
   - AAPL, MSFT, GOOGL, AMZN, TSLA, META, NVDA, JPM

---

## 🧪 Testing

Para probar que los datos están correctamente almacenados:

```typescript
// En /supabase/functions/server/index.tsx o en un script de prueba

// Verificar lista de acciones
const stocks = await kv.get("stocks:list");
console.log("Stocks:", stocks);

// Verificar historial
const history = await kv.get("stocks:AAPL:history:30");
console.log("History:", history);

// Verificar métricas
const metrics = await kv.get("stocks:AAPL:metrics");
console.log("Metrics:", metrics);
```

---

## 📞 Soporte

Si tienes dudas sobre el formato de datos o la integración, revisa los ejemplos en el archivo `/supabase/functions/server/stock_data.tsx` donde encontrarás la implementación completa con datos simulados.
