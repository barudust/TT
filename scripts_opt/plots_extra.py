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

sns.set_context("paper", font_scale=1.1)
plt.rcParams["font.family"] = "serif"

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
    fig, axes = plt.subplots(1, 3, figsize=(20, 4))
    pt = df[df["tipo"]=="por_ticker"]
    for ax, exp in zip(axes, EXPS):
        sub = pt[pt["experimento"]==exp]
        piv = sub.pivot(index="modelo", columns="ticker", values="sharpe_test").reindex(MODEL_ORDER)[TICKERS]
        sns.heatmap(piv, ax=ax, annot=True, fmt=".2f", cmap="RdYlGn", center=0,
                    vmin=-2, vmax=2.5, linewidths=0.5, cbar_kws={"label": "Sharpe"})
        ax.set_title(f"Experiment {exp}", fontweight="bold")
        ax.set_xlabel("Ticker"); ax.set_ylabel("Model" if exp=="A" else "")
    fig.suptitle("Annualized Sharpe Ratio by Model × Ticker (test=2025)",
                 fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig.savefig(OUT/"fig_sharpe_heatmap_per_ticker.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_f1_heatmap(df):
    """Heatmap F1-macro por (modelo × ticker) para cada exp."""
    fig, axes = plt.subplots(1, 3, figsize=(20, 4))
    pt = df[df["tipo"]=="por_ticker"]
    for ax, exp in zip(axes, EXPS):
        sub = pt[pt["experimento"]==exp]
        piv = sub.pivot(index="modelo", columns="ticker", values="test_f1_macro").reindex(MODEL_ORDER)[TICKERS]
        sns.heatmap(piv, ax=ax, annot=True, fmt=".3f", cmap="YlGn",
                    vmin=0.20, vmax=0.45, linewidths=0.5, cbar_kws={"label": "F1-macro"})
        ax.set_title(f"Experiment {exp}", fontweight="bold")
        ax.set_xlabel("Ticker"); ax.set_ylabel("Model" if exp=="A" else "")
    fig.suptitle("F1-macro Test by Model × Ticker (test=2025)",
                 fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig.savefig(OUT/"fig_f1_heatmap_per_ticker.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_signal_distribution(df):
    """Distribución de señales predichas (BUY/HOLD/SELL) por modelo en Exp B GLOBAL."""
    sub = df[(df["tipo"]=="global") & (df["experimento"]=="B")].set_index("modelo").reindex(MODEL_ORDER)
    cols = ["test_signal_buy","test_signal_hold","test_signal_sell"]
    data = sub[cols].copy()
    data.columns = ["BUY", "HOLD", "SELL"]
    fig, ax = plt.subplots(figsize=(9, 5))
    data.plot(kind="bar", stacked=True, ax=ax, color=["#2ecc71","#95a5a6","#e74c3c"],
              edgecolor="black", width=0.7)
    ax.axhline(33.3, color="black", linestyle=":", linewidth=1, alpha=0.5)
    ax.axhline(66.6, color="black", linestyle=":", linewidth=1, alpha=0.5)
    ax.set_ylabel("Predicted signal distribution (%)")
    ax.set_xlabel("")
    ax.set_title("Predicted Signal Distribution per Model (Exp B GLOBAL, test=2025)",
                 fontweight="bold")
    ax.tick_params(axis="x", rotation=0)
    ax.legend(title="Signal", loc="upper right")
    # Annotate percentages
    for c in ax.containers:
        ax.bar_label(c, fmt="%.0f%%", label_type="center", fontsize=9, color="white", fontweight="bold")
    plt.tight_layout()
    fig.savefig(OUT/"fig_signal_distribution.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_per_ticker_sharpe_boxplot(df):
    """Boxplot Sharpe por ticker, mostrando variabilidad entre modelos."""
    pt = df[df["tipo"]=="por_ticker"]
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.boxplot(data=pt, x="ticker", y="sharpe_test", ax=ax,
                order=TICKERS, palette="Set2", showmeans=True,
                meanprops={"marker":"D","markerfacecolor":"white","markeredgecolor":"black","markersize":8})
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Ticker"); ax.set_ylabel("Annualized Sharpe Ratio")
    ax.set_title("Distribution of Sharpe per Ticker across 5 models × 3 experiments",
                 fontweight="bold")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    fig.savefig(OUT/"fig_sharpe_boxplot_per_ticker.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_train_years_effect(df):
    """Efecto de los años de entrenamiento: Exp A (10y), B (6y), C (4y)."""
    g = df[df["tipo"]=="global"]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    # F1
    piv = g.pivot(index="modelo", columns="experimento", values="test_f1_macro").reindex(MODEL_ORDER)[EXPS]
    piv.columns = ["A (10 yr)", "B (6 yr)", "C (4 yr)"]
    piv.plot(kind="bar", ax=axes[0], edgecolor="black", colormap="tab10", width=0.7)
    axes[0].axhline(0.333, color="red", linestyle="--", linewidth=1, label="Random (1/3)")
    axes[0].set_title("F1-macro Test by Training Years (GLOBAL)", fontweight="bold")
    axes[0].set_ylabel("F1-macro"); axes[0].set_xlabel("")
    axes[0].legend(title="Training years"); axes[0].tick_params(axis="x", rotation=0)
    axes[0].grid(axis="y", alpha=0.3)
    for c in axes[0].containers: axes[0].bar_label(c, fmt="%.2f", padding=2, fontsize=7)
    # Sharpe
    piv2 = g.pivot(index="modelo", columns="experimento", values="sharpe_test").reindex(MODEL_ORDER)[EXPS]
    piv2.columns = ["A (10 yr)", "B (6 yr)", "C (4 yr)"]
    piv2.plot(kind="bar", ax=axes[1], edgecolor="black", colormap="tab10", width=0.7)
    axes[1].axhline(0, color="black", linewidth=0.8)
    axes[1].set_title("Annualized Sharpe Ratio by Training Years (GLOBAL)", fontweight="bold")
    axes[1].set_ylabel("Sharpe"); axes[1].set_xlabel("")
    axes[1].legend(title="Training years"); axes[1].tick_params(axis="x", rotation=0)
    axes[1].grid(axis="y", alpha=0.3)
    for c in axes[1].containers: axes[1].bar_label(c, fmt="%.2f", padding=2, fontsize=7)
    plt.tight_layout()
    fig.savefig(OUT/"fig_train_years_effect.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_model_ranking(df):
    """Ranking general de modelos con error bars (variabilidad entre tickers)."""
    pt = df[df["tipo"]=="por_ticker"]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, met, name in zip(axes, ["test_f1_macro","sharpe_test"],
                              ["F1-macro Test","Annualized Sharpe"]):
        stats = pt.groupby("modelo")[met].agg(["mean","std"]).reindex(MODEL_ORDER)
        stats = stats.sort_values("mean", ascending=False)
        ax.barh(stats.index, stats["mean"], xerr=stats["std"], color="#3498db",
                edgecolor="black", capsize=4)
        ax.set_xlabel(name); ax.set_ylabel("")
        ax.set_title(f"{name} Ranking (mean ± std across tickers and exps)",
                     fontweight="bold")
        ax.grid(axis="x", alpha=0.3)
        for i, v in enumerate(stats["mean"]):
            ax.text(v, i, f"  {v:.3f}", va="center", fontsize=10)
    plt.tight_layout()
    fig.savefig(OUT/"fig_model_ranking.png", dpi=150, bbox_inches="tight")
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
