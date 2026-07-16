# API Local (Flask) — Especificación

Servidor HTTP que expone datos de acciones, historial, métricas y señales
**generadas por el modelo real** (Regresión Logística elasticnet — ver
`docs/MODEL_INTEGRATION.md`), respaldadas en SQLite (`docs/DATABASE.md`).

## Tecnologías
- Flask + CORS
- yfinance (datos históricos reales, no simulados)
- SQLAlchemy 2.0 + SQLite
- scikit-learn (inferencia del modelo)

## Endpoints

### Salud
- `GET /health`
  - Respuesta: `{ "status": "ok" }`

### Acciones
- `GET /stocks`
  - Devuelve lista de acciones con señal actual del modelo:
```json
{
  "success": true,
  "data": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "currentPrice": 327.5,
      "signal": "hold",
      "confidence": 0.39,
      "lastUpdate": "2026-07-16T04:32:10.47Z"
    }
  ]
}
```

- `GET /stocks/:symbol`
  - Incluye señales recientes (últimos 10 días reales) e info de la
    compañía (de `yfinance`):
```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "currentPrice": 327.5,
    "signal": "hold",
    "confidence": 0.39,
    "lastUpdate": "2026-07-16T04:32:10.47Z",
    "recentSignals": [
      { "date": "2026-07-15", "signal": "hold", "actualPrice": 327.5, "correct": false }
    ],
    "companyInfo": {
      "sector": "Technology",
      "industry": "Consumer Electronics",
      "marketCap": 4810109091840,
      "peRatio": 38.17
    }
  }
}
```

- `POST /stocks`, `POST /stocks/:symbol`
  - Sobrescriben la caché en memoria y hacen upsert best-effort en SQLite
    (fila de hoy en `predictions`/`ohlcv_daily`, `model_version="manual-override"`).
    Pensados para pruebas/demos puntuales, no para el flujo real de datos.

### Historial
- `GET /stocks/:symbol/history?days=30|60|90`
  - Arreglo de observaciones reales: `date`, `open`, `close`, `high`,
    `low`, `volume`, `prediction` (señal del modelo ese día),
    `confidence`, `actualDirection` (movimiento real del precio al día
    siguiente: `up`/`down`/`neutral`, umbral ±1%).
- `POST /stocks/:symbol/history?days=N`
  - Reemplaza el historial en caché para esa ventana y hace upsert de cada
    fila en `ohlcv_daily`/`predictions`.

### Métricas
- `GET /stocks/:symbol/metrics`
  - Métricas sobre la ventana de 30 días: `accuracy`, `f1_macro`,
    `f1_buy`, `f1_sell`, `cumulativeReturn`, `return_vs_bh`,
    `sharpeRatio`, `maxDrawdown`, `winRate`, `profitFactor`,
    `numberOfTrades`, `exposure`, `finalCapital`,
    `signal_buy_pct`/`signal_hold_pct`/`signal_sell_pct`.
    Ver mapeo completo en `docs/API_FRONTEND_METRICS.md`.
- `GET /metrics`
  - Lo mismo para las 7 acciones, en arreglo.
- `POST /stocks/:symbol/metrics`
  - Sobrescribe las métricas en caché y hace upsert en `metrics`
    (ventana 30 días, por convención).

### Señales
- `POST /stocks/:symbol/signals`
  - Sobrescribe señales recientes en caché y hace upsert en `predictions`.

### Administración
- `POST /admin/refresh`
  - Vuelve a descargar OHLCV + contexto de mercado, recorre el modelo y
    repuebla caché + base de datos, sin reiniciar el proceso. Útil para
    demos en vivo. Puede tardar ~20-40s (7 tickers × descarga Yahoo).
  - Esto mismo corre automáticamente cada día hábil a las 16:30 hora de
    Nueva York (`REFRESH_HOUR`/`REFRESH_MINUTE` en `.env`), 30 min después
    del cierre de NYSE, vía APScheduler (`start_scheduler()` en `main.py`).
    Si se despliega con varios workers (gunicorn `-w N`), cada worker
    tendría su propio scheduler y el refresco correría N veces — para ese
    caso conviene mover el scheduler a un proceso/cron externo que llame a
    `POST /admin/refresh` una sola vez.

## Inicialización

`initialize_data()` (llamada al arrancar `api/main.py` y por
`POST /admin/refresh`):
1. Descarga contexto de mercado (SPY, VIX) una sola vez.
2. Por cada uno de los 7 tickers: descarga ~3 años de OHLCV, calcula las
   61 features técnicas, corre el modelo sobre toda la serie disponible.
3. Si Yahoo Finance falla para un ticker (o para el contexto de mercado),
   ese ticker se omite del catálogo — no se rellena con datos simulados
   (ver justificación en `docs/MODEL_INTEGRATION.md`).
4. Calcula métricas de clasificación + financieras sobre las ventanas de
   30/60/90 días y persiste todo en SQLite.

## Consideraciones
- Zona horaria: `timezone.utc` para el timestamp `lastUpdate`; el
  *scheduler* automático sí usa `America/New_York` (con DST manejado por
  `zoneinfo`/`tzdata`) para disparar después del cierre real de NYSE.
  Las fechas de las velas OHLCV son las que reporta Yahoo Finance
  (calendario NYSE, sin conversión adicional).
- Fuentes de datos: yfinance puede tener límites de tasa o datos
  retrasados; por eso existe `/admin/refresh` en vez de recalcular en
  cada request.
- CORS: abierto para facilitar desarrollo; ajustar en producción.
