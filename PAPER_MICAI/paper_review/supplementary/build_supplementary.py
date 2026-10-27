"""
Genera el material suplementario del paper MICAI 2026 (capítulo 171490174):
"A Benchmark of Five Machine-Learning Architectures for Daily Trading-Signal
Classification on US Tech Equities".

Contiene EXACTAMENTE lo que el texto del paper promete (camera-ready del
8-sep-2026, paper_review/camera_ready/paper.tex), una sección por mención:

  S1  §3.3  "full table in the supplementary material"      -> las 61 variables
  S2  §5.1  "Per-class F1 for every run"                    -> 120 corridas
  S3  §7.1  "The same four metrics for Exps A and C"        -> 2 tablas
  S4  §7.3  "full heatmap in the supplementary material"    -> 1 figura
  S5  §11   "code, data manifests, fixed random seeds and
             library versions"                              -> código, datos, semillas, versiones

Nada más: las figuras que el .tex oculta con \\extrafigsfalse no se citan en el
texto publicado, así que no se incluyen.

Todas las cifras salen de la corrida v4 (RESULTADOS_OPTIMIZADOS/v4/
resultados_v4.csv) con la misma selección que el paper (para LSTM, CNN y
CNN-LSTM, el mejor de los look-backs 20/60 por F1 de test; ver
scripts_opt/consolidar_v4.py). El script se detiene si eso no reproduce las
Tablas 4, 5 y 6 del paper.

Uso (desde la raíz del repo; requiere pdflatex, p. ej. MiKTeX):
    python paper_review/supplementary/build_supplementary.py
Salidas (en paper_review/supplementary/):
    MICAI2026_ch171490174_supplementary.tex
    MICAI2026_ch171490174_supplementary.pdf   <- el archivo que se envía
"""
import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
AQUI = Path(__file__).resolve().parent
V4 = RAIZ / "RESULTADOS_OPTIMIZADOS" / "v4" / "resultados_v4.csv"
HEATMAP = RAIZ / "paper_review" / "camera_ready" / "figures" / "fig_sharpe_heatmap.png"
PARQUETS = RAIZ / "tesis_ml_stocks" / "01_raw_datasets"
NOMBRE = "MICAI2026_ch171490174_supplementary"
REPO_URL = "https://github.com/barudust/TT"
REPO_TAG = "micai2026"   # etiqueta de git que fija la versión del código citada

TITULO = ("A Benchmark of Five Machine-Learning Architectures for Daily "
          "Trading-Signal Classification on US Tech Equities")
TICKERS = ["AAPL", "NVDA", "TSLA", "AMZN", "MSFT", "GOOGL", "META"]
MODELOS = ["LR", "XGBoost", "LSTM", "CNN-LSTM", "CNN"]          # orden de las tablas del paper
NOMBRE_MODELO = {"LR": "LR", "XGBoost": "XGBoost", "LSTM": "LSTM", "CNN-LSTM": "CNN-LSTM", "CNN": "CNN 1D"}

# Las 61 variables con la definición del código de entrenamiento
# (scripts_v1/01_build_raw_dataset.py; idéntica a api/ml/features.py).
VARIABLES = [
    ("Log returns", [
        ("ret_1d", r"$\ln(C_t/C_{t-1})$"),
        ("ret_2d", r"$\ln(C_t/C_{t-2})$"),
        ("ret_3d", r"$\ln(C_t/C_{t-3})$"),
        ("ret_5d", r"$\ln(C_t/C_{t-5})$"),
        ("ret_10d", r"$\ln(C_t/C_{t-10})$"),
    ]),
    ("Momentum", [
        ("mom_5d", r"$C_t/C_{t-4}-1$"),
        ("mom_10d", r"$C_t/C_{t-9}-1$"),
        ("mom_20d", r"$C_t/C_{t-19}-1$"),
        ("mom_60d", r"$C_t/C_{t-59}-1$"),
    ]),
    ("Moving averages", [
        ("dist_ma10", r"$C_t/\mathrm{MA}_{10}-1$, with $\mathrm{MA}_k$ the $k$-day simple moving average of $C$"),
        ("dist_ma20", r"$C_t/\mathrm{MA}_{20}-1$"),
        ("dist_ma30", r"$C_t/\mathrm{MA}_{30}-1$"),
        ("dist_ma50", r"$C_t/\mathrm{MA}_{50}-1$"),
        ("dist_ma200", r"$C_t/\mathrm{MA}_{200}-1$"),
        ("cruce_ma10_ma50", r"$\mathrm{MA}_{10}/\mathrm{MA}_{50}-1$ (crossover)"),
        ("cruce_ma20_ma50", r"$\mathrm{MA}_{20}/\mathrm{MA}_{50}-1$ (crossover)"),
        ("cruce_ma50_ma200", r"$\mathrm{MA}_{50}/\mathrm{MA}_{200}-1$ (crossover)"),
        ("pendiente_ma20", r"$(\mathrm{MA}_{20,t}-\mathrm{MA}_{20,t-5})/\mathrm{MA}_{20,t-5}$ (slope)"),
    ]),
    ("Volatility", [
        ("atr_14", r"ATR(14): 14-day mean of $\mathrm{TR}_t=\max(H-L,\,|H-C_{t-1}|,\,|L-C_{t-1}|)$"),
        ("atr_norm", r"$\mathrm{ATR}(14)/C_t$"),
        ("vol_5d", r"$\mathrm{std}_5(\text{ret\_1d})\sqrt{252}$"),
        ("vol_10d", r"$\mathrm{std}_{10}(\text{ret\_1d})\sqrt{252}$"),
        ("vol_20d", r"$\mathrm{std}_{20}(\text{ret\_1d})\sqrt{252}$"),
        ("vol_60d", r"$\mathrm{std}_{60}(\text{ret\_1d})\sqrt{252}$"),
        ("vol_ratio_5_20", r"vol\_5d / vol\_20d"),
        ("vol_ratio_20_60", r"vol\_20d / vol\_60d"),
    ]),
    ("Oscillators", [
        ("rsi_14", r"Wilder RSI(14): $100-100/(1+\overline{\text{gain}}/\overline{\text{loss}})$, exponential smoothing $\alpha=1/14$"),
        ("rsi_7", r"Wilder RSI(7), $\alpha=1/7$"),
        ("macd", r"$(\mathrm{EMA}_{12}(C)-\mathrm{EMA}_{26}(C))/C_t$"),
        ("macd_sig", r"$\mathrm{EMA}_9(\text{MACD line})/C_t$"),
        ("macd_hist", r"$(\text{MACD line}-\text{signal line})/C_t$"),
        ("stoch_k", r"$\%K=100\,(C-\min_{14}L)/(\max_{14}H-\min_{14}L)$"),
        ("stoch_d", r"$\%D$: 3-day mean of $\%K$"),
        ("stoch_diff", r"$\%K-\%D$"),
        ("williams_r", r"$-100\,(\max_{14}H-C)/(\max_{14}H-\min_{14}L)$"),
    ]),
    ("Volume and flow", [
        ("vol_log", r"$\ln(V+1)$"),
        ("vol_ratio", r"$V_t/\mathrm{MA}_{20}(V)$"),
        ("obv_ratio", r"$\mathrm{OBV}_t/|\mathrm{MA}_{20}(\mathrm{OBV})|-1$, $\mathrm{OBV}_t=\sum\mathrm{sign}(\Delta C)\,V$ from the first downloaded day"),
        ("obv_pendiente", r"$\big((\mathrm{OBV}_t-\mathrm{OBV}_{t-5})/\mathrm{OBV}_{t-5}\big)/C_t$ (OBV slope)"),
        ("vwap_dist", r"$(C-\mathrm{VWAP}_{20})/\mathrm{VWAP}_{20}$, $\mathrm{VWAP}_{20}=\sum_{20}\mathrm{TP}\,V/\sum_{20}V$, $\mathrm{TP}=(H+L+C)/3$"),
        ("cmf_20", r"Chaikin money flow $\sum_{20}\mathrm{CLV}\,V/\sum_{20}V$, $\mathrm{CLV}=((C-L)-(H-C))/(H-L)$"),
        ("mfi_14", r"Money flow index over 14 days on $\mathrm{TP}\,V$"),
        ("vol_trend", r"$\mathrm{MA}_{20}(V)/\mathrm{MA}_{60}(V)-1$"),
    ]),
    ("Candle patterns", [
        ("rango_rel", r"$(H-L)/C$ (relative range)"),
        ("cambio_intra", r"$(C-O)/O$ (intraday change)"),
        ("cuerpo_rel", r"$|C-O|/(H-L)$ (body / range)"),
        ("sombra_sup", r"$(H-\max(O,C))/\mathrm{ATR}(14)$ (upper shadow)"),
        ("sombra_inf", r"$(\min(O,C)-L)/\mathrm{ATR}(14)$ (lower shadow)"),
        ("gap_apertura", r"$(O_t-C_{t-1})/C_{t-1}$ (opening gap)"),
        ("hl_ratio", r"$(C-L)/(H-L)$ (position of the close in the range)"),
    ]),
    ("Seasonality", [
        ("dia_sin", r"$\sin(2\pi d/5)$, $d$ = weekday (Monday $=0$)"),
        ("dia_cos", r"$\cos(2\pi d/5)$"),
        ("mes_sin", r"$\sin(2\pi m/12)$, $m$ = month (1--12)"),
        ("mes_cos", r"$\cos(2\pi m/12)$"),
        ("semana_mes", r"$(w-2.5)/2.5$, $w=\lfloor(\text{day of month}-1)/7\rfloor+1$"),
    ]),
    ("Market context", [
        ("SP500_ret", r"$\ln(\mathrm{SPY}_t/\mathrm{SPY}_{t-1})$"),
        ("SP500_vol20", r"$\mathrm{std}_{20}(\text{SP500\_ret})\sqrt{252}$"),
        ("SP500_mom20", r"$\mathrm{SPY}_t/\mathrm{SPY}_{t-19}-1$"),
        ("VIX", r"close of the CBOE VIX index (\texttt{\textasciicircum VIX})"),
        ("VIX_change", r"$\mathrm{VIX}_t/\mathrm{VIX}_{t-1}-1$"),
        ("VIX_norm", r"$(\mathrm{VIX}-\mathrm{MA}_{252}(\mathrm{VIX}))/\mathrm{std}_{252}(\mathrm{VIX})$"),
    ]),
]


def tt(nombre: str) -> str:
    return r"\texttt{" + nombre.replace("_", r"\_") + "}"


def cargar_v4() -> pd.DataFrame:
    """Las 120 corridas del paper (mejor look-back por F1 de test, como consolidar_v4.py)."""
    df = pd.read_csv(V4)
    idx = df.groupby(["modelo", "tipo", "experimento", "ticker"], dropna=False)["test_f1_macro"].idxmax()
    return df.loc[idx].reset_index(drop=True)


def verificar_contra_paper(d: pd.DataFrame) -> None:
    """Se detiene si las cifras no reproducen las Tablas 4, 5 y 6 del paper."""
    t4 = {"LR": (0.411, 0.385, 0.401), "XGBoost": (0.396, 0.386, 0.373), "LSTM": (0.389, 0.370, 0.370),
          "CNN-LSTM": (0.376, 0.384, 0.371), "CNN": (0.361, 0.343, 0.373)}
    t6 = {"LR": (0.411, 0.392, 0.359), "XGBoost": (0.376, 0.370, 0.352), "CNN-LSTM": (0.368, 0.342, 0.356),
          "LSTM": (0.314, 0.353, 0.326), "CNN": (0.378, 0.332, 0.280)}
    t5 = {"LR": (0.385, 0.497, 1.210, -0.470, 0.755), "XGBoost": (0.386, 0.500, 1.083, -0.432, 0.345),
          "CNN-LSTM": (0.384, 0.505, 1.041, -0.403, 0.147), "LSTM": (0.370, 0.491, 1.120, -0.406, 0.433),
          "CNN": (0.343, 0.510, 1.031, -0.434, 0.121)}
    assert len(d) == 120, len(d)
    g = d[d.tipo == "global"].set_index(["modelo", "experimento"])
    for m, vals in t4.items():
        for e, v in zip("ABC", vals):
            assert abs(g.loc[(m, e), "test_f1_macro"] - v) < 6e-4, ("Tabla 4", m, e)
    pt = d[d.tipo == "por_ticker"].groupby(["modelo", "experimento"]).test_f1_macro.mean()
    for m, vals in t6.items():
        for e, v in zip("ABC", vals):
            assert abs(pt.loc[(m, e)] - v) < 6e-4, ("Tabla 6", m, e)
    cols = ["test_f1_macro", "win_rate_test", "profit_factor_test", "max_drawdown_test", "sharpe_test"]
    for m, vals in t5.items():
        for c, v in zip(cols, vals):
            assert abs(g.loc[(m, "B"), c] - v) < 6e-4, ("Tabla 5", m, c)


def f3(x, signo=False) -> str:
    if pd.isna(x):
        return "--"
    return f"${x:+.3f}$" if signo else f"{x:.3f}"


def tabla_variables() -> str:
    filas, n = [], 0
    for familia, items in VARIABLES:
        if n:
            filas.append(r"\midrule")
        filas.append(rf"\multicolumn{{3}}{{@{{}}l}}{{\emph{{{familia}}} ({len(items)})}} \\*[1pt]")
        for nombre, definicion in items:
            n += 1
            filas.append(rf"{n} & {tt(nombre)} & {definicion} \\")
    assert n == 61, n
    cab = r"\# & Column & Definition \\"
    return "\n".join([
        r"\begin{longtable}{@{}r l >{\raggedright\arraybackslash}p{0.66\textwidth}@{}}",
        r"\caption{Input features, grouped by family (count in parentheses).}\label{tab:s1}\\",
        r"\toprule " + cab + r" \midrule \endfirsthead",
        r"\toprule " + cab + r" \midrule \endhead",
        r"\bottomrule \endlastfoot",
        *filas,
        r"\end{longtable}",
    ])


def tabla_corridas(d: pd.DataFrame) -> str:
    filas = []
    for m in MODELOS:
        if filas:
            filas.append(r"\midrule")
        for scope in ["Global"] + TICKERS:
            for e in "ABC":
                if scope == "Global":
                    r = d[(d.modelo == m) & (d.tipo == "global") & (d.experimento == e)].iloc[0]
                else:
                    r = d[(d.modelo == m) & (d.tipo == "por_ticker") & (d.ticker == scope) & (d.experimento == e)].iloc[0]
                lb = "--" if pd.isna(r.lookback) else str(int(r.lookback))
                filas.append(f"{NOMBRE_MODELO[m]} & {scope} & {e} & {lb} & {f3(r.test_f1_macro)} & "
                             f"{f3(r.test_f1_sell)} & {f3(r.test_f1_hold)} & {f3(r.test_f1_buy)} \\\\")
    assert sum(1 for f in filas if f.endswith("\\\\")) == 120
    cab = r"Model & Training & Exp & Look-back & F1-macro & F1 SELL & F1 HOLD & F1 BUY \\"
    return "\n".join([
        r"{\small\begin{longtable}{@{}l l c c c c c c@{}}",
        r"\caption{Test F1-macro and per-class F1 of the 120 runs (test year 2025).}\label{tab:s2}\\",
        r"\toprule " + cab + r" \midrule \endfirsthead",
        r"\toprule " + cab + r" \midrule \endhead",
        r"\bottomrule \endlastfoot",
        *filas,
        r"\end{longtable}}",
    ])


def tabla_economica(d: pd.DataFrame, exp: str, etiqueta: str, titulo: str) -> str:
    sub = d[(d.tipo == "global") & (d.experimento == exp)].set_index("modelo").reindex(MODELOS)
    cols = ["test_f1_macro", "win_rate_test", "profit_factor_test", "max_drawdown_test", "sharpe_test"]
    mejor = {c: sub[c].max() for c in cols}
    filas = []
    for m in MODELOS:
        celdas = []
        for c in cols:
            v = sub.loc[m, c]
            txt = f3(v, signo=(c == "sharpe_test")) if c != "max_drawdown_test" else f"${v:.3f}$"
            # \boldmath: \textbf solo no engruesa los valores en modo matemático ($-0.365$, $+1.067$)
            celdas.append(rf"{{\boldmath\textbf{{{txt}}}}}" if v == mejor[c] else txt)
        filas.append(f"{NOMBRE_MODELO[m]} & " + " & ".join(celdas) + r" \\")
    return "\n".join([
        r"\begin{table}[H]\centering",
        rf"\caption{{{titulo}}}\label{{{etiqueta}}}",
        r"\begin{tabular}{@{}lccccc@{}}\toprule",
        r"Model & F1 & Win rate & Profit factor & Max drawdown & Sharpe \\ \midrule",
        *filas,
        r"\bottomrule\end{tabular}\end{table}",
    ])


def manifiesto() -> str:
    filas = []
    for tk in TICKERS:
        p = PARQUETS / f"{tk}_raw.parquet"
        df = pd.read_parquet(p)
        sha = hashlib.sha256(p.read_bytes()).hexdigest()
        filas.append(rf"{tk} & {df.index.min():%Y-%m-%d} & {df.index.max():%Y-%m-%d} & {len(df):,} & "
                     rf"{{\scriptsize\texttt{{{sha}}}}} \\")
    return "\n".join([
        r"\begin{table}[H]\centering",
        r"\caption{Stored datasets \texttt{tesis\_ml\_stocks/01\_raw\_datasets/\textless TICKER\textgreater\_raw.parquet} "
        r"(one row per trading day: the 61 features, the raw OHLCV, and the label with its forward return "
        r"and percentile thresholds) and their SHA-256 checksums.}\label{tab:s5}",
        r"\begin{tabular}{@{}lcccl@{}}\toprule",
        r"Ticker & First day & Last day & Rows & SHA-256 \\ \midrule",
        *filas,
        r"\bottomrule\end{tabular}\end{table}",
    ])


def construir_tex(d: pd.DataFrame) -> str:
    codigo = [
        (r"Data download, features and label (Section~3)", [r"scripts_v1/01_build_raw_dataset.py"]),
        (r"Temporal splits (Section~3.4)", [r"scripts_opt/common_v4.py"]),
        (r"Statistical feature pre-selection (Section~6)", [r"scripts_opt/analisis_feature_selection.py"]),
        (r"Benchmark of 120 runs (Section~7)", [r"scripts_opt/train_all_v4.py", r"scripts_opt/consolidar_v4.py",
                                          r"RESULTADOS_OPTIMIZADOS/v4/resultados_v4.csv (results)"]),
        (r"Robustness study (Section~8)", [r"scripts_opt/run_v5.py", r"scripts_opt/common_v5.py",
                                     r"scripts_opt/reporte_v5.py", r"RESULTADOS_OPTIMIZADOS/v5/ (results)"]),
        ("Figures", [r"scripts_opt/plots_paper.py"]),
        ("Reproduction checks", [r"RESULTADOS_OPTIMIZADOS/v5/g0_replicacion.csv (results)",
                                 r"scripts_opt/replicar_lr_v4.py",
                                 r"RESULTADOS_OPTIMIZADOS/v4/replica_lr_v4.csv (results)"]),
        ("This document", [r"paper_review/supplementary/build_supplementary.py"]),
    ]
    def _ruta(r):
        if r.endswith(" (results)"):
            return r"\path{" + r[:-10] + "} (results)"
        return r"\path{" + r + "}"
    tabla_codigo = "\n".join([
        r"\begin{table}[H]\centering\small",
        r"\caption{Where each part of the paper is implemented (paths relative to the repository root).}\label{tab:code}",
        r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{0.34\textwidth}p{0.6\textwidth}@{}}\toprule",
        r"Part of the paper & Files \\ \midrule",
        *[f"{parte} & " + r" \newline ".join(_ruta(x) for x in rutas) + r" \\" for parte, rutas in codigo],
        r"\bottomrule\end{tabular}\end{table}",
    ])
    return rf"""\documentclass[10pt]{{article}}
\usepackage[T1]{{fontenc}}
\usepackage{{lmodern}}
\usepackage{{float}}
\usepackage[utf8]{{inputenc}}
\usepackage[letterpaper,margin=2.3cm]{{geometry}}
\usepackage{{amsmath,amssymb}}
\usepackage{{array,booktabs,longtable,graphicx,caption}}
\usepackage{{xurl}}
\usepackage[hidelinks]{{hyperref}}
\captionsetup{{font=small,labelfont=bf}}
\renewcommand{{\thetable}}{{S\arabic{{table}}}}
\renewcommand{{\thefigure}}{{S\arabic{{figure}}}}
\renewcommand{{\thesection}}{{S\arabic{{section}}}}
\setlength{{\LTcapwidth}}{{\textwidth}}
\binoppenalty=10000 \relpenalty=10000 % no partir fórmulas en + o = (S1)
\pagestyle{{plain}}
\begin{{document}}

\begin{{center}}
{{\Large\bfseries Supplementary Material\par}}\vspace{{4pt}}
{{\itshape {TITULO}\par}}\vspace{{3pt}}
{{\small MICAI 2026 --- Lecture Notes in Artificial Intelligence\par}}
\end{{center}}
\vspace{{4pt}}

\noindent This document contains the material that the paper refers to as ``supplementary
material''. Each section corresponds to one reference in the paper. The results in Sections S2--S4
come from the benchmark reported in Section~7 of the paper (120 runs, test year 2025); for the sequence models
(LSTM, CNN~1D and CNN-LSTM) the reported run is the better of the two look-backs (20 or 60 days)
by test F1-macro, as in the paper. They reproduce Tables~4, 5 and~6 of the paper.

\section{{Full list of the 61 input features (cited in Section~3.3)}}
All features are computed per ticker from daily OHLCV data adjusted for splits and dividends
($O,H,L,C,V$) and, for the last family, from SPY and the CBOE VIX, using only information
available at the close of day~$t$. Column names are those used in the code.

{tabla_variables()}

\section{{Per-class F1 for every run (cited in Section~5.1)}}
F1-macro and per-class F1 on the 2025 test set for the 120 runs (5 models $\times$
3 experiments $\times$ (1 global + 7 per-ticker)). ``Global'' models are trained on the seven
tickers together and scored on all of them; per-ticker models are trained and scored on one
ticker. Look-back is the number of past days given to the sequence models.

{tabla_corridas(d)}

\section{{Economic metrics for Exps A and C (cited in Section~7.1)}}
Same metrics as Table~5 of the paper (which reports Exp~B) for the global models of the other two
experiments: long on BUY, short on SELL, flat on HOLD, one-day holding period, no transaction
costs; Sharpe is annualized. Best value per column in bold.

{tabla_economica(d, "A", "tab:s3", "Economic metrics, Exp A (10 training years) GLOBAL, test = 2025.")}
{tabla_economica(d, "C", "tab:s4", "Economic metrics, Exp C (4 training years) GLOBAL, test = 2025.")}

\section{{Sharpe ratio by model and ticker (cited in Section~7.3)}}
\begin{{figure}}[H]\centering
\includegraphics[width=0.92\textwidth]{{{HEATMAP.name}}}
\caption{{Annualized Sharpe ratio of the per-ticker models, per model and ticker, for the three
experiments (test = 2025). These are the 105 values whose variance decomposition is given in
Section~7.3 of the paper.}}\label{{fig:s1}}
\end{{figure}}

\section{{Code, data manifest, random seeds and library versions (cited in Section~11)}}
\paragraph{{Code.}} The complete pipeline is publicly available at \url{{{REPO_URL}}}; a snapshot
of the repository for this paper is tagged \texttt{{{REPO_TAG}}} (\url{{{REPO_URL}/tree/{REPO_TAG}}}).
Table~\ref{{tab:code}} lists where each part of the paper is implemented.

{tabla_codigo}

\paragraph{{Data manifest.}} Source: Yahoo Finance through the \texttt{{yfinance}} library, daily
bars adjusted for splits and dividends (\texttt{{auto\_adjust=True}}), downloaded for 2013-01-01 to
2025-12-31; the first year serves as warm-up for the indicators. Market context: SPY and \texttt{{\textasciicircum VIX}}
over the same window. Label: one-day forward log-return; BUY if it reaches the 70th percentile and
SELL if it falls to the 30th percentile of the previous 252 trading days of the same ticker
(thresholds shifted by one day, so no future information enters them), HOLD otherwise. Rows per
ticker: training 2,516 (Exp~A, 2014--2023), 1,509 (Exp~B, 2018--2023) and 1,006 (Exp~C,
2020--2023); validation 252 (2024); test 248 (2025). Global models use the seven tickers together
(1,736 test rows); in Section~7 the sequence models were scored on the test days with a complete
look-back window (1,596 rows at look-back 20 and 1,316 at 60), which the protocol of Section~8
aligns to the same 1,736 rows. Table~\ref{{tab:s5}} lists the stored datasets.

{manifiesto()}

\paragraph{{Random seeds.}} Benchmark (Section~7): LR is trained with seeds $\{{42, 1, 7, 2024, 100\}}$ and
the final class is the majority vote of the five models; XGBoost, LSTM, CNN~1D and CNN-LSTM are
trained with seeds $\{{42, 1, 7\}}$ and their class probabilities are averaged; the Optuna search of
XGBoost uses a TPE sampler with seed~42. Robustness study (Section~8): Optuna TPE sampler with seed~42
(25 random start-up trials) and a median pruner for the deep models; every frozen configuration is
evaluated on the test year with seeds $\{{42, 1, 7, 2024, 100\}}$.

\paragraph{{Library versions and hardware.}} PyTorch~2.12 (CUDA~12.8), scikit-learn~1.7.2,
XGBoost~3.2.0 and Optuna~4.8, on an NVIDIA GeForce RTX~5060~Ti. These versions were recorded for
the robustness study (Section~8). Two checks show that this environment reproduces the benchmark of
Section~7. The 18 global sequence-model runs (LSTM, CNN~1D and CNN-LSTM; three experiments;
look-backs 20 and 60), re-run with the code of Section~8 set to the protocol of Section~7, give the
same test F1-macro as the published runs, to the four decimals stored, in 18 of 18 cases. The 24 LR
runs, re-run with the original code (Python~3.13.5, scikit-learn~1.7.2), give identical F1-macro,
per-class F1, Sharpe, win rate, profit factor and maximum drawdown in 24 of 24 cases
(Table~\ref{{tab:code}}, ``Reproduction checks''). The XGBoost runs and the per-ticker
sequence-model runs were not re-run.

\end{{document}}
"""


def pdflatex() -> str:
    exe = shutil.which("pdflatex")
    if exe:
        return exe
    miktex = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "MiKTeX" / "miktex" / "bin" / "x64" / "pdflatex.exe"
    if miktex.exists():
        return str(miktex)
    sys.exit("No se encontró pdflatex (instalar MiKTeX: winget install MiKTeX.MiKTeX).")


def main():
    d = cargar_v4()
    verificar_contra_paper(d)
    shutil.copy(HEATMAP, AQUI / HEATMAP.name)
    tex = AQUI / f"{NOMBRE}.tex"
    tex.write_text(construir_tex(d), encoding="utf-8")
    exe = pdflatex()
    for _ in range(2):   # dos pasadas para las referencias cruzadas y longtable
        r = subprocess.run([exe, "-interaction=nonstopmode", "-halt-on-error", tex.name],
                           cwd=AQUI, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            print(r.stdout[-3000:])
            sys.exit("pdflatex falló")
    log = (AQUI / f"{NOMBRE}.log").read_text(encoding="utf-8", errors="replace")
    problemas = [l for l in log.splitlines()
                 if "Warning" in l and ("undefined" in l.lower() or "Rerun to get" in l or "may have changed" in l)]
    if problemas:
        sys.exit("Advertencias de LaTeX:\n" + "\n".join(problemas))
    for ext in (".aux", ".log", ".out"):
        (AQUI / f"{NOMBRE}{ext}").unlink(missing_ok=True)
    print(f"PDF: {AQUI / (NOMBRE + '.pdf')}")


if __name__ == "__main__":
    main()
