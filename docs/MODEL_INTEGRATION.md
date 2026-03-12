# Integración del Modelo en la API (Local)

Objetivo: incorporar un modelo de ML que produzca señales COMPRAR/VENDER/MANTENER y su confianza, sirviéndolas a través de `api/main.py`. El precio real mostrado proviene de datos de mercado, no del modelo.

## Ubicación
- Archivo: `api/main.py`
- Puntos de integración:
  - Cálculo de señales diarias: reemplazar/ajustar `generate_historical_data` o crear una función `infer_signals_with_model`.
  - Señal actual por acción: asignar `STOCKS_DATA[symbol]["signal"]` y `confidence`.
  - Métricas: calcular y asignar `METRICS_DATA[symbol]`.

## Flujo Propuesto
1. **Carga del modelo**
   - TensorFlow o PyTorch, según el proyecto.
   - Ejemplo (conceptual):
   ```python
   # Al inicio de main.py
   import tensorflow as tf
   model = tf.keras.models.load_model("ruta/al/modelo")
   ```

2. **Construcción de características**
   - A partir de OHLCV reciente (usando `yfinance` o tus propios datos).
   - Normalización y ventanas temporales coherentes con el entrenamiento.

3. **Inferencia**
   - Entrada: ventana temporal de características.
   - Salida: probabilidades o logits por clase.
   - Mapeo:
     - índice 0 → "buy"
     - índice 1 → "sell"
     - índice 2 → "hold"

4. **Asignación de resultados**
   - Para cada símbolo:
     - `STOCKS_DATA[symbol]["signal"] = "buy"|"sell"|"hold"`
     - `STOCKS_DATA[symbol]["confidence"] = float(probabilidad_max)`
     - Actualizar `SIGNALS_DATA[symbol]` con histórico de inferencias si corresponde (campos: `date`, `signal`, `actualPrice`, `correct` cuando aplique).

5. **Métricas**
   - Calcular `accuracy`, `precision` por clase, `f1Score`, y métricas financieras (retornos simulados).
   - Guardar en `METRICS_DATA[symbol]`.

## Ejemplo Esquemático
```python
def infer_signals_with_model(symbol, hist_df):
    # hist_df: DataFrame con columnas ['Open','High','Low','Close','Volume'] ya alineadas temporalmente
    window = build_window(hist_df)           # conversión a tensor [T, F]
    probs = model.predict(window[None, ...]) # [1, 3]
    pred_idx = int(probs.argmax(axis=1)[0])
    classes = ["buy","sell","hold"]
    signal = classes[pred_idx]
    confidence = float(probs[0,pred_idx])
    return signal, confidence
```

Integración en `initialize_data()`:
```python
for stock_config in STOCKS_CONFIG:
    symbol = stock_config["symbol"]
    hist_30 = HISTORICAL_DATA.get(f"{symbol}:30", [])
    # Convertir a DataFrame si lo necesitas para tu pipeline
    # hist_df = ...
    # signal, confidence = infer_signals_with_model(symbol, hist_df)
    # STOCKS_DATA[symbol]["signal"] = signal
    # STOCKS_DATA[symbol]["confidence"] = confidence
```

## Persistencia
- La implementación actual mantiene datos en memoria.
- Para producción: evaluar SQLite/PostgreSQL o cachés locales.

## Rendimiento
- Pre-cargar el modelo al iniciar el servidor.
- Reutilizar ventanas y evitar consultas redundantes a Yahoo Finance.
- Paralelizar inferencia si el hardware lo permite.

## Validación
- Verificar coherencia de las señales con datos reales.
- Reportar métricas (precisión por clase, F1, retorno simulado) en `GET /stocks/:symbol/metrics`.
