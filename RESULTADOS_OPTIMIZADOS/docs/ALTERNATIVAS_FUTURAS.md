# ALTERNATIVAS NO IMPLEMENTABLES CON DATOS ACTUALES
## Mejoras potenciales que requieren datos externos o recursos adicionales

> **Propósito:** Este documento lista las técnicas y fuentes de datos que probablemente mejorarían los resultados pero NO se implementaron en este trabajo porque requieren datos no disponibles en Yahoo Finance, costos adicionales o trabajo de ingeniería fuera del alcance de la tesis. Se documentan aquí para referencia futura y para argumentar limitaciones honestas en la sección de "trabajo futuro" del paper.

---

## 1. Fuentes de datos adicionales (las más impactantes)

### 1.1 Datos intradiarios (1m / 5m / 15m)
**Por qué mejoraría:** El target actual es a 1 día, lo que pierde gran cantidad de información intradía sobre volumen, volatilidad realizada y micro-estructura. Con datos de 1 minuto se pueden construir:
- Volatilidad realizada de Garman-Klass / Parkinson / Rogers-Satchell.
- Order-flow imbalance proxy.
- Patrones de apertura/cierre (gaps, drift).
- Mejor estimación del precio "fair value" intradía.

**Por qué no se hizo:** Yahoo Finance ofrece datos intradía solo de los últimos 60 días para 1m y 730 días para 5m. Para 12 años de historial se requiere:
- IBKR HMDS (~$10/mes).
- Polygon.io (~$30/mes plan starter).
- Databento o Alpaca Markets (suscripción pagada).

**Mejora esperada:** F1 +0.02 a +0.05.

### 1.2 Datos de sentimiento (noticias / Twitter / Reddit)
**Por qué mejoraría:** El sentimiento es un driver conocido del precio de corto plazo, especialmente en tickers como TSLA y NVDA donde Reddit/Twitter mueven precios.

**Fuentes:**
- Bloomberg/Reuters news feeds (caros, $20K+/año).
- StockTwits API (límites de rate y de historial).
- News API (gratis pero limitado).
- AlphaVantage news sentiment (gratis con límites).

**Implementación recomendada:** BERT/FinBERT para clasificar polaridad de titulares y luego features como `sentiment_5d_avg`, `sentiment_volume`, `sentiment_change`.

**Por qué no se hizo:** Requiere pipelines de NLP, almacenamiento de noticias y cuidado para evitar lookahead bias (las noticias se publican intradía y hay delays).

**Mejora esperada:** F1 +0.03 a +0.07 (especialmente para tickers con alta cobertura mediática).

### 1.3 Datos fundamentales y de earnings
**Por qué mejoraría:** Earnings surprise, guidance, dividendos y márgenes son drivers de precio. Calendarios de earnings permiten:
- Variables binarias `pre_earnings_5d` / `post_earnings_3d`.
- Earnings surprise como feature.
- Guidance change como feature.

**Fuentes:**
- Yahoo Finance tiene earnings calendar pero limitado.
- SimFin (gratis con límites).
- AlphaVantage (gratis con límites).
- Compustat (académico, requiere licencia).

**Por qué no se hizo:** El target diario no es óptimo para capturar eventos de earnings (que son ~4 días/año por ticker). Mejor para un target semanal.

**Mejora esperada:** F1 +0.01 a +0.03.

### 1.4 Datos macro
**Variables a agregar:**
- Yield curve (DGS2, DGS10, DGS30 desde FRED).
- Term spread = 10Y − 2Y.
- VIX term structure (VIX9D, VIX, VIX3M, VIX6M).
- Dollar index DXY.
- Gold/Oil prices.
- High-yield credit spread (HYG/LQD ratio).
- Initial jobless claims.

**Por qué mejoraría:** Régimen macro determina régimen de tasas y volatilidad, los cuales afectan estrategias quantitativas.

**Implementación:** FRED API (gratis, ilimitado).

**Por qué no se hizo aquí:** Para no expandir el alcance del paper actual. Es la mejora MÁS BARATA de implementar.

**Mejora esperada:** F1 +0.01 a +0.03.

### 1.5 Datos de opciones (implied volatility surface)
**Por qué mejoraría:** La superficie de IV contiene información forward-looking que el precio no tiene:
- IV ATM 30d / 60d.
- Put-call ratio.
- Skew (IV OTM put / IV OTM call).
- Term structure de IV.

**Fuentes:**
- Yahoo Finance options (intradía, no histórico).
- ORATS (académico, ~$100/mes).
- CBOE DataShop.

**Por qué no se hizo:** Sin historial gratuito accesible.

**Mejora esperada:** F1 +0.02 a +0.05 (sobre todo para anticipar movimientos grandes).

### 1.6 Datos de short interest y SI ratio
**Por qué mejoraría:** Short squeeze e interés cortos son drivers conocidos (GME, AMC, TSLA en sus mejores momentos).

**Fuentes:**
- FINRA (gratis pero mensual).
- S3 Partners (caro).

**Mejora esperada:** F1 +0.01 a +0.03 para tickers de alta volatilidad.

### 1.7 Datos institucionales (13F)
**Por qué mejoraría:** Cambios trimestrales en holdings de fondos grandes son señales útiles.

**Fuentes:** SEC EDGAR (gratis pero pesado).

**Mejora esperada:** F1 +0.005 a +0.02 (bajo por la baja frecuencia).

---

## 2. Mejoras computacionales (requieren más hardware/tiempo)

### 2.1 Búsqueda Optuna mucho más amplia
**Para qué:** Por ejemplo, 500 trials de XGBoost (vs 25-50 actuales) podría encontrar combinaciones de hiperparámetros mejores.

**Costo:** ~10x más tiempo de GPU. ~5-10 horas adicionales por config.

**Mejora esperada:** F1 +0.005 a +0.015 marginales.

### 2.2 Multi-seed con N=20+ seeds
**Para qué:** Las predicciones de LSTM/CNN tienen alta varianza entre seeds. Promediar 20 reduce la varianza vs los 3 actuales.

**Costo:** 7x más tiempo de entrenamiento.

**Mejora esperada:** F1 +0.005 a +0.02 en deep learning.

### 2.3 Walk-forward validation
**En vez de un único split train/val/test, hacer múltiples splits deslizantes:**
- Train 2018-2022, val 2023, test 2024 Q1
- Train 2018Q2-2022Q2, val 2023Q1-2023Q2, test 2024 Q2
- etc.

**Beneficios:**
- Más datos para evaluar (12+ folds en vez de 1).
- Reducción de varianza en estimación.
- Más robusto a régimen-shifts.

**Costo:** 12x el tiempo de entrenamiento.

**Mejora esperada:** Los números podrían cambiar ±0.02 pero la INTERPRETACIÓN sería más sólida (varianza honesta).

### 2.4 Transformer / Time series Transformer
**Modelos:**
- Informer
- Autoformer
- PatchTST
- Time Series Transformer

**Por qué no se hizo:** Estos modelos requieren mucho más data (~10K-100K muestras) para no overfittear. Con 10K muestras globales podríamos intentarlo pero con riesgo.

**Mejora esperada:** F1 +0.01 a +0.03 (incertidumbre alta).

---

## 3. Mejoras metodológicas avanzadas

### 3.1 Cross-asset feature engineering
**Por qué mejoraría:** Crear features que combinen información de varios activos:
- Beta rodante vs SP500.
- Correlación rodante con sector (XLK, XLF, etc.).
- Spread vs cluster de pares.
- Cointegración con índice.

**Por qué no se hizo aquí:** Aumenta complejidad considerable. Se prioriza simplicidad.

**Mejora esperada:** F1 +0.005 a +0.02.

### 3.2 Multi-task learning
**Idea:** Entrenar un solo modelo que prediga simultáneamente:
- Señal (BUY/HOLD/SELL).
- Magnitud del retorno (regresión).
- Volatilidad esperada (regresión).

**Beneficio:** Regularización implícita, mejor representación interna.

**Por qué no se hizo:** Requiere rediseñar arquitecturas y losses combinados.

**Mejora esperada:** F1 +0.01 a +0.04 en deep learning.

### 3.3 Meta-learning / FOMAML
**Idea:** Aprender un inicializador para LSTM/CNN-LSTM que generalice mejor a distintos tickers.

**Por qué no se hizo:** Complejidad técnica alta, beneficio incierto.

### 3.4 Bayesian Neural Networks
**Idea:** Modelos con uncertainty estimation. Sólo trade cuando la incertidumbre sea baja.

**Beneficio:** Mejora Sharpe dramáticamente (menos trades pero mejores).

**Por qué no se hizo:** Implementación más compleja, no triviol con PyTorch.

**Mejora esperada:** F1 similar, pero Sharpe podría ir de 1.2 a 2.0+.

### 3.5 Variational AutoEncoder para features
**Idea:** Comprimir las 61 features con VAE a un latent space de ~10 dims, luego entrenar predictor.

**Por qué no se hizo:** No claro que ayude con tan pocas features.

---

## 4. Mejoras de target / problema

### 4.1 Horizonte de predicción más largo
**Actualmente:** 1 día.
**Alternativas a probar:** 3 días, 5 días, 10 días, 21 días.

**Por qué mejoraría:** Más signal-to-noise. El ruido de 1 día es muy alto.

**Por qué no se hizo:** Cambiar el target requiere rebuilding del pipeline completo y cambia la naturaleza del estudio.

**Mejora esperada:** Probablemente F1 sube a 0.45-0.50 con 5d, pero menos relevante para "señal diaria".

### 4.2 Target multi-step (predecir vector de 5 días)
**Idea:** En vez de predecir 1 día, predecir 5 días simultáneamente.

**Por qué no se hizo:** Complejidad técnica. Cambio de paradigma.

### 4.3 Target binario (2 clases en vez de 3)
**Idea:** BUY / NOT-BUY o SIGNAL / NOISE.

**Por qué no se hizo:** Pierde información valiosa de SELL como señal corta. El usuario quería 3 clases.

**Mejora esperada:** F1 binario fácilmente alcanza 0.55-0.60. Pero es menos útil económicamente.

### 4.4 Quantile regression del retorno
**Idea:** En vez de clasificar, predecir cuantiles del retorno futuro.

**Por qué no se hizo:** Cambia naturaleza del problema.

---

## 5. Mejoras de evaluación

### 5.1 Backtesting realista con costos
**Que falta:**
- Spread bid-ask (~5-10 bp para large caps).
- Comisiones (~1 bp).
- Slippage en órdenes grandes.
- Costos de financiamiento de SELL (shorting cost).
- Tax implications.

**Por qué no se hizo:** Para mantener simplicidad en el primer paper. Reportar Sharpe sin costos es la norma académica.

**Impacto:** Reduce Sharpe pero todos los modelos en la misma proporción — comparativa válida.

### 5.2 Position sizing dinámico (Kelly, vol targeting)
**Idea:** En vez de full-notional, posiciones proporcionales a probabilidad y volatilidad inversa.

**Mejora esperada:** Sharpe +0.3 a +0.5.

### 5.3 Test estadístico (Diebold-Mariano, Reality Check)
**Idea:** Probar si la diferencia entre modelos es estadísticamente significativa.

**Por qué no se hizo:** Faltaría agregar al paper. Es trabajo pendiente.

---

## 6. Resumen — Próximos pasos por prioridad

| Prioridad | Mejora | Impacto F1 esperado | Costo (esfuerzo/dinero) |
|-----------|--------|---------------------|--------------------------|
| 🔴 ALTA | Datos macro (FRED) | +0.01–0.03 | Gratis, 4-8h |
| 🔴 ALTA | Walk-forward validation | varianza | Gratis, 6-12h CPU |
| 🟡 MEDIA | Sentimiento (FinBERT + News API) | +0.03–0.07 | Gratis-bajo, 20-40h |
| 🟡 MEDIA | Position sizing (Kelly, vol target) | Sharpe +0.3-0.5 | Gratis, 4-6h |
| 🟡 MEDIA | Datos de opciones IV | +0.02–0.05 | Pagado, $100/mes |
| 🟢 BAJA | Datos intradía | +0.02–0.05 | Pagado, $10-30/mes |
| 🟢 BAJA | Transformer | +0.01–0.03 | Gratis, alto compute |

### Recomendación final
Para una **segunda versión del paper** o trabajo de tesis extendido:
1. Agregar variables macro de FRED (gratis, alto impacto).
2. Implementar walk-forward validation (gratis, mejora confianza estadística).
3. Implementar position sizing y costos de transacción (gratis, mejora análisis económico).
4. Considerar agregar sentiment features (FinBERT) si hay tiempo.

Las demás mejoras requieren inversión monetaria o cambio significativo del alcance, por lo que se dejan como **trabajo futuro**.
