# A6 — Las seis etapas del proyecto

> **Resumen.** El modelo no se hizo de una vez: cada etapa respondió a algo
> que la anterior descubrió. **Etapa 1** es el reporte de TT1 (18 de mayo).
> **Etapa 2** exploró mejoras sin un protocolo limpio. **Etapa 3** igualó
> las condiciones (es la del paper, §7). **Etapa 4** hizo el protocolo
> estricto y da el **resultado principal** (paper §8). **Etapa 5** buscó más
> mejoras y casi nada ayudó. **Etapa 6** llevó el modelo a la plataforma y
> lo validó con datos de 2026.
>
> La vista general, las marcas de qué usa el paper y las equivalencias con
> los nombres viejos (v1 … v8) están en el
> [mapa de experimentos](../03_MAPA_DE_EXPERIMENTOS.md). Aquí está el
> detalle técnico de cada etapa.

---

## 1. Mapa rápido

| Etapa | Cuándo | Nombre viejo | Pregunta | Respuesta | Paper |
|---|---|---|---|---|---|
| **1. Línea base (TT1)** | Hasta 18 may | v1 | ¿Funciona el pipeline con 5 modelos? ¿Cuál gana? | XGBoost primero en F1, LR en Sharpe; pero cada modelo tenía distintas variables | No |
| **2. Primeras mejoras** | May–jun | optimización de mayo, "v0", v2, v3 | ¿Se puede mejorar cada modelo? | Algo, pero con selección hecha en la prueba | Solo §6 |
| **3. Comparación en igualdad** | Junio | v4 | ¿Cuál gana con las mismas condiciones? | LR primero (0.399 promedio); XGBoost cerca | §3–§7 |
| **4. Protocolo final** | Agosto | v5 (pasos V0–V6) | ¿Sobrevive a un protocolo estricto? | **Sí: LR significativamente mejor en A, B y C** | §8 |
| **5. Búsqueda de mejoras** | Fin de agosto | v7 ("Vía 7"), v8 ("Vía 8") | ¿Algo más ayuda sin cambiar el problema? | Solo 15 interacciones, y empatan en validación | No |
| **6. Plataforma y validación** | Sep–oct | "septiembre" | ¿Cómo se comporta el modelo real? | Ajuste de mantener; 2026: F1 0.354 | No |

---

## 2. Etapa 1 — Línea base (reporte de TT1)

Código: `scripts_v1/`. Entregado el 18 de mayo.

**Qué se hizo.** Ocho scripts en orden: construir el dataset (01), validar
y **seleccionar variables por modelo** (02), armar los conjuntos por modelo
(03), entrenar LR, XGBoost, LSTM, CNN-LSTM y CNN 1D (04–08). Tres
experimentos, **un modelo por acción como estrategia principal** (35 modelos
por experimento) y uno global como experimento adicional, ventana de 20 y 60
días para las redes.

**Configuración** (TT1 §3.4–§3.10):

- Variables filtradas por modelo con consenso en ≥ 3 de 7 acciones: LR con
  Pearson + VIF (8 / 4 / 3 variables en A / B / C), XGBoost con SHAP
  (24 / 23 / 25), LSTM con Spearman (25 / 10 / 3), CNN-LSTM y CNN 1D lo mismo
  que la LSTM + 5 canales OHLCV normalizados por ventana.
- LR one-vs-rest, L2, cuadrícula de C en {0.001…100}; XGBoost con cuadrícula;
  redes con arquitectura fija (ver [A5 §9](A5_REDES_NEURONALES.md#9-cómo-eran-las-redes-en-el-reporte-de-tt1)).
- Experimento A: entrenamiento 2014–2021, validación 2022–2023, **prueba
  2024–2025** (B y C ya probaban en 2025).

**Resultados del TT1** (por acción, mejor ventana según la prueba):

| Modelo | F1 promedio A / B / C | Promedio | Sharpe promedio Exp B |
|---|---|---:|---:|
| XGBoost | 0.378 / 0.371 / 0.359 | **0.369** | 0.270 |
| LR | 0.349 / 0.355 / 0.350 | 0.351 | **0.285** |
| CNN-LSTM | 0.321 / 0.342 / 0.356 | 0.340 | −0.430 |
| CNN 1D | 0.333 / 0.329 / 0.331 | 0.331 | −0.980 |
| LSTM | 0.302 / 0.297 / 0.272 | 0.291 | −0.400 |

Global contra por acción (Exp B): el global ya ganaba en 4 de 5 modelos
(LR 0.355 → 0.391).

**Conclusión del TT1:** no se rechaza H₀ (el DL no supera al ML); XGBoost
mejor en F1, LR mejor en Sharpe; pero —dice el propio TT1 (§5.6)— "la
asimetría en el número de características" impedía concluir sobre las
arquitecturas.

**Qué problemas tenía y en qué etapa se corrigieron:**

| Problema | Se corrigió en |
|---|---|
| Variables distintas por modelo | Etapa 3: las 61 para todos |
| Experimento A con otra prueba | Etapa 3: los tres prueban en 2025 |
| Ventana de las redes elegida con la prueba | Etapa 4 |
| Redes sin búsqueda de hiperparámetros | Etapa 4: Optuna para los cinco |
| Paro temprano que devolvía la época 1–2 | Etapa 4 (diagnosticado el 14 de agosto) |

**Qué quedó vigente.** `01_build_raw_dataset.py` sigue siendo la fuente de
verdad de las 61 variables y la etiqueta, y se copió idéntico a la API.

Comparación completa TT1 → TT2: [D1](../D_defensa/D1_TT1_VS_TT2.md).

---

## 3. Etapa 2 — Primeras mejoras (mayo–junio)

Con los datos y las particiones de TT1 se buscó subir el resultado de cada
modelo (`RESULTADOS_OPTIMIZADOS/docs/GUIA_PROGRESO.md`).

### 3.1 Optimización por modelo

Se probaron configuraciones por modelo (LR con distintas C, penalizaciones y
escaladores; LSTM apilada y bidireccional, etc.). La mejor fue una LR
*elasticnet* con las 61 variables: **F1 0.417, Sharpe 1.25 en el Exp B
global**. Esa cifra es **[NO CITAR]**: la configuración se eligió con la
prueba. Sirvió para la plataforma hasta agosto, no como resultado.

### 3.2 Preselección de variables contra usar las 61 · [PAPER §6]

En TT1 la selección por modelo **era el método**. Aquí se preguntó si de
verdad ayudaba: se comparó cada modelo con su filtro contra el mismo modelo
con las 61 variables:

| Modelo | Filtro | Δ F1 (todas − filtradas) en A / B / C |
|---|---|---|
| LR | Pearson + VIF (quedan 3–8) | +0.024 / +0.026 / +0.021 |
| XGBoost | SHAP top-N (23–25) | +0.009 / +0.021 / +0.022 |
| LSTM | Spearman (3–25) | +0.039 / +0.036 / −0.006 |
| CNN 1D | Spearman | +0.035 / −0.025 / +0.011 |
| CNN-LSTM | Spearman | −0.011 / +0.020 / −0.026 |

**En 11 de 15 casos usar todas es mejor.** La regularización del propio
modelo selecciona mejor que un filtro externo, que mira cada variable por
separado y no ve combinaciones.

- *Pearson:* correlación lineal de cada variable con la etiqueta.
- *VIF (factor de inflación de la varianza):* qué tanto una variable se
  explica con las demás (`1/(1−R²)`); alto = redundante.
- *Spearman:* correlación por rangos (capta relaciones monótonas no
  lineales).
- *SHAP:* cuánto aporta cada variable a las predicciones de un modelo de
  árboles (teoría de juegos).

**Cuidado:** esta tabla salió de la Etapa 2 (Experimento A con la prueba de
TT1 y mejor configuración elegida con la prueba). La conclusión se confirmó
después con el protocolo limpio (ver el punto 1 de la sección 8 del
[mapa](../03_MAPA_DE_EXPERIMENTOS.md#8-puntos-a-cuidar-para-la-estrategia-de-defensa)).

### 3.3 Más variables y otras ideas (todas descartadas)

| Idea | Resultado |
|---|---|
| 181 variables (z-scores, rezagos, interacciones) + calibración de umbrales por clase | F1 0.375: más variables = sobreajuste |
| 94 variables (curva de tasas, dólar, oro, petróleo, sectores XLK/XLF/XLY/XLE) | Sin mejora; primera evidencia de que el límite no estaba en las variables |
| LightGBM | 0.402: similar a XGBoost, sin ventaja |
| Stacking (una LR que combina a los demás) | 0.358: el meta-modelo se sobreajusta |
| Voto con pesos optimizados | 0.331: los pesos de 2024 no sirven en 2025 |
| Mezcla LR + XGBoost | 0.390: peor que la LR sola |
| Filtro por confianza de la LR | 0.412: igual que la LR sola |

**Qué dejó la Etapa 2:** dar las 61 variables a todos, la sospecha de un
techo cerca de 0.40 y la necesidad de un protocolo donde nada se decida con
la prueba.

---

## 4. Etapa 3 — Comparación en igualdad de condiciones (junio) · [PAPER §3–§7]

**Cambios clave:** las 61 variables para los cinco modelos; los tres
experimentos comparten la prueba 2025 y solo varía el entrenamiento (10, 6,
4 años). 120 corridas.

**Configuración:** LR elasticnet (cuadrícula de C), XGBoost con Optuna
(20–40 intentos), redes con arquitectura fija y cuadrícula chica (ver
[A5](A5_REDES_NEURONALES.md)).

**Resultados (F1-macro global, prueba 2025):**

| Modelo | A | B | C | Promedio |
|---|---:|---:|---:|---:|
| **LR** | **0.411** | 0.385 | **0.401** | **0.399** |
| XGBoost | 0.396 | **0.386** | 0.373 | 0.385 |
| CNN-LSTM | 0.376 | 0.384 | 0.371 | 0.377 |
| LSTM | 0.389 | 0.370 | 0.370 | 0.376 |
| CNN 1D | 0.361 | 0.343 | 0.373 | 0.359 |

Sharpe de la LR en B: +0.76. Es lo que reporta el paper en su §7.

**Problemas encontrados después** (diagnóstico del 14 de agosto): época
restaurada 1–2, ventana de las redes elegida con la prueba, reentrenamiento
solo para los clásicos, distinto número de filas por modelo. Detalle en
[A5 §3.4](A5_REDES_NEURONALES.md#34-lo-que-el-diagnóstico-encontró-14-de-agosto).

---

## 5. Etapa 4 — Protocolo final (agosto) · [PAPER §8] · resultado principal

**El protocolo:** las decisiones se toman en 2024 (modo *dev*:
entrenamiento 2018–2022, época elegida en 2023) y la prueba 2025 se evalúa
una sola vez (modo *final*). Detalle en [A3](A3_PROTOCOLO_Y_METRICAS.md).

| Paso | Qué hizo | Resultado | Paper |
|---|---|---|---|
| 4.1 Replicación | Reimplementar el pipeline y reproducir la Etapa 3 | 18/18 celdas idénticas | §8 |
| 4.2 Decisiones de protocolo | Torneo de 6 decisiones en 2024 | Solo el criterio de época por F1 ayuda (a la LSTM, +0.059) | §8 |
| 4.3 Optuna para las redes | 80 intentos, 17–20 hiperparámetros | Ganadoras en [A5](A5_REDES_NEURONALES.md) | §8 |
| 4.4 Optuna para LR y XGBoost | 150 intentos | LR: L2, C = 0.000165, RobustScaler | §8 |
| 4.5 Más variables (93) | Contexto de mercado ampliado | No ayuda → descartado | No |
| 4.6 Costos de transacción | 5 y 10 pb; umbral económico | LR con 10 pb: Sharpe +0.62 | No |
| 4.7 Intervalos y año por año | Bootstrap por bloques; prueba en 2020–2025 | LR significativamente mejor; en 6 años ≈ XGBoost | IC de B: §8 |

**Resultados (F1-macro global, prueba 2025):**

| Modelo | A | B | C |
|---|---:|---:|---:|
| **LR** | **0.406** | **0.404** | **0.400** |
| XGBoost | 0.359 | 0.359 | 0.362 |
| LSTM | 0.373 | 0.369 | 0.317 |
| CNN-LSTM | 0.245 | 0.372 | 0.338 |
| CNN 1D | 0.263 | 0.359 | 0.294 |

La LR es significativamente mejor que cada uno de los otros cuatro en los
tres experimentos. Detalle del Experimento B:

| Modelo | F1 | IC 95 % | Sharpe | Win rate | Máx. drawdown |
|---|---:|---|---:|---:|---:|
| **LR** | **0.404** | [0.379, 0.428] | **+0.89** | 52.0 % | −45 % |
| CNN-LSTM | 0.372 | [0.346, 0.395] | −0.07 | 48.4 % | −62 % |
| LSTM | 0.369 | [0.341, 0.395] | −0.35 | 49.0 % | −68 % |
| XGBoost | 0.359 | [0.334, 0.381] | +0.46 | 49.1 % | −50 % |
| CNN 1D | 0.359 | [0.332, 0.386] | −0.46 | 48.4 % | −73 % |

Prueba año por año (2020–2025) y su lectura: [A7 §3](A7_RESULTADOS_Y_LIMITES.md#3-walk-forward-20202025-la-evidencia-más-amplia).

---

## 6. Etapa 5 — Búsqueda de mejoras (fin de agosto)

Sobre el protocolo de la Etapa 4, **sin cambiar el problema**
(`docs/VIA7_REFINAMIENTO.md`, `docs/VIA8_DATASET.md`).

### 6.1 Ajustes al modelo ya entrenado

| Técnica | Qué es | Resultado |
|---|---|---|
| Calibración isotónica | Ajustar las probabilidades con una función monótona aprendida en validación | XGBoost +0.012 F1 / +0.13 Sharpe; LR −0.05; redes −0.06 |
| Umbral económico de mantener | Mover el umbral para maximizar ganancia | Sube el Sharpe, se derrumba el F1 |
| Mezcla LR + XGBoost por Sharpe | Promedio ponderado de probabilidades | Peor que la LR sola |
| Mezcla de los 5 (por F1 o Sharpe) | Pesos optimizados en 2024 | Peor que la LR sola |
| SWA | Promediar los pesos de las últimas épocas de una red | Mejora el Sharpe de la LSTM, no su F1 |
| Ponderar por recencia | Dar más peso a los datos recientes | LR: lo mejor es no ponderar |

### 6.2 Variables nuevas

| Técnica | Resultado con la LR | Decisión |
|---|---|---|
| Rezagos de las 10 mejores variables | −0.004 | Descartada |
| Variables entre acciones (beta, correlación, ranking) | +0.003 (marginal) | Descartada |
| Multi-escala (5 y 20 días) | −0.002 | Descartada |
| **15 interacciones** | +0.023 F1 en 2025; en 2019–2024 empatan (0.357 contra 0.354) | **Adoptadas** en la plataforma |

Las interacciones se propusieron viendo 2025; por eso se validaron después
en 2019–2024 sin ver 2025 (ver
[A2 §11](A2_VARIABLES.md#11-las-15-interacciones-vía-8-en-producción)). Los
resultados de A, B y C de la Etapa 4 son **sin** interacciones.

### 6.3 Cambiar la etiqueta · [FUERA]

Se probaron 30 combinaciones de horizonte (1 a 10 días) y percentiles. A
5–7 días con 25/75 la LR llega a F1 ≈ 0.43 y Sharpe ≈ +1.5, pero eso **ya no
es una señal diaria**: es otro problema. Queda como trabajo futuro y no se
reporta como resultado del TT.

---

## 7. Etapa 6 — Modelo de la plataforma y validación (septiembre–octubre)

Sin cambiar el problema, se midió (`docs/ANALISIS_HOLD_Y_GLOBAL.md`):

1. **Por qué tanto mantener:** voto dividido + régimen del VIX.
2. **Etiqueta 40/60 en vez de 30/70:** no corrige el exceso y empeora.
3. **Global contra por acción** sobre los mismos días: gana o empata el
   global en los 5 modelos.
4. **Prueba año por año** de la Etapa 4, que no se había analizado: ningún
   modelo pasa de 0.394.
5. **2026 fuera de muestra:** F1 0.313, κ 0.010 con el modelo de entonces.
6. **Ajuste:** reentrenar con peso de mantener × 0.90, elegido con
   2019–2024 por origen rodante. Sustituye al factor fijo sobre la
   probabilidad de mantener que se usaba desde julio (estaba ajustado a
   2024). En 2026: F1 0.354, κ 0.035, mantener 40 % (real 35 %).
7. **Niveles de seguridad** de la plataforma, calibrados con origen rodante.
8. **Ventana de las redes:** termina un día antes que la de la LR; cuesta
   ≈ 0.007 de F1 y no cambia el orden.

Además se auditó y corrigió la plataforma (métricas mal calculadas; ver
[B2](../B_sistema/B2_API.md)).

---

## 8. Qué se mantuvo y qué cambió a lo largo de todo

| Se mantuvo desde la Etapa 1 (TT1) | Cambió |
|---|---|
| Las 7 acciones, el periodo y Yahoo Finance | Exp A probaba en 2024–2025 → los tres prueban en 2025 (Etapa 3) |
| Las 61 variables calculadas | Cada modelo con su filtro → las 61 para todos (Etapa 3); 76 en la plataforma (+15 interacciones, Etapa 5) |
| La etiqueta 30/70 a un día | — (otras se probaron y quedaron fuera del planteamiento) |
| Los 5 modelos y CRISP-DM | Búsqueda: cuadrícula y redes fijas → Optuna para los cinco (Etapa 4) |
| F1-macro + métricas económicas | Se agregaron kappa, intervalos, permutación, año por año, costos |
| Global y por acción se entrenan | Principal por acción (Etapa 1) → **principal global** (Etapa 3) |
| | LR one-vs-rest L2 (Etapa 1) → elasticnet multinomial (Etapas 2–3) → L2 C 0.000165 (Etapa 4) → + interacciones (Etapa 5) → + peso de mantener 0.90 (Etapa 6) |

## 9. ¿Por qué tantas etapas?

Porque es investigación, no un plan lineal: cada etapa respondió a algo que
la anterior descubrió (comparaciones disparejas, errores de protocolo,
sospecha de sobreajuste a un año). Que la conclusión principal —los
clásicos regularizados igualan o superan a las redes— se mantenga en las
etapas 3 y 4, en la prueba año por año y en 2026 es justamente lo que la
hace creíble.

---

## Preguntas de este tema

Están desarrolladas en [D2](../D_defensa/D2_PREGUNTAS_GENERALES.md) y
[D5](../D_defensa/D5_PREGUNTAS_ESTADISTICA.md).
