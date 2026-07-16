"""
Consolidación final con v4 (splits unificados, test=2025).
Genera tablas y plots para el paper.
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

CSV = "RESULTADOS_OPTIMIZADOS/v4/resultados_v4.csv"
OUT = Path("RESULTADOS_OPTIMIZADOS/reportes/v4_final")
OUT.mkdir(parents=True, exist_ok=True)

TICKERS = ["AAPL","NVDA","TSLA","AMZN","MSFT","GOOGL","META"]
EXPS = ["A","B","C"]
MODEL_ORDER = ["LR","XGBoost","LSTM","CNN","CNN-LSTM"]


def load_best_lookback(df):
    """Selecciona mejor lookback por (modelo, tipo, exp, ticker)."""
    if "lookback" not in df.columns: return df
    grp = ["modelo","tipo","experimento","ticker"]
    idx = df.groupby(grp, dropna=False)["test_f1_macro"].idxmax()
    return df.loc[idx].reset_index(drop=True)


def main():
    if not Path(CSV).exists():
        print(f"⚠ No existe {CSV}"); return
    df = pd.read_csv(CSV)
    df = load_best_lookback(df)

    # Tabla 1: GLOBAL F1-macro
    g = df[df["tipo"]=="global"].pivot(index="modelo", columns="experimento",
                                        values="test_f1_macro").reindex(MODEL_ORDER).round(4)
    print("\n=== Tabla 1: F1-macro test GLOBAL ===")
    print(g.to_string())
    g.to_csv(OUT/"tabla1_F1_GLOBAL.csv")

    # Tabla 2: Exp B GLOBAL métricas económicas
    sub = df[(df["tipo"]=="global") & (df["experimento"]=="B")].set_index("modelo").reindex(MODEL_ORDER)
    tab2 = sub[["test_f1_macro","win_rate_test","profit_factor_test","max_drawdown_test","sharpe_test"]].round(4)
    tab2.columns = ["F1-macro","Win Rate","Profit Factor","Max DD","Sharpe"]
    print("\n=== Tabla 2: Exp B GLOBAL — métricas económicas ===")
    print(tab2.to_string())
    tab2.to_csv(OUT/"tabla2_economicas_ExpB.csv")

    # Tabla 3: POR-TICKER promedio
    pt = df[df["tipo"]=="por_ticker"].pivot_table(index="modelo", columns="experimento",
                                                    values="test_f1_macro", aggfunc="mean").reindex(MODEL_ORDER).round(4)
    print("\n=== Tabla 3: POR-TICKER F1-macro promedio ===")
    print(pt.to_string())
    pt.to_csv(OUT/"tabla3_F1_PORTICKER_mean.csv")

    # Tabla 4: drill-down mejor modelo Exp B por ticker
    best_model = g["B"].idxmax()
    drill = df[(df["modelo"]==best_model) & (df["tipo"]=="por_ticker") & (df["experimento"]=="B")]
    drill = drill.set_index("ticker").reindex(TICKERS)
    tab4 = drill[["test_f1_macro","sharpe_test","cumul_return_test","win_rate_test","max_drawdown_test"]].round(4)
    tab4.columns = ["F1-macro","Sharpe","Cum Return","Win Rate","Max DD"]
    print(f"\n=== Tabla 4: Drill-down {best_model} Exp B por ticker ===")
    print(tab4.to_string())
    tab4.to_csv(OUT/f"tabla4_drilldown_{best_model}_ExpB.csv")

    # Plot 1: GLOBAL barras 4 métricas
    metricas = [("test_f1_macro","F1-macro",0.5),
                ("win_rate_test","Win Rate",0.6),
                ("profit_factor_test","Profit Factor",2.0),
                ("max_drawdown_test","Max Drawdown",0)]
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    for ax, (col, name, top) in zip(axes.flatten(), metricas):
        sub_g = df[df["tipo"]=="global"]
        piv = sub_g.pivot(index="modelo", columns="experimento", values=col).reindex(MODEL_ORDER)
        piv.plot(kind="bar", ax=ax, edgecolor="black", colormap="tab10", width=0.7)
        ax.set_title(f"{name} — GLOBAL (test=2025)", fontweight="bold")
        ax.tick_params(axis="x", rotation=0)
        ax.grid(axis="y", alpha=0.3)
        if "F1" in name: ax.axhline(0.333, color="red", linestyle="--", linewidth=1)
        for cont in ax.containers:
            ax.bar_label(cont, fmt="%.2f", padding=2, fontsize=7)
    plt.tight_layout()
    fig.savefig(OUT/"plot1_global_4_metricas.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # Plot 2: Heatmap F1 por ticker (Exp B)
    sub_pt = df[(df["tipo"]=="por_ticker") & (df["experimento"]=="B")]
    if not sub_pt.empty:
        piv = sub_pt.pivot(index="modelo", columns="ticker", values="test_f1_macro").reindex(MODEL_ORDER)
        fig, ax = plt.subplots(figsize=(11, 4))
        sns.heatmap(piv, ax=ax, annot=True, fmt=".3f", cmap="YlGn", linewidths=0.5,
                    vmin=piv.min().min(), vmax=piv.max().max())
        ax.set_title("F1-macro Test por Ticker — Exp B GLOBAL", fontweight="bold")
        plt.tight_layout()
        fig.savefig(OUT/"plot2_heatmap_F1_por_ticker_ExpB.png", dpi=150, bbox_inches="tight")
        plt.close(fig)

    print(f"\n✓ Tablas y plots guardados en {OUT}")


if __name__ == "__main__":
    main()
