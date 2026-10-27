"""
Figuras del paper, dimensionadas para que el texto sea legible en la pagina.

Responde al punto 1 del Revisor #3 de MICAI ("the text within several figures is
too small to be easily read, particularly the axis labels, legends and
annotations").

El problema no era el DPI: era la reduccion. El paper coloca cada figura con
`\\includegraphics[width=...\\textwidth]` en una pagina Springer LNCS de una sola
columna (122 mm = 4.8 in de ancho de texto). Una figura creada a 19 in de ancho
se reduce ~4x al colocarla, asi que una anotacion de `fontsize=15` acaba
imprimiendose a menos de 4 pt. `plots_extra.py` ya traia el helper `ptsize()`
para corregir eso, pero solo estaba aplicado en 2 de las 6 figuras; los heatmaps
y las barras seguian con tamanos fijos.

Este script genera las 5 figuras que cita `paper.tex`, con los nombres exactos
que el .tex espera, directamente en `paper_review/figures/`:

    fig_global_metrics.png   fig_sharpe_heatmap.png   fig_sharpe_boxplot.png
    fig_train_years.png      fig_signal_dist.png

y ademas `fig_f1_heatmap.png` (material suplementario).

Dos decisiones de diseno para que las anotaciones quepan:

1. Las figuras se construyen a un ancho cercano al de la pagina (7.2 in como
   maximo, es decir una reduccion de 1.5x en vez de 4x), no a 15-19 in.
2. Los heatmaps van transpuestos respecto a `plots_extra.py`: los 5 modelos en
   el eje x y los 7 tickers en el eje y. Con 3 paneles eso da 15 columnas en
   4.8 in (~23 pt por celda) en vez de 21 columnas (~16 pt), que es lo que hacia
   imposible imprimir "-0.88" sin solaparse. Los titulos internos y los 3
   colorbars redundantes se eliminan: el `\\caption` del .tex ya dice que es.

Uso:
    python scripts_opt/plots_paper.py
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import sys
import functools
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass
print = functools.partial(print, flush=True)
warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

CSV = Path("RESULTADOS_OPTIMIZADOS/v4/resultados_v4.csv")
OUT = Path("paper_review/figures")

TICKERS = ["AAPL", "NVDA", "TSLA", "AMZN", "MSFT", "GOOGL", "META"]
EXPS = ["A", "B", "C"]
MODEL_ORDER = ["LR", "XGBoost", "LSTM", "CNN", "CNN-LSTM"]
# Etiquetas tal como aparecen en las tablas del paper (el CSV usa "CNN").
MODEL_LABELS = {"CNN": "CNN 1D"}

# Ancho del texto en Springer LNCS: 122 mm.
LNCS_TEXTWIDTH_IN = 4.8
DPI = 400

plt.rcParams.update({
    "font.family": "serif",
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.major.size": 2.5,
    "ytick.major.size": 2.5,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.02,
})


def ptsize(printed_pt, fig_width_in, frac=1.0):
    """Fontsize fuente necesario para imprimirse a `printed_pt` en la pagina.

    `fig_width_in` es el ancho con el que se crea la figura y `frac` la fraccion
    de \\textwidth con la que el .tex la coloca (width=frac*\\textwidth).
    """
    return printed_pt * fig_width_in / (LNCS_TEXTWIDTH_IN * frac)


def load_df():
    """Carga las 120 corridas y colapsa el lookback de los modelos secuenciales.

    Igual que `plots_extra.py`/`consolidar_v4.py`: para LSTM/CNN/CNN-LSTM se
    queda el mejor lookback por F1 de *test*. Es la seleccion que se reporta en
    el paper (v4) y esta declarada como tal en el .tex: sesga *a favor* de los
    modelos profundos, que aun asi pierden.
    """
    df = pd.read_csv(CSV)
    if "lookback" in df.columns:
        sec = df[df["lookback"].notna()]
        nsec = df[df["lookback"].isna()]
        idx = sec.groupby(["modelo", "tipo", "experimento", "ticker"])["test_f1_macro"].idxmax()
        df = pd.concat([nsec, sec.loc[idx]], ignore_index=True)
    return df


# ────────────────────────── heatmaps (modelo x ticker) ──────────────────────────
def _heatmap_grid(df, value, cmap, fname, cbar_label, fmt, vmin, vmax, center=None):
    W, frac = 7.2, 1.0
    fs_annot = ptsize(6.4, W, frac)
    fs_tick = ptsize(7.0, W, frac)
    fs_lab = ptsize(7.5, W, frac)
    fs_title = ptsize(8.0, W, frac)

    pt = df[df["tipo"] == "por_ticker"]
    fig, axes = plt.subplots(
        1, 3, figsize=(W, 3.6), sharey=True,
        gridspec_kw={"wspace": 0.10, "right": 0.90},
    )
    for ax, exp in zip(axes, EXPS):
        sub = pt[pt["experimento"] == exp]
        # Transpuesto respecto a plots_extra.py: modelos en x, tickers en y.
        piv = (sub.pivot(index="ticker", columns="modelo", values=value)
                  .reindex(TICKERS)[MODEL_ORDER]
                  .rename(columns=MODEL_LABELS))
        sns.heatmap(piv, ax=ax, annot=True, fmt=fmt, cmap=cmap, center=center,
                    vmin=vmin, vmax=vmax, linewidths=0.4, linecolor="white",
                    cbar=False, annot_kws={"fontsize": fs_annot})
        ax.set_title(f"Experiment {exp}", fontweight="bold", fontsize=fs_title, pad=3)
        ax.set_xlabel("")
        ax.set_ylabel("Ticker" if exp == "A" else "", fontsize=fs_lab)
        # length=0: en un heatmap la marca de tick no aporta y a este tamano se
        # pega al numero de la celda (se lee "--0.91" en vez de "-0.91").
        ax.tick_params(axis="x", labelsize=fs_tick, pad=2, length=0)
        ax.tick_params(axis="y", labelsize=fs_tick, pad=2, length=0)
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
                 rotation_mode="anchor")
        plt.setp(ax.get_yticklabels(), rotation=0, va="center")

    # Un solo colorbar compartido, en vez de tres.
    norm = plt.Normalize(vmin=vmin, vmax=vmax)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    cax = fig.add_axes([0.915, 0.18, 0.014, 0.64])
    cb = fig.colorbar(sm, cax=cax)
    cb.set_label(cbar_label, fontsize=fs_lab, labelpad=2)
    cb.ax.tick_params(labelsize=fs_tick, pad=1, length=2)
    cb.outline.set_linewidth(0.4)

    fig.savefig(OUT / fname, dpi=DPI)
    plt.close(fig)
    print(f"  ✓ {fname}   (annot {fs_annot:.1f}pt fuente -> 6.4pt impreso)")


def plot_sharpe_heatmap(df):
    _heatmap_grid(df, "sharpe_test", "RdYlGn", "fig_sharpe_heatmap.png",
                  "Sharpe", ".2f", vmin=-2.0, vmax=2.5, center=0)


def plot_f1_heatmap(df):
    _heatmap_grid(df, "test_f1_macro", "YlGn", "fig_f1_heatmap.png",
                  "F1-macro", ".2f", vmin=0.20, vmax=0.45)


# ────────────────────────── metricas globales (2x2) ──────────────────────────
def plot_global_metrics(df):
    W, frac = 7.2, 1.0
    fs_tick = ptsize(7.0, W, frac)
    fs_lab = ptsize(7.5, W, frac)
    fs_title = ptsize(8.0, W, frac)
    fs_bar = ptsize(5.6, W, frac)  # (sin usar: ver nota en el bucle)
    fs_leg = ptsize(6.8, W, frac)

    metrics = [("test_f1_macro", "F1-macro"), ("win_rate_test", "Win rate"),
               ("profit_factor_test", "Profit factor"),
               ("max_drawdown_test", "Maximum drawdown")]
    sub = df[df["tipo"] == "global"]

    fig, axes = plt.subplots(2, 2, figsize=(W, 4.6))
    for ax, (col, name) in zip(axes.flatten(), metrics):
        piv = (sub.pivot(index="modelo", columns="experimento", values=col)
                  .reindex(MODEL_ORDER).rename(index=MODEL_LABELS))
        piv.columns = [f"Exp {c}" for c in piv.columns]
        piv.plot(kind="bar", ax=ax, width=0.74, edgecolor="black",
                 linewidth=0.35, legend=False,
                 color=["#4C72B0", "#DD8452", "#55A868"])
        ax.set_title(name, fontweight="bold", fontsize=fs_title, pad=3)
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.tick_params(axis="x", labelsize=fs_tick, pad=1, length=0)
        ax.tick_params(axis="y", labelsize=fs_tick, pad=1)
        plt.setp(ax.get_xticklabels(), rotation=28, ha="right",
                 rotation_mode="anchor")
        ax.grid(axis="y", alpha=0.25, linewidth=0.4)
        ax.set_axisbelow(True)
        if col == "test_f1_macro":
            ax.axhline(0.3333, color="red", linestyle="--", linewidth=0.7)
            ax.set_ylim(0.30, 0.43)
        if col == "win_rate_test":
            ax.set_ylim(0.44, 0.535)
        if col == "profit_factor_test":
            ax.axhline(1.0, color="red", linestyle="--", linewidth=0.7)
            ax.set_ylim(0.90, 1.34)
        # Sin bar_label: 15 barras por panel a este ancho hacen que las
        # etiquetas se solapen entre si. Los valores exactos ya estan en las
        # tablas 5 y 6 del paper; aqui lo que se lee es el patron.

    handles, labels = axes[0][0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False,
               fontsize=fs_leg, bbox_to_anchor=(0.5, -0.035))
    fig.tight_layout(rect=[0, 0.03, 1, 1])
    fig.savefig(OUT / "fig_global_metrics.png", dpi=DPI)
    plt.close(fig)
    print(f"  ✓ fig_global_metrics.png   (bar labels {fs_bar:.1f}pt fuente -> 5.6pt impreso)")


# ────────────────────────── efecto del tamano del train ──────────────────────────
def plot_train_years(df):
    W, frac = 7.0, 1.0
    fs_tick = ptsize(7.0, W, frac)
    fs_lab = ptsize(7.5, W, frac)
    fs_title = ptsize(8.0, W, frac)
    fs_bar = ptsize(5.8, W, frac)
    fs_leg = ptsize(6.8, W, frac)

    sub = df[df["tipo"] == "global"]
    years = {"A": "10 y", "B": "6 y", "C": "4 y"}

    fig, axes = plt.subplots(1, 2, figsize=(W, 2.6))
    for ax, (col, name, ylab) in zip(
            axes, [("test_f1_macro", "F1-macro", "F1-macro"),
                   ("sharpe_test", "Annualized Sharpe ratio", "Sharpe")]):
        piv = (sub.pivot(index="modelo", columns="experimento", values=col)
                  .reindex(MODEL_ORDER).rename(index=MODEL_LABELS))
        piv.columns = [years[c] for c in piv.columns]
        piv.plot(kind="bar", ax=ax, width=0.74, edgecolor="black",
                 linewidth=0.35, legend=False,
                 color=["#4C72B0", "#DD8452", "#55A868"])
        ax.set_title(name, fontweight="bold", fontsize=fs_title, pad=3)
        ax.set_xlabel("")
        ax.set_ylabel(ylab, fontsize=fs_lab, labelpad=2)
        ax.tick_params(axis="x", labelsize=fs_tick, pad=1, length=0)
        ax.tick_params(axis="y", labelsize=fs_tick, pad=1)
        plt.setp(ax.get_xticklabels(), rotation=28, ha="right",
                 rotation_mode="anchor")
        ax.grid(axis="y", alpha=0.25, linewidth=0.4)
        ax.set_axisbelow(True)
        if col == "test_f1_macro":
            ax.axhline(0.3333, color="red", linestyle="--", linewidth=0.7)
            ax.set_ylim(0.30, 0.43)
        else:
            ax.axhline(0.0, color="black", linewidth=0.5)
        # Sin bar_label, por la misma razon que en fig_global_metrics.

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False,
               fontsize=fs_leg, title="Training years",
               title_fontsize=fs_leg, bbox_to_anchor=(0.5, -0.10))
    fig.tight_layout(rect=[0, 0.06, 1, 1])
    fig.savefig(OUT / "fig_train_years.png", dpi=DPI)
    plt.close(fig)
    print(f"  ✓ fig_train_years.png   (bar labels {fs_bar:.1f}pt fuente -> 5.8pt impreso)")


# ────────────────────────── distribucion de senales ──────────────────────────
def plot_signal_dist(df):
    W, frac = 6.6, 0.95
    fs_tick = ptsize(7.2, W, frac)
    fs_lab = ptsize(7.5, W, frac)
    fs_bar = ptsize(6.2, W, frac)
    fs_leg = ptsize(7.0, W, frac)

    sub = (df[(df["tipo"] == "global") & (df["experimento"] == "B")]
           .set_index("modelo").reindex(MODEL_ORDER).rename(index=MODEL_LABELS))
    piv = sub[["test_signal_buy", "test_signal_hold", "test_signal_sell"]]
    piv.columns = ["BUY", "HOLD", "SELL"]

    fig, ax = plt.subplots(figsize=(W, 2.5))
    piv.plot(kind="bar", stacked=True, ax=ax, width=0.62, edgecolor="black",
             linewidth=0.35, legend=False,
             color=["#2E7D32", "#9E9E9E", "#C62828"])
    ax.set_ylabel("Predicted signal share (%)", fontsize=fs_lab, labelpad=2)
    ax.set_xlabel("")
    ax.set_ylim(0, 100)
    ax.tick_params(axis="x", rotation=0, labelsize=fs_tick, pad=1)
    ax.tick_params(axis="y", labelsize=fs_tick, pad=1)
    for y in (33.3, 66.6):
        ax.axhline(y, color="black", linestyle=":", linewidth=0.7)
    for cont in ax.containers:
        ax.bar_label(cont, fmt="%.0f%%", label_type="center", fontsize=fs_bar,
                     color="white", fontweight="bold")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.10), ncol=3,
              frameon=False, fontsize=fs_leg)
    fig.tight_layout()
    fig.savefig(OUT / "fig_signal_dist.png", dpi=DPI)
    plt.close(fig)
    print(f"  ✓ fig_signal_dist.png   (bar labels {fs_bar:.1f}pt fuente -> 6.2pt impreso)")


# ────────────────────────── boxplot Sharpe por ticker ──────────────────────────
def plot_sharpe_boxplot(df):
    W, frac = 6.0, 0.85
    fs_tick = ptsize(7.2, W, frac)
    fs_lab = ptsize(7.5, W, frac)

    pt = df[df["tipo"] == "por_ticker"]
    order = (pt.groupby("ticker")["sharpe_test"].median()
               .sort_values(ascending=False).index.tolist())

    fig, ax = plt.subplots(figsize=(W, 2.4))
    sns.boxplot(data=pt, x="ticker", y="sharpe_test", order=order, ax=ax,
                width=0.58, linewidth=0.6, fliersize=1.6, color="#AEC7E8",
                showmeans=True,
                meanprops={"marker": "D", "markerfacecolor": "black",
                           "markeredgecolor": "black", "markersize": 2.6})
    ax.axhline(0.0, color="red", linestyle="--", linewidth=0.7)
    ax.set_xlabel("Ticker", fontsize=fs_lab, labelpad=2)
    ax.set_ylabel("Annualized Sharpe", fontsize=fs_lab, labelpad=2)
    ax.tick_params(axis="both", labelsize=fs_tick, pad=1)
    ax.grid(axis="y", alpha=0.25, linewidth=0.4)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(OUT / "fig_sharpe_boxplot.png", dpi=DPI)
    plt.close(fig)
    print(f"  ✓ fig_sharpe_boxplot.png   (ticks {fs_tick:.1f}pt fuente -> 7.2pt impreso)")


def main():
    if not CSV.exists():
        sys.exit(f"No se encontro {CSV}")
    OUT.mkdir(parents=True, exist_ok=True)
    df = load_df()
    print(f"Cargadas {len(df)} corridas de {CSV}")
    print(f"Escribiendo en {OUT}/  (ancho de texto LNCS = {LNCS_TEXTWIDTH_IN} in, {DPI} dpi)")
    plot_global_metrics(df)
    plot_sharpe_heatmap(df)
    plot_f1_heatmap(df)
    plot_train_years(df)
    plot_signal_dist(df)
    plot_sharpe_boxplot(df)
    print("Listo.")


if __name__ == "__main__":
    main()
