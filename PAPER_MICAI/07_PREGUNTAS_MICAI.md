# 07 — Preguntas probables en MICAI (inglés y español)

> Respuestas cortas para el público del congreso. Las de los sinodales sobre
> el artículo están en [`ESTUDIO_TT/D_defensa/D7_PREGUNTAS_PAPER.md`](https://github.com/barudust/TT/blob/main/ESTUDIO_TT/D_defensa/D7_PREGUNTAS_PAPER.md) (repositorio del TT).
> Regla: responder con lo que dice el artículo; si la pregunta va más allá,
> se puede mencionar lo que el TT hizo después, aclarando "since submission".

---

### P1. Isn't this just the efficient market hypothesis? Is there any signal at all?

**EN.** The signal is small but measurable: LR reaches 0.404 macro-F1 with a
95 % confidence interval of [0.379, 0.428], above the 0.333 random level. We
do not claim exploitable alpha; the paper is a comparative benchmark under
identical conditions.

**ES.** Hay señal pequeña pero medible (0.404, intervalo que no incluye 0.333).
No afirmamos que sea explotable; es una comparación entre modelos.

### P2. Why should a linear model beat deep networks?

**EN.** About 10 500 training rows and a near-noise one-day label put models
with 10⁵–10⁶ parameters in an overfitting regime. The 61 indicators are
already multi-day non-linear summaries, so a linear combination captures most
of the signal. Validation loss of every network stays at ln 3, and shrinking
the LSTM from 592 k to 10 k parameters changes nothing: the limit is the
information, not the capacity. This agrees with Grinsztajn et al. on tabular
data; networks win with tens of thousands of stocks and decades of data (Gu,
Kelly and Xiu).

**ES.** Pocas muestras para muchos parámetros, variables que ya resumen la
historia, pérdida de validación de las redes en ln 3. Coincide con la
literatura de datos tabulares.

### P3. Did the deep models get a fair search?

**EN.** That was the reviewers' main point, and Section 8 answers it: every
model is tuned with the same Optuna sampler on the same decision year (80
trials and 17–20 hyper-parameters for each network, 150 trials for LR and
XGBoost), nothing is decided on the test year and all five are scored on the
same 1 736 rows. The gap widens. The search is symmetric in procedure, not in
dimension, so we only claim that a realistic search does not overturn the
ranking.

**ES.** Sí, en la §8: misma herramienta y mismo año de decisión, nada con la
prueba, mismas filas. La brecha crece.

### P4. Only one test year. How do you know 2025 is not special?

**EN.** We acknowledge it as the main limitation. 2025 is within the
historical range and not an easy year (below-median return, high
volatility). Since submission we rolled the protocol over 2020–2025: LR and
XGBoost tie at the top (the six-year difference is not significant) and both
stay above the three networks; on unseen 2026 data LR again ranked first in
macro-F1.

**ES.** Es la limitación principal. Después del envío lo extendimos a seis
años y a 2026: los clásicos siguen arriba de las redes; LR y XGBoost empatan.

### P5. No transaction costs?

**EN.** Deliberately omitted for a first-order comparison; the paper predicts
that costs favour the model that trades least. Since submission we computed
it: with 10 basis points per position change, LR's Sharpe goes from +0.89 to
+0.62 and XGBoost's from +0.46 to +0.01, because XGBoost changes position much
more often.

**ES.** Se omitieron a propósito. Ya los calculamos: con 10 pb la LR conserva
+0.62 y XGBoost cae a +0.01.

### P6. Why macro-F1 and not accuracy or returns?

**EN.** Predicting HOLD always gives about 40 % accuracy and zero F1 for BUY
and SELL; macro-F1 penalizes that collapse. Returns are reported too (win
rate, profit factor, drawdown, Sharpe), because good classification does not
guarantee profit.

### P7. Why the 30/70 percentile label and a one-day horizon?

**EN.** Percentiles adapt to the volatility regime without choosing an
arbitrary threshold, and keep the classes close to 30/40/30. One day is the
product we wanted (a daily signal) and the hardest, noisiest case, which
makes the comparison demanding. Longer horizons are a different problem and
future work.

### P8. Is the look-back picked on the test set in Section 7 a leak?

**EN.** It is a protocol flaw that favours the deep models, and the paper
discloses it. That is why Section 7 is a lower bound on LR's margin and why
Section 8 removes it.

### P9. Why not Random Forest, SVM, Transformers, GRU…?

**EN.** We chose one representative per family: a linear baseline, gradient
boosting and three sequence architectures. Since the diagnosis shows that
very different networks of very different sizes reach the same validation
loss, we do not expect another architecture to change the conclusion with
this input; Transformers would need far more data.

### P10. Global model or one model per stock?

**EN.** Both are in the paper; pooling helps XGBoost in all three experiments
and the deep models in seven of nine, and is neutral for LR. Pooling
multiplies the sample by seven, and the percentile label makes the classes
comparable across stocks.

### P11. Survivorship bias? Only seven tech stocks.

**EN.** Yes, they are survivors of one sector and one market; we list it as a
limitation. The benchmark is about comparing models on the same data, not
about generalizing to the market.

### P12. Can I reproduce it?

**EN.** Yes. Data are free from Yahoo Finance; code, seeds, library versions
and data checksums are in the supplementary material, and the current code
reproduces the published runs exactly (18 of 18 deep-model cells and all 24 LR
runs).

### P13. What is the practical takeaway for practitioners?

**EN.** Start with a well-regularized linear classifier; it is cheap,
interpretable and hard to beat on daily data without alternative sources.
Spend effort on choosing the assets and on better data before adding model
complexity.

### P14. Does the LSTM use bidirectional layers? Isn't that a leak?

**EN.** Within a closed input window everything is in the past, so reading it
in both directions does not use future information. In Section 8 the search
selected a unidirectional LSTM with attention, and it still ranks below LR.

### P15. What about the CNN-LSTM with OHLCV channels mentioned in Section 4?

**EN.** That sentence describes an earlier design; in the reported runs all
five models receive exactly the same 61 features. *(Solo si lo preguntan; ver
`04_PAPER_VS_TT.md` §3.)*
