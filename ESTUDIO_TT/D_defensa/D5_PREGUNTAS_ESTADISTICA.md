# D5 — Preguntas de estadística, validación y rigor

> Para sinodales con formación en estadística o ciencia de datos. Respuesta
> corta = lo que dices; "Para entenderlo" = el fondo. Detalle en
> [A3](../A_modelo/A3_PROTOCOLO_Y_METRICAS.md) y
> [A7](../A_modelo/A7_RESULTADOS_Y_LIMITES.md).

---

## Validación

### E1. ¿Cómo separaron entrenamiento, validación y prueba?

**Respuesta corta.** Siempre por tiempo: entrenamiento con años pasados,
validación con el año siguiente y prueba con el último. Tres experimentos
con la misma prueba (2025) y 10, 6 o 4 años de entrenamiento (2014, 2018 o
2020 a 2023), validación 2024. El principal es el de 6 años.

### E2. ¿Por qué no validación cruzada (k-fold)?

**Respuesta corta.** El k-fold aleatorio mezcla días futuros en el
entrenamiento, y como días cercanos se parecen (autocorrelación), inflaría
los resultados. Lo que sí hicimos es la versión temporal: un
**walk-forward** de 6 años (entrenar 5, validar 1, probar el siguiente, con
prueba en 2020, 2021, …, 2025) y un **origen rodante** 2019–2024 para elegir
el ajuste de MANTENER.

### E3. ¿Cómo evitaron sobreajustar al año de prueba?

**Respuesta corta.** Con un protocolo anidado en v5: todas las decisiones
(hiperparámetros, ablaciones) se toman en modo *dev* —entrenar 2018–2022,
elegir la época con 2023 y la configuración con 2024— y 2025 se evalúa una
sola vez por configuración congelada. Además, evaluamos en 2026, un año que
no se usó para nada.

### E4. ¿Qué fuentes de fuga de información controlaron?

**Respuesta corta.** (1) Variables calculadas solo con datos hasta el cierre
del día; (2) umbrales de la etiqueta con `shift(1)`; (3) escalador y pesos de
clase ajustados solo con entrenamiento; (4) separación cronológica; (5)
ninguna decisión con 2025 en v5; (6) en la plataforma se descarta la vela del
día mientras el mercado está abierto.

**Si preguntan por purga/embargo (López de Prado):** la etiqueta del último
día de un periodo usa el cierre del primer día del siguiente. En rigor se
debería purgar ese día; es 1 de ~250 por corte y no revela etiquetas de
prueba, así que el efecto es despreciable. Lo reconocemos.

### E5. ¿Por qué el modelo de producción se entrenó con 2018–2025, incluida la prueba?

**Respuesta corta.** Es la práctica estándar: lo que se evalúa con
entrenamiento/validación/prueba es el **procedimiento**; una vez elegido, se
reentrena con todos los datos disponibles para usarlo. La prueba honesta del
modelo final es 2026, que nunca vio: F1 0.354.

### E6. Probaron unas 30 técnicas sobre 2025. ¿No es *data snooping*?

**Respuesta corta.** Es un riesgo real y lo tratamos así: los
hiperparámetros se eligen en validación; el ajuste de MANTENER se eligió con
6 años de origen rodante; 2026 no se usó para decidir nada; y declaramos que
la "mejora" de las interacciones (+0.023 en 2025) no se sostiene en
validación.

**Para entenderlo.** Si pruebas ~10 variantes y te quedas con la mejor
sobre el mismo año, el máximo del ruido parece mejora (*winner's curse*).
Con un error estándar del F1 de ≈ 0.0125, el máximo esperado de 10
variantes sin efecto real es ≈ 1.54 σ ≈ +0.019: del tamaño de la mejora de
las interacciones. Por eso en origen rodante empatan (0.357 con
interacciones contra 0.354 sin ellas).

---

## Métricas

### E7. ¿Por qué F1-macro y no accuracy?

**Respuesta corta.** Con 42 % de MANTENER, decir siempre MANTENER da 42 %
de exactitud sin aprender nada. El F1-macro promedia el F1 de las tres
clases por igual y ese modelo trivial sacaría ≈ 0.20. Macro y no ponderado
porque las clases que importan económicamente son COMPRAR y VENDER.

### E8. ¿Qué es el kappa de Cohen y por qué lo usan?

**Respuesta corta.** El acuerdo entre predicción y realidad descontando el
que habría por azar: `κ = (p_o − p_e)/(1 − p_e)`. 0 es azar, 1 perfecto. Lo
usamos porque, a diferencia del F1, es comparable entre etiquetas con
distinta proporción de clases (30/70 contra 40/60), y dice directamente
cuánto superamos el azar: 0.14 en 2025 (LR + interacciones), 0.035 en 2026.
Según Landis y Koch (1977), menos de 0.20 es "acuerdo leve".

**Ejemplo (2025):** `p_o = 0.453`;
`p_e = 0.297·0.270 + 0.420·0.570 + 0.283·0.160 = 0.365`;
`κ = (0.453 − 0.365)/(1 − 0.365) = 0.14`.

### E9. ¿Calcularon AUC-ROC o balanced accuracy?

**Respuesta corta.** No eran métricas principales, pero las calculamos con
las probabilidades guardadas de v5 (Exp B, 2025) y la LR también es la mejor:
AUC-ROC macro 0.593 (las demás 0.539–0.573) y balanced accuracy 0.407 (las
demás 0.364–0.373).

### E10. ¿Por qué el Sharpe y no solo F1?

**Respuesta corta.** Porque un modelo puede acertar días de movimientos
pequeños y fallar los grandes. El Sharpe mide la ganancia de la estrategia
por unidad de riesgo: `√252 · media / desviación` de los retornos diarios de
la estrategia (COMPRAR +r, VENDER −r, MANTENER 0).

### E11. ¿Un Sharpe de +0.9 en un año es significativo?

**Respuesta corta.** Por sí solo no. Con un año de datos el error estándar
del Sharpe anualizado es ≈ 1 (Lo, 2002), así que el intervalo de 95 % es
aproximadamente [−1.1, 2.9]. Por eso la métrica principal es la de
clasificación y las conclusiones económicas son comparativas. En el
walk-forward el Sharpe medio de la LR es +0.22 con desviación 0.50 entre
años: `t = 0.22/(0.50/√6) ≈ 1.1`, no significativo.

### E12. ¿Incluyeron costos de transacción?

**Respuesta corta.** Las cifras principales van sin costos para comparar en
igualdad, pero en v5 calculamos 5 y 10 puntos base por cambio de posición.
La LR pasa de Sharpe +0.89 a +0.76 y +0.62; XGBoost de +0.46 a +0.23 y +0.01.
Los costos castigan la rotación (0.38 en la LR contra 0.65 en XGBoost), así
que amplían la ventaja de la LR.

---

## Significancia

### E13. ¿Cómo saben que el resultado no es suerte?

**Respuesta corta.** Con cuatro pruebas: (1) **bootstrap por bloques**: el
F1 de la LR en 2025 está en [0.379, 0.428] y las diferencias pareadas con
los otros cuatro excluyen el cero; (2) **permutación**: en 2025 solo el 0.4 %
de 500 reordenamientos de las señales supera al modelo; (3)
**walk-forward** de 6 años; (4) **2026** fuera de muestra. Conclusión
honesta: hay señal, débil y dependiente del año (en 2024 el 79 % de las
permutaciones supera al modelo).

### E14. ¿Cómo funciona el bootstrap por bloques? ¿Por qué bloques?

**Respuesta corta.** Se toman al azar, con reemplazo, bloques de 20 días
consecutivos del año de prueba hasta completar su tamaño, se calcula el F1, y
se repite 2 000 veces; los percentiles 2.5 y 97.5 dan el intervalo. Bloques
y no días sueltos porque los días están correlacionados; remuestrear días
sueltos subestimaría la incertidumbre.

### E15. ¿Cómo funciona la prueba de permutación?

**Respuesta corta.** Se barajan las señales del modelo entre los días:
mantiene cuántas COMPRAR, MANTENER y VENDER hay, pero rompe su relación con
lo que pasó. Repetido 500 veces da la distribución del Sharpe bajo la
hipótesis "las señales no tienen información"; el p-valor es la fracción de
barajadas que igualan o superan al modelo.

### E16. ¿Cómo compararon el modelo global contra el de cada acción?

**Respuesta corta.** Con un diseño pareado: global y por acción evaluados
sobre los mismos días de cada acción; 21 pares por modelo (3 experimentos ×
7 acciones). Prueba de signo y de rangos con signo de Wilcoxon. En la LR el
global gana 18 de 21 (p = 0.002, binomial). Advertencia: los pares no son
independientes (mismo año y mercado), así que los p-valores son optimistas;
lo que da confianza es que la dirección se repite en v4 y v5.

### E17. ¿El ajuste de MANTENER × 0.90 es una mejora significativa?

**Respuesta corta.** No, y no lo presentamos así. Mejora el F1 en 4 de 6
años de desarrollo (Wilcoxon p ≈ 0.31); con 6 años no hay potencia
estadística. El objetivo era una proporción de MANTENER realista sin perder
desempeño, y eso sí se cumple: en 2026 pasa de 60 % a 40 % (real 35 %) y el
F1 de 0.313 a 0.354.

---

## Comportamiento del modelo

### E18. ¿Por qué el modelo predice tanto MANTENER?

**Respuesta corta.** Porque sabe cuándo habrá movimiento pero no hacia
dónde. En todos los días que dice MANTENER, P(COMPRAR) + P(VENDER) supera a
P(MANTENER) (≈ 0.62 contra 0.38), pero esa probabilidad se reparte entre las
dos direcciones y ninguna supera a MANTENER en el argmax: "voto dividido".
La magnitud es predecible (la volatilidad se agrupa, como en los modelos
GARCH), la dirección casi no (eficiencia débil del mercado).

**Además:** las variables más pesadas son del VIX y del S&P 500, iguales para
las 7 acciones, por eso el MANTENER llega en bloque cuando el VIX está bajo
su media anual.

### E19. ¿No es simplemente desbalance de clases?

**Respuesta corta.** No. Ya entrenamos con pesos "balanced", que le bajan
el peso a MANTENER. Y con la etiqueta 40/60, donde MANTENER es solo el 20 %,
el modelo sigue diciéndolo el 53 % de los días. La causa es la forma de las
probabilidades (voto dividido), no la proporción de clases.

### E20. Si el modelo da probabilidades, ¿por qué no movieron el umbral de decisión?

**Respuesta corta.** Lo probamos con origen rodante de 6 años: multiplicar
P(MANTENER) por un factor fijo empeora fuera de muestra (con 0.90, el F1
medio baja de 0.357 a 0.334), porque el sesgo cambia de signo entre años
(2022 predice MANTENER de menos; 2023 de más). Lo que funcionó fue ajustar
el peso de MANTENER **al entrenar**, que reajusta interceptos y
coeficientes.

**Para entenderlo.** El argmax es óptimo para la exactitud; para F1-macro el
óptimo puede ser con umbrales por clase, así que moverlos es legítimo.
Multiplicar `p_MANTENER` por *k* equivale a sumar `log k` a su puntaje (un
cambio de *prior*). Como las probabilidades están comprimidas cerca de 1/3,
un *k* pequeño mueve mucho. Un primer análisis con solo 2024 sugería
k = 0.90: era sobreajuste a un año.

### E21. ¿Por qué no calibraron las probabilidades?

**Respuesta corta.** Calibrar cambia cuánto confía el modelo, no
necesariamente qué clase elige. La escala de temperatura no cambia el
argmax; la calibración isotónica sí puede, y la probamos en la Vía 7:
empeoró la LR (−0.05 de F1). La regresión logística ya optimiza log-loss,
que suele dar probabilidades razonablemente calibradas.

### E22. ¿Por qué la confianza del modelo es tan baja (35–45 %)?

**Respuesta corta.** Por la regularización muy fuerte y la poca señal: los
coeficientes son diminutos y las probabilidades quedan cerca de 1/3. Aun
así es informativa: con confianza ≤ 0.36 acierta 39 % y entre 0.40 y 0.45
acierta 56 %.

### E23. Si 2025 fue el mejor año del modelo, ¿no eligieron la prueba a conveniencia?

**Respuesta corta.** No: 2025 se fijó en v4 como el último año completo,
antes de conocer los resultados, para que los tres experimentos lo
compartieran. Precisamente por eso reportamos el walk-forward y 2026, donde
el modelo rinde menos, y lo decimos.
