# Notas Técnicas - TradingSignals AI

## Arquitectura de la Aplicación

### Frontend (Cliente Web)
- **Framework**: React 18.3 con TypeScript
- **Routing**: React Router 7 (Data Mode)
- **Gráficos**: Recharts para visualizaciones
- **UI**: Tailwind CSS 4 + Radix UI components
- **Estado**: React Hooks (useState, useEffect)

### Backend (Supabase Edge Functions)
- **Runtime**: Deno
- **Framework**: Hono (ligero y rápido)
- **Base de datos**: Key-Value Store de Supabase
- **CORS**: Habilitado para todos los orígenes

### Flujo de Datos

```
Python Script (Diario)
  ↓ [Genera señales con LSTM/CNN-LSTM]
  ↓
KV Store (Supabase)
  ↓ [Almacena: señales, historial, métricas]
  ↓
API REST (Edge Functions)
  ↓ [Expone endpoints GET]
  ↓
Frontend React
  ↓ [Renderiza UI responsiva]
  ↓
Usuario
```

---

## Endpoints de la API

### Base URL
```
https://uawrdarivadefdvxbgoj.supabase.co/functions/v1/make-server-8ca8c1f7
```

### 1. GET /stocks
**Propósito**: Obtener lista de todas las acciones con señales actuales

**Respuesta**:
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
  ]
}
```

### 2. GET /stocks/:symbol
**Propósito**: Obtener detalle de una acción específica

**Parámetros**: 
- `symbol` (path): Símbolo de la acción (ej: AAPL)

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "currentPrice": 175.30,
    "signal": "buy",
    "confidence": 0.78,
    "lastUpdate": "2026-03-02T18:00:00Z",
    "recentSignals": [...]
  }
}
```

### 3. GET /stocks/:symbol/history
**Propósito**: Obtener historial de precios

**Parámetros**:
- `symbol` (path): Símbolo de la acción
- `days` (query, opcional): 30, 60 o 90 (default: 30)

**Respuesta**:
```json
{
  "success": true,
  "data": [
    {
      "date": "2026-01-15",
      "close": 172.30,
      "prediction": "buy",
      "actualDirection": "up"
    }
  ]
}
```

### 4. GET /stocks/:symbol/metrics
**Propósito**: Obtener métricas de rendimiento

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "accuracy": 0.72,
    "buyPrecision": 0.68,
    "sellPrecision": 0.75,
    "holdPrecision": 0.70,
    "f1Score": 0.71,
    "evaluationPeriod": 30,
    "totalPredictions": 150,
    "correctPredictions": 108
  }
}
```

### 5. GET /metrics
**Propósito**: Obtener métricas de todas las acciones

**Respuesta**:
```json
{
  "success": true,
  "data": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "accuracy": 0.72,
      ...
    }
  ]
}
```

---

## Estructura del KV Store

### Claves Utilizadas

```
stocks:list                      → Lista de todas las acciones
stocks:AAPL:history:30          → Historial de 30 días para AAPL
stocks:AAPL:history:60          → Historial de 60 días para AAPL
stocks:AAPL:history:90          → Historial de 90 días para AAPL
stocks:AAPL:metrics             → Métricas de rendimiento para AAPL
stocks:AAPL:signals             → Historial de señales recientes para AAPL
```

---

## Modelos de Deep Learning

### LSTM (Long Short-Term Memory)
- **Ventaja**: Excelente para series temporales
- **Arquitectura sugerida**:
  ```
  Input (secuencia de precios) → LSTM (128 unidades) → 
  Dropout (0.2) → LSTM (64 unidades) → 
  Dropout (0.2) → Dense (3 clases: buy/sell/hold)
  ```

### CNN-LSTM (Convolutional + LSTM)
- **Ventaja**: Captura patrones locales y temporales
- **Arquitectura sugerida**:
  ```
  Input → Conv1D (32 filtros) → MaxPooling → 
  LSTM (64 unidades) → Dropout (0.2) → 
  Dense (3 clases: buy/sell/hold)
  ```

### Features Sugeridas
- Precio de cierre normalizado
- Volumen normalizado
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Media móvil (7, 14, 21 días)

---

## Consideraciones de Rendimiento

### Optimizaciones Implementadas

1. **Caching en KV Store**
   - Los datos simulados se generan una vez y se cachean
   - Reduce llamadas repetitivas a funciones pesadas

2. **Lazy Loading**
   - Los datos históricos solo se cargan cuando se accede al detalle
   - Reduce payload en la lista principal

3. **Skeleton Loading**
   - Mejora percepción de velocidad
   - Muestra estructura mientras carga datos

4. **Error Handling**
   - Manejo graceful de errores de red
   - Mensajes informativos al usuario
   - Retry automático opcional

---

## Seguridad

### API Key
- Se usa `publicAnonKey` (clave pública)
- Safe para uso en frontend
- Solo permite operaciones de lectura

### CORS
- Habilitado para todos los orígenes (`*`)
- Necesario para desarrollo y producción

### Rate Limiting
- Considera implementar rate limiting en producción
- Supabase tiene límites por defecto

---

## Datos Simulados vs. Reales

### Actualmente (Simulados)
- Precios basados en valores históricos realistas
- Señales generadas aleatoriamente
- Métricas coherentes (60-75% accuracy)
- Backtesting simulado con distribución realista

### Para Producción (Reales)
1. Conecta Yahoo Finance API para precios reales
2. Ejecuta modelos LSTM/CNN-LSTM entrenados
3. Almacena predicciones reales en KV Store
4. Calcula métricas basadas en resultados históricos

---

## Próximos Pasos para Producción

### 1. Entrenar Modelos
```python
# Ejemplo simplificado
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler

# Preparar datos
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# Crear modelo LSTM
model = tf.keras.Sequential([
    tf.keras.layers.LSTM(128, return_sequences=True, input_shape=(sequence_length, n_features)),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.LSTM(64),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(3, activation='softmax')  # buy/sell/hold
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_val, y_val))
```

### 2. Implementar Script de Actualización
- Usar `update_script_example.py` como base
- Configurar cron job para ejecución diaria
- Logging para debugging

### 3. Conectar Yahoo Finance
```python
import yfinance as yf

ticker = yf.Ticker("AAPL")
data = ticker.history(period="1d")
current_price = data['Close'].iloc[-1]
```

### 4. Calcular Métricas Reales
```python
from sklearn.metrics import accuracy_score, precision_score, f1_score

y_true = actual_directions  # "up", "down", "neutral"
y_pred = predicted_signals  # "buy", "sell", "hold"

accuracy = accuracy_score(y_true, y_pred)
precision = precision_score(y_true, y_pred, average='weighted')
f1 = f1_score(y_true, y_pred, average='weighted')
```

---

## Testing

### Frontend
```bash
# Verificar que la app carga
# Verificar navegación entre pantallas
# Verificar gráficos se renderizan
# Verificar botón de actualizar funciona
# Verificar diseño responsive en mobile
```

### Backend
```bash
# Test endpoints
curl https://uawrdarivadefdvxbgoj.supabase.co/functions/v1/make-server-8ca8c1f7/stocks

# Test con parámetros
curl "https://uawrdarivadefdvxbgoj.supabase.co/functions/v1/make-server-8ca8c1f7/stocks/AAPL/history?days=60"
```

### Datos
```typescript
// Verificar formato en consola del navegador
const response = await fetch(url);
const data = await response.json();
console.log(JSON.stringify(data, null, 2));
```

---

## Troubleshooting

### Problema: "No se pudieron cargar los datos"
- Verificar que Supabase Edge Functions esté corriendo
- Verificar que las claves en `/utils/supabase/info.tsx` sean correctas
- Revisar logs del navegador (F12 → Console)
- Verificar que el KV Store tenga datos

### Problema: Gráficos no se muestran
- Verificar que `recharts` esté instalado
- Verificar que los datos tengan el formato correcto
- Revisar errores en consola

### Problema: Métricas incorrectas
- Verificar formato de datos históricos
- Asegurar que `prediction` y `actualDirection` coincidan con el schema
- Revisar lógica de cálculo en `stock_data.tsx`

---

## Licencia y Uso Académico

Este proyecto es parte del Trabajo Terminal TT 2026-B164 de ESCOM-IPN.

**USO EXCLUSIVAMENTE ACADÉMICO**

No está autorizado para:
- Uso comercial
- Asesoramiento financiero real
- Operaciones de trading reales
- Distribución sin autorización

---

## Contacto y Soporte

Para preguntas técnicas sobre la implementación:
1. Revisa `INTEGRATION_GUIDE.md`
2. Revisa código en `/supabase/functions/server/stock_data.tsx`
3. Consulta ejemplos en `update_script_example.py`

**Fecha de última actualización**: Marzo 2026  
**Versión**: 1.0.0
