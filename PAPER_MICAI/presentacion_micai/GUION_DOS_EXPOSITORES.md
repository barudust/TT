# Guion para dos expositores — MICAI 2026

> Generado desde `fuente/guion.py` (no editar a mano: cambiar ahí y volver a correr
> `generar_guion.py`). Inglés sencillo, frases cortas. Debajo de cada bloque en inglés
> va la traducción, solo para que sepan qué están diciendo: **en el congreso se dice
> solo el inglés**.

**Duración total: 8:20 min** (límite oficial: 10 min de exposición + 5 de preguntas).
El margen es para hablar despacio, respirar y cambiar de expositor sin prisa.

| Expositor | Diapositivas | Tiempo |
|---|---|---:|
| **Expositor 1** | 1, 2, 3, 4, 10, 11 | 4:45 |
| **Expositor 2** | 5, 6, 7, 8, 9 | 3:35 |

- **Expositor 1** abre (portada, pregunta, datos, modelos) y cierra (por qué gana, mensajes finales).
- **Expositor 2** presenta los cuatro resultados y la comparación justa.
- Cambian de expositor **dos veces**; la frase para pasar la palabra está marcada con →.
- Si solo presenta una persona, el guion es el mismo: se omiten las frases de cambio.
- Reemplazar **[NAME]** por los nombres reales en la diapositiva 1.
- Si la sesión es después de las 12:00, decir *Good afternoon, everyone* (gud af-ter-NÚN).

---

## Diapositiva 1 · Portada — Expositor 1 · 30 s (minuto 0:00 → 0:30)

> **Good morning, everyone.**  
> **My name is [NAME], and this is my colleague [NAME].**  
> **We are from ESCOM, at the Instituto Politécnico Nacional, in Mexico City.**  
> **Today we present a benchmark of five machine learning models for daily trading signals.**  

<details><summary>Traducción</summary>

- Buenos días a todos.
- Me llamo [NOMBRE] y él/ella es mi compañero(a) [NOMBRE].
- Somos de ESCOM, del Instituto Politécnico Nacional, en la Ciudad de México.
- Hoy presentamos una comparación de cinco modelos de aprendizaje automático para señales diarias de trading.

</details>

## Diapositiva 2 · La pregunta — Expositor 1 · 50 s (minuto 0:30 → 1:20)

> **Our question is simple: do deep networks beat simple models for daily trading signals?**  
> **Many papers compare only one or two models.**  
> **They often report accuracy or RMSE. These numbers do not tell us if a strategy makes money.**  
> **And many papers remove features with statistical filters, but they do not check if this helps.**  
> **So we made a fair test with five models, measured as classification and as a trading strategy.**  

<details><summary>Traducción</summary>

- Nuestra pregunta es simple: ¿las redes profundas le ganan a los modelos simples en señales diarias de trading?
- Muchos artículos comparan solo uno o dos modelos.
- Muchas veces reportan accuracy o RMSE. Esos números no dicen si una estrategia gana dinero.
- Y muchos artículos quitan variables con filtros estadísticos, pero no revisan si eso ayuda.
- Así que hicimos una prueba justa con cinco modelos, medida como clasificación y como estrategia de trading.

</details>

## Diapositiva 3 · Datos y etiqueta — Expositor 1 · 70 s (minuto 1:20 → 2:30)

> **We use seven big tech stocks: Apple, NVIDIA, Tesla, Amazon, Microsoft, Google and Meta.**  
> **The data is free, from Yahoo Finance, from 2013 to 2025.**  
> **Every day, each stock gets one label: buy, hold or sell.**  
> **We compare tomorrow's return with the last 252 days.**  
> **If it is in the top 30 percent, the label is buy. If it is in the bottom 30 percent, the label is sell. The rest is hold.**  
> **So the label changes with the volatility, and it only uses past data.**  
> **The input is 61 technical features, plus the S&P 500 and the VIX.**  

<details><summary>Traducción</summary>

- Usamos siete acciones tecnológicas grandes: Apple, NVIDIA, Tesla, Amazon, Microsoft, Google y Meta.
- Los datos son gratis, de Yahoo Finance, de 2013 a 2025.
- Cada día, cada acción recibe una etiqueta: comprar, mantener o vender.
- Comparamos el retorno de mañana con los últimos 252 días.
- Si está en el 30 % más alto, la etiqueta es comprar. Si está en el 30 % más bajo, es vender. Lo demás es mantener.
- Así la etiqueta se adapta a la volatilidad y solo usa datos del pasado.
- La entrada son 61 variables técnicas, más el S&P 500 y el VIX.

</details>

## Diapositiva 4 · Modelos y protocolo — Expositor 1 · 55 s (minuto 2:30 → 3:25)

> **We compare five models.**  
> **Two classical models: logistic regression and XGBoost.**  
> **And three deep networks: an LSTM, a one-dimensional CNN, and a hybrid CNN-LSTM.**  
> **We use three splits. All of them test on the same year, 2025. Only the training history changes: ten, six or four years.**  
> **We train one global model and one model per stock. In total, 120 runs.**  
> **Our main metric is macro-F1, and we also simulate a simple trading strategy.**  
>
> → **Now, my colleague will show the results.**

<details><summary>Traducción</summary>

- Comparamos cinco modelos.
- Dos modelos clásicos: regresión logística y XGBoost.
- Y tres redes profundas: una LSTM, una CNN de una dimensión y una híbrida CNN-LSTM.
- Usamos tres particiones. Todas prueban en el mismo año, 2025. Solo cambia la historia de entrenamiento: diez, seis o cuatro años.
- Entrenamos un modelo global y un modelo por acción. En total, 120 corridas.
- Nuestra métrica principal es F1-macro y también simulamos una estrategia de trading sencilla.
- → Ahora mi compañero(a) va a mostrar los resultados.

</details>

## Diapositiva 5 · Resultado 1 — Expositor 2 · 60 s (minuto 3:25 → 4:25)

> **Thank you. Here is the first result.**  
> **Each group is one split. The blue bar is logistic regression.**  
> **It has the best average macro-F1: zero point three nine nine.**  
> **It wins in splits A and C, and XGBoost is very close in split B.**  
> **The dashed line is random guessing: zero point three three three. So the signal is small, but it is there.**  
> **In money, logistic regression is also the best in the main split: Sharpe ratio zero point seven six, and profit factor one point two one.**  

<details><summary>Traducción</summary>

- Gracias. Aquí está el primer resultado.
- Cada grupo es una partición. La barra azul es la regresión logística.
- Tiene el mejor F1-macro promedio: 0.399.
- Gana en las particiones A y C, y XGBoost está muy cerca en la B.
- La línea punteada es adivinar al azar: 0.333. La señal es pequeña, pero existe.
- En dinero, la regresión logística también es la mejor en la partición principal: Sharpe 0.76 y profit factor 1.21.

</details>

## Diapositiva 6 · Resultado 2 — Expositor 2 · 30 s (minuto 4:25 → 4:55)

> **Second result. Many studies filter the features before training.**  
> **We tested the common filters: Pearson, VIF, SHAP and Spearman.**  
> **In eleven of fifteen cases, keeping all 61 features was better.**  
> **The model's own regularization selects features better than an external filter.**  

<details><summary>Traducción</summary>

- Segundo resultado. Muchos estudios filtran las variables antes de entrenar.
- Probamos los filtros comunes: Pearson, VIF, SHAP y Spearman.
- En 11 de 15 casos, conservar las 61 variables fue mejor.
- La regularización del propio modelo elige mejor que un filtro externo.

</details>

## Diapositiva 7 · Resultado 3 — Expositor 2 · 30 s (minuto 4:55 → 5:25)

> **Third result. We split the variation of the Sharpe ratio.**  
> **The stock explains fifteen point five percent. The model explains only three point four percent.**  
> **So, choosing the stock matters about four and a half times more than choosing the model.**  

<details><summary>Traducción</summary>

- Tercer resultado. Dividimos la variación del Sharpe.
- La acción explica 15.5 %. El modelo explica solo 3.4 %.
- Elegir la acción importa unas cuatro veces y media más que elegir el modelo.

</details>

## Diapositiva 8 · ¿Fue justo? — Expositor 2 · 45 s (minuto 5:25 → 6:10)

> **But was the comparison fair? The reviewers asked a good question.**  
> **XGBoost had a bigger search, and the window of the networks was chosen on the test set.**  
> **So we rebuilt everything. All decisions use 2024. The test year, 2025, is used only one time.**  
> **All five models use the same search with Optuna, and the same 1,736 test rows.**  

<details><summary>Traducción</summary>

- ¿Pero la comparación fue justa? Los revisores hicieron una buena pregunta.
- XGBoost tuvo una búsqueda más grande, y la ventana de las redes se eligió con la prueba.
- Así que rehicimos todo. Todas las decisiones usan 2024. El año de prueba, 2025, se usa una sola vez.
- Los cinco modelos usan la misma búsqueda con Optuna y las mismas 1,736 filas de prueba.

</details>

## Diapositiva 9 · Resultado 4 — Expositor 2 · 50 s (minuto 6:10 → 7:00)

> **And the result? The gap does not close.**  
> **Logistic regression gets zero point four zero four, with a 95 percent confidence interval from zero point three seven nine to zero point four two eight.**  
> **It is significantly better than the other four models.**  
> **The networks never reduce their validation loss below the random level. A very small LSTM gives the same result as a big one.**  
>
> → **Now my colleague will explain why.**

<details><summary>Traducción</summary>

- ¿Y el resultado? La diferencia no se cierra.
- La regresión logística obtiene 0.404, con un intervalo de confianza del 95 % de 0.379 a 0.428.
- Es significativamente mejor que los otros cuatro modelos.
- Las redes nunca bajan su pérdida de validación del nivel del azar. Una LSTM muy pequeña da lo mismo que una grande.
- → Ahora mi compañero(a) va a explicar por qué.

</details>

## Diapositiva 10 · ¿Por qué gana? — Expositor 1 · 45 s (minuto 7:00 → 7:45)

> **Why does a simple linear model win here?**  
> **First, the data is small for deep models: about ten thousand rows.**  
> **Second, the one-day label is very noisy.**  
> **Third, our features already summarize many days, so a linear model can use them well.**  
> **We also have limitations: we test only one year, we do not include transaction costs, and we use only seven stocks from one sector.**  

<details><summary>Traducción</summary>

- ¿Por qué gana aquí un modelo lineal simple?
- Primero, los datos son pocos para modelos profundos: unas diez mil filas.
- Segundo, la etiqueta de un día tiene mucho ruido.
- Tercero, nuestras variables ya resumen muchos días, así que un modelo lineal las aprovecha bien.
- También tenemos limitaciones: probamos un solo año, no incluimos costos de transacción y usamos solo siete acciones de un sector.

</details>

## Diapositiva 11 · Cierre — Expositor 1 · 35 s (minuto 7:45 → 8:20)

> **To finish, three messages.**  
> **One: a well-regularized logistic regression is a strong and cheap baseline.**  
> **Two: do not filter the features before training.**  
> **Three: the stock matters more than the model.**  
> **Our code and data are public. Thank you. We are happy to answer your questions.**  

<details><summary>Traducción</summary>

- Para terminar, tres mensajes.
- Uno: una regresión logística bien regularizada es un punto de partida fuerte y barato.
- Dos: no filtren las variables antes de entrenar.
- Tres: la acción importa más que el modelo.
- Nuestro código y datos son públicos. Gracias. Con gusto respondemos sus preguntas.

</details>

---

## Diapositivas de respaldo (solo si una pregunta las necesita)

- **12.** Corrected protocol, full Table 6 (hyper-parameters, intervals, Sharpe).
- **13.** Since submission: six test years, transaction costs, unseen 2026 data.
- **14.** Benchmark tables 3–5 (global, economics, per-stock).
- **15.** Hyper-parameter search: trials and search space per model.

Para saltar a una diapositiva en PowerPoint durante la presentación: escribir el número
y presionar **Enter** (por ejemplo `13` + Enter). Para volver: el número de la última.

---

## Pronunciación (aproximada, para hispanohablantes)

La sílaba en MAYÚSCULAS es la que se acentúa.

| Palabra | Se dice |
|---|---|
| logistic regression | lo-YÍS-tic ri-GRÉ-shon |
| benchmark | BÉNCH-mark |
| machine learning | ma-SHÍN LÉR-ning |
| deep networks | DIP NÉT-uorks |
| trading signals | TRÉI-ding SÍG-nals |
| macro-F1 | MÁ-cro ef-UÁN |
| Sharpe ratio | SHARP RÉI-shio |
| profit factor | PRÓ-fit FÁC-tor |
| percent | per-SÉNT |
| percentile | per-SÉN-tail |
| volatility | vo-la-TÍ-li-ti |
| regularization | re-guiu-la-rai-SÉI-shon |
| confidence interval | CÓN-fi-dens ÍN-ter-val |
| significantly | sig-NÍ-fi-cant-li |
| validation loss | va-li-DÉI-shon LOS |
| XGBoost | ex-yi-BÚST |
| LSTM | el-es-ti-ÉM |
| CNN | si-en-ÉN |
| one-dimensional | uán-di-MÉN-sho-nal |
| hybrid | JÁI-brid |
| Optuna | op-TÚ-na |
| Yahoo Finance | YÁ-ju FÁI-nans |
| NVIDIA | en-VÍ-dia |
| reviewers | ri-VIÚ-ers |
| noisy | NÓI-si |
| baseline | BÉIS-lain |
| features | FÍ-chers |
| history | JÍS-to-ri |
| thousand | ZÁU-sand |
| 2025 | tuén-ti tuén-ti FÁIV |
| 2024 | tuén-ti tuén-ti FÓR |
| 0.404 | SÍ-ro point FOR SÍ-ro FOR |
| 1,736 | uán ZÁU-sand SÉ-ven JÁN-dred ZÉR-ti SIKS |
| 252 | tu JÁN-dred FÍF-ti TU |

**Números:** el punto decimal se dice *point* y cada dígito por separado: 0.404 = *zero point four zero four*. Los porcentajes: 15.5 % = *fifteen point five percent*.

---

## Preguntas probables (respuestas cortas)

Quién contesta cada una es una sugerencia por tema; el otro puede completar.

### 1. Is there a real signal, or is it random?
*¿Hay señal real o es azar?* — contesta **Expositor 2**

> **Yes, there is a signal, but it is small. Logistic regression gets 0.404. Random is 0.333. The confidence interval does not include 0.333.**

Sí hay señal, pero es pequeña. La LR obtiene 0.404; el azar es 0.333; el intervalo no incluye 0.333.

### 2. Why does a linear model beat deep networks?
*¿Por qué un modelo lineal le gana a las redes?* — contesta **Expositor 1**

> **The data is small for deep models, the one-day label is very noisy, and our features already summarize many days. The validation loss of the networks stays at the random level.**

Pocos datos para redes, etiqueta con mucho ruido y variables que ya resumen muchos días. La pérdida de validación de las redes se queda en el nivel del azar.

### 3. Did the deep models get a fair hyper-parameter search?
*¿Las redes tuvieron una búsqueda justa de hiperparámetros?* — contesta **Expositor 2**

> **Yes. In Section 8 all models use the same Optuna search, the same decision year and the same test rows. The networks search 17 to 20 hyper-parameters. The gap is bigger, not smaller.**

Sí. En la sección 8 todos usan la misma búsqueda con Optuna, el mismo año de decisión y las mismas filas. Las redes buscan 17 a 20 hiperparámetros. La diferencia crece.

### 4. You test only one year. Is 2025 special?
*Solo prueban un año. ¿2025 es especial?* — contesta **Expositor 2**

> **It is our main limitation. 2025 is not an easy year: the return is below the median and the volatility is high. After the paper, we tested six years, 2020 to 2025. Logistic regression and XGBoost are similar, and both are better than the networks.**

Es nuestra limitación principal. 2025 no es un año fácil. Después del artículo probamos seis años: LR y XGBoost son parecidos y ambos superan a las redes.

### 5. What about transaction costs?
*¿Y los costos de transacción?* — contesta **Expositor 2**

> **They are not in the paper. After the paper we tested 10 basis points. Logistic regression keeps a Sharpe ratio of 0.62. XGBoost goes to almost zero, because it trades more.**

No están en el artículo. Después probamos 10 puntos base: la LR conserva Sharpe 0.62 y XGBoost cae casi a cero porque opera más.

### 6. Why macro-F1 and not accuracy?
*¿Por qué F1-macro y no accuracy?* — contesta **Expositor 1**

> **If a model always says hold, the accuracy is about 40 percent. Macro-F1 gives the same weight to buy, hold and sell.**

Si un modelo siempre dice mantener, la exactitud es de 40 %. F1-macro le da el mismo peso a las tres clases.

### 7. Why a one-day horizon?
*¿Por qué un horizonte de un día?* — contesta **Expositor 1**

> **We want a daily signal. It is also the most difficult case. Longer horizons are a different problem, for future work.**

Queremos una señal diaria; además es el caso más difícil. Otros horizontes son otro problema, trabajo futuro.

### 8. Why not Transformers or GRU?
*¿Por qué no Transformers o GRU?* — contesta **Expositor 2**

> **Transformers need much more data. In our tests, very different networks, small and big, give the same result. So the limit is the data, not the architecture.**

Los Transformers necesitan muchos más datos. Redes muy distintas dan lo mismo: el límite son los datos, no la arquitectura.

### 9. Can I reproduce your results?
*¿Puedo reproducir sus resultados?* — contesta **Expositor 1**

> **Yes. The data is free from Yahoo Finance. The code, the seeds and the library versions are public, in the supplementary material.**

Sí. Los datos son gratis; código, semillas y versiones están en el material suplementario.

### 10. Global model or one model per stock?
*¿Modelo global o uno por acción?* — contesta **Expositor 2**

> **We tested both. The global model has seven times more data, and it is better or equal.**

Probamos los dos. El global tiene siete veces más datos y es mejor o igual.

### 11. What about survivorship bias? Only seven tech stocks.
*¿Y el sesgo de supervivencia? Solo siete acciones tecnológicas.* — contesta **Expositor 1**

> **Yes, it is a limitation. We compare models on the same data. We do not say the results are true for the whole market.**

Sí, es una limitación. Comparamos modelos con los mismos datos; no decimos que valga para todo el mercado.

### 12. Can people use this to trade?
*¿Se puede usar para invertir?* — contesta **Expositor 1**

> **It is a comparison, not a trading system. But for daily data, a simple regularized model is a good starting point.**

Es una comparación, no un sistema de inversión. Pero un modelo simple regularizado es un buen punto de partida.

Respuestas más completas: `../07_PREGUNTAS_MICAI.md`.

---

## Frases de apoyo (para cualquier momento)

| Inglés | Español | Se dice |
|---|---|---|
| **Sorry, could you repeat the question, please?** | ¿Perdón, puede repetir la pregunta, por favor? | SÓ-ri, cud yu ri-PÍT de CUÉS-chon, plis? |
| **Could you speak a little more slowly, please?** | ¿Podría hablar un poco más despacio? | cud yu SPIK a LÍ-tel mor SLÓU-li, plis? |
| **Thank you for the question.** | Gracias por la pregunta. | ZÉNK yu for de CUÉS-chon. |
| **That is a good question. My colleague will answer.** | Buena pregunta. Mi compañero(a) va a responder. | dat is a gud CUÉS-chon. mai CÓ-lig uil ÁN-ser. |
| **We have more details in the paper.** | Tenemos más detalles en el artículo. | ui jav mor DÍ-teils in de PÉI-per. |
| **We did not test that. It is future work.** | No lo probamos. Es trabajo futuro. | ui did not test dat. it is FIÚ-cher uork. |
| **Let me show you a backup slide.** | Le muestro una diapositiva de respaldo. | let mi SHOU yu a BÁK-ap slaid. |
| **We can talk more after the session.** | Podemos platicar más al final de la sesión. | ui can tok mor ÁF-ter de SÉ-shon. |
