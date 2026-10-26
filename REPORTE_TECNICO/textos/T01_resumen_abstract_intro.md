# T01 — Resumen, abstract y piezas de la introducción

> Borradores para adaptar. Las cifras salen de `03_CIFRAS_VIGENTES.md`.
> Extensión pensada: resumen ≤ 1 página.

---

## 1. Resumen (reemplaza p. 1)

**Resumen**

El presente trabajo terminal describe el diseño, la implementación y la
evaluación de una herramienta de apoyo a la toma de decisiones en el mercado
bursátil que genera, para cada día hábil, una señal de compra, venta en corto
o mantenimiento para las siete empresas tecnológicas de mayor capitalización
del mercado estadounidense (Apple, Microsoft, Alphabet, Amazon, NVIDIA, Meta
y Tesla).

El problema se formula como una clasificación en tres clases: la etiqueta de
cada día compara el retorno logarítmico del día siguiente con los
percentiles 30 y 70 de los 252 días hábiles anteriores, lo que produce una
distribución cercana a 30/40/30 que se adapta al régimen de volatilidad de
cada acción. Como entrada se usan 61 características técnicas en nueve
familias, calculadas a partir de datos diarios gratuitos de Yahoo Finance,
incluido el contexto del S&P 500 y del VIX.

Para determinar si el aprendizaje profundo aporta una ventaja sobre modelos
más simples, se compararon tres arquitecturas profundas (LSTM, CNN 1D y
CNN-LSTM) con dos modelos clásicos (Regresión Logística y XGBoost) bajo un
mismo protocolo: las mismas características, la misma partición temporal,
las mismas filas de prueba y una búsqueda de hiperparámetros con Optuna en
la que ninguna decisión usó el año de prueba. Se definieron tres
experimentos con 10, 6 y 4 años de entrenamiento y el mismo año de prueba
(2025), y se evaluaron ocho métricas, entre ellas F1-macro (principal),
kappa de Cohen y una simulación económica con y sin costos de transacción.
La robustez se midió con intervalos de confianza bootstrap, una prueba año
por año de 2020 a 2025 y una prueba ciega con datos de 2026 que no
intervinieron en ninguna decisión.

La Regresión Logística obtuvo el mayor F1-macro en el año de prueba (0.404,
IC 95 % [0.379, 0.428], en el experimento principal) y fue significativamente
mejor que los otros cuatro modelos en los tres experimentos, con el mejor
índice de Sharpe (+0.89; +0.62 con costos de 10 puntos base). En seis años de
prueba año por año empata con XGBoost y ambos superan a las redes; en 2026
volvió a quedar primera en clasificación. Las tres redes no lograron reducir
su pérdida de validación por debajo del nivel del azar con ninguna
configuración, lo que indica que, con datos diarios públicos y señal a un
día, la complejidad adicional no se traduce en mejores señales.

El modelo elegido se integró en una plataforma web desplegada que, cada día
hábil después del cierre, calcula y publica la recomendación para las siete
acciones, evalúa las recomendaciones anteriores contra lo ocurrido y muestra
la comparación de los cinco modelos. La comparación se publicó en la
conferencia MICAI 2026 (Springer, *Lecture Notes in Artificial
Intelligence*).

**Palabras clave:** aprendizaje profundo, regresión logística, señales de
trading, clasificación multiclase, series de tiempo financieras.

---

## 2. Abstract (reemplaza p. 2)

**Abstract**

This work presents the design, implementation and evaluation of a
decision-support tool for the stock market that produces, for every trading
day, a buy, short-sell or hold signal for the seven largest US technology
companies (Apple, Microsoft, Alphabet, Amazon, NVIDIA, Meta and Tesla).

The task is formulated as three-class classification: each day's label
compares the next-day log return against the 30th and 70th percentiles of the
previous 252 trading days, which yields a class distribution close to
30/40/30 that adapts to each stock's volatility regime. The input consists of
61 technical features in nine families, computed from free daily Yahoo
Finance data, including S&P 500 and VIX context.

To determine whether deep learning adds value over simpler models, three
deep architectures (LSTM, 1-D CNN and CNN-LSTM) were compared against two
classical models (logistic regression and XGBoost) under a single protocol:
the same features, temporal split and test rows, and an Optuna
hyper-parameter search in which no decision used the test year. Three
experiments with 10, 6 and 4 training years share the same test year (2025),
and eight metrics are reported, including macro-F1 (primary), Cohen's kappa
and a backtest with and without transaction costs. Robustness is assessed
with block-bootstrap confidence intervals, a year-by-year test over
2020–2025 and a blind test on 2026 data that was never used for any
decision.

Logistic regression achieved the highest macro-F1 on the test year (0.404,
95 % CI [0.379, 0.428], principal experiment) and was significantly better
than the other four models in all three experiments, with the best Sharpe
ratio (+0.89; +0.62 with 10 basis-point costs). Over six test years it ties
with XGBoost, and both outperform the networks; in 2026 it again ranked first
in classification. None of the networks reduced its validation loss below
the chance level under any configuration, indicating that with public daily
data and a one-day signal the additional complexity does not translate into
better signals.

The selected model was deployed in a web platform that, after every market
close, computes and publishes the recommendation for the seven stocks,
evaluates past recommendations against realized outcomes and displays the
comparison of the five models. The comparison was published at MICAI 2026
(Springer, Lecture Notes in Artificial Intelligence).

**Keywords:** deep learning, logistic regression, trading signals,
multiclass classification, financial time series.

---

## 3. La frase que explica el título (para resumen, introducción y conclusiones)

Versión larga (introducción o conclusiones):

> El título del trabajo refiere al diseño e implementación de modelos de
> aprendizaje profundo para el análisis y la toma de decisiones en el
> mercado bursátil. Ese diseño e implementación se realizaron: se
> construyeron, optimizaron y evaluaron tres arquitecturas (LSTM, CNN 1D y
> CNN-LSTM). Como establece el objetivo general, su desempeño se contrastó
> con modelos de referencia, y la evidencia —en igualdad de condiciones, con
> pruebas estadísticas y en varios años— mostró que en este problema no
> superan a una Regresión Logística bien regularizada. Por ello la
> plataforma despliega el modelo que mejor cumple el criterio de selección
> declarado, y la respuesta a la pregunta de investigación forma parte de
> los resultados del trabajo.

Versión corta (resumen, presentación):

> Se diseñaron e implementaron tres modelos de aprendizaje profundo y se
> compararon con dos referencias clásicas; como la evidencia favoreció a la
> Regresión Logística, es el modelo que se despliega.

---

## 4. Sección 1.5 Productos del trabajo (nueva)

**1.5 Productos del trabajo**

El trabajo terminal produjo tres resultados verificables:

1. **Plataforma web desplegada.** Disponible en
   https://tt-frontend-womf.onrender.com. Publica cada día hábil la
   recomendación del modelo para las siete acciones, el resultado de cada
   recomendación anterior, el desempeño acumulado y la comparación de los
   cinco modelos evaluados. Su diseño e implementación se describen en el
   capítulo 5.
2. **Artículo científico.** La comparación de los cinco modelos y su
   verificación con el protocolo final fueron aceptadas en la *Mexican
   International Conference on Artificial Intelligence* (MICAI 2026) y se
   publicarán en la serie *Lecture Notes in Artificial Intelligence* de
   Springer [ref.]. El Anexo A describe qué parte del trabajo cubre el
   artículo.
3. **Repositorio reproducible.** El código, los datos, los resultados de
   cada etapa y las versiones de las bibliotecas están en un repositorio
   público (https://github.com/barudust/TT); el Anexo C indica cómo
   reproducir cada resultado.

---

## 5. Párrafo para agregar en la introducción (después de §1, párrafo 4)

> Los resultados muestran que, con datos diarios públicos y señal a un día,
> los modelos clásicos igualan o superan a las arquitecturas profundas: la
> Regresión Logística obtuvo el mejor desempeño en el año de prueba, con
> diferencias estadísticamente significativas, y en seis años de prueba
> empata con XGBoost. Este modelo se integró en una plataforma web que
> actualiza sus recomendaciones cada día hábil.
