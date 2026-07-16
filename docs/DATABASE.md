# Almacenamiento de Datos

Estado: **implementado** con SQLite vía SQLAlchemy 2.0 (`api/database.py`,
`api/models.py`). No se usa Flask-SQLAlchemy ni Flask-Migrate (no estaban
instalados y agregaban complejidad innecesaria para el tamaño del
proyecto); es SQLAlchemy declarativo simple con sesiones manuales.

## Por qué SQLite y no Postgres

- Cero configuración: un archivo `trading_system.db` en `api/`.
- Es lo que ya declaraban `.env`/`.env.example` desde antes de esta
  integración.
- `docker-compose.yml` deja Postgres listo como opción para un despliegue
  futuro tipo Azure (ver ese archivo); no se usa por defecto y las
  credenciales ya no están quemadas en el código, se leen de `.env`.
- Migración a Postgres cuando haga falta: cambiar `DATABASE_URL` en
  `.env`; el esquema (`api/models.py`) es compatible con ambos motores
  porque usa tipos genéricos de SQLAlchemy.

## Configuración

`DATABASE_URL` en `api/.env` (por defecto `sqlite:///./trading_system.db`).
`api/database.py` lee esta variable con `python-dotenv` y expone:

- `engine`, `SessionLocal` — para queries manuales.
- `init_db()` — crea las tablas si no existen (`Base.metadata.create_all`),
  se llama automáticamente al iniciar `api/main.py`.

## Esquema real (`api/models.py`)

- **`assets`**: `id`, `ticker` (único), `name`, `sector`, `industry`.
  Sector/industria se llenan desde `yfinance` (`Ticker.info`) en cada
  refresco.
- **`ohlcv_daily`**: `id`, `asset_id` (FK), `date`, `open`, `high`, `low`,
  `close`, `volume`. Único por (`asset_id`, `date`).
- **`predictions`**: `id`, `asset_id` (FK), `date`, `signal`
  (`buy`/`sell`/`hold`), `confidence`, `prob_buy`/`prob_hold`/`prob_sell`,
  `actual_price`, `model_version`, `created_at`. Único por
  (`asset_id`, `date`).
- **`metrics`**: `id`, `asset_id` (FK), `window_days` (30/60/90),
  `model_version` y las métricas de clasificación (`accuracy`,
  `f1_macro`, `f1_buy`, `f1_sell`) + financieras (`cumulative_return`,
  `return_vs_bh`, `sharpe_ratio`, `max_drawdown`, `win_rate`,
  `profit_factor`, `number_of_trades`, `exposure`, `final_capital`) +
  distribución de señales (`signal_buy_pct`, `signal_hold_pct`,
  `signal_sell_pct`). Único por (`asset_id`, `window_days`).

No hay una tabla de *features* técnicas: las 61 columnas que usa el
modelo (ver `docs/MODEL_INTEGRATION.md`) son derivadas del OHLCV y se
recalculan en memoria con `api/ml/features.py` cada vez que se refrescan
los datos — persistirlas sería redundante (se pueden reconstruir desde
`ohlcv_daily` + datos de mercado) y el cálculo de las 61 columnas para 7
tickers × ~500 días toma bajo un segundo, así que no hay necesidad real
de cachearlas en disco.

## Cómo se llenan las tablas

`initialize_data()` en `api/main.py`, al arrancar el servidor (o al
llamar `POST /admin/refresh`):

1. Descarga OHLCV + contexto de mercado real (Yahoo Finance) por ticker.
2. Corre el modelo sobre toda la serie disponible (no solo el día actual).
3. Por cada ticker: hace *upsert* del `Asset`, borra e inserta de nuevo
   sus filas de `ohlcv_daily` y `predictions` (más simple y suficientemente
   rápido que un upsert fila por fila para el tamaño de este proyecto), y
   hace upsert de las 3 filas de `metrics` (una por ventana 30/60/90).

Los endpoints `GET` de la API siguen sirviendo desde caché en memoria
(poblada en el mismo paso) por velocidad; la base de datos es el registro
persistente para auditoría/histórico entre reinicios, no la ruta caliente
de lectura.

## Consideraciones

- Fechas en UTC, sin zona horaria de mercado (NYSE) todavía — ver
  limitaciones en `docs/THESIS_QA.md`.
- Los endpoints `POST /stocks*` (actualización manual/testing) siguen
  operando solo sobre la caché en memoria, no tocan la base de datos.
  Es una limitación conocida, no un descuido: esos endpoints existen para
  pruebas/demos puntuales, no para el flujo real de datos.
