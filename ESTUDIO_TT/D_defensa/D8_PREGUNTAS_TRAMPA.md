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

## Consejos para el día

1. **Reconoce primero, explica después.** Un sinodal detecta una evasiva al
   instante.
2. **Ten a mano 5 cifras:** 0.404 [0.379, 0.428] y Sharpe +0.89 (2025);
   0.35 de media en seis años; 0.394 máximo en cualquier año; 0.354 en 2026;
   ln 3 en las redes.
3. **Distingue paper y TT:** el paper es la corrida de la Etapa 3 + Etapa 4; el TT es todo.
4. **No digas "probamos"** de algo que no se corrió (CatBoost, GRU,
   Transformer, TabNet, Random Forest).
5. **Si no sabes:** "no lo medimos; se podría medir así…".
