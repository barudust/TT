# A6 — Evolución del modelo: de v1 a v8

> **Resumen.** El modelo no se hizo de una vez. Cada versión respondió a
> algo que se descubrió en la anterior: v1 es lo que se entregó en el
> reporte de TT1 (18 de mayo); v2–v3 armaron el pipeline de optimización y
> probaron más variables; v4 hizo la comparación justa (es la del paper);
> v5 corrigió el protocolo y agregó búsqueda simétrica, intervalos de
> confianza y walk-forward; v7 y v8 agotaron las mejoras razonables; y en
> septiembre se analizó el modelo en producción y se ajustó el exceso de
> MANTENER. No existe "v6" como versión.

---

## 1. Mapa rápido

| Versión | Cuándo | Pregunta que respondía | Respuesta |
|---|---|---|---|
| **v1 = TT1** | Hasta el 18 de mayo | ¿Funciona el pipeline con 5 modelos? ¿Cuál gana? | XGBoost primero en F1, LR en Sharpe; pero cada modelo tenía distintas variables y el Exp A otra prueba |
| v2 | Mayo | ¿Ayuda calibrar los umbrales de decisión por clase? | Mejora inestable; no |
| v3 | Mayo–junio | ¿Más variables (94) mejoran? | No; sobreajuste |
| **v4** | Junio (aprox.) | ¿Cuál gana con una comparación justa? | LR y XGBoost empatan arriba; **es la del paper** |
| **v5** | Agosto | ¿El resultado sobrevive a un protocolo estricto? | **Sí: LR significativamente mejor en 2025**; en 6 años LR ≈ XGBoost |
| v7 | 26 ago | ¿Algún refinamiento posterior ayuda? | Solo calibración isotónica a XGBoost |
| v8 | 26 ago | ¿Se puede mejorar el dataset? | Interacciones "ayudan" en 2025 pero empatan en validación |
| Sep. | 30 sep | ¿Cómo se comporta en producción y por qué tanto MANTENER? | Voto dividido; ajuste de peso × 0.90 |

---

## 2. v1 — El reporte de TT1 (`scripts_v1/`, entregado el 18 de mayo)

**Qué se hizo.** Ocho scripts en orden: construir el dataset (01), validar
y **seleccionar variables por modelo** (02), armar los conjuntos por modelo
(03), entrenar LR, XGBoost, LSTM, CNN-LSTM y CNN 1D (04–08). Tres
experimentos, **un modelo por acción como estrategia principal** (35 modelos
por experimento) y uno global como experimento adicional, lookback 20 y 60.

**Configuración** (TT1 §3.4–§3.10):

- Variables filtradas por modelo con consenso en ≥ 3 de 7 acciones: LR con
  Pearson + VIF (8 / 4 / 3 variables en A / B / C), XGBoost con SHAP
  (24 / 23 / 25), LSTM con Spearman (25 / 10 / 3), CNN-LSTM y CNN 1D lo mismo
  que la LSTM + 5 canales OHLCV normalizados por ventana.
- LR one-vs-rest, L2, cuadrícula de C en {0.001…100}; XGBoost con cuadrícula;
  redes con arquitectura fija (ver [A5 §9](A5_REDES_NEURONALES.md#9-cómo-eran-las-redes-en-el-reporte-de-tt1)).
- Exp A: entrenamiento 2014–2021, validación 2022–2023, **prueba 2024–2025**.

**Resultados del TT1** (por acción, mejor lookback según la prueba):

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

**Qué problemas tenía (y se corrigieron después):**

1. Variables distintas por modelo → desde v4, las 61 para todos.
2. Exp A con otra prueba → desde v4, los tres prueban en 2025.
3. Lookback de las redes elegido con la prueba → corregido en v5.
4. Redes sin búsqueda de hiperparámetros → Optuna en v5.
5. Paro temprano por pérdida que restauraba la época 1–2 → diagnosticado
   en agosto.

**Qué quedó vigente.** `01_build_raw_dataset.py` sigue siendo la fuente de
verdad de las 61 variables y la etiqueta, y se copió idéntico a la API.

**Cuidado:** una evaluación de mayo (`GUIA_PROGRESO.md`) reportaba F1 0.417
y Sharpe 1.25. Esas cifras **no son comparables** con v4/v5 (otro protocolo).
No citarlas como resultado.

Comparación completa TT1 → TT2: [D1](../D_defensa/D1_TT1_VS_TT2.md).

### Optimización por modelo (mayo, `GUIA_PROGRESO.md`)

Se probaron configuraciones por modelo (LR con distintas C y escaladores,
LSTM apilada y bidireccional, etc.). Conclusión de entonces: había un
"techo" alrededor de 0.40 que ninguna variante superaba de forma estable.

### Selección de variables: de método del TT1 a experimento del paper

En TT1 la selección por modelo **era el método**. Después se preguntó si
realmente ayudaba: se comparó cada modelo con su filtro contra el mismo
modelo con las 61 variables:

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

### Ensambles (v0)

Stacking (una LR que combina las probabilidades de los otros modelos):
igual que la LR sola. Promedio simple de los 5: ~0.38, peor que la LR. Mezcla
optimizada: ~90 % LR + 10 % XGBoost, es decir, la LR sola.

---

## 3. v2 — Calibrar el umbral por clase

Ajustar después del entrenamiento a partir de qué probabilidad se declara
cada clase. Mejora marginal y no estable entre experimentos. Se descartó.

## 4. v3 — 94 variables

Se agregaron 33 variables de contexto (curva de tasas, dólar, oro,
petróleo, sectores XLK/XLF/XLY/XLE). **Sin mejora**; los modelos se ajustan
más al ruido. Fue la primera evidencia de que el límite no estaba en las
variables.

## 5. v4 — La comparación justa (la del paper)

**Cambio clave:** los tres experimentos comparten la prueba 2025 y solo
varía el entrenamiento (10, 6, 4 años). 120 corridas.

**Configuración:** LR elasticnet (cuadrícula de C), XGBoost con Optuna
(20–40 intentos), redes con arquitectura fija y cuadrícula chica (ver
[A5](A5_REDES_NEURONALES.md)).

**Resultados (Exp B, global, 2025):**

| LR | XGBoost | LSTM | CNN | CNN-LSTM |
|---:|---:|---:|---:|---:|
| 0.385 | 0.386 | 0.370 | 0.343 | 0.384 |

Promedio de la LR en los tres experimentos: **0.399** (el más alto); Sharpe
de la LR en B: +0.76. Es lo que reporta el paper en su §7.

**Problemas encontrados después** (diagnóstico del 14 de agosto): época
restaurada 1–2, lookback elegido con la prueba, reentrenamiento solo para
los clásicos, distinto número de filas por modelo. Detalle en
[A5 §3.4](A5_REDES_NEURONALES.md#34-lo-que-el-diagnóstico-encontró-14-de-agosto).

## 6. v5 — Protocolo corregido (agosto)

Se planeó en siete sub-etapas (**V0–V6, con mayúscula, dentro de v5**):

| Sub-etapa | Qué hizo | Resultado |
|---|---|---|
| V0 | Reimplementar el pipeline y replicar v4 | 18/18 celdas idénticas |
| V1 | Torneo de 6 decisiones de protocolo | Solo el criterio de época por F1 ayuda (a la LSTM, +0.059) |
| V2 | Optuna para las 3 redes (80 intentos, 17–20 hiperparámetros) | Ganadoras en [A5](A5_REDES_NEURONALES.md) |
| V3 | Optuna para LR y XGBoost (150 intentos) | LR: L2, C = 0.000165, Robust |
| V4 | Dataset ampliado (93 variables) | No ayuda |
| V5 | Costos de transacción y umbral económico | LR con 10 pb: Sharpe +0.62 |
| V6 | Bootstrap por bloques y walk-forward | LR significativamente mejor en 2025; en 6 años ≈ XGBoost |

**Por eso "no existe v6":** V6 es una sub-etapa de v5. Después de v5 se
pasó a v7.

**Resultados (Exp B, global, 2025):**

| Modelo | F1 | IC 95 % | Sharpe | Win rate | Máx. drawdown |
|---|---:|---|---:|---:|---:|
| **LR** | **0.404** | [0.379, 0.428] | **+0.89** | 52.0 % | −45 % |
| CNN-LSTM | 0.372 | [0.346, 0.395] | −0.07 | 48.4 % | −62 % |
| LSTM | 0.369 | [0.341, 0.395] | −0.35 | 49.0 % | −68 % |
| XGBoost | 0.359 | [0.334, 0.381] | +0.46 | 49.1 % | −50 % |
| CNN 1D | 0.359 | [0.332, 0.386] | −0.46 | 48.4 % | −73 % |

## 7. v7 — Refinamiento posterior a Optuna (Vía 7)

Seis técnicas que no requieren cambiar los datos
(`docs/VIA7_REFINAMIENTO.md`):

| Técnica | Qué es | Resultado |
|---|---|---|
| Calibración isotónica | Ajustar las probabilidades con una función monótona aprendida en validación | XGBoost +0.012 F1 / +0.13 Sharpe (**única adopción**); LR −0.05; redes −0.06 |
| Umbral económico de MANTENER | Mover el umbral para maximizar ganancia | Sube el Sharpe, se derrumba el F1 |
| Mezcla LR + XGBoost por Sharpe | Promedio ponderado de probabilidades | Peor que la LR sola |
| Mezcla de los 5 (por F1 o Sharpe) | Pesos optimizados en 2024 | Peor que la LR sola (los pesos de 2024 no sirven en 2025) |
| SWA | Promediar los pesos de las últimas épocas de una red | Mejora el Sharpe de la LSTM, no su F1; nada en las otras |
| Ponderar por recencia | Dar más peso a los datos recientes | LR: lo mejor es no ponderar; XGBoost: baja el Sharpe |

## 8. v8 — Exploración del dataset (Vía 8)

Cinco técnicas (`docs/VIA8_DATASET.md`):

| Técnica | Resultado con la LR |
|---|---|
| Otros horizontes y percentiles (6 × 5 = 30 combinaciones) | Con 5–7 días y 25/75: F1 ~0.43, Sharpe ~+1.5. **Cambia el problema** |
| Rezagos de las 10 mejores variables | −0.004 |
| Variables entre activos (beta, correlación, ranking) | +0.003 (marginal) |
| Multi-escala (5 y 20 días) | −0.002 |
| **15 interacciones** | **+0.023 F1, +0.24 Sharpe en 2025** |

El modelo de producción se actualizó a **LR + 15 interacciones** (26 de
agosto). En septiembre se comprobó que esa mejora solo existe en 2025: en
validación 2024 y en origen rodante 2019–2024 empatan (ver
[A2 §11](A2_VARIABLES.md#11-las-15-interacciones-vía-8-en-producción)). Se
conservan como equivalentes.

## 9. Septiembre — Análisis del modelo en producción

Sin cambiar el problema, se midió (`docs/ANALISIS_HOLD_Y_GLOBAL.md`):

1. **Por qué tanto MANTENER:** voto dividido + régimen del VIX.
2. **40/60 en vez de 30/70:** peor.
3. **Global contra por acción** sobre las mismas filas: gana o empata el
   global en los 5 modelos.
4. **Walk-forward de v5** que no se había citado: ningún modelo pasa de 0.394.
5. **2026 fuera de muestra:** F1 0.313, κ 0.010 con el modelo de entonces.
6. **Ajuste:** reentrenar con peso de MANTENER × 0.90, elegido con
   2019–2024 por origen rodante. En 2026: F1 0.354, κ 0.035, MANTENER 40 %
   (real 35 %).

Además se auditó y corrigió la plataforma (métricas mal calculadas; ver
[B2](../B_sistema/B2_API.md)).

## 10. Qué se mantuvo y qué cambió a lo largo de todo

| Se mantuvo desde v1 (TT1) | Cambió |
|---|---|
| Las 7 acciones, el periodo y Yahoo Finance | Exp A probaba en 2024–2025 → los tres prueban en 2025 (v4) |
| Las 61 variables calculadas | Cada modelo con su filtro → las 61 para todos (v4); 76 en producción (+15 interacciones) |
| La etiqueta 30/70 a un día | — (se probaron otras y se descartaron) |
| Los 5 modelos y CRISP-DM | Búsqueda: cuadrícula y redes fijas → Optuna simétrica (v5) |
| F1-macro + métricas económicas | Se agregaron kappa, IC bootstrap, permutación, walk-forward, costos |
| Global y por acción se entrenan | Principal por acción (TT1) → **principal global** |
| | LR one-vs-rest L2 (TT1) → elasticnet multinomial C 0.01–1 (v4) → L2 C 0.000165 (v5) → + interacciones → + peso MANTENER 0.90 |

## 11. ¿Por qué tantas versiones?

Porque es investigación, no un plan lineal: cada versión respondió a algo
que la anterior descubrió (comparaciones injustas, errores de protocolo,
sospecha de sobreajuste a un año). Que la conclusión principal —los
clásicos regularizados igualan o superan a las redes— se mantenga en v4, v5,
el walk-forward y 2026 es justamente lo que la hace creíble.

---

## Preguntas de este tema

Están desarrolladas en [D2](../D_defensa/D2_PREGUNTAS_GENERALES.md) y
[D5](../D_defensa/D5_PREGUNTAS_ESTADISTICA.md).
