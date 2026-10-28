# D8 — Preguntas trampa y cómo responderlas

> Preguntas diseñadas para incomodar. La regla para todas: **reconoce lo que
> es cierto, da la cifra y explica qué hiciste al respecto.** Nunca inventes;
> "eso no lo medimos, pero se podría medir así…" es una buena respuesta.

---

### T1. "Su modelo es apenas mejor que una moneda. ¿Qué aportaron?"

Que medimos con rigor cuánto se puede extraer de datos públicos diarios con
cinco familias de modelos: poco y de forma inestable entre años (F1 ≈ 0.35
de media en seis años, azar 0.33). Y que en ese régimen un modelo lineal bien
regularizado iguala o supera a redes profundas, con dos protocolos, un
prueba año por año y una evaluación en vivo. Un resultado negativo bien medido es
un resultado; y la hipótesis de mercado eficiente predice justamente que
esto debería ser casi impredecible.

### T2. "Si la regresión logística gana, ¿para qué entrenaron cinco modelos?"

Porque a priori no lo sabíamos: la hipótesis del trabajo era la contraria
(que el aprendizaje profundo ganaría). La contribución es la evidencia
comparativa. Si solo hubiéramos entrenado la LR, no podríamos afirmar nada
sobre las redes.

### T3. "Hicieron muchas versiones hasta que les salió un buen número."

Al revés: las versiones posteriores hicieron el protocolo **más
estricto**, y varias "mejoras" las declaramos como no significativas (las
interacciones solo mejoran en 2025; el ajuste de MANTENER no es
significativo). Reportamos la prueba año por año, donde la LR empata con XGBoost, y
2026, donde el modelo rinde menos que en 2025. Si buscáramos el mejor número,
no publicaríamos esos.

### T4. "2025 fue el mejor año del modelo. Eligieron la prueba a conveniencia."

2025 se fijó en la Etapa 3 como el último año completo, antes de conocer los
resultados, para que los tres experimentos compartieran el año de prueba. Lo
decimos nosotros mismos y por eso reportamos seis años de prueba año por año y
2026.

### T5. "Las redes están mal diseñadas; con una buena arquitectura ganarían."

Probamos 17–20 hiperparámetros por red con Optuna, incluyendo capas,
unidades, filtros, kernel, ventana, pérdida y pooling. Medimos que su
pérdida de validación nunca baja del azar (ln 3) con ninguna configuración y
que una LSTM 57 veces más chica rinde igual. Cuando arquitecturas y tamaños
tan distintos convergen al mismo nivel, el límite está en la información
de los datos, no en el diseño.

### T6. "La ventana de sus redes termina un día antes. Les quitaron información."

Es correcto: la ventana va de *t − lookback* a *t − 1* y la LR ve el día
*t*. No es fuga de información, es una desventaja. La medimos: a la LR,
quitarle el día *t* le cuesta 0.007 de F1, mientras que la diferencia con las
redes es de 0.03 a 0.045 en 2025 y de 0.02 a 0.06 en la prueba año por año; y las
redes no superan el azar en validación con ninguna configuración. No cambia
la conclusión, pero la corrección (ventana hasta *t*) está en el trabajo
futuro.

### T7. "¿Probaron Transformers? Son el estado del arte."

No los corrimos. Necesitan muchos más datos o pre-entrenamiento que ~10 500
filas, y el diagnóstico mostró que el límite no es la arquitectura. Sería
interesante con cientos de acciones y transferencia de aprendizaje; está en
trabajo futuro.

> No digas que se probaron. Solo LightGBM se probó además de los cinco.

### T8. "Un Sharpe de +0.89 es excelente. ¿Por qué no lo venden?"

Porque con un año de datos el error estándar del Sharpe es ≈ 1: su
intervalo va de alrededor de −1 a +3. En seis años el Sharpe medio de la LR
es +0.22, no significativo. Y no modelamos deslizamiento ni tamaño de
posición. No lo usaríamos con dinero real.

### T9. "Su plataforma casi siempre dice MANTENER. Está descompuesta."

No: es un comportamiento explicado. El modelo sabe cuándo habrá
movimiento pero no hacia dónde, así que en días de baja volatilidad (VIX bajo
su media) se abstiene. Lo corregimos parcialmente bajando el peso de
MANTENER al entrenar (en 2026 pasó de 60 % a 40 %, con 35 % real), pero en
meses muy tranquilos sigue predominando; es preferible a operar sin
información.

### T10. "Ustedes mismos dicen que las métricas de la plataforma estaban mal."

Sí, en una auditoría del 30 de septiembre encontramos y corregimos errores
de versiones anteriores (comparaciones contra el día anterior, F1 que eran
precisiones, Sharpe sobre el precio). Hoy la plataforma mide exactamente lo
mismo que la tesis, y hay pruebas automáticas que lo verifican, como la que
compara la etiqueta en vivo con la del entrenamiento.

### T11. "Las interacciones las eligieron mirando la prueba. Eso es trampa."

La decisión de adoptarlas sí se tomó mirando 2025, y por eso no las
presentamos como mejora: en validación 2024 y en seis años de origen rodante
empatan con el modelo sin ellas. Las mantenemos porque no empeoran. La
selección de **cuáles** variables usar sí se hizo sin la prueba (las 10 de
mayor coeficiente en entrenamiento).

### T12. "La base de datos no está normalizada."

Las tablas base están en 3FN; las de señales y métricas tienen columnas
derivadas a propósito, como registro de lo que se calculó y mostró con cada
versión del modelo. No hay riesgo de anomalías porque un solo proceso
recalcula todo desde la fuente en cada actualización. Si se necesitara 3FN
estricta: tabla de versiones de modelo, vistas para métricas y aciertos, y
quitar confianza y precio duplicados.

### T13. "¿Por qué no usaron una base 'de verdad' como PostgreSQL?"

Porque la base es pequeña, con un solo escritor y reconstruible; SQLite no
necesita servidor ni costo. El código usa SQLAlchemy con tipos genéricos y el
`docker-compose` ya trae PostgreSQL: cambiar es una variable de entorno.

### T14. "En TT1 entregaron otra cosa: otras variables, otro ganador, PostgreSQL… ¿cuál es su trabajo?"

El TT1 fue la primera iteración y dejó explícitas sus limitaciones: cada
modelo con distintas variables, redes con hiperparámetros fijos, un solo
año de prueba y la aplicación sin terminar. En TT2 resolvimos cada una. El
ganador cambió de XGBoost a la LR porque al darle a la LR las mismas 61
variables mejoró (de 0.355 a 0.392 por acción, y 0.404 global) y XGBoost no; en seis años ambos empatan. La conclusión
de fondo es la misma del TT1: los clásicos igualan o superan a las redes,
ahora con pruebas estadísticas. PostgreSQL se cambió por SQLite porque el
ETL ya corre en el mismo proceso que la API (un solo escritor) y la base es
reconstruible. Detalle en [D1](D1_TT1_VS_TT2.md).

### T14b. "En TT1 dijeron que la ventaja de los clásicos era por la asimetría de variables. ¿Entonces su comparación no vale?"

Al contrario: tomamos esa limitación y la corregimos. Desde la Etapa 3 los cinco
modelos reciben exactamente las mismas 61 variables, y los clásicos siguen
arriba (en la Etapa 4 la LR es significativamente mejor que las tres redes). La
asimetría no era la causa; la causa es que con estos datos las redes no
aprenden nada que generalice (su pérdida de validación no baja del azar).

### T14c. "El TT1 dice 54 características y ustedes dicen 61."

El texto del TT1 tiene un error de conteo: su propia Tabla 4 lista 61
variables y el código siempre calculó 61. Lo corregimos.

### T15. "¿No es circular entrenar con 2018–2025 y luego decir que funciona?"

El modelo en producción no se evalúa con esos años: se evalúa en 2026, que
nunca vio (F1 0.354). Lo que se validó con entrenamiento/validación/prueba
fue el procedimiento; reentrenar con todos los datos disponibles es la
práctica estándar.

### T16. "La regresión logística es un modelo de los años 50. ¿Esto es un TT de 2026?"

La elección de un modelo se juzga por su desempeño medido, no por su
antigüedad. Probamos modelos modernos con búsqueda seria y la LR fue igual o
mejor, más barata, determinista e interpretable. Esa es una conclusión útil
y alineada con la literatura reciente sobre datos tabulares (Grinsztajn et
al., 2022).

### T17. "¿Qué es lo más débil de su trabajo?"

Que la señal es débil e inestable entre años: el paper usa un solo año de
prueba que resultó el mejor; en seis años el F1 de la LR va de 0.31 a 0.39 y
en 2026 es 0.35. Lo que sí se sostiene en todas las pruebas es la conclusión
comparativa. Y como limitaciones de alcance: 7 acciones de un sector, sin
datos alternativos y con un backtest simplificado.

### T18. "Si empezaran de nuevo, ¿qué harían distinto?"

Usar desde el inicio el protocolo de la Etapa 4 (decisiones solo en validación,
mismas filas para todos, intervalos de confianza) y la prueba año por año como
evaluación principal; definir la etiqueta después de explorar horizontes;
incluir costos como métrica principal; y construir las ventanas de las redes
hasta el día *t*.

---

## Preguntas sobre los experimentos que no funcionaron

> La idea que hay detrás de todas: **ninguna etapa se hizo sabiendo su
> resultado.** Cada una respondió a algo concreto: el resultado anterior, la
> literatura, los revisores del artículo, la sinodal o el sistema en
> operación. El registro completo, con el motivo de cada prueba, está en el
> Anexo B del reporte
> (`REPORTE_TECNICO/tablas/ANEXO_B_REGISTRO_DE_EXPERIMENTOS.md`).

### T19. "En TT1 ya sabían que las redes perdían. ¿Por qué siguieron?"

Porque el TT1 no demostraba eso. Su comparación era dispareja: cada modelo
recibía variables distintas (de 3 a 25), las redes tenían hiperparámetros
fijos y su ventana se eligió con la prueba. El propio reporte de TT1 lo dijo
como su principal limitación. Además, la literatura que revisamos reportaba
redes por encima de la LR y de XGBoost en clasificación (Nabipour 2020,
Siswara 2024, Long 2019). Con esa evidencia, lo razonable era igualar las
condiciones antes de concluir, y eso fue lo que hicimos en las Etapas 2 a 4.

### T20. "¿Para qué probaron unas treinta técnicas si al final se quedaron con la LR?"

Porque "las redes no superan a un modelo lineal" solo es creíble si las
redes tuvieron una oportunidad real. Si no las hubiéramos optimizado, la
primera objeción habría sido "no las ajustaron bien", y de hecho fue lo que
nos pidieron los revisores del artículo. Cada prueba descartada cierra una
objeción. Los resultados negativos también son resultados: muestran que el
límite está en la información de los datos y no en el modelo.

### T21. "En agosto rehicieron todo. ¿No bastaba con lo de junio?"

No. Los revisores del artículo de MICAI pidieron una búsqueda de
hiperparámetros comparable para las redes. Al revisar, encontramos que las
redes estaban en desventaja: su paro temprano restauraba la época 1 o 2 y su
ventana se había elegido con la prueba. Era posible que con un protocolo
justo las redes mejoraran, así que había que comprobarlo. Fue su mejor
oportunidad, y aun así la LR ganó con significancia en los tres
experimentos.

### T22. "Las mejoras de la Etapa 5 las midieron sobre 2025. Eso es buscar hasta que salga."

Es cierto que se midieron sobre 2025, y por eso solo las usamos para
**descartar**. La regla de adopción se fijó antes de probar (≥ 0.005 de F1 o
≥ 0.10 de Sharpe). La única técnica adoptada, las interacciones, la
validamos después con un origen rodante 2019–2024 y resultó equivalente, no
mejor. Los resultados de A, B y C y los del artículo son **sin** ellas. Y la
prueba ciega de 2026 no intervino en ninguna decisión.

### T23. "Si a varios días el modelo funciona mejor, ¿por qué no cambiaron el horizonte?"

(Si preguntan el número: con 5–7 días la LR llegó a F1 ≈ 0.43 en 2025. No
lo ofrezcas tú; si lo piden, dilo con las tres razones.)

Por tres razones. Primera, el problema que planteamos es una señal diaria, y
la plataforma publica una recomendación por día: a cinco días sería otro
problema. Segunda, esa cifra se midió sobre 2025, así que cambiar la etiqueta
después de verla sería mover la meta. Tercera, el F1 de etiquetados con
distinta proporción de clases no se puede comparar directamente. Lo dejamos
como trabajo futuro, con esa exploración como evidencia de que podría
funcionar.

### T24. "En la validación 2024 la LR fue la peor. ¿Por qué la eligieron?"

Porque la validación de un año no sirve para escoger. Lo comprobamos: elegir
cada año el modelo que gana en validación da un F1 medio de 0.342–0.344,
peor que quedarse siempre con la LR (0.350–0.360). El criterio que
declaramos es otro: entre los modelos que empatan en seis años de prueba (LR
y XGBoost), elegir el más simple y el que paga menos costos. La prueba ciega
de 2026 lo confirmó: la LR quedó primera en F1.

### T25. "La calibración isotónica mejora a XGBoost. ¿Por qué no la usaron?"

Porque aun calibrado XGBoost llega a 0.371, por debajo de la LR sin calibrar
(0.404). Además, aplicar un paso extra a un solo modelo rompe la igualdad de
condiciones de la comparación.

### T26. "¿Por qué no agregaron más datos de mercado: tasas, dólar, oro…?"

Sí lo hicimos, tres veces: 181 variables (puntajes z, rezagos e
interacciones), 94 variables con contexto macroeconómico y sectorial, y 93
variables con bonos, volatilidad del VIX, crédito, dólar, oro, petróleo e
índices. Ninguna mejoró de forma consistente. Más variables dan a los
modelos más formas de ajustarse al ruido.

### T27. "¿Cuándo decidieron parar y por qué ahí?"

Cuando ninguna técnica superaba la variación natural del mismo modelo entre
años: las pruebas movían el F1 entre −0.05 y +0.03, y la LR sola cambia unos
0.07 de un año a otro. Seguir probando sobre los mismos datos aumenta la
probabilidad de encontrar una mejora que es solo ruido. Lo que sí podría
cambiar el resultado (otro horizonte, más acciones, datos externos) cambia el
problema, y lo dejamos como trabajo futuro.

### T28. "En la Tabla 34 la proporción móvil tiene mejor F1 y kappa que el peso × 0.90. ¿Por qué eligieron el peso?"

Porque en F1 y kappa empatan (0.367 contra 0.365 y 0.070 contra 0.068: dos
milésimas), y el peso × 0.90 da más Sharpe en los tres periodos que
revisamos: 2019–2024 (+0.54 contra +0.51), 2025 (+0.93 contra +0.81) y 2026
(+0.29 contra +0.16). Entre los pesos de reentrenamiento, el × 0.90 fue el
mejor en las tres métricas a la vez. Todo se decidió con 2019–2024, sin ver
2025 ni 2026.

### T29. "¿La LR saca 0.404, 0.390 o 0.373 en 2025? Cada tabla dice otra cosa."

Son el mismo año con montajes distintos, y cada tabla compara solo dentro de
sí misma. 0.404 es el resultado principal: Etapa 4, Experimento B, seis años
de entrenamiento (Tabla 25). 0.373 es la prueba año por año: cinco años de
entrenamiento (2019–2023) y los ajustes de la Etapa 3 (Tabla 30). 0.390 es la
base de la reimplementación que usamos en la Etapa 5 para probar variables
nuevas sin tocar el código de la Etapa 4 (Tabla 32). Lo que se lee en cada
tabla es la diferencia entre variantes, no el número absoluto.

### T30. "Con los ajustes de la Etapa 4, XGBoost gana el promedio de seis años. ¿No debieron elegir XGBoost?"

Los ajustes de la Etapa 4 se eligieron con 2024, así que para 2020–2023 son
información del futuro; por eso la prueba que cuenta es la de los ajustes de
la Etapa 3, que no vieron ningún año de prueba (LR 0.360, XGBoost 0.356). Con
cualquiera de los dos, LR y XGBoost quedan a menos de 0.01, menos de lo que
cambia el mismo modelo de un año a otro: es un empate. Ante el empate
decidimos con criterios que no dependen del año: parámetros (186 contra 485
árboles), rotación (0.38 contra 0.65), Sharpe con costos, interpretabilidad y
determinismo. Y en la prueba ciega de 2026, que nadie vio, la LR quedó
primera.

### T31. "En la Tabla 34 la proporción fija tiene el mayor Sharpe. ¿Por qué no la usaron?"

Porque el criterio principal es el F1-macro, no el Sharpe, y ahí la
proporción fija queda casi tres centésimas abajo (0.337 contra 0.365). Su
ventaja en Sharpe solo aparece en 2019–2024 (+0.58 contra +0.54); en 2025 da
menos (+0.88 contra +0.93). Además, fijar el 40 % de MANTENER le impone al
modelo la proporción del pasado, aunque el año cambie. Con el peso × 0.90 la
proporción sale del propio modelo.

---

## Consejos para el día

1. **Reconoce primero, explica después.** Un sinodal detecta una evasiva al
   instante.
2. **Ten a mano 5 cifras:** 0.404 [0.379, 0.428] y Sharpe +0.89 (2025);
   0.36 de media en seis años con los ajustes fijados de antemano (0.35 con
   los de la Etapa 4); ningún modelo llega a 0.40 en ningún año; 0.354 en
   2026; ln 3 en las redes.
3. **Distingue paper y TT:** el paper es la corrida de la Etapa 3 + Etapa 4; el TT es todo.
4. **No digas "probamos"** de algo que no se corrió (CatBoost, GRU,
   Transformer, TabNet, Random Forest).
5. **Si no sabes:** "no lo medimos; se podría medir así…".
