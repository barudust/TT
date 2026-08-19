# Documentos de RESULTADOS_OPTIMIZADOS

> El paper académico y sus borradores viven en **[`../../paper/`](../../paper/)**,
> no aquí. Esta carpeta es solo la bitácora interna del proceso de
> optimización.

- **`GUIA_PROGRESO.md`** — bitácora interna completa: hipótesis,
  configuraciones probadas, resultados por experimento. Muy detallada,
  pero se quedó en la sesión de mayo — no cubre v3/v4/v4_final (junio).
  Para el documento del paper (más reciente, usa la evaluación v4), ver
  `../../paper/paper.tex`.
- **`ANALISIS_FEATURE_SELECTION.md`** — por qué se usan las 61 features
  completas en vez de un subconjunto filtrado.
- **`ALTERNATIVAS_FUTURAS.md`** — ideas no exploradas (datos macro FRED,
  sentimiento FinBERT, IV de opciones, walk-forward validation).
- **`DIAGNOSTICO_MODELOS_PROFUNDOS.md`** (2026-08-14) — evidencia medida de qué
  está fallando en LSTM/CNN/CNN-LSTM: entrenan 1–2 épocas efectivas, su pérdida
  de validación nunca mejora al azar, y hay tres asimetrías de protocolo frente a
  LR/XGBoost. Reproducible con `python scripts_opt/diag_deep.py`.
- **`PLAN_MAESTRO_BUSQUEDA.md`** (2026-08-14) — **el plan vigente**: siete vías
  con compuertas de decisión para sacar el máximo posible usando solo datos de
  Yahoo Finance (protocolo, Optuna real, simetría de búsqueda, más datos,
  calibración, walk-forward y pruebas estadísticas).
- **`PLAN_OPTUNA_DEEP_MODELS.md`** — ⛔ superado por los dos anteriores. Se
  conserva como historial; su tabla de "qué buscó cada script" sigue siendo
  correcta.

Ver también `../reportes/` (CSVs/JSON con las comparativas numéricas que
respaldan estos documentos y el paper, incluye `v1_vs_v3/` y `v4_final/`).
