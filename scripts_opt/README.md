# scripts_opt — pipeline de optimización

Segunda fase del pipeline (posterior a `../scripts_v1/`). Se corren desde la
raíz del repo — leen de `tesis_ml_stocks/` y escriben en
`../RESULTADOS_OPTIMIZADOS/`. Pasó por varias iteraciones (v1 → v2 → v3 →
v4) antes de declarar ganador; esta tabla documenta qué sigue siendo la
fuente de verdad y qué quedó como historial.

## Módulos `common*` (indican a qué iteración pertenece cada script)

| Módulo | Iteración | Dataset que carga |
|---|---|---|
| `common.py` | v1 (61 features) | `tesis_ml_stocks/01_raw_datasets/` |
| `common_v2.py` | v2 (181 features) | `tesis_ml_stocks/01_raw_datasets_v2/` |
| `common_v3.py` | v3 (94 features = 61 + 33 de mercado) | `tesis_ml_stocks/01_raw_datasets_v3/` |
| `common_v4.py` | v4 (splits unificados, test=2025 fijo) | reusa carga de v1 con `SPLITS_V4` propios |
| `common_velas.py` | experimento aislado (solo OHLCV) | reusa carga de v1 |

## Vigente / fuente de verdad

- **`opt_lr.py`** (config `LR-02-elasticnet-all`, experimento B) — generó
  `modelo_global.pkl`, verificado **idéntico byte a byte** al `.pkl` que
  corre en producción en `api/ml/artifacts/`. Es el script a
  re-ejecutar si algún día hay que reentrenar el modelo de producción.
- **`consolidar_120.py`** — produce la tabla maestra de 120 corridas citada
  literalmente en `../paper/PAPER_FINAL.md` (líneas 470 y 483). Es el
  consolidador "oficial" citado en el paper (superset de `consolidar.py`,
  que solo cubre 4 de los 5 modelos).
- **`reporte_final.py`** — reporte completo baseline-vs-optimizado (tablas
  `MAESTRA_`/`MEJOR_` + plots `FINAL_*`); superset funcional de
  `comparar_baseline.py`.
- **`analisis_feature_selection.py`** — respaldado por
  `../RESULTADOS_OPTIMIZADOS/docs/ANALISIS_FEATURE_SELECTION.md`.
- **`diag_deep.py`** (2026-08-14) — diagnóstico de los modelos profundos de v4:
  costo real por entrenamiento, época que restaura el early stopping, curvas
  train/val sin early stopping, efecto del `MinMaxScaler` y F1 de validación de
  LR como referencia. No toca test. Corre en 2.2 min y respalda
  `../RESULTADOS_OPTIMIZADOS/docs/DIAGNOSTICO_MODELOS_PROFUNDOS.md`.
- **`opt_xgb.py`, `opt_lstm.py`, `opt_cnn_lstm.py`, `opt_cnn_puro.py`,
  `opt_cnn_puro_filtradas.py`** — comparadores de la iteración v1 que
  alimentan las tablas anteriores (no ganaron, pero sus CSVs siguen siendo
  insumo activo de `consolidar_120.py`/`reporte_final.py`).

## Historial de iteración — conservar, no re-ejecutar

- `common_v2.py`, `feature_engineering_v2.py`, `opt_lr_v2.py`,
  `opt_xgb_v2.py` — rama v2 (181 features), documentada explícitamente como
  **"no mejoró"** en `GUIA_PROGRESO.md`.
- `common_v3.py`, `expand_market_data.py`, `train_all_v3.py`,
  `comparar_v1_v3.py` — rama v3 (94 features), superada por v4.
- `common_v4.py`, `train_all_v4.py`, `consolidar_v4.py`, `plots_extra.py` —
  corrida más reciente (1 junio, "splits unificados"). Da otro resultado
  (F1-macro=0.385, Sharpe=0.755 vs. 0.417/1.25 de v1) y **no está
  referenciada** en `GUIA_PROGRESO.md` ni `PAPER_FINAL.md` — ver
  `../STATUS.md` para la discusión completa de esta discrepancia. Útil
  como evidencia de sensibilidad a los splits, no como fuente primaria de
  cifras.
- `consolidar.py` — subsumido por `consolidar_120.py` (4 de 5 modelos, sin
  CNN puro).
- `opt_lgbm.py` — corrida real y documentada ("alternativa viable a XGB"),
  pero su CSV no entra en ningún consolidador automático de esta carpeta;
  queda solo en la narrativa.
- `stacking.py`, `soft_voting.py`, `ensemble_lr_xgb.py`,
  `lr_confidence_filter.py` — ensembles/filtros probados y descartados
  ("peor"/"similar" en `GUIA_PROGRESO.md`); se conservan porque justifican
  en la tesis por qué no se usaron.

## Posible limpieza pendiente (no aplicada — revisar antes de borrar)

- **`common_velas.py`** — cero importadores en todo el repo (confirmado por
  grep global). Parece preparado para un experimento que nunca se llegó a
  correr, o cuyo script consumidor se perdió en alguna reorganización.
- **`comparar_baseline.py`** — su único output
  (`comparativa_baseline_vs_optimizado.csv`) es redundante con
  `MAESTRA_baseline_optimizado.csv` de `reporte_final.py` (mismas fuentes,
  menos tablas). Parece el borrador que `reporte_final.py` reemplazó.
