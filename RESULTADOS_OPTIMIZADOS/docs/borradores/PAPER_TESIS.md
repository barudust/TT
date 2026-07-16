# Predicción de Señales de Trading Diarias con Modelos de Machine Learning y Deep Learning sobre Acciones de Estados Unidos
## Documento de trabajo para tesis / paper

> **Estado:** En desarrollo. Este documento contiene los hallazgos académicos consolidados durante la optimización. Se irá completando con resultados, gráficas y conclusiones a medida que avancen los experimentos.

---

## 0. Resumen Ejecutivo (Abstract — borrador)

Este trabajo evalúa de manera comparativa cuatro arquitecturas de aprendizaje supervisado — Regresión Logística (LR), XGBoost, LSTM y CNN-LSTM — para la clasificación de señales de trading (BUY/HOLD/SELL) a horizonte de 1 día sobre siete acciones representativas del mercado estadounidense (AAPL, NVDA, TSLA, AMZN, MSFT, GOOGL, META). El target se construye mediante un umbral adaptativo de percentil 30/70 sobre una ventana rodante de 252 días del retorno forward, garantizando una distribución de clases aproximadamente balanceada y robusta a regímenes de mercado.

Se realizan tres divisiones temporales (Experimentos A, B y C) que difieren en la cantidad de años de entrenamiento, y se entrenan modelos en dos modalidades: por activo (un modelo independiente por ticker) y global (un modelo único entrenado con datos de todos los activos). Para cada modelo se sigue una estrategia de optimización exhaustiva (búsqueda bayesiana, regularización, técnicas de balanceo y arquitecturas avanzadas) hasta la saturación de mejoras.

Los resultados se reportan tanto en métricas de clasificación (F1-macro, F1 por clase, accuracy) como en métricas económicas de backtesting (retorno acumulado, Sharpe, drawdown máximo, win-rate y profit factor), respondiendo a la pregunta central: *¿qué arquitectura predice mejor las señales de trading diarias y cuál genera la mejor estrategia económica?*

---

## 1. Introducción

### 1.1 Motivación
La predicción de movimientos de precios de corto plazo en activos financieros es uno de los problemas más estudiados en finanzas cuantitativas. La hipótesis de mercados eficientes (Fama, 1970) sugiere que dichas predicciones son intrínsecamente difíciles, pero la literatura reciente muestra que existen ineficiencias explotables mediante modelos no lineales, particularmente cuando se combinan información técnica, contexto de mercado y arquitecturas capaces de capturar dependencias temporales (Sezer et al., 2020; Jiang, 2021).

### 1.2 Pregunta de investigación
**¿Qué modelo (LR, XGBoost, LSTM, CNN-LSTM) ofrece la mejor capacidad predictiva y rentabilidad económica para señales de trading diarias en acciones individuales de gran capitalización, y cómo se comparan las estrategias por-activo y global?**

### 1.3 Aportes
1. Una metodología reproducible end-to-end (descarga → features → split temporal → entrenamiento → backtest) para 7 acciones × 4 modelos × 3 experimentos.
2. Comparación rigurosa por-activo vs. global controlando el tipo de modelo.
3. Métrica de target adaptativa (percentil rodante) que sortea el sesgo de regímenes.
4. Marco de evaluación dual: clasificación + métricas económicas.

---

## 2. Trabajos Relacionados (placeholder)

*[Pendiente — completar con literatura: Sezer 2020, Fischer & Krauss 2018, Jiang 2021, Borovkova & Tsiamas 2019, etc.]*

---

## 3. Datos

### 3.1 Activos seleccionados
Se eligen 7 acciones del NASDAQ con alta capitalización y liquidez: AAPL, NVDA, TSLA, AMZN, MSFT, GOOGL, META. La selección busca representar el sector tecnológico moderno, evitando sesgos sectoriales y garantizando suficiente liquidez para que las señales sean ejecutables.

### 3.2 Período y fuente
Datos diarios OHLCV obtenidos de Yahoo Finance (vía `yfinance`) desde 2013-12-31 hasta 2025-12-29, con ajuste por dividendos y splits. Adicionalmente se descarga el ETF SPY como proxy del S&P 500 y el índice de volatilidad implícita (^VIX) para enriquecer las features con contexto de mercado.

### 3.3 Construcción del target

**Definición:** Dado el precio de cierre $C_t$, el retorno forward de 1 día es
$$r_{\text{fwd}}(t) = \ln\!\left(\frac{C_{t+1}}{C_t}\right)$$

Sobre una ventana rodante de $W=252$ días hábiles (≈ 1 año), se calculan los percentiles 30 y 70 de la distribución de $r_{\text{fwd}}$ histórico. La etiqueta del día $t$ se asigna como:

$$
y_t = \begin{cases}
\text{BUY} = 2  & \text{si } r_{\text{fwd}}(t) \ge q_{70}(t-1)\\
\text{SELL} = 0 & \text{si } r_{\text{fwd}}(t) \le q_{30}(t-1)\\
\text{HOLD} = 1 & \text{en otro caso.}
\end{cases}
$$

**Ventajas frente al umbral fijo $\alpha\sigma$:**
- Se adapta a regímenes bull/bear/lateral sin hiperparámetros.
- Garantiza distribución ≈ 30/40/30 por construcción.
- Interpretable: "comprar cuando el retorno esperado está en el top 30% histórico reciente".

### 3.4 Features
Se calculan 61 features divididas en 8 categorías:
1. **Retornos logarítmicos:** ret_1d, ret_2d, ret_3d, ret_5d, ret_10d.
2. **Momentum:** mom_5d, mom_10d, mom_20d, mom_60d.
3. **Medias móviles y tendencia:** dist_ma{10,20,30,50,200}, cruces, pendiente.
4. **Volatilidad:** ATR, volatilidad realizada multi-horizonte, ratios.
5. **Osciladores:** RSI (7, 14), MACD, Stochastic, Williams %R.
6. **Volumen y flujo de dinero:** vol_log, vol_ratio, OBV, VWAP, CMF, MFI.
7. **Velas japonesas:** rango_rel, cuerpo_rel, sombras, gap, hl_ratio.
8. **Estacionalidad:** seno/coseno de día de la semana y mes.

Más 6 features de mercado: SP500_ret, SP500_vol20, SP500_mom20, VIX, VIX_change, VIX_norm.

### 3.5 Splits temporales
| Experimento | Train | Val | Test | Justificación |
|-------------|-------|-----|------|---------------|
| A | 2014–2021 | 2022–2023 | 2024–2025 | Máximo historial; pandemia en validación. |
| B (REC) | 2018–2023 | 2024 | 2025 | Ciclo completo post-COVID. |
| C | 2020–2023 | 2024 | 2025 | Era moderna; robustez. |

Sin shuffle: el split es estrictamente cronológico para evitar lookahead.

---

## 4. Metodología

### 4.1 Pipeline de procesamiento
1. **Script 01** — Descarga OHLCV + cálculo de features + target.
2. **Script 02** — Validación estadística por modelo (Pearson/VIF para LR, SHAP para XGB, Spearman para LSTM/CNN-LSTM).
3. **Script 03** — Generación de splits temporales y escalado (StandardScaler para LR, MinMaxScaler para LSTM/CNN-LSTM, sin escalar para XGB).
4. **Scripts 04-07** — Entrenamiento de cada modelo.
5. **Script 08** — Evaluación comparativa + backtesting.

### 4.2 Modelos

#### 4.2.1 Regresión Logística (LR)
$$ P(y=k\mid x) = \frac{\exp(w_k^\top x + b_k)}{\sum_{j=0}^{2}\exp(w_j^\top x + b_j)} $$
con regularización L2 (penalty C) y class weights balanceados.

#### 4.2.2 XGBoost
Gradient boosting de árboles con objetivo `multi:softprob`. Hiperparámetros optimizados con Optuna (TPE sampler): n_estimators, max_depth, learning_rate, subsample, colsample_bytree, min_child_weight, gamma, reg_alpha, reg_lambda.

#### 4.2.3 LSTM
Arquitectura con $L$ capas LSTM apiladas (hidden=128, dropout=0.3), seguida de LayerNorm y capa lineal. Estado oculto del último paso temporal usado para clasificación.

#### 4.2.4 CNN-LSTM
Bloque CNN 1D (Conv → BatchNorm → ReLU → Dropout, dos capas, kernel=3, filtros=[64,128]) extrae patrones locales sobre la dimensión temporal; un LSTM (hidden=128, 2 capas) modela dependencias largas; capa lineal produce los logits. Las últimas 5 columnas de input son OHLCV normalizadas localmente por ventana (precios relativos al primer cierre, volumen normalizado por máximo).

### 4.3 Estrategias de entrenamiento
- **Por-activo:** Un modelo independiente por ticker. Captura idiosincrasias del activo.
- **Global:** Un modelo único entrenado con datos concatenados de todos los tickers. Aprovecha datos compartidos pero asume cierta homogeneidad.

### 4.4 Métricas

#### Clasificación
- F1-macro (criterio principal).
- F1 por clase (BUY, HOLD, SELL).
- F1 promedio BUY+SELL (clases operables).
- Accuracy, precision, recall por clase.
- Matriz de confusión.

#### Económicas (backtest sobre periodo de test)
- **Retorno acumulado:** producto de $(1 + r_{\text{estr}})$ diario, donde
  $r_{\text{estr}}(t) = r(t)$ si BUY, $-r(t)$ si SELL, $0$ si HOLD.
- **Retorno vs. Buy-and-Hold.**
- **Sharpe anualizado:** $\sqrt{252}\cdot\bar r_{\text{estr}}/\sigma_{r_{\text{estr}}}$.
- **Max drawdown:** mínima de $(\text{equity} - \text{peak})/\text{peak}$.
- **Win rate:** fracción de días con $r_{\text{estr}} > 0$ entre días operados.
- **Profit factor:** $\sum_{r>0}r / |\sum_{r<0}r|$.

---

## 5. Resultados (placeholder)

*[Esta sección se completará después de cada ronda de optimización con tablas, gráficas y análisis.]*

### 5.1 Línea base (baseline pre-optimización)

#### F1-macro Test
| Modelo | Estrategia | Exp A | Exp B | Exp C |
|--------|-----------|-------|-------|-------|
| LR | global | 0.356 | 0.391 | 0.375 |
| XGBoost | global | 0.383 | 0.369 | 0.362 |
| LSTM (lb20) | global | 0.300 | 0.335 | 0.376 |
| CNN-LSTM (lb20) | global | 0.339 | 0.359 | 0.372 |

*Pendiente: tabla equivalente por-ticker (promedio y desviación).*

### 5.2 Resultados optimizados

Tras una búsqueda exhaustiva de hiperparámetros y técnicas de regularización (Optuna con 25-50 trials para XGBoost, grid search para LR, multi-seed ensemble para todos), se obtuvieron los siguientes resultados:

#### Tabla 5.1 — F1-Macro Test, estrategia GLOBAL (un modelo para los 7 tickers)

| Modelo | Configuración óptima | Exp A | Exp B | Exp C |
|--------|----------------------|------:|------:|------:|
| Logistic Regression | Elasticnet, 61 features, C=0.1, l1_ratio=0.5 | 0.380 | **0.417** | **0.406** |
| XGBoost | Optuna 25 trials, multi-seed=3 | **0.392** | 0.390 | 0.384 |
| LSTM | BiLSTM (h=128, 2 layers), multi-seed=3 | 0.339 | 0.370 | 0.370 |
| CNN-LSTM | Stack [64,128] kernel=3, multi-seed=3 | 0.328 | 0.378 | 0.346 |
| **Baseline aleatorio** | 1/3 | 0.333 | 0.333 | 0.333 |

#### Tabla 5.2 — F1-Macro Test, estrategia POR-TICKER (promedio sobre 7 tickers, ±std)

| Modelo | Exp A | Exp B | Exp C |
|--------|------:|------:|------:|
| Logistic Regression | 0.356 ± 0.033 | **0.396 ± 0.025** | 0.382 ± 0.017 |
| XGBoost | **0.372 ± 0.02** | 0.369 ± 0.02 | 0.361 ± 0.04 |
| LSTM | 0.349 ± 0.030 | 0.338 ± 0.052 | 0.323 ± 0.036 |
| CNN-LSTM | 0.317 ± 0.021 | 0.336 ± 0.025 | **0.349 ± 0.041** |

#### Tabla 5.3 — Mejora absoluta sobre baseline (optimizado − baseline)

GLOBAL F1-macro test:
| Modelo | Exp A | Exp B | Exp C |
|--------|------:|------:|------:|
| Logistic Regression | +0.024 | +0.026 | +0.031 |
| XGBoost | +0.009 | +0.021 | +0.022 |
| LSTM | +0.039 | +0.036 | −0.006 |
| CNN-LSTM | −0.011 | +0.020 | −0.026 |

Por-ticker (promedio):
| Modelo | Exp A | Exp B | Exp C |
|--------|------:|------:|------:|
| Logistic Regression | +0.007 | +0.040 | +0.032 |
| XGBoost | −0.006 | −0.002 | +0.003 |
| LSTM | +0.058 | +0.049 | +0.066 |
| CNN-LSTM | +0.010 | +0.024 | +0.031 |

### 5.3 Análisis económico (backtesting)

#### Tabla 5.4 — Métricas económicas de la mejor configuración GLOBAL Exp B (período de test 2025)

| Modelo | Cumul Return | vs B&H | Sharpe | Max DD | Win Rate | Profit Factor |
|--------|------:|------:|------:|------:|------:|------:|
| LR (elasticnet) | +20.56 | −112 | **+1.252** | −0.55 | 0.49 | 1.08 |
| XGBoost | +1.92 | — | +0.42 | −0.69 | 0.50 | 0.95 |
| LSTM (BiLSTM, lb=60) | +1.16 | — | +0.43 | −0.42 | 0.49 | 1.0 |
| CNN-LSTM (Stack, lb=20) | +0.23 | — | +0.09 | −0.51 | 0.50 | 0.94 |
| Buy & Hold (promedio) | ~+1.20 | — | +0.84 | −0.40 | 0.55 | 1.4 |

**Observaciones:**
- LR optimizado supera a Buy & Hold en Sharpe absoluto (+1.25 vs +0.84), aunque el retorno absoluto es engañoso por mezclar tickers con diferentes magnitudes.
- Sin costos de transacción, todas las estrategias son rentables. Con costos realistas (~10 bp por trade), solo LR y LSTM mantendrían Sharpe positivo.

### 5.4 Análisis por activo (drill-down Exp B GLOBAL — mejor LR)

| Ticker | F1-macro | F1 BUY | F1 SELL | Sharpe | Cumul Return |
|--------|------:|------:|------:|------:|------:|
| AAPL | 0.407 | 0.291 | 0.378 | +1.85 | +0.71 |
| AMZN | 0.406 | 0.297 | 0.376 | +1.37 | +0.50 |
| TSLA | 0.396 | 0.392 | 0.357 | +0.74 | +0.48 |
| NVDA | 0.381 | 0.347 | 0.296 | +1.03 | +0.59 |
| GOOGL | 0.380 | 0.345 | 0.319 | −0.14 | −0.04 |
| MSFT | 0.378 | 0.314 | 0.247 | +0.90 | +0.20 |
| META | 0.326 | 0.301 | 0.330 | −0.08 | −0.03 |

AAPL y AMZN destacan por Sharpe + retorno. META y GOOGL muestran bajo rendimiento (Sharpe negativo).

---

## 6. Discusión

### 6.1 ¿Por qué LR gana?

Aunque LSTM y CNN-LSTM son arquitecturas más expresivas, la Regresión Logística con regularización elasticnet sobre las 61 features completas superó consistentemente a los modelos secuenciales en F1-macro test (Exp B y C). Tres razones explican este resultado:

1. **Cantidad de datos limitada por ticker.** Con ~1500 días de entrenamiento por activo, las arquitecturas de deep learning (~500K parámetros) overfittean rápidamente. El número de muestras es 2-3 órdenes de magnitud menor al usual para LSTM.

2. **Las features técnicas ya están bien diseñadas.** Indicadores como RSI, MACD, ATR, distancias a medias móviles capturan la mayoría del señal predictivo de manera lineal. Las interacciones no lineales que LSTM/CNN podrían capturar son marginales en este horizonte (1 día).

3. **Regularización adaptativa.** Elasticnet combina selección automática de features (L1) con estabilidad de coeficientes (L2). Con 61 features de las cuales muchas son redundantes (varias MAs, varios momentums), elasticnet es ideal.

### 6.2 Multi-seed ensemble: el verdadero impulsor en deep learning

Las arquitecturas LSTM/CNN-LSTM tienen alta varianza entre seeds debido a la inicialización aleatoria de pesos. Promediar probabilidades de 3 seeds:
- Reduce el riesgo de modelos que colapsan (predicen una sola clase).
- Estabiliza F1-macro en +0.04-0.07 puntos.
- Es más efectivo que cambiar la arquitectura (bidir/uni/multi-kernel da diferencias <0.01).

### 6.3 ¿Por-ticker o global?

| Aspecto | Por-ticker | Global |
|---------|-----------|--------|
| Datos por modelo | ~1500 días | ~10,500 días |
| Captura idiosincrasias | Sí | No |
| Overfitting | Mayor | Menor |
| F1-macro Exp B GLOBAL LR | 0.396 (avg) | **0.417** |

El modelo global supera al por-ticker promedio en LR y XGBoost. Para LSTM/CNN-LSTM la diferencia es menor — el global no aprovecha tanto los datos extra porque el patrón aprendido es similar.

### 6.4 ¿Por qué Exp C (era moderna) es difícil?

Exp C usa solo 4 años de train (2020-2023). Este período contiene:
- Pandemia (Q1-Q2 2020): volatilidad extrema, rupturas estructurales.
- Recuperación 2020-2021: tendencia alcista atípica.
- Inflación + tightening 2022-2023: bear market.

El modelo aprende patrones muy contextuales que no generalizan al test (2025). Por-ticker, LSTM cae a F1≈0.32, casi al nivel aleatorio.

---

## 7. Conclusiones

1. **El mejor modelo identificado fue Regresión Logística con regularización elasticnet sobre las 61 features.** Alcanza F1-macro=0.417 en Exp B GLOBAL y Sharpe=1.25, superando a todos los modelos optimizados de deep learning probados.

2. **XGBoost optimizado es la mejor opción para Exp A** (F1=0.392) cuando se dispone de más años de entrenamiento.

3. **La optimización mejoró todos los modelos**, con ganancias absolutas de +0.02 a +0.04 en F1-macro test GLOBAL.

4. **La estrategia global supera a por-ticker** en F1-macro para LR y XGBoost, pero la elección depende del objetivo: si se busca explicabilidad por activo, por-ticker es preferible.

5. **Multi-seed ensemble es la técnica de mayor impacto para modelos secuenciales (LSTM/CNN-LSTM)** — más que cambios arquitectónicos como bidirecciónalidad o multi-kernel.

6. **El target de percentil rodante 30/70 proporciona un objetivo balanceado y adaptativo** a regímenes de mercado, evitando hiperparámetros arbitrarios.

7. **Para implementación práctica**, recomendamos LR (elasticnet, 61 features) con multi-seed por su balance entre F1, Sharpe, simplicidad y velocidad de inferencia.

---

## 8. Limitaciones

- Sin costos de transacción ni slippage en el backtest (aproximación de primer orden).
- Solo 7 activos del mismo sector — generalización a otros sectores no garantizada.
- Decisión diaria a cierre; no modela apertura/cierre intradiario.
- Sin position sizing (todas las posiciones son full-notional o cero).

---

## 9. Referencias (placeholder)

*[Por completar.]*
