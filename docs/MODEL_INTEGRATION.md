# Integración del Modelo en la API

Estado: **implementado**. La API (`api/main.py`) genera señales BUY/SELL/HOLD
reales usando el modelo entrenado en `RESULTADOS_OPTIMIZADOS/`, no una
heurística ni datos simulados.

## Modelo elegido

**Regresión Logística multinomial, global (los 7 tickers juntos):** L2 con
C = 0.000165 (ganador de Optuna en v5), RobustScaler, 61 indicadores + 15
interacciones (Vía 8) y pesos de clase "balanced" con el de HOLD × 0.90.
Entrenada con 2018-2025. `config_id`: `LR-v8-interactions-holdw090`.
Se regenera con `python scripts_opt/entrenar_produccion.py`.

| Evaluación | F1-macro | κ | Sharpe | Fuente |
|---|---:|---:|---:|---|
| Test 2025, Exp B (LR v5, 61 features) | 0.404 | — | +0.89 | `RESULTADOS_OPTIMIZADOS/v5/resultados_finales.csv` |
| Test 2025, Exp B (+ interacciones, Vía 8) | 0.413 | 0.14 | +0.92 | `RESULTADOS_OPTIMIZADOS/v8/interactions.csv` |
| Walk-forward 2020-2025 (LR v5, media) | 0.350 | — | +0.22 | `RESULTADOS_OPTIMIZADOS/analisis_hold/5_walk_forward_v5_resumen.csv` |
| Origen rodante 2019-2024, pipeline de producción (media) | 0.365 | 0.068 | +0.54 | `analisis_hold/7_reglas_alternativas_resumen.csv` |
| **2026 fuera de muestra, modelo desplegado** | **0.354** | **0.035** | +0.29 | `scripts_opt/evaluar_produccion_2026.py` |

Por qué este modelo y no los de deep learning, y por qué no se puede mejorar
más con datos de Yahoo Finance: `RESULTADOS_OPTIMIZADOS/JUSTIFICACION_LIMITE_DEL_MODELO.md`.
Por qué el peso de HOLD: `RESULTADOS_OPTIMIZADOS/docs/ANALISIS_HOLD_Y_GLOBAL.md` §8
(sin él, el modelo predecía HOLD el 60 % de los días de 2026 con 35 % real).

> **Historia.** Hasta agosto de 2026 corría el `LR-02-elasticnet-all` de la
> evaluación v1 (F1 0.417 / Sharpe 1.25, cifras de un protocolo anterior que
> no son comparables con v4/v5). Se reemplazó por el ganador de la Vía 8 y,
> el 2026-09-30, por esta versión con el peso de HOLD ajustado.

El `.pkl` (modelo + `RobustScaler` + lista de 76 features + pares de
interacción + hiperparámetros, ~6 KB) vive dentro del propio API en
`api/ml/artifacts/lr_elasticnet_global_expB.pkl` (el nombre del archivo se
conservó por compatibilidad) para que el servicio no dependa de la carpeta
`RESULTADOS_OPTIMIZADOS/` en tiempo de ejecución. `GET /model` describe el
modelo cargado leyendo ese `.pkl`.

## Features (61 columnas + 15 interacciones)

`api/ml/features.py` reimplementa **exactamente** el cálculo de
`scripts_v1/01_build_raw_dataset.py` (raíz del repo): retornos log, momentum,
distancia a medias móviles (10/20/30/50/200), cruces de medias, RSI,
MACD, estocástico, Williams %R, ATR, volumen/OBV/CMF/MFI, velas
japonesas (cuerpo, sombras, gap de apertura), estacionalidad
(día/mes/semana del mes) y contexto de mercado (retorno y volatilidad de
SPY, nivel y cambio de VIX). Cualquier cambio a estas fórmulas debe
replicarse en ambos archivos o las predicciones dejan de ser comparables
con las métricas reportadas en la tesis.

Para inferencia en vivo se descargan ~3 años de historial OHLCV por
ticker (necesario para el *warmup* de indicadores como la media móvil de
200 días y la ventana rodante de 252 días de `VIX_norm`); solo la última
fila (día más reciente) se usa como señal "de hoy", pero se conserva
toda la serie para las ventanas de 30/60/90 días y las métricas de
backtest.

## Flujo de inferencia (`api/ml/model.py`)

```python
from ml.features import fetch_ohlcv, fetch_market_context, build_feature_frame
from ml.model import load_model

market = fetch_market_context("3y")          # SPY + VIX, una sola vez
ohlcv  = fetch_ohlcv("AAPL", "3y")
feat   = build_feature_frame(ohlcv, market)   # 61 features + 15 interacciones + OHLCV crudo
model  = load_model()                         # carga una vez (cache en proceso)

pred = model.predict_row(feat.iloc[-1])
# {"signal": "hold", "confidence": 0.39, "probabilities": {"buy": .., "sell": .., "hold": ..}}
```

Mapeo de clases (idéntico al entrenamiento, ver `scripts_opt/common.py`):
`0=SELL`, `1=HOLD`, `2=BUY`.

`initialize_data()` en `api/main.py` corre este flujo para los 7 tickers al
arrancar el servidor, guarda resultados en memoria (para servir rápido) y
los persiste en SQLite (ver `docs/DATABASE.md`). También existe
`POST /admin/refresh` para recalcular todo sin reiniciar el proceso.

## Qué pasa si Yahoo Finance falla

Si no se puede descargar el contexto de mercado (SPY/VIX) o el historial
de un ticker puntual, ese ticker se omite del catálogo en memoria (no
aparece en `GET /stocks`) en vez de mostrar una señal simulada como
real. Se prefirió esto a un *fallback* silencioso a datos sintéticos
porque mezclar señales reales y falsas sin marcarlas sería engañoso para
quien usa la app o evalúa la tesis.

## Confianza baja, ¿es un bug?

No. Con la regularización fuerte que eligió Optuna y la poca señal que hay
en datos OHLCV de 1 día, sus `predict_proba` quedan entre 0.33 y 0.45 para
la clase ganadora (azar = 0.33). Aun así la confianza es informativa: en
2025 la tasa de acierto sube de 39 % a 56 % cuando la confianza pasa de
≤ 0.36 a 0.40–0.45. Confianzas artificialmente altas serían la señal de
alarma, no lo contrario.

## Modelos alternativos disponibles

Si se quisiera cambiar de modelo en el futuro (p. ej. comparar en vivo
contra XGBoost o LightGBM), basta con apuntar `MODEL_PATH` en `.env` a
otro `.pkl` compatible... con una salvedad: **solo los modelos de
`scripts_opt/opt_lr.py` guardan el `StandardScaler` dentro del mismo
pickle** (`{"model", "scaler", "hp", "feat_cols", "config_id"}`).
XGBoost/LightGBM no necesitan scaler pero tienen otra API de carga
(`Booster.load_model`); LSTM/CNN-LSTM están en PyTorch (`.pt`) y
requieren además fijar el `lookback` y no tienen el scaler serializado
(hay que recalcularlo). Cambiar de familia de modelo implica adaptar
`api/ml/model.py`, no solo la ruta del archivo.
