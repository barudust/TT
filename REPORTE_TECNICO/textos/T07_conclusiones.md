# T07 — Conclusiones: borrador del capítulo 7

---

## 7.1 Conclusiones generales

Este trabajo diseñó, implementó y evaluó cinco modelos para generar señales
diarias de compra, venta en corto o mantenimiento sobre las siete empresas
tecnológicas de mayor capitalización del mercado estadounidense: tres
arquitecturas de aprendizaje profundo (LSTM, CNN 1D y CNN-LSTM) y dos modelos
clásicos (Regresión Logística y XGBoost). La comparación se realizó en
igualdad de condiciones —las mismas 61 características, la misma partición
temporal, las mismas filas de evaluación, la misma búsqueda de
hiperparámetros y las mismas ocho métricas—, con un protocolo en el que
ninguna decisión usó el año de prueba.

El hallazgo central es que, con datos diarios públicos y una señal a un día,
**los modelos clásicos igualan o superan a las arquitecturas profundas**. La
Regresión Logística obtuvo el mayor F1-macro en el año de prueba en los tres
experimentos (0.406, 0.404 y 0.401) y fue significativamente mejor que los
otros cuatro modelos, con el mejor índice de Sharpe (+0.89; +0.62 con costos
de 10 puntos base). En seis años de prueba año por año, la Regresión
Logística y XGBoost no difieren significativamente y ambos superan a las tres
redes; en una prueba ciega con datos de 2026 la Regresión Logística volvió a
quedar primera en clasificación.

La señal que se puede extraer es débil y cambia entre años: el kappa de la
Regresión Logística es 0.12 en 2025 y cercano a 0.04 en 2026, y una prueba de
permutación detecta señal en 2025 pero no en 2024. Ninguna de las cerca de
treinta técnicas probadas para mejorar el resultado superó la variación
natural del mismo modelo entre años. Las redes no lograron reducir su pérdida
de validación por debajo del nivel del azar con ninguna configuración, lo que
indica que el límite no está en la arquitectura, sino en la información que
contienen los datos sobre la dirección del día siguiente.

El modelo seleccionado se integró en una plataforma web desplegada que cada
día hábil publica la recomendación para las siete acciones, evalúa las
recomendaciones anteriores contra lo ocurrido y muestra la comparación de los
cinco modelos.

## 7.2 Cumplimiento de los objetivos

**Objetivo general.** Cumplido: se implementaron y entrenaron modelos de
inteligencia artificial que recomiendan comprar, vender o mantener, se
evaluaron frente a modelos de referencia con una simulación económica y se
integraron en una aplicación web desplegada.

**Objetivo específico 1 — Implementar modelos para la estimación direccional
diaria.** Cumplido. Se implementaron los cinco modelos con scikit-learn,
XGBoost y PyTorch, sobre un conjunto de datos de siete acciones con 61
características y una etiqueta adaptativa por percentiles. Cada modelo se
entrenó de forma global y por acción en tres experimentos (120 corridas por
etapa), con búsqueda de hiperparámetros con Optuna.

**Objetivo específico 2 — Evaluar el desempeño.** Cumplido. Se evaluaron
ocho métricas para los cinco modelos sobre las mismas filas, una simulación
económica con y sin costos, intervalos de confianza bootstrap, una prueba de
permutación, una prueba año por año de seis años y una prueba ciega con datos
de 2026.

**Objetivo específico 3 — Comparar los modelos y determinar los mejores.**
Cumplido. La Regresión Logística es la mejor en la prueba principal en las
ocho métricas y supera con significancia a los otros cuatro; en seis años
empata con XGBoost y ambos superan a las redes; entre las tres redes no hay
diferencias significativas. Con el criterio de selección declarado se eligió
la Regresión Logística. Un modelo global para las siete acciones resultó
mejor o igual que un modelo por acción en los cinco modelos.

**Objetivo específico 4 — Desarrollar una aplicación web.** Cumplido. La
plataforma está desplegada en https://tt-frontend-womf.onrender.com, se
actualiza cada día hábil después del cierre, presenta cada recomendación con
su nivel de seguridad en palabras y su resultado posterior, y muestra la
comparación de los cinco modelos y material para usuarios sin conocimientos
de finanzas.

**Pregunta de investigación e hipótesis.** No se rechaza H₀: ninguna de las
tres arquitecturas de aprendizaje profundo supera de manera consistente a los
modelos de referencia. El trabajo diseñó e implementó las tres arquitecturas
que plantea su título; la evidencia indicó que el modelo que debía
desplegarse es el más simple.

## 7.3 Discusión

**Por qué gana un modelo lineal bien regularizado.** Con una señal débil, el
error de generalización está dominado por la varianza, y un modelo rígido y
fuertemente regularizado —la Regresión Logística final usa C = 0.000165—
acepta un poco de sesgo a cambio de casi no tener varianza. Las
características ya son transformaciones no lineales de la historia de varios
días (RSI, MACD, volatilidades, distancias a medias móviles), de modo que
combinarlas linealmente captura casi toda la información disponible, y las
ventanas que reciben las redes aportan información redundante. Además, unas
10 500 filas de entrenamiento son pocas para ajustar entre 67 000 y 276 000
parámetros sin aprender ruido. El resultado coincide con lo observado en
datos tabulares (Grinsztajn et al., 2022) y en estudios de mercado con
muestras de tamaño parecido (Patel et al., 2015), y contrasta con trabajos en
los que las redes ganan con decenas de miles de acciones y décadas de datos
(Gu, Kelly y Xiu, 2020). A diferencia de Nabipour et al. (2020), que en el
mercado de Teherán encuentran ventaja de las redes recurrentes en
clasificación binaria, aquí, con las mismas características para todos los
modelos, las redes no la tienen.

**Clasificación y dinero no siempre coinciden.** En 2025 XGBoost y la CNN 1D
tienen el mismo F1-macro (0.359) y Sharpe muy distintos (+0.46 y −0.46); en
2026 la CNN 1D tiene el F1 más bajo y el mejor Sharpe. Con un año de datos el
error estándar del Sharpe es cercano a 1, por lo que el desempeño económico
de un solo periodo no es un criterio estable de selección, y las conclusiones
económicas del trabajo son comparativas.

**La acción importa más que el modelo.** En la comparación publicada, la
acción explica 4.5 veces más la variación del Sharpe que el modelo. Para
quien quiera aplicar estas señales, elegir sobre qué acciones operar pesa más
que elegir un modelo más complejo.

**Por qué el modelo predice mantener en bloque.** Las variables con más peso
son las del VIX y del S&P 500, comunes a las siete acciones; cuando el
mercado está tranquilo, el modelo tiende a recomendar mantener para todas.
El ajuste del peso de la clase corrigió la proporción sin cambiar la etiqueta.

## 7.4 Limitaciones

- La señal es débil y cambia entre años; el desempeño de 2025 fue el mejor
  de la prueba año por año.
- Siete acciones de un solo sector y de un solo país, todas sobrevivientes;
  las conclusiones podrían no generalizarse a otros mercados.
- Solo datos de precios y volumen, sin noticias, fundamentales ni
  macroeconomía.
- Simulación simplificada: horizonte de un día, tamaño de posición fijo,
  ejecución al precio de cierre, venta en corto sin costo de préstamo y
  costos fijos por cambio de posición.
- La búsqueda de hiperparámetros es simétrica en procedimiento, no en
  dimensión.
- La ventana de las redes termina un día antes que la información de los
  modelos clásicos (efecto medido ≈ 0.007 de F1).
- Las 15 interacciones del modelo de producción se adoptaron observando
  2025; la validación posterior las encontró equivalentes.
- La plataforma usa el plan gratuito de Render: se suspende sin tráfico y la
  actualización programada solo corre si el servicio está activo.
- La plataforma es demostrativa y no constituye asesoría financiera.

## 7.5 Trabajo futuro

Las líneas de trabajo futuro que planteó TT1 —ajustar el periodo de
entrenamiento, integrar los módulos, desplegar la aplicación y realizar una
búsqueda sistemática de hiperparámetros— se realizaron en esta etapa. Las
líneas que quedan, en orden de valor esperado, son:

1. **Cambiar el horizonte** de forma explícita (por ejemplo, a cinco días),
   como un problema distinto del que aborda este trabajo.
2. **Ampliar el universo de acciones**, incluidas empresas que dejaron de
   cotizar, para que las redes cuenten con datos suficientes.
3. **Agregar datos gratuitos de otras fuentes**, como indicadores
   macroeconómicos (FRED) y sentimiento de noticias.
4. **Ajustar el tamaño de la posición** según la volatilidad y optimizar la
   estrategia considerando costos.
5. **Corregir la ventana de las redes** para incluir el día *t* y repetir el
   protocolo final.
6. **Otras arquitecturas** (GRU, Transformers), solo si se cuenta con más
   datos.
7. En la plataforma: restringir CORS, proteger `POST /admin/refresh`, agregar
   pruebas automáticas del frontend y un servicio con actualización
   garantizada.
