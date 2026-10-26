# 06 — Guion para la presentación en MICAI

> Base para preparar las diapositivas del congreso. Pensado para **15 minutos
> de exposición + 5 de preguntas** (ajustar al tiempo que indique el programa
> de MICAI). Diapositivas y discurso en **inglés** (el artículo está en
> inglés); notas de apoyo en español. Solo se usan resultados que están en
> el artículo; lo que el TT agregó después va en una diapositiva final
> opcional y marcado como "since submission".
>
> Figuras listas en `figuras_presentacion/` (P01–P06) y en
> `../paper_review/figures/` (`fig_signal_dist.png`, `fig_sharpe_heatmap.png`).

---

## Mensaje central (una frase)

> **"On daily, free data for seven large-cap tech stocks, a well-regularized
> logistic regression matches or beats XGBoost and three deep networks — and
> the result survives a symmetric hyper-parameter search and bootstrap
> confidence intervals."**

Tres ideas que el público debe llevarse:
1. A simple linear baseline is hard to beat in this regime.
2. Statistical feature pre-selection does not help (11 of 15 cases).
3. Which stock you trade matters more than which model you use.

---

## Diapositivas

| # | Título (en la diapositiva) | Contenido | Figura | Tiempo |
|---|---|---|---|---:|
| 1 | A Benchmark of Five Machine-Learning Architectures for Daily Trading-Signal Classification on US Tech Equities | Autores, ESCOM-IPN y CIC-IPN, MICAI 2026 | — | 0:20 |
| 2 | Why another benchmark? | Tres problemas: 1–2 modelos por estudio; accuracy/RMSE que no se traducen en dinero; filtrar variables sin probar que ayude | — | 1:00 |
| 3 | Task: one signal per day | BUY / HOLD / SELL para AAPL, NVDA, TSLA, AMZN, MSFT, GOOGL, META. Etiqueta: percentiles 30/70 del retorno del día siguiente en 252 días (adaptativa, sin *look-ahead*) | Ecuación de la etiqueta (o versión en inglés de `../REPORTE_TECNICO/diagramas/D10_etiqueta`) | 1:15 |
| 4 | Data and features | Yahoo Finance gratis, 2013–2025; 61 indicadores en 9 familias + SPY y VIX | Lista de familias | 0:50 |
| 5 | Same test year, different history | Tabla 1: A/B/C con 10/6/4 años, todos prueban en 2025. Por qué 2025 es defendible (retorno debajo de la mediana, volatilidad alta) | Tabla 1 | 1:00 |
| 6 | Five models, one protocol | LR, XGBoost, LSTM, 1-D CNN, CNN-LSTM; global y por acción; 120 corridas; F1-macro + backtest | Esquema simple | 1:00 |
| 7 | Result 1 — LR leads on average | LR 0.399 promedio; gana A y C; XGBoost cerca | **P01** | 1:30 |
| 8 | …and in money | Exp B: LR profit factor 1.21 y Sharpe +0.76, los más altos | **P04** | 1:00 |
| 9 | Result 2 — Do not pre-filter features | 11 de 15 casos: mejor usar las 61; la regularización interna gana | **P03** | 1:15 |
| 10 | Result 3 — The ticker matters more than the model | 15.5 % contra 3.4 % de la variación del Sharpe | **P05** (+ opcional `fig_sharpe_heatmap.png`) | 1:15 |
| 11 | Was the comparison fair? | Dos asimetrías (búsqueda y ventana elegida en prueba) → protocolo dev/final, mismas 1 736 filas, Optuna para los cinco | Esquema dev/final | 1:15 |
| 12 | A serious search does not close the gap | LR 0.404 [0.379, 0.428], significativamente mejor que los cuatro; las redes caen | **P02** o **P06** | 1:30 |
| 13 | Why does LR win? | Pocas muestras para 10⁵–10⁶ parámetros; variables ya son agregados de varios días; pérdida de validación de las redes en ln 3; LSTM de 592 k a 10 k sin cambio | — | 1:00 |
| 14 | Limitations | Un año de prueba; sin costos; siete acciones de un sector; búsqueda simétrica en procedimiento, no en dimensión | — | 0:40 |
| 15 | Takeaways | Las tres ideas de arriba; código y datos reproducibles (repositorio, suplementario) | — | 0:30 |
| (16) | Since submission *(opcional, respaldo)* | Seis años de prueba (LR y XGBoost empatan, ambos sobre las redes), costos de 10 pb (LR +0.62, XGBoost +0.01), datos de 2026 no vistos (LR primera en F1) | — | — |

Total ≈ 15 minutos. Si hay menos tiempo: quitar 4 (fusionar con 3), 8
(mencionarlo en 7) y 13 (mencionarlo en 12).

---

## Notas por diapositiva (qué decir)

**2.** "Most papers compare one or two deep models against each other, and
report accuracy. With three near-balanced classes, predicting HOLD always
already gives about 40 % accuracy. We wanted a fair, five-model comparison
scored both as classification and as a trading strategy."

**3.** "Each day, each stock gets one of three labels, comparing tomorrow's
log return with the 30th and 70th percentiles of the previous year. The
thresholds adapt to the volatility regime and use only past data."

**5.** "The three splits share the test year, so any difference between them
is only the amount of history. 2025 is not an easy year: below-median return,
third-highest volatility."

**7.** "Logistic regression with elastic-net is first on average, 0.399. Note
the random baseline is 0.333: the signal is small, as expected for one-day
returns." *(Si preguntan por las redes en esta tabla: su ventana se eligió con
la prueba, lo que les favorece.)*

**9.** "Filtering features with Pearson, VIF, SHAP or Spearman hurt in 11 of
15 cases. The model's own regularization selects better than an external
univariate screen."

**10.** "Decomposing the Sharpe of the 105 per-ticker runs, the ticker
explains 15.5 % and the model only 3.4 %. Choosing the stock matters more
than choosing the architecture."

**11.** "Reviewers rightly asked whether the deep models had a fair chance.
They had a smaller search, and their look-back was picked on the test set. So
we rebuilt the protocol: every decision on 2024, the test year evaluated once,
the same rows and the same Optuna search for everyone."

**12.** "The gap does not close; it widens. LR is significantly better than
each of the other four; none of the others differ among themselves. The
biggest lever for the networks was not a hyper-parameter but the checkpoint
criterion."

**13.** "Validation loss of every network stays at ln 3, the value of
predicting one third for each class. A 10 k-parameter LSTM does as well as a
592 k one. The limit is the information in the inputs, not the capacity."

---

## Recomendaciones de forma

- Una idea por diapositiva; el número clave grande (0.399, 11/15, 15.5 % vs
  3.4 %, 0.404).
- Mismos colores por modelo que las figuras P01–P06 (LR azul, XGBoost
  naranja, LSTM verde agua, CNN-LSTM amarillo, 1-D CNN rosa).
- Llevar la Tabla 6 completa en una diapositiva de respaldo (preguntas sobre
  hiperparámetros) y las Tablas 3–5 completas en otra.
- Ensayar las respuestas de `07_PREGUNTAS_MICAI.md`, sobre todo P1–P5.
- Tener a mano el enlace al repositorio y a la plataforma
  (https://tt-frontend-womf.onrender.com) por si preguntan por
  reproducibilidad o aplicación.

## Material que falta preparar (para otra sesión)

1. El deck de diapositivas con este guion.
2. Versión en inglés de los diagramas de etiqueta y de protocolo dev/final
   (`../REPORTE_TECNICO/diagramas/fuente/` genera las versiones en español;
   basta traducir los textos).
3. Un guion de 2 minutos ("elevator pitch") por si la sesión se retrasa.
