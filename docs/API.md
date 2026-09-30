# API Local (Flask) — Especificación

Servidor HTTP que expone datos de acciones, historial, métricas y señales
**generadas por el modelo real** (Regresión Logística — ver
`docs/MODEL_INTEGRATION.md` y `GET /model`), respaldadas en SQLite
(`docs/DATABASE.md`). Ningún valor que sirve la API es simulado: precios de
Yahoo Finance, señales y probabilidades del modelo, y resultados evaluados
contra el precio real del día siguiente.

## Tecnologías
- Flask + CORS
- yfinance (datos históricos reales, no simulados)
- SQLAlchemy 2.0 + SQLite
- scikit-learn (inferencia del modelo y F1)

## Endpoints

### Salud
- `GET /health`
  - Respuesta: `{ "status": "ok" }`

### Modelo
- `GET /model`
  - Describe el modelo cargado, leído del `.pkl` (no texto fijo):
    algoritmo, regularización, número de variables, rango de
    entrenamiento, estrategia global y definición de la etiqueta.
```json
{
  "success": true,
  "data": {
    "version": "LR-v8-interactions-produccion",
    "algorithm": "LogisticRegression",
    "penalty": "l2", "C": 0.000165, "classWeight": "balanced",
    "scaler": "RobustScaler",
    "nFeatures": 76, "nFeaturesBase": 61, "nInteractions": 15,
    "trainRange": "2018-01-01 a 2025-12-31 (todos los datos)",
    "nTrainSamples": 14063,
    "strategy": "global (un solo modelo para los 7 tickers)",
    "target": { "horizonDays": 1, "percentileSell": 30, "percentileBuy": 70, "rollingWindowDays": 252 }
  }
}
```

### Estado del mercado
- `GET /market-status`
  - `isOpen` / `isTradingDay` según el horario regular de NYSE
    (L-V 09:30-16:00 America/New_York) y sus feriados oficiales 2026-2027
    (`NYSE_HOLIDAYS` en `main.py`; agregar los de años siguientes cuando
    NYSE los publique).

### Acciones
- `GET /stocks`
  - Lista de acciones con la señal del modelo para el siguiente día hábil:
```json
{
  "success": true,
  "data": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "currentPrice": 329.4,
      "signal": "hold",
      "confidence": 0.384,
      "probabilities": { "buy": 0.3008, "hold": 0.384, "sell": 0.3151 },
      "dataDate": "2026-09-29",
      "lastUpdate": "2026-09-30T18:52:03.120546Z",
      "modelVersion": "LR-v8-interactions-produccion"
    }
  ]
}
```
  - `confidence` = probabilidad que el modelo da a la señal elegida
    (máximo de `probabilities`). Con tres clases, azar = 0.33.
  - `dataDate` = fecha del cierre con el que se calculó la señal. Mientras
    NYSE está abierto, Yahoo devuelve la vela del día en curso con precio
    intradía; esa fila se descarta (`sin_vela_en_curso`) para no calcular
    señales con un precio que todavía no es el cierre.
  - `lastUpdate` = momento (UTC, ISO-8601) en que la API recalculó.

- `GET /stocks/:symbol`
  - Lo anterior + las últimas 10 señales (la más reciente primero) con su
    resultado real + info de la compañía (de `yfinance`):
```json
"recentSignals": [
  { "date": "2026-09-29", "signal": "hold", "confidence": 0.3856, "actualPrice": 227.21,
    "actualSignal": null, "nextReturn": null, "correct": null },
  { "date": "2026-09-28", "signal": "hold", "confidence": 0.3611, "actualPrice": 228.86,
    "actualSignal": "hold", "nextReturn": -0.721, "correct": true }
]
```
  - `nextReturn` = % del cierre de `date` al cierre del siguiente día hábil.
  - `actualSignal` = la señal que habría sido correcta, con la **misma
    etiqueta del entrenamiento** (`api/ml/target.py`): BUY si el retorno
    quedó ≥ percentil 70 de los 252 días previos, SELL si ≤ percentil 30,
    HOLD en otro caso.
  - `correct` = `signal == actualSignal`; `null` mientras no exista el
    cierre siguiente (se resuelve en el siguiente refresco).

### Historial
- `GET /stocks/:symbol/history?days=30|60|90`
  - Una fila por día: `date`, `open`, `close`, `high`, `low`, `volume`,
    `prediction`, `confidence`, `probabilities`, `actualSignal`,
    `nextReturn`, `correct` (mismas definiciones que arriba).

### Métricas
- `GET /stocks/:symbol/metrics?days=30|60|90` (default 30)
- `GET /metrics?days=30|60|90` — lo mismo para las 7 acciones.
  - Definiciones exactas en `docs/API_FRONTEND_METRICS.md`.

### Overrides manuales (desactivados)
- `POST /stocks`, `POST /stocks/:symbol`, `POST /stocks/:symbol/history`,
  `POST /stocks/:symbol/metrics`, `POST /stocks/:symbol/signals`
  - Permiten escribir valores que **no** salen del modelo, así que
    responden `403` salvo que se arranque la API con
    `ENABLE_MANUAL_OVERRIDES=1` (solo para pruebas locales). Lo que
    escriben se marca en SQLite con `model_version="manual-override"`.

### Administración
- `POST /admin/refresh`
  - Vuelve a descargar OHLCV + contexto de mercado, recorre el modelo y
    repuebla caché + base de datos, sin reiniciar el proceso. Puede tardar
    ~20-40s (7 tickers × descarga Yahoo).
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
2. Por cada uno de los 7 tickers: descarga ~3 años de OHLCV (sin la vela
   del día si el mercado sigue abierto), calcula las 61 features + 15
   interacciones y corre el modelo sobre toda la serie disponible.
3. Calcula la etiqueta real de cada día (`ml/target.py`) sobre el
   historial completo de cierres, para evaluar cada señal contra el día
   siguiente.
4. Si Yahoo Finance falla para un ticker (o para el contexto de mercado),
   ese ticker se omite del catálogo — no se rellena con datos simulados
   (ver justificación en `docs/MODEL_INTEGRATION.md`).
5. Calcula métricas sobre las ventanas de 30/60/90 días y persiste todo en
   SQLite (incluidas las tres probabilidades de cada predicción).

## Consideraciones
- Zona horaria: `lastUpdate` en UTC; el scheduler y `/market-status` usan
  `America/New_York` (con DST manejado por `zoneinfo`/`tzdata`). Las
  fechas de las velas OHLCV son las que reporta Yahoo Finance.
- El modelo en producción se entrenó con datos hasta 2025-12-31, así que
  toda señal de 2026 en adelante es fuera de muestra (las ventanas de
  30/60/90 días de la plataforma ya caen completas en 2026).
- Fuentes de datos: yfinance puede tener límites de tasa o datos
  retrasados; por eso existe `/admin/refresh` en vez de recalcular en
  cada request.
- CORS: abierto para facilitar desarrollo; ajustar en producción.
