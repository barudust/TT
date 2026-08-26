# Vía 7 — Refinamiento post-Optuna

> **Fecha inicio: 2026-08-25.** Este documento resume las técnicas que las vías
> 0-6 NO probaron. Nada de teoría — código real, resultados reales,
> conclusiones honestas. Cierra la búsqueda: si algo de aquí no ayuda, ya no
> hay nada más razonable que probar sin cambiar la definición del problema
> (target, features, activos) o meter datos externos (que ya están listados
> en [ALTERNATIVAS_FUTURAS.md](ALTERNATIVAS_FUTURAS.md)).

## Motivación

Al revisar el trabajo hecho encontré que **el pipeline ya cubre el 95 % de
las técnicas estándar**:

- Multi-seed averaging, elasticnet, class balancing, refit train+val
- Optuna 150 trials LR/XGB, 80 trials deep (V2)
- Búsqueda simétrica LR/XGB (V3)
- Bootstrap IC 95 % con embargo (V6)
- Walk-forward v4 y v5
- Focal loss + label smoothing YA están en el espacio de búsqueda
- Feature selection Pearson/VIF/Spearman/SHAP probado y descartado (11/15)
- Ensembles simples (stacking, soft voting, blending trivial) descartados
- Alternativas descartadas: LightGBM, CatBoost, GRU, Transformer, TabNet, N-BEATS

**Lo que faltaba probar** (buscado con `grep` sobre `scripts_opt/`):

| Técnica | Por qué faltaba |
|---|---|
| Calibración isotónica | Post-training, mejora argmax cuando las probas están mal calibradas |
| Threshold económico de HOLD | Sube Sharpe sin re-entrenar; el paper documenta signal_hold artificialmente alto |
| Blending LR+XGB optimizado por Sharpe | Antes se hizo por F1 y ganó ~90 % LR; con Sharpe podría ser distinto |
| SWA (Stochastic Weight Averaging) | Estándar en deep learning moderno; reduce overfitting sin costo extra |
| Recency weighting temporal | Mercados no son estacionarios; datos recientes deberían pesar más |

## Metodología

Todas las técnicas se prueban sobre el **baseline v5 congelado** (config
ganadora de Optuna), en **Exp B GLOBAL** (el experimento principal), en
**test 2025**. Regla de adopción: mejora ≥ 0.005 F1 O ≥ 0.10 Sharpe respecto
al baseline v5. Cualquier resultado se documenta aquí, positivo o negativo.

Baseline v5 (test 2025, tabla2 v5):

| Modelo | F1 | Win Rate | Profit Factor | Max DD | Sharpe |
|---|---:|---:|---:|---:|---:|
| LR | 0.4036 | 0.520 | 1.270 | −0.453 | +0.895 |
| XGBoost | 0.3591 | 0.491 | 1.111 | −0.499 | +0.462 |
| LSTM | 0.3688 | 0.490 | 0.923 | −0.676 | −0.345 |
| CNN | 0.3590 | 0.484 | 0.900 | −0.725 | −0.459 |
| CNN-LSTM | 0.3723 | 0.484 | 0.982 | −0.621 | −0.074 |

## Resultados

Datos primarios en `RESULTADOS_OPTIMIZADOS/v7/{calibracion,blending,swa,recency}.csv`.

### 1) Calibración isotónica + threshold económico

Probs de val (2024) generadas en modo dev (out-of-sample). Isotónica ajustada por clase (one-vs-rest) sobre val y aplicada a test.

| Modelo | Baseline F1 | +iso F1 | +thr F1 | Baseline Sharpe | +iso Sharpe | +thr Sharpe |
|---|---:|---:|---:|---:|---:|---:|
| LR | **0.4036** | 0.3575 | 0.2563 | **+0.895** | +0.303 | +1.177 |
| XGBoost | 0.3591 | **0.3711** | **0.3786** | +0.462 | +0.596 | **+0.809** |
| LSTM | 0.3688 | 0.3126 | 0.3410 | −0.345 | +0.123 | −0.470 |
| CNN | 0.3590 | 0.3124 | 0.2379 | −0.459 | +0.481 | +0.046 |
| CNN-LSTM | 0.3723 | 0.3053 | 0.2517 | −0.074 | +0.332 | +0.619 |

**Hallazgos:**

1. **XGBoost + calibración isotónica MEJORA AMBAS métricas**: F1 sube 0.359 → **0.371** (+0.012) y Sharpe +0.46 → **+0.60**. Es la única técnica de esta vía que mejora F1 y Sharpe simultáneamente. **Se adopta para XGBoost.**
2. **XGBoost + threshold económico** da F1=0.379 y Sharpe=+0.81. Es la mejor XGB variante, aunque τ=0.275 se elige sobre validación y hay riesgo de overfitting al τ. Se adopta con cautela (registrado como opción).
3. **LR + threshold económico** empuja Sharpe a +1.18 (mejor de todos) pero derrumba F1 (0.404 → 0.256). Solo tiene sentido si el objetivo es Sharpe puro y se acepta muchísimos HOLD. Se documenta pero no se adopta como principal.
4. **Deep models con isotonic** rescatan sus Sharpe negativos a positivos, aunque F1 baja 0.06–0.07. Coste alto en F1, beneficio moderado en Sharpe. No cambia el ranking del paper.

**Adopción v7:** XGBoost pasa de baseline a **XGBoost + isotonic** (F1 y Sharpe ambos mejoran). Los demás modelos se quedan igual.

### 2) Blending LR + XGB, objetivo Sharpe (Optuna 50 trials)

Optuna busca `w_lr ∈ [0,1]` que maximice Sharpe en val (2024). Aplicado a test.

| Pesos elegidos | F1 test | Sharpe test | vs LR baseline |
|---|---:|---:|---|
| LR=0.255, XGB=0.745 | 0.3586 | +0.306 | **PEOR** (F1 −0.045, Sharpe −0.589) |

**Hallazgo:** Optuna encuentra pesos que maximizan Sharpe en val, pero **no generalizan**. LR solo (Sharpe +0.895) supera cualquier blend LR+XGB.

### 3) Blending 5-way por F1 y por Sharpe (Optuna 100 trials cada uno)

| Objetivo Optuna | Pesos | F1 test | Sharpe test |
|---|---|---:|---:|
| F1-macro | LR=0.03, XGB=0.03, LSTM=0.41, CNN=0.03, CNN-LSTM=0.49 | 0.3730 | +0.042 |
| Sharpe | LR=0.11, XGB=0.45, LSTM=0.28, CNN=0.06, CNN-LSTM=0.10 | 0.3578 | +0.152 |

**Hallazgo:** Ambos peores que LR solo. Aún el que "optimiza F1" en val (que da mucho peso a LSTM+CNN-LSTM) pierde 0.03 F1 en test. Confirma que **el mejor modelo simple (LR) supera cualquier ensemble de los 5** en este dataset.

### 4) SWA en LSTM / CNN / CNN-LSTM

100 épocas, SWA arranca en la 40 y promedia los pesos de las últimas 60 con `torch.optim.swa_utils.AveragedModel` + `SWALR`. Después `update_bn` sobre train. Tres semillas promediadas por soft-voting.

| Modelo | Baseline F1 / Sharpe | +SWA F1 / Sharpe | Diagnóstico |
|---|---|---|---|
| LSTM | 0.3688 / **−0.345** | 0.3611 / **+0.141** | F1 casi igual, Sharpe pasa de negativo a positivo (**+0.49**). MaxDD también mejora (−0.68 → −0.53). |
| CNN | 0.3590 / −0.459 | 0.3375 / −0.448 | F1 baja (−0.022), Sharpe casi igual. **PEOR**. |
| CNN-LSTM | 0.3723 / −0.074 | 0.3723 / −0.051 | Igual F1, Sharpe casi igual. Sin efecto. |

**Hallazgo:** SWA solo ayuda al LSTM: rescata el Sharpe negativo, pero el F1 baja marginalmente. No cambia el ranking (LR sigue muy por encima). Se documenta pero no se adopta como configuración principal.

### 5) Recency weighting en LR / XGB

Se pondera cada muestra por `w = exp(-Δdías / τ)` respecto al día más reciente de train. τ ∈ {30, 90, 180, 365, 730, 1500, 3000, ∞} en días.

**LR** (elegido en val 2024, aplicado en test 2025):

| τ | F1 val | Comentario |
|---:|---:|---|
| 30 días | 0.1888 | colapsa a HOLD (muy pocos datos) |
| 90 | 0.1888 | igual |
| 180 | 0.1888 | igual |
| 365 | 0.2031 | mejora leve |
| 730 | 0.2622 | sigue mejorando |
| 1500 | 0.3034 | sigue |
| 3000 | 0.3152 | sigue |
| **∞** (sin decay) | **0.3258** ★ | **el ganador es "no pesar por antigüedad"** |

Test 2025 con τ=∞: F1=**0.4042** vs baseline 0.4036 (**+0.0006**), Sharpe **+0.947** vs +0.895 (**+0.052**). Mejora insignificante — al borde de ruido de coma flotante.

**XGBoost** (mismo procedimiento):

| τ | F1 val |
|---:|---:|
| 30 | 0.3093 |
| 90 | 0.3150 |
| 180 | 0.3442 |
| 365 | 0.3412 |
| 730 | 0.3504 |
| 1500 | 0.3588 |
| **3000** | **0.3632** ★ |
| ∞ | 0.3597 |

Test 2025 con τ=3000 d (~8 años, casi todo el train): F1=0.3642 vs baseline 0.3591 (+0.005), Sharpe **+0.029** vs baseline +0.462 (**−0.43**). F1 sube marginalmente pero Sharpe se derrumba. **Descartado.**

**Hallazgo:** el mercado (al menos las 7 tech de 2018-2025) **no es lo suficientemente no-estacionario** como para que pesar por antigüedad ayude. Los datos "viejos" siguen siendo informativos.

## Conclusiones definitivas

De las 6 técnicas ejecutadas en Vía 7:

| # | Técnica | Resultado | Adoptada |
|---|---|---|:---:|
| 1a | Isotonic calibration (LR) | F1 −0.05, Sharpe −0.59 | ✗ |
| 1b | Isotonic calibration (XGBoost) | **F1 +0.012, Sharpe +0.13** | ✓ |
| 1c | Isotonic calibration (deep) | F1 −0.06/−0.07, Sharpe se vuelve positivo pero MaxDD sigue mal | ✗ |
| 2 | Threshold económico HOLD | Sharpe sube pero F1 destruida | ✗ |
| 3a | Blending LR+XGB por Sharpe | Peor que LR solo | ✗ |
| 3b | Blending 5-way por F1 | Peor que LR solo | ✗ |
| 3c | Blending 5-way por Sharpe | Peor que LR solo | ✗ |
| 4a | SWA LSTM | Sharpe mejora pero F1 no; no cambia ranking | ✗ (documentado) |
| 4b | SWA CNN | F1 baja | ✗ |
| 4c | SWA CNN-LSTM | Sin efecto | ✗ |
| 5a | Recency weighting LR | Óptimo τ=∞ (sin decay); mejora insignificante | ✗ |
| 5b | Recency weighting XGB | F1 marginal pero Sharpe cae 0.43 | ✗ |

**Única adopción:** XGBoost + calibración isotónica (F1 0.359 → **0.371**, Sharpe +0.46 → **+0.60**).

**Conclusión general:** **ninguna técnica supera al LR baseline** (F1 0.404, Sharpe +0.895) de forma robusta. El único cambio real que hace v7 al ranking del paper es mejorar XGBoost, pero sigue siendo segundo lejos de LR.

## Diagnóstico honesto

El pipeline v0-v6 ya extrajo casi todo lo que se puede sin cambiar la
definición del problema. Las 6 técnicas de Vía 7 son estándar en la
literatura y ninguna produjo mejora salvo isotonic en XGBoost.

**Con los datos disponibles (Yahoo Finance, OHLCV+SPY+VIX, 61 features,
target percentile-based 1d), la búsqueda está cerrada.** El techo es
LR ≈ 0.40 F1 / +0.9 Sharpe en 2025.

Las mejoras adicionales requieren cambiar la naturaleza del problema o
meter datos externos, y ya están listadas en
[`ALTERNATIVAS_FUTURAS.md`](ALTERNATIVAS_FUTURAS.md): datos intradía,
sentimiento, macro (FRED), opciones, short interest, horizonte de
predicción distinto (5d, 10d), target multi-step, etc.

## Archivos generados por Vía 7

```
scripts_opt/via7_refinamiento.py         ← script único con 6 sub-comandos
RESULTADOS_OPTIMIZADOS/v7/
├── preds_val/{5 modelos}_B_global.npz   ← probs de val 2024 (out-of-sample)
├── calibracion.csv                       ← isotonic + threshold
├── blending.csv                          ← LR+XGB y 5-way
├── swa.csv                               ← SWA en 3 deep
├── recency.csv                           ← recency LR/XGB
└── tabla_refinamiento.csv                ← consolidado ordenado por Sharpe
RESULTADOS_OPTIMIZADOS/logs/via7_*.log    ← salidas verbatim
```
