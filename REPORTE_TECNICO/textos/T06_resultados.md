# T06 — Resultados: estructura por etapas y párrafos clave

> Esqueleto del capítulo 6 con los párrafos que cambian. Las tablas (T-xx)
> están en `tablas/TABLAS_NUEVAS.md` y las gráficas (Gxx) en `graficas/`.
> Las cifras, en `03_CIFRAS_VIGENTES.md`.

---

## 6 (introducción)

Este capítulo presenta los resultados en el orden en que se obtuvieron,
por etapa. La Etapa 1 corresponde al reporte de TT1 y se resume como punto de
partida; las Etapas 2 y 3 corrigieron sus limitaciones; la **Etapa 4**, con
el protocolo final, da el **resultado principal**, que se complementa con la
prueba año por año y la prueba ciega 2026. Las Etapas 5 y 6 documentan la
búsqueda de mejoras y el modelo que se despliega. Salvo que se indique otra
cosa, las cifras son F1-macro sobre la prueba de 2025.

## 6.1 Entorno de implementación

(Hardware del documento actual, correcto.) Versiones: Python 3.13.5,
scikit-learn 1.7.2, PyTorch 2.12 con CUDA 12.8, XGBoost 3.2.0, Optuna 4.8; la
plataforma fija scikit-learn 1.7.2 para que el archivo del modelo cargue con
la misma versión con que se entrenó. Scripts por etapa en la Tabla T-16.

## 6.2 Etapa 1: línea base (TT1)

La primera versión del sistema entrenó un modelo por acción, con un
subconjunto de características distinto para cada modelo, y eligió la
ventana de las redes con el conjunto de prueba. Con ese diseño XGBoost obtuvo
el mayor F1-macro promedio (0.369) y la Regresión Logística el mayor Sharpe
(0.285 en el Experimento B), y las tres redes quedaron por debajo (Tabla
T-01). Estas cifras **no son comparables** con las de las etapas siguientes
por cuatro razones: cada modelo recibía información distinta (entre 3 y 25
características), el Experimento A tenía otro año de prueba (2024–2025), la
ventana de las redes se eligió con la prueba y las redes se evaluaban sobre
menos días que los modelos clásicos. El propio reporte de TT1 señaló la
asimetría de características como la principal limitación de la comparación;
las etapas siguientes la eliminaron.

## 6.3 Etapa 2: primeras mejoras

Se optimizó cada modelo y se probaron tres ideas. (1) **Preselección de
características**: comparar cada modelo con y sin su filtro estadístico
mostró que usar las 61 es mejor en 11 de 15 combinaciones (publicado en
[artículo, §6]). (2) **Más características**: 181 (con transformaciones y
rezagos) y 94 (con contexto macroeconómico y sectorial) no mejoraron (−0.010
de F1 en promedio con 94). (3) **Ensambles**: stacking, votación suave y
mezclas de la Regresión Logística con XGBoost no superaron a la Regresión
Logística sola. Las configuraciones de esta etapa se eligieron con la prueba,
por lo que sus cifras no se reportan como resultado; lo que se conservó fue
la decisión de dar las 61 características a todos los modelos y la necesidad
de un protocolo que no usara la prueba.

## 6.4 Etapa 3: comparación en igualdad de condiciones

Con las mismas 61 características para los cinco modelos y la misma prueba en
los tres experimentos (120 corridas), la Regresión Logística obtuvo el mayor
F1-macro promedio en el modelo global (0.399; Tabla T-07) y el mejor Sharpe
en el Experimento B (+0.76). XGBoost quedó segundo (0.385) y las redes entre
0.359 y 0.377. La variación entre acciones fue mayor que entre modelos: la
acción explica el 15.5 % de la variación del Sharpe y el modelo el 3.4 %.
Estos resultados se publicaron en MICAI 2026 [§7]. Dos limitaciones quedaban
abiertas: las redes no tenían una búsqueda de hiperparámetros comparable a la
de XGBoost y su ventana se seguía eligiendo con la prueba.

## 6.5 Etapa 4: protocolo final (resultado principal)

Con el protocolo de la sección 4.10 —ninguna decisión con la prueba, la
misma búsqueda para los cinco y las mismas filas de evaluación—, la Regresión
Logística obtuvo el mayor F1-macro en los tres experimentos (0.406, 0.404 y
0.401; Tabla T-09, Figura G01) y fue **significativamente mejor que cada uno
de los otros cuatro modelos en los tres**: en el Experimento B, por +0.045
sobre XGBoost, +0.035 sobre la LSTM, +0.031 sobre la CNN-LSTM y +0.045 sobre
la CNN 1D, con intervalos bootstrap que excluyen el cero. Entre los otros
cuatro no hubo diferencias significativas en el Experimento B. La Regresión
Logística fue también la mejor en las otras siete métricas (Tabla T-10):
exactitud, exactitud balanceada, kappa (0.120), AUC macro (0.593), pérdida
logarítmica y el índice de Sharpe sin costos (+0.89) y con 10 puntos base
(+0.62). XGBoost conserva un Sharpe positivo sin costos (+0.46), pero cambia
de posición con más frecuencia (rotación de 0.65 contra 0.38) y con costos
queda en +0.01 (Figura G02); las tres redes tienen Sharpe negativo.

Comparado con la Etapa 3, el F1 de la Regresión Logística sube (de 0.385 a
0.404 en B) y el de las redes baja en promedio cuando se elimina la ventaja de
elegir su ventana con la prueba (Figura G03): ni una búsqueda de
hiperparámetros equivalente ni un protocolo más cuidadoso acercan las redes
a los modelos clásicos.

**Por qué no ganan las redes.** El diagnóstico de la Etapa 4 mostró que
ninguna configuración de red reduce su pérdida de validación por debajo de
ln 3 ≈ 1.0986, el valor que obtiene un modelo que asigna 1/3 a cada clase;
que reducir la LSTM de 592 131 a 10 275 parámetros no cambia el resultado;
que con paro temprano por pérdida se restauraba la primera o la segunda
época, y que elegir la época por F1 de validación fue la mejora más grande
(+0.059 a la LSTM). El límite no está en la capacidad ni en la
regularización de las redes, sino en la poca información que la entrada
contiene sobre la dirección del día siguiente, que las características ya
resumen.

## 6.6 Robustez en el tiempo

**Prueba año por año.** En seis años de prueba (2020–2025), con los ajustes
fijados en la Etapa 3, la Regresión Logística obtuvo el mayor F1-macro medio
(0.360) y ganó tres de los seis años, seguida de XGBoost (0.356); las redes
quedaron entre 0.326 y 0.338 (Tabla T-12, Figura G04). Juntando los seis
años, la diferencia entre la Regresión Logística y XGBoost no es
significativa (+0.003), mientras que la ventaja sobre cada red sí lo es
(+0.017 a +0.026). El orden cambia de un año a otro y ningún modelo llega a
0.40 en ningún año. Con los ajustes elegidos con 2024 la conclusión es la
misma: los dos modelos clásicos quedan juntos y arriba (XGBoost 0.356,
Regresión Logística 0.350) y las redes debajo (0.29–0.33).

**Permutación.** En 2025 solo el 0.4 % de 500 permutaciones de las señales
supera al modelo, mientras que en 2024 lo supera el 79 %: la señal existe en
algunos años y no en otros.

**Prueba ciega 2026.** Con los ajustes congelados de la Etapa 4, entrenando
con 2020–2024 y evaluando del 2 de enero al 22 de octubre de 2026, la
Regresión Logística volvió a obtener el mayor F1-macro (0.346), seguida muy
de cerca por XGBoost (0.343); la LSTM (0.331), la CNN-LSTM (0.318) y la CNN
1D (0.304) quedaron abajo, aunque solo la diferencia con la CNN 1D es
significativa (Tabla T-13, Figura G05). En la simulación económica de ese
periodo, la CNN 1D (+0.88) y la LSTM (+0.72) obtuvieron un Sharpe mayor que la
Regresión Logística (+0.38). Un periodo de diez meses no basta para que esas
diferencias sean significativas, y el resultado confirma lo que muestra la
prueba año por año: en clasificación los modelos clásicos se mantienen
arriba, mientras que el orden económico cambia de un periodo a otro.

## 6.7 Etapa 5: búsqueda de mejoras

(Conservar §6.6.4–6.6.6 del documento actual con los nombres de etapa.)
Agregar al final: de las técnicas probadas, solo se adoptaron las 15
interacciones, y como **equivalentes**: mejoraron el F1 en 2025, el año en que
se decidió adoptarlas (0.390 → 0.413), pero en la validación de 2024 y en el
origen rodante 2019–2024 empataron (0.354 contra 0.357) (Tabla T-20). Los
resultados de los Experimentos A, B y C se reportan sin ellas. Los cambios de
horizonte y de percentiles de la etiqueta modifican el problema y se dejan
como trabajo futuro.

## 6.8 Etapa 6: modelo de la plataforma

**Global contra por acción** (texto en `T03` §5, Tabla T-17, Figura G07).

**Exceso de la clase mantener.** El modelo balanceado predecía mantener con
más frecuencia de la real (57–64 % contra 40–42 % en 2024–2025). La causa es
un "voto dividido": en todos los días en que predice mantener, la suma de
las probabilidades de comprar y vender supera a la de mantener; el modelo
aprende que habrá movimiento, pero no hacia dónde, y ninguna dirección supera
por separado a mantener. Además, como las variables con más peso son del VIX
y del S&P 500, iguales para las siete acciones, en periodos de VIX bajo el
modelo predice mantener para casi todas. Se compararon ocho correcciones con
origen rodante 2019–2024, sin mirar 2025 ni 2026 (Tabla T-18). Entre los
pesos de reentrenamiento, el de mantener × 0.90 fue el mejor en F1, kappa y
Sharpe a la vez. La proporción móvil causal de 252 días obtuvo un F1 y un
kappa prácticamente iguales (0.367 y 0.070, contra 0.365 y 0.068), pero
menos Sharpe en 2019–2024 (+0.51 contra +0.54), en 2025 (+0.81 contra +0.93)
y en 2026 (+0.16 contra +0.29), por lo que se eligió el peso × 0.90. En
enero–septiembre de 2026 el modelo corregido obtuvo F1 0.354 y kappa 0.035,
contra 0.313 y 0.010 del modelo anterior, con una proporción de mantener
cercana a la real (40 % contra 35 %) (Tabla T-19). La mejora no es
estadísticamente significativa (Wilcoxon p = 0.31): se trata de un modelo
equivalente con una proporción de clases más realista.

**Niveles de seguridad** (Tabla T-21).

## 6.9 Selección del modelo desplegado

(Texto en `T03` §3.)
