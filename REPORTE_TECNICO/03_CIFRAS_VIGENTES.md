# 03 — Cifras vigentes (y las que no se citan)

> Toda cifra que vaya al documento debe estar aquí o en el archivo que se
> indica. Rutas relativas a la raíz del repositorio.
> `RO/` = `RESULTADOS_OPTIMIZADOS/`.
>
> Decimales: F1, kappa, AUC y exactitudes con 3 decimales; Sharpe con 2
> (o 3 cuando se copie de una tabla del paper); porcentajes con 1.

---

## 1. Datos

| Cifra | Qué es | Fuente |
|---|---|---|
| 7 | Acciones: AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA | `scripts_v1/01_build_raw_dataset.py` |
| 2013-01-01 | Inicio de la descarga (calentamiento de indicadores) | `DOWNLOAD_START` en el mismo script |
| 2013-12-31 a 2025-12-29 | Periodo con todas las variables completas | paper §3.1; `ESTUDIO_TT/A_modelo/A1` |
| 3 017 días por acción; 21 119 filas día-acción | Tamaño del dataset de desarrollo | A1 §3 |
| 2026-01-02 a 2026-10-22 | Datos de validación ciega (no usados en ninguna decisión) | `tesis_ml_stocks/01_raw_datasets_2026/` |
| 30 / 40 / 30 % | Proporción de VENDER / MANTENER / COMPRAR en 2014–2025 | paper §3.4 |
| 29.6 / 42.2 / 28.3 % | La misma proporción en 2025 (año de prueba) | paper §3.4 |
| 248 días hábiles; **1 736 filas** | Prueba 2025 por acción y total (7 × 248) | `RO/v5/resultados_finales.csv` (`n_eval`) |
| 1 421 filas | Prueba ciega 2026 (7 acciones, 2 ene–22 oct) | `RO/observaciones_sinodal/4_ciega2026.csv` |
| +24.2 %, volatilidad 39.1 %, caída máx. −33.0 %, VIX medio 19.0 | 2025 como año de prueba (no es un año "fácil") | paper §3.4 |

## 2. Características

| Cifra | Qué es | Fuente |
|---|---|---|
| **61** | Características base, 9 familias: retornos 5, momentum 4, medias móviles 9, volatilidad 8, osciladores 9, volumen 8, velas 7, calendario 5, mercado 6 | A2; Tabla 4 del reporte |
| **15** | Interacciones (productos de pares), solo en producción | `api/ml/artifacts/interaction_pairs.json` |
| **76** | Total en producción | A2 |
| 26 / 76 | Pares con \|r\| > 0.9 / > 0.8 (entrenamiento Exp B) | `RO/observaciones_sinodal/3_multicolinealidad_diagnostico.json` |
| 26 / 10 | Variables con VIF > 10 / > 100; VIF máximo 1 327.8 | ídem |
| 45 | Variables que quedan con un filtro iterativo VIF ≤ 10 | ídem |

## 3. Etapa 1 — línea base de TT1 (solo como antecedente)

Por acción, lookback de las redes elegido con la prueba, variables distintas
por modelo, Exp A con prueba 2024–2025. **No es comparable** con lo demás.

| Modelo | F1 promedio A/B/C | Sharpe promedio Exp B |
|---|---:|---:|
| XGBoost | 0.369 | 0.270 |
| LR | 0.351 | 0.285 |
| CNN-LSTM | 0.340 | −0.430 |
| CNN 1D | 0.331 | −0.980 |
| LSTM | 0.291 | −0.400 |

Fuente: Tablas 18 y 23 del reporte actual; `ESTUDIO_TT/D_defensa/D1` §8.

## 4. Etapa 2 — primeras mejoras

| Cifra | Qué es | Fuente |
|---|---|---|
| **11 de 15** | Combinaciones (5 modelos × 3 experimentos) en que usar las 61 variables supera a la preselección estadística (Pearson+VIF, SHAP, Spearman) | paper §6, Tabla 3 del paper |
| hasta +0.039 | Mayor ventaja de usar las 61 (LSTM, Exp A) | ídem |
| 94 variables, −0.010 | Agregar contexto macro y sectorial: cambio medio de F1, mejora solo en 6 de 15 | §6.6.1 del reporte; `RO/v3/` |

## 5. Etapa 3 — comparación en igualdad (paper §7)

F1-macro, prueba 2025, modelo **global**, lookback de las redes elegido con
la prueba (el paper lo declara):

| Modelo | A | B | C | Promedio |
|---|---:|---:|---:|---:|
| **LR** | **0.411** | 0.385 | **0.401** | **0.399** |
| XGBoost | 0.396 | **0.386** | 0.373 | 0.385 |
| LSTM | 0.389 | 0.370 | 0.370 | 0.376 |
| CNN-LSTM | 0.376 | 0.384 | 0.371 | 0.377 |
| CNN 1D | 0.361 | 0.343 | 0.373 | 0.359 |

Por acción (promedio de 7): LR 0.411 / 0.392 / 0.359 (prom. 0.387);
XGBoost 0.376 / 0.370 / 0.352; CNN-LSTM 0.368 / 0.342 / 0.356; LSTM 0.314 /
0.353 / 0.326; CNN 0.378 / 0.332 / 0.280.

Exp B global, economía: LR profit factor 1.210 y Sharpe **+0.755**; XGBoost
1.083 / +0.345; CNN-LSTM 1.041 / +0.147; LSTM 1.120 / +0.433; CNN 1.031 /
+0.121.

La acción explica el 15.5 % de la variación del Sharpe y el modelo el 3.4 %
(≈ 4.5 veces); experimento 7.0 %; interacción y ruido 74.1 %.

Fuente: `paper_review/paper.tex` (Tablas 4–6, §7.3); `RO/v4/resultados_v4.csv`.

## 6. Etapa 4 — protocolo final (**resultado principal**)

### 6.1 F1-macro con intervalos (prueba 2025, global, mismas 1 736 filas)

| Modelo | A | B | C |
|---|---|---|---|
| **LR** | **0.406** [0.382, 0.428] | **0.404** [0.379, 0.428] | **0.401** [0.376, 0.424] |
| XGBoost | 0.359 [0.334, 0.383] | 0.359 [0.334, 0.381] | 0.362 [0.339, 0.387] |
| LSTM | 0.373 [0.345, 0.402] | 0.369 [0.341, 0.395] | 0.317 [0.285, 0.346] |
| CNN-LSTM | 0.245 [0.230, 0.261] | 0.372 [0.346, 0.395] | 0.338 [0.307, 0.369] |
| CNN 1D | 0.263 [0.246, 0.279] | 0.359 [0.332, 0.386] | 0.294 [0.260, 0.327] |

Intervalo: bootstrap por bloques de 20 días, 2 000 réplicas, percentiles
2.5–97.5. **La LR es significativamente mejor que cada uno de los otros
cuatro en A, B y C** (todas las diferencias pareadas excluyen el cero).
Diferencias en B: +0.045 sobre XGBoost, +0.035 sobre LSTM, +0.031 sobre
CNN-LSTM, +0.045 sobre CNN 1D. Entre los otros cuatro, en B ninguna
diferencia es significativa.

Fuente: `RO/v5/v6_ic_{A,B,C}_v1.csv`, `RO/v5/v6_pares_{A,B,C}_v1.csv`.

> Nota de redondeo: la LR de C vale 0.4005 (así está guardada); en los
> documentos de estudio aparece como 0.400 o 0.401. Usar **0.401**
> (redondeo convencional) en todo el reporte y no mezclar.

### 6.2 Ocho métricas, Exp B (todas sobre las mismas filas)

| Modelo | F1-macro | Exactitud | Exactitud balanceada | Kappa | AUC macro | Log-loss | Sharpe 0 pb | Sharpe 10 pb | Rotación |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **LR** | **0.404** | **0.435** | **0.407** | **0.120** | **0.593** | **1.076** | **+0.89** | **+0.62** | 0.38 |
| CNN-LSTM | 0.372 | 0.386 | 0.374 | 0.069 | 0.573 | 1.091 | −0.07 | −0.20 | 0.18 |
| LSTM | 0.369 | 0.381 | 0.374 | 0.065 | 0.551 | 1.093 | −0.35 | −0.41 | 0.09 |
| CNN 1D | 0.359 | 0.377 | 0.369 | 0.060 | 0.568 | 1.094 | −0.46 | −0.53 | 0.11 |
| XGBoost | 0.359 | 0.362 | 0.364 | 0.046 | 0.539 | 1.217 | +0.46 | +0.01 | 0.65 |

La LR es la mejor en las ocho métricas en A, B y C (A y C en el mismo
archivo). Fuente: `RO/observaciones_sinodal/1_metricas_panel.csv`.

### 6.3 Otros datos de la Etapa 4

| Cifra | Qué es | Fuente |
|---|---|---|
| 18 de 18 | Celdas de la Etapa 3 que el código nuevo reproduce idénticas | `RO/v5/g0_replicacion.csv` |
| +0.059 | Lo que gana la LSTM al elegir la época por F1 en vez de pérdida | paper §8 |
| ln 3 ≈ 1.0986 | Pérdida de validación de la que ninguna red baja | paper §8; A5 §3.4 |
| 592 131 → 10 275 | Parámetros de la LSTM sin cambio de resultado | A5 §3.4 |
| −0.024 a −0.047 | Lo que pierden las redes si se reentrenan con validación | paper §8 |
| 150 / 150 / 80 / 80 / 80 | Intentos de Optuna: LR, XGBoost, LSTM, CNN, CNN-LSTM | A3 §4.2 |
| 5 / 9 / 17 / 20 / 19 | Hiperparámetros buscados (mismo orden) | ídem |
| 54 / 53 / 74 | Intentos terminados de LSTM / CNN / CNN-LSTM (el resto podados) | ídem |
| C = 0.000165, L2, RobustScaler | LR ganadora | `RO/v5/ganadores_clasicos.json` |
| 0.38 / 0.65 | Rotación media de LR / XGBoost | `1_metricas_panel.csv` |
| +0.76 / +0.62 | Sharpe de la LR en B con 5 / 10 pb | `RO/v5/resultados_finales.csv` |
| −45 % (B), −42 % (A), −44 % (C) | Peor caída de la simulación de la LR (sin costos) | ídem (`max_dd`) |
| 52 % / 1.27 | Win rate / profit factor de la LR en B | ídem |
| 20.7 / 51.7 / 27.5 % | Distribución de señales de la LR en B (COMPRAR / MANTENER / VENDER) | ídem |

## 7. Robustez en el tiempo

### 7.1 Prueba año por año 2020–2025 (entrenar 5 años, validar el anterior, probar el año)

| Modelo | Ajustes fijos de la Etapa 3 (no vieron ningún año) | Ajustes elegidos con 2024 (Etapa 4) |
|---|---:|---:|
| LR | **0.360** (gana 3 de 6 años, lugar medio 1.83) | 0.350 |
| XGBoost | 0.356 | **0.356** |
| CNN 1D | 0.338 | 0.292 |
| LSTM | 0.331 | 0.314 |
| CNN-LSTM | 0.326 | 0.328 (5 años) |

- Seis años juntos: LR − XGBoost **+0.003** (no significativa); LR − cada
  red +0.017 a +0.026 (significativas).
- Ningún modelo pasa de **0.394** en ningún año (LR, 2025).
- Sharpe medio con 10 pb (ajustes fijos): LR +0.09, XGBoost −0.10, CNN −0.02,
  LSTM −0.50, CNN-LSTM −0.63.

Fuente: `RO/observaciones_sinodal/2_seleccion_resumen.csv`,
`2_lr_contra_cada_uno_6anios.csv`, `RO/v5/walkforward_v4.csv`.

### 7.2 Elegir el modelo con la validación de un año no funciona

Si cada año se eligiera el modelo con mejor F1 en validación, el F1 medio en
prueba sería **0.342** (ajustes fijos) o **0.344** (ajustes de 2024), peor
que quedarse siempre con la LR (0.360 / 0.350). La correlación entre el
ranking de validación y el de prueba va de −0.6 a +0.9 según el año.
Fuente: `2_eleccion_por_validacion.csv`.

### 7.3 Permutación

| Año | % de 500 permutaciones que superan al modelo | Lectura |
|---|---:|---|
| 2025 | 0.4 % | Hay señal |
| 2024 | 79 % | Ese año no hubo |

Permutación de las señales del modelo de la plataforma (misma cantidad de
cada señal, reasignadas al azar entre días). Fuente:
`RO/docs/ANALISIS_HOLD_Y_GLOBAL.md` §2.4 (`scripts_opt/analisis_hold_global.py`); A3 §8.

### 7.4 Prueba ciega 2026 de los cinco (ajustes congelados, entrenar 2020–2024, validar 2025)

| Modelo | F1-macro | Kappa | Sharpe 0 pb | Sharpe 10 pb | MANTENER predicho |
|---|---:|---:|---:|---:|---:|
| **LR** | **0.346** | 0.038 | +0.38 | +0.02 | 54 % |
| XGBoost | 0.343 | 0.036 | 0.00 | −0.49 | 55 % |
| LSTM | 0.331 | 0.040 | +0.72 | +0.65 | 24 % |
| CNN-LSTM | 0.318 | 0.017 | +0.16 | −0.01 | 19 % |
| CNN 1D | 0.304 | 0.032 | **+0.88** | **+0.82** | 9 % |

Diferencias de F1 de la LR: +0.003 (XGBoost), +0.015 (LSTM), +0.028
(CNN-LSTM) no significativas; +0.042 sobre la CNN 1D significativa.
Fuente: `4_ciega2026.csv`, `4_ciega2026_diferencias.csv`.

## 8. Etapa 5 — búsqueda de mejoras

| Prueba | Resultado | Fuente |
|---|---|---|
| Calibración isotónica | XGBoost 0.359 → 0.371 y Sharpe +0.46 → +0.60; LR 0.404 → 0.358; redes −0.06 | `RO/v7/`, A4 §2.5 |
| Umbral económico de MANTENER | LR Sharpe 0.89 → 1.18 pero F1 0.404 → 0.256 (MANTENER 95 %) | `RO/v7/` |
| Mezclas | 5 modelos por F1: 0.373 (Sharpe 0.04); LR+XGBoost por Sharpe: 0.359 (Sharpe 0.31); contra LR sola 0.404 / 0.89 | `RO/v7/` |
| SWA | LSTM Sharpe −0.35 → +0.14; F1 0.369 → 0.361 | `RO/v7/` |
| Rezagos / entre activos / multi-escala | −0.004 / +0.003 / −0.002 | `RO/v8/` |
| **15 interacciones** | 2025: 0.390 → 0.413 (donde se decidió adoptarlas); validación 2024: 0.326 → 0.325; origen rodante 2019–2024: 0.354 → 0.357 → **equivalentes** | A2 §11 |

## 9. Etapa 6 — modelo de la plataforma

| Cifra | Qué es | Fuente |
|---|---|---|
| **18 de 21**, p = 0.002 | Pares (acción × experimento) en que la LR global gana a la LR por acción sobre los mismos días | `RO/analisis_hold/4a_global_vs_porticker_por_modelo.csv` |
| 0.394 / 0.375 | F1 de la LR global / por acción en esos pares | ídem |
| 40 % / 57–64 % | MANTENER real / predicho por el modelo "balanced" (2024–2025) | A7 §4.1 |
| 100 % | Días en que dice MANTENER con P(COMPRAR) + P(VENDER) > P(MANTENER) ("voto dividido") | A7 §4.2 |
| × 0.90 | Peso de MANTENER al entrenar, elegido con origen rodante 2019–2024 | `scripts_opt/ajuste_hold_rolling.py` |
| 0.365 / 0.068 / +0.54 | F1 / kappa / Sharpe medio 2019–2024 con ese peso | A7 §4.3 |
| **0.354**, κ 0.035, Sharpe +0.29 | Modelo de la plataforma en 2026 (enero–septiembre) | `RO/analisis_hold/8_confirmacion_2026.csv` |
| 0.313, κ 0.010 | Modelo anterior ("balanced") en el mismo periodo | ídem |
| Wilcoxon p = 0.31 | El ajuste no es una mejora significativa (mejora en 4 de 6 años) | A7 §4.4 |
| 37 / 38 / 42 de cada 100 | Aciertos de los niveles «Nada», «Poco» y «Medianamente segura» (azar 33) | `Frontend/src/app/format.ts`; `calibrar_niveles_confianza.py` |
| 0.4125 / 0.4086 | Escalador global contra por acción en 2025 (diferencia despreciable) | A2 §13 |
| ≈ 0.007 | Lo que cuesta que la ventana de las redes termine en *t − 1* (medido con la LR) | `scripts_opt/verificar_ventana_redes.py` |

> **Dos cifras de 2026 que no hay que confundir:** **0.354** es el modelo de
> la plataforma (LR + interacciones + peso × 0.90, entrenado con 2018–2025)
> en enero–septiembre. **0.346** es la LR de la prueba ciega de los cinco
> (sin interacciones, entrenada con 2020–2024) en enero–22 de octubre. Son
> modelos y periodos distintos.

## 10. Multicolinealidad (respuesta a la sinodal)

61 variables contra filtro VIF ≤ 10 (calculado solo con el entrenamiento),
F1-macro 2025:

| Modelo | A | B | C |
|---|---|---|---|
| LR | 0.406 vs 0.404 | 0.404 vs 0.409 | 0.401 vs 0.398 |
| XGBoost | 0.359 vs 0.357 | 0.359 vs 0.366 | 0.362 vs 0.367 |
| LSTM | 0.373 vs 0.339 | 0.369 vs 0.360 | 0.317 vs 0.319 |
| CNN-LSTM | 0.245 vs 0.206 | 0.372 vs 0.357 | 0.338 vs 0.322 |
| CNN 1D | 0.263 vs 0.240 | 0.359 vs 0.345 | 0.294 vs 0.279 |

Las 61 son mejores en **11 de 15**; perjudica a las redes en 8 de 9; a los
clásicos les da igual (±0.006). Fuente:
`RO/observaciones_sinodal/3_multicolinealidad_resumen.csv`.

## 11. Referencias de azar

| Estrategia trivial (2025) | F1-macro |
|---|---:|
| Decir siempre MANTENER | ≈ 0.20 |
| Al azar con las proporciones reales | ≈ 0.33 |

---

## 12. **No citar**

| Cifra | Por qué no |
|---|---|
| **F1 0.417 / Sharpe 1.25** | Etapa 2: la configuración se eligió mirando la prueba y el Exp A tenía otra prueba. Era la cifra de la LR que corrió en la plataforma hasta agosto |
| F1 ≈ 0.43 y Sharpe ≈ 1.1–1.5 a 5–7 días | Otro problema (ya no es señal diaria); trabajo futuro |
| Percentiles 25/75: 0.411 | Cambia la definición de las clases; no comparable |
| "+0.023 de F1 por las interacciones" como mejora | Solo aparece en el año en que se decidió adoptarlas |
| CNN 1D en META, Exp C: Sharpe 3.640 / +223.6 % | Mejor caso entre 105 combinaciones de TT1, con lookback elegido en la prueba |
| F1 promedio de NVDA 0.269 / TSLA 0.269 / NVDA 0.284 | No coinciden con las Tablas 15–17 (C-27) |
| Tiempos del ETL "~30 s, ~20 s…" (Tabla 11) | No se midieron así; el sistema actual recalcula todo en segundos |
| "< 50 ms" de respuesta | No hay medición que lo respalde; si se quiere, medirlo con la API desplegada |
| Versiones de §6.1 (scikit-learn 1.8.0, PyTorch 2.11) | No coinciden con las registradas (ver S-09) |
