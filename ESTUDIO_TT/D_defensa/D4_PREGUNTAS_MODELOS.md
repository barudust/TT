# D4 — Preguntas de modelos: Regresión Logística, XGBoost y redes neuronales

> Respuesta corta = lo que dices. "Si repreguntan" = el fondo. Detalle en
> [A4](../A_modelo/A4_MODELOS_CLASICOS.md) y
> [A5](../A_modelo/A5_REDES_NEURONALES.md).

---

## Regresión Logística

### M1. Explique la regresión logística multinomial.

**Respuesta corta.** Para cada una de las tres clases calcula un puntaje
lineal, `z_k = β_k · x + b_k`, con las 76 variables del día, y los
convierte en probabilidades con softmax, `p_k = e^{z_k} / Σ_j e^{z_j}`. La
señal es la clase con mayor probabilidad. Se entrena minimizando la
entropía cruzada (qué tan baja es la probabilidad que asigna a la clase
correcta) más una penalización a los coeficientes.

### M2. ¿Qué es la regularización y cuál usaron?

**Respuesta corta.** Penalizar coeficientes grandes para que el modelo no
memorice ruido. L2 (Ridge) penaliza la suma de cuadrados y encoge todos los
coeficientes; L1 (Lasso) penaliza la suma de valores absolutos y vuelve
algunos exactamente cero; elasticnet mezcla ambas. En el paper (v4) usamos
elasticnet; con Optuna (v5), que podía elegir cualquiera, ganó **L2 con
C = 0.000165**, que es la que está en producción.

### M3. ¿Por qué C es tan pequeño? ¿Qué implica?

**Respuesta corta.** C es el inverso de la fuerza de la regularización, así
que 0.000165 es regularización muy fuerte. Optuna lo eligió porque con tan
poca señal lo que mejor generaliza es alejarse poco de "no sé nada". La
consecuencia es que las probabilidades quedan cerca de 1/3 (confianza de
0.36 a 0.45). Aun así la confianza es informativa: con confianza baja
acierta 39 % y con confianza entre 0.40 y 0.45 acierta 56 %.

**Si repreguntan (lectura bayesiana):** equivale a una estimación MAP con
un prior gaussiano muy concentrado en cero sobre los coeficientes.

### M4. ¿Por qué ganó elasticnet en el paper y L2 después?

**Respuesta corta.** En v4 no se comparó: se fijó elasticnet con
l1_ratio = 0.5 y solo se buscó C en {0.01, 0.1, 1}. En v5 Optuna podía
elegir L1, L2 o elasticnet y C en un rango mucho más amplio; con una
regularización tan fuerte la parte L1 no agrega nada y ganó L2.

### M5. ¿Cuántos parámetros tiene la LR?

**Respuesta corta.** 3 clases × 76 variables + 3 interceptos = 231. Frente
a ~14 000 filas de entrenamiento es un modelo pequeño, y por eso difícil de
sobreajustar.

### M6. ¿Qué son los pesos de clase "balanced" y el ajuste de MANTENER × 0.90?

**Respuesta corta.** "Balanced" da a cada clase un peso inversamente
proporcional a su frecuencia, `n / (3 · n_clase)`, para que el modelo no
aprenda a decir siempre MANTENER. En producción, además, multiplicamos el
peso de MANTENER por 0.90 (pesos efectivos 1.103 / 0.762 / 1.097) porque el
modelo predecía MANTENER de más. El 0.90 se eligió solo con 2019–2024 y fue
el mejor en F1, kappa y Sharpe a la vez.

### M7. ¿Qué es SAGA?

**Respuesta corta.** Un algoritmo de optimización estocástico para la
regresión logística; es el único de scikit-learn que soporta elasticnet
multinomial. En la investigación con L2 se usó lbfgs; como el problema es
convexo, ambos llegan a la misma solución.

### M8. ¿Por qué ganó el modelo más simple?

**Respuesta corta.** Por el balance sesgo–varianza. Con poca señal y unas
10 500 filas, el error de un modelo flexible lo domina la varianza: aprende
ruido. La LR muy regularizada acepta un poco de sesgo y casi no tiene
varianza. Además, las 61 variables ya son transformaciones no lineales de
la historia (RSI, MACD, medias), así que combinarlas linealmente captura
casi toda la señal disponible. Coincide con la literatura de datos
tabulares (Grinsztajn et al., 2022).

---

## XGBoost

### M9. Explique XGBoost.

**Respuesta corta.** Es *gradient boosting* de árboles de decisión: se
entrenan cientos de árboles uno tras otro y cada uno corrige los errores de
los anteriores (ajusta el gradiente de la pérdida). La predicción es la suma
de todos. Se regulariza con profundidad máxima, mínimo de ejemplos por hoja,
ganancia mínima para dividir (gamma), penalizaciones L1/L2 en las hojas y
submuestreo de filas y columnas.

### M10. ¿Qué configuración ganó?

**Respuesta corta.** Con 150 intentos de Optuna: 485 árboles de profundidad
9, tasa de aprendizaje 0.074, submuestreo 0.97 de filas y 0.93 de columnas,
gamma 0.035, reg_alpha 1.70, reg_lambda 5.23; pesos balanceados por
muestra; entrenamiento en GPU.

### M11. ¿Por qué XGBoost no ganó si suele ganar en datos tabulares?

**Respuesta corta.** En seis años de walk-forward **empata** con la LR
(0.356 contra 0.350). En 2025 la LR fue significativamente mejor, y con
costos de transacción la LR gana claramente porque cambia de posición
mucho menos (rotación 0.38 contra 0.65): con 10 pb el Sharpe de XGBoost cae a
+0.01 y el de la LR a +0.62. Ante empate en clasificación, elegimos el
modelo más simple, determinista, interpretable y barato de operar.

### M12. ¿Usaron paro temprano en XGBoost?

**Respuesta corta.** No; el número de árboles lo eligió Optuna como
hiperparámetro. Lo único que se le agregó después fue calibración isotónica
(Vía 7), que mejoró un poco su F1 (0.359 → 0.371) sin cambiar el ranking.

---

## Redes neuronales: diseño

### M13. ¿Cómo diseñaron las redes?

**Respuesta corta.** En dos etapas. En la primera (la del paper) usamos
arquitecturas estándar fijas: una LSTM bidireccional de 2 capas de 128
unidades, una CNN de 3 bloques convolucionales (64, 128 y 192 filtros) y una
CNN-LSTM de 2 bloques convolucionales más una LSTM de 2 capas. En la
segunda, después de un diagnóstico, dejamos que Optuna eligiera 17 a 20
hiperparámetros, incluidos el número de capas, de unidades y de filtros,
el tamaño del kernel, la ventana, el dropout, la función de pérdida y el
tipo de pooling. Las ganadoras son las de v5.

### M14. ¿Cuántas capas tiene cada red y por qué?

**Respuesta corta.**
- **LSTM:** 2 capas LSTM de 118 unidades + pooling por atención +
  LayerNorm + capa de salida. 198 480 parámetros.
- **CNN 1D:** 2 bloques convolucionales (50 y 100 filtros, kernel de 7 días)
  + promedio global + capa densa de 101 + salida. 67 007 parámetros.
- **CNN-LSTM:** 2 bloques convolucionales (77 y 154 filtros, kernel 7, con
  BatchNorm) + 1 capa LSTM de 136 unidades + salida. 276 109 parámetros.

El número de capas no se fijó a mano: Optuna podía elegir de 1 a 3 capas
LSTM y de 1 a 4 bloques convolucionales y eligió 2. La razón de fondo es que
con ~10 000 ejemplos y poca señal, más capas solo agregan parámetros que
aprenden ruido. Además medimos que una LSTM de 1 capa y 16 unidades (10 275
parámetros) rinde igual que una de 592 131: el tamaño no es lo que limita.

### M15. ¿Qué recibe la red como entrada?

**Respuesta corta.** Una ventana de los últimos días (10 en la LSTM y la
CNN, 20 en la CNN-LSTM) con las 61 variables de cada día, escaladas con
RobustScaler ajustado en entrenamiento. Es un tensor de forma
(lote, días, 61).

### M16. Explique cómo funciona una LSTM.

**Respuesta corta.** Es una red recurrente que lee la secuencia día por día
y mantiene una memoria (el estado de celda). Tres compuertas con función
sigmoide controlan esa memoria: la de **olvido** decide qué borrar, la de
**entrada** qué agregar y la de **salida** qué exponer. Así evita el
problema del gradiente que desaparece de las recurrentes simples y puede
recordar patrones de varios pasos.

**Si repreguntan las ecuaciones:**
`f = σ(W_f[h, x] + b_f)`, `i = σ(W_i[h, x] + b_i)`,
`c = f ⊙ c_ant + i ⊙ tanh(W_c[h, x] + b_c)`, `o = σ(W_o[h, x] + b_o)`,
`h = o ⊙ tanh(c)`.

### M17. ¿Por qué bidireccional en el paper y no en la versión final?

**Respuesta corta.** Leer la ventana en ambos sentidos es válido porque toda
la ventana es pasado, y era la configuración estándar de v4. En v5 Optuna
podía elegir y prefirió unidireccional; la diferencia no fue relevante, lo
que confirma que la arquitectura no es la limitante.

### M18. ¿Qué es el pooling por atención?

**Respuesta corta.** En vez de usar solo el último estado de la LSTM, una
capa lineal le da un puntaje a cada día de la ventana, se normalizan con
softmax y se hace una suma ponderada de los estados. El modelo aprende qué
días pesan más. Optuna lo eligió para la LSTM.

### M19. Explique la CNN 1D. ¿Por qué 1D y no 2D?

**Respuesta corta.** Una convolución 1D desliza un filtro a lo largo del
tiempo: cada filtro mira, por ejemplo, 7 días de las 61 variables y se
activa cuando encuentra cierto patrón, en cualquier posición de la ventana.
Es 1D porque los datos son una serie de tiempo (una dimensión temporal con
61 canales), no una imagen con dos dimensiones espaciales.

### M20. ¿Qué hace la parte convolucional en la CNN-LSTM?

**Respuesta corta.** Transforma cada paso de la ventana en 154 rasgos
locales (patrones de hasta 7 días); la LSTM lee después esa secuencia de
rasgos en orden. La idea es combinar detección de patrones locales con
memoria del orden temporal.

### M21. ¿Qué es dropout? ¿Y BatchNorm y LayerNorm?

**Respuesta corta.** **Dropout** apaga al azar una fracción de neuronas en
cada paso de entrenamiento (0.16 a 0.43 en las ganadoras) para que la red no
dependa de ninguna en particular; reduce el sobreajuste. **BatchNorm**
normaliza las activaciones de cada lote y estabiliza el entrenamiento (la
CNN-LSTM lo usa; la CNN no). **LayerNorm** normaliza el vector de cada
ejemplo antes de la capa de salida.

### M22. ¿Qué función de pérdida usaron?

**Respuesta corta.** Optuna podía elegir entropía cruzada (con *label
smoothing*) o *focal loss*, y eligió **focal loss** en las tres redes
(γ entre 1.4 y 2.5). La focal loss, `−(1−p)^γ · log p`, le resta peso a los
ejemplos que ya se clasifican bien para concentrarse en los difíciles.

### M23. ¿Cómo entrenaron? (optimizador, épocas, paro temprano)

**Respuesta corta.** AdamW (que incluye *weight decay*, una penalización L2
de los pesos), hasta 100 épocas, paro temprano con paciencia de 20 épocas
según el criterio elegido (pérdida o F1 de validación), restaurando la mejor
época; recorte de gradiente; programador de la tasa de aprendizaje;
pesos de clase balanceados; 5 semillas promediadas en la evaluación final.
Cada entrenamiento tarda 7–12 segundos en una GPU de consumo.

### M24. ¿Qué framework usaron?

**Respuesta corta.** PyTorch, con CUDA en una GPU RTX 5060 Ti. Lo elegimos
por el control fino del ciclo de entrenamiento (criterio de época, focal
loss, poda de Optuna).

---

## Redes neuronales: por qué no ganaron

### M25. ¿Por qué las redes no superaron a la regresión logística?

**Respuesta corta.** Porque con esta representación no aprenden nada que
generalice. La pérdida de validación de un modelo que dice 1/3 a cada clase
es ln 3 ≈ 1.099, y las redes nunca bajan de ahí con ninguna configuración.
Las variables ya son resúmenes de varios días (retornos de 10 días,
momentum de 60, distancia a la media de 200), así que darle a la red 10 o
20 días de esos resúmenes no le aporta información nueva; y la etiqueta de un
día es casi ruido. Achicar la LSTM 57 veces no cambia nada: no es problema
de capacidad ni de regularización.

### M26. ¿No será que no las ajustaron bien?

**Respuesta corta.** Eso fue justo lo que señalaron los revisores del paper,
y por eso hicimos v5: una búsqueda de Optuna con 17–20 hiperparámetros por
red, sobre el mismo año de decisión que los modelos clásicos y sin mirar la
prueba. El resultado no cambió: la LR siguió arriba y con más margen. La
mejora más grande para las redes no fue un hiperparámetro sino elegir la
época por F1 de validación (+0.059 en la LSTM). Reconocemos que la búsqueda
es simétrica en procedimiento pero no en dimensión (las redes tienen más
hiperparámetros con menos intentos); por eso afirmamos solo que una
búsqueda realista no cambia el orden.

### M27. ¿Qué significa que la pérdida de validación no baje de ln 3?

**Respuesta corta.** Que la red, como estimador de probabilidades, no es
mejor que el azar en datos que no vio. ln 3 = 1.0986 es la entropía cruzada
de predecir 1/3 para cada clase; predecir la proporción 30/40/30 da 1.089. Las
redes quedan en ~1.09–1.10. Por eso el paro temprano por pérdida restauraba
la época 1 o 2: todo lo que aprendían después era ruido del entrenamiento.

### M28. ¿Las redes ven la misma información que la LR?

**Respuesta corta.** Casi. Hay una asimetría que detectamos al revisar el
código: la ventana de las redes termina el día **anterior** al que se
predice (días *t − lookback* a *t − 1*), mientras la LR ve el día *t*. No es
fuga de información (a las redes les falta un día, no les sobra), pero es
una desventaja. La medimos: a la LR, quitarle el día *t* le cuesta 0.007
de F1, mucho menos que la diferencia con las redes (0.03–0.045 en 2025), y
las redes no bajan del azar en validación con ninguna configuración, así
que no cambia la conclusión. La corrección es construir la ventana hasta
*t*.

### M29. ¿Con más datos ganarían las redes?

**Respuesta corta.** Posiblemente. La literatura donde las redes ganan
(Gu, Kelly y Xiu, 2020) usa ~30 000 acciones y 60 años. También podrían
ganar con entradas crudas (precios minuto a minuto o el libro de órdenes),
donde la red tiene que aprender las variables, o con horizontes más largos.
Nuestra conclusión está acotada a este régimen: 7 acciones, datos diarios,
variables ya construidas y señal de un día.

### M30. ¿Por qué no probaron GRU, Transformer o TabNet?

**Respuesta corta.** No los corrimos. El TT fijó cinco modelos, y el
diagnóstico mostró que el límite viene de la señal en los datos, no de la
arquitectura: redes muy distintas y de tamaños muy distintos llegan a la
misma pérdida de validación. Una GRU es una LSTM simplificada; un
Transformer necesita muchos más datos o pre-entrenamiento; y en datos
tabulares de este tamaño los árboles suelen igualar a TabNet. Además de los
cinco, solo probamos LightGBM (igual que XGBoost).

> Nunca digas que se probaron. Documentos antiguos los listaban como
> "probados"; se corrigió.

### M31. ¿Y Random Forest, SVM o k-NN?

**Respuesta corta.** Tampoco se corrieron. Random Forest es otro conjunto
de árboles (en paralelo en vez de en secuencia), una SVM lineal tiene la
misma frontera que la LR, una SVM con kernel cuesta entre O(n²) y O(n³) y no
da probabilidades sin calibración, y k-NN se degrada con 61 dimensiones.
Ya cubrimos los sesgos inductivos principales: lineal, árboles, recurrente
y convolucional.

### M32. ¿Probaron combinar modelos (ensambles)?

**Respuesta corta.** Sí: stacking, promedio simple y mezclas con pesos
optimizados por F1 o por Sharpe. Ninguno superó a la LR sola. Cuando un
modelo domina y los demás cometen errores parecidos, mezclarlos solo agrega
ruido; y los pesos óptimos en 2024 no sirvieron en 2025. Lo que sí usamos es
promediar varias **semillas** del mismo modelo para reducir la varianza.

### M33. ¿Cuál es la diferencia entre "modelo global" y "por acción"? ¿Cuál es mejor?

**Respuesta corta.** Global = un solo modelo entrenado con las 7 acciones
juntas (~10 500 filas); por acción = 7 modelos de ~1 500 filas. Los
comparamos sobre exactamente los mismos días: el global gana o empata en los
cinco modelos y en la LR gana 18 de 21 comparaciones (p = 0.002). Tiene 7
veces más datos, y como la etiqueta es relativa a cada acción y las
variables son razones, los patrones son comparables entre acciones.

---

## Cambios respecto al TT1

### MT1. En TT1 las redes tenían arquitectura fija. ¿Por qué no buscaron hiperparámetros desde el inicio?

**Respuesta corta.** El TT1 lo justificó por costo computacional y por
comparar las tres redes en igualdad. Después medimos que un entrenamiento
tarda 7 a 12 segundos en GPU, así que el costo no era el límite, y en v5
hicimos la búsqueda con Optuna (80 intentos, 17–20 hiperparámetros por red),
que era el trabajo futuro que el propio TT1 proponía. Las redes no
superaron a los clásicos.

### MT2. ¿Qué era la CNN 1D "como ablación"?

**Respuesta corta.** En TT1 la CNN 1D se diseñó como la CNN-LSTM sin el
bloque LSTM: mismo bloque convolucional y misma entrada, con promedio global
en vez de LSTM. Así la diferencia entre ambas medía el aporte del bloque
recurrente. En TT1 la CNN-LSTM ganaba por 0.012 a 0.025; en v5 sus
intervalos de confianza se traslapan (0.372 contra 0.359), así que el
bloque recurrente no aporta una diferencia significativa.

### MT3. En TT1 la LR era one-vs-rest y ahora es multinomial. ¿Por qué?

**Respuesta corta.** One-vs-rest entrena tres clasificadores binarios
independientes (cada clase contra las demás) y sus probabilidades no
compiten entre sí. La multinomial modela las tres clases juntas con
softmax, que es lo natural cuando las clases son excluyentes y lo que
optimiza directamente la entropía cruzada de tres clases.

### MT4. En TT1 la LSTM era unidireccional, en el paper bidireccional y ahora unidireccional. ¿Por qué tantos cambios?

**Respuesta corta.** TT1 la fijó unidireccional a priori; en v4 se usó
bidireccional (2 × 128), que es válido porque toda la ventana es pasado; en
v5 dejamos que Optuna decidiera y eligió unidireccional. Que la decisión no
cambie el resultado confirma que la arquitectura no es la limitante.
