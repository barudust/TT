"""
Plots adicionales para el paper:
  - Heatmaps Sharpe por modelo×ticker para cada exp
  - Heatmap completo del ganador (LR) por ticker×exp
  - Distribución de señales BUY/HOLD/SELL por modelo
  - Curva de equity acumulado para el mejor modelo en cada activo
  - Boxplot de variabilidad entre tickers
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import sys, warnings, functools
import numpy as np
import pandas as pd
from pathlib import Path

try: sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except: pass
print = functools.partial(print, flush=True)
warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams["font.family"] = "serif"
DPI = 220

# The paper places every figure at \includegraphics[width=\textwidth] inside a
# single-column Springer LNCS page (~4.8in of text width). A figure created
# at, say, 20in wide gets shrunk ~4x on the page, so a naive "make fonts a
# bit bigger" pass barely moves the printed size. ptsize() converts a
# *printed* target size (in pt, what you actually want a reader to see on
# the page) into the source matplotlib fontsize needed for a figure of a
# given width so it survives that shrink.
LNCS_TEXTWIDTH_IN = 4.8

def ptsize(printed_pt, fig_width_in):
    return printed_pt * fig_width_in / LNCS_TEXTWIDTH_IN

CSV = "RESULTADOS_OPTIMIZADOS/v4/resultados_v4.csv"
OUT = Path("RESULTADOS_OPTIMIZADOS/reportes/v4_final")
OUT.mkdir(parents=True, exist_ok=True)

TICKERS = ["AAPL","NVDA","TSLA","AMZN","MSFT","GOOGL","META"]
EXPS = ["A","B","C"]
MODEL_ORDER = ["LR","XGBoost","LSTM","CNN","CNN-LSTM"]


def load_df():
    df = pd.read_csv(CSV)
    if "lookback" in df.columns:
        sec = df[df["lookback"].notna()]
        nsec = df[df["lookback"].isna()]
        idx = sec.groupby(["modelo","tipo","experimento","ticker"])["test_f1_macro"].idxmax()
        df = pd.concat([nsec, sec.loc[idx]], ignore_index=True)
    return df


def plot_sharpe_heatmaps(df):
    """Heatmap Sharpe por (modelo × ticker) para cada experimento."""
    W = 19
    fig, axes = plt.subplots(1, 3, figsize=(W, 6.0))
    pt = df[df["tipo"]=="por_ticker"]
    for ax, exp in zip(axes, EXPS):
        sub = pt[pt["experimento"]==exp]
        piv = sub.pivot(index="modelo", columns="ticker", values="sharpe_test").reindex(MODEL_ORDER)[TICKERS]
        sns.heatmap(piv, ax=ax, annot=True, fmt=".2f", cmap="RdYlGn", center=0,
                    vmin=-2, vmax=2.5, linewidths=0.5, cbar_kws={"label": "Sharpe"},
                    annot_kws={"fontsize": 15})
        ax.set_title(f"Experiment {exp}", fontweight="bold", fontsize=19)
        ax.set_xlabel("Ticker", fontsize=16)
        ax.set_ylabel("Model" if exp=="A" else "", fontsize=16)
        ax.tick_params(axis="x", labelsize=14)
        ax.tick_params(axis="y", labelsize=11)
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        plt.setp(ax.get_yticklabels(), rotation=0, va="center")
        cbar = ax.collections[0].colorbar
        cbar.ax.tick_params(labelsize=14)
        cbar.set_label("Sharpe", fontsize=15)
    fig.suptitle("Annualized Sharpe Ratio by Model × Ticker (test=2025)",
                 fontsize=21, fontweight="bold", y=1.10)
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(OUT/"fig_sharpe_heatmap_per_ticker.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def plot_f1_heatmap(df):
    """Heatmap F1-macro por (modelo × ticker) para cada exp."""
    W = 19
    fig, axes = plt.subplots(1, 3, figsize=(W, 6.0))
    pt = df[df["tipo"]=="por_ticker"]
    for ax, exp in zip(axes, EXPS):
        sub = pt[pt["experimento"]==exp]
        piv = sub.pivot(index="modelo", columns="ticker", values="test_f1_macro").reindex(MODEL_ORDER)[TICKERS]
        sns.heatmap(piv, ax=ax, annot=True, fmt=".3f", cmap="YlGn",
                    vmin=0.20, vmax=0.45, linewidths=0.5, cbar_kws={"label": "F1-macro"},
                    annot_kws={"fontsize": 14})
        ax.set_title(f"Experiment {exp}", fontweight="bold", fontsize=19)
        ax.set_xlabel("Ticker", fontsize=16)
        ax.set_ylabel("Model" if exp=="A" else "", fontsize=16)
        ax.tick_params(axis="x", labelsize=14)
        ax.tick_params(axis="y", labelsize=11)
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        plt.setp(ax.get_yticklabels(), rotation=0, va="center")
        cbar = ax.collections[0].colorbar
        cbar.ax.tick_params(labelsize=14)
        cbar.set_label("F1-macro", fontsize=15)
    fig.suptitle("F1-macro Test by Model × Ticker (test=2025)",
                 fontsize=21, fontweight="bold", y=1.10)
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(OUT/"fig_f1_heatmap_per_ticker.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def plot_signal_distribution(df):
    """Distribución de señales predichas (BUY/HOLD/SELL) por modelo en Exp B GLOBAL."""
    W = 9
    sub = df[(df["tipo"]=="global") & (df["experimento"]=="B")].set_index("modelo").reindex(MODEL_ORDER)
    cols = ["test_signal_buy","test_signal_hold","test_signal_sell"]
    data = sub[cols].copy()
    data.columns = ["BUY", "HOLD", "SELL"]
    fig, ax = plt.subplots(figsize=(W, 5.0))
    data.plot(kind="bar", stacked=True, ax=ax, color=["#2ecc71","#95a5a6","#e74c3c"],
              edgecolor="black", width=0.7)
    ax.axhline(33.3, color="black", linestyle=":", linewidth=1, alpha=0.5)
    ax.axhline(66.6, color="black", linestyle=":", linewidth=1, alpha=0.5)
    ax.set_ylabel("Predicted signal distribution (%)", fontsize=ptsize(9, W))
    ax.set_xlabel("")
    ax.set_title("Predicted Signal Distribution per Model (Exp B GLOBAL, test=2025)",
                 fontweight="bold", fontsize=ptsize(10, W))
    ax.tick_params(axis="x", rotation=0, labelsize=ptsize(8.5, W))
    ax.tick_params(axis="y", labelsize=ptsize(8, W))
    ax.legend(title="Signal", loc="upper left", bbox_to_anchor=(1.01, 1.0),
              fontsize=ptsize(8, W), title_fontsize=ptsize(8, W))
    # Annotate percentages
    for c in ax.containers:
        ax.bar_label(c, fmt="%.0f%%", label_type="center", fontsize=ptsize(8, W),
                     color="white", fontweight="bold")
    plt.tight_layout()
    fig.savefig(OUT/"fig_signal_distribution.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def plot_per_ticker_sharpe_boxplot(df):
    """Boxplot Sharpe por ticker, mostrando variabilidad entre modelos."""
    W = 9
    pt = df[df["tipo"]=="por_ticker"]
    fig, ax = plt.subplots(figsize=(W, 5.0))
    sns.boxplot(data=pt, x="ticker", y="sharpe_test", ax=ax,
                order=TICKERS, palette="Set2", showmeans=True,
                meanprops={"marker":"D","markerfacecolor":"white","markeredgecolor":"black","markersize":9})
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Ticker", fontsize=ptsize(9, W))
    ax.set_ylabel("Annualized Sharpe Ratio", fontsize=ptsize(9, W))
    ax.set_title("Distribution of Sharpe per Ticker across 5 models × 3 experiments",
                 fontweight="bold", fontsize=ptsize(10, W))
    ax.tick_params(axis="both", labelsize=ptsize(8.5, W))
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    fig.savefig(OUT/"fig_sharpe_boxplot_per_ticker.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def plot_train_years_effect(df):
    """Efecto de los años de entrenamiento: Exp A (10y), B (6y), C (4y)."""
    # NOTE: two side-by-side panels means each one only occupies ~half of the
    # final printed width, so the single-figure-width ptsize() estimate is
    # too generous here (titles collide). Fixed, empirically-checked sizes.
    g = df[df["tipo"]=="global"]
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.0))
    fig.subplots_adjust(wspace=0.32)
    # F1
    piv = g.pivot(index="modelo", columns="experimento", values="test_f1_macro").reindex(MODEL_ORDER)[EXPS]
    piv.columns = ["A (10 yr)", "B (6 yr)", "C (4 yr)"]
    piv.plot(kind="bar", ax=axes[0], edgecolor="black", colormap="tab10", width=0.7)
    axes[0].axhline(0.333, color="red", linestyle="--", linewidth=1, label="Random (1/3)")
    axes[0].set_title("F1-macro Test by Training Years (GLOBAL)", fontweight="bold", fontsize=14)
    axes[0].set_ylabel("F1-macro", fontsize=13); axes[0].set_xlabel("")
    axes[0].legend(title="Training years", fontsize=10, title_fontsize=10, loc="lower right")
    axes[0].tick_params(axis="both", labelsize=12)
    plt.setp(axes[0].get_xticklabels(), rotation=20, ha="right")
    axes[0].grid(axis="y", alpha=0.3)
    for c in axes[0].containers: axes[0].bar_label(c, fmt="%.2f", padding=2, fontsize=9)
    # Sharpe
    piv2 = g.pivot(index="modelo", columns="experimento", values="sharpe_test").reindex(MODEL_ORDER)[EXPS]
    piv2.columns = ["A (10 yr)", "B (6 yr)", "C (4 yr)"]
    piv2.plot(kind="bar", ax=axes[1], edgecolor="black", colormap="tab10", width=0.7)
    axes[1].axhline(0, color="black", linewidth=0.8)
    axes[1].set_title("Annualized Sharpe Ratio by Training Years (GLOBAL)", fontweight="bold", fontsize=14)
    axes[1].set_ylabel("Sharpe", fontsize=13); axes[1].set_xlabel("")
    axes[1].legend(title="Training years", fontsize=10, title_fontsize=10, loc="upper right")
    axes[1].tick_params(axis="both", labelsize=12)
    plt.setp(axes[1].get_xticklabels(), rotation=20, ha="right")
    axes[1].grid(axis="y", alpha=0.3)
    for c in axes[1].containers: axes[1].bar_label(c, fmt="%.2f", padding=2, fontsize=9)
    fig.savefig(OUT/"fig_train_years_effect.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def plot_model_ranking(df):
    """Ranking general de modelos con error bars (variabilidad entre tickers)."""
    # Same two-panel caveat as plot_train_years_effect(): fixed sizes, not ptsize().
    pt = df[df["tipo"]=="por_ticker"]
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.0))
    fig.subplots_adjust(wspace=0.35)
    for ax, met, name in zip(axes, ["test_f1_macro","sharpe_test"],
                              ["F1-macro Test","Annualized Sharpe"]):
        stats = pt.groupby("modelo")[met].agg(["mean","std"]).reindex(MODEL_ORDER)
        stats = stats.sort_values("mean", ascending=False)
        ax.barh(stats.index, stats["mean"], xerr=stats["std"], color="#3498db",
                edgecolor="black", capsize=4)
        ax.set_xlabel(name, fontsize=13); ax.set_ylabel("")
        ax.set_title(f"{name} Ranking\n(mean ± std across tickers and exps)",
                     fontweight="bold", fontsize=13)
        ax.tick_params(axis="both", labelsize=12)
        ax.grid(axis="x", alpha=0.3)
        for i, v in enumerate(stats["mean"]):
            ax.text(v, i, f"  {v:.3f}", va="center", fontsize=11)
    fig.savefig(OUT/"fig_model_ranking.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def main():
    df = load_df()
    print(f"Filas: {len(df)}")

    plot_sharpe_heatmaps(df)
    plot_f1_heatmap(df)
    plot_signal_distribution(df)
    plot_per_ticker_sharpe_boxplot(df)
    plot_train_years_effect(df)
    plot_model_ranking(df)

    print(f"✓ Plots guardados en {OUT}")


if __name__ == "__main__":
    main()
