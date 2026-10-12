# D7 — Preguntas sobre el paper

> El paper es un producto extra del TT. Detalle en
> [C1](../C_paper/C1_PAPER_MICAI.md).

---

### P1. ¿Qué publicaron y dónde?

**Respuesta corta.** *"A Benchmark of Five Machine-Learning Architectures
for Daily Trading-Signal Classification on US Tech Equities"*, aceptado en
MICAI 2026 (Mexican International Conference on Artificial Intelligence),
que publica Springer en *Lecture Notes in Artificial Intelligence*. Enviamos
la versión final el 8 de septiembre de 2026.

### P2. ¿Qué relación tiene el paper con el TT?

**Respuesta corta.** El paper publica una parte del TT: la comparación de
los cinco modelos (corrida v4) y su verificación con un protocolo más
estricto (v5), más el experimento de selección de variables. El TT es más
amplio: además evalúa seis años con walk-forward y 2026 fuera de muestra,
analiza y ajusta el exceso de MANTENER, compara global contra por acción
sobre las mismas filas, prueba dos rondas más de mejoras (Vías 7 y 8) e
incluye la plataforma desplegada.

### P3. ¿Qué concluye el paper?

**Respuesta corta.** Que una regresión logística regularizada supera en
promedio a XGBoost y a tres redes profundas en F1-macro (0.399 de promedio,
Sharpe +0.76 en el experimento principal), que la ventaja sobrevive a una
búsqueda simétrica de hiperparámetros con intervalos de confianza
(significativamente mejor que los cuatro), que filtrar variables con
pruebas estadísticas empeora en 11 de 15 casos, y que la volatilidad de cada
acción explica más variación del Sharpe (15.5 %) que la elección del
modelo (3.4 %).

### P4. ¿Qué les pidieron los revisores y qué cambiaron?

**Respuesta corta.** Lo principal: que las redes no habían tenido una
búsqueda de hiperparámetros comparable a la de XGBoost, y que el texto de
las figuras era ilegible. Respondimos con un diagnóstico de las redes y un
protocolo nuevo (v5): búsqueda con Optuna para los cinco modelos sobre el
mismo año de decisión, ninguna decisión con la prueba, mismas filas para
todos e intervalos bootstrap. Eso agregó la sección 8 del paper. También
regeneramos las figuras al tamaño impreso y transparentamos que en la
corrida original el lookback de las redes se había elegido con la prueba.

### P5. En el paper la LR gana; en su walk-forward empata con XGBoost. ¿Se contradicen?

**Respuesta corta.** No. El paper evalúa un año de prueba (2025) y lo
declara como su limitación principal. El walk-forward extiende la
evaluación a seis años: ahí la LR y XGBoost empatan arriba y las redes
quedan abajo. La conclusión que se mantiene en ambos es la comparativa: los
clásicos regularizados igualan o superan a las redes en este régimen. Y con
costos de transacción la LR vuelve a quedar arriba porque opera menos.

### P6. El paper dice que la LSTM es bidireccional. ¿Es la que ganó?

**Respuesta corta.** La del paper en la sección 7 (corrida v4) sí era
bidireccional de 2 capas de 128 unidades. En la búsqueda de la sección 8,
Optuna eligió una LSTM unidireccional de 2 capas de 118 unidades con
atención. En ambos casos queda por debajo de la LR.

### P7. ¿Por qué en el paper el lookback de las redes se eligió con la prueba?

**Respuesta corta.** Fue un error de protocolo de la primera corrida que
detectamos en el diagnóstico. El paper lo declara explícitamente: elegir el
mejor lookback con la prueba le da a las redes una ventaja que la LR no
tiene, así que la diferencia de la sección 7 es un límite inferior del
margen de la LR. En la sección 8, sin esa ventaja, las redes caen y la LR
amplía su margen.

### P8. ¿Por qué el paper no incluye costos de transacción si ustedes los calcularon?

**Respuesta corta.** El paper los declara como limitación porque su
objetivo era una comparación de primer orden entre modelos en igualdad de
condiciones. En el TT sí los reportamos: con 10 puntos base la LR mantiene
un Sharpe de +0.62 y XGBoost cae a +0.01.

### P9. ¿El código y los datos son reproducibles?

**Respuesta corta.** Sí. Todo el código, semillas y versiones de bibliotecas
están en el repositorio; los datos son de Yahoo Finance. El material
suplementario incluye dos verificaciones: las 18 corridas globales de las
redes y las 24 de la LR de la sección 7 se reproducen exactas con el entorno
documentado (PyTorch 2.12, scikit-learn 1.7.2, XGBoost 3.2, Optuna 4.8).

### P10. ¿Qué aportó el paper al TT?

**Respuesta corta.** Validación externa: la metodología y la conclusión
principal pasaron revisión por pares en un congreso internacional. Y la
revisión nos obligó a hacer el protocolo v5, que hizo el trabajo más
riguroso.

### P11. ¿Qué cambiarían del paper hoy?

**Respuesta corta.** Reportaría el walk-forward de seis años como
evaluación principal en vez de un solo año, incluiría los costos de
transacción en la tabla principal, haría la comparación global contra por
acción sobre las mismas filas y corregiría la ventana de las redes para que
incluya el último día.
