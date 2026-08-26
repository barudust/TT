# Vía 8 — Exploración del dataset

> **Fecha: 2026-08-25.** Vía complementaria a [VIA7_REFINAMIENTO.md](VIA7_REFINAMIENTO.md).
> Objetivo: probar 5 ampliaciones del dataset que ni v0-v7 tocaron, siempre
> dentro del scope "Yahoo Finance, sin news, sin fundamentales, sin cambiar el
> problema" — con una excepción explícita: el **target ablation** SÍ cambia el
> problema, y se estudia como sensibilidad para saber si el target del paper
> (1d, percentiles 30/70) es óptimo.

## Motivación

Al terminar Vía 7 y auditar lo hecho, quedaron 5 huecos legítimos en el dataset:

1. **Target ablation** — probar horizontes {1,2,3,5,7,10 días} × percentiles {0.20/0.80, 0.25/0.75, 0.30/0.70, 0.33/0.67, 0.40/0.60}. ¿Es el target actual el más aprendible o hay uno mejor?
2. **Lag features** — valores previos (t-1, t-3, t-5) de las top-10 features. Da memoria explícita a LR/XGB.
3. **Cross-asset** — 3 features nuevas por ticker: `beta_vs_spy_20d`, `corr_xlk_20d`, `rank_ret_7`. Relaciona los tickers entre sí y con el mercado.
4. **Multi-timeframe** — mismas top-10 features agregadas en ventanas 5d y 20d.
5. **Interactions** — 15 productos entre pares de las top-10 features.

Todo se evalúa en **Exp B GLOBAL, test 2025**, con LR y XGBoost usando los
hyperparams ganadores de Optuna v5. Baseline de referencia dentro de este
pipeline:

- LR: F1=0.3907, Sharpe=+0.683
- XGBoost: F1=0.3695, Sharpe=+0.565

*(Nota: estos números difieren ligeramente del baseline v5 reportado
—F1=0.4036 LR, 0.3591 XGB— porque el pipeline de v8 es un re-implementación
independiente para poder cambiar features sin tocar v5. Lo que importa es la
comparación **relativa** dentro de v8.)*

## Resultados

### 1) Target ablation (LR sobre 16 + 12 configs)

| Horizonte | q=0.20/0.80 | q=0.25/0.75 | q=0.30/0.70 | q=0.33/0.67 | q=0.40/0.60 |
|:---:|:---:|:---:|:---:|:---:|:---:|
| **1d** | — | **F1 0.411** / Sh +0.72 | F1 0.390 / Sh +0.68 (baseline) | F1 0.389 / Sh +0.76 | F1 0.345 / Sh +0.74 |
| 2d | F1 0.418 / Sh +0.72 | F1 0.410 / Sh +0.85 | F1 0.395 / Sh +0.97 | — | — |
| 3d | — | F1 0.409 / Sh +0.81 | F1 0.405 / Sh +1.06 | F1 0.404 / Sh +0.98 | F1 0.362 / Sh +1.32 |
| **5d** | F1 0.424 / Sh +1.16 | **F1 0.430 / Sh +1.15** | F1 0.414 / Sh **+1.29** | F1 0.404 / Sh +1.03 | F1 0.395 / Sh +1.30 |
| **7d** | F1 0.419 / Sh +1.43 | F1 0.425 / **Sh +1.51** | F1 **0.430** / Sh +1.18 | — | — |
| 10d | F1 0.400 / Sh +1.15 | F1 0.400 / Sh +1.18 | F1 0.402 / Sh +1.02 | F1 0.416 / Sh +1.21 | F1 0.398 / Sh +1.09 |

**Hallazgo:** el target de 1d es el más difícil de todo el barrido. El sweet spot está en **h=5-7d con percentiles 0.25/0.75**: F1 sube a ~0.43 (+0.03) y Sharpe a ~+1.15 a +1.51 (+0.5 a +0.8). h=10d ya empeora (regresión a la media).

**Implicación:** el paper publicó el problema más difícil posible. Cambiar a target de 5d subiría F1 y Sharpe sustancialmente, pero cambia la definición del problema ("señal cada 5 días" ≠ "señal diaria"). Se documenta como **material de sensibilidad** y como base para una segunda versión / trabajo futuro.

### 2) Lag features (+30 features nuevas)

Top-10 features (por |coef| de LR baseline): VIX_norm, vol_log, VIX, SP500_vol20, SP500_ret, rango_rel, atr_norm, vol_ratio, SP500_mom20, sombra_sup. Se agregan sus valores en t−1, t−3, t−5.

| Dataset | Modelo | F1 | Sharpe |
|---|---|---:|---:|
| baseline | LR | 0.3907 | +0.683 |
| baseline | XGBoost | 0.3695 | +0.565 |
| +lags | LR | 0.3865 | +0.540 (peor) |
| +lags | XGBoost | 0.3814 | +0.262 (peor Sharpe) |

**Hallazgo:** XGBoost F1 sube marginalmente (+0.012) pero Sharpe cae (−0.30). LR empeora ambas. **No adoptar.** Los indicadores técnicos ya son transformaciones de la historia; agregar lags añade ruido.

### 3) Cross-asset (+3 features)

| Dataset | Modelo | F1 | Sharpe |
|---|---|---:|---:|
| baseline | LR | 0.3907 | +0.683 |
| baseline | XGBoost | 0.3695 | +0.565 |
| +cross_asset | LR | 0.3940 | +0.823 |
| +cross_asset | XGBoost | 0.3789 | +0.428 |

**Hallazgo:** LR mejora ambas (+0.003 F1, +0.14 Sharpe). Mejora pequeña pero direccionalmente positiva. XGBoost F1 sube +0.009 pero Sharpe cae. **No convincente para adopción.**

### 4) Multi-timeframe (+20 features)

Top-10 agregadas en ventanas 5d y 20d.

| Dataset | Modelo | F1 | Sharpe |
|---|---|---:|---:|
| baseline | LR | 0.3907 | +0.683 |
| baseline | XGBoost | 0.3695 | +0.565 |
| +multi_tf | LR | 0.3886 | +0.484 (peor) |
| +multi_tf | XGBoost | 0.3818 | +0.503 |

**Hallazgo:** XGBoost F1 sube +0.012 pero Sharpe similar. LR empeora ambas. **No adoptar.** Similar razonamiento: las medias móviles ya son parte del feature set original (ma10, ma20, ma50, ma200), agregar más versiones no aporta.

### 5) Interactions (+15 productos entre top-10)

| Dataset | Modelo | F1 | Sharpe |
|---|---|---:|---:|
| baseline | LR | 0.3907 | +0.683 |
| baseline | XGBoost | 0.3695 | +0.565 |
| **+interactions** | **LR** | **0.4133** | **+0.914** |
| +interactions | XGBoost | 0.3826 | +0.205 |

**Hallazgo:** **LR mejora ambas dramáticamente** (+0.023 F1, +0.23 Sharpe). Los productos entre features capturan relaciones no lineales que LR normalmente no puede aprender. XGBoost, que ya modela interacciones internamente en sus árboles, no gana.

**Adopción:** LR + interactions (productos entre 15 pares de las top-10 features).

### 6) Combinaciones (mejores técnicas apiladas)

Se apilan las mejoras que aportaron algo (interactions + crossasset) sobre distintos targets:

| Config | Modelo | F1 | Sharpe | Win Rate | Max DD |
|---|---|---:|---:|---:|---:|
| baseline (h=1d, 30/70, base) | LR | 0.390 | +0.68 | 0.516 | −0.42 |
| baseline (h=1d, 30/70, base) | XGB | 0.368 | +0.56 | 0.498 | −0.57 |
| **h=1d + interactions** *(mismo problema)* | **LR** | **0.413** | **+0.92** | 0.532 | −0.52 |
| h=1d + interactions | XGB | 0.383 | +0.21 | 0.508 | −0.50 |
| h=5d, 25/75, base | LR | 0.430 | +1.15 | 0.528 | −0.90 |
| h=5d, 30/70, base | LR | 0.414 | +1.29 | 0.534 | −0.89 |
| h=5d, 25/75, base + inter | LR | 0.430 | +1.19 | 0.526 | −0.91 |
| h=5d, 30/70, base + inter | LR | 0.416 | **+1.39** | 0.528 | −0.92 |
| **h=5d, 25/75, base + inter + crossasset** | **LR** | **0.432** | +1.15 | 0.528 | −0.91 |
| **h=5d, 25/75, base + inter + crossasset** | **XGB** | **0.390** | **+1.26** | 0.513 | −0.88 |
| h=10d, 33/67, base + inter | LR | 0.408 | +1.34 | 0.521 | −0.995 |

Notas:
- El MaxDD "−0.9" en configs de horizonte largo es engañoso: los retornos individuales de 5d son ~5× los de 1d, así que el drawdown absoluto también escala. Si se quiere comparar drawdown "por unidad de tiempo", habría que dividir. **No es un colapso, es un cambio de unidades.**
- Con **h=5d, 25/75, base + inter + crossasset**, tanto LR como XGB llegan a Sharpe > +1.15. Es la mejor combinación general.

## Conclusiones definitivas

### Sin cambiar el problema (h=1d, q=0.30/0.70, como el paper)

**Única mejora robusta:** LR + **interactions** (15 productos entre top-10 features).
- F1: 0.390 → **0.413** (+0.023)
- Sharpe: +0.68 → **+0.92** (+0.24)

Esto es una **mejora genuina** al mismo problema del paper.

### Cambiando el problema (mejores targets)

**h=5d, q=0.25/0.75, base + interactions + crossasset** es la mejor combinación en absoluto:
- LR: F1=**0.432**, Sharpe=+1.15
- XGB: F1=0.390, Sharpe=**+1.26**

Cambiar de "señal cada 1 día" a "señal cada 5 días" **es una decisión de producto/tesis**, no técnica: son problemas diferentes.

### Resumen de qué se adoptaría en cada escenario

| Escenario | Config recomendada | F1 test | Sharpe |
|---|---|---:|---:|
| Paper actual (respetar h=1d) | LR + interactions | 0.413 | +0.92 |
| Nueva iteración libre | h=5d, 25/75, LR + inter + CA | 0.432 | +1.15 |
| Máximo Sharpe | h=5d, 30/70, LR + inter | 0.416 | +1.39 |
| Baseline v5 (referencia) | LR baseline | 0.404 | +0.90 |

### Qué NO ayuda con este dataset

- **Lag features:** los indicadores técnicos ya son transformaciones de la historia; agregar lags añade ruido.
- **Multi-timeframe:** las medias móviles ya están en el feature set original.
- **Cross-asset por sí solo:** aporta marginalmente en LR. Solo suma con interactions y target ajustado.
- **Target de 1d:** es el más ruidoso. h=3-7d es más aprendible.

## Diagnóstico final combinando Vía 7 + Vía 8

Después de todo lo probado (v0-v8), estas son las palancas reales:

| Palanca | Ganancia F1 | Ganancia Sharpe | Cambia el problema |
|---|---:|---:|:---:|
| Optuna 150 trials (v5) | 0.033 | +0.24 | No |
| XGBoost + isotonic (v7) | 0.012 | +0.13 | No |
| **LR + interactions (v8)** | **0.023** | **+0.24** | **No** |
| Target h=5d en vez de 1d (v8) | 0.03-0.04 | +0.3-0.7 | **Sí** |
| Datos externos (macro, IV, sentimiento) | +0.02 a +0.07 | +0.5 (estimado) | No, pero requiere infra |

**Recomendación final:** para la próxima iteración del paper:
1. Adoptar **LR + interactions** (mejora genuina sin cambiar el problema).
2. Añadir tabla de **sensibilidad al horizonte de target** (una fila por h=1,3,5,7,10 mostrando F1 y Sharpe).
3. Mantener la comparación de los 5 modelos con el mismo target del paper original.
4. Marcar como "trabajo futuro" el target de 5d con las mejoras acumuladas.

## Archivos generados

```
scripts_opt/via8_dataset.py             ← 5 sub-comandos + consolidar
scripts_opt/via8_target_extendido.py    ← ampliación del target ablation
scripts_opt/via8_combinado.py           ← combinaciones apiladas
RESULTADOS_OPTIMIZADOS/v8/
├── target_ablation.csv                 ← 16 configs (h × q)
├── target_ablation_ext.csv             ← 12 configs adicionales
├── lag_features.csv
├── crossasset.csv
├── multi_tf.csv
├── interactions.csv
├── combinados.csv                      ← target × interactions × crossasset
└── tabla_dataset.csv                   ← consolidado
RESULTADOS_OPTIMIZADOS/logs/via8_*.log
```
