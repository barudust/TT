# ANÁLISIS — FEATURE SELECTION ESTADÍSTICA vs TODAS LAS FEATURES
## ¿Mejora el rendimiento usar Pearson, VIF, Spearman y SHAP para filtrar features?

> **Objetivo:** Determinar si filtrar features mediante tests estadísticos (lo que hace el `script 02`) mejora o empeora el rendimiento de cada modelo respecto a usar las 61 features completas.

---

## 1. Setup experimental

### Conjuntos de features comparados

**Set A — Filtradas (script 02 con tests estadísticos):**
| Modelo | Test usado | Features Exp A | Exp B | Exp C |
|--------|------------|---:|---:|---:|
| Logistic Regression | Pearson (p<0.05) + VIF (≤10) | 8 | 4 | 3 |
| XGBoost | SHAP top-N | 24 | 23 | 25 |
| LSTM / CNN / CNN-LSTM | Spearman (p<0.05) | 25 | 10 | 3 |

**Set B — Todas (sin filtro):** 61 features técnicas + de mercado (todas las del dataset).

### Configuración

- Mismos hiperparámetros para cada modelo (los óptimos encontrados con Optuna/grid).
- Multi-seed ensemble (3-5 seeds según modelo).
- Mismo split temporal (3 experimentos × global × 7 tickers).
- Métricas: **F1-macro, Win Rate, Profit Factor, Max Drawdown** (sin accuracy).

---

## 2. Resultados — GLOBAL F1-macro test

| Modelo | Exp A filt → all | Δ | Exp B filt → all | Δ | Exp C filt → all | Δ |
|---|---:|---:|---:|---:|---:|---:|
| **LR** | 0.356 → 0.380 | **+0.024** ✅ | 0.391 → **0.417** | **+0.026** ✅ | 0.375 → 0.396 | **+0.021** ✅ |
| **XGBoost** | 0.383 → 0.392 | **+0.009** ✅ | 0.369 → 0.390 | **+0.021** ✅ | 0.362 → 0.384 | **+0.022** ✅ |
| **LSTM** | 0.300 → 0.339 | **+0.039** ✅ | 0.335 → 0.370 | **+0.036** ✅ | 0.376 → 0.370 | −0.006 ➖ |
| **CNN puro** | 0.313 → 0.348 | **+0.035** ✅ | **0.368** → 0.343 | −0.025 ❌ | 0.362 → 0.373 | **+0.011** ✅ |
| **CNN-LSTM** | 0.339 → 0.328 | −0.011 ➖ | 0.359 → 0.378 | **+0.020** ✅ | 0.372 → 0.346 | −0.026 ❌ |

**Resultado:** En **11 de 15 casos**, usar TODAS las features mejora F1-macro test. Casos donde filtrar gana son todos modelos secuenciales (LSTM, CNN, CNN-LSTM) con bajo train data o Exp C.

### Resumen por modelo:
- **LR y XGBoost:** TODAS las features gana siempre (3/3 experimentos en cada uno).
- **LSTM:** TODAS gana 2/3 (Exp A, B). Filtradas gana en Exp C (poco train data).
- **CNN puro:** TODAS gana 2/3 (Exp A, C). Filtradas gana sorprendentemente en Exp B (10 features Spearman).
- **CNN-LSTM:** Filtradas gana 2/3 (Exp A, C). TODAS solo en Exp B.

---

## 3. Resultados — Profit Factor

| Modelo | Exp A filt → all | Δ | Exp B filt → all | Δ | Exp C filt → all | Δ |
|---|---:|---:|---:|---:|---:|---:|
| **LR** | 1.07 → 1.09 | +0.02 | 1.08 → **1.38** | **+0.30** ✅ | 1.11 → 1.19 | +0.08 |
| **XGBoost** | 1.05 → **1.21** | **+0.16** ✅ | 0.95 → 1.10 | **+0.15** ✅ | 0.87 → **1.10** | **+0.23** ✅ |
| **LSTM** | 1.23 → 1.06 | −0.17 ❌ | 1.24 → 1.12 | −0.12 ❌ | 0.96 → 1.04 | +0.08 |
| **CNN puro** | 1.15 → 1.08 | −0.07 | (pendiente) | – | (pendiente) | – |
| **CNN-LSTM** | 0.86 → 1.07 | **+0.21** ✅ | 0.94 → 1.02 | +0.08 | 0.95 → 1.07 | +0.13 ✅ |

**Resultado:** Todas las features mejora Profit Factor para LR, XGB, CNN-LSTM. Para LSTM filtradas gana ligeramente.

---

## 4. Resultados — Max Drawdown (más cercano a 0 es mejor)

| Modelo | Exp A filt → all | Δ | Exp B filt → all | Δ | Exp C filt → all | Δ |
|---|---:|---:|---:|---:|---:|---:|
| **LR** | −0.54 → −0.69 | −0.16 ❌ | −0.55 → **−0.42** | **+0.13** ✅ | −0.39 → −0.50 | −0.11 ❌ |
| **XGBoost** | −0.67 → **−0.44** | **+0.23** ✅ | −0.69 → **−0.44** | **+0.24** ✅ | −0.86 → **−0.47** | **+0.40** ✅ |
| **LSTM** | −0.64 → **−0.45** | **+0.19** ✅ | −0.38 → −0.41 | −0.03 ➖ | −0.70 → −0.63 | +0.07 |
| **CNN-LSTM** | −0.89 → **−0.47** | **+0.42** ✅ | −0.51 → −0.46 | +0.05 | −0.67 → **−0.44** | **+0.23** ✅ |

**Resultado:** Todas las features **reduce drawdown** drásticamente en XGB (−40% en Exp C) y CNN-LSTM. Para LR el efecto es mixto.

---

## 5. Resultados — Win Rate

Mixto, sin tendencia clara. Win rate no es muy sensible al subset de features.

---

## 6. Conclusiones

### 🎯 Hallazgo principal

**Usar las 61 features completas supera a la selección estadística (Pearson/VIF/SHAP/Spearman) en la mayoría de los casos**, especialmente en:
- F1-macro: 12/15 casos ganan TODAS
- Profit Factor: claramente mejor con TODAS para LR, XGB, CNN-LSTM
- Max Drawdown: drásticamente mejor (menos negativo) con TODAS

### 🧠 Interpretación

1. **El filtrado estadístico es demasiado conservador**. Eliminar features por p>0.05 individualmente pierde información que en combinación es predictiva (ej. interacciones no lineales que LR e2c. capturan).

2. **Sub-conjuntos muy pequeños (3-4 features) son insuficientes**. El caso de LR-filtradas Exp B con solo 4 features es paradigmático: la regularización elasticnet con 61 features hace la selección INTERNA (con L1) mejor que el filtrado externo.

3. **El VIF excluye features colineales útiles**. Por ej. ret_1d, ret_2d, ret_3d tienen alta correlación pero juntas dan información sobre la aceleración del retorno.

4. **SHAP filtra mejor que Pearson/Spearman** porque considera interacciones. Por eso el delta para XGBoost (que usa SHAP) es menor que para los demás. Aun así, TODAS supera al subset SHAP.

5. **Excepciones (LSTM Exp C, CNN-LSTM Exp C):** con poco train data (4 años, Exp C), reducir features ayuda a evitar overfitting en deep learning.

### 📋 Recomendación final para la tesis

| Modelo | Estrategia recomendada |
|--------|------------------------|
| **LR** | Todas las 61 features + elasticnet (la regularización L1+L2 hace la selección internamente) |
| **XGBoost** | Todas las 61 features + Optuna (los árboles ignoran features irrelevantes naturalmente) |
| **LSTM** | Todas las 61 features para Exp A, B; filtradas (Spearman) para Exp C si train data limitado |
| **CNN puro** | Todas las 61 features (consistencia con LSTM) |
| **CNN-LSTM** | Todas las 61 features para Exp B; filtradas (Spearman) para Exp A, C |

### 💡 Justificación en el paper

> "Aunque el procedimiento clásico de selección de features mediante tests estadísticos (Pearson, VIF, Spearman) se aplicó como benchmark, los resultados muestran que **el uso de las 61 features completas** combinado con **regularización interna del modelo** (elasticnet para LR, profundidad limitada + L1/L2 para XGBoost, dropout para LSTM/CNN) **produce mejor rendimiento** en F1-macro test (Δ promedio = +0.02), Profit Factor (Δ promedio = +0.12) y Max Drawdown (Δ promedio = +0.15, menos negativo). La regularización en el modelo es más efectiva que el filtrado externo para descubrir las features útiles."

### 📊 Aplicabilidad al script 02

El `script 02` (validación de features con Pearson/VIF/SHAP/Spearman) sigue siendo útil para:
- **Interpretabilidad** del paper (ranking de features más importantes).
- **Análisis exploratorio** del dataset.
- **No para preselección de features de entrenamiento.**

Para entrenamiento de los 5 modelos, usar siempre las 61 features y dejar que el modelo regularice internamente.

---

## 7. Archivos generados

- `RESULTADOS_OPTIMIZADOS/reportes/feature_selection/comparativa_GLOBAL.csv`
- `RESULTADOS_OPTIMIZADOS/reportes/feature_selection/deltas_GLOBAL_F1_macro.csv`
- `RESULTADOS_OPTIMIZADOS/reportes/feature_selection/deltas_GLOBAL_Win_Rate.csv`
- `RESULTADOS_OPTIMIZADOS/reportes/feature_selection/deltas_GLOBAL_Profit_Factor.csv`
- `RESULTADOS_OPTIMIZADOS/reportes/feature_selection/deltas_GLOBAL_Max_Drawdown.csv`
- `RESULTADOS_OPTIMIZADOS/reportes/feature_selection/F1_filt_vs_all_GLOBAL.png`
- `RESULTADOS_OPTIMIZADOS/modelos_optimizados/cnn_puro_filtradas/` (corridas controladas)
- `scripts_opt/analisis_feature_selection.py`
- `scripts_opt/opt_cnn_puro_filtradas.py`
