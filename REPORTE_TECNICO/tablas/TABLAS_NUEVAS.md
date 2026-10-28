# Tablas nuevas para el reporte

> Tablas listas para pasar al documento. Cada una indica a qué sección va,
> qué tabla actual reemplaza (si aplica) y de dónde salen los datos.
> `RO/` = `RESULTADOS_OPTIMIZADOS/`. Formato sugerido: tres decimales en F1,
> kappa y AUC; dos en Sharpe.

| ID | Contenido | Sección | Reemplaza |
|---|---|---|---|
| T-01 | Etapa 1 (TT1) resumida | 6.2 | Tablas 15–18, 23–28 |
| T-02 | Las seis etapas | 4.1 | — |
| T-03 | Particiones y validaciones | 4.7 | Tablas 3 y 8 |
| T-04 | Familias de características y 15 interacciones | 4.5 | Complementa Tabla 4 |
| T-05 | Configuración de los cinco modelos por etapa | 4.9 | Tabla 9 y texto de 4.8 |
| T-06 | Búsqueda de hiperparámetros | 4.10 | — |
| T-07 | Etapa 3 (paper §7) | 6.4 | — |
| T-08 | Igualdad de condiciones | 4.11 | — |
| T-09 | Etapa 4: F1 con intervalos | 6.5 | — |
| T-10 | Etapa 4: ocho métricas | 6.5 | — |
| T-11 | Multicolinealidad | 4.6 | Tablas 5–7 |
| T-12 | Prueba año por año | 6.6 | Tabla 29 |
| T-13 | Prueba ciega 2026 | 6.6 | — |
| T-14 | Endpoints de la API | 5.6 | Tabla 13 |
| T-14b | Pantallas de la aplicación | 5.7 | — |
| T-15 | Cambios del sistema respecto a TT1 | 5.11 | Tablas 10, 11, 12, 14 |
| T-16 | Reproducibilidad: scripts por etapa | Anexo C | — |
| T-17 | Global contra por acción | 6.8 | Tabla 21 |
| T-18 | Corrección del exceso de mantener | 6.8 | — |
| T-19 | Modelo de la plataforma en 2026 | 6.8 | — |
| T-20 | Lo que aportaron las interacciones | 6.7 | — |
| T-21 | Niveles de seguridad | 5.7 / 6.8 | — |

---

## T-01 · Etapa 1 (TT1): resumen de la línea base

**Pie sugerido:** *Resultados de la Etapa 1 (reporte de TT1): modelos por
acción, características distintas por modelo y ventana de las redes elegida
con la prueba. F1-macro promedio de los tres experimentos (Exp A con prueba
2024–2025) y Sharpe promedio de las siete acciones en el Experimento B. No
comparables con las etapas siguientes.*

| Modelo | Características | F1 promedio | Mínimo | Máximo | Desv. est. | Sharpe Exp B |
|---|---|---:|---:|---:|---:|---:|
| XGBoost | 23–25 (SHAP) | 0.369 | 0.304 | 0.424 | 0.028 | 0.270 |
| Regresión Logística | 3–8 (Pearson + VIF) | 0.351 | 0.253 | 0.425 | 0.041 | 0.285 |
| CNN-LSTM | 3–25 (Spearman) + 5 OHLCV | 0.340 | 0.207 | 0.418 | 0.047 | −0.430 |
| CNN 1D | 3–25 (Spearman) + 5 OHLCV | 0.331 | 0.264 | 0.387 | 0.029 | −0.980 |
| LSTM | 3–25 (Spearman) | 0.291 | 0.124 | 0.370 | 0.076 | −0.400 |

Fuente: Tablas 18 y 23 del reporte actual.

---

## T-02 · Las seis etapas del proyecto

| Etapa | Nombre | Periodo (2026) | Pregunta | Respuesta | En el paper |
|---|---|---|---|---|---|
| 1 | Línea base (TT1) | hasta mayo | ¿Funciona el sistema completo con cinco modelos? | Sí; XGBoost mejor en F1 y LR en Sharpe, con una comparación dispareja | No |
| 2 | Primeras mejoras | mayo–junio | ¿Se puede mejorar cada modelo? | Poco; filtrar variables empeora (11 de 15); hace falta un protocolo limpio | §6 |
| 3 | Comparación en igualdad de condiciones | junio | ¿Cuál gana si todos reciben lo mismo? | La LR (0.399), con XGBoost cerca | §3–§7 |
| 4 | Protocolo final | agosto | ¿El resultado sobrevive a un protocolo estricto? | Sí: la LR gana con significancia en A, B y C | §8 |
| 5 | Búsqueda de mejoras | fin de agosto | ¿Algo más mejora sin cambiar el problema? | Casi nada; se adoptan 15 interacciones como equivalentes | No |
| 6 | Modelo de la plataforma y validación | septiembre–octubre | ¿Cómo se comporta el modelo real con datos nuevos? | Se corrige el exceso de mantener; 2026: F1 0.354 | No |

Fuente: `ESTUDIO_TT/03_MAPA_DE_EXPERIMENTOS.md` §3. Figura: `diagramas/D08`.

---

## T-03 · Particiones temporales y validaciones

**Pie:** *Particiones usadas en el trabajo. Los tres experimentos comparten
validación y prueba; las validaciones adicionales evalúan el desempeño en
otros años.*

| Uso | Entrenamiento | Validación / elección | Prueba | Etapas |
|---|---|---|---|---|
| Experimento A | 2014–2023 | 2024 | 2025 | 3–4 |
| **Experimento B (principal)** | **2018–2023** | **2024** | **2025** | 3–4 |
| Experimento C | 2020–2023 | 2024 | 2025 | 3–4 |
| Protocolo final, modo *dev* | 2018–2022 | época: 2023; configuración: 2024 | — | 4 |
| Protocolo final, modo *final* | 2018–2023 | época: 2024 | 2025 (una vez) | 4 |
| Prueba año por año, año *T* (2020–2025) | T−6 a T−2 | T−1 | T | 4 |
| Origen rodante, año *Y* (2019–2024) | los 6 años previos a *Y* | — | Y | 6 |
| Prueba ciega 2026 | 2020–2024 | 2025 | 2 ene–22 oct 2026 | 6 |
| Modelo de la plataforma | 2018–2025 | — | En operación (2026) | 6 |
| *Antecedente:* Experimento A de TT1 | *2014–2021* | *2022–2023* | *2024–2025* | *1–2* |

Folds de la prueba año por año: 2020 (entrena 2014–2018, valida 2019), 2021
(2015–2019, 2020), 2022 (2016–2020, 2021), 2023 (2017–2021, 2022), 2024
(2018–2022, 2023), 2025 (2019–2023, 2024).
Figura: `diagramas/D09`.

---

## T-04 · Familias de características y las 15 interacciones

| Familia | Número | Características |
|---|---:|---|
| Retornos logarítmicos | 5 | ret_1d, ret_2d, ret_3d, ret_5d, ret_10d |
| Momentum | 4 | mom_5d, mom_10d, mom_20d, mom_60d |
| Medias móviles | 9 | dist_ma10, dist_ma20, dist_ma30, dist_ma50, dist_ma200, cruce_ma10_ma50, cruce_ma20_ma50, cruce_ma50_ma200, pendiente_ma20 |
| Volatilidad | 8 | atr_14, atr_norm, vol_5d, vol_10d, vol_20d, vol_60d, vol_ratio_5_20, vol_ratio_20_60 |
| Osciladores | 9 | rsi_14, rsi_7, macd, macd_sig, macd_hist, stoch_k, stoch_d, stoch_diff, williams_r |
| Volumen y flujo | 8 | vol_log, vol_ratio, obv_ratio, obv_pendiente, vwap_dist, cmf_20, mfi_14, vol_trend |
| Velas | 7 | rango_rel, cambio_intra, cuerpo_rel, sombra_sup, sombra_inf, gap_apertura, hl_ratio |
| Calendario | 5 | dia_sin, dia_cos, mes_sin, mes_cos, semana_mes |
| Contexto de mercado | 6 | SP500_ret, SP500_vol20, SP500_mom20, VIX, VIX_change, VIX_norm |
| **Total base** | **61** | Para los cinco modelos |
| Interacciones | 15 | Solo en el modelo de la plataforma (abajo) |
| **Total en producción** | **76** | |

**Las 15 interacciones** (productos de pares de las 10 variables con mayor
coeficiente; pares sorteados con semilla 42):

| # | Interacción | # | Interacción |
|---|---|---|---|
| 1 | VIX_norm × SP500_vol20 | 9 | vol_log × vol_ratio |
| 2 | atr_norm × vol_ratio | 10 | SP500_ret × rango_rel |
| 3 | VIX × vol_ratio | 11 | vol_log × SP500_mom20 |
| 4 | SP500_ret × SP500_mom20 | 12 | atr_norm × SP500_mom20 |
| 5 | VIX_norm × SP500_mom20 | 13 | SP500_vol20 × SP500_ret |
| 6 | SP500_ret × vol_ratio | 14 | SP500_vol20 × atr_norm |
| 7 | VIX_norm × SP500_ret | 15 | atr_norm × sombra_sup |
| 8 | SP500_ret × atr_norm | | |

Fuente: `api/ml/features.py`, `api/ml/artifacts/interaction_pairs.json`,
`ESTUDIO_TT/A_modelo/A2` §11.

---

## T-05 · Configuración de los cinco modelos por etapa

**Pie:** *Evolución de la configuración de cada modelo. La columna "Etapa 4"
es la que produce el resultado principal; la LR de producción agrega las 15
interacciones y el peso de mantener × 0.90.*

| Modelo | TT1 (Etapa 1) | Etapa 3 (paper §7) | **Etapa 4 (final)** |
|---|---|---|---|
| **LR** | One-vs-rest, L2, C ∈ {0.001…100} en rejilla, StandardScaler, 3–8 variables | Multinomial, elasticnet (l1_ratio 0.5), C ∈ {0.01, 0.1, 1}, StandardScaler, 61 | **Multinomial, L2, C = 0.000165, RobustScaler, pesos balanceados, 61** (Optuna, 150 intentos) |
| **XGBoost** | Rejilla (árboles 100–500, prof. 3/4/6, tasa 0.01–0.1), `scale_pos_weight`, 23–25 variables | Optuna 20–40 intentos, pesos por muestra, 3 semillas, 61 | **485 árboles, prof. 9, tasa 0.074, submuestreo 0.97/0.93, min_child_weight 2, gamma 0.035, α 1.70, λ 5.23, pesos por muestra, 5 semillas** (Optuna, 150) |
| **LSTM** | Unidireccional 2 × 128, dropout 0.3, Adam 10⁻³, lote 64, 80 épocas, paciencia 15 (pérdida), lookback 20/60 | Bidireccional 2 × 128, AdamW, lote 128, lookback 20/60 (elegido con la prueba) | **Unidireccional 2 × 118, atención, dropout 0.43, focal γ 1.43, AdamW 1.6·10⁻⁴, lookback 10; 198 480 parámetros** (Optuna, 80) |
| **CNN 1D** | Conv 64→128 (k3, BN) + promedio global, F_Exp + 5 OHLCV | 3 bloques 64→128→192 (k3, BN), promedio + máximo global | **2 bloques 50→100 (k7, sin BN), promedio global, densa 101, focal γ 2.48, lookback 10; 67 007 parámetros** |
| **CNN-LSTM** | Conv 64→128 (k3, BN) → LSTM 2 × 128, F_Exp + 5 OHLCV | Conv 64→128 → LSTM 2 × 128 | **Conv 77→154 (k7, BN) → LSTM 1 × 136, focal γ 2.01, lookback 20; 276 109 parámetros** |
| Entrenamiento de redes | Fijo, sin búsqueda | Rejilla chica (unidades, capas, dropout) | Hasta 100 épocas, paciencia 20, criterio elegido por Optuna; sin reentrenar con validación |
| Estrategia | Por acción (principal) | Global y por acción | Global (principal) y por acción |

Fuentes: `ESTUDIO_TT/A_modelo/A4`, `A5`; `RO/v5/ganadores_clasicos.json`,
`ganadores_dl.json`.

---

## T-06 · Búsqueda de hiperparámetros (Etapa 4)

| Modelo | Intentos | Terminados | Hiperparámetros | Principales espacios de búsqueda |
|---|---:|---:|---:|---|
| LR | 150 | 150 | 5 | penalización {L1, L2, elasticnet}; C ∈ [10⁻⁴, 10³] (log); l1_ratio ∈ [0, 1]; pesos {balanced, ninguno}; escalador {Standard, Robust} |
| XGBoost | 150 | 150 | 9 | árboles 150–800; profundidad 2–10; tasa 0.005–0.3; submuestreo 0.5–1 y 0.3–1; min_child_weight 1–15; gamma 0–3; α 0–5; λ 0.1–8 |
| LSTM | 80 | 54 | 17 | Comunes de redes + unidades 16–256, capas 1–3, bidireccional, pooling {último, media+máx, atención} |
| CNN 1D | 80 | 53 | 20 | Comunes + bloques 1–4, filtros base 16–256, kernel {3, 5, 7}, dilatación {1, 2}, BN, densa 32–256, pooling {GAP+GMP, GAP, aplanar} |
| CNN-LSTM | 80 | 74 | 19 | Comunes + filtros base 16–128 (2 bloques), kernel {3, 5, 7}, unidades, capas |

Comunes de redes: criterio de época {pérdida, F1, F1 media de 3}; lookback
{10, 20, 40, 60}; dropout 0–0.6; tasa 10⁻⁵–3·10⁻³; weight decay 10⁻⁶–10⁻¹;
lote {64, 128, 256, 512}; pesos {balanced, ninguno, raíz}; programador
{plateau, coseno, ninguno}; recorte {0.5, 1, 5}; escalador {MinMax,
Standard, Robust}; pérdida {entropía cruzada con label smoothing 0–0.2,
focal γ 0.5–3}.
Muestreador TPE, semilla 42, 25 intentos iniciales al azar, multivariado;
poda por mediana en redes; objetivo F1-macro 2024 (modo dev).
Fuente: `ESTUDIO_TT/A_modelo/A3` §4.

---

## T-07 · Etapa 3: comparación en igualdad de condiciones (paper §7)

**Pie:** *F1-macro en la prueba 2025, Etapa 3 (mismas 61 características para
los cinco). Ventana de las redes elegida con la prueba (lo declara el
paper). En negritas, el mejor por columna.*

| Modelo | Global A | Global B | Global C | Global promedio | Por acción promedio |
|---|---:|---:|---:|---:|---:|
| LR | **0.411** | 0.385 | **0.401** | **0.399** | **0.387** |
| XGBoost | 0.396 | **0.386** | 0.373 | 0.385 | 0.366 |
| CNN-LSTM | 0.376 | 0.384 | 0.371 | 0.377 | 0.355 |
| LSTM | 0.389 | 0.370 | 0.370 | 0.376 | 0.331 |
| CNN 1D | 0.361 | 0.343 | 0.373 | 0.359 | 0.330 |
| Azar | 0.333 | 0.333 | 0.333 | 0.333 | |

Economía, Experimento B global: LR profit factor 1.210, Sharpe +0.755;
XGBoost 1.083 / +0.345; CNN-LSTM 1.041 / +0.147; LSTM 1.120 / +0.433;
CNN 1D 1.031 / +0.121.
Fuente: `paper_review/paper.tex` (Tablas 3–5); `RO/v4/resultados_v4.csv`.

---

## T-08 · Igualdad de condiciones

**Pie:** *Qué es igual para los cinco modelos en la Etapa 4 y cómo era en
la Etapa 1.*

| Aspecto | Etapa 1 (TT1) | Etapa 4 (final) |
|---|---|---|
| Características | Distintas por modelo (3 a 25) | **Las mismas 61** |
| Partición | Exp A con otra prueba | **La misma** en A, B y C |
| Filas de prueba | Clásicos 248 días por acción; redes 228 o 188 | **Las mismas 1 736** |
| Búsqueda de hiperparámetros | Rejilla en clásicos; redes fijas | **Optuna para los cinco, mismo año de decisión** |
| Uso de la prueba para decidir | Ventana de las redes elegida con la prueba | **Ninguno** |
| Métricas | F1 y simulación sin costos | **Las mismas ocho, mismo código** |
| Estrategia | Por acción | **Global** (y por acción como comparación) |
| Semillas | Una | **Cinco, probabilidades promediadas** |
| Lo que sí es distinto (por diseño) | — | Pérdida de entrenamiento y elección de época propias de cada familia; forma de la entrada (vector o ventana) |

Fuente: `ESTUDIO_TT/D_defensa/D9` §1; `RO/observaciones_sinodal/1_mismas_filas.csv`.

---

## T-09 · Etapa 4: F1-macro con intervalos de confianza (resultado principal)

**Pie:** *F1-macro en la prueba 2025 con el protocolo final, modelo global,
1 736 filas. Entre corchetes, intervalo de confianza del 95 % por bootstrap
por bloques de 20 días (2 000 réplicas). La LR es significativamente mejor que
cada uno de los otros cuatro modelos en los tres experimentos.*

| Modelo | Exp A (10 años) | Exp B (6 años, principal) | Exp C (4 años) |
|---|---|---|---|
| **Regresión Logística** | **0.406** [0.382, 0.428] | **0.404** [0.379, 0.428] | **0.401** [0.376, 0.424] |
| CNN-LSTM | 0.245 [0.230, 0.261] | 0.372 [0.346, 0.395] | 0.338 [0.307, 0.369] |
| LSTM | 0.373 [0.345, 0.402] | 0.369 [0.341, 0.395] | 0.317 [0.285, 0.346] |
| XGBoost | 0.359 [0.334, 0.383] | 0.359 [0.334, 0.381] | 0.362 [0.339, 0.387] |
| CNN 1D | 0.263 [0.246, 0.279] | 0.359 [0.332, 0.386] | 0.294 [0.260, 0.327] |

**Diferencias pareadas de la LR** (F1 de la LR menos el del otro modelo;
todas significativas):

| Contra | Exp A | Exp B | Exp C |
|---|---:|---:|---:|
| XGBoost | +0.047 | +0.045 | +0.039 |
| LSTM | +0.033 | +0.035 | +0.084 |
| CNN-LSTM | +0.161 | +0.031 | +0.062 |
| CNN 1D | +0.143 | +0.045 | +0.106 |

Nota: en A la CNN-LSTM y la CNN 1D colapsan (no predicen ningún mantener).
Fuente: `RO/v5/v6_ic_{A,B,C}_v1.csv`, `v6_pares_{A,B,C}_v1.csv`. Figura: `graficas/G01`.

---

## T-10 · Etapa 4: las ocho métricas (Experimento B)

**Pie:** *Las ocho métricas para los cinco modelos sobre las mismas 1 736
filas de 2025. En negritas, el mejor. La LR es la mejor en las ocho también en
los Experimentos A y C.*

| Modelo | F1-macro | Exactitud | Exact. balanceada | Kappa | AUC macro | Log-loss | Sharpe 0 pb | Sharpe 10 pb | Rotación |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **LR** | **0.404** | **0.435** | **0.407** | **0.120** | **0.593** | **1.076** | **+0.89** | **+0.62** | 0.38 |
| CNN-LSTM | 0.372 | 0.386 | 0.374 | 0.069 | 0.573 | 1.091 | −0.07 | −0.20 | 0.18 |
| LSTM | 0.369 | 0.381 | 0.374 | 0.065 | 0.551 | 1.093 | −0.35 | −0.41 | 0.09 |
| CNN 1D | 0.359 | 0.377 | 0.369 | 0.060 | 0.568 | 1.094 | −0.46 | −0.53 | 0.11 |
| XGBoost | 0.359 | 0.362 | 0.364 | 0.046 | 0.539 | 1.217 | +0.46 | +0.01 | 0.65 |
| *Referencia* | *azar 0.333* | | *0.333* | *0* | *0.5* | *ln 3 = 1.099* | | | |

Otras cifras de la LR en B: win rate 52 %, profit factor 1.27, caída máxima
−45 %, señales 20.7 % comprar / 51.7 % mantener / 27.5 % vender; Sharpe con 5
pb +0.76.
Fuente: `RO/observaciones_sinodal/1_metricas_panel.csv`; `RO/v5/resultados_finales.csv`.
Figura: `graficas/G02`.

---

## T-11 · Multicolinealidad: 61 características contra filtro VIF ≤ 10

**Pie:** *F1-macro en la prueba 2025 (protocolo final) con las 61
características y con un filtro iterativo VIF ≤ 10 calculado solo con el
entrenamiento (45 características). Δ = 61 − filtro; positivo favorece usar
las 61.*

| Modelo | Exp A: 61 / filtro (Δ) | Exp B | Exp C |
|---|---|---|---|
| LR | 0.406 / 0.404 (+0.001) | 0.404 / 0.409 (−0.006) | 0.401 / 0.398 (+0.002) |
| XGBoost | 0.359 / 0.357 (+0.002) | 0.359 / 0.366 (−0.006) | 0.362 / 0.367 (−0.005) |
| LSTM | 0.373 / 0.339 (+0.034) | 0.369 / 0.360 (+0.009) | 0.317 / 0.319 (−0.002) |
| CNN-LSTM | 0.245 / 0.206 (+0.039) | 0.372 / 0.357 (+0.015) | 0.338 / 0.322 (+0.016) |
| CNN 1D | 0.263 / 0.240 (+0.023) | 0.359 / 0.345 (+0.014) | 0.294 / 0.279 (+0.016) |

Las 61 son mejores en 11 de 15 casos; el filtro perjudica a las redes en 8 de
9 y a los clásicos les cambia ±0.006. Diagnóstico (entrenamiento Exp B): 26
pares con |r| > 0.9, 76 con |r| > 0.8; 26 variables con VIF > 10, 10 con
VIF > 100 (máximo 1 327.8). Pares más correlacionados: stoch_k–williams_r
(1.00), dist_ma20–vwap_dist (0.99), cruce_ma10_ma50–macd_sig (0.97).
Fuente: `RO/observaciones_sinodal/3_multicolinealidad_*`. Figura: `graficas/G06`.

---

## T-12 · Prueba año por año (2020–2025)

**Pie:** *F1-macro del modelo global en cada año de prueba, entrenando con
los cinco años anteriores al año de validación. Ajustes fijados en la Etapa 3
(no vieron ningún año de prueba). En negritas, el mejor de cada año.*

| Año de prueba | LR | XGBoost | LSTM | CNN 1D | CNN-LSTM |
|---|---:|---:|---:|---:|---:|
| 2020 | **0.393** | 0.375 | 0.350 | 0.314 | 0.327 |
| 2021 | **0.378** | 0.355 | 0.320 | 0.302 | 0.314 |
| 2022 | 0.358 | 0.347 | 0.351 | **0.375** | 0.369 |
| 2023 | 0.330 | 0.329 | 0.295 | **0.352** | 0.297 |
| 2024 | 0.326 | **0.369** | 0.299 | 0.333 | 0.306 |
| 2025 | **0.373** | 0.363 | 0.371 | 0.350 | 0.344 |
| **Media** | **0.360** | 0.356 | 0.331 | 0.338 | 0.326 |
| Años ganados | 3 | 1 | 0 | 2 | 0 |
| Sharpe medio con 10 pb | **+0.09** | −0.10 | −0.50 | −0.02 | −0.63 |

Juntando los seis años: LR − XGBoost = +0.003 [−0.007, +0.013] (no
significativa); LR − LSTM +0.026, LR − CNN-LSTM +0.025, LR − CNN 1D +0.017
(significativas).
Con los ajustes elegidos con 2024 (Etapa 4; Tabla 29 del reporte actual): LR
0.350, XGBoost 0.356, CNN-LSTM 0.328 (cinco años), LSTM 0.314, CNN 1D 0.292;
con unos u otros ajustes, ningún modelo llega a 0.40 en ningún año.
Fuente: `RO/v5/walkforward_v4.csv`;
`RO/observaciones_sinodal/2_lr_contra_cada_uno_6anios.csv`,
`2_seleccion_resumen.csv`. Figura: `graficas/G04`.

---

## T-13 · Prueba ciega 2026

**Pie:** *Prueba con datos del 2 de enero al 22 de octubre de 2026 (1 421
filas), no usados en ninguna decisión. Ajustes congelados de la Etapa 4,
entrenamiento 2020–2024, validación 2025.*

| Modelo | F1-macro | Kappa | AUC macro | Sharpe 0 pb | Sharpe 10 pb | Mantener predicho | Dif. de F1 de la LR [IC 95 %] |
|---|---:|---:|---:|---:|---:|---:|---|
| **LR** | **0.346** | 0.038 | 0.520 | +0.38 | +0.02 | 54 % | — |
| XGBoost | 0.343 | 0.036 | 0.526 | 0.00 | −0.49 | 55 % | +0.003 [−0.032, +0.034] |
| LSTM | 0.331 | 0.040 | 0.532 | +0.72 | +0.65 | 24 % | +0.015 [−0.020, +0.056] |
| CNN-LSTM | 0.318 | 0.017 | 0.523 | +0.16 | −0.01 | 19 % | +0.028 [−0.009, +0.070] |
| CNN 1D | 0.304 | 0.032 | 0.530 | **+0.88** | **+0.82** | 9 % | +0.042 [+0.006, +0.083] (significativa) |

Fuente: `RO/observaciones_sinodal/4_ciega2026.csv`, `4_ciega2026_diferencias.csv`.
Figura: `graficas/G05`.

---

## T-14 · Endpoints de la API

**Pie:** *Rutas de la API. Todas las respuestas tienen la forma
`{"success": true, "data": …}` o `{"success": false, "error": "…"}`.*

| Método y ruta | Devuelve |
|---|---|
| `GET /health` | Estado del servicio y cuántas acciones hay cargadas (`stocksLoaded` de `stocksExpected`) |
| `GET /model` | Ficha del modelo leída del `.pkl`: versión, algoritmo, penalización, C, pesos de clase, escalador, número de variables, rango de entrenamiento; definición de la etiqueta |
| `GET /market-status` | Si NYSE está abierto, si hoy es día hábil (feriados 2026–2027), hora de Nueva York y horario de actualización |
| `GET /stocks` | Las 7 acciones: precio, recomendación para la siguiente sesión, confianza, 3 probabilidades, fecha del cierre usado |
| `GET /stocks/:symbol` | Lo anterior + las últimas 10 recomendaciones con su resultado + datos de la empresa |
| `GET /stocks/:symbol/history?days=30\|60\|90` | Una fila por día: OHLCV, predicción, confianza, probabilidades, etiqueta real, retorno siguiente, acierto |
| `GET /stocks/:symbol/metrics?days=30\|60\|90` | Métricas de la ventana para una acción |
| `GET /metrics?days=30\|60\|90` | Métricas de las 7 acciones |
| `GET /stocks/:symbol/info` | Datos de la empresa (sector, capitalización, beta…) |
| `POST /admin/refresh` | Fuerza la actualización completa |
| `POST /stocks`, `/stocks/:s`, `.../history`, `.../metrics`, `.../signals` | **Desactivados (403)**; solo para pruebas locales con `ENABLE_MANUAL_OVERRIDES=1` |

Fuente: `api/main.py`; `ESTUDIO_TT/B_sistema/B2` §2; `docs/API.md`.

---

## T-14b · Pantallas de la aplicación

| Ruta | Pantalla | Qué muestra | Datos |
|---|---|---|---|
| `/` | **Hoy** | Una tarjeta por empresa: recomendación con una frase, precio, seguridad en palabras; para qué sesión es y con qué cierre se calculó; modelo elegido con enlace a «Modelos» | `GET /stocks`, `GET /market-status` |
| `/stock/:symbol` | **Detalle** | Recomendación y seguridad; 3 probabilidades; precio con un punto por recomendación; «¿Qué habría pasado con $1,000?»; aciertos; últimas 10 recomendaciones; ventanas de 30/60/90 días | `GET /stocks/:s`, `.../history`, `.../metrics` |
| `/performance` | **Resultados** | Resumen de las 7 empresas; ganancia contra comprar y esperar; F1 por empresa contra el azar; tabla ordenable | `GET /metrics` |
| `/modelos` | **Modelos** | Modelo elegido y por qué; igualdad de condiciones; prueba 2025 (A/B/C); intervalos; año por año; prueba ciega 2026; dinero con y sin comisión; global contra por acción; multicolinealidad | JSON generado por `observaciones_sinodal.py` |
| `/aprende` | **Aprende** | Qué es comprar, vender en corto y mantener: barra interactiva, venta en corto en 4 pasos, juego con los últimos 30 días reales | `GET /stocks/:s/history?days=30` |
| `/ayuda` | **Ayuda** | Guía rápida por pantalla y glosario buscable | — |
| `/about` | **Acerca de** | Descripción, metodología, ficha del modelo, aviso legal, créditos | `GET /model` |

Fuente: `Frontend/src/app/routes.ts`; `ESTUDIO_TT/B_sistema/B4` §2.

---

## T-15 · Cambios del sistema respecto al diseño de TT1

| Componente | Diseño de TT1 | Sistema final | Por qué |
|---|---|---|---|
| Actualización | Script aparte con cron, incremental, 7 pasos, métricas semanales y mensuales | Dentro de la API (APScheduler), recalcula ~3 años, métricas de 30/60/90 días | Un solo servicio; sin cron en el plan gratuito; todo sale del modelo vigente |
| Base de datos | PostgreSQL, 9 tablas + 1 desnormalizada, JSONB | SQLite, 4 tablas | Un solo escritor; base reconstruible; despliegue gratuito; compatible con PostgreSQL |
| Variables guardadas | `features_daily` (46) | No se guardan | Se recalculan en menos de un segundo |
| API | 6–7 GET + 5 POST de carga | 9 GET + `POST /admin/refresh`; POST de carga desactivados | El ETL ya no escribe por la API; evitar datos que no salen del modelo |
| Rutas | `/api/summary`, `/api/signals`, `/api/equity`… y `/stocks…` | `/stocks…`, `/metrics`, `/model`, `/market-status`, `/health` | Un solo juego de rutas |
| Interfaz | 3 niveles, matriz de confusión, pastel, consulta cada hora | 7 pantallas, curva de $1,000, seguridad en palabras, sin consulta periódica | Usuario sin contexto; el dato cambia una vez al día |
| Despliegue | Local (3 puertos) | Render (Docker + sitio estático) | Era trabajo futuro de TT1 |
| Modelo | "Pendiente" | `LR-v8-interactions-holdw090` | Resultado de la comparación |
| Pruebas | Manuales | 24 automáticas + funcionales | |

Fuente: `ESTUDIO_TT/D_defensa/D1` §9; `B1` §4b; `B3` §4.

---

## T-16 · Reproducibilidad: scripts por etapa

| Etapa | Scripts | Resultados |
|---|---|---|
| Datos (todas) | `scripts_v1/01_build_raw_dataset.py` | `tesis_ml_stocks/01_raw_datasets/` (y `_2026/` con `observaciones_sinodal.py dataset2026`) |
| 1 (TT1) | `scripts_v1/02`–`08` | `tesis_ml_stocks/03_model_datasets`, `04_models` |
| 2 | `scripts_opt/opt_*.py`, `analisis_feature_selection.py`, `common_v2.py`, `common_v3.py`, ensambles | `RO/modelos_optimizados*/`, `RO/reportes/` |
| 3 (paper §7) | `scripts_opt/common_v4.py`, `train_all_v4.py`, `consolidar_v4.py`, `replicar_lr_v4.py`, `plots_paper.py` | `RO/v4/` |
| 4 (paper §8) | `scripts_opt/diag_deep.py`, `common_v5.py`, `run_v5.py`, `reporte_v5.py` | `RO/v5/` |
| 5 | `scripts_opt/via7_refinamiento.py`, `via8_dataset.py`, `via8_target_extendido.py`, `via8_combinado.py` | `RO/v7/`, `RO/v8/` |
| 6 | `scripts_opt/analisis_hold_global.py`, `ajuste_hold_rolling.py`, `ajuste_hold_2026.py`, `evaluar_produccion_2026.py`, `calibrar_niveles_confianza.py`, `verificar_ventana_redes.py`, `entrenar_produccion.py` | `RO/analisis_hold/`, `api/ml/artifacts/` |
| Respuesta a la sinodal | `scripts_opt/observaciones_sinodal.py` (`metricas`, `seleccion`, `multicolinealidad`, `ciega2026`, `exportar_web`) | `RO/observaciones_sinodal/` |
| Plataforma | `api/`, `Frontend/`, `render.yaml`, `docker-compose.yml` | Render |

Instantánea del código del paper: etiqueta de git `micai2026`. Manifiesto de
datos (filas, fechas y SHA-256) y versiones: material suplementario del
paper, sección S5. Dependencias: `scripts_opt/requirements.txt`,
`api/requirements.txt`.

---

## T-17 · Modelo global contra un modelo por acción (mismos días)

**Pie:** *Comparación pareada en 21 pares (7 acciones × 3 experimentos),
Etapa 4, prueba 2025. El modelo global y el de cada acción se evalúan sobre
exactamente los mismos días.*

| Modelo | F1 global | F1 por acción | Pares que gana el global | p (prueba de signo) |
|---|---:|---:|---:|---:|
| **LR** | **0.394** | 0.375 | **18 de 21** | **0.002** |
| XGBoost | 0.359 | 0.364 | 10 de 21 | 1.00 |
| LSTM | 0.334 | 0.314 | 16 de 21 | 0.027 |
| CNN 1D | 0.293 | 0.212 | 19 de 21 | < 0.001 |
| CNN-LSTM | 0.305 | 0.330 | 7 de 21 | 0.19 |

Los pares no son independientes (mismo año y mercado): los valores *p* son
optimistas. Fuente: `RO/analisis_hold/4a_global_vs_porticker_por_modelo.csv`.
Figura: `graficas/G07`.

---

## T-18 · Corrección del exceso de mantener (origen rodante 2019–2024)

**Pie:** *Ocho alternativas evaluadas sin usar 2025 ni 2026. Mantener real
promedio: 40 %. En negritas, la alternativa elegida.*

| Alternativa | F1 | Kappa | Sharpe | Mantener predicho |
|---|---:|---:|---:|---:|
| Pesos balanceados (modelo anterior) | 0.357 | 0.063 | +0.52 | 47 % |
| P(mantener) × 0.90 al decidir | 0.334 | 0.050 | +0.37 | 23 % |
| Proporción fija por año (40 %) | 0.337 | 0.062 | +0.58 | 45 % |
| Proporción móvil causal (63 días) | 0.365 | 0.061 | +0.42 | 43 % |
| Proporción móvil causal (252 días) | 0.367 | 0.070 | +0.51 | 41 % |
| Reentrenar con peso de mantener × 0.95 | 0.360 | 0.062 | +0.53 | 42 % |
| **Reentrenar con peso de mantener × 0.90** | **0.365** | **0.068** | **+0.54** | **36 %** |
| Reentrenar con peso × 0.85 | 0.360 | 0.062 | +0.46 | 30 % |
| Reentrenar con peso × 0.80 | 0.352 | 0.061 | +0.41 | 24 % |

*Nota. Entre los pesos de reentrenamiento, × 0.90 es el mejor en las tres
métricas. La proporción móvil de 252 días empata en F1 y kappa, pero tiene
menos Sharpe en 2019–2024, en 2025 (+0.81 contra +0.93) y en 2026 (+0.16
contra +0.29, Tabla T-19). La proporción fija de 40 % tiene el mayor Sharpe
en 2019–2024 (+0.58), pero un F1 de 0.337 y menos Sharpe en 2025 (+0.88
contra +0.93); se descartó porque el F1-macro es la métrica principal.*

Fuente: `RESULTADOS_OPTIMIZADOS/docs/ANALISIS_HOLD_Y_GLOBAL.md` §8.2;
`ESTUDIO_TT/A_modelo/A7` §4.3; `RO/analisis_hold/`.

---

## T-19 · Modelo de la plataforma en 2026 (enero–septiembre)

| Modelo | F1 | Kappa | Mantener (real 34.7 %) | Sharpe | Sharpe de portafolio |
|---|---:|---:|---:|---:|---:|
| Pesos balanceados (anterior) | 0.313 | 0.010 | 59.7 % | +0.38 | +0.71 |
| Proporción móvil causal | 0.350 | 0.027 | 37.0 % | +0.16 | +0.33 |
| **Peso × 0.90 (en producción)** | **0.354** | **0.035** | **39.7 %** | +0.29 | +0.60 |
| Comprar y mantener las 7 | | | | | +0.49 |

La mejora no es significativa (mejora el F1 en 4 de 6 años; Wilcoxon
p = 0.31). Fuente: `RO/analisis_hold/8_confirmacion_2026.csv`; `A7` §4.4.

---

## T-20 · Lo que aportaron las 15 interacciones

| Evaluación | Sin interacciones | Con interacciones |
|---|---:|---:|
| Prueba 2025 (año en que se decidió adoptarlas) | 0.390 | 0.413 |
| Validación 2024 | 0.326 | 0.325 |
| Origen rodante 2019–2024 (media de 6 años) | 0.354 | 0.357 |
| Sharpe medio en esos 6 años | +0.53 | +0.52 |

Se conservan en producción como **equivalentes**, no como mejora.
Fuente: `ESTUDIO_TT/A_modelo/A2` §11.

---

## T-21 · Niveles de seguridad de la recomendación

| Nivel | Probabilidad máxima del modelo | Aciertos (de cada 100) | Días |
|---|---|---:|---:|
| Nada segura | menor a 0.35 | 37 | ~30 % |
| Poco segura | 0.35 a 0.3664 | 38 | ~30 % |
| Medianamente segura | 0.3664 o más | 42 | ~40 % |
| *Azar* | | *33* | |

Calibrado con siete años evaluados sin haberlos visto (2019–2025); el nivel
alto supera al bajo en los siete años. No hay nivel «Segura» porque ningún
tramo acierta ni la mitad de las veces.
Fuente: `Frontend/src/app/format.ts`; `scripts_opt/calibrar_niveles_confianza.py`;
`ESTUDIO_TT/A_modelo/A4` §1.4.
