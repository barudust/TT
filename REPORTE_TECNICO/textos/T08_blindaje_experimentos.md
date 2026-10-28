# T08 — Textos para blindar los experimentos (versión del 28 de octubre)

> **Para qué sirve.** El reporte ya dice *qué* se hizo y *qué salió* en cada
> etapa, pero casi nunca dice **por qué se hizo**. Esa es la pregunta que
> puede hacer un sinodal: "si ya sabían que no iba a funcionar, ¿para qué lo
> hicieron?". La respuesta honesta es que **ninguna etapa se hizo sabiendo
> su resultado**: cada una respondió a algo concreto (el resultado anterior,
> la literatura, los revisores del artículo, la sinodal o el sistema en
> operación). Estos textos lo dejan escrito en el documento.
>
> Están listos para pegar, en el tono del resto del reporte (impersonal, sin
> primera persona). Cada uno dice dónde va. Las cifras están verificadas
> contra el repositorio (fuentes en
> [`../tablas/ANEXO_B_REGISTRO_DE_EXPERIMENTOS.md`](../tablas/ANEXO_B_REGISTRO_DE_EXPERIMENTOS.md)).

---

## 1. Nuevo §4.1.1 "Cómo se decidió cada etapa" (va después de la Figura 1)

> **4.1.1 Cómo se decidió cada etapa**
>
> Ninguna etapa se emprendió conociendo su resultado. Cada una respondió a
> una pregunta que dejó abierta la anterior o a una observación externa, y la
> decisión de continuar se tomó con la evidencia disponible en ese momento.
>
> Al cerrar el Trabajo Terminal I, los modelos clásicos aparecían por encima
> de las redes, pero esa comparación no permitía concluir nada sobre las
> arquitecturas: cada modelo recibía variables distintas, las redes tenían
> hiperparámetros fijos y su ventana se había elegido con la prueba. El
> propio reporte de Trabajo Terminal I señaló esa asimetría como su
> principal limitación. Además, la literatura revisada en el capítulo III
> reportaba ventajas de las redes sobre la Regresión Logística y XGBoost en
> clasificación bursátil [23], [25], [27], [34]. Con esa evidencia, la
> hipótesis razonable seguía siendo que las redes podían superar a los
> modelos clásicos si se comparaban en igualdad de condiciones.
>
> La Etapa 2 atendió el trabajo futuro que planteó el Trabajo Terminal I
> (buscar hiperparámetros y revisar la selección de variables). La Etapa 3
> igualó las condiciones para publicar la comparación. La Etapa 4 surgió de
> la revisión del artículo, cuyos revisores pidieron una búsqueda de
> hiperparámetros comparable para las redes, y de un diagnóstico que mostró
> que las redes habían estado en desventaja (su paro temprano restauraba la
> primera o la segunda época). Esa etapa fue, por lo tanto, la mejor
> oportunidad que recibieron las redes. La Etapa 5 probó las técnicas
> estándar que un evaluador podría señalar como pendientes. La Etapa 6
> respondió al comportamiento del modelo en la plataforma y a las
> observaciones de la sinodal.
>
> Probar alternativas que finalmente no mejoraron el resultado no es un
> esfuerzo perdido: una conclusión del tipo "las redes no superan a un modelo
> lineal" solo es creíble si las redes recibieron una oportunidad real de
> hacerlo. Cada prueba descartada cierra una objeción posible. El registro
> completo de las pruebas, con su motivo, su resultado y la decisión que se
> tomó, se presenta en el Anexo B.

**Nota para quien edita:** las referencias [23], [25], [27] y [34] son las
del documento actual (Siswara 2024, Agrawal 2022, Long 2019, Nabipour 2020).
Si cambia la numeración, actualizarlas.

---

## 2. Primer párrafo "Motivación" de cada sección del capítulo VII

Una o dos frases al inicio de cada sección. Así cada resultado viene
precedido de su porqué.

**7.2 Etapa 1** (al inicio):
> Esta etapa corresponde al diseño registrado en el Trabajo Terminal I:
> construir el sistema completo con los cinco modelos y compararlos.

**7.3 Etapa 2** (sustituye "Esta etapa buscó mejorar cada modelo y probó
tres ideas."):
> El Trabajo Terminal I dejó dos tareas pendientes: buscar los
> hiperparámetros de cada modelo y revisar si la selección de variables por
> modelo se justificaba. Esta etapa las atendió y probó, además, si más
> variables o la combinación de modelos mejoraban el resultado.

**7.4 Etapa 3** (al inicio):
> La Etapa 2 mostró que filtrar variables perjudicaba y que sus cifras no
> podían reportarse, porque se habían elegido observando la prueba. Esta
> etapa repitió la comparación con las mismas 61 características para los
> cinco modelos y la misma prueba en los tres experimentos.

**7.5.1 Etapa 4** (sustituye "El diagnóstico anterior llevó a rehacer el
protocolo…"):
> Esta etapa tuvo dos motivos. Los revisores del artículo enviado a MICAI
> 2026 pidieron una búsqueda de hiperparámetros comparable para las redes, y
> el diagnóstico de la Etapa 3 mostró que las redes habían estado en
> desventaja. Por ello se rehízo el protocolo para que ninguna decisión
> utilizara la prueba…

**7.7 Etapa 5** (sustituye "Con el protocolo final fijo se probó lo que
quedaba sin cambiar el problema."):
> Con el resultado principal establecido, quedaban técnicas estándar cuya
> ausencia podría señalarse como una debilidad: calibrar las probabilidades,
> combinar modelos, promediar pesos, dar más peso a los datos recientes y
> construir variables nuevas. Esta etapa las probó sobre el protocolo
> congelado del Experimento B, con una regla de adopción declarada antes de
> probar: una técnica se adoptaba solo si mejoraba el F1-macro en 0.005 o el
> índice de Sharpe en 0.10. Su efecto se midió sobre 2025, por lo que estas
> pruebas solo sirven para descartar; la única que se adoptó se validó
> después con un origen rodante de 2019 a 2024.

**7.8 Etapa 6** (al inicio):
> Al operar en la plataforma, el modelo mostró un comportamiento que la
> prueba de 2025 no había revelado: predecía MANTENER con mucha más
> frecuencia que la real. Esta etapa analizó y corrigió ese exceso y atendió
> las observaciones de la sinodal.

---

## 3. Textos para los experimentos que faltan o están incompletos

### 3.1 [FALTA] Las 93 variables de la Etapa 4 — va en §7.5.3, después del torneo de decisiones

> También se probó ampliar el conjunto con 32 variables de contexto de
> mercado, todas gratuitas en Yahoo Finance (rendimientos de bonos del Tesoro
> de distintos plazos, volatilidad del VIX, diferenciales de crédito, dólar,
> oro, petróleo e índices tecnológicos y de empresas pequeñas), para un total
> de 93. En validación, el cambio en las redes fue de −0.011 a +0.029 de
> F1-macro según el experimento, sin una dirección consistente, y las
> configuraciones ganadoras de la búsqueda usan las 61 características. Junto
> con las pruebas de la Etapa 2 (181 y 94 variables), esto indica que la
> falta de información de mercado no explica el límite observado.

### 3.2 [INCOMPLETO] Torneo de seis decisiones — tabla nueva en §7.5.3

El texto actual nombra las seis decisiones pero no muestra los números ni
la regla. Agregar la regla y esta tabla:

> Cada decisión se probó por separado en el Experimento B, con cinco
> semillas por variante y evaluando con 2024; una variante se adoptaba solo
> si mejoraba el F1-macro en al menos 0.005 y más que la desviación entre
> semillas (Tabla X).

**Tabla X. Torneo de decisiones de protocolo de las redes (F1-macro medio de cinco semillas, validación 2024, Experimento B).**

| Decisión | Variante | CNN 1D | CNN-LSTM | LSTM |
|---|---|---:|---:|---:|
| Criterio de época | Pérdida de validación (Etapa 3) | 0.301 | 0.335 | 0.286 |
| | **F1 de validación** | **0.328** | 0.335 | **0.344** |
| | F1 promedio de tres épocas | 0.323 | 0.310 | 0.334 |
| Ventanas alineadas | No (Etapa 3) | 0.301 | 0.335 | 0.344 |
| | **Sí** | **0.314** | 0.309 | 0.342 |
| Escalador | Min-max (Etapa 3) | 0.314 | 0.335 | 0.342 |
| | Estándar | 0.326 | 0.315 | 0.337 |
| | Robusto con recorte en ±5 | 0.320 | 0.306 | 0.309 |
| Pesos de clase | Balanceados (Etapa 3) | 0.314 | 0.335 | 0.342 |
| | Sin pesos | 0.304 | 0.312 | 0.345 |
| | Raíz cuadrada | 0.293 | 0.315 | 0.347 |
| Reentrenar con validación | No (Etapa 3) | 0.314 | 0.335 | 0.342 |
| | Sí | 0.290 | 0.293 | 0.294 |

*Nota. El pooling temporal se omite: sus alternativas quedaron dentro del
ruido (CNN 1D 0.308–0.331, CNN-LSTM 0.305–0.306, LSTM 0.336–0.346). Las
ventanas alineadas se adoptaron aunque le cuestan 0.027 a la CNN-LSTM,
porque sin ellas los cinco modelos no se evalúan sobre las mismas filas.
Fuente: `RESULTADOS_OPTIMIZADOS/v5/v1_ablaciones.csv`.*

### 3.3 [FALTA] Por qué cinco semillas — va en §4.10.5, antes de "En la evaluación final…"

> Al construir el código del protocolo final se observó que un cambio que
> no altera las matemáticas, la forma de recorrer el conjunto de validación
> durante el entrenamiento, movía el F1-macro de la LSTM de 0.362 a 0.384 con
> los mismos datos, la misma semilla y los mismos pesos iniciales. La causa
> es que las operaciones de la GPU no son deterministas y el entrenamiento
> amplifica esas diferencias hasta cambiar la época elegida. Una diferencia
> de implementación movía el resultado más que la distancia entre dos
> modelos, por lo que desde la Etapa 4 cada configuración se entrena con
> cinco semillas, se promedian sus probabilidades y las comparaciones se
> hacen con intervalos de confianza y no con un número aislado.

### 3.4 [FALTA] Por qué tres experimentos y qué respondieron — va al final de §7.5.2

> Los tres experimentos responden si conviene usar más historia. La
> Regresión Logística casi no cambia con la cantidad de años de
> entrenamiento (0.406 con diez, 0.404 con seis y 0.401 con cuatro), mientras
> que las redes varían mucho: la CNN-LSTM va de 0.245 con diez años a 0.372
> con seis. Más historia no mejora a ningún modelo de forma consistente y la
> conclusión comparativa es la misma en los tres experimentos.

### 3.5 [FALTA] Costos de 5 puntos base — va en §7.5.2, junto al Sharpe con 10 pb

> Con un costo de 5 puntos base el índice de Sharpe del Experimento B es
> +0.76 para la Regresión Logística, +0.23 para XGBoost, −0.14 para la
> CNN-LSTM, −0.38 para la LSTM y −0.50 para la CNN 1D.

(Opcional: agregar la columna "Sharpe 5 pb" a la Tabla 27.)

### 3.6 [FALTA] La LR no fue la primera en validación — va en §7.9, antes de "Se verificó además que elegir cada año…"

> Conviene señalar que en la validación de 2024 la Regresión Logística no
> fue la primera: en el Experimento B obtuvo 0.324, frente a 0.366 de la
> CNN-LSTM. Por eso el criterio de selección no es "el mejor en validación",
> y se comprobó que esa regla habría sido peor que conservar la Regresión
> Logística.

Esto se adelanta a la pregunta "si en validación era la peor, ¿por qué la
eligieron?". Es mejor que lo diga el documento a que lo descubra un sinodal.

### 3.7 [INCOMPLETO] Decisión sobre la calibración isotónica — va en §7.7, después de "…y a las redes alrededor de 0.06."

> No se adoptó: aun calibrado, XGBoost (0.371) queda por debajo de la
> Regresión Logística sin calibrar (0.404), y aplicar un paso adicional a un
> solo modelo rompería la igualdad de condiciones de la comparación.

### 3.8 [INCOMPLETO] Barrido de la etiqueta — sustituye la última frase de §7.7 ("Los cambios de horizonte…")

> También se evaluó si la etiqueta elegida es la más fácil de aprender, con
> 28 combinaciones de horizonte (1 a 10 días) y percentiles (de 20/80 a
> 40/60) para la Regresión Logística. Con un horizonte de un día, los
> percentiles más extremos (25/75) dieron un F1-macro algo mayor, a cambio de
> una clase MANTENER más grande, y los más cercanos (40/60) uno claramente
> menor. Con horizontes de cinco a siete días el F1-macro fue mayor. Estos resultados no
> se usaron para cambiar la etiqueta por tres razones: los F1 de etiquetados
> con distinta proporción de clases no son comparables entre sí (sección
> 2.6.1), se midieron sobre 2025, y un horizonte distinto de un día cambia el
> problema planteado, que es una señal diaria. Por ello se conservó la
> etiqueta de un día con percentiles 30/70 y el horizonte largo se propone
> como trabajo futuro (sección 9.3).

**Sin cifras a propósito.** El F1 a 5–7 días (≈ 0.43) y el de 25/75 a un
día (0.411) están en la lista de "No citar" de `03_CIFRAS_VIGENTES.md`:
puestos junto a 0.404 se leen como mejoras, y no lo son porque miden otro
problema. Si un sinodal pregunta por el número, la respuesta está en
`ESTUDIO_TT/D_defensa/D8_PREGUNTAS_TRAMPA.md`, T23.

Y en §9.3, "Cambio explícito del horizonte de predicción", agregar al final:

> Una exploración realizada durante la Etapa 5 apunta en esa dirección: con
> horizontes de cinco a siete días el F1-macro de la Regresión Logística fue
> mayor que con un día, aunque se midió sobre 2025 y con otra definición del
> problema, por lo que debe confirmarse con el protocolo final.

### 3.9 [FALTA] Historial del modelo en la plataforma — va en §6.2 o al inicio de §7.8

> La plataforma ha usado tres versiones del modelo. De julio al 26 de agosto
> usó una Regresión Logística con penalización elasticnet configurada en la
> Etapa 2. El 26 de agosto se sustituyó por la configuración de la Etapa 4
> con las 15 interacciones de la Etapa 5. El 30 de septiembre se reentrenó
> con el peso de MANTENER multiplicado por 0.90 (Etapa 6), que es la versión
> vigente (LR-v8-interactions-holdw090). Antes de esta corrección, en julio,
> se había aplicado un factor fijo a la probabilidad de MANTENER; se
> descartó porque se había ajustado con los datos de 2024.

Útil por si alguien vio la plataforma en la presentación de avances con
otras cifras.

### 3.10 [INCOMPLETO] LightGBM y filtro de confianza — va en §7.3, después de "…Ninguna combinación superó a la Regresión Logística sola."

> LightGBM obtuvo un F1-macro similar al de XGBoost, sin ventaja, y el
> filtro de confianza de la Regresión Logística, que solo emite COMPRAR o
> VENDER cuando la probabilidad supera un umbral, no mejoró su F1-macro
> (−0.005).

### 3.11 [FALTA] Pruebas múltiples — va en §7.10, al final de la "Segunda" razón

> El riesgo de probar muchas variantes sobre los mismos datos está
> documentado en finanzas: cuantas más configuraciones se evalúan, más
> probable es que la mejor lo sea por azar [Bailey et al. 2014]. Por eso las
> pruebas de la Etapa 5, medidas sobre 2025, solo se usaron para descartar, y
> la única técnica adoptada se validó después con datos que no intervinieron
> en su elección.

---

## 4. Tabla 37 ampliada (sustituye a la actual en §7.10)

**Tabla 37. Resumen de las seis etapas de experimentación.**

| Etapa | Cuándo | Qué la motivó | Pregunta | Respuesta | Qué se decidió |
|---|---|---|---|---|---|
| 1. Línea base (TT1) | Hasta mayo | Diseño registrado en TT1 | ¿Funciona el sistema completo con cinco modelos? | Sí; XGBoost mejor en F1 y la LR en Sharpe, con una comparación dispareja | Igualar las condiciones antes de concluir |
| 2. Primeras mejoras | Mayo–junio | Trabajo futuro de TT1 (hiperparámetros, selección de variables) | ¿Se puede mejorar cada modelo? | Poco; filtrar variables empeora (11 de 15) | Las 61 variables para todos; un protocolo que no use la prueba |
| 3. Igualdad de condiciones | Junio | Etapa 2 y envío del artículo | ¿Cuál gana si todos reciben lo mismo? | La LR (0.399), con XGBoost cerca | Publicar la comparación (MICAI 2026) |
| 4. Protocolo final | Agosto | Revisores del artículo y diagnóstico de las redes | ¿El resultado sobrevive a un protocolo estricto? | Sí: la LR gana con significancia en A, B y C | Resultado principal; criterio de selección |
| 5. Búsqueda de mejoras | Fin de agosto | Técnicas estándar aún sin probar | ¿Algo más mejora sin cambiar el problema? | Casi nada; 15 interacciones equivalentes | Adoptar las interacciones en la plataforma; cerrar la búsqueda |
| 6. Plataforma y validación | Septiembre–octubre | Exceso de MANTENER en operación; observaciones de la sinodal | ¿Cómo se comporta el modelo real con datos nuevos? | Se corrige el exceso; en 2026, F1 0.354 | Peso de MANTENER × 0.90; un modelo global |

---

## 5. Correcciones de cifras que acompañan a estos textos

### 5.1 §7.9 (p. 133) y §7.10 (p. 135): rango de la LR entre años

**Dice:** "la misma Regresión Logística va de 0.314 en 2022 a 0.394 en
2025, y en 2024 XGBoost (0.369) superó a la Regresión Logística (0.326)".

**Problema:** 0.314 y 0.394 son de la prueba año por año con los ajustes de
la Etapa 4; 0.369 y 0.326 son de la Tabla 29, que usa los de la Etapa 3. En
la Tabla 29 la LR de 2022 es 0.358 y la de 2025 es 0.373. Un lector que
compare con la tabla encuentra cifras que no están en ella.

**Debe decir (§7.9):** "la misma Regresión Logística va de 0.326 en 2024 a
0.393 en 2020 (Tabla 29), y en 2024 XGBoost (0.369) la superó".

**Debe decir (§7.10):** "…mientras que el mismo modelo cambia hasta 0.07 de
un año a otro (la Regresión Logística va de 0.326 en 2024 a 0.393 en 2020)".

### 5.2 §4.9.1 (p. 69) y §7.9 (p. 133): parámetros de la LR

La LR de la comparación tiene 61 variables: 3 × (61 + 1) = **186**
parámetros. Los **231** son del modelo de la plataforma, con 76 variables:
3 × (76 + 1).

- **§4.9.1, dice:** "…pesos de clase balanceados, con 231 parámetros."
  **Debe decir:** "…con 186 parámetros (231 en el modelo de la plataforma,
  que agrega 15 interacciones)."
- **§7.9, dice:** "tiene 231 parámetros frente a 485 árboles de
  profundidad 9". **Debe decir:** "tiene 186 parámetros frente a 485
  árboles de profundidad 9".

### 5.3 "Se publicó" — resumen, abstract, §3.6, §4.1, §7.4

El capítulo está **aceptado y en prensa**; el congreso es del 2 al 6 de
noviembre y todavía no hay DOI. Si el documento se entrega antes de que
salga el volumen:

- Resumen: "La comparación fue aceptada para su publicación en la
  conferencia MICAI 2026 (Springer, Lecture Notes in Artificial
  Intelligence)".
- Abstract: "The comparison was accepted for publication at MICAI 2026…".
- §4.1 y §7.4: "el artículo aceptado en MICAI 2026" en lugar de "el
  artículo presentado".

Cuando salga el DOI, agregarlo a la referencia [2].
