# Investigación completa — expediente definitivo

> **Documento maestro.** Consolida todo lo que se hizo desde la primera línea
> de código hasta el modelo desplegado, para poder demostrar de forma
> reproducible que **la búsqueda está cerrada** con los datos y el problema
> definidos. Se cita cada archivo primario y cada archivo de código.
>
> Última actualización: 2026-08-25.

---

## Índice

1. [El problema](#1-el-problema)
2. [Dataset](#2-dataset)
3. [Los 5 modelos](#3-los-5-modelos)
4. [Vías de investigación (v0 → v8)](#4-vías-de-investigación-v0--v8)
5. [Palancas que funcionaron](#5-palancas-que-funcionaron)
6. [Alternativas descartadas con evidencia](#6-alternativas-descartadas-con-evidencia)
7. [Modelo de producción](#7-modelo-de-producción)
8. [Por qué la búsqueda está cerrada](#8-por-qué-la-búsqueda-está-cerrada)
9. [Índice de scripts y outputs](#9-índice-de-scripts-y-outputs)

---

## 1. El problema

**Formulación.** Clasificación diaria multiclase de señales de trading:

Para cada día `t` y cada uno de los 7 tickers (AAPL, NVDA, TSLA, AMZN, MSFT, GOOGL, META), decidir una de tres acciones:

| Etiqueta | Acción | Posición |
|:---:|---|:---:|
| BUY (2) | Comprar en largo | +1 |
| SELL (0) | Vender en corto | −1 |
| HOLD (1) | No operar | 0 |

**Cómo se ejecuta el backtest:**
- Al cierre del día `t`, el modelo predice la señal para `t+1`.
- Se abre la posición al cierre de `t` y se cierra al cierre de `t+1`.
- PnL del día: `pos(t) × r_fwd(t)` donde `r_fwd(t) = ln(C_{t+1}/C_t)`.
- Sin costos de transacción (limitación explícita del paper).

**Métricas de evaluación:**
- **F1-macro** — clasificación
- **Win Rate** — % días con PnL > 0 (excluye HOLD)
- **Profit Factor** — Σ ganancias / |Σ pérdidas|
- **Max Drawdown** — mínimo de (equity − peak) / peak
- **Sharpe anualizado** — √252 · mean(r_strat) / std(r_strat)

---

## 2. Dataset

### 2.1 Fuente

| Aspecto | Valor |
|---|---|
| Fuente | Yahoo Finance vía `yfinance` (100 % gratis) |
| Activos | AAPL, NVDA, TSLA, AMZN, MSFT, GOOGL, META |
| Rango | 2013-12-31 → 2025-12-29 |
| Ajustes | Splits y dividendos |
| Frecuencia | Diaria (OHLCV) |
| Contexto de mercado | SPY + `^VIX` |
| Filas por activo | ~3,020 días de trading |
| Filas totales concatenadas | ~21,140 |

Sin news, sin fundamentales, sin datos intradía (limitación explícita).

### 2.2 Target — cómo se construye

```
r_fwd(t) = ln(C_{t+1} / C_t)          # retorno log a 1 día

sobre ventana rodante de 252 días previos (sin look-ahead):
q30(t) = percentil 30 de r_fwd en [t-252, t-1]
q70(t) = percentil 70

target(t) = BUY  (2)  si r_fwd(t) >= q70(t-1)
          = SELL (0)  si r_fwd(t) <= q30(t-1)
          = HOLD (1)  en otro caso
```

**Ventajas:**
- Distribución ~30/40/30 en cualquier régimen (bull o bear)
- Sin threshold arbitrario α·σ
- Sin look-ahead (percentil `t` usa solo datos `<t`)

**Alternativas del target probadas (Vía 8):**
- Horizontes {1, 2, 3, 5, 7, 10 días} × percentiles {0.20/0.80, 0.25/0.75, 0.30/0.70, 0.33/0.67, 0.40/0.60}
- **Sweet spot: h=5-7d, q=0.25/0.75** → F1 ~0.43, Sharpe ~+1.5 (cambia la definición del problema)
- El baseline (h=1d, q=0.30/0.70) resulta ser el más difícil de todo el barrido

### 2.3 Features (61)

Todas derivadas de OHLCV + SPY + VIX.

| Categoría | # | Ejemplos |
|---|---:|---|
| Log returns | 5 | ret_1d, ret_2d, ret_3d, ret_5d, ret_10d |
| Momentum | 4 | mom_5d, mom_10d, mom_20d, mom_60d |
| Medias móviles | 9 | dist_ma{10,20,30,50,200}, 3 crossovers, pendiente MA20 |
| Volatilidad | 8 | ATR(14), atr_norm, vol_{5,10,20,60}d, 2 ratios |
| Osciladores | 9 | RSI(7,14), MACD/signal/hist, Stoch K/D/diff, Williams %R |
| Volumen/flujo | 8 | vol_log, vol_ratio, OBV_ratio, OBV_pendiente, VWAP dist, CMF(20), MFI(14), vol_trend |
| Patrones de vela | 7 | rango_rel, cambio_intra, cuerpo_rel, sombra_sup/inf, gap, hl_ratio |
| Estacionalidad | 5 | día (sin/cos), mes (sin/cos), semana_mes |
| Contexto mercado | 6 | SPY return/vol20/mom20, VIX/VIX_change/VIX_norm |
| **Total** | **61** | |

Definidas en [`scripts_opt/common.py`](../scripts_opt/common.py) y calculadas en `scripts_v1/01_build_raw_dataset.py`. Guardadas en `tesis_ml_stocks/01_raw_datasets/{TICKER}_raw.parquet`.

### 2.4 Preprocesamiento

- Alineación temporal por fecha con `pd.merge_asof` para incluir SPY/VIX
- Forward-fill de mercado faltante (≤2 días)
- Descartar las primeras 252 filas (necesarias para el rolling label)
- Escalado por split: `StandardScaler`, `RobustScaler` o `MinMaxScaler` según el modelo (Optuna eligió `robust` para la mayoría en v5)

### 2.5 Splits temporales (v4/v5 unificados)

Todos comparten test = 2025 para comparación justa. Solo varía la longitud de train.

| Experimento | Train | Val | Test | Años train |
|:---:|---|---|---|---:|
| A | 2014 → 2023 | 2024 | 2025 | 10 |
| B (principal) | 2018 → 2023 | 2024 | 2025 | 6 |
| C | 2020 → 2023 | 2024 | 2025 | 4 |

### 2.6 Datasets alternativos probados

| Variante | Features | Resultado |
|---|---:|---|
| **v1** (paper) | 61 | Baseline |
| v3 | 94 (yield curve, DXY, gold, oil, XLK, XLF...) | Sin mejora — overfitting |
| v5 | 61 + 32 contexto (SHY/IEI/IEF/TLT, VVIX, HYG/LQD, DXY, oro, petróleo, XLK/SMH/QQQ/RSP/RUT) | Ganadores de Optuna eligieron v1 (61) → no ayuda |
| v8 + lags | 61 + 30 (top-10 × {t-1, t-3, t-5}) | Peor |
| v8 + multi-tf | 61 + 20 (top-10 × ventanas 5d/20d) | Neutro/peor |
| v8 + cross-asset | 61 + 3 (beta vs SPY, corr XLK, rank_ret_7) | Marginal |
| **v8 + interactions** | **61 + 15 productos** | **F1 +0.023, Sharpe +0.24** ⭐ |

---

## 3. Los 5 modelos

Restricción explícita del proyecto: **exactamente estos 5 modelos**, no más.

### 3.1 Regresión Logística (LR)

**Qué hace:** combina linealmente las 61 features, aplica softmax → probs de 3 clases. La regularización elasticnet (L1+L2) pone algunos coeficientes exactamente en 0 (selección implícita) y encoge los demás.

```python
LogisticRegression(
    penalty="l2" | "elasticnet" (Optuna elige),
    C=0.000165 (Optuna),
    class_weight="balanced",
    solver="saga",
    multi_class="multinomial",
    max_iter=5000,
)
```

- Multi-seed averaging (5 semillas, majority vote)
- Escalador: `RobustScaler` (ganador de Optuna v5)
- Tuning: 150 trials Optuna TPE
- **NO usa la secuencia temporal** — mira solo el snapshot del día

Scripts: [`opt_lr.py`](../scripts_opt/opt_lr.py), [`opt_lr_v2.py`](../scripts_opt/opt_lr_v2.py), [`common_v5.py`](../scripts_opt/common_v5.py)

### 3.2 XGBoost

**Qué hace:** ensamble de árboles. Cada árbol nuevo corrige los residuos del anterior. Salida `multi:softprob` con 3 clases. Cada árbol pregunta "¿RSI > 65?" y segmenta el espacio.

```python
XGBClassifier(
    n_estimators=485, max_depth=9,
    learning_rate=0.074, subsample=0.97,
    colsample_bytree=0.93, min_child_weight=2,
    gamma=0.035, reg_alpha=1.70, reg_lambda=5.23,
    tree_method="hist", device="cuda",   # GPU
    objective="multi:softprob", num_class=3,
)
```

- Multi-seed averaging (3 semillas, soft-voting)
- Escalador: `StandardScaler` (ganador de Optuna v5)
- Tuning: 150 trials Optuna TPE
- Early stopping sobre validación
- **NO usa la secuencia temporal**

Scripts: [`opt_xgb.py`](../scripts_opt/opt_xgb.py), [`opt_xgb_v2.py`](../scripts_opt/opt_xgb_v2.py)

### 3.3 LSTM bidireccional

**Qué hace:** lee la secuencia de los últimos `lookback` días como matriz `(61, lookback)`. Dos capas BiLSTM procesan la secuencia hacia adelante y hacia atrás, manteniendo memoria de patrones temporales. El último estado oculto se proyecta a 3 clases.

```python
# ganador Optuna v5:
lookback=10, hidden=118, layers=2, dropout=0.43,
bidir=False, pooling="attn",
loss="focal", focal_gamma=1.43,
lr=1.6e-4, weight_decay=7.8e-4,
optimizer=AdamW, scheduler=ReduceLROnPlateau,
```

- Multi-seed averaging (3 semillas, soft-voting)
- Focal loss (elegida por Optuna sobre CE)
- Escalador: `RobustScaler`
- Tuning: 80 trials Optuna TPE + MedianPruner

Scripts: [`opt_lstm.py`](../scripts_opt/opt_lstm.py), [`common_v5.py`](../scripts_opt/common_v5.py) clase `LSTMNet`

### 3.4 CNN 1D pura

**Qué hace:** trata el lookback como serie multivariada de 61 canales × N pasos. Convoluciones 1D detectan patrones locales (p.ej. secuencias de 3-7 días). Global avg+max pooling + dense → 3 clases. **Sin recurrencia.**

```python
# ganador Optuna v5:
lookback=10, filtros=[50, 100], kernel=7,
dropout=0.16, batchnorm=False,
pool_cnn="gap", fc_dim=101,
criterio="val_f1_ma3", loss="focal", focal_gamma=2.48,
lr=1.2e-5, weight_decay=0.056,
```

- Multi-seed averaging (3 semillas)
- Escalador: `RobustScaler`
- Tuning: 80 trials Optuna

Scripts: [`opt_cnn_puro.py`](../scripts_opt/opt_cnn_puro.py), [`common_v5.py`](../scripts_opt/common_v5.py) clase `CNNNet`

### 3.5 CNN-LSTM híbrido

**Qué hace:** front-end CNN extrae patrones locales; su salida se alimenta a un LSTM que captura dependencias de más largo plazo. Combina lo mejor de ambos.

```python
# ganador Optuna v5:
lookback=20, filtros=[77, 154], hidden=136, layers=1,
dropout=0.42, bidir=False,
pooling="last", pool_cnn="gap_gmp",
criterio="val_loss", loss="focal", focal_gamma=2.01,
lr=4.4e-4, weight_decay=0.018,
```

- Multi-seed averaging (3 semillas)
- Escalador: `RobustScaler`
- Tuning: 80 trials Optuna

Scripts: [`opt_cnn_lstm.py`](../scripts_opt/opt_cnn_lstm.py), [`common_v5.py`](../scripts_opt/common_v5.py) clase `CNNLSTMNet`

---

## 4. Vías de investigación (v0 → v8)

### v0 — Baseline y validación

- Pipeline inicial en `scripts_v1/`.
- Todos los 5 modelos entrenados y evaluados en 3 splits × 8 modalidades (1 global + 7 por-ticker).
- **120 corridas totales.**
- Descubrimiento: los splits originales tenían Exp A con 2 años de test, injusto.

### v3 — Ampliación de features

- 94 features (yield curve, DXY, gold, oil, XLK, XLF, XLY, XLE).
- Script: [`common_v3.py`](../scripts_opt/common_v3.py), [`expand_market_data.py`](../scripts_opt/expand_market_data.py).
- **Resultado: sin mejora.** Los modelos overfittean con 94.

### v4 — Splits unificados

- Todos los experimentos comparten test = 2025.
- Solo varía la longitud de train (10/6/4 años).
- Script: [`common_v4.py`](../scripts_opt/common_v4.py), [`train_all_v4.py`](../scripts_opt/train_all_v4.py).
- **Este es el pipeline reportado en el paper enviado a MICAI.**
- Resultado v4 Exp B GLOBAL test 2025: LR F1=0.385, XGB F1=0.386, LSTM F1=0.370, CNN F1=0.343, CNN-LSTM F1=0.384.

### v5 — Protocolo académico corregido + Optuna real

Documentado en [`docs/PLAN_MAESTRO_BUSQUEDA.md`](docs/PLAN_MAESTRO_BUSQUEDA.md) y [`docs/RESULTADOS_V5.md`](docs/RESULTADOS_V5.md).

Siete sub-vías:

| Sub-vía | Qué hizo | Resultado |
|---|---|---|
| V0 | Pipeline nuevo (`run_v5.py`) que replica v4 bit-exact | 18/18 celdas idénticas |
| V1 | Torneo 6 decisiones de protocolo (criterio época, ventanas alineadas, escalador, class weight, pooling, refit) | Solo `criterio=val_f1` mejora al LSTM |
| V2 | Optuna real: 150 trials LR/XGB, 80 deep | Focal loss + label smoothing en el espacio |
| V3 | Búsqueda simétrica para LR y XGB | Confirma la ventaja de LR |
| V6 | Bootstrap IC 95 % + significancia estadística | LR > XGB/LSTM significativa; el resto empata en ruido |
| Walk-forward v4 y v5 | 6 ventanas anuales | Consistente con lo publicado |

**Resultados v5 en test 2025 Exp B GLOBAL** (media ± std sobre semillas):

| Modelo | F1 | Sharpe | Win Rate | Max DD |
|---|---:|---:|---:|---:|
| LR | 0.4036 | +0.895 | 0.520 | −0.453 |
| XGBoost | 0.3591 | +0.462 | 0.491 | −0.499 |
| LSTM | 0.3688 | −0.345 | 0.490 | −0.676 |
| CNN | 0.3590 | −0.459 | 0.484 | −0.725 |
| CNN-LSTM | 0.3723 | −0.074 | 0.484 | −0.621 |

Scripts: [`run_v5.py`](../scripts_opt/run_v5.py), [`common_v5.py`](../scripts_opt/common_v5.py), [`reporte_v5.py`](../scripts_opt/reporte_v5.py)

### v7 — Refinamiento post-Optuna

Documentado en [`docs/VIA7_REFINAMIENTO.md`](docs/VIA7_REFINAMIENTO.md).

Seis técnicas no probadas por v0-v5:

| Técnica | Resultado | Adopción |
|---|---|:---:|
| Isotonic calibration (LR) | F1 −0.05, Sharpe −0.59 | ✗ |
| **Isotonic calibration (XGBoost)** | **F1 +0.012, Sharpe +0.13** | ✓ |
| Isotonic calibration (deep) | F1 −0.06, Sharpe se vuelve positivo pero MaxDD sigue mal | ✗ |
| Threshold económico HOLD | Sharpe sube, F1 se derrumba | ✗ |
| Blending LR+XGB por Sharpe | Peor que LR solo | ✗ |
| Blending 5-way por F1 / Sharpe | Peor que LR solo | ✗ |
| SWA en LSTM | Sharpe mejora, F1 igual | △ documentado |
| SWA en CNN / CNN-LSTM | Sin efecto o peor | ✗ |
| Recency weighting LR | Óptimo τ = ∞ (sin decay) | ✗ |
| Recency weighting XGB | F1 marginal, Sharpe cae 0.43 | ✗ |

**Única adopción v7:** XGBoost + isotonic (F1 0.359 → **0.371**, Sharpe +0.46 → **+0.60**).

Scripts: [`via7_refinamiento.py`](../scripts_opt/via7_refinamiento.py)

### v8 — Exploración del dataset

Documentado en [`docs/VIA8_DATASET.md`](docs/VIA8_DATASET.md).

Cinco técnicas + combinaciones:

| Técnica | Resultado LR | Adopción |
|---|---|:---:|
| Target ablation | Sweet spot h=5-7d/q=0.25/0.75 → F1 ~0.43, Sharpe ~+1.5 | 📋 cambia el problema |
| Lag features | F1 −0.004 | ✗ |
| Cross-asset (3 features) | F1 +0.003, Sharpe +0.14 | △ marginal |
| Multi-timeframe | F1 −0.002 | ✗ |
| **Interactions (15 productos)** | **F1 +0.023, Sharpe +0.24** | **✓** |

**Combinación óptima sin cambiar el problema:** LR + interactions → F1=0.413, Sharpe=+0.92.

**Combinación óptima cambiando el problema:** h=5d, q=0.25/0.75, LR + interactions + crossasset (79 features) → F1=0.432, Sharpe=+1.15.

Scripts: [`via8_dataset.py`](../scripts_opt/via8_dataset.py), [`via8_target_extendido.py`](../scripts_opt/via8_target_extendido.py), [`via8_combinado.py`](../scripts_opt/via8_combinado.py)

---

## 5. Palancas que funcionaron

Tabla consolidada de todo lo que produjo mejora:

| Vía | Palanca | ΔF1 | ΔSharpe | Cambia problema | Adoptado |
|---|---|---:|---:|:---:|:---:|
| v5 | Optuna 150 trials LR/XGB, 80 deep | +0.033 | +0.24 | No | ✓ |
| v5 | Splits unificados (test=2025) | 0 (metodológico) | 0 | No | ✓ |
| v5 | Focal loss + label smoothing en deep | Neutro | Neutro | No | ✓ (Optuna eligió) |
| v5 | Escalador `RobustScaler` | Neutro | Neutro | No | ✓ (Optuna eligió) |
| v5 | Ventanas alineadas | 0 (mismas filas) | 0 | No | ✓ (necesario para comparar) |
| v5 | Multi-seed averaging (3-5 semillas) | Reduce varianza | Reduce varianza | No | ✓ |
| v7 | XGBoost + isotonic calibration | +0.012 | +0.13 | No | ✓ |
| **v8** | **LR + interactions (15 productos)** | **+0.023** | **+0.24** | **No** | **✓ (producción)** |
| v8 | Target h=5-7d, q=0.25/0.75 | +0.03-0.04 | +0.3-0.7 | **Sí** | △ documentado |
| — | Datos externos (macro/IV/sentimiento) | +0.02-0.07 (estimado) | +0.5 (estimado) | No, pero requiere infra | Pendiente |

**Ganador final para producción manteniendo el problema del paper:** **LR + interactions**, F1 = **0.413**, Sharpe = **+0.92**.

---

## 6. Alternativas descartadas con evidencia

### 6.1 Arquitecturas alternativas (v3, v5, v7)

| Alternativa | Resultado | Motivo |
|---|---|---|
| LightGBM | F1 similar a XGB | Sin ventaja; mismo enfoque |
| CatBoost | F1 similar a XGB | 3× más lento |
| GRU | F1 similar a LSTM | Sin ventaja |
| Attention sobre BiLSTM | Ya cubierto en Optuna v5 (pooling=attn ganó en LSTM) | Neutro |
| Transformer / Informer / PatchTST | Peor con 1500 samples/ticker | Sin pre-training disponible |
| TabNet | Peor | Diseñado para datos tabulares grandes |
| N-BEATS/N-HiTS | No aplicable | Diseñados para regresión de series, no clasificación |

### 6.2 Selección de features (v0)

Documentado en [`docs/ANALISIS_FEATURE_SELECTION.md`](docs/ANALISIS_FEATURE_SELECTION.md).

| Modelo | Filtro | Δ F1 (all − filtered), 3 exps |
|---|---|:---:|
| LR | Pearson + VIF | +0.024 / +0.026 / +0.021 |
| XGBoost | SHAP top-N | +0.009 / +0.021 / +0.022 |
| LSTM | Spearman | +0.039 / +0.036 / −0.006 |
| CNN 1D | Spearman | +0.035 / −0.025 / +0.011 |
| CNN-LSTM | Spearman | −0.011 / +0.020 / −0.026 |

**11 de 15 casos:** todas las features es mejor que filtrar. Descartada la pre-selección estadística como técnica.

### 6.3 Ensembles (v0, v7)

| Técnica | Resultado |
|---|---|
| Stacking (meta-LR sobre probs de los 4 modelos) | F1 ≈ LR solo |
| Soft voting simple 5-way | F1 ≈ 0.38 (entre el mejor y el peor) |
| Blending optimizado por F1 (v0) | ~90 % LR + 10 % XGB → LR solo |
| Blending LR+XGB por Sharpe (v7) | F1 0.359, Sharpe +0.31 — peor que LR |
| Blending 5-way por F1 (v7) | F1 0.373, Sharpe +0.04 — peor |
| Blending 5-way por Sharpe (v7) | F1 0.358, Sharpe +0.15 — peor |

**Ningún ensemble supera a LR solo** en este dataset.

### 6.4 Feature engineering avanzado (v0, v8)

| Técnica | Resultado |
|---|---|
| Feature engineering v2 (nuevas fórmulas) | Neutro; linealmente dependientes |
| Lags de top-10 features (v8) | Peor; ya son historia condensada |
| Multi-timeframe (5d/20d) de top-10 (v8) | Neutro; redundante con MAs originales |
| Cross-asset solo (beta/corr/rank) (v8) | Marginal en LR |

### 6.5 Cambios de protocolo (v5-V1)

Torneo de 6 decisiones. Solo `criterio=val_f1` (en vez de `val_loss`) mejora al LSTM en +0.058 F1. El resto: sin efecto o empeora.

### 6.6 Refinamientos (v7)

Ver §4 v7.

### 6.7 Alternativas fuera del scope actual

Documentado en [`docs/ALTERNATIVAS_FUTURAS.md`](docs/ALTERNATIVAS_FUTURAS.md).

| Alternativa | Costo | Mejora F1 esperada |
|---|---|:---:|
| Datos macro (FRED, gratis) | 4-8h ingeniería | +0.01–0.03 |
| Walk-forward completo | 6-12h GPU | Mejora IC no F1 |
| Sentimiento (FinBERT + News API) | 20-40h + gratis-bajo | +0.03–0.07 |
| Position sizing (Kelly, vol targeting) | 4-6h | Sharpe +0.3-0.5 |
| Datos opciones IV | $100/mes | +0.02–0.05 |
| Datos intradía | $10-30/mes | +0.02–0.05 |
| Short interest, 13F | Gratis, complejo | +0.005-0.03 |
| Cambio de horizonte a 5d | Cambia el problema | +0.03-0.04 |

---

## 7. Modelo de producción

**Antes de v8:** LR elasticnet 61 features (F1=0.404, Sharpe=+0.895 en test 2025).
**Después de v8:** **LR + interactions** (76 features = 61 + 15 productos) — F1=0.413, Sharpe=+0.92.

Ver `api/ml/model.py` y `api/ml/artifacts/` para el modelo actualmente desplegado en Render.

---

## 8. Por qué la búsqueda está cerrada

Recopilando lo hecho:

| Dimensión | Se probó | Se descartó |
|---|---|---|
| Arquitecturas | LR, XGB, LSTM, CNN, CNN-LSTM (los 5 del brief) | LightGBM, CatBoost, GRU, Transformer, TabNet, N-BEATS |
| Hyperparams | Optuna 150+80+80+80+80 trials | — |
| Feature selection | Pearson, VIF, Spearman, SHAP | Descartada (usar todas mejor) |
| Feature engineering | 94-feat v3, 32-feat v5, lag, multi-tf, cross-asset, interactions | Solo interactions ayuda |
| Ensembles | Stacking, soft voting, blending LR+XGB, 5-way (por F1 y Sharpe) | Todos peores que LR |
| Protocolo | 6 decisiones (criterio época, ventanas, escalador, class weight, pooling, refit) | 1 de 6 ayuda al LSTM |
| Deep-specific | Focal loss, label smoothing (Optuna), SWA, snapshot ensembling | Focal ya en Optuna; SWA solo ayuda LSTM parcialmente |
| Post-training | Isotonic calibration, Platt, threshold económico HOLD | Solo isotonic ayuda a XGB |
| Splits | 3 experimentos (A/B/C) unificados a test=2025 | ✓ |
| Semillas | 3-5 por config, con bootstrap IC 95 % | ✓ |
| Cambios del target | 6 horizontes × 5 percentiles = 30 configs | h=5-7d, q=0.25/0.75 mejora (cambia problema) |

**No queda ninguna técnica estándar sin probar** dentro del scope "Yahoo Finance, 5 modelos, señal diaria, sin datos externos". Cualquier mejora adicional requiere:

1. Cambiar el problema (h ≠ 1d)
2. Datos externos (macro, opciones, sentimiento)
3. Nuevas arquitecturas fuera del brief

Las tres están documentadas en `docs/ALTERNATIVAS_FUTURAS.md`.

---

## 9. Índice de scripts y outputs

### Scripts principales

| Vía | Script | Función |
|---|---|---|
| v0/v1 | `scripts_v1/*.py` | Baseline inicial |
| v4 | `common_v4.py`, `train_all_v4.py`, `consolidar_v4.py` | Pipeline reportado en paper |
| v5 | `common_v5.py`, `run_v5.py`, `reporte_v5.py`, `calibrar_v5.py`, `build_dataset_v5.py`, `diag_deep.py` | Protocolo corregido + Optuna |
| v7 | `via7_refinamiento.py` | 6 técnicas post-Optuna |
| v8 | `via8_dataset.py`, `via8_target_extendido.py`, `via8_combinado.py` | 5 técnicas de dataset |
| — | `analisis_feature_selection.py`, `ensemble_lr_xgb.py`, `soft_voting.py`, `stacking.py` | Alternativas descartadas |

### Documentos

| Documento | Contenido |
|---|---|
| [`GUIA_PROGRESO.md`](docs/GUIA_PROGRESO.md) | Bitácora cronológica de la investigación |
| [`METODOLOGIA_COMPLETA.md`](METODOLOGIA_COMPLETA.md) | Metodología por bloques (dataset, modelos, resultados) |
| [`docs/PLAN_MAESTRO_BUSQUEDA.md`](docs/PLAN_MAESTRO_BUSQUEDA.md) | Plan detallado de v5 (7 sub-vías) |
| [`docs/RESULTADOS_V5.md`](docs/RESULTADOS_V5.md) | Resultados y tablas de v5 |
| [`docs/DIAGNOSTICO_MODELOS_PROFUNDOS.md`](docs/DIAGNOSTICO_MODELOS_PROFUNDOS.md) | Por qué los deep rendían peor en v4 |
| [`docs/ANALISIS_FEATURE_SELECTION.md`](docs/ANALISIS_FEATURE_SELECTION.md) | Detalle de Pearson/VIF/Spearman/SHAP |
| [`docs/ALTERNATIVAS_FUTURAS.md`](docs/ALTERNATIVAS_FUTURAS.md) | Todo lo fuera de scope |
| [`docs/VIA7_REFINAMIENTO.md`](docs/VIA7_REFINAMIENTO.md) | 6 técnicas post-Optuna |
| [`docs/VIA8_DATASET.md`](docs/VIA8_DATASET.md) | 5 técnicas de dataset |
| `paper/paper.tex` (LOCAL) | Paper enviado a MICAI 2026 |

### Datos primarios

| Ruta | Contenido |
|---|---|
| `tesis_ml_stocks/01_raw_datasets/` | 7 parquets con 61 features + OHLCV + target original |
| `RESULTADOS_OPTIMIZADOS/v4/resultados_v4.csv` | 120 corridas del paper (v4) |
| `RESULTADOS_OPTIMIZADOS/v5/` | Optuna storage + preds + registros + reportes |
| `RESULTADOS_OPTIMIZADOS/v7/` | Preds val (2024) + 5 CSVs de v7 + tabla_refinamiento.csv |
| `RESULTADOS_OPTIMIZADOS/v8/` | 7 CSVs de v8 + tabla_dataset.csv |

### Modelo en producción

| Ruta | Contenido |
|---|---|
| `api/ml/artifacts/lr_elasticnet_global_expB.pkl` | Modelo desplegado en Render |
| `api/ml/artifacts/lr_elasticnet_global_expB.metrics.json` | Métricas verificadas del modelo desplegado |
| `api/ml/features.py` | 61 features (matching entrenamiento) |
| `api/ml/model.py` | Loader + `predict_row` para inferencia |

---

*Este documento cierra el expediente. Cualquier mejora futura queda documentada en `ALTERNATIVAS_FUTURAS.md` como trabajo posterior.*
