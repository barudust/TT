# T03 — Justificaciones (observaciones de la sinodal del 26 de octubre)

> Textos para el documento sobre los cinco puntos que pidió la sinodal.
> El detalle, las tablas completas y cómo decirlo en la defensa están en
> `ESTUDIO_TT/D_defensa/D9_OBSERVACIONES_SINODAL.md`. Datos en
> `RESULTADOS_OPTIMIZADOS/observaciones_sinodal/`.
>
> Dónde va cada uno: §1 y §4 → nueva sección 4.6; §2 → 4.11; §3 → 4.12
> (criterio) y 6.9 (aplicación); §5 → 6.8.

---

## 1. Por qué el mismo conjunto de características para los cinco modelos

**4.6 Mismo conjunto de características para todos los modelos**

Para que una diferencia de desempeño pueda atribuirse al modelo y no a los
datos que recibe, los cinco modelos usan el mismo conjunto de 61
características, calculado con el mismo código y con la misma partición
temporal. Lo único que cambia entre familias es la forma de la entrada: los
modelos clásicos reciben el vector de características del día y las redes
una ventana de días consecutivos, lo que conserva su capacidad de aprovechar
la secuencia.

En la primera etapa del trabajo cada modelo recibía un subconjunto distinto,
elegido con un método estadístico acorde a sus supuestos (Pearson y VIF para
la Regresión Logística, valores SHAP para XGBoost y Spearman para las redes).
Ese diseño impedía comparar arquitecturas: en el Experimento C, por ejemplo,
XGBoost recibía 25 características y la LSTM 3, de modo que una diferencia de
desempeño podía deberse a la información disponible y no a la arquitectura.
Además, al compararse cada modelo con y sin su filtro, usar las 61
características fue mejor en 11 de 15 combinaciones de modelo y experimento
[artículo propio, §6]. A la Regresión Logística, en particular, el filtro le
quitaba información que su propia regularización aprovecha: en el
Experimento B por acción su F1-macro pasó de 0.355 con 4 características a
0.392 con las 61.

---

## 2. Métricas justas: qué es igual para los cinco

**(para 4.11, con la tabla T-08)**

La comparación entre los cinco modelos se realizó en igualdad de
condiciones:

- **Mismas características** (61) y **misma partición temporal**.
- **Mismas filas de prueba:** las ventanas de las redes se construyen sobre
  la serie continua y cada ejemplo se asigna al conjunto según la fecha de su
  etiqueta, de modo que los cinco modelos se evalúan sobre los mismos 1 736
  días-acción de 2025. En versiones anteriores las redes perdían los
  primeros 20 o 60 días de cada conjunto y se evaluaban sobre menos días.
- **Misma búsqueda de hiperparámetros:** Optuna con el mismo muestreador y el
  mismo año de decisión (2024) para los cinco; ninguna decisión usó 2025.
- **Mismas métricas, con el mismo código:** F1-macro, exactitud, exactitud
  balanceada, kappa de Cohen, AUC macro, pérdida logarítmica y el índice de
  Sharpe de la simulación sin costos y con costos de 10 puntos base.

Lo que **no** es igual, por diseño, es la función de pérdida con que cada
familia entrena (entropía cruzada regularizada en la Regresión Logística,
pérdida logística de árboles en XGBoost, *focal loss* en las redes) y el
criterio para elegir la época de las redes; ambos son parte del
entrenamiento y no de la evaluación.

Con esta evaluación, la Regresión Logística obtiene el mejor valor en las
ocho métricas en los tres experimentos (Tabla T-10).

---

## 3. Criterio de selección del modelo

**4.12 Criterio de selección del modelo (se declara antes de los resultados)**

El trabajo distingue dos decisiones:

1. **La pregunta de investigación** (si las arquitecturas profundas superan
   a los modelos clásicos) se responde comparando los cinco modelos en la
   prueba principal, con diferencias pareadas e intervalos de confianza, y
   comprobando que la dirección se mantiene en los tres experimentos y en la
   prueba año por año.
2. **La elección del modelo que se despliega** no se basa en el resultado de
   un solo año. Entre los modelos que no difieren significativamente en
   varios años de prueba se elige el que cumple mejor criterios que no
   dependen del año de prueba: menor número de parámetros, menor rotación (y
   por tanto menor costo de operar), interpretabilidad de sus decisiones y
   determinismo del entrenamiento. Una prueba ciega con datos posteriores,
   no usados en ninguna decisión, sirve de confirmación.

**6.9 Selección del modelo desplegado (aplicación del criterio)**

En la prueba principal la Regresión Logística fue significativamente mejor
que los otros cuatro modelos en los tres experimentos. En la prueba año por
año de 2020 a 2025, sin embargo, la Regresión Logística y XGBoost no
difieren significativamente (diferencia de +0.003 en F1-macro con los
ajustes fijados de antemano), mientras que ambos superan a las tres redes con
significancia. Se verificó además que elegir cada año el modelo con mejor
desempeño en validación no es confiable: esa regla habría obtenido un
F1-macro medio de 0.342–0.344, menor que el de conservar siempre la Regresión
Logística (0.350–0.360).

Ante el empate entre los dos modelos clásicos, se eligió la Regresión
Logística porque tiene 231 parámetros frente a 485 árboles de profundidad 9,
cambia de posición con menos frecuencia (rotación de 0.38 contra 0.65), lo
que se refleja en un mejor índice de Sharpe con costos (+0.62 contra +0.01 en
2025), cada coeficiente indica cómo influye una característica en cada clase,
y su entrenamiento es determinista. En la prueba ciega de enero a octubre de
2026 la Regresión Logística obtuvo el mayor F1-macro (0.346), sin diferencia
significativa con XGBoost, la LSTM y la CNN-LSTM. En la simulación económica
de ese periodo dos redes obtuvieron un Sharpe mayor (CNN 1D +0.88, LSTM +0.72,
Regresión Logística +0.38), lo que confirma que el desempeño económico de un
solo periodo no es un criterio estable de selección.

---

## 4. Multicolinealidad: diagnóstico y decisión

**(para 4.6, después del §1 de este archivo; con la tabla T-11)**

Las 61 características presentan multicolinealidad apreciable: en el
entrenamiento del Experimento B hay 26 pares con |r| > 0.9 (por ejemplo, el
estocástico %K y el Williams %R, que son la misma fórmula en otra escala, o
la distancia a la media de 20 días y al VWAP) y 26 variables con VIF mayor
a 10. Como se explicó en la sección 2.9, esto afecta la interpretación de
los coeficientes individuales pero no necesariamente la capacidad
predictiva, y la penalización L2 está diseñada para este caso.

Para comprobarlo con el protocolo final, se repitió la evaluación de los
cinco modelos con un filtro iterativo que elimina variables hasta que todas
tienen VIF ≤ 10, calculado solo con los datos de entrenamiento de cada caso
(quedan 45 variables). Con las 61 características el F1-macro fue mejor en
11 de 15 combinaciones de modelo y experimento. El filtro redujo el
desempeño de las tres redes en 8 de 9 casos (hasta 0.039 de F1-macro) y no
cambió de forma apreciable el de los modelos clásicos (diferencias de
±0.006). Por ello se conservaron las 61 características para los cinco
modelos, que además es la opción más favorable para las redes.

---

## 5. Un modelo global en lugar de uno por acción

**(para 6.8, con la tabla T-17)**

Cada modelo se entrenó de dos formas: un modelo global con las siete
acciones juntas y un modelo para cada acción. Para compararlas con rigor, ambos
se evaluaron sobre exactamente los mismos días de cada acción, en 21 pares
(7 acciones × 3 experimentos). El modelo global gana o empata en los cinco
modelos y ninguno es significativamente mejor por acción; en la Regresión
Logística el global gana 18 de 21 pares (prueba de signo, p = 0.002). Las
razones son que el modelo global dispone de siete veces más datos, que la
etiqueta es un percentil de cada acción (las clases significan lo mismo en
las siete) y que las características son razones comparables entre acciones;
con una señal débil, un modelo por acción tiende a ajustarse al ruido de esa
acción. Por eso la plataforma usa un solo modelo para las siete acciones.
Como los 21 pares comparten el año y el mercado no son independientes, los
valores *p* son optimistas; lo que da confianza es que la dirección se repite
en distintas etapas del trabajo.
