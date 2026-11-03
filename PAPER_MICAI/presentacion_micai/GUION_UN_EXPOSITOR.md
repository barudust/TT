# Guion para un expositor — MICAI 2026

> Generado desde `fuente/guion.py` (no editar a mano: cambiar ahí y volver a correr
> `generar_guion.py`). Inglés sencillo, frases cortas. Debajo de cada bloque en inglés
> va la traducción, para saber qué se está diciendo: **en el congreso se dice solo el
> inglés**. Para tenerlo a la mano al presentar están las tarjetas (`TARJETAS_*.pdf`).

**Cuándo y dónde:** Jueves 5 de noviembre de 2026, 16:40 h, Room 1104, Tec de Monterrey, Campus Chihuahua. Sesión *Machine Learning & Data Analytics* (16:00–18:20), Paper ID 78.

**Duración total: 8:24 min** (límite oficial: 10 min de exposición + 5 de preguntas).
El margen es para hablar despacio y respirar. Versión alternativa: `GUION_DOS_EXPOSITORES.md`.

- ✂ marca una frase que se puede saltar si vas tarde (la información ya está en la diapositiva).

---

## Diapositiva 1 · Portada · 34 s (minuto 0:00 → 0:34)

> **Good afternoon, everyone.**  
> **My name is Baruc Polvo. I am from ESCOM, at the Instituto Politécnico Nacional, in Mexico City.**  
> **Today I will present our benchmark of five machine learning models for daily trading signals.**  
> **This is joint work with my colleagues from ESCOM and CIC.**  

<details><summary>Traducción</summary>

- Buenas tardes a todos.
- Me llamo Baruc Polvo. Soy de ESCOM, del Instituto Politécnico Nacional, en la Ciudad de México.
- Hoy voy a presentar nuestra comparación de cinco modelos de aprendizaje automático para señales diarias de trading.
- Es un trabajo conjunto con mis colegas de ESCOM y del CIC.

</details>

## Diapositiva 2 · La pregunta · 50 s (minuto 0:34 → 1:24)

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

## Diapositiva 3 · Datos y etiqueta · 62 s (minuto 1:24 → 2:26)

> **We use seven big tech stocks: Apple, NVIDIA, Tesla, Amazon, Microsoft, Google and Meta.**  
> **The data is free, from Yahoo Finance, from 2013 to 2025.**  
> **Every day, each stock gets one label: buy, hold or sell.**  
> **We compare tomorrow's return with the last 252 days.**  
> **Top 30 percent: the label is buy. Bottom 30 percent: the label is sell. The rest is hold.**  
> **So the label changes with the volatility, and it only uses past data.**  
> **✂ The input is 61 features: technical indicators, plus the S&P 500 and the VIX.**  

<details><summary>Traducción</summary>

- Usamos siete acciones tecnológicas grandes: Apple, NVIDIA, Tesla, Amazon, Microsoft, Google y Meta.
- Los datos son gratis, de Yahoo Finance, de 2013 a 2025.
- Cada día, cada acción recibe una etiqueta: comprar, mantener o vender.
- Comparamos el retorno de mañana con los últimos 252 días.
- El 30 % más alto: la etiqueta es comprar. El 30 % más bajo: la etiqueta es vender. Lo demás es mantener.
- Así la etiqueta se adapta a la volatilidad y solo usa datos del pasado.
- La entrada son 61 variables: indicadores técnicos, más el S&P 500 y el VIX.

</details>

## Diapositiva 4 · Modelos y protocolo · 52 s (minuto 2:26 → 3:18)

> **We compare five models.**  
> **Two classical models: logistic regression and XGBoost.**  
> **And three deep networks: an LSTM, a one-dimensional CNN, and a hybrid CNN-LSTM.**  
> **We use three splits. All of them test on the same year, 2025. Only the training history changes: ten, six or four years.**  
> **We train one global model and one model per stock. In total, 120 runs.**  
> **Our main metric is macro-F1, and we also simulate a simple trading strategy.**  

<details><summary>Traducción</summary>

- Comparamos cinco modelos.
- Dos modelos clásicos: regresión logística y XGBoost.
- Y tres redes profundas: una LSTM, una CNN de una dimensión y una híbrida CNN-LSTM.
- Usamos tres particiones. Todas prueban en el mismo año, 2025. Solo cambia la historia de entrenamiento: diez, seis o cuatro años.
- Entrenamos un modelo global y un modelo por acción. En total, 120 corridas.
- Nuestra métrica principal es F1-macro y también simulamos una estrategia de trading sencilla.

</details>

## Diapositiva 5 · Resultado 1 · 60 s (minuto 3:18 → 4:18)

> **Here is the first result.**  
> **Each group is one split. The blue bar is logistic regression.**  
> **It has the best average macro-F1: zero point three nine nine.**  
> **It wins in splits A and C. In split B, XGBoost is very slightly better.**  
> **The dashed line is random guessing: zero point three three three. So the signal is small, but it is there.**  
> **In the trading simulation of split B, logistic regression is the best: Sharpe ratio zero point seven six, and profit factor one point two one.**  

<details><summary>Traducción</summary>

- Aquí está el primer resultado.
- Cada grupo es una partición. La barra azul es la regresión logística.
- Tiene el mejor F1-macro promedio: 0.399.
- Gana en las particiones A y C. En la B, XGBoost es apenas un poco mejor.
- La línea punteada es adivinar al azar: 0.333. La señal es pequeña, pero existe.
- En la simulación de trading de la partición B, la regresión logística es la mejor: Sharpe 0.76 y profit factor 1.21.

</details>

## Diapositiva 6 · Resultado 2 · 31 s (minuto 4:18 → 4:49)

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

## Diapositiva 7 · Resultado 3 · 42 s (minuto 4:49 → 5:31)

> **Third result. We split the variation of the Sharpe ratio.**  
> **The stock explains fifteen point five percent. The model explains only three point four percent.**  
> **So, choosing the stock matters about four and a half times more than choosing the model.**  
> **✂ For example, Amazon does well with almost any model, and Google does badly with almost any model.**  

<details><summary>Traducción</summary>

- Tercer resultado. Dividimos la variación del Sharpe.
- La acción explica 15.5 %. El modelo explica solo 3.4 %.
- Elegir la acción importa unas cuatro veces y media más que elegir el modelo.
- Por ejemplo, a Amazon le va bien con casi cualquier modelo y a Google le va mal con casi cualquiera.

</details>

## Diapositiva 8 · ¿Fue justo? · 44 s (minuto 5:31 → 6:15)

> **But was the comparison fair? The reviewers asked a good question.**  
> **XGBoost had a bigger search, and the input window of the networks was chosen on the test set.**  
> **So we rebuilt everything. All decisions use 2024. The test year, 2025, is used only one time.**  
> **All five models use the same search tool, Optuna, and the same 1,736 test rows.**  

<details><summary>Traducción</summary>

- ¿Pero la comparación fue justa? Los revisores hicieron una buena pregunta.
- XGBoost tuvo una búsqueda más grande, y la ventana de entrada de las redes se eligió con la prueba.
- Así que rehicimos todo. Todas las decisiones usan 2024. El año de prueba, 2025, se usa una sola vez.
- Los cinco modelos usan la misma herramienta de búsqueda, Optuna, y las mismas 1,736 filas de prueba.

</details>

## Diapositiva 9 · Resultado 4 · 48 s (minuto 6:15 → 7:03)

> **And the result? The gap does not close.**  
> **Logistic regression gets zero point four zero four, with a 95 percent confidence interval from zero point three seven nine to zero point four two eight.**  
> **It is significantly better than the other four models.**  
> **The validation loss of the networks never goes clearly below the random level.**  
> **✂ A very small LSTM gives the same result as a big one.**  

<details><summary>Traducción</summary>

- ¿Y el resultado? La diferencia no se cierra.
- La regresión logística obtiene 0.404, con un intervalo de confianza del 95 % de 0.379 a 0.428.
- Es significativamente mejor que los otros cuatro modelos.
- La pérdida de validación de las redes nunca baja claramente del nivel del azar.
- Una LSTM muy pequeña da lo mismo que una grande.

</details>

## Diapositiva 10 · ¿Por qué gana? · 47 s (minuto 7:03 → 7:50)

> **So, why does a simple linear model win here?**  
> **First, the data is small for deep models: about ten thousand rows.**  
> **Second, the one-day label is very noisy.**  
> **Third, our features already summarize many days, so a linear model can use them well.**  
> **We also have limitations: we test only one year, we do not include transaction costs, and we use only seven stocks from one sector.**  

<details><summary>Traducción</summary>

- Entonces, ¿por qué gana aquí un modelo lineal simple?
- Primero, los datos son pocos para modelos profundos: unas diez mil filas.
- Segundo, la etiqueta de un día tiene mucho ruido.
- Tercero, nuestras variables ya resumen muchos días, así que un modelo lineal las aprovecha bien.
- También tenemos limitaciones: probamos un solo año, no incluimos costos de transacción y usamos solo siete acciones de un sector.

</details>

## Diapositiva 11 · Cierre · 34 s (minuto 7:50 → 8:24)

> **To finish, three messages.**  
> **One: a well-regularized logistic regression is a strong and cheap baseline.**  
> **Two: do not filter the features before training.**  
> **Three: the stock matters more than the model.**  
> **Our code and data are public. Thank you. I am happy to answer your questions.**  

<details><summary>Traducción</summary>

- Para terminar, tres mensajes.
- Uno: una regresión logística bien regularizada es un punto de partida fuerte y barato.
- Dos: no filtren las variables antes de entrenar.
- Tres: la acción importa más que el modelo.
- Nuestro código y datos son públicos. Gracias. Con gusto respondo sus preguntas.

</details>

---

## Versión de 2 minutos (solo si el moderador pide recortar)

Si la sesión va retrasada y piden acortar, la dice **una sola persona** y solo se muestran
las diapositivas 1, 5, 9, 11 (escribir el número y **Enter**).

**Diapositiva 1**

> **Good afternoon. My name is Baruc Polvo, from the Instituto Politécnico Nacional, in Mexico City.**  
> **Our question is simple: for daily trading signals, do deep networks beat simple models?**  
> **Each day we predict one signal, buy, hold or sell, for seven big tech stocks, with free data from Yahoo Finance.**  

<details><summary>Traducción</summary>

- Buenas tardes. Me llamo Baruc Polvo, del Instituto Politécnico Nacional, en la Ciudad de México.
- Nuestra pregunta es simple: para señales diarias de trading, ¿las redes profundas le ganan a los modelos simples?
- Cada día predecimos una señal, comprar, mantener o vender, para siete acciones grandes de tecnología, con datos gratis de Yahoo Finance.

</details>

**Diapositiva 5**

> **We compared five models: logistic regression, XGBoost, LSTM, CNN and CNN-LSTM. Same data, same test year: 2025.**  
> **Logistic regression was the best on average, with a macro F1 of zero point three nine nine.**  

<details><summary>Traducción</summary>

- Comparamos cinco modelos: regresión logística, XGBoost, LSTM, CNN y CNN-LSTM. Mismos datos, mismo año de prueba: 2025.
- La regresión logística fue la mejor en promedio, con un F1-macro de 0.399.

</details>

**Diapositiva 9**

> **Then we gave all five models the same hyper-parameter search tool. The gap did not close.**  
> **Logistic regression got zero point four zero four, significantly better than the other four models.**  

<details><summary>Traducción</summary>

- Después les dimos a los cinco modelos la misma herramienta de búsqueda de hiperparámetros. La diferencia no se cerró.
- La regresión logística obtuvo 0.404, significativamente mejor que los otros cuatro modelos.

</details>

**Diapositiva 11**

> **Three messages. One: a simple linear model is hard to beat here.**  
> **Two: do not filter the features before training. Three: the stock matters more than the model.**  
> **Thank you. Questions?**  

<details><summary>Traducción</summary>

- Tres mensajes. Uno: aquí es difícil ganarle a un modelo lineal simple.
- Dos: no filtren las variables antes de entrenar. Tres: la acción importa más que el modelo.
- Gracias. ¿Preguntas?

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
| afternoon | af-ter-NÚN |
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
| regularization | re-guiu-la-ri-SÉI-shon |
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
| 2024 | tuén-ti tuén-ti FOR |
| 0.404 | SÍ-ro point FOR SÍ-ro FOR |
| 1,736 | uán ZÁU-sand SÉ-ven JÁN-dred ZÉR-ti SIKS |
| 252 | tu JÁN-dred FÍF-ti TU |

**Números:** el punto decimal se dice *point* y cada dígito por separado: 0.404 = *zero point four zero four*. Los porcentajes: 15.5 % = *fifteen point five percent*.

---

## Preguntas probables (respuestas cortas)

Las palabras clave son las que hay que reconocer al oír la pregunta.

### A. ¿La señal es real?

**1. Is there a real signal, or is it random?**  
*¿Hay señal real o es azar?*  
Si oyes: signal · random · luck · efficient market

> **Yes, there is a signal, but it is small. Logistic regression gets 0.404. Random is 0.333. The confidence interval does not include 0.333. We do not say that you can make money with it.**

Sí hay señal, pero es pequeña; el intervalo no incluye el azar. No decimos que se pueda ganar dinero con ella.

**2. The intervals overlap. Why do you say significant?**  
*Los intervalos se enciman. ¿Por qué dicen que es significativo?*  
Si oyes: overlap · intervals · significant

> **Because we test paired differences, on the same rows. Logistic regression minus each model has an interval that does not include zero. For example, plus 0.045 against XGBoost.**

Porque probamos diferencias pareadas, en las mismas filas; el intervalo de la diferencia no incluye el cero. (Ayuda: diapositiva 12.)

**3. What kind of bootstrap did you use?**  
*¿Qué bootstrap usaron?*  
Si oyes: bootstrap · block · resamples

> **A block bootstrap on the test rows: blocks of 20 rows and 2,000 resamples. We use blocks because the days are not independent.**

Bootstrap de bloques: bloques de 20 filas y 2,000 remuestreos, porque los días no son independientes.

### B. ¿Por qué gana la LR?

**4. Why does a linear model beat deep networks?**  
*¿Por qué un modelo lineal le gana a las redes?*  
Si oyes: why linear · deep networks · overfitting

> **The data is small for deep models, the one-day label is very noisy, and our features already summarize many days. The validation loss of the networks stays near the random level, and a small LSTM does the same as a big one.**

Pocos datos, etiqueta con ruido y variables que ya resumen. La pérdida de validación se queda cerca del azar. (Ayuda: diapositiva 10.)

**5. Why not Transformers, GRU or other models?**  
*¿Por qué no Transformers, GRU u otros modelos?*  
Si oyes: Transformer · GRU · random forest · SVM · other models

> **We did not test them. We chose a linear model, a tree model and three sequence networks. Transformers need much more data. In our tests, very different networks give the same result, so the limit is the data, not the architecture.**

No los probamos. Los Transformers necesitan muchos más datos. Redes muy distintas dan lo mismo: el límite son los datos.

**6. Which regularization did you use?**  
*¿Qué regularización usaron?*  
Si oyes: elastic net · L2 · C · regularization

> **In Section 7 we use elastic net. In Section 8, Optuna could choose L1, L2 or elastic net. It chose L2 with very strong regularization: C equal to 0.000165.**

Elastic net en la §7. En la §8 Optuna eligió L2 con regularización muy fuerte: C = 0.000165. (Ayuda: diapositiva 15.)

### C. ¿Fue justo?

**7. Did the deep models get a fair hyper-parameter search?**  
*¿Las redes tuvieron una búsqueda justa de hiperparámetros?*  
Si oyes: fair · search · tuning · hyper-parameters

> **Yes. In Section 8 all models use the same Optuna sampler, the same decision year and the same test rows. The networks search 17 to 20 hyper-parameters. The gap is bigger, not smaller.**

Sí: mismo muestreador, mismo año de decisión y mismas filas. Las redes buscan 17 a 20 hiperparámetros y la diferencia crece. (Ayuda: diapositiva 15.)

**8. Was the look-back chosen on the test set?**  
*¿La ventana se eligió con la prueba?*  
Si oyes: look-back · window · test set · oracle

> **Yes, in Section 7, and we say it in the paper. It helps the networks, not logistic regression. Section 8 removes this problem.**

Sí, en la §7, y el artículo lo dice. Favorece a las redes. La §8 lo quita.

**9. Is there data leakage?**  
*¿Hay fuga de datos?*  
Si oyes: leakage · look-ahead · future data · scaler · bidirectional

> **The label thresholds use only past data, shifted by one day. The scalers are fitted on the training data. In Section 8, no decision uses 2025. And a bidirectional LSTM only reads a closed window of past days.**

Umbrales con datos pasados, escaladores ajustados con entrenamiento, ninguna decisión con 2025. La LSTM bidireccional solo lee días pasados.

### D. Limitaciones

**10. You test only one year. Is 2025 special?**  
*Solo prueban un año. ¿2025 es especial?*  
Si oyes: one year · 2025 · special · walk-forward

> **It is our main limitation. 2025 is not an easy year: the return is below the median and the volatility is high. After the paper, we tested six years, 2020 to 2025. Logistic regression and XGBoost are similar, and both are better than the networks.**

Es la limitación principal. Después del artículo probamos seis años: LR y XGBoost son parecidos y superan a las redes. (Ayuda: diapositiva 13.)

**11. What about transaction costs?**  
*¿Y los costos de transacción?*  
Si oyes: costs · transaction · fees · slippage

> **They are not in the paper. After the paper we tested 10 basis points. Logistic regression keeps a Sharpe ratio of 0.62. XGBoost goes to almost zero, because it trades more.**

No están en el artículo. Con 10 puntos base la LR conserva Sharpe 0.62 y XGBoost cae casi a cero porque opera más. (Ayuda: diapositiva 13.)

**12. What about survivorship bias? Only seven tech stocks.**  
*¿Y el sesgo de supervivencia? Solo siete acciones tecnológicas.*  
Si oyes: survivorship · bias · only tech · other markets

> **Yes, it is a limitation. We compare models on the same data. We do not say the results are true for the whole market.**

Sí, es una limitación. Comparamos modelos con los mismos datos; no decimos que valga para todo el mercado.

### E. Decisiones de diseño

**13. Why macro-F1 and not accuracy?**  
*¿Por qué F1-macro y no accuracy?*  
Si oyes: accuracy · macro-F1 · why this metric

> **If a model always says hold, the accuracy is about 40 percent. Macro-F1 gives the same weight to buy, hold and sell.**

Si un modelo siempre dice mantener, la exactitud es de 40 %. F1-macro le da el mismo peso a las tres clases.

**14. Why a one-day horizon and this label?**  
*¿Por qué un horizonte de un día y esta etiqueta?*  
Si oyes: one day · horizon · percentile · 30/70 · label

> **We want a daily signal, and one day is the most difficult case. The percentiles adapt to the volatility, so we do not choose a fixed threshold. Longer horizons are a different problem, for future work.**

Queremos una señal diaria y es el caso más difícil. Los percentiles se adaptan a la volatilidad. Otros horizontes son trabajo futuro.

**15. Global model or one model per stock?**  
*¿Modelo global o uno por acción?*  
Si oyes: global · per stock · one model

> **We tested both. The global model has seven times more data, and it is better or equal.**

Probamos los dos. El global tiene siete veces más datos y es mejor o igual.

### F. Uso y siguiente paso

**16. Can people use this to trade?**  
*¿Se puede usar para invertir?*  
Si oyes: trade · real money · profit · buy and hold

> **It is a comparison, not a trading system. We do not say that it beats the market. But for daily data, a simple regularized model is a good starting point.**

Es una comparación, no un sistema de inversión. No decimos que le gane al mercado. Un modelo simple regularizado es un buen punto de partida.

**17. Can I reproduce your results?**  
*¿Puedo reproducir sus resultados?*  
Si oyes: reproduce · code · data · GitHub

> **Yes. The data is free from Yahoo Finance. The code, the seeds and the library versions are public. The link is on this slide.**

Sí. Datos gratis; código, semillas y versiones públicos. El enlace está en esta diapositiva.

**18. What is the next step?**  
*¿Cuál es el siguiente paso?*  
Si oyes: future work · next steps · what now

> **We want more stocks and sectors, longer horizons, and richer data, like news. We already extended the test to six years and to 2026 data.**

Más acciones y sectores, otros horizontes y datos más ricos. Ya lo extendimos a seis años y a datos de 2026.

Respuestas más completas: `../07_PREGUNTAS_MICAI.md`.

---

## Frases de apoyo (para cualquier momento)

| Inglés | Español | Se dice |
|---|---|---|
| **Sorry, could you repeat the question, please?** | ¿Perdón, puede repetir la pregunta, por favor? | SÓ-ri, cud yu ri-PÍT de CUÉS-chon, plis? |
| **Could you speak a little more slowly, please?** | ¿Podría hablar un poco más despacio? | cud yu SPIK a LÍ-tel mor SLÓU-li, plis? |
| **You are asking about transaction costs, right?** | ¿Pregunta por los costos, verdad? (repite la palabra clave para ganar tiempo) | yu ar ÁS-king a-BÁUT …, ráit? |
| **Thank you for the question.** | Gracias por la pregunta. | ZÉNK yu for de CUÉS-chon. |
| **We have more details in the paper.** | Tenemos más detalles en el artículo. | ui jav mor DÍ-teils in de PÉI-per. |
| **We did not test that. It is future work.** | No lo probamos. Es trabajo futuro. | ui did not test dat. it is FIÚ-cher uork. |
| **Let me show you a backup slide.** | Le muestro una diapositiva de respaldo. | let mi SHOU yu a BÁK-ap slaid. |
| **We can talk more after the session.** | Podemos platicar más al final de la sesión. | ui can tok mor ÁF-ter de SÉ-shon. |

## Si el moderador te dice…

| Oyes | Haces |
|---|---|
| “Two minutes left.” | Salta lo marcado con ✂ y sigue. |
| “Please wrap up.” / “Please finish.” | Escribe 11 + Enter y di los tres mensajes. |
| “You only have five minutes.” / “We are late.” | Usa la tarjeta de la versión corta. |
| “Time is up.” | Di “Thank you” y termina. |
