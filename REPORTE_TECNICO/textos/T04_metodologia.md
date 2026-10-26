# T04 — Metodología: borradores de las secciones que cambian

> Borradores para el capítulo 4 con el protocolo final. Numeración según
> `01_ESTRUCTURA_PROPUESTA.md`. Tablas en `tablas/TABLAS_NUEVAS.md`,
> figuras en `diagramas/`.

---

## 1. Marco de trabajo y etapas del proyecto (4.1)

El trabajo se condujo con CRISP-DM como marco de proceso para el análisis de
datos y SCRUM como marco de gestión. CRISP-DM organiza el trabajo en seis
fases —comprensión del negocio, comprensión de los datos, preparación,
modelado, evaluación y despliegue— que se recorren de forma iterativa: los
hallazgos de la evaluación pueden obligar a volver a la preparación de los
datos o al modelado. El trabajo recorrió ese ciclo seis veces. Cada vuelta,
que en este documento se denomina **etapa**, respondió una pregunta concreta
(Tabla T-02, Figura D08):

1. **Etapa 1 — Línea base (TT1).** Se construyó el sistema completo con los
   cinco modelos, con una selección de características distinta para cada
   uno y un modelo por acción. La comparación mostró a los clásicos arriba,
   pero no era en igualdad de condiciones.
2. **Etapa 2 — Primeras mejoras.** Se optimizó cada modelo y se probaron
   preselección de variables, más variables y ensambles. Se encontró que
   filtrar variables empeora y que hacía falta un protocolo que no usara el
   año de prueba para decidir.
3. **Etapa 3 — Comparación en igualdad de condiciones.** Los cinco modelos
   recibieron las mismas 61 características y los tres experimentos la misma
   prueba (2025): 120 corridas. Es la comparación publicada en MICAI (§7).
4. **Etapa 4 — Protocolo final.** Ninguna decisión usa la prueba, los cinco
   modelos se ajustan con la misma búsqueda (Optuna) y se evalúan sobre las
   mismas filas, con intervalos de confianza, costos y prueba año por año.
   Es el **resultado principal** (MICAI §8).
5. **Etapa 5 — Búsqueda de mejoras.** Se probaron calibración, mezclas,
   promedios de pesos, recencia y nuevas variables sin cambiar el problema;
   solo se adoptaron 15 interacciones, como equivalentes.
6. **Etapa 6 — Modelo de la plataforma y validación.** Se analizó y corrigió
   el exceso de la clase mantener, se comparó el modelo global contra uno
   por acción, se entrenó el modelo de producción y se validó con datos de
   2026.

Los Experimentos A, B y C (sección 4.7) se repiten dentro de las etapas 1 a
4; no son etapas. SCRUM organizó estas etapas en sprints con entregables y
revisión al cierre (registro en `docs/ACTIVIDADES_SEGUIMIENTO.md`).

---

## 2. Pregunta de investigación e hipótesis (4.2)

**Pregunta.** ¿Pueden los modelos de aprendizaje profundo (LSTM, CNN 1D y
CNN-LSTM) ofrecer un desempeño superior, en métricas de clasificación y en
una simulación económica, frente a modelos clásicos (Regresión Logística y
XGBoost) y a líneas base ingenuas, al generar señales diarias de compra,
venta o mantenimiento para las siete acciones de estudio?

**Hipótesis nula (H₀).** Ninguno de los modelos de aprendizaje profundo
evaluados (LSTM, CNN 1D y CNN-LSTM) presenta un desempeño superior de manera
consistente frente a los modelos de referencia.

**Hipótesis alternativa (H₁).** Al menos uno de los modelos de aprendizaje
profundo supera de manera consistente a los modelos de referencia.

**Criterio de "superior de manera consistente".** Un modelo es superior a
otro si la diferencia pareada de F1-macro en el año de prueba tiene un
intervalo de confianza bootstrap del 95 % que excluye el cero en el
Experimento B (principal), la misma dirección se observa en los Experimentos
A y C, y la ventaja no se invierte en la prueba año por año (sección 4.7).
Las métricas económicas se usan como criterio secundario.

---

## 3. Datos (4.3, párrafo del periodo)

Los datos se descargan de Yahoo Finance con la biblioteca `yfinance`
(`auto_adjust=True`) desde el 1 de enero de 2013, para que los indicadores
más largos (la media móvil de 200 días y la normalización del VIX con 252
días) estén completos al inicio del periodo de estudio. Tras eliminar las
filas incompletas, el conjunto de desarrollo va del 31 de diciembre de 2013 al
29 de diciembre de 2025: 3 017 días por acción y 21 119 filas día-acción.
Los datos del 2 de enero al 22 de octubre de 2026 se descargaron después con
el mismo código y se usaron únicamente como prueba ciega; ninguna decisión
del trabajo los utilizó. La plataforma, por su parte, descarga los datos de
cada día hábil.

---

## 4. Partición temporal y validaciones adicionales (4.7)

**4.7.1 Experimentos.** Los datos se dividen siempre en orden cronológico:
entrenamiento, validación y prueba, sin mezclar fechas. Se definen tres
experimentos que comparten la validación (2024) y la prueba (2025) y
difieren solo en la cantidad de historia de entrenamiento (Tabla T-03,
Figura D09):

| Experimento | Entrenamiento | Validación | Prueba | Años |
|---|---|---|---|---:|
| A | 2014–2023 | 2024 | 2025 | 10 |
| **B (principal)** | **2018–2023** | **2024** | **2025** | **6** |
| C | 2020–2023 | 2024 | 2025 | 4 |

Así, cualquier diferencia entre experimentos se debe a cuánta historia se
usa. El Experimento B se declaró principal desde el diseño, como punto medio
entre cantidad de datos y vigencia del régimen de mercado. 2025 es el último
año completo; no es un año especialmente favorable (retorno medio de +24 %,
por debajo de la mediana de 2014–2024, y volatilidad de 39 %, la tercera más
alta).

**4.7.2 Validaciones adicionales.** Un solo año de prueba no basta para
separar el efecto del modelo del régimen de ese año. Por eso se agregan:

- **Prueba año por año (2020–2025).** Para cada año *T* se entrena con los
  cinco años [T−6, T−2], se valida con T−1 y se prueba con T. La ventana de
  entrenamiento tiene el mismo tamaño en todos los años. Se corre con los
  ajustes fijados en la Etapa 3 (que no vieron ningún año de prueba) y con
  los de la Etapa 4.
- **Origen rodante (2019–2024).** Para cada año *Y* se entrena el pipeline de
  producción con los seis años anteriores y se predice *Y*. Se usó para
  tomar las decisiones del modelo de la plataforma sin mirar 2025 ni 2026.
- **Prueba ciega 2026.** Del 2 de enero al 22 de octubre de 2026, con los
  ajustes congelados.
- **Modelo de producción.** Se entrena con 2018–2025 (la configuración del
  Experimento B extendida hasta el último año completo).

---

## 5. Escalado y construcción de secuencias (4.8)

**Escalado.** El escalador se trató como un hiperparámetro más
(estandarización, escalado robusto o min-max). La búsqueda eligió el
**escalado robusto** (`(x − mediana) / (P75 − P25)`) para la Regresión
Logística y las tres redes; los retornos tienen colas pesadas y la mediana y
el rango intercuartílico no se distorsionan con días extremos. XGBoost es
invariante a transformaciones monótonas. El escalador se ajusta solo con el
entrenamiento (por acción en la investigación; uno global en producción, con
una diferencia despreciable: 0.4125 contra 0.4086 de F1 en 2025).

**Secuencias.** Las redes reciben una ventana de *W* días consecutivos con
las 61 características de cada día, es decir, tensores de forma
`(n, W, 61)`. Las ventanas se construyen sobre la serie continua de cada
acción y cada ejemplo se asigna al conjunto (entrenamiento, validación o
prueba) según la fecha de su etiqueta. La ventana del primer día de prueba
incluye días del final de la validación, lo cual no es fuga de información
porque solo mira hacia atrás y el escalador se ajustó con el entrenamiento.
Con este diseño los cinco modelos se evalúan sobre **exactamente las mismas
filas** (Figura D12).

Para la fila del día *t*, la ventana abarca los días *t − W* a *t − 1*; la
etiqueta describe el movimiento de *t* a *t + 1*. En consecuencia, las redes
no ven las características del día *t*, que la Regresión Logística y XGBoost
sí reciben. No es una fuga (le falta información, no le sobra), pero es una
desventaja para las redes. Su efecto se midió entrenando la Regresión
Logística con las características de *t − 1*: su F1-macro en 2025 baja de
0.393 a 0.386 (−0.007), mucho menos que la diferencia observada entre la
Regresión Logística y las redes.

---

## 6. Modelos (4.9)

Cada modelo se entrena como **modelo global** con las siete acciones
(~10 500 filas en el Experimento B) y, como comparación, como un modelo por
acción (~1 500 filas). Las configuraciones finales, elegidas con la búsqueda
de la sección 4.10, son (Tabla T-05):

- **Regresión Logística multinomial** con penalización L2 y C = 0.000165
  (regularización muy fuerte), escalado robusto y pesos de clase balanceados.
  La búsqueda podía elegir entre L1, L2 y elasticnet con C entre 10⁻⁴ y 10³.
- **XGBoost** con 485 árboles de profundidad máxima 9, tasa de aprendizaje
  0.074, submuestreo de filas 0.97 y de columnas 0.93, `min_child_weight` 2,
  `gamma` 0.035, regularización L1 1.70 y L2 5.23, y pesos por muestra
  balanceados.
- **LSTM** unidireccional de 2 capas de 118 unidades sobre una ventana de 10
  días, con *pooling* por atención, normalización de capa, dropout 0.43 y
  *focal loss* (γ = 1.43); 198 480 parámetros.
- **CNN 1D** con dos bloques convolucionales (50 y 100 filtros, kernel 7) sobre
  una ventana de 10 días, promedio global en el tiempo y una capa densa de
  101 unidades; *focal loss* (γ = 2.48); 67 007 parámetros.
- **CNN-LSTM** con dos bloques convolucionales (77 y 154 filtros, kernel 7,
  normalización por lotes) seguidos de una LSTM de 136 unidades sobre una
  ventana de 20 días; *focal loss* (γ = 2.01); 276 109 parámetros.

**Líneas base.** Decir siempre mantener (F1-macro ≈ 0.20 en 2025) y una
asignación aleatoria con las proporciones del entrenamiento (≈ 0.33).

Las configuraciones de las etapas anteriores (TT1 y Etapa 3) se resumen en
la Tabla T-05 para mostrar la evolución.

---

## 7. Protocolo de entrenamiento y búsqueda de hiperparámetros (4.10)

**Protocolo anidado.** Para que ningún resultado de prueba influya en las
decisiones, se separan tres papeles de los datos (Figura D11):

| Modo | Entrena | Elige la época (redes) | Elige la configuración | Evalúa |
|---|---|---|---|---|
| dev | 2018–2022 | 2023 | 2024 | — |
| final | 2018–2023 | 2024 | — (congelada) | 2025, una sola vez |

En modo *dev* se toman todas las decisiones (ablaciones de protocolo y
búsqueda de hiperparámetros) con 2024. En modo *final* se entrena con la
configuración congelada y 2025 se evalúa una sola vez. Antes de cambiar el
protocolo se verificó que el código nuevo reproduce los resultados de la
Etapa 3 (18 de 18 celdas idénticas), de modo que las diferencias se deben al
protocolo y no a la reimplementación.

**Búsqueda.** Los cinco modelos se ajustan con Optuna y el muestreador TPE
(semilla 42, 25 intentos iniciales al azar, modo multivariado); las redes
usan además poda por mediana. El objetivo es el F1-macro de 2024. El
presupuesto es de 150 intentos para la Regresión Logística (5
hiperparámetros) y XGBoost (9), y 80 para cada red (17 a 20 hiperparámetros,
incluidos el número de capas, el tamaño de la ventana, la función de pérdida,
el *pooling*, el escalador y el criterio de época). La búsqueda es simétrica
en procedimiento —misma herramienta y mismo año de decisión—, no en
dimensión, por lo que la afirmación que se sostiene es que una búsqueda
realista no cambia el orden de los modelos, no que se haya encontrado el
óptimo de cada red. Un entrenamiento de red tarda de 7 a 12 segundos en la
GPU, por lo que el cómputo no fue una restricción.

**Entrenamiento de las redes.** Hasta 100 épocas con AdamW, recorte de
gradiente y paro temprano con paciencia 20 sobre el criterio elegido por la
búsqueda (pérdida de validación, F1 de validación o F1 promedio de tres
épocas); se restauran los pesos de la mejor época. Reentrenar las redes con
entrenamiento + validación las empeoró (−0.024 a −0.047 de F1-macro), por lo
que solo los modelos clásicos se reentrenan con ambos conjuntos antes de
evaluar la prueba.

**Semillas.** En la evaluación final cada modelo se entrena con cinco
semillas (42, 1, 7, 2024 y 100) y se promedian sus probabilidades. La
Regresión Logística es determinista.

---

## 8. Validación estadística y métricas (4.11)

Para cada modelo se calculan, sobre las mismas 1 736 filas de prueba, las
ocho métricas de la sección 2.6 y la simulación económica de la sección
2.6.3, sin costos y con 5 y 10 puntos base por cambio de posición. Para el
modelo global, las métricas se calculan sobre las filas de las siete acciones
juntas y el índice de Sharpe sobre los 1 736 retornos diarios día-acción
concatenados.

Las comparaciones se validan con:
- intervalos de confianza del 95 % por bootstrap por bloques de 20 días
  (2 000 réplicas) para cada modelo y para la diferencia pareada entre cada
  par de modelos;
- una prueba de permutación de las señales (500 permutaciones);
- la prueba año por año 2020–2025, con la diferencia conjunta de los seis
  años;
- pruebas de signo y de Wilcoxon para la comparación pareada entre el modelo
  global y el modelo por acción;
- la prueba ciega 2026.

Si estas pruebas coinciden, la conclusión no depende de un año ni de una
métrica.
