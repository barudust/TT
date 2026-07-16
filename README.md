# TT 2026-B164 — Plataforma de Clasificación Bursátil

Trabajo Terminal: predicción de señales de trading (COMPRAR/VENDER/MANTENER)
para siete acciones tecnológicas de EE. UU. (AAPL, NVDA, TSLA, AMZN, MSFT,
GOOGL, META), comparando empíricamente cinco arquitecturas de ML/DL, y una
plataforma web que sirve las señales del modelo ganador con datos e
inferencia reales.

**Estado actual y qué falta**: ver [`STATUS.md`](STATUS.md).

## Estructura del repositorio

```
.
├── Proyecto/                  # Aplicación web (frontend + API + BD) — repo git propio
├── scripts_opt/               # Pipeline de optimización que generó RESULTADOS_OPTIMIZADOS/
├── RESULTADOS_OPTIMIZADOS/    # Resultados de todos los experimentos + papers/bitácora
├── scripts_v1/                # Primera iteración del pipeline (parcialmente superada)
├── tesis_ml_stocks/           # Datasets crudos y artefactos de datos (parquet)
├── docs/                      # Diagramas/recursos a nivel de todo el proyecto
├── render.yaml                # Blueprint de despliegue (ver Proyecto/docs/DEPLOY_RENDER.md)
└── STATUS.md
```

## Dónde está cada cosa

- **¿Quiero correr la app web?** → [`Proyecto/README.md`](Proyecto/README.md)
  (frontend React + API Flask + SQLite, modelo real ya conectado).
- **¿Quiero entender qué modelo ganó y por qué?** →
  [`RESULTADOS_OPTIMIZADOS/docs/GUIA_PROGRESO.md`](RESULTADOS_OPTIMIZADOS/docs/GUIA_PROGRESO.md)
  (bitácora completa) o [`RESULTADOS_OPTIMIZADOS/docs/PAPER_FINAL.md`](RESULTADOS_OPTIMIZADOS/docs/PAPER_FINAL.md)
  (redacción tipo paper).
- **¿Quiero reproducir el entrenamiento?** → los scripts en
  [`scripts_opt/`](scripts_opt) (ver `scripts_opt/common.py` para configuración
  de tickers/splits/rutas) leen de `tesis_ml_stocks/01_raw_datasets/` y
  escriben en `RESULTADOS_OPTIMIZADOS/`. Se corren desde la raíz del repo.
  Ver [`scripts_opt/README.md`](scripts_opt/README.md) para qué scripts son
  la fuente de verdad (incl. el que generó el `.pkl` en producción) y
  cuáles son iteraciones (v2/v3/v4) ya superadas.
- **¿Qué es `scripts_v1/`?** → la primera pasada del pipeline (antes de la
  fase de optimización). Ver [`scripts_v1/README.md`](scripts_v1/README.md)
  para qué sigue vigente y qué quedó superado.

## Resumen del hallazgo principal

El modelo con mejor desempeño, tras comparar Regresión Logística, XGBoost,
LightGBM, LSTM y CNN-LSTM en tres particiones temporales, es una
**Regresión Logística con regularización elasticnet** entrenada globalmente
sobre los 7 tickers (F1-macro = 0.417, Sharpe de backtest = 1.25 en el
experimento principal). Es el modelo que corre en producción en `Proyecto/`.
Detalle completo en `RESULTADOS_OPTIMIZADOS/docs/GUIA_PROGRESO.md`.

## Licencia

Uso académico.
