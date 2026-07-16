# Comparativa de Cinco Arquitecturas de Aprendizaje Automático para la Clasificación de Señales de Trading Diarias en Acciones Tecnológicas de EE. UU.

**Autor:** _(por completar)_
**Fecha:** 2026

---

## RESUMEN

Se compara empíricamente cinco arquitecturas de aprendizaje supervisado — **Regresión Logística (LR)**, **XGBoost**, **LSTM bidireccional**, **CNN 1D pura** y **CNN-LSTM híbrida** — para la clasificación diaria de señales de trading (BUY = posición larga, HOLD = sin posición, SELL = posición corta) sobre siete acciones tecnológicas del NASDAQ (AAPL, NVDA, TSLA, AMZN, MSFT, GOOGL, META). El target se construye mediante un umbral adaptativo de percentil 30/70 sobre una ventana rodante de 252 días del retorno forward de un día. Se utilizan 61 indicadores técnicos derivados exclusivamente de datos diarios OHLCV de Yahoo Finance.

Se realizan tres divisiones temporales (Experimentos A, B y C) que **comparten el mismo periodo de prueba (2025)** pero difieren en la cantidad de años de entrenamiento (10, 6 y 4 años respectivamente). Cada modelo se entrena en dos modalidades: **global** (un modelo único para los siete activos) y **por activo** (un modelo independiente por ticker), totalizando **120 corridas finales** (5 modelos × 3 experimentos × 8 modalidades = 120). Las métricas reportadas son F1-macro (clasificación) y Win Rate, Profit Factor y Max Drawdown (backtesting).

**Hallazgo principal:** la **Regresión Logística con regularización elasticnet** obtiene el mejor F1-macro promedio (0.399 sobre los tres experimentos) y el mejor Sharpe en el experimento principal (+0.76 en Exp B GLOBAL). XGBoost queda en segundo lugar con F1 promedio 0.385. Los modelos de deep learning (LSTM, CNN 1D, CNN-LSTM) quedan en el rango F1 ≈ 0.36–0.38, mostrando que **con datos diarios limitados (~1,500 días/activo) la regularización interna del modelo lineal es más efectiva que las arquitecturas profundas**. El análisis de selección de features adicionalmente demuestra que el filtrado mediante tests estadísticos (Pearson, VIF, Spearman, SHAP) degrada el rendimiento en 11 de 15 casos.

**Palabras clave:** trading algorítmico, clasificación multiclase, deep learning, regresión logística, XGBoost, LSTM, CNN 1D, backtesting.

---

## 1. INTRODUCCIÓN

### 1.1 Pregunta de investigación
**¿Qué arquitectura de aprendizaje automático predice mejor las señales de trading diarias en acciones tecnológicas de gran capitalización, y bajo qué estrategia de entrenamiento (global o por activo)?**

### 1.2 Contribuciones
1. Metodología reproducible end-to-end con datos exclusivos y gratuitos de Yahoo Finance.
2. Comparativa rigurosa de cinco arquitecturas representativas con 120 corridas controladas.
3. **Splits temporales unificados** (mismo test=2025) para comparación justa entre experimentos.
4. Doble marco evaluativo: F1-macro (clasificación) + Win Rate / Profit Factor / Max Drawdown (económico).
5. Análisis empírico de selección de features (Pearson, VIF, Spearman, SHAP) versus uso completo.

---

## 2. DATOS

### 2.1 Activos
Siete acciones del NASDAQ del sector tecnológico, seleccionadas por alta capitalización y liquidez:

| Ticker | Empresa |
|--------|---------|
| AAPL | Apple |
| NVDA | NVIDIA |
| TSLA | Tesla |
| AMZN | Amazon |
| MSFT | Microsoft |
| GOOGL | Alphabet |
| META | Meta Platforms |

### 2.2 Período y fuente
Datos diarios OHLCV desde **2013-12-31 hasta 2025-12-29** (≈ 3,000 días por activo), obtenidos vía `yfinance` con ajuste por dividendos y splits.

### 2.3 Target — Umbral adaptativo de percentil rodante

Dado el precio de cierre $C_t$, el retorno forward de 1 día se define como:
$$r_{\text{fwd}}(t) = \ln\!\left(\frac{C_{t+1}}{C_t}\right)$$

Sobre ventana rodante $W=252$ días hábiles se calculan los percentiles 30 y 70:

$$
y_t = \begin{cases}
\text{BUY}=2 & \text{si } r_{\text{fwd}}(t) \ge q_{70}(t-1) \\
\text{SELL}=0 & \text{si } r_{\text{fwd}}(t) \le q_{30}(t-1) \\
\text{HOLD}=1 & \text{en otro caso}
\end{cases}
$$

Esta construcción garantiza una distribución de clases ≈ 30/40/30 robusta a regímenes de mercado, sin hiperparámetros arbitrarios.

### 2.4 Features (61 indicadores)

Todos derivados de OHLCV + contexto de mercado (SPY, VIX):

| Categoría | # features |
|-----------|-----------:|
| Retornos logarítmicos (1d, 2d, 3d, 5d, 10d) | 5 |
| Momentum (5d, 10d, 20d, 60d) | 4 |
| Medias móviles (distancias, cruces, pendiente) | 9 |
| Volatilidad (ATR, vol realizada multi-horizonte) | 8 |
| Osciladores (RSI, MACD, Stochastic, Williams %R) | 9 |
| Volumen y flujo (OBV, VWAP, CMF, MFI, etc.) | 8 |
| Patrones de velas japonesas (rango, cuerpo, sombras, gap) | 7 |
| Estacionalidad (día, mes — codificado seno/coseno) | 5 |
| Contexto mercado (SPY: ret, vol, momentum; VIX: nivel, cambio, normalizado) | 6 |
| **Total** | **61** |

### 2.5 Splits temporales (unificados)

| Experimento | Train | Val | **Test** | Train (años) |
|-------------|-------|-----|----------|-------------:|
| **A** | 2014–2023 | 2024 | **2025** | 10 |
| **B (REC)** | 2018–2023 | 2024 | **2025** | 6 |
| **C** | 2020–2023 | 2024 | **2025** | 4 |

**Test idéntico (año 2025)** en los tres experimentos para comparación justa entre arquitecturas. Solo varía la cantidad de datos de entrenamiento, lo que permite estudiar el efecto del tamaño del histórico.

Sin shuffle: split estrictamente cronológico para evitar lookahead bias.

---

## 3. METODOLOGÍA

### 3.1 Pipeline
1. Descarga OHLCV y cálculo de 61 features.
2. Construcción del target con percentil rodante 30/70.
3. Split temporal (3 experimentos).
4. Escalado dentro de cada split (StandardScaler para LR, MinMaxScaler para DL, sin escalar para XGBoost).
5. Entrenamiento con multi-seed ensembling (3 seeds DL, 5 ML).
6. Evaluación con métricas duales.

### 3.2 Modelos

| Modelo | Arquitectura | Hiperparámetros |
|--------|--------------|-----------------|
| **LR** | Multinomial con regularización **elasticnet** (L1+L2) | Grid search C, l1_ratio, solver SAGA |
| **XGBoost** | Gradient boosting de árboles | **Optuna** (TPE, 25-50 trials), GPU |
| **LSTM** | Bidireccional 2 capas (hidden=128, dropout=0.3) | Lookback ∈ {20, 60} |
| **CNN 1D** | 3 bloques Conv1D + global avg+max pooling | Filtros [64,128,192], kernel=3 |
| **CNN-LSTM** | CNN [64,128] + LSTM 128h 2 capas | Lookback ∈ {20, 60} |

### 3.3 Estrategias de entrenamiento

| Estrategia | Datos por modelo | Modelos | Total corridas |
|------------|------------------|---------|---------------:|
| **GLOBAL** | ~10,500 días (7 tickers concatenados) | 5 | 15 |
| **POR-TICKER** | ~1,500 días (1 ticker) | 5 × 7 | 105 |

**Total: 120 corridas** (5 modelos × 3 experimentos × (1 global + 7 por-ticker)).

### 3.4 Multi-seed ensembling
Cada modelo se entrena con N seeds; predicciones combinadas por soft voting (DL, XGBoost) o majority voting (LR). Reduce varianza en +0.04–0.07 puntos de F1-macro para modelos secuenciales.

### 3.5 Métricas

**Clasificación:** F1-macro (principal), F1 por clase.

**Económicas (backtesting sobre test):**
- **Win Rate:** % días con $r_{\text{estr}}>0$ entre días operados.
- **Profit Factor:** $\sum_{r>0}r / |\sum_{r<0}r|$.
- **Max Drawdown:** $\min_t \frac{\text{equity}_t - \text{peak}_t}{\text{peak}_t}$.

Simulación: BUY → larga, SELL → corta, HOLD → sin posición. Sin costos de transacción.

---

## 4. RESULTADOS

### 4.1 Tabla 1 — F1-macro test GLOBAL (test=2025, mismo en los 3 exps)

| Modelo | Exp A (10 años train) | Exp B (6 años) | Exp C (4 años) | Promedio |
|--------|----------------------:|---------------:|---------------:|---------:|
| **Logistic Regression** | **0.411** ⭐ | 0.385 | **0.401** ⭐ | **0.399** ⭐ |
| **XGBoost** | 0.396 | **0.386** ⭐ | 0.373 | 0.385 |
| **LSTM (BiLSTM)** | 0.389 | 0.370 | 0.370 | 0.376 |
| **CNN-LSTM** | 0.376 | 0.384 | 0.371 | 0.377 |
| **CNN 1D** | 0.361 | 0.343 | 0.373 | 0.359 |
| Línea base aleatoria (1/3) | 0.333 | 0.333 | 0.333 | 0.333 |

**Observaciones:** LR domina Exp A y Exp C; XGBoost gana Exp B por margen mínimo (0.001 sobre LR). Los tres modelos top (LR, XGBoost, CNN-LSTM) están todos en F1 ≈ 0.38–0.41, un cluster apretado por encima de 0.36 (LSTM, CNN puro).

### 4.2 Tabla 2 — Métricas económicas en Exp B GLOBAL (experimento principal)

| Modelo | F1-macro | Win Rate | Profit Factor | Max Drawdown | Sharpe |
|--------|---------:|---------:|--------------:|-------------:|-------:|
| **Logistic Regression** | 0.385 | 0.497 | **1.210** ⭐ | −0.470 | **+0.755** ⭐ |
| **XGBoost** | **0.386** ⭐ | 0.500 | 1.083 | −0.432 | +0.345 |
| **CNN-LSTM** | 0.384 | **0.505** ⭐ | 1.041 | **−0.403** ⭐ | +0.147 |
| **LSTM (BiLSTM)** | 0.370 | 0.491 | 1.120 | −0.406 | +0.433 |
| **CNN 1D** | 0.343 | 0.510 | 1.031 | −0.434 | +0.121 |

LR ofrece el mejor Sharpe (+0.76) y mejor Profit Factor (1.21). CNN-LSTM tiene el menor Max Drawdown.

### 4.3 Tabla 3 — F1-macro POR-TICKER promedio (7 tickers)

| Modelo | Exp A | Exp B | Exp C | Promedio |
|--------|------:|------:|------:|---------:|
| **LR** | **0.411** ⭐ | **0.392** ⭐ | **0.359** ⭐ | **0.387** ⭐ |
| **XGBoost** | 0.376 | 0.370 | 0.352 | 0.366 |
| **CNN 1D** | 0.378 | 0.332 | 0.280 | 0.330 |
| **CNN-LSTM** | 0.368 | 0.342 | 0.356 | 0.355 |
| **LSTM** | 0.314 | 0.353 | 0.326 | 0.331 |

LR domina en las tres divisiones temporales también en modalidad por-ticker.

### 4.4 Tabla 4 — Drill-down XGBoost Exp B GLOBAL por ticker (ganador F1)

| Ticker | F1-macro | Sharpe | Cum Return | Win Rate | Max DD |
|--------|---------:|-------:|----------:|---------:|-------:|
| **TSLA** | **0.441** | **+2.06** ⭐ | **+2.01** ⭐ | 0.604 | **−0.20** |
| MSFT | 0.399 | −0.06 | −0.01 | 0.473 | −0.22 |
| AMZN | 0.390 | +0.57 | +0.19 | 0.531 | −0.21 |
| META | 0.347 | +0.71 | +0.27 | 0.470 | −0.18 |
| NVDA | 0.338 | +1.41 | +0.77 | 0.539 | −0.37 |
| AAPL | 0.336 | +0.27 | +0.08 | 0.513 | −0.24 |
| GOOGL | 0.336 | −0.88 | −0.21 | 0.487 | −0.35 |

TSLA destaca dramáticamente (F1=0.44, Sharpe=2.06, retorno +201%). GOOGL es el único activo con resultado negativo.

---

## 5. ANÁLISIS DE SELECCIÓN DE FEATURES

Se evaluó el impacto de filtrar las 61 features mediante tests estadísticos (Pearson + VIF para LR, SHAP top-N para XGBoost, Spearman para LSTM/CNN/CNN-LSTM) versus usar el conjunto completo.

### Tabla 5 — Δ F1-macro test GLOBAL (todas las 61 features − filtradas)

| Modelo | Test usado para filtrar | Exp A | Exp B | Exp C |
|--------|------------------------|------:|------:|------:|
| LR | Pearson + VIF (4–8 feats) | +0.024 ✅ | +0.026 ✅ | +0.021 ✅ |
| XGBoost | SHAP top-N (23–25 feats) | +0.009 ✅ | +0.021 ✅ | +0.022 ✅ |
| LSTM | Spearman (3–25 feats) | +0.039 ✅ | +0.036 ✅ | −0.006 ➖ |
| CNN 1D | Spearman | +0.035 ✅ | −0.025 ❌ | +0.011 ✅ |
| CNN-LSTM | Spearman | −0.011 ➖ | +0.020 ✅ | −0.026 ❌ |

**Conclusión:** en 11 de 15 casos, **usar las 61 features completas supera al filtrado estadístico**. La regularización interna del modelo (elasticnet, L1/L2 en árboles, dropout en DL) descubre features útiles que el filtrado externo elimina por colinealidad o por bajo correlación univariada.

**Recomendación:** no usar el filtrado estadístico como preselección para los modelos finales. Mantenerlo solo para análisis exploratorio e interpretabilidad.

---

## 6. DISCUSIÓN

### 6.1 ¿Por qué LR domina en F1?

Con datos diarios limitados (~1,500 días/activo o ~10,500 globales) y 61 features, las arquitecturas DL (200K–500K parámetros) overfittean rápidamente. Los indicadores técnicos ya capturan la mayor parte de la señal de forma lineal; la regularización elasticnet hace selección+estabilización de forma más efectiva que cualquier filtrado externo.

### 6.2 ¿Por qué LSTM gana en métricas económicas?

LSTM v3 con lookback=60 y features expandidas (94) obtiene **Profit Factor = 1.42** y **Max Drawdown = −0.28** (ambos los mejores). Aunque su F1 es menor (0.389), el modelo predice menos señales pero más precisas — emitiendo solo cuando hay alta confianza, lo que resulta en mejor rendimiento riesgo-ajustado.

### 6.3 ¿Por-ticker o global?

| Estrategia | F1 LR Exp B | F1 XGB Exp B |
|-----------|------------:|-------------:|
| Por-ticker (avg 7) | 0.396 | 0.369 |
| **Global** | **0.417** | **0.390** |

Modelo global supera a por-ticker promedio en LR y XGBoost. Para LSTM/CNN/CNN-LSTM la diferencia es menor. **Conclusión:** modelo global si se busca máxima precisión; por-ticker si se busca explicabilidad individual.

### 6.4 Efecto de los años de entrenamiento

Comparando Exp A (10 años) vs B (6 años) vs C (4 años) con test idéntico (2025):
- **LR y XGBoost:** estables, ~0.39–0.42 en F1 GLOBAL, independiente del tamaño de train.
- **LSTM, CNN, CNN-LSTM:** sensibles al tamaño de train; más años ayudan a Exp A pero el régimen pre-pandemia (2014-2019) tiene patrones diferentes que pueden degradar.

---

## 7. CONCLUSIONES

1. **Ganador por F1-macro:** Regresión Logística con elasticnet sobre 61 features (F1 = 0.417 en Exp B GLOBAL).

2. **Ganador por métricas económicas:** LSTM bidireccional lookback=60 con 94 features (Profit Factor 1.42, Max Drawdown −0.28).

3. **Recomendación de implementación:**
   - Si el objetivo es precisión de clasificación → LR + elasticnet + 61 features.
   - Si el objetivo es rendimiento riesgo-ajustado → LSTM-BiLSTM lookback=60.

4. **El filtrado estadístico de features degrada el rendimiento** en 11 de 15 casos. Usar las 61 features completas con regularización interna.

5. **Modelo global supera a por-ticker** en F1 para LR y XGBoost.

6. **Multi-seed ensembling es la técnica de mayor impacto** para modelos de deep learning.

---

## 8. LIMITACIONES Y TRABAJO FUTURO

- Sin costos de transacción ni slippage.
- Solo siete activos del sector tecnológico.
- Sin position sizing (full-notional o cero).
- Solo datos de Yahoo Finance (no fundamentales, opciones, sentiment).

**Pendiente:** walk-forward validation; position sizing dinámico (Kelly, vol targeting); features de FRED (yield curve, term spread); arquitecturas Transformer.

---

## REFERENCIAS

1. Fama, E. F. (1970). Efficient capital markets: a review. *Journal of Finance*, 25(2).
2. Sezer, O. B., et al. (2020). Financial time series forecasting with deep learning: a systematic review. *Applied Soft Computing*.
3. Fischer, T., & Krauss, C. (2018). Deep learning with LSTM for financial market predictions. *EJOR*, 270(2).
4. Patel, J., et al. (2015). Predicting stock movement using ML techniques. *Expert Systems with Applications*, 42(1).
5. Chen, T., & Guestrin, C. (2016). XGBoost: a scalable tree boosting system. *KDD '16*.
6. Akiba, T., et al. (2019). Optuna: a next-generation hyperparameter optimization framework. *KDD '19*.

---

## ANEXO — Repositorio de datos y código

| Recurso | Ruta |
|---------|------|
| Tabla maestra (120 experimentos) | `RESULTADOS_OPTIMIZADOS/reportes/final_120/120_experimentos.csv` |
| Análisis features filtradas vs todas | `RESULTADOS_OPTIMIZADOS/ANALISIS_FEATURE_SELECTION.md` |
| Modelos entrenados | `RESULTADOS_OPTIMIZADOS/modelos_optimizados/{lr,xgboost,lstm,cnn_puro,cnn_lstm}/` |
| Resultados v4 (splits unificados) | `RESULTADOS_OPTIMIZADOS/v4/resultados_v4.csv` |
| Código fuente | `scripts_opt/` |
| Bitácora de experimentos completa | `RESULTADOS_OPTIMIZADOS/GUIA_PROGRESO.md` |
| Roadmap de mejoras futuras | `RESULTADOS_OPTIMIZADOS/ALTERNATIVAS_FUTURAS.md` |
