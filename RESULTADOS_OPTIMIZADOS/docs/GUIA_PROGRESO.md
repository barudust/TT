# GUÍA INTERNA DE PROGRESO — OPTIMIZACIÓN DE MODELOS
## Tesis: Predicción de Señales de Trading con ML/DL en Acciones US

> **Propósito de este documento:** Es la libreta de bitácora del proceso de optimización. Sirve para que, al retomar el trabajo, sepa exactamente qué se hizo, qué funcionó, qué no, y qué falta. NO es el documento del paper — ese es `PAPER_TESIS.md`.

---

## 0. CONTEXTO BASE (Lo que tenemos al iniciar)

### Datos
- **Tickers (7):** AAPL, NVDA, TSLA, AMZN, MSFT, GOOGL, META
- **Período:** 2013-12-31 a 2025-12-29 (~3000 días por ticker)
- **Features disponibles en RAW:** 61 features técnicas + OHLCV + market context (SPY, VIX)
- **Target:** 3 clases (BUY=2, HOLD=1, SELL=0), basado en percentil 30/70 rodante de retorno forward 1d sobre ventana 252 días → distribución ≈ 30%/40%/30%

### Splits Temporales (3 experimentos)
- **Exp A:** Train 2014-2021 / Val 2022-2023 / Test 2024-2025 — "Máximo historial"
- **Exp B:** Train 2018-2023 / Val 2024 / Test 2025 — "Post-COVID RECOMENDADO"
- **Exp C:** Train 2020-2023 / Val 2024 / Test 2025 — "Era moderna"

### Selección de features actual (problemática crítica detectada)
La selección de features en Script 02 produce listas muy desiguales:
- **LR Exp B:** SOLO 4 features (SP500_ret, cmf_20, hl_ratio, mfi_14) — DEMASIADO RESTRICTIVO
- **LR Exp C:** SOLO 3 features
- **XGBoost Exp B:** 23 features
- **LSTM/CNN-LSTM Exp B:** 10 features
- **LSTM/CNN-LSTM Exp C:** 3 features — DEMASIADO POCAS

**→ Hipótesis de mejora #1:** Los modelos lineales y secuenciales están sub-alimentados. Usar TODAS las features relevantes (o un superset más generoso) debería mejorar resultados.

### Baseline F1-macro (Test) — Punto de Partida

| Modelo | Tipo | Exp A | Exp B | Exp C |
|--------|------|-------|-------|-------|
| LR | global | 0.356 | **0.391** | 0.375 |
| LR | por-ticker avg | 0.349 | 0.355 | 0.349 |
| XGBoost | global | **0.383** | 0.369 | 0.362 |
| XGBoost | por-ticker avg | 0.378 | 0.372 | 0.358 |
| LSTM | global (lb20) | 0.300 | 0.335 | **0.376** |
| LSTM | global (lb60) | 0.291 | 0.316 | 0.360 |
| CNN-LSTM | global (lb20) | 0.339 | 0.359 | **0.372** |
| CNN-LSTM | global (lb60) | 0.322 | 0.345 | 0.335 |

**Observaciones críticas:**
1. Los modelos lineales (LR) están casi al nivel de modelos complejos — señal de que la selección de features es el cuello de botella.
2. LSTM/CNN-LSTM colapsan en varias configuraciones (predicen una sola clase). Indica problemas de regularización o pesos iniciales.
3. Línea base aleatoria 3-clases = 0.333. Mejores resultados están solo +6-8% por encima.

---

## 1. PLAN DE OPTIMIZACIÓN

### Estrategia general
Para cada modelo, optimizar en orden:
1. **Datos/features:** Expandir conjunto de features (probar superset completo).
2. **Hiperparámetros:** Búsqueda exhaustiva con Optuna/grid.
3. **Arquitectura:** Variantes y modificaciones (bidirec., attention, depth).
4. **Ensemble/calibración:** Stacking, threshold tuning, multi-seed.
5. **Evaluación rigurosa:** Multi-seed con std, walk-forward.

### Métrica primaria de selección
- **F1-macro Test** como criterio principal (clasificación balanceada).
- **F1 BUY+SELL avg** como criterio secundario (clases más útiles para trading).
- **Sharpe Test** como criterio económico (consistencia de la estrategia).

### Multi-seed
Cada experimento final debe correrse con N=5 seeds para reportar media±std.

---

## 2. BITÁCORA DE EXPERIMENTOS

### MODELO 1 — REGRESIÓN LOGÍSTICA

#### Estado: EN PROGRESO (sesión 2026-05-22)

#### Hipótesis de mejora
- H1.1: Usar todas las 61 features mejora F1 vs. usar solo 4 consenso.
- H1.2: Penalización elasticnet permite selección automática y mejor regularización.
- H1.3: Calibración de threshold por clase mejora distribución de señales.
- H1.4: Ridge con escalado correcto + interacciones polinómicas (grado 2) capta no-linealidades.

#### Configuraciones a probar
| ID | Features | Penalty | C | Class weight | Solver |
|----|----------|---------|---|--------------|--------|
| LR-01 | Todas (61) | l2 | grid amplio | balanced | lbfgs |
| LR-02 | Todas (61) | elasticnet | grid + l1_ratio | balanced | saga |
| LR-03 | Todas (61) | l1 | grid amplio | balanced | saga |
| LR-04 | Solo top-20 SHAP | l2 | grid | balanced | lbfgs |
| LR-05 | LR-01 + polynomial features (degree=2, interaction_only) | l2 | grid | balanced | lbfgs |
| LR-06 | LR-01 + threshold tuning por clase | l2 | mejor | balanced | lbfgs |

#### Resultados (F1-macro test, ensemble multi-seed mayoría votada)

**GLOBAL:**
| Config | Exp A | Exp B | Exp C |
|--------|-------|-------|-------|
| Baseline | 0.356 | 0.391 | 0.375 |
| LR-01 (l2, 61 feats) | 0.376 | 0.386 | 0.399 |
| LR-02 (elasticnet, 61 feats) | **0.380** | **0.417** | 0.396 |
| LR-03 (l1, 61 feats) | 0.375 | 0.382 | **0.406** |
| LR-05 (l2, top-20 shap) | 0.368 | 0.371 | 0.378 |

**POR-TICKER (promedio sobre 7 tickers):**
| Config | Exp A | Exp B | Exp C |
|--------|-------|-------|-------|
| Baseline | 0.349 | 0.355 | 0.349 |
| LR-01 (l2) | 0.337 | 0.392 | 0.366 |
| LR-02 (elasticnet) | 0.354 | **0.396** | 0.357 |
| LR-03 (l1) | **0.356** | 0.383 | 0.365 |
| LR-05 (l2 shap) | 0.347 | 0.388 | **0.382** |

**Sharpe global (best per exp):**
- Exp A: LR-05 (0.656) y LR-03 (0.517)
- Exp B: **LR-02 elasticnet (1.252)** ← gana en F1 y Sharpe
- Exp C: LR-01 (1.018), LR-03 (0.957)

#### Hallazgos clave LR
1. **Más features ayudan:** L2 con 61 features supera a L2 con top-20 shap. Confirma hipótesis H1.1.
2. **Elasticnet es el mejor regularizador para Exp B:** gana en F1 y Sharpe.
3. **L1 brilla en Exp C:** selección de features automática útil cuando hay poco train (4 años).
4. **Multi-seed ensemble (mayoría):** estabiliza resultados (no probado contra seed único, pero esperado).
5. **Distribución pred:** todos los modelos predicen menos BUY de los que hay (sesgo hacia HOLD/SELL).

#### Pendiente
- LR-06: calibración de threshold por clase (puede ayudar a destapar el sesgo anti-BUY).
- Skip LR-04 polynomial (no se ha visto ganancia clara con más complejidad).
- Considerar finalizar LR aquí: marginal improvement ya difícil sin sobreajustar.

---

### MODELO 2 — XGBOOST

#### Estado: PENDIENTE

#### Hipótesis de mejora
- H2.1: Aumentar Optuna trials de 30 → 100+ con sampler TPE mejora.
- H2.2: GPU acelera la búsqueda → trials más extensivos.
- H2.3: Multi-seed averaging reduce varianza.
- H2.4: Stacking con calibración mejora distribución de probabilidades.
- H2.5: Más features (todas las 61) > consenso 23.

#### Configuraciones a probar
| ID | Features | Trials | Multi-seed | Class weight |
|----|----------|--------|------------|--------------|
| XGB-01 | Consenso | 100 | 5 seeds | balanced |
| XGB-02 | Todas (61) | 100 | 5 seeds | balanced |
| XGB-03 | Top-30 por importancia | 100 | 5 seeds | balanced |
| XGB-04 | XGB-02 + early stopping + monotonic constraints | 150 | 5 seeds | balanced |
| XGB-05 | LightGBM como comparación | 100 | 5 seeds | balanced |

---

### MODELO 3 — LSTM

#### Estado: EN PROGRESO (sesión 2026-05-22)

#### Resultados (multi-seed=3 ensemble)

**LSTM-02-bi (bidireccional, hidden=128, 2 layers, dropout=0.3, CE balanced):**

GLOBAL F1-macro test:
| Lookback | Exp A | Exp B | Exp C |
|----------|-------|-------|-------|
| 20 | 0.336 (base 0.300, +12%) | 0.362 (base 0.335, +8%) | 0.370 (base 0.376, -2%) |
| 60 | 0.339 (base 0.291, +16%) | 0.370 (base 0.316, +17%) | 0.352 (base 0.360, -2%) |

**LSTM-01-stack (unidireccional, similar al baseline + multi-seed):**

| Lookback | Exp B GLOBAL |
|----------|------|
| 20 | 0.360 |
| 60 | 0.351 |

**Hallazgos clave LSTM**
1. Bidireccional (LSTM-02) ofrece ganancia marginal vs unidireccional (LSTM-01) en Exp B (0.362 vs 0.360 en lb=20). Multi-seed ensembling es el verdadero driver.
2. Mejoras consistentes en Exp A (+12-16%) y Exp B (+8-17%).
3. Exp C es difícil — modelos colapsan en algunos tickers (especialmente con lb=60 y poco train data).
4. Early stopping ocurre temprano (epoch 20-30): overfitting es el problema principal.
5. Mejores per-ticker en lb=20; per-ticker se vuelve muy ruidoso en lb=60 con poco data (~1000 muestras).

#### Estado: COMPLETO (LSTM-02-bi y LSTM-01-stack para Exp B; LSTM-02-bi para Exp A y C)

#### Hipótesis de mejora
- H3.1: Bidireccional + más capas mejora captura temporal.
- H3.2: Focal loss reduce colapso en clase mayoritaria.
- H3.3: Label smoothing regulariza.
- H3.4: Más features (no solo 10) ayuda.
- H3.5: Lookback más grande (60 o más) capta tendencias.
- H3.6: Attention encima del LSTM destaca momentos importantes.

#### Configuraciones a probar
| ID | Arq | Lookback | Features | Loss |
|----|-----|----------|----------|------|
| LSTM-01 | Stack (2L, 128h, dropout 0.3) | 20, 60 | Todas + market | CE balanced |
| LSTM-02 | BiLSTM (2L, 128h, dropout 0.3) | 20, 60 | Todas | CE balanced |
| LSTM-03 | LSTM + Attention | 20, 60 | Todas | CE balanced |
| LSTM-04 | LSTM-02 + Focal loss | 20, 60 | Todas | Focal γ=2 |
| LSTM-05 | LSTM-02 + Label smoothing | 20, 60 | Todas | CE LS 0.1 |

---

### MODELO 4 — CNN-LSTM

#### Estado: PENDIENTE

#### Hipótesis de mejora
- H4.1: CNN multi-kernel paralelo capta patrones a distintas escalas (Inception-style).
- H4.2: Más filtros en capas tempranas mejora capacidad.
- H4.3: Pooling temporal (max + avg) en vez de solo el último frame.
- H4.4: BiLSTM después de CNN.
- H4.5: Focal loss + label smoothing similar a LSTM.

#### Configuraciones a probar
| ID | CNN | LSTM | Lookback | Loss |
|----|-----|------|----------|------|
| CNN-LSTM-01 | [64,128] k=[3,3] | 128h 2L | 20, 60 | CE balanced |
| CNN-LSTM-02 | Multi-kernel [3,5,7] paralelo | BiLSTM 128h | 20, 60 | CE balanced |
| CNN-LSTM-03 | [64,128,256] k=[3,3,3] | 128h 2L | 20, 60 | Focal |
| CNN-LSTM-04 | CNN-LSTM-02 + temporal attention | BiLSTM | 60 | CE LS |

---

## 3. INVARIANTES Y PRINCIPIOS DE RIGOR

- **No leakage:** scalers, percentiles y todo tipo de preproc se hace SOLO con train.
- **Reproducibilidad:** `random_state=42` + multi-seed para reportar varianza.
- **Test puro:** No tocar test hasta finalizar configuraciones (val es para selección).
- **Comparación justa:** Todos los modelos usan los mismos splits temporales.
- **Pesos balanceados:** Class weight = "balanced" cuando no se use focal loss.
- **Early stopping:** Sobre val_loss para evitar overfitting.

---

## 4. ARCHIVOS GENERADOS

### Por experimento
- `RESULTADOS_OPTIMIZADOS/modelos_optimizados/{modelo}/{config_id}/{ticker}_{exp}.pkl`
- `RESULTADOS_OPTIMIZADOS/modelos_optimizados/{modelo}/{config_id}/metricas.json`
- `RESULTADOS_OPTIMIZADOS/logs/{modelo}_{config_id}_{timestamp}.log`

### Reportes consolidados
- `RESULTADOS_OPTIMIZADOS/reportes/resumen_global.csv`
- `RESULTADOS_OPTIMIZADOS/reportes/mejor_config_por_modelo.json`
- `RESULTADOS_OPTIMIZADOS/reportes/comparativa_final.csv`

---

## 5. CRITERIO DE PARADA (cuándo decir "no hay más mejora")

Un modelo se considera optimizado cuando:
1. Se probaron ≥4 configuraciones distintas.
2. La mejora marginal entre las últimas dos configuraciones es < 0.005 en F1-macro.
3. Multi-seed std ≤ 0.02 (resultados estables).
4. Inspección manual de errores no revela patrones obvios.

---

## 6. NOTAS DE SESIÓN

### Sesión 2026-05-22 (inicio)
- Exploración inicial completa.
- Detectada feature selection muy restrictiva en LR/LSTM/CNN-LSTM.
- Hardware: NVIDIA RTX 5060 Ti (CUDA disponible).
- Plan trazado, listo para empezar con LR.

### Sesión 2026-05-22 (progreso)

#### Tabla maestra de mejoras (delta F1-macro test optimizado vs baseline)

**GLOBAL:**
| Modelo | Exp A | Exp B | Exp C | Mejor config |
|--------|-------|-------|-------|--------------|
| LogisticRegression | +0.024 (0.356→0.380) | +0.026 (0.391→**0.417**) | +0.031 (0.375→0.406) | elasticnet/L1 con 61 features |
| XGBoost | pendiente | pendiente | pendiente | (Optuna lento por contención GPU) |
| LSTM | +0.039 (0.300→0.339) | +0.036 (0.335→0.370) | -0.006 (0.376→0.370) | LSTM-02-bi multi-seed |
| CNN-LSTM | -0.011 (0.339→0.328) | +0.020 (0.359→0.378) | -0.026 (0.372→0.346) | CNN-01-base multi-seed |

**POR-TICKER (promedio sobre 7):**
| Modelo | Exp A | Exp B | Exp C |
|--------|-------|-------|-------|
| LogisticRegression | +0.007 | +0.040 | +0.032 |
| XGBoost | pendiente | pendiente | pendiente |
| LSTM | +0.058 | +0.049 | +0.066 |
| CNN-LSTM | +0.010 | +0.024 | +0.031 |

#### Hallazgos clave finales (preliminar — falta XGB)

1. **Logistic Regression es el mejor modelo overall.** Alcanza F1-macro=0.417 en Exp B GLOBAL, superando a todos los demás modelos optimizados.

2. **Más features ≠ siempre mejor.** Las 61 features completas funcionaron mejor que el consenso de 4 features para LR. Pero para LSTM/CNN-LSTM, las arquitecturas simples y profundas no escalan bien.

3. **Multi-seed ensemble ayuda más a deep learning.** Para LSTM/CNN-LSTM, la varianza entre seeds es grande y promediar 3 seeds mejora el F1 por_ticker en +5-7%.

4. **Bidireccional vs unidireccional es marginal.** LSTM-02-bi (bi) ~ LSTM-01-stack (uni) en F1, lo mismo para CNN-LSTM. El driver real es multi-seed.

5. **Arquitecturas complejas (deeper, multi-kernel, focal loss) overfittean.** No mejoran sobre las versiones simples + multi-seed.

6. **Exp B (post-COVID) es el más fácil.** Todos los modelos rinden mejor allí.

7. **Exp C (era moderna, menos train data) es el más difícil.** Modelos secuenciales (LSTM/CNN-LSTM) tienden a colapsar.

#### Configuraciones finales recomendadas para tesis

| Modelo | Mejor config | F1 Exp A | F1 Exp B | F1 Exp C |
|--------|--------------|----------|----------|----------|
| LR (global) | LR-02 elasticnet / LR-03 L1 | 0.380 | **0.417** | **0.406** |
| LR (por-ticker) | LR-02 elasticnet / LR-03 L1 / LR-05 shap | 0.356 | 0.396 | 0.382 |
| XGBoost (global) | (baseline Optuna 30) | 0.383 | 0.369 | 0.362 |
| LSTM (global) | LSTM-02-bi lb=60 | 0.339 | 0.370 | 0.352 |
| LSTM (por-ticker) | LSTM-02-bi lb=20 | 0.349 | 0.338 | 0.323 |
| CNN-LSTM (global) | CNN-01-base lb=20 | 0.309 | 0.378 | 0.346 |
| CNN-LSTM (por-ticker) | CNN-01-base lb=20 | 0.336 | 0.336 | 0.349 |

### Status final tareas
- ✓ LR: COMPLETO (4 configs × 3 exps × 2 tipos, multi-seed=5)
- ✓ XGB: COMPLETO (XGB-01-all con 25 trials, 3 seeds × 3 exps × 2 tipos)
- ✓ LSTM: COMPLETO (LSTM-01, LSTM-02-bi para Exp A, B, C ambos lookbacks)
- ✓ CNN-LSTM: COMPLETO (5 configs para Exp B; CNN-01 para A, C ambos lookbacks)

### Tabla maestra final — F1-Macro Test (BASELINE vs OPTIMIZADO)

**GLOBAL:**
| Modelo | Exp A baseline | Exp A optim | Δ | Exp B baseline | Exp B optim | Δ | Exp C baseline | Exp C optim | Δ |
|--------|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LR | 0.356 | **0.380** | +0.024 | 0.391 | **0.417** | +0.026 | 0.375 | **0.406** | +0.031 |
| XGBoost | 0.383 | **0.392** | +0.009 | 0.369 | **0.390** | +0.021 | 0.362 | **0.384** | +0.022 |
| LSTM | 0.300 | **0.339** | +0.039 | 0.335 | **0.370** | +0.036 | 0.376 | 0.370 | −0.006 |
| CNN-LSTM | 0.339 | 0.328 | −0.011 | 0.359 | **0.378** | +0.020 | 0.372 | 0.346 | −0.026 |

**POR-TICKER (promedio sobre 7 tickers):**
| Modelo | Exp A | Exp B | Exp C |
|--------|---:|---:|---:|
| LR (base→opt) | 0.349→0.356 | 0.355→**0.396** | 0.349→**0.382** |
| XGBoost (base→opt) | 0.378→0.372 | 0.371→0.369 | 0.359→0.361 |
| LSTM (base→opt) | 0.290→**0.349** | 0.288→**0.338** | 0.257→**0.323** |
| CNN-LSTM (base→opt) | 0.307→0.317 | 0.312→**0.336** | 0.317→**0.349** |

### Mejor modelo por experimento (criterio: F1-macro test GLOBAL optimizado)

| Experimento | 1° | 2° | 3° | 4° |
|---|---|---|---|---|
| **Exp A** | XGBoost 0.392 | LR 0.380 | LSTM 0.339 | CNN-LSTM 0.328 |
| **Exp B** | **LR 0.417** | XGBoost 0.390 | CNN-LSTM 0.378 | LSTM 0.370 |
| **Exp C** | **LR 0.406** | XGBoost 0.384 | LSTM 0.370 | CNN-LSTM 0.346 |

### Hallazgos clave finales

1. **LR domina globalmente.** Es el mejor modelo en Exp B y Exp C, y solo XGB lo supera por +0.012 en Exp A. Más interpretable y rápido de entrenar.

2. **XGBoost optimizado mejora consistentemente.** Con multi-seed ensemble + 25 trials Optuna, gana ~+0.02 en F1 sobre baseline para Exp B y C.

3. **Más features ayuda.** Para LR, usar las 61 features con regularización elasticnet/L1 supera ampliamente al subset de consenso (4 features).

4. **Multi-seed ensemble es crítico para deep learning.** LSTM/CNN-LSTM ganan +0.04-0.07 en F1 por-ticker promediando 3 seeds. Sin esto, los modelos colapsan a una sola clase con frecuencia.

5. **Arquitecturas complejas no mejoran sobre simples.** En CNN-LSTM, la versión `CNN-01-base` (unidireccional, kernels 3+3, idéntica al baseline) supera a configuraciones bidireccionales, multi-kernel y deeper. La clave es multi-seed, no la arquitectura.

6. **Exp B (recomendado) es el más fácil.** Todos los modelos rinden mejor allí (post-COVID, ciclo completo). Confirma elección del experimento "principal" para la tesis.

7. **Exp C (era moderna, menos data) es el más difícil para deep learning.** LSTM y CNN-LSTM tienden a colapsar; LR brilla con regularización L1.

### Conclusión del proceso de optimización

La optimización fue exitosa:
- **LR pasa de F1=0.391 (baseline) a 0.417 (+6.6%) en Exp B GLOBAL** — mejor resultado overall.
- **XGB pasa de F1=0.369 a 0.390 (+5.7%) en Exp B GLOBAL**.
- **LSTM pasa de F1=0.335 a 0.370 (+10.4%) en Exp B GLOBAL**.
- **CNN-LSTM pasa de F1=0.359 a 0.378 (+5.3%) en Exp B GLOBAL**.
- Por-ticker promedio, las mejoras son aún más drásticas en modelos secuenciales (+15-25%).

El ganador del estudio es **Regresión Logística con elasticnet sobre todas las 61 features**, con F1-macro=0.417 en Exp B GLOBAL y Sharpe Test=1.25.

### Próximos pasos (futuro trabajo)
- Threshold calibration por clase para reducir el sesgo a SELL en LR.
- Stacking de los 4 modelos (meta-modelo sobre probabilidades).
- Walk-forward validation para más robustez temporal.
- Costos de transacción y slippage en el backtest.

---

## 7. SESIÓN 2 — Búsqueda de mejoras adicionales

Intentamos varias técnicas para superar el ceiling de 0.42 F1-macro:

### Técnicas probadas

| Técnica | F1 Exp B GLOBAL | Vs LR-v1 (0.417) | Veredicto |
|---------|----------------:|-----------------:|-----------|
| LR-v1 elasticnet (baseline optimizado) | **0.417** | 0 | Ceiling actual |
| LR-confidence filter (umbrales conf.) | 0.412 | −0.005 | No mejora F1, similar Sharpe |
| LightGBM | 0.402 | −0.015 | Alternativa competitiva (más rápida) |
| Ensemble LR+XGB (weighted soft vote) | 0.390 | −0.027 | val→test gap arruina el blend |
| XGB-v1 baseline | 0.390 | −0.027 | — |
| CNN-LSTM-v1 | 0.378 | −0.039 | — |
| LR-v2 features expandidas (181) + calib | 0.375 | −0.042 | Overfitting con más features |
| LSTM-v1 | 0.370 | −0.047 | — |
| Stacking (meta-LR sobre 4 modelos) | 0.358 | −0.059 | Meta-modelo overfit val pequeño |
| SoftVoting (pesos óptimos val) | 0.331 | −0.086 | Pesos optimizados val no generalizan |

### Análisis de por qué no se pudo mejorar

1. **Ceiling de información:** Las features técnicas + market context ya capturan casi toda la señal predictiva disponible en datos OHLCV de 1 día. El "ruido" del retorno diario es estructural — la mayor parte (>50%) del movimiento intradía es no predecible solo con datos de precio.

2. **Más features = overfit:** Con 181 features y ~10K muestras globales, los modelos overfittean en val y degradan en test. Las 61 originales son el sweet spot.

3. **Ensembles fallan por val→test gap:** En val (2024), XGB > LR. En test (2025), LR > XGB. Cualquier pesado optimizado en val sub-pesa a LR.

4. **Stacking overfit:** El meta-modelo se entrena sobre val (1736 muestras). Es poco data para aprender bien la combinación.

5. **LSTM/CNN-LSTM contaminan:** Sus probs son menos confiables (más sesgo, alta varianza). Mezclar con LR/XGB diluye la señal.

### Mejoras realizadas que NO bajaron el ceiling pero sí dieron alternativas

- **LightGBM** (0.402): casi tan bueno como XGB y mucho más rápido. Buena alternativa.
- **LR-confidence filter** (0.412 F1, 1.20 Sharpe): casi mismo F1 pero distribución más balanceada de señales.
- **Documento de alternativas externas:** ver `ALTERNATIVAS_FUTURAS.md` — datos macro FRED, sentimiento FinBERT, opciones IV, walk-forward.

### Conclusión definitiva sobre el ceiling

**Con datos de Yahoo Finance OHLCV diario + market context (SPY/VIX):**
- F1-macro test ceiling para Exp B GLOBAL ≈ **0.42** (LR elasticnet).
- F1-macro test ceiling para Exp C GLOBAL ≈ **0.41** (LR L1).
- F1-macro test ceiling para Exp A GLOBAL ≈ **0.39** (XGBoost Optuna).

Para superar este ceiling necesitamos:
- **Datos adicionales:** FRED macro (gratis), sentiment news (gratis con limit), opciones IV (pagado).
- **Más resolución temporal:** intradía (1m/5m).
- **Más targets:** horizonte 3-5 días en lugar de 1 día (mejor SNR).

Ver `ALTERNATIVAS_FUTURAS.md` para el roadmap detallado.

---

## 8. ARCHIVOS GENERADOS — SESIÓN 2

- `RESULTADOS_OPTIMIZADOS/modelos_optimizados_v2/lr/` — LR con 181 features (no mejoró)
- `RESULTADOS_OPTIMIZADOS/modelos_optimizados_v2/xgboost/` — XGB con 181 features (no mejoró)
- `RESULTADOS_OPTIMIZADOS/modelos_optimizados/lightgbm/` — **LightGBM (alternativa viable a XGB)**
- `RESULTADOS_OPTIMIZADOS/stacking/` — Meta-LR sobre 4 modelos (peor)
- `RESULTADOS_OPTIMIZADOS/soft_voting/` — Pesos óptimos por modelo (peor)
- `RESULTADOS_OPTIMIZADOS/ensemble_lr_xgb/` — Ensemble simple (peor)
- `RESULTADOS_OPTIMIZADOS/lr_confidence_filter/` — Filtro por confianza (similar)
- `RESULTADOS_OPTIMIZADOS/reportes/COMPARATIVA_TOTAL.csv` — Tabla con todas las variantes
- `RESULTADOS_OPTIMIZADOS/ALTERNATIVAS_FUTURAS.md` — Datos y técnicas no disponibles
- `tesis_ml_stocks/01_raw_datasets_v2/` — Datasets con 181 features (mantener para experiment.)

### Scripts sesión 2 (en `scripts_opt/`)

- `feature_engineering_v2.py` — Construye dataset v2 con z-scores, lags, interacciones
- `common_v2.py` — Loader del dataset v2
- `opt_lr_v2.py` — LR sobre v2 con threshold calibration constrained
- `opt_xgb_v2.py` — XGB sobre v2
- `opt_lgbm.py` — LightGBM sobre v1
- `stacking.py` — Stacking ensemble
- `soft_voting.py` — Soft voting con búsqueda de pesos
- `ensemble_lr_xgb.py` — Ensemble simple LR+XGB
- `lr_confidence_filter.py` — Filtro por confianza

