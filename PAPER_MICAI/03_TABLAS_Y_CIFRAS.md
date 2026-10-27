# 03 — Tablas y cifras del artículo (copiadas del texto publicado)

> Números exactos de `paper_review/paper.tex`. Si alguna cifra se cita en
> una diapositiva, el reporte técnico o una respuesta, debe coincidir con
> esta página. Fuentes de datos: §3–§7 `RESULTADOS_OPTIMIZADOS/v4/resultados_v4.csv`;
> §8 `RESULTADOS_OPTIMIZADOS/v5/` (reportes `tabla1`–`tabla5`).

## Tabla 1 — Particiones temporales (§3.4)

| Experiment | Train | Validation | Test | Train years |
|---|---|---|---|---:|
| A | 2014–2023 | 2024 | 2025 | 10 |
| B | 2018–2023 | 2024 | 2025 | 6 |
| C | 2020–2023 | 2024 | 2025 | 4 |

## Tabla 2 — Efecto de la preselección estadística (§6)

Δ = F1(todas las 61) − F1(filtradas), modelo global. Positivo: usar todas es mejor.

| Model | Filter | Exp A | Exp B | Exp C |
|---|---|---:|---:|---:|
| LR | Pearson + VIF (4–8 feats) | +0.024 | +0.026 | +0.021 |
| XGBoost | SHAP top-N (23–25 feats) | +0.009 | +0.021 | +0.022 |
| LSTM | Spearman (3–25 feats) | +0.039 | +0.036 | −0.006 |
| CNN 1D | Spearman | +0.035 | −0.025 | +0.011 |
| CNN-LSTM | Spearman | −0.011 | +0.020 | −0.026 |

11 de 15 positivos. Figura para diapositiva: `figuras_presentacion/P03`.

## Tabla 3 — F1-macro en la prueba 2025, modelos globales (§7.1)

| Model | Exp A (10y) | Exp B (6y) | Exp C (4y) | Avg |
|---|---:|---:|---:|---:|
| **LR** | **0.411** | 0.385 | **0.401** | **0.399** |
| XGBoost | 0.396 | **0.386** | 0.373 | 0.385 |
| LSTM | 0.389 | 0.370 | 0.370 | 0.376 |
| CNN-LSTM | 0.376 | 0.384 | 0.371 | 0.377 |
| CNN 1D | 0.361 | 0.343 | 0.373 | 0.359 |
| Random 1/3 | 0.333 | 0.333 | 0.333 | 0.333 |

Figura: `figuras_presentacion/P01`.

## Tabla 4 — Métricas económicas, Exp B global, 2025 (§7.1)

| Model | F1 | Win rate | Profit factor | Max drawdown | Sharpe |
|---|---:|---:|---:|---:|---:|
| LR | 0.385 | 0.497 | **1.210** | −0.470 | **+0.755** |
| XGBoost | **0.386** | 0.500 | 1.083 | −0.432 | +0.345 |
| CNN-LSTM | 0.384 | **0.505** | 1.041 | **−0.403** | +0.147 |
| LSTM | 0.370 | 0.491 | 1.120 | −0.406 | +0.433 |
| CNN 1D | 0.343 | 0.510 | 1.031 | −0.434 | +0.121 |

*(Nota: el texto marca en negritas el win rate de CNN-LSTM, 0.505, aunque el
de la CNN 1D, 0.510, es mayor; detalle de formato del artículo publicado, no
se corrige.)* Figura: `figuras_presentacion/P04`.

## Tabla 5 — F1-macro promedio de 7 acciones, modelos por acción (§7.2)

| Model | Exp A | Exp B | Exp C | Avg |
|---|---:|---:|---:|---:|
| **LR** | **0.411** | **0.392** | **0.359** | **0.387** |
| XGBoost | 0.376 | 0.370 | 0.352 | 0.366 |
| CNN-LSTM | 0.368 | 0.342 | 0.356 | 0.355 |
| LSTM | 0.314 | 0.353 | 0.326 | 0.331 |
| CNN 1D | 0.378 | 0.332 | 0.280 | 0.330 |

## Tabla 6 — Exp B global con el protocolo corregido, 2025 (§8)

| Model | Trials | H-par | F1-macro | 95 % CI | Δ vs Tabla 4 | Sharpe |
|---|---:|---:|---:|---|---:|---:|
| **LR** | 150 | 5 | **0.404** | [0.379, 0.428] | +0.019 | **+0.895** |
| CNN-LSTM | 80 | 19 | 0.372 | [0.346, 0.395] | −0.011 | −0.074 |
| LSTM | 80 | 17 | 0.369 | [0.341, 0.395] | −0.001 | −0.345 |
| XGBoost | 150 | 9 | 0.359 | [0.334, 0.381] | −0.027 | +0.462 |
| CNN 1D | 80 | 20 | 0.359 | [0.332, 0.386] | +0.016 | −0.459 |

Diferencias pareadas de la LR (todas excluyen el cero): +0.045 XGBoost,
+0.035 LSTM, +0.031 CNN-LSTM, +0.045 CNN 1D. Ninguna de las seis diferencias
entre los otros cuatro es significativa. Figuras: `figuras_presentacion/P02`
y `P06`.

## Figura 1 — Distribución de señales, globales, Exp B (§7.5)

Archivo: `paper_review/figures/fig_signal_dist.png`. Mensajes: CNN 49 %
BUY y 6 % SELL; LR 18 % BUY y 38 % SELL; LSTM y XGBoost cerca de la
proporción base.

## Otras cifras del texto

| Cifra | Qué es | Sección |
|---|---|---|
| 120 | Corridas: 5 modelos × 3 particiones × (1 global + 7 por acción) | §1, §7 |
| 61 | Variables en 9 familias | §3.3 |
| 2013-12-31 a 2025-12-29 | Periodo de datos | §3.1 |
| +24.2 % / +46.3 % / 9.º de 12 | Retorno medio 2025 / mediana 2014–2024 / posición | §3.4 |
| 39.1 % (3.ª) / −33.0 % / 19.0 | Volatilidad, caída máxima media y VIX medio de 2025 | §3.4 |
| 29.6 / 42.2 / 28.3 % | Proporción SELL/HOLD/BUY en 2025 | §3.4, §7.5 |
| 15.5 % / 3.4 % / 7.0 % / 74.1 % | Acción / modelo / experimento / interacción y ruido en el Sharpe | §7.3 (figura `P05`) |
| −0.15 / −0.16 | Media del Sharpe de GOOGL / mediana de NVDA | §7.3 |
| 0.026 | Diferencia de la LR entre ventanas de entrenamiento | §7.4 |
| F1 0.44, Sharpe +2.06, +201 % | XGBoost por acción, TSLA, Exp B | §7.6 |
| 1 736 / 1 596 / 1 316 | Filas de prueba: protocolo corregido / redes lookback 20 / 60 en §7 | §8 |
| 18 de 18 | Celdas reproducidas por el código nuevo | §8 |
| 54 / 53 / 74 | Intentos terminados de LSTM / CNN / CNN-LSTM (de 80) | §8 |
| 7–12 s | Duración de un entrenamiento de red en GPU | §8 |
| +0.005 / −0.025 / −0.054 / −0.059 | Cambio medio de F1 entre §7 y §8: LR / XGBoost / CNN / CNN-LSTM | §8 |
| +0.059 | Ganancia de la LSTM al elegir la época por F1 | §8 |
| ln 3 = 1.0986 | Pérdida de validación de la que no bajan las redes | §8 |
| 592 k → 10 k | Parámetros de la LSTM sin cambio de resultado | §8 |
| −0.024 a −0.047 | Efecto de reentrenar las redes con validación | §8 |
| 1.27 | Profit factor de la LR con el protocolo corregido | §8 |
| −0.41, −0.40 → −0.68, −0.62 | Caída máxima de LSTM y CNN-LSTM en §7 y en §8 | §9 |
