# Anexo B (propuesto) — Registro completo de experimentos

> **Para qué sirve.** El capítulo VII dice que "se probaron cerca de treinta
> técnicas", pero no las enumera en ningún lugar. Un sinodal puede pedir la
> lista o preguntar por qué se probó algo que no funcionó. Este anexo es la
> lista completa: **qué se probó, por qué era razonable probarlo en ese
> momento, qué salió y qué se decidió**. Va al final del documento, después
> del manual de usuario (o antes, si el manual pasa a ser el Anexo C).
>
> Todas las cifras son F1-macro del modelo global salvo que se diga otra
> cosa, y salen del archivo que se indica en la última sección. Las de las
> etapas 1 y 2 **no son comparables** con las demás (otra partición, otras
> variables, decisiones tomadas viendo la prueba); por eso solo se reportan
> como dirección del efecto.
>
> Columna "TT2": dónde aparece en la versión del 28 de octubre. **FALTA** =
> no aparece; **INCOMPLETO** = se menciona sin el motivo, el resultado o la
> decisión. Los textos para completarlos están en
> [`../textos/T08_blindaje_experimentos.md`](../textos/T08_blindaje_experimentos.md).

---

## Texto de introducción del anexo (listo para pegar)

> Este anexo registra todas las pruebas realizadas durante el trabajo, en el
> orden en que se hicieron, incluidas las que no mejoraron el resultado. Para
> cada una se indica qué la motivó (el resultado de la etapa anterior, la
> literatura, la revisión del artículo, una observación de la sinodal o el
> comportamiento del sistema en operación), qué se obtuvo y qué se decidió.
> Se reportan también los resultados negativos porque una comparación solo
> es creíble si las alternativas recibieron una oportunidad real: concluir
> que las redes no superan a los modelos clásicos exige haber intentado
> mejorarlas. Ninguna prueba se emprendió conociendo su resultado; cada una
> respondió a una pregunta que dejó abierta la anterior. Las cifras de las
> Etapas 1 y 2 no son comparables con las demás porque se obtuvieron con otra
> partición y con decisiones que observaron la prueba; se reportan solo como
> dirección del efecto. Las pruebas de la Etapa 5 se midieron sobre el año
> 2025 y por eso solo se usaron para descartar; la única que se adoptó se
> validó después con un origen rodante de 2019 a 2024.

---

## Etapa 1 — Línea base (Trabajo Terminal I, hasta el 18 de mayo)

| # | Qué se probó | Por qué se probó | Resultado | Decisión | TT2 |
|---:|---|---|---|---|---|
| 1 | Sistema completo con los 5 modelos, un modelo por acción y los 3 experimentos (A con prueba 2024–2025) | Diseño registrado en TT1: comparar aprendizaje profundo contra referencias clásicas | XGBoost 0.369, LR 0.351, CNN-LSTM 0.340, CNN 1D 0.331, LSTM 0.291 (promedio por acción); mejor Sharpe: LR (0.285 en B) | La comparación no era pareja (filas 2–3); se rehízo en TT2 | §7.2 ✓ |
| 2 | Selección de variables distinta por modelo: Pearson + VIF (LR), SHAP (XGBoost), Spearman (redes) | Cada filtro respetaba los supuestos de su familia (lineal, árboles, monotónica) | Cada modelo recibía de 3 a 25 variables; el propio TT1 (§5.6) lo señaló como su principal limitación | Se sustituye por las mismas 61 para todos (fila 7) | §4.6, §7.2 ✓ |
| 3 | Ventana de las redes de 20 o 60 días, elegida con la prueba; redes evaluadas sobre menos días | Práctica habitual en la literatura revisada | Favorecía a las redes y las evaluaba sobre 228 o 188 días contra 248 | Corregido en la Etapa 4 (mismas 1 736 filas, todo elegido con 2024) | §7.2, Tabla 24 ✓ |

## Etapa 2 — Primeras mejoras (mayo–junio)

| # | Qué se probó | Por qué se probó | Resultado | Decisión | TT2 |
|---:|---|---|---|---|---|
| 4 | Optimización de cada modelo por separado (LR elasticnet, XGBoost con Optuna de 20–40 intentos, LSTM bidireccional, otros escaladores) | Trabajo futuro que planteó TT1: búsqueda sistemática de hiperparámetros | Mejora algo cada modelo, pero la mejor configuración se eligió viendo la prueba | Cifras **no citables**; queda la idea de optimizar a todos | §7.3 ✓ |
| 5 | Ajuste posterior del umbral de probabilidad de cada clase | Con probabilidades cercanas a 1/3, el argmax favorecía MANTENER | Subía el F1 en un experimento y lo bajaba en otro | Descartado | §7.3 ✓ |
| 6 | **Preselección estadística contra usar las 61 variables** (15 combinaciones modelo × experimento) | Comprobar si la asimetría de TT1 se justificaba: ¿el filtro ayuda a cada modelo? | Las 61 ganan en 11 de 15 (hasta +0.039); el filtro solo ayudó en 4 casos, todos de redes; LR por acción: 0.355 (4 variables) → 0.392 (61) | Las 61 para los cinco. **Publicado (artículo, §6)** | §4.6, §7.3 ✓ |
| 7 | 181 variables (puntajes z, rezagos e interacciones) | Más información de entrada podría subir el techo | Peor | Descartado | §7.3 ✓ |
| 8 | 94 variables con contexto macroeconómico y sectorial (curva de tasas, dólar, oro, petróleo, ETF sectoriales) | Las tecnológicas dependen de tasas y del ciclo; la literatura usa contexto macro | −0.010 en promedio; mejora solo en 6 de 15 combinaciones | Descartado | §7.3 ✓ |
| 9 | LightGBM | Boosting más rápido y con otro crecimiento de árboles [Ke 2017] | F1 similar a XGBoost, sin ventaja | Descartado; no entra en la comparación (alcance de 5 modelos) | §1.3, §7.3 **INCOMPLETO** (sin resultado) |
| 10 | Stacking (meta-LR sobre las probabilidades de los modelos) | Los ensambles suelen superar a sus componentes [Wolpert 1992]; Sonkavde et al. [31] lo reportan en bolsa | F1 global entre 0.309 y 0.364 | Descartado | §7.3 ✓ |
| 11 | Votación suave de los 5 modelos | Promediar modelos distintos reduce varianza | F1 entre 0.322 y 0.346 | Descartado | §7.3 ✓ |
| 12 | Mezcla LR + XGBoost con pesos elegidos en validación | Combinar el mejor lineal con el mejor de árboles | Los pesos quedaron en 0 y 1: la mezcla era XGBoost solo | Descartado | §7.3 ✓ |
| 13 | Filtro de confianza para la LR (operar solo si la probabilidad máxima supera un umbral) | Operar menos días pero con más acierto | F1 sin mejora (−0.005), Sharpe parecido | Descartado | §7.3 **INCOMPLETO** (sin resultado) |

## Etapa 3 — Comparación en igualdad de condiciones (junio)

| # | Qué se probó | Por qué se probó | Resultado | Decisión | TT2 |
|---:|---|---|---|---|---|
| 14 | Las mismas 61 variables para los cinco, la misma prueba 2025 en A, B y C; 120 corridas | Corregir la asimetría de TT1 (filas 2 y 6) y preparar el artículo | LR 0.399 promedio, XGBoost 0.385, redes 0.359–0.377 | **Publicado (artículo, §7)** | §7.4 ✓ |
| 15 | Efecto de la cantidad de historia (A = 10, B = 6, C = 4 años) | ¿Más años ayudan, o el mercado viejo estorba? Es la razón de tener tres experimentos | LR casi igual en los tres (0.411 / 0.385 / 0.401 en la Etapa 3; 0.406 / 0.404 / 0.401 en la Etapa 4); las redes cambian mucho y en la Etapa 4 dos colapsan en A | La conclusión no depende de cuántos años se usen | Tablas 23 y 25 tienen los números; **FALTA** la respuesta explícita |
| 16 | Descomposición del Sharpe por acción y por modelo | Saber si importa más qué modelo o qué acción | La acción explica 15.5 % y el modelo 3.4 % | **Publicado (artículo, §7.3)** | §7.4, §8.1.4 ✓ |

## Etapa 4 — Protocolo final (agosto) — resultado principal

| # | Qué se probó | Por qué se probó | Resultado | Decisión | TT2 |
|---:|---|---|---|---|---|
| 17 | Diagnóstico de las redes (14 de agosto) | **Los revisores del artículo pidieron** una búsqueda de hiperparámetros comparable para las redes; había que saber si estaban en desventaja | Pérdida de validación nunca por debajo de ln 3; el paro temprano restauraba la época 1–2; LSTM de 592 131 a 10 275 parámetros sin cambio | Rehacer el protocolo (filas 18–25) | §7.5.3 ✓; **FALTA** decir que lo pidieron los revisores |
| 18 | Replicación de la Etapa 3 con el código nuevo | Separar el efecto del protocolo del de la reimplementación | 18 de 18 celdas idénticas | Base para todo lo demás | §4.10.1 ✓ |
| 19 | Sensibilidad a detalles de implementación en GPU | Hallazgo al construir el código nuevo | Un cambio que no altera las matemáticas (cómo se recorre la validación) movió el F1 de la LSTM de 0.362 a 0.384 (+0.023) con la misma semilla | Desde aquí: 5 semillas, media y desviación, intervalos de confianza | **FALTA** |
| 20 | Torneo de 6 decisiones de protocolo (época, ventanas alineadas, escalador, pesos de clase, pooling, reentrenar con validación) | El diagnóstico apuntaba al protocolo, no a la arquitectura. Regla: adoptar solo si mejora ≥ 0.005 y más que la desviación entre semillas | Solo elegir la época por F1 ayuda (LSTM +0.059); reentrenar con validación empeora (−0.024 a −0.047); alinear ventanas cuesta −0.027 a la CNN-LSTM y se adopta igual para comparar sobre las mismas filas | Criterio de época dentro de la búsqueda; ventanas alineadas | §7.5.3 **INCOMPLETO** (sin tabla ni regla) |
| 21 | Optuna para las redes: 80 intentos, 17–20 hiperparámetros | Dar a las redes la oportunidad que pidieron los revisores | Ninguna configuración baja la pérdida de validación de ln 3 | Configuraciones congeladas | §4.10.2, Tabla 7 ✓ |
| 22 | Optuna para LR y XGBoost: 150 intentos | Misma herramienta y mismo año de decisión para todos | LR: L2, C = 0.000165, escalado robusto | Configuraciones congeladas | §4.10.2 ✓ |
| 23 | **93 variables** (61 + 32 de contexto: bonos del Tesoro SHY/IEI/IEF/TLT, VVIX, crédito HYG/LQD, dólar, oro, petróleo, QQQ, XLK, SMH, RSP, Russell 2000) | El plan de esta etapa buscaba "subir el techo" con más datos gratuitos de Yahoo | En validación las redes cambiaron entre −0.011 y +0.029 según el experimento, sin dirección consistente; las configuraciones ganadoras usan las 61 | Descartado | **FALTA** |
| 24 | Costos de transacción de 5 y 10 pb | La literatura y el artículo marcan la falta de costos como limitación | B, Sharpe con 5 pb: LR +0.76, XGBoost +0.23, CNN-LSTM −0.14, LSTM −0.38, CNN 1D −0.50; con 10 pb: LR +0.62, XGBoost +0.01 | La LR resiste mejor por operar menos | §7.5.2 ✓ (10 pb); **FALTA** 5 pb |
| 25 | Intervalos bootstrap por bloques y diferencias pareadas | Separar diferencias reales del azar de un año | La LR es significativamente mejor que los otros cuatro en A, B y C | Resultado principal | §7.5.2 ✓ |
| 26 | Prueba de permutación | ¿Hay señal o es suerte? | En 2025 solo 0.4 % de las permutaciones supera al modelo; en 2024, 79 % | Se declara como límite: la señal cambia entre años | §7.6.2 ✓ |
| 27 | Prueba año por año 2020–2025 (ajustes de la Etapa 3 y de la Etapa 4) | Un solo año de prueba no basta | LR 0.360 y XGBoost 0.356 sin diferencia significativa; ambos superan a las redes | LR y XGBoost empatan; criterio de selección (fila 46) | §7.6.1 ✓ |

## Etapa 5 — Búsqueda de mejoras (fin de agosto)

Todas sobre el protocolo congelado, Experimento B global, **medidas en 2025**.
Regla declarada antes de probar: adoptar solo si mejora ≥ 0.005 el F1 o
≥ 0.10 el Sharpe.

| # | Qué se probó | Por qué se probó | Resultado | Decisión | TT2 |
|---:|---|---|---|---|---|
| 28 | Calibración isotónica de probabilidades | Con probabilidades mal calibradas el argmax se equivoca de clase [Zadrozny y Elkan 2002] | XGBoost: +0.012 de F1 (0.359 → 0.371) y +0.13 de Sharpe; LR: 0.404 → 0.358; redes: ≈ −0.06 | No se adopta: aun calibrado, XGBoost queda debajo de la LR, y aplicarla a un solo modelo rompe la igualdad de condiciones | §7.7 **INCOMPLETO** (sin decisión) |
| 29 | Umbral económico de MANTENER | Maximizar la ganancia moviendo el umbral, sin reentrenar | Sharpe de la LR 0.89 → 1.18, pero F1 0.404 → 0.256 (MANTENER el 95 % de los días) | Descartado: el Sharpe sube porque casi no opera | §7.7 ✓ |
| 30 | Mezclas con pesos optimizados en 2024 (LR + XGBoost y los 5 modelos, por F1 y por Sharpe) | Repetir la mezcla de la Etapa 2 con el protocolo limpio | 0.359–0.373 de F1 contra 0.404 de la LR sola | Descartado: los pesos de un año no sirven al siguiente | §7.7 ✓ |
| 31 | Promedio de pesos de las últimas épocas (SWA) | Técnica estándar para generalizar mejor en redes [Izmailov 2018] | LSTM: Sharpe −0.35 → +0.14, F1 igual; CNN y CNN-LSTM sin efecto o peor | Descartado | §7.7 ✓ |
| 32 | Más peso a los datos recientes | El mercado no es estacionario [Gama 2014] | LR: el óptimo es no ponderar; XGBoost: F1 marginal y Sharpe −0.43 | Descartado | §7.7 ✓ (solo LR) |
| 33 | Rezagos de las 10 variables con más peso | Dar memoria explícita a los modelos clásicos | −0.004 | Descartado | §7.7 ✓ |
| 34 | Variables entre activos (beta contra SPY, correlación con XLK, ranking de retorno) | Relacionar las siete acciones entre sí | +0.003 | Descartado (dentro del ruido) | §7.7 ✓ |
| 35 | Las mismas 10 variables en ventanas de 5 y 20 días | Varias escalas de tiempo a la vez | −0.002 | Descartado | §7.7 ✓ |
| 36 | 15 interacciones (productos de pares) | Dar a la LR algo de no linealidad sin cambiar de modelo | +0.023 en 2025; en origen rodante 2019–2024: 0.357 contra 0.354 | **Adoptadas en la plataforma** como equivalentes; A/B/C y el artículo son sin ellas | §7.7, Tabla 31 ✓ |
| 37 | Barrido de la etiqueta: 24 combinaciones de 6 horizontes (1–10 días) y 5 pares de percentiles (28 corridas, 4 repetidas) | ¿La etiqueta de 1 día y 30/70 es la más aprendible? | Con 1 día, 25/75 da un F1 algo mayor (con más MANTENER) y 40/60 uno claramente menor; con 5–7 días el F1 es mayor. Los F1 de etiquetados distintos no son comparables y se midieron sobre 2025 (cifras en la lista "No citar") | Fuera del planteamiento: se conserva 1 día y 30/70; el horizonte largo pasa a trabajo futuro | §7.7 **INCOMPLETO** (no dice que se probó) |

## Etapa 6 — Modelo de la plataforma y validación (septiembre–octubre)

| # | Qué se probó | Por qué se probó | Resultado | Decisión | TT2 |
|---:|---|---|---|---|---|
| 38 | Factor fijo sobre la probabilidad de MANTENER (julio, antecedente) | La plataforma predecía MANTENER de más | Funcionaba en 2024 porque se ajustó con 2024 | Descartado en septiembre por estar ajustado a un año | **FALTA** |
| 39 | Diagnóstico del exceso de MANTENER | En operación predecía 57–64 % contra 40–42 % real; en 2026, F1 0.313 y kappa 0.010 | "Voto dividido" y peso de las variables del VIX y del S&P 500 | Corregir sin cambiar la etiqueta | §7.8.2 ✓ |
| 40 | Etiqueta 40/60 | Hipótesis: una clase central más angosta reduce MANTENER | No corrige el exceso y empeora | Se conserva 30/70 | §7.8.2 ✓ |
| 41 | Ocho correcciones con origen rodante 2019–2024 (factor fijo al decidir, proporción fija de 40 %, proporción móvil de 63 y de 252 días, pesos de clase × 0.95 / 0.90 / 0.85 / 0.80) | Elegir la corrección sin ver 2025 ni 2026 | Entre los pesos, × 0.90 es el mejor en F1, kappa y Sharpe a la vez; la proporción móvil de 252 días empata en F1 y kappa, con menos Sharpe en 2019–2024, 2025 y 2026 | En producción desde el 30 de septiembre | §7.8.2, Tabla 33 ✓ |
| 42 | Modelo global contra uno por acción sobre los mismos días (21 pares) | ¿Conviene un modelo por acción, como en TT1? | El global gana o empata en los cinco; LR 18 de 21 (p = 0.002) | Un solo modelo para las siete | §7.8.1 ✓ |
| 43 | Niveles de seguridad calibrados (año por año 2019–2025) | Mostrar la confianza sin prometer de más | Nivel alto > bajo en los siete años; ninguno acierta la mitad | Tres niveles, sin "segura" | §7.8.3 ✓ |
| 44 | Ventana de las redes que termina un día antes | Medir la desventaja de las redes | Cuesta ≈ 0.007 de F1, no cambia el orden | Se declara como limitación | §4.8.2, §7.8.2 ✓ |
| 45 | Escalador global contra uno por acción en producción | Simplificar la plataforma | 0.4086 contra 0.4125 | Escalador global | §4.8.1 ✓ |
| 46 | Observaciones de la sinodal (26 de octubre): ocho métricas para los cinco, criterio de selección, prueba ciega 2026 de los cinco, filtro VIF ≤ 10, regla "elegir cada año el mejor en validación" | Atender las observaciones | LR primera en las ocho métricas; LR primera en 2026 (0.346) sin diferencia significativa con tres modelos; las 61 mejor que el filtro en 11 de 15; la regla de validación da 0.342–0.344, peor que conservar la LR | Criterio de selección declarado (§4.12, §7.9) | §7.5–7.9 ✓ |

## Alternativas consideradas que no se corrieron

| Alternativa | Por qué no se corrió |
|---|---|
| GRU, Transformers (Informer, PatchTST), TabNet | Fuera del alcance de cinco modelos registrado en TT1; con ≈ 10 500 filas y redes que no bajan de ln 3, no se esperaba que una arquitectura más grande cambiara el resultado (trabajo futuro) |
| CatBoost | Mismo sesgo inductivo que XGBoost y LightGBM, que ya empatan |
| N-BEATS, N-HiTS | Diseñados para regresión de series, no para clasificación |
| Noticias, fundamentales, opciones, datos intradía | Cambian la fuente de datos (planteamiento: precios diarios gratuitos) |

> **Cuidado:** documentos de trabajo antiguos dicen que CatBoost, GRU,
> TabNet y Transformers "se probaron". **No es cierto**; solo hay código y
> resultados de LightGBM (corrección del 30 de septiembre en
> `RESULTADOS_OPTIMIZADOS/INVESTIGACION_COMPLETA.md` §6.1). No escribir que
> se probaron.

---

## De dónde sale cada cifra

| Filas | Archivo |
|---|---|
| 1–3 | Reporte de TT1; `tesis_ml_stocks/04_models/` |
| 4–13 | `RESULTADOS_OPTIMIZADOS/docs/GUIA_PROGRESO.md`, `docs/ANALISIS_FEATURE_SELECTION.md`, `stacking/`, `soft_voting/`, `ensemble_lr_xgb/`, `lr_confidence_filter/`, `v3/` |
| 14–16 | `RESULTADOS_OPTIMIZADOS/v4/resultados_v4.csv`; artículo §7 |
| 17–19 | `RESULTADOS_OPTIMIZADOS/docs/DIAGNOSTICO_MODELOS_PROFUNDOS.md`; `docs/RESULTADOS_V5.md` ("Hallazgo lateral") |
| 20 | `RESULTADOS_OPTIMIZADOS/v5/v1_ablaciones.csv`; `docs/RESULTADOS_V5.md` (V1) |
| 21–22 | `RESULTADOS_OPTIMIZADOS/v5/estudios/`, `v5/reportes/tabla4_busqueda.md` |
| 23 | `RESULTADOS_OPTIMIZADOS/v5/v4_features_comparacion.csv`, `v5/log_features_AC_v5.txt` |
| 24–25 | `RESULTADOS_OPTIMIZADOS/v5/resultados_finales.csv`, `v5/v6_ic_*`, `v5/v6_pares_*` |
| 26–27 | `RESULTADOS_OPTIMIZADOS/v5/walkforward_v4*.csv`, `v5/log_wf_v5.txt` |
| 28–32 | `RESULTADOS_OPTIMIZADOS/docs/VIA7_REFINAMIENTO.md`; `v7/` |
| 33–37 | `RESULTADOS_OPTIMIZADOS/docs/VIA8_DATASET.md`; `v8/` |
| 38–45 | `RESULTADOS_OPTIMIZADOS/docs/ANALISIS_HOLD_Y_GLOBAL.md`; `analisis_hold/`, `calibracion_hold/` |
| 46 | `scripts_opt/observaciones_sinodal.py`; `ESTUDIO_TT/D_defensa/D9_OBSERVACIONES_SINODAL.md` |
