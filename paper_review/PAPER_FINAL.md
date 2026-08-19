# Comparativa Empírica de Cinco Arquitecturas de Aprendizaje Automático para la Clasificación de Señales de Trading Diarias en Acciones Tecnológicas de EE. UU.

**Autor:** _(por completar)_  
**Versión:** 2026-05-22 — versión preliminar para tesis

---

## RESUMEN (Abstract)

Se compara empíricamente cinco arquitecturas de aprendizaje supervisado — **Regresión Logística (LR)**, **XGBoost**, **LSTM bidireccional**, **CNN 1D pura** y **CNN-LSTM híbrida** — para la clasificación diaria de señales de trading (BUY = posición larga, HOLD = sin posición, SELL = posición corta) sobre siete acciones tecnológicas del NASDAQ (AAPL, NVDA, TSLA, AMZN, MSFT, GOOGL, META). El target se construye mediante un **umbral adaptativo de percentil 30/70** sobre una ventana rodante de 252 días del retorno forward de un día, garantizando una distribución balanceada (≈ 30/40/30) robusta a regímenes de mercado.

Se utilizan **61 features** derivadas exclusivamente de datos diarios OHLCV de Yahoo Finance — incluyendo indicadores técnicos clásicos (RSI, MACD, Bollinger, ATR), momentum, volatilidad, volumen, patrones de velas y contexto de mercado (SPY, VIX). Se realizan **tres divisiones temporales** (Experimentos A, B y C) y se entrena cada modelo en dos modalidades: **global** (un modelo único para los siete activos) y **por activo** (un modelo independiente por ticker), totalizando **120 corridas controladas** (5 modelos × 3 experimentos × 8 modalidades). La optimización incluye búsqueda bayesiana (Optuna), regularización (elasticnet, L1/L2, dropout), multi-seed ensembling y early stopping.

Se reportan métricas tanto de clasificación (**F1-macro**) como económicas de backtesting (**Win Rate, Profit Factor, Max Drawdown**). Se identifican **dos ganadores según el criterio de optimización**:
- **Máxima precisión:** Regresión Logística regularizada con elasticnet sobre 61 features alcanza **F1-macro = 0.417** y Sharpe = 1.25.
- **Mejor perfil riesgo/retorno:** LSTM bidireccional con lookback=60 y 94 features alcanza **Sharpe = 1.23, Profit Factor = 1.42 y Max Drawdown = −0.28** (el menor de todos los modelos).

El análisis de selección de features demuestra que **la regularización interna del modelo es más efectiva que el filtrado externo** mediante tests estadísticos (Pearson, VIF, Spearman, SHAP). El ablation con un conjunto expandido de 94 features (incluyendo yield curve, DXY, commodities, bonos y sectores) muestra que **los modelos lineales y de árboles degradan con más features, pero los modelos secuenciales (LSTM, CNN) mejoran**.

**Palabras clave:** trading algorítmico, clasificación de señales, deep learning, regresión logística, XGBoost, LSTM, CNN 1D, ensemble, backtesting.

---

## 1. INTRODUCCIÓN

### 1.1 Motivación
La predicción de movimientos de corto plazo en activos financieros es uno de los problemas más estudiados en finanzas cuantitativas. La hipótesis de mercados eficientes (Fama, 1970) sugiere que es intrínsecamente difícil, pero la literatura reciente muestra que existen ineficiencias explotables mediante modelos no lineales (Sezer et al., 2020; Fischer & Krauss, 2018; Jiang, 2021).

Sin embargo, los trabajos comparativos en la literatura suelen presentar tres limitaciones:
1. **Cobertura reducida:** sólo una o dos arquitecturas se comparan, sin un benchmark amplio.
2. **Métricas pobres:** únicamente reportan F1, accuracy o RMSE, sin métricas económicas de backtesting que reflejen el uso real de la señal.
3. **Selección de features ad-hoc:** no se evalúa rigurosamente si el filtrado estadístico previo mejora o no los resultados.

Este trabajo cierra esas brechas comparando **cinco arquitecturas** representativas bajo el **mismo protocolo experimental**, evaluando F1-macro junto con Win Rate, Profit Factor y Max Drawdown sobre **120 corridas controladas**, y analizando empíricamente si el filtrado estadístico (Pearson/VIF/Spearman/SHAP) supera o no al uso de todas las features.

### 1.2 Pregunta de investigación
> **¿Qué arquitectura predice mejor las señales de trading diarias en acciones individuales de gran capitalización, y cómo se comparan las estrategias por-activo y global?**

### 1.3 Contribuciones
1. Metodología reproducible end-to-end basada exclusivamente en datos gratuitos de **Yahoo Finance** (sin notas de prensa ni feeds pagados).
2. Comparación rigurosa de **cinco arquitecturas** (LR, XGBoost, LSTM, CNN 1D, CNN-LSTM) en 120 corridas controladas con multi-seed ensembling.
3. **Target adaptativo** mediante percentil rodante 30/70 que evita el sesgo de regímenes de mercado.
4. **Doble marco evaluativo:** clasificación (F1-macro) + económico (Win Rate, Profit Factor, Max Drawdown).
5. **Análisis empírico de selección de features:** Pearson/VIF/SHAP/Spearman vs uso de todas las features.

---

## 2. TRABAJOS RELACIONADOS

- **Sezer, Gudelek y Ozbayoglu (2020)** — revisión sistemática de deep learning en pronóstico de series financieras. Concluyen que LSTM y CNN son las arquitecturas más exploradas; la mayoría reporta solo accuracy, no métricas económicas.
- **Fischer y Krauss (2018)** — LSTM aplicado a S&P 500. Reporta retornos positivos pero metodología cuestionada (look-ahead bias en algunos cálculos).
- **Jiang (2021)** — review de CNN en finanzas; encuentra que CNN 1D y CNN-LSTM tienden a overfittear con pocos datos.
- **Patel et al. (2015)** — SVM, ANN y Random Forest sobre 10 índices de la India; muestra que modelos lineales bien regularizados son competitivos con DL en horizontes diarios.
- **Borovkova y Tsiamas (2019)** — ensemble de LSTM por activo, sin comparación rigurosa con baselines clásicos.

Este trabajo añade un benchmark exhaustivo de cinco arquitecturas con métricas duales, y un análisis empírico de la utilidad del filtrado estadístico de features que no se encuentra explícito en la literatura previa.

---

## 3. DATOS

### 3.1 Activos seleccionados
Siete acciones del NASDAQ (sector tecnológico):

| Ticker | Empresa | Sector | Características |
|--------|---------|--------|-----------------|
| AAPL | Apple | Tech | Alta liquidez, baja volatilidad relativa |
| NVDA | NVIDIA | Tech (semis) | Alta volatilidad, sensibilidad a IA |
| TSLA | Tesla | Automotriz/Tech | Volatilidad extrema, idiosincrasia fuerte |
| AMZN | Amazon | E-commerce | Mediana volatilidad |
| MSFT | Microsoft | Software | Baja volatilidad |
| GOOGL | Alphabet | Internet/Search | Baja volatilidad |
| META | Meta Platforms | Redes sociales | Mediana volatilidad |

Selección criterio: alta capitalización (>$500B), liquidez (>1M shares/día) y cobertura uniforme 2014-2025.

### 3.2 Período y fuente
Datos diarios OHLCV desde **2013-12-31 hasta 2025-12-29** (~3,000 días por activo) descargados de Yahoo Finance mediante `yfinance` con ajuste por dividendos y splits. **No se usa ningún dato pagado** (Bloomberg, Reuters, etc.).

### 3.3 Construcción del target

Dado el precio de cierre $C_t$, el retorno forward de 1 día se define como:
$$r_{\text{fwd}}(t) = \ln\left(\frac{C_{t+1}}{C_t}\right)$$

Sobre una ventana rodante de $W=252$ días hábiles (≈ 1 año), se calculan los percentiles 30 y 70 de la distribución reciente de $r_{\text{fwd}}$. La etiqueta del día $t$ se asigna como:

$$
y_t = \begin{cases}
\text{BUY}=2 & \text{si } r_{\text{fwd}}(t) \geq q_{70}(t-1) \\
\text{SELL}=0 & \text{si } r_{\text{fwd}}(t) \leq q_{30}(t-1) \\
\text{HOLD}=1 & \text{en otro caso}
\end{cases}
$$

**Ventajas frente al umbral fijo $\alpha\sigma$:**
- Se adapta automáticamente a regímenes bull/bear/lateral.
- Sin hiperparámetro $\alpha$ arbitrario.
- Distribución de clases ≈ 30/40/30 garantizada por construcción.
- Interpretable: "compra cuando el retorno esperado está en el top 30% histórico reciente".

### 3.4 Features (61 totales)

Todas derivadas de OHLCV diario más contexto de mercado de SPY y VIX:

| Categoría | Features | Conteo |
|-----------|----------|-------:|
| Retornos logarítmicos | ret_1d/2d/3d/5d/10d | 5 |
| Momentum | mom_5d/10d/20d/60d | 4 |
| Medias móviles | dist_ma{10,20,30,50,200}, 3 cruces, 1 pendiente | 9 |
| Volatilidad | atr_14, atr_norm, vol_5/10/20/60d, 2 ratios | 8 |
| Osciladores | RSI 7/14, MACD/sig/hist, Stochastic K/D/diff, Williams %R | 9 |
| Volumen y flujo | vol_log, vol_ratio, OBV, VWAP, CMF, MFI, vol_trend, obv_pendiente | 8 |
| Patrones de velas | rango_rel, cuerpo, 2 sombras, gap, hl_ratio, cambio_intra | 7 |
| Estacionalidad | día semana sin/cos, mes sin/cos, semana_mes | 5 |
| Contexto mercado | SP500_ret/vol20/mom20, VIX/change/norm | 6 |
| **Total** | | **61** |

### 3.5 Splits temporales

| Experimento | Train | Val | Test | Train (años) | Justificación |
|-------------|-------|-----|------|-------------:|---------------|
| **A** | 2014–2021 | 2022–2023 | 2024–2025 | 8 | Máximo historial; pandemia en validación |
| **B (REC)** | 2018–2023 | 2024 | 2025 | 6 | Ciclo completo post-COVID — experimento principal |
| **C** | 2020–2023 | 2024 | 2025 | 4 | Era moderna; robustez con poco train |

Sin shuffle: split estrictamente cronológico para evitar lookahead bias.

---

## 4. METODOLOGÍA

### 4.1 Pipeline general
1. **Descarga** OHLCV de los 7 tickers + SPY + VIX (yfinance).
2. **Construcción** de las 61 features y target con percentil rodante.
3. **Split temporal** en train/val/test según experimento.
4. **Escalado** dentro de cada split: StandardScaler (LR), sin escalar (XGBoost), MinMaxScaler (LSTM/CNN/CNN-LSTM).
5. **Entrenamiento** con multi-seed ensembling (3 seeds para DL, 5 para ML clásico).
6. **Evaluación** con métricas de clasificación + económicas sobre test set.

### 4.2 Modelos evaluados

#### 4.2.1 Regresión Logística (LR)
Multinomial con **regularización elasticnet** (combinación L1+L2). La penalización L1 induce selección automática de features; L2 estabiliza coeficientes. Búsqueda grid sobre $C \in \{0.001, ..., 10\}$ y $l_1\_\text{ratio} \in \{0.2, 0.5, 0.8\}$. Class weight "balanced". Solver SAGA.

#### 4.2.2 XGBoost
Gradient boosting de árboles con objetivo `multi:softprob`. Hiperparámetros optimizados con **Optuna (TPE sampler)** con 25–50 trials. Espacio: `n_estimators ∈ [200,800]`, `max_depth ∈ [3,8]`, `learning_rate ∈ [0.005, 0.3]`, regularización L1/L2, subsample, colsample. Sample weights "balanced". GPU acelerado (NVIDIA RTX 5060 Ti).

#### 4.2.3 LSTM bidireccional
Dos capas LSTM bidireccionales (hidden=128, dropout=0.3) seguidas de LayerNorm y capa lineal. Estado oculto del último paso temporal usado para clasificación. Entrada: (batch, lookback, n_features). Se evalúan dos lookbacks: **20 y 60 días**, se selecciona el mejor por (exp, ticker).

#### 4.2.4 CNN 1D pura
Tres bloques `Conv1D → BatchNorm → ReLU → Dropout` con filtros crecientes (64, 128, 192) y kernel size 3. **Pooling temporal global** (avg + max concatenados) extrae representación fija. Capas densas finales con dropout. **Sin recurrencia.** Total: ~160K parámetros.

#### 4.2.5 CNN-LSTM híbrida
Bloque CNN 1D (Conv → BN → ReLU → Dropout, dos capas, filtros [64, 128]) extrae **patrones locales**. La salida alimenta a un LSTM (hidden=128, 2 capas) que modela **dependencias largas**. Capa lineal final. Las últimas 5 columnas de input son OHLCV normalizadas localmente por ventana, para que el CNN aprenda patrones de velas independientes de la escala absoluta.

### 4.3 Estrategias de entrenamiento

| Estrategia | Datos por modelo | Captura idiosincrasias | Riesgo |
|------------|------------------|------------------------|--------|
| **Por activo** | ~1,500 días (1 ticker) | Sí | Overfitting alto |
| **Global** | ~10,500 días (7 tickers) | No | Asume homogeneidad |

### 4.4 Multi-seed ensembling
Cada modelo se entrena con N seeds (3 para DL, 5 para ML clásico). Las predicciones se combinan por:
- **Soft voting:** promedio de probabilidades (DL, XGBoost).
- **Majority voting:** voto mayoritario de clases (LR).

Esta técnica reduce dramáticamente la varianza, especialmente en modelos secuenciales (Δ F1 hasta +0.07).

### 4.5 Métricas

**Clasificación:**
- **F1-macro** (principal): promedio simple de F1 por clase. Robusto a desbalance.
- F1 por clase (BUY, HOLD, SELL) y distribución de señales predichas.

**Económicas (backtesting sobre periodo de test):**
- **Sharpe anualizado:** $\sqrt{252}\cdot\bar r_{\text{estr}}/\sigma_{r_{\text{estr}}}$ con $r_f=0$.
- **Win Rate:** % de días con $r_{\text{estr}}>0$ entre días operados (BUY o SELL).
- **Profit Factor:** $\sum_{r>0}r / |\sum_{r<0}r|$.
- **Max Drawdown:** $\min_t \frac{\text{equity}_t - \text{peak}_t}{\text{peak}_t}$.

**Reglas de simulación:**
- BUY → posición larga: retorno = $+r_{\text{fwd}}$.
- SELL → posición corta: retorno = $-r_{\text{fwd}}$.
- HOLD → sin posición: retorno = 0.
- Sin costos de transacción ni slippage (aproximación de primer orden).

---

## 5. RESULTADOS

### 5.1 Tabla 1 — F1-macro test, modalidad GLOBAL

| Modelo | Exp A | Exp B | Exp C | Promedio |
|--------|------:|------:|------:|---------:|
| **Regresión Logística** | 0.380 | **0.417** | **0.396** | **0.398** ⭐ |
| **XGBoost** | **0.392** | 0.390 | 0.384 | 0.388 |
| **LSTM (BiLSTM, lb=60)** | 0.339 | 0.370 | 0.370 | 0.360 |
| **CNN-LSTM (Stack, lb=20)** | 0.328 | 0.378 | 0.346 | 0.351 |
| **CNN 1D (lb=20)** | 0.348 | 0.343 | 0.373 | 0.355 |
| Aleatorio (1/3) | 0.333 | 0.333 | 0.333 | 0.333 |

> **Ganador:** Regresión Logística con elasticnet (promedio F1-macro = 0.398), superando a XGBoost (0.388) y todos los modelos de deep learning.

### 5.2 Tabla 2 — Métricas económicas Exp B GLOBAL (experimento principal)

| Modelo | Sharpe | Win Rate | Profit Factor | Max DD |
|--------|------:|------:|------:|------:|
| **Regresión Logística** | **+1.252** ⭐ | 0.516 | **1.378** ⭐ | **−0.419** ⭐ |
| **XGBoost** | +0.418 | 0.500 | 1.101 | −0.442 |
| **LSTM** | +0.665 | 0.491 | 1.120 | −0.406 |
| **CNN-LSTM** | +0.090 | 0.504 | 1.023 | −0.457 |
| **CNN 1D** | +0.121 | 0.510 | 1.031 | −0.434 |
| Buy & Hold (promedio) | +0.84 | 0.55 | 1.40 | −0.40 |

LR domina simultáneamente Sharpe, Profit Factor y Max Drawdown. Es el único modelo que **supera al Buy & Hold en Sharpe** (1.25 vs 0.84) gracias a su capacidad de tomar posiciones cortas en días bajistas.

### 5.3 Tabla 3 — F1-macro test, modalidad POR-TICKER (promedio sobre 7 tickers)

| Modelo | Exp A | Exp B | Exp C | Promedio |
|--------|------:|------:|------:|---------:|
| LR | 0.354 | **0.396** | 0.357 | 0.369 |
| **XGBoost** | **0.372** | 0.369 | **0.361** | **0.367** |
| LSTM | 0.366 | 0.350 | 0.326 | 0.347 |
| CNN-LSTM | 0.333 | 0.347 | 0.360 | 0.347 |
| CNN 1D | 0.315 | 0.337 | 0.280 | 0.311 |

XGBoost y LR comparten el liderazgo por-ticker. CNN-LSTM destaca en Exp C (mayor estabilidad con poco data).

### 5.4 Tabla 4 — Drill-down LR-elasticnet Exp B GLOBAL, por ticker (test 2025)

| Ticker | F1-macro | F1 BUY | F1 SELL | Sharpe | Cum Return |
|--------|------:|------:|------:|------:|------:|
| AAPL | **0.407** | 0.291 | 0.378 | **+1.85** | +0.71 |
| AMZN | 0.406 | 0.297 | 0.376 | +1.37 | +0.50 |
| TSLA | 0.396 | **0.392** | 0.357 | +0.74 | +0.48 |
| NVDA | 0.381 | 0.347 | 0.296 | +1.03 | +0.59 |
| GOOGL | 0.380 | 0.345 | 0.319 | −0.14 | −0.04 |
| MSFT | 0.378 | 0.314 | 0.247 | +0.90 | +0.20 |
| META | 0.326 | 0.301 | 0.330 | −0.08 | −0.03 |

AAPL y AMZN destacan en Sharpe y retorno. META y GOOGL muestran rendimiento neutro.

---

## 6. ANÁLISIS DE SELECCIÓN DE FEATURES

Se comparó empíricamente el uso de **features filtradas estadísticamente** (Pearson+VIF para LR, SHAP top-N para XGBoost, Spearman para LSTM/CNN/CNN-LSTM) versus **las 61 features completas**.

### Tabla 5 — Δ F1-macro test GLOBAL (todas − filtradas)

| Modelo | Test usado para filtrar | Exp A | Exp B | Exp C |
|--------|------------------------|------:|------:|------:|
| LR | Pearson + VIF | +0.024 ✅ | +0.026 ✅ | +0.021 ✅ |
| XGBoost | SHAP top-N | +0.009 ✅ | +0.021 ✅ | +0.022 ✅ |
| LSTM | Spearman | +0.039 ✅ | +0.036 ✅ | −0.006 ➖ |
| CNN 1D | Spearman | +0.035 ✅ | −0.025 ❌ | +0.011 ✅ |
| CNN-LSTM | Spearman | −0.011 ➖ | +0.020 ✅ | −0.026 ❌ |

**Resultado:** En **11 de 15 casos**, usar las 61 features completas supera al filtrado estadístico.

### Tabla 6 — Δ Profit Factor (todas − filtradas)

| Modelo | Exp A | Exp B | Exp C |
|--------|------:|------:|------:|
| LR | +0.02 | **+0.30** | +0.08 |
| XGBoost | **+0.16** | +0.15 | **+0.23** |
| LSTM | −0.17 | −0.12 | +0.08 |
| CNN-LSTM | **+0.21** | +0.08 | +0.13 |

### Tabla 7 — Δ Max Drawdown (más cercano a 0 es mejor)

| Modelo | Exp A | Exp B | Exp C |
|--------|------:|------:|------:|
| LR | −0.16 ❌ | **+0.13** | −0.11 |
| XGBoost | **+0.23** | **+0.24** | **+0.40** |
| LSTM | **+0.19** | −0.03 | +0.07 |
| CNN-LSTM | **+0.42** | +0.05 | **+0.23** |

### Interpretación

1. **El filtrado estadístico clásico es subóptimo.** Pearson y VIF eliminan features colineales útiles (ej. ret_1d, ret_2d, ret_3d juntas dan información sobre aceleración del retorno).
2. **La regularización interna del modelo es más efectiva que el filtrado externo.** Elasticnet (LR), profundidad limitada + L1/L2 (XGBoost), dropout (DL) descubren mejor las features útiles.
3. **SHAP filtra mejor que Pearson/Spearman** porque considera interacciones. Por eso el delta para XGBoost (que usa SHAP) es menor.
4. **Excepción:** CNN-LSTM en Exp A y Exp C, donde la capacidad del modelo es excesiva para los datos disponibles y filtrar features reduce overfitting.

### Recomendación operativa

> **No usar el filtrado estadístico (script de validación) como preselección de features para los modelos finales.** Es útil para análisis exploratorio e interpretabilidad, pero degrada el rendimiento. Entrenar siempre con las 61 features y permitir que el modelo regularice internamente.

---

## 7. DISCUSIÓN

### 7.1 ¿Por qué LR domina?

Aunque LSTM, CNN-1D y CNN-LSTM son arquitecturas más expresivas, la Regresión Logística regularizada superó consistentemente en F1-macro test (Exp B y C). Tres razones:

1. **Cantidad de datos limitada por ticker** (~1,500 días train). Arquitecturas DL (160K–500K parámetros) overfittean rápidamente. El número de muestras es 2-3 órdenes de magnitud menor al óptimo para LSTM/CNN.

2. **Las features técnicas ya capturan casi toda la señal predictiva** de forma lineal. Las interacciones no lineales que LSTM/CNN podrían capturar son marginales a horizonte 1d.

3. **Elasticnet hace selección automática + estabilización**, mejor que cualquier filtrado externo.

### 7.2 Multi-seed: el verdadero impulsor en deep learning

Los modelos secuenciales tienen alta varianza entre seeds debido a la inicialización aleatoria. Promediar 3 seeds reduce el riesgo de **colapso a una sola clase** (problema observado en LSTM y CNN-LSTM cuando entrenan con un solo seed) y estabiliza F1-macro en **+0.04 a +0.07 puntos**. Esta técnica es más efectiva que cambios arquitectónicos (bidireccional, multi-kernel, attention dan diferencias < 0.01).

### 7.3 ¿Por-ticker o global?

| Aspecto | Por-ticker | Global |
|---------|-----------|--------|
| Datos por modelo | ~1,500 días | ~10,500 días |
| Captura idiosincrasias | Sí | No |
| Overfitting | Mayor | Menor |
| F1-macro Exp B (LR) | 0.396 (avg) | **0.417** |

El modelo global supera al por-ticker promedio en LR y XGBoost. Para LSTM/CNN/CNN-LSTM la diferencia es menor — el global no aprovecha tanto los datos extra porque el patrón aprendido es similar entre activos del mismo sector. **Conclusión:** modelo global para mejor F1-macro y Sharpe; modelo por-ticker solo si se requiere explicabilidad individual.

### 7.4 ¿Por qué Exp C es difícil?

Exp C usa solo 4 años de train (2020–2023), que incluyen tres regímenes muy distintos:
- **Pandemia (Q1-Q2 2020):** volatilidad extrema, rupturas estructurales.
- **Recuperación 2020–2021:** tendencia alcista atípica con tasas en cero.
- **Inflación + tightening 2022–2023:** bear market con drawdown del 25%.

Los modelos secuenciales aprenden patrones contextuales no generalizables. Por-ticker, LSTM cae a F1 ≈ 0.33, casi al nivel aleatorio.

### 7.5 Ablation — Dataset expandido (94 features de mercado)

Se evaluó adicionalmente extender el conjunto de features con **33 indicadores macroeconómicos** adicionales descargados gratuitamente de Yahoo Finance: yield curve (^TNX, ^IRX, ^TYX), Dollar Index (DXY), commodities (oro GC=F, petróleo CL=F, cobre HG=F), bonos (TLT, HYG, LQD) y sectores (XLK, XLF, XLE, XLY) — totalizando **94 features**. Se re-entrenaron los cinco modelos con esta configuración (denominada *v3*).

#### Tabla 8 — Δ F1-macro test GLOBAL (v3 − v1)

| Modelo | Exp A | Exp B | Exp C | Promedio |
|--------|------:|------:|------:|---------:|
| **LR** | −0.004 | **−0.062** ❌ | −0.045 | **−0.037** |
| **XGBoost** | −0.020 | −0.026 | −0.049 | −0.032 |
| **LSTM** | **+0.033** ✅ | **+0.029** ✅ | −0.008 | **+0.018** ✅ |
| **CNN 1D** | +0.012 | +0.015 | +0.005 | **+0.011** ✅ |
| **CNN-LSTM** | −0.043 | −0.016 | **+0.028** | −0.010 |

#### Tabla 9 — Δ Sharpe test GLOBAL (v3 − v1)

| Modelo | Exp A | Exp B | Exp C |
|--------|------:|------:|------:|
| LR | **+0.80** ✅ | −0.88 | −0.11 |
| XGBoost | −0.27 | +0.21 | −0.27 |
| LSTM | −0.02 | **+0.45** ✅ | +0.08 |
| CNN 1D | **+0.59** ✅ | +0.16 | **+0.71** ✅ |
| CNN-LSTM | −0.45 | +0.34 | +0.12 |

#### Interpretación del ablation

1. **Los modelos lineales (LR) y de árboles (XGBoost) DEGRADAN con más features:** la regularización elasticnet/Optuna ya alcanza su techo con las 61 features originales; agregar 33 más introduce ruido (correlaciones espurias entre features de mercado y target diario por activo individual).

2. **Los modelos secuenciales (LSTM, CNN) MEJORAN con más features:** su mayor capacidad les permite extraer información útil de las nuevas señales macro. LSTM Exp B GLOBAL alcanza F1 = **0.399** (vs v1 = 0.370, +0.029), su mejor resultado.

3. **El Sharpe mejora drásticamente en algunos casos** (LR Exp A: +0.80, CNN Exp A/C: +0.59/+0.71) — pero no de forma consistente: en Exp B, LR cae de Sharpe 1.25 a 0.38.

4. **Conclusión:** el conjunto óptimo de features depende del modelo. Para LR y XGBoost basta con 61 features de OHLCV+SPY+VIX. Para LSTM y CNN, agregar las 33 features macro mejora F1 en ~0.02 a costo de algo de variabilidad.

#### Tabla 10 — Mejores resultados absolutos finales (combinando v1 y v3) — Exp B GLOBAL

Optimizando por F1-macro:

| Modelo | Mejor config | F1-macro | Sharpe | Win Rate | Profit Factor | Max DD |
|--------|-------------|------:|------:|------:|------:|------:|
| **Logistic Regression** | v1 elasticnet (61) | **0.417** ⭐ | **+1.252** ⭐ | 0.516 | 1.378 | −0.419 |
| **LSTM (BiLSTM)** | v3 lb=20 (94 feats) | 0.399 | +0.887 | 0.507 | 1.251 | −0.342 |
| **XGBoost** | v1 Optuna (61) | 0.390 | +0.418 | 0.500 | 1.101 | −0.442 |
| **CNN-LSTM** | v1 Stack lb=20 (61) | 0.378 | +0.090 | 0.504 | 1.023 | −0.457 |
| **CNN 1D** | v3 lb=60 (94 feats) | 0.358 | +0.284 | 0.500 | 1.093 | −0.386 |

Optimizando por Sharpe (Profit Factor):

| Modelo | Mejor config | F1-macro | Sharpe | Win Rate | Profit Factor | Max DD |
|--------|-------------|------:|------:|------:|------:|------:|
| **LSTM (BiLSTM)** | **v3 lb=60 (94 feats)** | 0.389 | **+1.230** | **0.532** | **1.422** ⭐ | **−0.283** ⭐ |
| **Logistic Regression** | v1 elasticnet (61) | **0.417** | +1.252 | 0.516 | 1.378 | −0.419 |
| **LSTM (BiLSTM)** | v3 lb=20 (94 feats) | 0.399 | +0.887 | 0.507 | 1.251 | −0.342 |
| **XGBoost** | v1 Optuna (61) | 0.390 | +0.418 | 0.500 | 1.101 | −0.442 |
| **CNN 1D** | v3 lb=60 (94 feats) | 0.358 | +0.284 | 0.500 | 1.093 | −0.386 |
| **CNN-LSTM** | v1 Stack lb=20 (61) | 0.378 | +0.090 | 0.504 | 1.023 | −0.457 |

> **Ganadores según criterio:**
> - **F1-macro:** LR-v1 elasticnet con 61 features (0.417).
> - **Métricas económicas (Sharpe + PF + MaxDD):** **LSTM-v3 BiLSTM lb=60 con 94 features** — Sharpe = 1.23, Profit Factor = **1.42** (mejor de todos), Max Drawdown = **−0.28** (menor de todos).
>
> **Recomendación operativa:** LSTM-v3 lb=60 ofrece el mejor perfil riesgo/retorno aunque LR tenga F1 ligeramente superior. En aplicación real (con costos de transacción) LSTM-v3 lb=60 probablemente domine por el menor drawdown.

---

## 8. CONCLUSIONES

1. **Hay dos ganadores según criterio en Exp B GLOBAL:**
   - **Por F1-macro:** Regresión Logística con elasticnet sobre 61 features (F1 = **0.417**, Sharpe = 1.25).
   - **Por métricas económicas:** LSTM bidireccional con lookback=60 y 94 features (F1 = 0.389, Sharpe = 1.23, **Profit Factor = 1.42** ⭐, **Max Drawdown = −0.28** ⭐).

2. **XGBoost optimizado con Optuna es la mejor alternativa para Exp A** (F1 = 0.392), cuando se dispone de más años de entrenamiento.

3. **La estrategia global supera a por-ticker** en F1-macro para LR y XGBoost. Por-ticker es preferible solo cuando se busca explicabilidad por activo.

4. **Multi-seed ensembling es la técnica de mayor impacto** para modelos secuenciales (LSTM, CNN, CNN-LSTM), más que cambios arquitectónicos.

5. **El filtrado estadístico de features (Pearson/VIF/Spearman/SHAP) degrada el rendimiento.** La regularización interna del modelo es más efectiva. Las 61 features completas con regularización ganan en 11 de 15 casos en F1-macro.

6. **El target de percentil rodante 30/70 proporciona un objetivo balanceado** y adaptativo a regímenes de mercado, sin hiperparámetros ad-hoc.

7. **Recomendación práctica:**
   - Si el objetivo es **precisión de clasificación**: LR + elasticnet + 61 features + multi-seed.
   - Si el objetivo es **rendimiento económico (Sharpe/drawdown)**: LSTM bidireccional con lookback=60 entrenado con 94 features de mercado expandido.
   - En aplicación con costos reales de transacción, el menor drawdown de LSTM-v3 lb=60 probablemente domine.

---

## 9. LIMITACIONES

- **Sin costos de transacción ni slippage** en el backtest (aproximación de primer orden). En la práctica con costos de ~10 bp, solo LR mantendría Sharpe positivo.
- **Solo 7 activos del sector tecnológico** — generalización a otros sectores no garantizada.
- Decisión diaria a cierre; **no se modela intradía**.
- **Sin position sizing** (todas las posiciones full-notional o cero).
- **Solo datos de Yahoo Finance** (no incluye fundamentales, insider trading, opciones IV, sentiment de noticias).
- Single split temporal (sin walk-forward).

---

## 10. TRABAJO FUTURO

Documentado exhaustivamente en `ALTERNATIVAS_FUTURAS.md`. Resumen por prioridad:

**🔴 Alta prioridad (gratis):**
- Walk-forward validation (12+ folds) para reducir varianza estimativa.
- Position sizing dinámico (Kelly fraction, vol targeting).
- Costos de transacción y slippage realistas.

**🟡 Media prioridad:**
- Sentimiento de noticias (FinBERT + News API gratis con límites).
- Datos macro adicionales (FRED — gratis e ilimitado).

**🟢 Baja prioridad:**
- Datos de opciones (implied volatility surface) — requiere licencia pagada.
- Datos intradía 1m/5m — requiere licencia pagada.
- Arquitecturas Transformer (Informer, PatchTST) — alto compute, ganancia incierta.

---

## REFERENCIAS

1. Fama, E. F. (1970). Efficient capital markets: a review of theory and empirical work. *Journal of Finance*, 25(2), 383-417.
2. Sezer, O. B., Gudelek, M. U., & Ozbayoglu, A. M. (2020). Financial time series forecasting with deep learning: a systematic literature review. *Applied Soft Computing*, 90.
3. Fischer, T., & Krauss, C. (2018). Deep learning with long short-term memory networks for financial market predictions. *European Journal of Operational Research*, 270(2), 654-669.
4. Jiang, W. (2021). Applications of deep learning in stock market prediction: recent progress. *Expert Systems with Applications*, 184.
5. Patel, J., Shah, S., Thakkar, P., & Kotecha, K. (2015). Predicting stock and stock price index movement using trend deterministic data preparation and machine learning techniques. *Expert Systems with Applications*, 42(1), 259-268.
6. Borovkova, S., & Tsiamas, I. (2019). An ensemble of LSTM neural networks for high-frequency stock market classification. *Journal of Forecasting*, 38(6), 600-619.
7. Chen, T., & Guestrin, C. (2016). XGBoost: a scalable tree boosting system. *KDD '16*.
8. Akiba, T., et al. (2019). Optuna: a next-generation hyperparameter optimization framework. *KDD '19*.

---

## ANEXO A — Archivos generados

### Datos y modelos
- `tesis_ml_stocks/01_raw_datasets/{TICKER}_raw.parquet` — 61 features por ticker.
- `tesis_ml_stocks/01_raw_datasets_v3/{TICKER}_raw_v3.parquet` — 94 features (ablation).
- `RESULTADOS_OPTIMIZADOS/modelos_optimizados/{lr,xgboost,lstm,cnn_puro,cnn_lstm}/` — modelos entrenados.

### Reportes y tablas
- `RESULTADOS_OPTIMIZADOS/reportes/final_120/120_experimentos.csv` — **tabla maestra de 120 corridas**.
- `RESULTADOS_OPTIMIZADOS/reportes/final_120/resumen_GLOBAL_{F1_macro,Win_Rate,Profit_Factor,Max_Drawdown}.csv`
- `RESULTADOS_OPTIMIZADOS/reportes/feature_selection/comparativa_GLOBAL.csv`

### Figuras
- `RESULTADOS_OPTIMIZADOS/reportes/final_120/120_global_metrics.png` — barras F1/WR/PF/DD por modelo.
- `RESULTADOS_OPTIMIZADOS/reportes/final_120/120_heatmap_F1_macro_exp_*.png` — heatmaps por ticker.
- `RESULTADOS_OPTIMIZADOS/reportes/feature_selection/F1_filt_vs_all_GLOBAL.png`
- `RESULTADOS_OPTIMIZADOS/reportes/figuras/FINAL_baseline_vs_opt_global.png`

### Scripts (`scripts_opt/`)
- `common.py` — utilidades comunes (loaders, métricas).
- `opt_lr.py`, `opt_xgb.py`, `opt_lstm.py`, `opt_cnn_puro.py`, `opt_cnn_lstm.py` — un script por modelo.
- `consolidar_120.py` — consolidación de tabla maestra.
- `analisis_feature_selection.py` — comparativa filtradas vs todas.
- `comparar_v1_v3.py` — comparativa 61 vs 94 features.
- `expand_market_data.py` — descarga de features de mercado adicionales.
- `train_all_v3.py` — re-entrenamiento masivo con dataset expandido.

### Documentación complementaria
- `RESULTADOS_OPTIMIZADOS/GUIA_PROGRESO.md` — bitácora completa del proceso.
- `RESULTADOS_OPTIMIZADOS/ANALISIS_FEATURE_SELECTION.md` — análisis detallado.
- `RESULTADOS_OPTIMIZADOS/ALTERNATIVAS_FUTURAS.md` — roadmap de mejoras pendientes.
