# scripts_v1 — pipeline inicial (numerado)

Primer pipeline de la tesis, ejecutado en orden (01 → 08). Se corren desde
la raíz de `Dataset_N` (usan rutas relativas tipo `tesis_ml_stocks/...`,
no relativas al script):

```bash
cd Dataset_N
python scripts_v1/01_build_raw_dataset.py
```

## Qué sigue vigente

- **`01_build_raw_dataset.py`**: sigue siendo la fuente de verdad de la
  ingeniería de features (61 columnas técnicas + contexto SPY/VIX).
  Escribe en `tesis_ml_stocks/01_raw_datasets/`, que es lo que consume
  `scripts_opt/` para entrenar todo lo que hay en `RESULTADOS_OPTIMIZADOS/`.
  También fue portado 1:1 a `Proyecto/api/ml/features.py` para inferencia
  en vivo — ver `Proyecto/docs/MODEL_INTEGRATION.md`.
- **`02_validate_features.py`**: validación de esas features (nulos,
  colinealidad, distribución).

## Qué quedó superado

- **`03_build_model_datasets.py` → `08_evaluate_models.py`** (más
  `fix_metricas.py`, un parche puntual sobre 04-07): primera pasada de
  entrenamiento/evaluación, escriben en `tesis_ml_stocks/03_model_datasets`,
  `tesis_ml_stocks/04_models` y `tesis_ml_stocks/Validacion_*`. Estos
  resultados **no** son los reportados en la tesis — quedaron reemplazados
  por el pipeline de optimización en `../scripts_opt/`, que es el que
  generó `../RESULTADOS_OPTIMIZADOS/` (ver
  `../RESULTADOS_OPTIMIZADOS/docs/GUIA_PROGRESO.md` para la bitácora
  completa y la comparación baseline vs. optimizado).

Se conservan (no se borraron) porque documentan la primera iteración del
trabajo, no porque haya que volver a correrlos.
