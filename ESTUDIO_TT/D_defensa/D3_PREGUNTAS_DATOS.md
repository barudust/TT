# D3 — Preguntas de datos, etiqueta y variables

> Respuesta corta = lo que dices. "Si repreguntan" = el fondo. Detalle en
> [A1](../A_modelo/A1_DATOS_Y_ETIQUETA.md) y [A2](../A_modelo/A2_VARIABLES.md).

---

## Datos

### DA1. ¿Qué datos usaron y de dónde?

**Respuesta corta.** Precios diarios (apertura, máximo, mínimo, cierre y
volumen) de AAPL, NVDA, TSLA, AMZN, MSFT, GOOGL y META de 2013-12-31 a
2025-12-29, más el S&P 500 (a través del fondo SPY) y el índice de
volatilidad VIX, todo de Yahoo Finance con la biblioteca `yfinance`, con
precios ajustados por *splits* y dividendos. Son 3 017 días por acción y
21 119 filas en total.

### DA2. ¿Por qué ajustar por splits y dividendos?

**Respuesta corta.** Porque una división de acciones (por ejemplo, 1 en 4)
haría parecer que el precio cayó 75 % en un día. El ajuste corrige la serie
histórica para que los retornos reflejen solo movimientos reales.

### DA3. ¿Por qué agregar el S&P 500 y el VIX si predicen acciones individuales?

**Respuesta corta.** Porque las acciones no se mueven solas: cuando cae el
mercado caen casi todas, y cuando el VIX se dispara hay pánico general. Sin
eso el modelo no distingue una caída propia de una caída de todo el mercado.
De hecho, las variables del VIX y del S&P 500 terminaron siendo las de más
peso en el modelo.

### DA4. ¿Qué pasa con el sesgo de supervivencia?

**Respuesta corta.** Existe: las 7 son empresas que crecieron; una que
hubiera quebrado no estaría. Es una limitación explícita. La conclusión
principal es comparativa entre modelos con los mismos datos, así que el
sesgo afecta a todos por igual; pero los niveles absolutos de ganancia
podrían estar inflados. Extender al S&P 500 histórico, con empresas que
salieron del índice, es trabajo futuro.

### DA5. ¿Por qué desde 2014 y por qué 2025 como prueba?

**Respuesta corta.** Desde 2014 tenemos todos los indicadores completos
(la media de 200 días necesita casi un año de historia, por eso se
descargó desde 2013) y cubrimos varios regímenes: alcista largo, COVID,
recuperación, año bajista 2022 y auge de la IA. 2025 era el último año
completo cuando se fijó la prueba en v4, antes de ver resultados. No fue un
año fácil: retorno por debajo de la mediana histórica y volatilidad alta.

### DA6. ¿Limpiaron los datos? ¿Hubo valores faltantes?

**Respuesta corta.** Las 7 acciones tienen datos diarios completos. Las
primeras filas de cada serie no tienen todos los indicadores (por el
calentamiento de las medias largas) y se descartan. Si falta un día del
contexto de mercado se usa el último valor conocido, nunca uno futuro.

---

## Etiqueta

### DE1. ¿Cómo definieron COMPRAR, MANTENER y VENDER?

**Respuesta corta.** Con el retorno logarítmico del día siguiente,
`ln(C_{t+1}/C_t)`. Si está en el 30 % más alto de los retornos del último
año (252 días) de esa acción, es COMPRAR; si está en el 30 % más bajo, es
VENDER; si no, MANTENER. El umbral se calcula solo con días anteriores.

### DE2. ¿Por qué percentiles móviles y no un umbral fijo como ±1 %?

**Respuesta corta.** Porque la volatilidad cambia mucho entre épocas: en un
año tranquilo casi ningún día pasa de ±1 % y en 2020 casi todos lo
pasaban. Con un umbral fijo la etiqueta cambiaría de significado y de
proporción cada año. El percentil móvil se adapta solo: "subida fuerte" es
fuerte **para ese momento**.

### DE3. ¿Por qué 30/70 y no otros cortes?

**Respuesta corta.** Da clases balanceadas (~30/40/30) con una clase clara
de "no operar", y es la elección usual en la literatura. Probamos 20/80,
25/75, 35/65 y 40/60. Con 40/60 el modelo empeora (kappa −45 %) y sigue
diciendo MANTENER el 53 % de los días aunque solo el 20 % lo sea. Con 20/80
el kappa sube un poco, pero MANTENER pasa a ser el 61 % de los días y casi
no se operaría.

**Si repreguntan "¿por qué comparan con kappa y no con F1?":** porque el F1
no es comparable entre etiquetas con distinta proporción de clases (cambia
cuánto vale el azar); el kappa descuenta el azar y sí lo es.

### DE4. ¿Por qué una ventana de 252 días?

**Respuesta corta.** Es un año de mercado. Más corta da percentiles
inestables; más larga tarda en adaptarse a un cambio de régimen.

### DE5. ¿Por qué retorno logarítmico?

**Respuesta corta.** Se puede sumar entre días (el retorno de varios días es
la suma de los diarios), es simétrico entre subidas y bajadas
equivalentes y su distribución es más parecida a la normal.

### DE6. ¿Por qué horizonte de un día?

**Respuesta corta.** Es la definición directa de una señal diaria, da el
máximo de ejemplos y es el caso más exigente para comparar modelos. Probamos
2, 3, 5, 7 y 10 días: con 5–7 días el F1 sube a ~0.43, pero eso ya es otro
problema (una señal semanal), así que lo dejamos como trabajo futuro.

### DE7. ¿Cómo evitan que la etiqueta use información del futuro?

**Respuesta corta.** La etiqueta, por definición, mira un día adelante
(es lo que se quiere predecir) y **nunca** se usa como entrada. Lo que
podría filtrar información son los umbrales: se calculan con
`shift(1)`, es decir, con los 252 días **anteriores**, sin incluir el día
que se etiqueta.

### DE8. ¿La proporción de clases es 30/40/30 todos los años?

**Respuesta corta.** En promedio sí, pero varía por año porque el umbral
sale del año anterior: si el año nuevo es más agitado, hay más COMPRAR y
VENDER. Por ejemplo, MANTENER fue 32 % en 2022 y 48 % en 2023. Eso explica
por qué un ajuste fijo del umbral de MANTENER no funciona.

### DE9. ¿No pierden información al no distinguir una subida de 1 % de una de 5 %?

**Respuesta corta.** Sí, es una simplificación deliberada: modelar la
magnitud es regresión, y el ruido diario domina. Para usar la magnitud
habría que agregar tamaño de posición (por ejemplo, según volatilidad), que
dejamos como trabajo futuro.

### DE10. ¿Por qué no usaron la triple barrera que proponían al inicio?

**Respuesta corta.** La triple barrera cierra cada ejemplo en un día
distinto (cuando toca una barrera), mezcla horizontes y requiere calibrar
dos parámetros más (ancho de la barrera y plazo). Para una comparación
limpia entre cinco modelos preferimos un horizonte fijo con umbrales
adaptativos, que consigue lo mismo que buscábamos de la triple barrera
(adaptarse a la volatilidad) sin parámetros adicionales.

---

## Variables

### DV1. ¿Cuántas variables usan y cuáles?

**Respuesta corta.** 61 base en 9 familias: retornos (5), momentum (4),
medias móviles (9), volatilidad (8), osciladores como RSI, MACD y
estocástico (9), volumen y flujo (8), forma de la vela (7), calendario (5)
y contexto de mercado del S&P 500 y el VIX (6). El modelo en producción
agrega 15 interacciones: 76 en total.

### DV2. ¿Por qué 61 y no más ni menos?

**Respuesta corta.** No es un número mágico: es lo que resulta de cubrir las
9 familias estándar de indicadores técnicos. Probamos con más (94 y 93
variables, con bonos, dólar, oro, petróleo y sectores) y no mejora. Probamos
con menos (filtrando con Pearson, VIF, Spearman y SHAP) y fue peor en 11 de
15 casos.

### DV3. ¿No hay variables redundantes?

**Respuesta corta.** Sí, varias están correlacionadas (RSI y estocástico,
por ejemplo). Lo probamos: quitarlas con filtros fue peor. La regularización
del modelo reparte el peso entre variables correlacionadas mejor que un
filtro que mira cada variable por separado.

**Si preguntan por VIF:** es `1/(1 − R²)` de explicar una variable con las
demás; un VIF alto indica redundancia. Se usó en el filtro para la LR.

### DV4. Explique el RSI / el MACD / el ATR.

- **RSI:** de 0 a 100, compara el promedio de subidas con el de bajadas
  recientes (14 días): `100 − 100/(1 + subidas/bajadas)`. Más de 70 se
  interpreta como "sobrecomprado".
- **MACD:** diferencia entre la media exponencial de 12 y la de 26 días;
  su media de 9 días es la línea de señal. Lo dividimos entre el precio
  para que sea comparable entre acciones.
- **ATR:** promedio de 14 días del rango verdadero, el mayor entre
  máximo − mínimo y los saltos contra el cierre anterior. Mide cuánto se
  mueve la acción en un día típico.

### DV5. ¿Por qué codificar el día de la semana con seno y coseno?

**Respuesta corta.** Porque el calendario es circular: con números 1 a 5 el
viernes quedaría lejos del lunes; en el círculo quedan cerca. Con una
columna por día (one-hot) todos los días serían igual de distintos.

### DV6. ¿Cuáles variables son las más importantes?

**Respuesta corta.** Las de volatilidad y de mercado: VIX normalizado,
volumen, VIX, volatilidad del S&P 500, retorno del S&P 500, rango del día,
ATR normalizado, volumen relativo, momentum del S&P 500 y sombra superior de
la vela. Es coherente con que lo predecible es la magnitud del movimiento
(la volatilidad se agrupa) y no su dirección.

### DV7. ¿Qué son las 15 interacciones y por qué las agregaron?

**Respuesta corta.** Productos de pares de las 10 variables más importantes
(por ejemplo, VIX normalizado × volatilidad del S&P 500). Permiten que en una
regresión lineal el efecto de una variable dependa de otra. Mejoraron 0.023
el F1 en 2025, pero en validación y en seis años de origen rodante empatan
con el modelo sin ellas; las mantenemos porque no empeoran, y las
presentamos como equivalentes, no como mejora.

### DV8. ¿Cómo garantizan que la API calcule las variables igual que en el entrenamiento?

**Respuesta corta.** El código de la API (`api/ml/features.py`) es una copia
exacta de las fórmulas del entrenamiento, hay pruebas automáticas de las
variables, y la etiqueta en vivo coincide al 100 % con la del dataset
(también probado).

### DV9. ¿Por qué RobustScaler?

**Respuesta corta.** Escala con la mediana y el rango intercuartílico, que
no se distorsionan con días extremos como marzo de 2020. Con media y
desviación estándar esos días inflarían la escala y aplastarían al resto.
Optuna lo eligió para la LR y las tres redes.

### DV10. ¿El escalador se ajusta con todos los datos?

**Respuesta corta.** No: en la evaluación, solo con el periodo de
entrenamiento, y se aplica igual a validación y prueba. Ajustarlo con todos
filtraría información del futuro (la mediana y los cuartiles de la
prueba).

---

## Cambios respecto al TT1

### DT1. En TT1 cada modelo usaba sus propias variables. ¿Por qué lo quitaron?

**Respuesta corta.** Por dos razones. Primera, el propio TT1 concluyó que
esa asimetría impedía comparar arquitecturas: en el experimento C la LSTM
tenía 3 variables y XGBoost 25. Segunda, lo medimos: cada modelo con las 61
variables fue mejor que con su filtro en 11 de 15 casos. La regularización
del modelo selecciona mejor que un filtro que mira cada variable por
separado. Desde v4 los cinco modelos reciben las mismas 61.

### DT2. En TT1 el experimento A probaba en 2024–2025. ¿Por qué cambió?

**Respuesta corta.** Porque así A no se podía comparar con B y C, que
probaban solo en 2025: cualquier diferencia podía deberse al año y no a la
cantidad de historia. Desde v4 los tres prueban en 2025 y solo cambia el
entrenamiento (10, 6 o 4 años).

### DT3. ¿Qué eran los canales OHLCV de la CNN-LSTM en TT1 y por qué ya no están?

**Respuesta corta.** En TT1 la CNN-LSTM y la CNN 1D recibían, además de las
variables, los precios de apertura, máximo, mínimo y cierre divididos entre
el cierre del primer día de la ventana, y el volumen dividido entre el
máximo de la ventana, para que las convoluciones aprendieran formas de
velas. Se quitaron para que los cinco modelos tuvieran exactamente la misma
entrada; las formas de vela ya están descritas por las 7 variables de vela.
