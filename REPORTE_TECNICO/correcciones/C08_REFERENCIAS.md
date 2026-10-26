# C08 — Referencias (p. 103–104)

## Resumen de puntos

| ID | Tema | Prioridad |
|---|---|---|
| 8-01 | Título incorrecto de Fama (1970) | IMPORTANTE |
| 8-02 | [21] Goodfellow et al. no se cita | FORMA |
| 8-03 | Orden de numeración (IEEE) | FORMA |
| 8-04 | Referencias que el texto usa y no están | IMPORTANTE |
| 8-05 | Referencias para lo que se agrega | IMPORTANTE |
| 8-06 | El artículo propio | IMPORTANTE |
| 8-07 | Sitios web sin fecha de consulta | FORMA |
| 8-08 | Verificar [19] | IMPORTANTE |

---

### 8-01 · [2] Fama · IMPORTANTE
**Dice:** E. F. Fama, "Efficient capital markets: A review of empirical
work".
**Debe decir:** E. F. Fama, "Efficient capital markets: A review of
**theory and** empirical work", *The Journal of Finance*, vol. 25, no. 2,
pp. 383–417, 1970. (Así aparece en el paper.)

### 8-02 · [21] Goodfellow, Bengio y Courville · FORMA
Está en la lista pero nunca se cita. Citarla en §2.5.1 (redes profundas),
que hoy no tiene ninguna cita (2-17).

### 8-03 · Orden · FORMA
En IEEE la numeración sigue el orden de primera aparición: hoy se lee [15],
[17], [16] y [22], [20], [23] (3-02). Usar el administrador de fuentes de
Word para que se renumere solo.

### 8-04 · Citadas en el texto y ausentes de la lista · IMPORTANTE

| Dónde se usa | Referencia a agregar |
|---|---|
| §4.3.2 y Tabla 4 (momentum mensual) | N. Jegadeesh y S. Titman, "Returns to buying winners and selling losers: Implications for stock market efficiency", *The Journal of Finance*, vol. 48, no. 1, pp. 65–91, 1993 |
| §2.1.4 (RSI), §4.3.4 (ATR) | J. W. Wilder, *New Concepts in Technical Trading Systems*. Greensboro, NC: Trend Research, 1978 |
| §4.4.3 (SHAP), si se conserva la mención | S. M. Lundberg y S.-I. Lee, "A unified approach to interpreting model predictions", en *Advances in Neural Information Processing Systems*, pp. 4765–4774, 2017 |
| §4 (CRISP-DM) | P. Chapman et al., *CRISP-DM 1.0: Step-by-step data mining guide*, SPSS, 2000 (o R. Wirth y J. Hipp, 2000) |
| §4 (SCRUM) | K. Schwaber y J. Sutherland, *The Scrum Guide*, 2020 |

### 8-05 · Para el contenido nuevo · IMPORTANTE

| Para | Referencia (las marcadas con * ya están en el paper) |
|---|---|
| Revisión de DL en finanzas (3.4, 1.1) | *O. B. Sezer, M. U. Gudelek y A. M. Ozbayoglu, "Financial time series forecasting with deep learning: A systematic literature review: 2005–2019", *Applied Soft Computing*, vol. 90, 106181, 2020 |
| LSTM en el S&P 500 (3.4) | *T. Fischer y C. Krauss, "Deep learning with long short-term memory networks for financial market predictions", *European Journal of Operational Research*, vol. 270, no. 2, pp. 654–669, 2018 |
| Modelos regularizados igualan a redes (3.4, 7.3) | *J. Patel, S. Shah, P. Thakkar y K. Kotecha, "Predicting stock and stock price index movement using trend deterministic data preparation and machine learning techniques", *Expert Systems with Applications*, vol. 42, no. 1, pp. 259–268, 2015 |
| Árboles y lineales vs. DL en datos tabulares (2.4.2, 7.3) | *L. Grinsztajn, E. Oyallon y G. Varoquaux, "Why do tree-based models still outperform deep learning on tabular data?", en *NeurIPS Datasets and Benchmarks*, vol. 35, 2022 |
| Cuándo ganan las redes (7.3) | *S. Gu, B. Kelly y D. Xiu, "Empirical asset pricing via machine learning", *The Review of Financial Studies*, vol. 33, no. 5, pp. 2223–2273, 2020 |
| Optuna (4.10) | *T. Akiba, S. Sano, T. Yanase, T. Ohta y M. Koyama, "Optuna: A next-generation hyperparameter optimization framework", en *Proc. KDD*, pp. 2623–2631, 2019 |
| TPE (4.10) | J. Bergstra, R. Bardenet, Y. Bengio y B. Kégl, "Algorithms for hyper-parameter optimization", en *NeurIPS*, 2011 |
| Elastic net (4.8.1) | *H. Zou y T. Hastie, "Regularization and variable selection via the elastic net", *J. R. Stat. Soc. B*, vol. 67, no. 2, pp. 301–320, 2005 |
| CNN (2.5.3) | *Y. LeCun et al., "Backpropagation applied to handwritten zip code recognition", *Neural Computation*, vol. 1, no. 4, pp. 541–551, 1989 |
| Focal loss (2.5.1, 4.8) | T.-Y. Lin, P. Goyal, R. Girshick, K. He y P. Dollár, "Focal loss for dense object detection", en *Proc. ICCV*, pp. 2980–2988, 2017 |
| AdamW (2.5.1) | I. Loshchilov y F. Hutter, "Decoupled weight decay regularization", en *ICLR*, 2019 |
| Bootstrap por bloques (2.8) | H. R. Künsch, "The jackknife and the bootstrap for general stationary observations", *The Annals of Statistics*, vol. 17, no. 3, pp. 1217–1241, 1989 |
| Kappa (2.6) | J. Cohen, "A coefficient of agreement for nominal scales", *Educational and Psychological Measurement*, vol. 20, no. 1, pp. 37–46, 1960; y J. R. Landis y G. G. Koch, "The measurement of observer agreement for categorical data", *Biometrics*, vol. 33, no. 1, pp. 159–174, 1977 |
| Error estándar del Sharpe (4.11) | A. W. Lo, "The statistics of Sharpe ratios", *Financial Analysts Journal*, vol. 58, no. 4, pp. 36–52, 2002 |
| Sharpe (4.11) | W. F. Sharpe, "The Sharpe ratio", *The Journal of Portfolio Management*, vol. 21, no. 1, pp. 49–58, 1994 |
| scikit-learn | F. Pedregosa et al., "Scikit-learn: Machine learning in Python", *JMLR*, vol. 12, pp. 2825–2830, 2011 |
| PyTorch | A. Paszke et al., "PyTorch: An imperative style, high-performance deep learning library", en *NeurIPS*, 2019 |

Antes de agregar cada una, verificar los datos bibliográficos con la fuente
original (las del paper ya pasaron la revisión de Springer).

### 8-06 · El artículo propio · IMPORTANTE
Agregar y citar (en 1.5, 3.6, 6.4–6.5 y el anexo):

> J. B. Polvo Cuatianquiz, A. Reyes Vera, E. Juárez Carbajal, D. Reyes Ramos
> y M. Aragón García, "A Benchmark of Five Machine-Learning Architectures for
> Daily Trading-Signal Classification on US Tech Equities", en *Advances in
> Computational Intelligence. MICAI 2026*, Lecture Notes in Artificial
> Intelligence, Springer, 2026 (en prensa).

Verificar el orden de autores y el título del volumen con
`paper_review/paper.tex` y, cuando salga, agregar el DOI y las páginas
(`PAPER_MICAI/01_FICHA_Y_ESTADO.md`).

### 8-07 · [25] TrendSpider y [26] Trade Ideas · FORMA
Agregar "Consultado: [fecha]" (son páginas web y los precios cambian).

### 8-08 · [19] Sonkavde et al. · IMPORTANTE
Verificar que la descripción del texto (§3.3) corresponda a ese artículo
(ver 3-03).
