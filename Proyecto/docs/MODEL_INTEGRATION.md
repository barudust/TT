# Integración del Modelo en la API

Estado: **implementado**. La API (`api/main.py`) genera señales BUY/SELL/HOLD
reales usando el modelo entrenado en `RESULTADOS_OPTIMIZADOS/`, no una
heurística ni datos simulados.

## Modelo elegido

**Regresión Logística con elasticnet, entrenamiento global (los 7 tickers
juntos), Experimento B (train 2018-2023, val 2024, test 2025).**

Config id: `LR-02-elasticnet-all`, artefacto original:
`RESULTADOS_OPTIMIZADOS/modelos_optimizados/lr/LR-02-elasticnet-all/experimento_B/modelo_global.pkl`.

Es el ganador declarado en `RESULTADOS_OPTIMIZADOS/docs/GUIA_PROGRESO.md` tras
comparar contra XGBoost, LightGBM, LSTM y CNN-LSTM en los tres experimentos
temporales:

| Métrica (test, Exp B GLOBAL) | Valor |
|---|---|
| F1-macro | 0.4167 |
| Accuracy | 0.4407 |
| Sharpe (backtest simple) | 1.25 |
| Retorno acumulado | +20.6% |
| Retorno vs Buy&Hold | +17.4% |

Razones documentadas para elegirlo sobre los modelos de deep learning:
gana en Exp B y Exp C, pierde por solo +0.012 F1 frente a XGBoost en Exp A,
es más interpretable, no requiere GPU, y las arquitecturas más complejas
(LSTM, CNN-LSTM) no superaron el techo de ~0.42 F1-macro pese a más
esfuerzo de optimización (ver sección 7 de `GUIA_PROGRESO.md`).

El `.pkl` (modelo + `StandardScaler` + lista de 61 features, ~5KB) está
copiado dentro del propio API en `api/ml/artifacts/lr_elasticnet_global_expB.pkl`
para que el servicio no dependa de la carpeta `RESULTADOS_OPTIMIZADOS/`
en tiempo de ejecución (útil si se despliega la API sola, p. ej. a Azure).

## Features (61 columnas)

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
feat   = build_feature_frame(ohlcv, market)   # 61 features + OHLCV crudo
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

No. El modelo tiene F1-macro ≈ 0.42 sobre 3 clases (el azar sería
≈0.33), por lo que sus `predict_proba` suelen quedar entre 0.35 y 0.45
para la clase ganadora — es el techo de información real que hay en
datos OHLCV de 1 día (ver el análisis "Conclusión definitiva sobre el
ceiling" en `GUIA_PROGRESO.md`). Confianzas artificialmente altas
serían la señal de alarma, no lo contrario.

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
