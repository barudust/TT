# T02 — Marco teórico: secciones nuevas y reemplazos

> Borradores para §2.6 (métricas adicionales), §2.6.3 (simulación,
> reemplazo), §2.8 (validación estadística) y §2.9 (multicolinealidad).
> Las referencias entre corchetes están en `correcciones/C08_REFERENCIAS.md`.

---

## 1. Métricas adicionales (agregar a §2.6.1)

**Exactitud balanceada.** Es el promedio del recall de las tres clases,
`BA = (1/K) Σ_k Recall_k`. A diferencia de la exactitud, no premia a un
modelo que predice siempre la clase más frecuente: con tres clases, el azar
da 0.33.

**Kappa de Cohen.** Mide el acuerdo entre las predicciones y la realidad
descontando el que se esperaría por azar [Cohen, 1960]:
`κ = (p_o − p_e) / (1 − p_e)`, donde `p_o` es la exactitud observada y
`p_e = Σ_k p_k^{real} · p_k^{pred}` la exactitud esperada si las
predicciones fueran independientes de la realidad con las mismas
proporciones. κ = 0 equivale al azar y κ = 1 al acuerdo perfecto; valores
menores a 0.20 se consideran acuerdo leve [Landis y Koch, 1977]. Su ventaja
para este trabajo es que, a diferencia del F1, es comparable entre
etiquetados con distinta proporción de clases.

**AUC macro.** El área bajo la curva ROC mide la probabilidad de que el
modelo asigne más probabilidad de una clase a un ejemplo de esa clase que a
uno de otra. Para tres clases se calcula una curva por clase (uno contra
todos) y se promedian. Un valor de 0.5 es azar. A diferencia de las métricas
anteriores, no depende de la regla con que se elige la clase, sino de las
probabilidades.

**Pérdida logarítmica.** `LL = −(1/n) Σ_i log p_{y_i}(x_i)`, la entropía
cruzada promedio en el conjunto evaluado. Un modelo que asigna 1/3 a cada
clase obtiene `ln 3 ≈ 1.0986`; valores menores indican probabilidades mejor
calibradas que el azar. Es la métrica que usan las redes para entrenar, por
lo que también sirve como diagnóstico: si la pérdida de validación no baja
de ln 3, el modelo no generaliza.

**Uso en este trabajo.** Las ocho métricas (F1-macro, exactitud, exactitud
balanceada, kappa, AUC macro, pérdida logarítmica, índice de Sharpe sin
costos y con costos) se calculan con el mismo código para los cinco modelos
y sobre las mismas filas. La función de pérdida que cada familia usa para
entrenar y el criterio para elegir la época son parte del entrenamiento, no
de la evaluación.

---

## 2. Simulación económica (reemplaza §2.6.3)

**2.6.3 Simulación económica (backtesting)**

Como complemento de las métricas de clasificación, las señales de cada
modelo se traducen en una estrategia de inversión simple. Al cierre del día
*t* el modelo emite una señal; la posición correspondiente es +1 (comprar,
posición larga), −1 (vender, posición corta) o 0 (mantener, sin posición). La
posición se abre al precio de cierre de *t* y se cierra al cierre de *t + 1*,
de modo que el retorno de la estrategia es

`r_s(t) = posición_t · ln(C_{t+1} / C_t)`.

Cuando se consideran costos de transacción, cada cambio de posición paga
*c* puntos base: `r_s(t) = posición_t · r_{t+1} − c · |posición_t −
posición_{t−1}|`, de modo que pasar de una posición corta a una larga paga
el doble. La **rotación** es el cambio medio de posición por día; una
estrategia que cambia de posición con frecuencia paga más costos.

A partir de `r_s` se calculan el retorno acumulado (`e^{Σ r_s} − 1`), el
índice de Sharpe anualizado (`√252 · media(r_s) / desv(r_s)`, con tasa libre
de riesgo cero), la tasa de operaciones ganadoras y el factor de ganancia
(sobre los días con posición) y la caída máxima de la curva de capital. Como
referencia se usa la estrategia de comprar y mantener la acción durante todo
el periodo.

---

## 3. Validación estadística (nueva §2.8)

**2.8 Validación estadística de las comparaciones**

Una diferencia de F1-macro entre dos modelos en un año de prueba puede
deberse al azar de ese año. Para distinguir diferencias reales se usan las
siguientes herramientas.

**Bootstrap por bloques.** El bootstrap estima la variabilidad de una
métrica remuestreando los datos con reemplazo. En series de tiempo, los días
consecutivos están correlacionados, de modo que remuestrear días sueltos
subestima la variabilidad; el bootstrap por bloques remuestrea bloques de
días consecutivos [Künsch, 1989]. En este trabajo se usan bloques de 20 días
hábiles y 2 000 réplicas; los percentiles 2.5 y 97.5 de las réplicas forman
el intervalo de confianza del 95 %. Para comparar dos modelos se aplica a la
**diferencia pareada** (los dos modelos sobre las mismas réplicas): si el
intervalo de la diferencia excluye el cero, la diferencia es significativa.

**Prueba de permutación.** Para saber si un modelo tiene señal, se compara
su métrica con la de señales que conservan la misma proporción de cada clase
pero reasignadas al azar entre los días. La proporción de permutaciones que
igualan o superan al modelo es un valor *p* empírico.

**Pruebas pareadas no paramétricas.** Para comparar dos variantes sobre
varios pares de casos (por ejemplo, modelo global contra modelo por acción en
cada acción y experimento) se usan la prueba de signo y la de Wilcoxon de
rangos con signo, que no suponen normalidad.

**Error estándar del índice de Sharpe.** Con un año de datos diarios, el
error estándar del Sharpe anualizado es aproximadamente 1 [Lo, 2002]: un
Sharpe de +0.9 en un año es compatible con un rango amplio de valores. Por
eso las conclusiones económicas de un solo año son comparativas y la métrica
principal es la de clasificación.

**Validación en el tiempo.** Un solo año de prueba no separa el efecto del
modelo del régimen de ese año. La prueba año por año (*walk-forward*)
repite el entrenamiento y la evaluación para varios años de prueba
consecutivos, siempre entrenando solo con el pasado.

---

## 4. Multicolinealidad y regularización (nueva §2.9)

**2.9 Multicolinealidad y regularización**

Existe multicolinealidad cuando una o más características pueden expresarse
casi como combinación lineal de otras. Se mide con el factor de inflación de
la varianza (VIF): `VIF_i = 1 / (1 − R_i²)`, donde `R_i²` es el coeficiente
de determinación de la regresión de la característica *i* sobre todas las
demás. Un VIF mayor a 10 suele considerarse alto. El VIF de todas las
variables puede calcularse como la diagonal de la inversa de la matriz de
correlación.

La multicolinealidad hace inestables los coeficientes **individuales** de un
modelo lineal (es difícil atribuir el efecto a una u otra variable), pero no
empeora necesariamente su capacidad **predictiva**: la combinación de las
variables correlacionadas sigue siendo informativa. La penalización L2
(regresión *ridge*) se diseñó para este caso: al castigar la suma de los
coeficientes al cuadrado, reparte el peso entre variables parecidas en lugar
de asignar coeficientes grandes y de signo opuesto. Los modelos de árboles no
se ven afectados, porque en cada división eligen una sola variable.

Una práctica común es eliminar variables con VIF alto antes de entrenar. Sin
embargo, un filtro de este tipo evalúa las variables por separado o en
pares, y puede descartar información que solo es útil combinada; por eso en
este trabajo su efecto se mide experimentalmente (sección 4.6).
