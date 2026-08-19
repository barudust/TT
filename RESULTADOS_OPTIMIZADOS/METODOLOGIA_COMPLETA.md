# Metodología completa — Todo lo que se hizo para encontrar el mejor modelo

Este documento inventaría **cada intervención** hecha sobre datos, features, arquitecturas y evaluación para obtener el mejor clasificador diario BUY/HOLD/SELL en 7 acciones tecnológicas de EE.UU. Sirve como bitácora técnica y complemento al paper.

---

## 1. Dataset

### 1.1 Fuente y activos

| Detalle | Valor |
|---|---|
| Fuente | Yahoo Finance (`yfinance`) — gratis, sin news, sin fundamentales |
| Activos | AAPL, NVDA, TSLA, AMZN, MSFT, GOOGL, META |
| Rango temporal | 2013-12-31 a 2025-12-29 (~12 años) |
| Ajustes | Splits y dividendos aplicados |
| Frecuencia | Diaria (OHLCV) |
| Contexto de mercado | SPY (ETF S&P 500) + `^VIX` |
| Filas por activo | ~3,020 días de mercado |
| Filas totales (concatenadas para modo global) | ~21,140 |

### 1.2 Descarga y datos extra (`expand_market_data.py`)

Se descargaron adicionalmente:
- **Yield curve:** `^TNX` (10y), `^FVX` (5y), `^IRX` (3m)
- **Sectores:** XLK (tech), XLF (financials), XLY (consumer discretionary), XLE (energy)
- **Commodities:** GLD (gold), USO (oil)
- **Dólar:** DX-Y.NYB
- **Bonos:** TLT (long-term treasuries)

Con estos se construyó `common_v3.py` con **94 features** en total. Sin embargo, la comparación empírica mostró que **61 features rinden igual o mejor** por overfitting reducido en las arquitecturas deep; se optó por el conjunto de 61 como versión final.

### 1.3 Preprocesamiento (todos los scripts)

- Alineación temporal por fecha con `pd.merge_asof` para incluir SPY/VIX.
- Forward-fill de valores faltantes de mercado (≤2 días).
- Se descartan las primeras 252 filas por activo (necesarias para el rolling label).
- Escalado por split: `StandardScaler` para LR, `MinMaxScaler` para deep, valores crudos para XGBoost.

### 1.4 Splits temporales (`common_v4.py`)

**Los tres experimentos comparten el mismo año de prueba (2025) para poder compararlos justamente.** Solo varía la ventana de train:

| Experimento | Train | Val | Test | Años train |
|---|---|---|---|---:|
| A | 2014-01 → 2023-12 | 2024 | 2025 | 10 |
| B | 2018-01 → 2023-12 | 2024 | 2025 | 6 |
| C | 2020-01 → 2023-12 | 2024 | 2025 | 4 |

**Corrección importante:** una versión anterior (v1/v3) tenía Exp A con 2024-2025 como test (2 años), lo cual sesgaba la comparación (2024 fue año fácil). En `common_v4.py` se unificó todo a test=2025.

---

## 2. Etiquetado (target)

### 2.1 Definición

Para cada día `t`:

```
r_fwd(t) = ln(C_{t+1} / C_t)
```

Sobre ventana rodada de 252 días (usando **solo datos previos a t**, sin look-ahead):

```
q30(t) = percentil 30 de r_fwd en [t-252, t-1]
q70(t) = percentil 70 de r_fwd en [t-252, t-1]
```

Etiqueta:

```
y_t = BUY  (2)  si r_fwd(t) >= q70(t-1)
y_t = SELL (0)  si r_fwd(t) <= q30(t-1)
y_t = HOLD (1)  en otro caso
```

### 2.2 Ventajas de este target

- Distribución **~30/40/30 en todo régimen** (bull o bear).
- No necesita threshold arbitrario `α·σ`.
- Sin look-ahead: el quantile en `t` se calcula solo con datos `<t`.

### 2.3 Alternativas descartadas

- **Threshold fijo (±1%)**: desbalanceado en regímenes de baja volatilidad → colapsa a HOLD.
- **Threshold n·σ móvil**: mejor pero exige elegir n; el percentil rodado lo hace paramétricamente.
- **Regresión sobre el return**: no captura la asimetría del PnL.

---

## 3. Features (61 en total — versión final)

Todas se calculan por activo a partir de OHLCV + SPY + VIX. Nada de news, nada de fundamentales.

| Categoría | # | Ejemplos |
|---|---:|---|
| Log returns | 5 | `ret_1d`, `ret_2d`, `ret_3d`, `ret_5d`, `ret_10d` |
| Momentum | 4 | `mom_5d`, `mom_20d`, `mom_60d`, `mom_120d` |
| Medias móviles | 9 | Distancia a MA10/20/50/200, 3 crossovers, pendiente MA20 |
| Volatilidad | 8 | ATR(14), realized vol 5/10/20/60d, 2 ratios |
| Osciladores | 9 | RSI(7,14), MACD/signal/hist, Stoch K/D/diff, Williams %R |
| Volumen/flujo | 8 | OBV, VWAP-distance, CMF(20), MFI(14), vol_ratio |
| Patrones de vela | 7 | body/range, upper/lower shadow, gap, HL ratio |
| Estacionalidad | 5 | Weekday, month (sin/cos), week-of-month |
| Contexto mercado | 6 | SPY return/vol/momentum, VIX level/change/normalizado |
| **Total** | **61** | |

Definidas en `scripts_opt/common.py`. Versión extendida de 94 en `common_v3.py` (no adoptada como final).

---

## 4. Selección estadística de features — probada y descartada

Se probó, para cada modelo, el escenario "todas las 61 features" vs. "subset filtrado por test estadístico". Resultado consolidado en `ANALISIS_FEATURE_SELECTION.md`.

| Modelo | Test aplicado | Features seleccionadas | Δ F1 (all − filtered) |
|---|---|---:|---:|
| LR | Pearson + VIF | 4–8 | +0.024 / +0.026 / +0.021 |
| XGBoost | SHAP top-N | 23–25 | +0.009 / +0.021 / +0.022 |
| LSTM | Spearman | 3–25 | +0.039 / +0.036 / −0.006 |
| CNN 1D | Spearman | variable | +0.035 / −0.025 / +0.011 |
| CNN-LSTM | Spearman | variable | −0.011 / +0.020 / −0.026 |

**Conclusión:** en 11 de 15 casos usar las 61 features es mejor. La regularización interna (elasticnet en LR, L2+pruning en XGBoost, dropout+weight decay en deep) supera al filtro externo. Se **usan las 61 features en todos los modelos finales**.

Los tests siguen documentados como herramienta exploratoria en `scripts_opt/analisis_feature_selection.py`.

---

## 5. Modelos — qué se hizo por cada uno

Cada modelo se entrenó bajo el mismo protocolo:
- Splits `A/B/C` (test=2025)
- Modalidad GLOBAL (1 modelo para 7 tickers) y POR-TICKER (7 modelos independientes)
- Multi-seed: 3 para deep, 5 para ML
- Pesos de clase "balanced"
- F1-macro como objetivo de tuning
- Métricas: F1 + backtest (Win Rate, PF, Max DD, Sharpe)

### 5.1 Regresión Logística (`opt_lr.py`, `opt_lr_v2.py`)

| Aspecto | Detalle |
|---|---|
| Tipo | Multinomial (softmax), `sklearn.linear_model.LogisticRegression` |
| Regularización | **Elasticnet** (`l1_ratio=0.5`), penalización L1+L2 combinada |
| Solver | **SAGA** (único que soporta elasticnet multinomial) |
| C (inverso de regularización) | Buscado en {0.01, 0.1, 1.0} sobre validación |
| Escalado | `StandardScaler` (media 0, std 1) |
| Class weight | `balanced` (auto según frecuencia de clases) |
| max_iter | 3000 |
| Multi-seed | 5 semillas; voting por mayoría en las predicciones |
| Threshold calibration (v2) | Se exploró calibrar thresholds por clase (LR-v2); marginal — se descartó |
| Confidence filter (`lr_confidence_filter.py`) | Solo tradear cuando `P(clase) > τ`. Mejora precisión pero baja cobertura; útil como opción práctica, no como comparativa. |

**Tuning específico probado:**
- Combinaciones `(C, l1_ratio)` en grid; el óptimo estable fue `C=1, l1_ratio=0.5`.
- Verificado que `l1_ratio=1` (Lasso puro) elimina demasiadas features; `l1_ratio=0` (Ridge puro) no aporta selección.
- 5 semillas suavizan la variabilidad de SAGA en convergencia.

**Resultado (F1 promedio 0.399, ganador global).**

### 5.2 XGBoost (`opt_xgb.py`, `opt_xgb_v2.py`)

| Aspecto | Detalle |
|---|---|
| Tipo | Gradient Boosted Trees (`multi:softprob`) |
| Backend | `xgboost` con `tree_method='hist'` y `device='cuda'` (GPU NVIDIA RTX 5060 Ti) |
| Tuning | **Optuna** (TPE sampler) con 20-40 trials por setting |
| Hyperparams optimizados | `n_estimators` (100-800), `max_depth` (3-10), `learning_rate` (0.01-0.3, log), `subsample` (0.6-1.0), `colsample_bytree` (0.6-1.0), `min_child_weight` (1-10), `reg_alpha` (0-2), `reg_lambda` (0-2), `gamma` (0-2) |
| Early stopping | `early_stopping_rounds=30` sobre validación |
| Class weight | Vector de `sample_weight` balanceado por clase |
| Multi-seed | 3 semillas; averaging por soft-voting (media de probabilidades) |
| Ensembles internos | Se probó blending de 3 folds; no aporta vs. multi-seed simple |

**Tuning específico probado:**
- Con SHAP top-25 features vs. todas las 61: mejor con todas.
- Comparación GBDT vs. Extra-Trees: XGB gana consistentemente.
- LightGBM (`opt_lgbm.py`) probado como alternativa: rendimiento similar, XGBoost más estable en Windows con GPU CUDA.
- CatBoost probado: sin ventaja sobre XGB, mucho más lento.

**Resultado (F1 promedio 0.385, 2º global; empatado con LR en Exp B).**

### 5.3 LSTM bidireccional (`opt_lstm.py`, `train_all_v3.py`, `train_all_v4.py`)

| Aspecto | Detalle |
|---|---|
| Framework | PyTorch, CUDA |
| Arquitectura | **BiLSTM 2 capas** stacked, hidden=128, dropout=0.3 |
| Regularización | LayerNorm después de la LSTM, dropout=0.3 |
| Cabezal | Linear(128*2 → 3) — usa el último estado oculto |
| Lookbacks probados | 20, 30, 40, 60 días |
| Optimizador | AdamW, `lr=1e-3`, `weight_decay=1e-4` |
| Scheduler | `ReduceLROnPlateau` sobre val_loss, factor=0.5, patience=5 |
| Gradient clipping | `clip_grad_norm_(1.0)` |
| Épocas | máx 80, early stopping patience=15 |
| Batch size | 128 |
| Loss | `CrossEntropyLoss(weight=class_weights_balanced)` |
| Multi-seed | 3 semillas; average por soft-voting |

**Tuning específico probado:**
- Unidireccional vs. bidireccional: **bidireccional gana** (~+0.02 F1).
- Hidden 64/128/256: 128 es óptimo (256 sobreajusta con 1500 samples/ticker).
- Dropout 0.2/0.3/0.5: 0.3 es óptimo.
- Attention layer añadida al final: sin mejora significativa, se descarta por simplicidad.
- Comparación con **GRU** (`opt_lstm.py` con flag): resultados similares, se mantuvo BiLSTM por ser el estándar.
- Comparación con **Transformer 2 layers**: no cabe en 1500 samples/ticker; requiere pre-training que no está disponible aquí.

**Resultado (F1 promedio 0.376, 3º global; mejor Sharpe fuera del top-2 en Exp B).**

### 5.4 CNN 1D pura (`opt_cnn_puro.py`, `opt_cnn_puro_filtradas.py`)

| Aspecto | Detalle |
|---|---|
| Framework | PyTorch |
| Arquitectura | 3 bloques Conv1D: filtros 64 → 128 → 192; kernel_size=3; padding='same' |
| Cada bloque | `Conv1d + BatchNorm1d + ReLU + Dropout(0.3) + MaxPool1d(2)` |
| Pooling final | **Global Average Pool + Global Max Pool concatenados** |
| Cabezal | `Linear(384 → 128) + ReLU + Dropout(0.4) + Linear(128 → 3)` |
| Input shape | `(batch, features=61, seq_len=lookback)` |
| Sin recurrencia | Estrictamente convolucional — captura patrones locales |
| Resto | Mismo entrenamiento que LSTM (AdamW, ReduceLROnPlateau, early stopping) |

**Tuning específico probado:**
- Kernel size 3/5/7: `kernel=3` óptimo (patrones cortos de 3 días — vela + 2 anteriores).
- 2 vs. 3 vs. 4 bloques Conv: 3 bloques óptimo.
- Solo AvgPool vs. Avg+Max concatenado: **Avg+Max concatenado aporta** (+0.01 F1).
- Filtros crecientes 64→128→192 vs. planos 128→128→128: crecientes ganan.
- Se probó también CNN con **feature-selection previa** (`opt_cnn_puro_filtradas.py`): peor.

**Resultado (F1 promedio 0.359, 5º global — más débil).** Aún así es útil como reference para el híbrido.

### 5.5 CNN-LSTM híbrido (`opt_cnn_lstm.py`)

| Aspecto | Detalle |
|---|---|
| Framework | PyTorch |
| Front-end | **2 bloques Conv1D** (filtros 64 → 128, kernel=3) para extraer patrones locales |
| Back-end | **LSTM** hidden=128, 2 capas, dropout=0.3 (procesa la secuencia de features conv) |
| Cabezal | `Linear(128 → 3)` |
| Input especial | Los últimos 5 canales del input llevan **OHLCV normalizado localmente** (cada ventana dividida entre su primer close y su max volumen) para que el CNN aprenda formas de vela invariantes a escala |
| Resto | Mismo optimizador y scheduler que LSTM/CNN puro |

**Tuning específico probado:**
- Con y sin la normalización local OHLCV: **con** aporta (~+0.015 F1).
- CNN → LSTM (probado) vs. LSTM → CNN vs. paralelo: **CNN → LSTM secuencial** gana.
- Dropout entre CNN y LSTM: sin diferencia.

**Resultado (F1 promedio 0.377, 4º global; mejor Max DD en Exp B: −0.40).**

---

## 6. Ensembles probados

### 6.1 Multi-seed averaging (usado)

Estándar en todos los modelos finales. Deep: 3 semillas → media de probabilidades → argmax. LR: 5 semillas → majority vote. **Sí aporta**: −40 % de varianza en F1 vs. una sola semilla.

### 6.2 Stacking (`stacking.py` — probado, no adoptado)

Meta-modelo LR sobre las probabilidades de los 4 modelos base (LR + XGB + LSTM + CNN-LSTM). Resultado: F1 comparable a LR solo, con 4× más compute → no vale.

### 6.3 Soft Voting (`soft_voting.py` — probado, no adoptado)

Media simple de las probabilidades de los 5 modelos. Resultado: F1 ≈ 0.38, entre el mejor y el peor → no aporta.

### 6.4 Blending optimizado (probado, no adoptado)

Buscar pesos `w_i` que maximicen F1 en validación (constraint suma=1). El óptimo era ~90 % LR + 10 % XGB → esencialmente LR solo.

**Conclusión:** en este dataset, el mejor modelo simple (LR elasticnet) es tan bueno como cualquier ensemble.

---

## 7. Alternativas de arquitectura probadas y no adoptadas

Documentadas en `ALTERNATIVAS_FUTURAS.md`. Cada una probada empíricamente:

| Arquitectura | Resultado | Motivo de descarte |
|---|---|---|
| **LightGBM** (`opt_lgbm.py`) | F1 similar a XGB | No aporta variedad, mismo enfoque |
| **CatBoost** | F1 similar a XGB | 3× más lento, sin ventaja |
| **GRU** | F1 similar a LSTM | Sin ventaja significativa |
| **Attention** sobre BiLSTM | ~+0.005 F1 | No justifica complejidad |
| **Transformer** | Peor con 1500 samples | Sin pre-training disponible |
| **TabNet** | Peor | Diseñado para datos tabulares grandes |
| **N-BEATS/N-HiTS** | No aplicable | Diseñados para regresión de series, no clasificación |
| **XGBoost + threshold calibration** (v2) | Marginal | No estable entre folds |
| **Feature engineering avanzado** (v2) | Neutro | Nuevas features linealmente dependientes |
| **Confidence filter** (LR + threshold τ) | Cobertura baja | Útil en producción, no comparable en F1 |

---

## 8. Iteraciones del proyecto (v1 → v3 → v4 → v5)

| Versión | Cambio principal | Splits | Features | Resultado |
|---|---|---|---|---|
| **v1** | Baseline inicial, todos los modelos | A/B/C originales | 61 | LR 0.380 en Exp A |
| **v2** | Threshold calibration | A/B/C | 61 | Sin mejora estable |
| **v3** | 94 features (mercado extra) | A/B/C | 94 | Sin mejora — overfitting |
| **v4** (final) | **Splits unificados: test=2025 en todos** | A/B/C v4 | 61 | LR 0.399 promedio |
| **v5** | Sandbox: calibración por-ticker | A/B/C v4 | 61 | Similar a v4 |

**La versión final del paper es v4.** Todos los resultados reportados se recomputan con `common_v4.py` y `train_all_v4.py`.

---

## 9. Evaluación

### 9.1 Métrica primaria: F1-macro

- Media no ponderada de F1 por clase.
- Penaliza colapso a una sola clase (algo que la accuracy no hace).
- Adecuada al balance ~30/40/30 del target.

### 9.2 Métricas económicas (backtest)

Se traduce cada predicción a posición:
- BUY → +1 (largo)
- SELL → −1 (corto)
- HOLD → 0 (fuera)

Return diario de estrategia: `r_strat(t) = pos(t) × r_fwd(t)`. Se calcula:

- **Win Rate**: fracción de días con `r_strat > 0` (entre días con posición ≠ 0).
- **Profit Factor**: `Σ ganancias / |Σ pérdidas|`.
- **Max Drawdown**: mínimo de `(equity_t − peak_t)/peak_t`.
- **Sharpe anualizado**: `√252 · mean(r_strat) / std(r_strat)`, con `r_f=0`.

### 9.3 Por qué no reportamos accuracy

Con 3 clases balanceadas, predecir siempre HOLD da ~40 % accuracy sin información útil. F1-macro sí detecta el colapso.

### 9.4 Costos de transacción

**No incluidos** en el backtest. Con costos realistas (~2-5 bps por trade) los modelos con Sharpe <0.5 probablemente pierdan la ventaja. Es una limitación explícita del paper.

---

## 10. Análisis de dispersión entre tickers (validación no-bug)

Se verificó que el ordenamiento por Sharpe/Win Rate **no muestra clustering artificial por modelo o experimento**. La variabilidad por ticker excede la variabilidad por modelo:

| Ticker | Sharpe promedio (15 corridas: 5 modelos × 3 exps) |
|---|---:|
| AMZN | +0.95 |
| TSLA | +0.53 |
| META | +0.42 |
| NVDA | +0.32 |
| AAPL | +0.21 |
| MSFT | +0.08 |
| GOOGL | −0.15 |

Modelos: std entre 0.62 y 0.93. Tickers: rango de medias de −0.15 a +0.95.
**Interpretación:** la elección del ticker importa más que la elección del modelo. AMZN/TSLA son intrínsecamente más predecibles/tradables; GOOGL es range-bound en 2025.

---

## 11. Reproducibilidad

- **Semillas fijas** por corrida (documentadas dentro de cada script).
- **`requirements.txt`** en la raíz del repo.
- **CSVs primarios** (no derivados): `RESULTADOS_OPTIMIZADOS/v4/resultados_v4.csv`.
- **Scripts autosuficientes** — todos ejecutables desde la raíz con `python scripts_opt/<script>.py`.
- **Hardware usado**: NVIDIA RTX 5060 Ti (CUDA 12.x), Python 3.11, PyTorch 2.x.

---

## 12. Resumen ejecutivo

| Pregunta | Respuesta empírica |
|---|---|
| ¿Cuál es el mejor modelo? | **LR con elasticnet** (F1 promedio 0.399, Sharpe Exp B +0.76) |
| ¿Ayuda la selección estadística de features? | No — 11/15 casos peor. Se usa el conjunto de 61 completo. |
| ¿Ayudan más años de train? | Marginalmente. Exp A (10y) > Exp C (4y) en LR. Los deep models son planos. |
| ¿Global > por-ticker? | Depende. LR y XGB rinden similar; deep pierden más al aislar por ticker. |
| ¿Los deep models valen la pena? | Solo si hay más historia o inputs más ricos. En este dataset, no. |
| ¿Cuál es el activo más predecible? | AMZN (Sharpe promedio +0.95); GOOGL es el peor (−0.15). |

**Modelo recomendado para producción:** LR elasticnet global, Exp B (6 años train, refresh anual). Sencillo, rápido, mejor Sharpe.

---

## 13. Estructura del proyecto

```
TT_Proyecto/
├── scripts_opt/                      # todos los scripts de entrenamiento y evaluación
│   ├── common.py                     # loader base 61 features
│   ├── common_v3.py                  # loader 94 features (no adoptado)
│   ├── common_v4.py                  # loader con splits unificados (final)
│   ├── expand_market_data.py         # descarga contexto extra de Yahoo
│   ├── opt_lr.py, opt_lr_v2.py       # entrenamiento LR
│   ├── opt_xgb.py                    # entrenamiento XGB con Optuna
│   ├── opt_lstm.py                   # entrenamiento LSTM/GRU
│   ├── opt_cnn_puro.py               # CNN 1D pura
│   ├── opt_cnn_lstm.py               # CNN + LSTM híbrido
│   ├── opt_lgbm.py                   # LightGBM alternativo
│   ├── train_all_v4.py               # corrida completa 5 modelos v4
│   ├── consolidar_v4.py              # genera tablas paper
│   ├── plots_extra.py                # figuras adicionales
│   ├── analisis_feature_selection.py # Pearson/VIF/Spearman/SHAP
│   ├── stacking.py, soft_voting.py   # ensembles probados
│   └── reporte_final.py              # dashboard consolidado
├── RESULTADOS_OPTIMIZADOS/
│   ├── v4/resultados_v4.csv          # datos primarios (120 corridas)
│   ├── reportes/v4_final/            # tablas y plots finales
│   ├── METODOLOGIA_COMPLETA.md       # (este archivo)
│   ├── PAPER.md                      # versión markdown corta
│   ├── PAPER_FINAL.md                # versión markdown extendida
│   ├── ANALISIS_FEATURE_SELECTION.md # detalle sección 4
│   ├── ALTERNATIVAS_FUTURAS.md       # detalle sección 7
│   └── GUIA_PROGRESO.md              # bitácora cronológica
└── paper/                            # LaTeX del paper (NO incluido en este commit)
    ├── paper.tex
    ├── paper.pdf
    └── figures/
```

---

*Última actualización: 2026-08-18*
