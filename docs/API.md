# API Local (Flask) — Especificación

Servidor HTTP que expone datos de acciones, historial, métricas y señales. Punto de integración del modelo ML.

## Tecnologías
- Flask + CORS
- yfinance (datos históricos)

## Endpoints

### Salud
- `GET /health`
  - Respuesta: `{ "status": "ok" }`

### Acciones
- `GET /stocks`
  - Devuelve lista de acciones con señal actual:
  - Ejemplo:
```json
{
  "success": true,
  "data": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "currentPrice": 175.3,
      "signal": "buy",
      "confidence": 0.78,
      "lastUpdate": "2026-03-02T18:00:00Z"
    }
  ]
}
```

- `GET /stocks/:symbol`
  - Incluye señales recientes y datos de compañía:
```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "currentPrice": 175.3,
    "signal": "buy",
    "confidence": 0.78,
    "lastUpdate": "2026-03-02T18:00:00Z",
    "recentSignals": [
      { "date": "2026-02-20", "signal": "buy", "predictedPrice": 176.1, "actualPrice": 175.9, "correct": true }
    ],
    "companyInfo": {
      "sector": "Technology",
      "industry": "Consumer Electronics"
    }
  }
}
```

- `POST /stocks`
  - Actualiza varias acciones a la vez. Cuerpo: lista de objetos con clave `symbol`.
- `POST /stocks/:symbol`
  - Actualiza una acción. Cuerpo: objeto con los campos que desees persistir.

### Historial
- `GET /stocks/:symbol/history?days=30|60|90`
  - Devuelve arreglo de observaciones con `date`, `close`, `prediction`, `actualDirection`.
- `POST /stocks/:symbol/history?days=N`
  - Reemplaza el historial para esa ventana.

### Métricas
- `GET /stocks/:symbol/metrics`
  - Métricas por acción: `accuracy`, `buyPrecision`, `sellPrecision`, `holdPrecision`, `f1Score`, `cumulativeReturn`, `sharpeRatio`, `winRate`, `profitFactor`, `maxDrawdown`, `numberOfTrades`, `exposure`, `finalCapital`.
- `GET /metrics`
  - Métricas globales agregadas.
- `POST /stocks/:symbol/metrics`
  - Sobrescribe las métricas de una acción.

### Señales
- `POST /stocks/:symbol/signals`
  - Sobrescribe señales recientes (`date`, `signal`, `predictedPrice`, `actualPrice`, `correct`).

## Inicialización
- La función `initialize_data()` carga Yahoo Finance, deriva señales y métricas, y precalcula ventanas 30/60/90 días.
- El modelo ML puede sustituir o complementar esta generación (ver `docs/MODEL_INTEGRATION.md`).

## Consideraciones
- Zona horaria: se usa `timezone.utc`.
- Fuentes de datos: yfinance puede tener límites o retrasos; considerar caché local.
- CORS: abierto para facilitar desarrollo; ajustar en producción.

