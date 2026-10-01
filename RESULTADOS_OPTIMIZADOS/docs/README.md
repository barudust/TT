# Documentos de la investigación

> El paper académico vive en **[`../../paper_review/`](../../paper_review/)**.
> El punto de entrada para todo el proyecto es **[`../../CONTEXTO.md`](../../CONTEXTO.md)**.

## Para la tesis y la defensa (vigentes, 2026-09-30)

En `RESULTADOS_OPTIMIZADOS/` (un nivel arriba):

- **[`../JUSTIFICACION_LIMITE_DEL_MODELO.md`](../JUSTIFICACION_LIMITE_DEL_MODELO.md)** —
  por qué, con datos de Yahoo Finance y los 5 modelos, no se puede mejorar
  más: walk-forward 2020–2025, todo lo probado, exceso de HOLD, 40/60,
  global vs por-ticker, respuestas cortas para la defensa.
- **[`../GUIA_DEFENSA_TT.md`](../GUIA_DEFENSA_TT.md)** — guía de estudio de 17
  capítulos; el Cap. 15 es el banco de preguntas y el Cap. 17 las preguntas de
  una sinodal experta en ML/DL y estadística.
- **[`../INVESTIGACION_COMPLETA.md`](../INVESTIGACION_COMPLETA.md)** — expediente
  de todo lo hecho (v0–v8) con sus archivos.
- **[`../METODOLOGIA_COMPLETA.md`](../METODOLOGIA_COMPLETA.md)** — metodología por
  bloques (dataset, modelos, resultados).

En esta carpeta:

- **`ANALISIS_HOLD_Y_GLOBAL.md`** (2026-09-30) — por qué el modelo predecía
  tanto HOLD, 40/60, ajuste del peso de HOLD (§8, el que está en producción),
  global vs por-ticker, evaluación 2026 fuera de muestra, walk-forward de v5 y
  la auditoría de la plataforma web.
- **`RESULTADOS_V5.md`** — protocolo corregido + Optuna simétrico + IC
  bootstrap (lo que el paper llama "Robustness").
- **`VIA7_REFINAMIENTO.md`** — calibración, SWA, blending, recencia.
- **`VIA8_DATASET.md`** — target ablation, lags, cross-asset, multi-timeframe,
  interactions. Ojo: sus cifras se midieron en test 2025 (ver
  `ANALISIS_HOLD_Y_GLOBAL.md` §1).
- **`DIAGNOSTICO_MODELOS_PROFUNDOS.md`** (2026-08-14) — por qué LSTM/CNN/CNN-LSTM
  no aprendían: 1–2 épocas efectivas, pérdida de validación ≈ ln 3.
- **`ANALISIS_FEATURE_SELECTION.md`** — por qué se usan todas las features
  (filtrar empeora en 11 de 15 casos).
- **`ALTERNATIVAS_FUTURAS.md`** — lo que queda fuera del alcance (datos macro,
  sentimiento, opciones, intradía). El walk-forward y los costos de
  transacción que menciona ya se hicieron en v5.

## Historial (no citar cifras de aquí sin revisar)

- **`GUIA_PROGRESO.md`** — bitácora de mayo (evaluación v1: F1 0.417 /
  Sharpe 1.25 con un protocolo anterior, no comparable con v4/v5).
- **`PLAN_MAESTRO_BUSQUEDA.md`** — el plan de v5 (sus siete sub-vías ya se
  ejecutaron; resultados en `RESULTADOS_V5.md`).
- **`PLAN_OPTUNA_DEEP_MODELS.md`** — superado por el anterior.

Datos que respaldan todo: `../v4/`, `../v5/` (incluye `preds/` y
`log_wf_v5.txt`), `../v7/`, `../v8/`, `../analisis_hold/` y `../reportes/`.
