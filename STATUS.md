# Estado del proyecto

Última actualización: 2026-07-15.

## Modelado (`scripts_opt/` → `RESULTADOS_OPTIMIZADOS/`)

**Completo.** Ganador declarado: Regresión Logística elasticnet, global,
Exp B (F1-macro=0.417, Sharpe=1.25). Comparado contra XGBoost, LightGBM,
LSTM y CNN-LSTM en tres particiones temporales (A/B/C), por-ticker y
global. Bitácora completa en `RESULTADOS_OPTIMIZADOS/docs/GUIA_PROGRESO.md`.

Pendiente si se retoma: threshold calibration por clase, stacking de los
4 modelos, walk-forward validation, costos de transacción en el backtest
(ver "Próximos pasos" en la bitácora).

## Plataforma web (`Proyecto/`)

**Fase 1 — conectar todo con datos/modelo reales: completa.**
- API real: descarga OHLCV de Yahoo Finance, calcula las 61 features
  (idénticas al entrenamiento) y corre el modelo ganador — ya no hay
  señales aleatorias ni datos simulados en el flujo normal.
- Persistencia real en SQLite (antes: solo caché en memoria; el esquema
  SQLAlchemy anterior nunca llegó a correr).
- Documentación de `Proyecto/docs/` reescrita para describir lo
  implementado, no propuestas.

**Fase 2 — scheduler, tests, overrides en BD, Docker: completa.**
- Refresco automático diario (16:30 hora NY, después del cierre de NYSE).
- Suite de tests (`Proyecto/api/tests/`, pytest, sin red real) — verde.
- Los endpoints `POST /stocks*` (overrides manuales) ahora también
  escriben en SQLite, no solo en caché.
- `Dockerfile`s + `docker-compose.yml` para levantar API+frontend juntos.
  **Sin verificar en un build real** — Docker Desktop no tenía el daemon
  corriendo en el entorno donde se armó esto. Antes de confiar en esto,
  correr `docker compose up -d --build` una vez.
- Android: descartado a propósito (queda como app web/PWA, sin
  empaquetado nativo).

## Organización del repositorio

**Hecho (2026-07-15):** scripts sueltos movidos a `scripts_v1/`,
documentos de `RESULTADOS_OPTIMIZADOS/` organizados en
`RESULTADOS_OPTIMIZADOS/docs/` (con los borradores de papers aparte en
`docs/borradores/`), diagrama de arquitectura movido a `docs/`, este
`STATUS.md` y el `README.md` raíz agregados. Ver `git log` en este repo
(local, sin remoto) para el detalle de cada movimiento.

**Deliberadamente sin tocar:**
- `RESULTADOS_OPTIMIZADOS/modelos_optimizados/`, `logs/`, `reportes/`,
  `v3/`, `v4/`, `v4_final*` — estructura interna de experimentos, muy
  grande (~500MB) y con muchas rutas relativas hardcodeadas en
  `scripts_opt/*.py`; reorganizarla es alto riesgo para poco beneficio.
- `tesis_ml_stocks/` — datos crudos/derivados (~740MB), igual de
  sensible a rutas hardcodeadas.
- `scripts_opt/` — ya vivía en su propia carpeta con nombre claro, no
  hacía falta moverlo.

**Resuelto:** `Proyecto/ecommerce-security-lab/` (carpeta sin relación
con la tesis, con contenido de riesgo — ver historial de conversación)
fue eliminada por el usuario.

## Huecos conocidos / no abordados

- No existe un `requirements.txt` para el pipeline de entrenamiento
  (`scripts_opt/`, `scripts_v1/`) — solo para `Proyecto/api/`. Reproducir
  el entrenamiento requiere instalar manualmente pandas, numpy,
  scikit-learn, xgboost, lightgbm, torch, optuna, pyarrow.
- Sin control de versiones de los datos (`tesis_ml_stocks/*.parquet`) más
  allá de este commit de git — son snapshots de Yahoo Finance en el
  momento en que se corrieron los scripts.
- `Proyecto/` tiene su propio repo git con remoto en GitHub
  (`barudust/TT`); este repo raíz (`Dataset_N`) es local, sin remoto.
