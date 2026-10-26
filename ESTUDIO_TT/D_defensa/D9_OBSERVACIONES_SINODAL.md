# D9 — Observaciones de la sinodal (26 de octubre) y cómo se respondieron

> **Resumen.** La sinodal hizo cuatro observaciones: (1) que no medíamos a
> los cinco modelos con las mismas reglas; (2) que tal vez elegimos el
> modelo por un resultado de prueba y no por su desempeño; (3) que
> explicáramos la multicolinealidad del dataset y por qué decimos que
> filtrar empeora; y (4) que la plataforma diga qué modelo usamos y muestre
> la comparación. Cada respuesta tiene evidencia nueva, calculada con
> `scripts_opt/observaciones_sinodal.py` (resultados en
> `RESULTADOS_OPTIMIZADOS/observaciones_sinodal/`). Al final van los
> párrafos listos para el reporte técnico.

---

## 1. «No están usando métricas justas para todos»

### Qué había de cierto

En el **reporte de TT1 (Etapa 1)** sí había diferencias entre familias de
modelos, y probablemente es lo que leyó:

| Dónde | En TT1 | Desde la Etapa 3–4 |
|---|---|---|
| Selección de variables | Cada familia con una prueba distinta: Pearson + VIF para la LR (3–8 variables), SHAP para XGBoost (23–25), Spearman para las redes (3–25) | Las mismas 61 variables para los cinco |
| Ajuste de hiperparámetros | Cuadrícula para LR y XGBoost; redes con arquitectura fija | Optuna para los cinco, con el mismo objetivo (F1-macro en 2024) |
| Ventana de las redes | Elegida con la prueba | Elegida por Optuna en 2024 |
| Filas calificadas | Las redes perdían los primeros días de cada periodo | Los cinco en las mismas 1,736 filas |

### Lo que es igual hoy (Etapa 4)

| Elemento | Igual para los cinco |
|---|---|
| Datos, acciones, años y 61 variables | Sí |
| Separación por tiempo (entrenamiento / validación 2024 / prueba 2025) | Sí |
| Filas de prueba | Sí: las mismas 1,736 (comprobado fila por fila: `1_mismas_filas.csv`) |
| Métricas | Sí: las mismas ocho, con el mismo código (`panel_metricas`) |
| Criterio para elegir ajustes | Sí: F1-macro en 2024 |
| Prueba | Sí: 2025 una vez; además seis años y 2026 |

**Lo único que no puede ser igual** es cómo aprende cada modelo por dentro:
la LR y XGBoost minimizan la pérdida logarítmica; las redes, entropía cruzada
o pérdida focal, y además eligen la época con la validación (la LR no tiene
épocas). Eso es parte del modelo, no de la evaluación: **a todos se les
califica con las mismas reglas.**

### Evidencia nueva: las ocho métricas para los cinco (prueba 2025)

`1_metricas_panel.csv`. La Regresión Logística es la mejor **en las ocho
métricas y en los tres experimentos**:

| Exp B | F1 | Exactitud | Exact. balanceada | Kappa | AUC | Log-loss ↓ | Sharpe | Sharpe 10 pb |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **LR** | **0.404** | **0.435** | **0.407** | **0.120** | **0.593** | **1.076** | **+0.89** | **+0.62** |
| XGBoost | 0.359 | 0.362 | 0.364 | 0.046 | 0.538 | 1.217 | +0.46 | +0.01 |
| LSTM | 0.369 | 0.381 | 0.373 | 0.065 | 0.551 | 1.093 | −0.35 | −0.41 |
| CNN-LSTM | 0.372 | 0.386 | 0.373 | 0.069 | 0.573 | 1.091 | −0.07 | −0.20 |
| CNN 1D | 0.359 | 0.377 | 0.369 | 0.060 | 0.568 | 1.094 | −0.46 | −0.53 |

En A y C pasa lo mismo (tablas en el CSV). La conclusión no depende de qué
métrica se elija.

---

## 2. «¿Eligen el mejor modelo por resultados o por desempeño?»

### Qué quiso decir (en palabras simples)

Si se elige al ganador **mirando la prueba**, la prueba deja de ser un
examen sorpresa: pasa a ser parte de la elección y el número que se reporta
sale optimista. Es como decidir quién es el mejor estudiante viendo solo el
examen final de un día: pudo tener suerte. Lo correcto es **elegir con datos
de validación (o de varios años) y usar la prueba solo para reportar**. Y
"el mejor modelo no siempre es el que da el número más alto": también
cuentan la estabilidad, el costo de operarlo y la sencillez.

### Lo que hay que reconocer

- La pregunta del TT es **comparativa** (¿el aprendizaje profundo supera a
  los clásicos?). Para eso se califica a los cinco en la misma prueba, sin
  elegir nada con ella: eso es legítimo.
- Pero cuando decimos "la LR es la ganadora" y la ponemos en la plataforma,
  **sí estamos eligiendo**, y si fuera solo por 2025 sería elegir con la
  prueba.
- Con la validación de un solo año (2024) la LR no sale primera: los cinco
  quedan entre 0.324 y 0.366.

### Evidencia nueva

**a) La validación de un solo año no sirve para escoger** (`2_eleccion_por_validacion.csv`).
Si en la prueba año por año se eligiera cada año el modelo con mejor
validación, el F1 promedio sería **0.342** (ajustes fijos de antemano) o
**0.344** (ajustes de la Etapa 4): **peor que quedarse siempre con
cualquiera de los dos clásicos** (0.350–0.360). La correlación entre el orden
en validación y el orden en prueba va de −0.6 a 0.9 según el año. Con tan
poca señal, un año no basta para escoger.

**b) Con seis años de prueba** (`2_seleccion_resumen.csv`,
`2_lr_contra_cada_uno_6anios.csv`):

| Ajustes | Modelo | F1 promedio | Lugar promedio | Años ganados | Sharpe 10 pb |
|---|---|---:|---:|---:|---:|
| Fijos de antemano (no vieron ningún año) | **LR** | **0.360** | **1.83** | **3** | **+0.09** |
| | XGBoost | 0.356 | 2.67 | 1 | −0.10 |
| | CNN 1D | 0.338 | 3.00 | 2 | −0.02 |
| | LSTM | 0.331 | 3.67 | 0 | −0.50 |
| | CNN-LSTM | 0.326 | 3.83 | 0 | −0.63 |
| Elegidos con 2024 | XGBoost | 0.356 | 2.33 | 1 | −0.20 |
| | LR | 0.350 | 2.33 | 3 | −0.06 |

Juntando los seis años de prueba (bootstrap por bloques): **LR − XGBoost no
es significativa** (+0.003 y +0.006); **LR − cada red sí es significativa**
(+0.017 a +0.055).

**c) Prueba ciega 2026 para los cinco** (`4_ciega2026.csv`): ajustes
congelados de la Etapa 4, entrenamiento 2020–2024, validación 2025, prueba
enero–octubre de 2026, que ninguna decisión usó.

| Modelo | Validación 2025 | F1 2026 | Kappa | AUC | Log-loss ↓ | % mantener | Sharpe | Sharpe 10 pb |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **LR** | **0.402** | **0.346** | 0.038 | 0.520 | **1.097** | 54 % | +0.38 | +0.02 |
| XGBoost | 0.360 | 0.343 | 0.036 | 0.526 | 1.210 | 55 % | −0.00 | −0.49 |
| LSTM | 0.349 | 0.331 | **0.040** | **0.532** | 1.099 | 24 % | +0.72 | +0.65 |
| CNN-LSTM | 0.365 | 0.318 | 0.017 | 0.523 | 1.101 | 19 % | +0.16 | −0.01 |
| CNN 1D | 0.313 | 0.304 | 0.032 | 0.530 | 1.101 | 9 % | **+0.88** | **+0.82** |

1,421 filas (7 acciones, 2 de enero a 22 de octubre de 2026). Diferencia de
F1 de la LR contra cada uno: XGBoost +0.003, LSTM +0.015, CNN-LSTM +0.028
(no significativas) y CNN 1D +0.042 (significativa).

**Cómo leerlo, sin maquillarlo:**

- En la validación (2025) de este pliegue, la LR es la mejor; elegirla por
  validación habría dado el primer lugar en F1 en 2026. Aquí sí coinciden.
- En 2026 los cinco quedan casi en el azar (kappa ≤ 0.04, AUC 0.52–0.53):
  la señal es débil, como en todos los años.
- **En dinero, en 2026 las redes salen mejor.** La CNN 1D dice «mantener»
  solo el 9 % de los días y casi no cambia de posición, así que se comporta
  como una apuesta casi fija en una dirección; en un año con tendencia eso
  paga. Un Sharpe de diez meses tiene un error estándar cercano a 1: no es
  significativo, pero hay que reportarlo.
- Conclusión que sí se sostiene: en **clasificación**, los clásicos quedan
  arriba o empatados con las redes en todas las pruebas; en **dinero** el
  orden cambia de un año a otro y no hay un ganador estable.

### El criterio de elección (declarado)

1. **Pregunta del TT (clásicos contra redes):** se responde con todas las
   pruebas. Los clásicos superan a las redes con significancia en seis años
   y en las ocho métricas de 2025.
2. **Entre los dos clásicos:** empatan en seis años. Ante un empate, se
   elige por criterios que no dependen de la prueba:

| Criterio | Regresión Logística | XGBoost |
|---|---|---|
| Parámetros | 231 | 485 árboles de profundidad 9 |
| Rotación (cambios de posición) | 0.38 | 0.65 |
| Sharpe con comisión, promedio de seis años | +0.09 / −0.06 | −0.10 / −0.20 |
| Interpretable | Sí: cada coeficiente dice qué variable empuja | Solo con herramientas aparte (SHAP) |
| Determinista | Sí | Depende de la semilla (se promedian 5) |

3. **Confirmación:** 2026, datos que nadie usó: la LR queda primera en F1,
   casi empatada.

**Cómo decirlo:** "No elegimos la Regresión Logística porque ganó en 2025.
En seis años empata con XGBoost; ante el empate elegimos la más simple y
barata de operar, y en 2026, con datos nuevos, siguió primera en
clasificación. Lo que sí afirmamos con seguridad es que en clasificación los
modelos clásicos igualan o superan a las redes; en dinero el orden cambia de
un año a otro."

---

## 3. Multicolinealidad: por qué no quitamos variables parecidas

### Qué es y cuánta hay

Multicolinealidad = varias variables dicen casi lo mismo. Se mide con el
**VIF** (qué tanto se puede adivinar una variable con las demás; mayor a 10
se considera alto). En el entrenamiento del Experimento B
(`3_multicolinealidad_diagnostico.json`):

- 26 pares de variables con correlación mayor a 0.9 (76 mayores a 0.8). Por
  ejemplo, estocástico %K y Williams %R son la misma fórmula con otra escala
  (r = 1.0); distancia a la media de 20 días y al VWAP (r = 0.99).
- 26 variables con VIF mayor a 10; 10 con VIF mayor a 100.
- Si se quitan una por una hasta que todas queden con VIF ≤ 10, **quedan 45
  de 61**.

### Por qué no es un problema para predecir

- La multicolinealidad hace inestables **los coeficientes individuales**
  (difícil decir cuánto aporta cada variable), pero no hace peor la
  **predicción** del conjunto.
- La **regularización L2** de la LR (la "ridge") se inventó justamente para
  esto: reparte el peso entre variables parecidas en lugar de darle un
  coeficiente enorme a una.
- **XGBoost** no se ve afectado: cada árbol escoge una variable u otra.
- Un filtro como VIF o correlación mira las variables por separado o en
  pares, y puede quitar información que solo sirve **combinada**.

### Por qué decíamos que filtrar empeora

- En TT1 la LR usaba Pearson + VIF y le quedaban 3 a 8 variables. Al darle
  las 61, en el Experimento B por acción pasó de 0.355 a 0.392 (Etapa 3).
- El §6 del artículo (11 de 15 casos peor) salió de la Etapa 2, con las
  particiones de TT1.

### Evidencia nueva con el protocolo final (`3_multicolinealidad_resultados.csv`)

Cada modelo con las 61 contra el mismo modelo con el filtro VIF ≤ 10,
calculado **solo con el entrenamiento** de cada pliegue:

F1-macro en la prueba 2025 (diferencia = las 61 − con filtro; positivo = las
61 son mejores):

| Modelo | A | B | C | Seis años (promedio) |
|---|---:|---:|---:|---:|
| Regresión Logística | 0.406 vs 0.404 (+0.001) | 0.404 vs 0.409 (−0.006) | 0.401 vs 0.398 (+0.002) | 0.350 vs 0.354 (−0.004) |
| XGBoost | 0.359 vs 0.357 (+0.002) | 0.359 vs 0.366 (−0.006) | 0.362 vs 0.367 (−0.005) | 0.356 vs 0.358 (−0.003) |
| LSTM | 0.373 vs 0.339 (+0.034) | 0.369 vs 0.360 (+0.009) | 0.317 vs 0.319 (−0.002) | — |
| CNN-LSTM | 0.245 vs 0.206 (+0.039) | 0.372 vs 0.357 (+0.015) | 0.338 vs 0.322 (+0.016) | — |
| CNN 1D | 0.263 vs 0.240 (+0.023) | 0.359 vs 0.345 (+0.014) | 0.294 vs 0.279 (+0.016) | — |

**Lectura:**

- Con las 61 variables el resultado es mejor en **11 de 15 casos** (5
  modelos × 3 experimentos), la misma cifra que el §6 del artículo, ahora con
  el protocolo final y un filtro calculado solo con el entrenamiento.
- **A las redes, quitar variables las empeora** (8 de 9 casos, hasta 0.039
  de F1): pierden información que les servía.
- **A los clásicos les da prácticamente igual** (diferencias de ±0.006, a
  favor y en contra; en seis años el filtro queda 0.003–0.004 arriba, dentro
  del ruido). Es lo esperado: la L2 y los árboles ya manejan la
  multicolinealidad.
- **Por qué se quedan las 61:** el filtro no ayuda de forma clara a nadie y
  perjudica a las redes. Como la comparación exige las mismas variables para
  todos, usar el filtro haría la comparación **más desfavorable para las
  redes**; con las 61 se les da la mejor oportunidad, y aun así los clásicos
  quedan arriba.

---

## 4. «Pongan en la página qué modelo eligieron y la comparación»

- **Hoy:** debajo del título, «Modelo: Regresión Logística · ¿por qué este?»,
  que lleva a la pestaña nueva.
- **Acerca de:** el apartado del modelo se llama «Modelo elegido: Regresión
  Logística» y enlaza a la comparación.
- **Pestaña nueva «Modelos»** (`/modelos`), con gráficas:
  1. El modelo elegido y por qué (los tres puntos de la sección 2).
  2. Tabla de igualdad de condiciones.
  3. Prueba principal 2025 con selector A/B/C: barras de F1 con la línea del
     azar y la tabla de las ocho métricas (el mejor en negritas).
  4. Intervalos de confianza.
  5. Año por año, con la opción de ajustes fijos o elegidos con 2024, más la
     tabla de "¿y si eligiéramos por validación?".
  6. Prueba ciega 2026.
  7. Dinero con y sin comisión.
  8. Global contra por acción.
  9. Multicolinealidad: diagnóstico y las 61 contra el filtro.

Los datos los genera `observaciones_sinodal.py exportar_web` en
`Frontend/src/app/data/comparacion_modelos.json`: la página no calcula
nada, solo muestra resultados guardados.

---

## 5. Por qué el mismo dataset para todos (justificación)

1. **Diseño experimental:** para saber si un modelo es mejor que otro hay
   que cambiar solo el modelo. Si cada uno recibe variables distintas, la
   diferencia puede venir de las variables y no del modelo.
2. **Lo pedía el propio TT1** (§5.6): la asimetría en las variables impedía
   concluir sobre las arquitecturas.
3. **No perjudica a las redes:** reciben las mismas 61 variables pero en
   ventanas de días seguidos (10 a 20), así que conservan su ventaja de ver
   la secuencia.
4. **Filtrar no ayuda:** ni la selección por modelo del TT1 ni el filtro de
   multicolinealidad mejoran el resultado (sección 3).

---

## 6. Párrafos para el reporte técnico

**Igualdad de condiciones.** Los cinco modelos se entrenaron y evaluaron
con el mismo conjunto de 61 variables, la misma partición temporal y las
mismas filas de prueba (1,736 días-acción de 2025). Los hiperparámetros de
los cinco se eligieron con Optuna maximizando el F1-macro en el año de
validación 2024, sin usar el año de prueba. La evaluación usa las mismas
ocho métricas para todos: F1-macro, exactitud, exactitud balanceada, kappa
de Cohen, AUC macro, pérdida logarítmica y el índice de Sharpe de la
simulación con y sin costos de transacción. La función de pérdida de
entrenamiento y la elección de época son propias de cada familia y no
forman parte de la evaluación.

**Criterio de selección del modelo.** La comparación entre familias
(clásicos contra redes) se realizó evaluando a los cinco modelos en la
misma prueba, sin usarla para tomar decisiones. Para elegir el modelo que
se despliega no se usó un único año: la elección por validación de un solo
año resultó inestable (F1 promedio de 0.342 frente a 0.350–0.360 de los
modelos clásicos fijos). En seis años de prueba la Regresión Logística y
XGBoost no difieren significativamente; ante el empate se eligió la
Regresión Logística por parsimonia (231 parámetros), menor rotación (0.38
contra 0.65) y por tanto mejor desempeño con costos, interpretabilidad y
determinismo. En una prueba ciega con datos de enero a octubre de 2026, no
usados en ninguna decisión, la Regresión Logística obtuvo el mayor F1-macro
(0.346), sin diferencia significativa frente a XGBoost, LSTM y CNN-LSTM; en
la simulación económica de ese periodo dos redes obtuvieron mayor Sharpe, lo
que confirma que en esta tarea el desempeño económico de un solo periodo no
es un criterio estable de selección.

**Multicolinealidad.** Las 61 variables presentan multicolinealidad
apreciable (26 pares con |r| > 0.9 y 26 variables con VIF > 10 en el
entrenamiento del experimento B). Este fenómeno afecta la interpretación de
coeficientes individuales, no la capacidad predictiva; la penalización L2
de la Regresión Logística está diseñada para este caso y los modelos de
árboles son insensibles a él. Un filtro de VIF ≤ 10 calculado solo con los
datos de entrenamiento (que deja 45 variables) empeora el F1-macro en 11 de
15 combinaciones de modelo y experimento: reduce el desempeño de las tres
redes neuronales (hasta 0.039) y no cambia de forma apreciable el de los
modelos clásicos (±0.006). Por ello se conservaron las 61 variables para los
cinco modelos, que además es la opción más favorable para las redes.
