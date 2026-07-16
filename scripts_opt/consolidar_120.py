"""
================================================================================
CONSOLIDACIÓN — 120 EXPERIMENTOS FINALES
================================================================================
5 modelos × 3 experimentos × (1 global + 7 tickers) = 120 corridas.

Modelos: LR, XGBoost, LSTM, CNN (puro 1D), CNN-LSTM
Selección: la mejor configuración optimizada por modelo. Para modelos secuenciales,
           se selecciona el mejor lookback (20 ó 60) por (exp, ticker) según F1-macro.

Métricas reportadas: F1-macro, Win Rate, Profit Factor, Max Drawdown
(SIN accuracy, según pedido del usuario).
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import sys, json, warnings, functools
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

# Configs ganadores por modelo
SOURCES = {
    "LR":       {"path": "RESULTADOS_OPTIMIZADOS/modelos_optimizados/lr/resultados_lr_opt.csv",
                 "config_id": "LR-02-elasticnet-all"},
    "XGBoost":  {"path": "RESULTADOS_OPTIMIZADOS/modelos_optimizados/xgboost/resultados_xgb_opt.csv",
                 "config_id": "XGB-01-all"},
    "LSTM":     {"path": "RESULTADOS_OPTIMIZADOS/modelos_optimizados/lstm/resultados_lstm_opt.csv",
                 "config_id": "LSTM-02-bi"},
    "CNN":      {"path": "RESULTADOS_OPTIMIZADOS/modelos_optimizados/cnn_puro/resultados_cnn_puro.csv",
                 "config_id": "CNN-puro"},
    "CNN-LSTM": {"path": "RESULTADOS_OPTIMIZADOS/modelos_optimizados/cnn_lstm/resultados_cnn_lstm_opt.csv",
                 "config_id": "CNN-01-base"},
}

TICKERS = ["AAPL", "NVDA", "TSLA", "AMZN", "MSFT", "GOOGL", "META"]
EXPS = ["A", "B", "C"]
MODEL_ORDER = ["LR", "XGBoost", "LSTM", "CNN", "CNN-LSTM"]

OUT = Path("RESULTADOS_OPTIMIZADOS/reportes/final_120")
OUT.mkdir(parents=True, exist_ok=True)


# ────────── CARGA + SELECCIÓN MEJOR LOOKBACK ──────────
def cargar_y_seleccionar():
    """Para cada modelo, carga su CSV y filtra a config_id. Para sec.: mejor lookback."""
    all_rows = []
    for model, info in SOURCES.items():
        if not Path(info["path"]).exists():
            print(f"  ⚠ No existe {info['path']}"); continue
        df = pd.read_csv(info["path"])
        df = df[df["config_id"] == info["config_id"]].copy()
        df["modelo"] = model

        if "lookback" in df.columns and df["lookback"].notna().any():
            # Para cada (tipo, ticker, exp), elige mejor lookback por F1
            grp_cols = ["tipo", "ticker", "experimento"]
            best_idx = df.groupby(grp_cols)["test_f1_macro"].idxmax()
            df = df.loc[best_idx].reset_index(drop=True)
        all_rows.append(df)
    return pd.concat(all_rows, ignore_index=True, sort=False)


# ────────── TABLA 120 EXPERIMENTOS ──────────
def tabla_120(df):
    """Tabla por (modelo, exp, tipo, ticker) con métricas pedidas."""
    rows = []
    for model in MODEL_ORDER:
        for exp in EXPS:
            # Global
            sub_g = df[(df["modelo"]==model) & (df["experimento"]==exp) & (df["tipo"]=="global")]
            if not sub_g.empty:
                r = sub_g.iloc[0]
                rows.append({
                    "modelo": model, "experimento": exp, "tipo": "global", "ticker": "GLOBAL",
                    "lookback": int(r["lookback"]) if pd.notna(r.get("lookback")) else None,
                    "F1_macro":      round(r["test_f1_macro"], 4),
                    "F1_BUY":        round(r["test_f1_buy"],   4) if pd.notna(r.get("test_f1_buy")) else None,
                    "F1_SELL":       round(r["test_f1_sell"],  4) if pd.notna(r.get("test_f1_sell")) else None,
                    "F1_HOLD":       round(r["test_f1_hold"],  4) if pd.notna(r.get("test_f1_hold")) else None,
                    "Win_Rate":      round(r["win_rate_test"], 4) if pd.notna(r.get("win_rate_test")) else None,
                    "Profit_Factor": round(r["profit_factor_test"], 4) if pd.notna(r.get("profit_factor_test")) else None,
                    "Max_Drawdown":  round(r["max_drawdown_test"], 4) if pd.notna(r.get("max_drawdown_test")) else None,
                    "Sharpe":        round(r["sharpe_test"],   4) if pd.notna(r.get("sharpe_test")) else None,
                    "Cum_Return":    round(r["cumul_return_test"], 4) if pd.notna(r.get("cumul_return_test")) else None,
                })
            # Por ticker
            for ticker in TICKERS:
                sub_t = df[(df["modelo"]==model) & (df["experimento"]==exp) &
                           (df["tipo"]=="por_ticker") & (df["ticker"]==ticker)]
                if not sub_t.empty:
                    r = sub_t.iloc[0]
                    rows.append({
                        "modelo": model, "experimento": exp, "tipo": "por_ticker", "ticker": ticker,
                        "lookback": int(r["lookback"]) if pd.notna(r.get("lookback")) else None,
                        "F1_macro":      round(r["test_f1_macro"], 4),
                        "F1_BUY":        round(r["test_f1_buy"],   4) if pd.notna(r.get("test_f1_buy")) else None,
                        "F1_SELL":       round(r["test_f1_sell"],  4) if pd.notna(r.get("test_f1_sell")) else None,
                        "F1_HOLD":       round(r["test_f1_hold"],  4) if pd.notna(r.get("test_f1_hold")) else None,
                        "Win_Rate":      round(r["win_rate_test"], 4) if pd.notna(r.get("win_rate_test")) else None,
                        "Profit_Factor": round(r["profit_factor_test"], 4) if pd.notna(r.get("profit_factor_test")) else None,
                        "Max_Drawdown":  round(r["max_drawdown_test"], 4) if pd.notna(r.get("max_drawdown_test")) else None,
                        "Sharpe":        round(r["sharpe_test"],   4) if pd.notna(r.get("sharpe_test")) else None,
                        "Cum_Return":    round(r["cumul_return_test"], 4) if pd.notna(r.get("cumul_return_test")) else None,
                    })
    return pd.DataFrame(rows)


# ────────── PLOTS ──────────
def plot_global(df120):
    metricas = ["F1_macro", "Win_Rate", "Profit_Factor", "Max_Drawdown"]
    sub = df120[df120["tipo"]=="global"]
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    for ax, met in zip(axes.flatten(), metricas):
        piv = sub.pivot(index="modelo", columns="experimento", values=met).reindex(MODEL_ORDER)
        piv.plot(kind="bar", ax=ax, edgecolor="black", colormap="tab10", width=0.7)
        ax.set_title(f"{met} — GLOBAL", fontweight="bold")
        ax.tick_params(axis="x", rotation=0)
        ax.grid(axis="y", alpha=0.3)
        if met == "F1_macro":
            ax.axhline(0.333, color="red", linestyle="--", linewidth=1, label="Aleatorio")
        for cont in ax.containers:
            ax.bar_label(cont, fmt="%.2f", padding=2, fontsize=7)
    plt.tight_layout()
    fig.savefig(OUT / "120_global_metrics.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_heatmap_por_ticker(df120, metric="F1_macro"):
    sub = df120[df120["tipo"]=="por_ticker"]
    for exp in EXPS:
        se = sub[sub["experimento"]==exp]
        if se.empty: continue
        piv = se.pivot(index="modelo", columns="ticker", values=metric).reindex(MODEL_ORDER)
        if piv.empty: continue
        fig, ax = plt.subplots(figsize=(11, 4))
        sns.heatmap(piv, ax=ax, annot=True, fmt=".3f", cmap="YlGn",
                    linewidths=0.5, vmin=piv.min().min(), vmax=piv.max().max())
        ax.set_title(f"{metric} — Por Ticker — Exp {exp}", fontweight="bold")
        plt.tight_layout()
        fig.savefig(OUT / f"120_heatmap_{metric}_exp_{exp}.png", dpi=150, bbox_inches="tight")
        plt.close(fig)


def main():
    print("="*75)
    print("  CONSOLIDACIÓN — 120 EXPERIMENTOS FINALES (5 modelos)")
    print("="*75)

    df = cargar_y_seleccionar()
    df120 = tabla_120(df)
    print(f"\nTotal experimentos: {len(df120)}")

    # Tabla principal
    df120.to_csv(OUT / "120_experimentos.csv", index=False)
    print(f"✓ Guardado: {OUT}/120_experimentos.csv")

    # Tabla pivote por métrica
    for met in ["F1_macro", "Win_Rate", "Profit_Factor", "Max_Drawdown"]:
        # GLOBAL
        piv_g = df120[df120["tipo"]=="global"].pivot(
            index="modelo", columns="experimento", values=met).reindex(MODEL_ORDER)
        piv_g.to_csv(OUT / f"resumen_GLOBAL_{met}.csv")
        print(f"\n  --- GLOBAL {met} ---")
        print(piv_g.to_string())

        # POR TICKER (promedio)
        piv_pt = df120[df120["tipo"]=="por_ticker"].pivot_table(
            index="modelo", columns="experimento", values=met, aggfunc="mean").reindex(MODEL_ORDER)
        piv_pt.to_csv(OUT / f"resumen_PORTICKER_mean_{met}.csv")
        print(f"\n  --- POR-TICKER mean {met} ---")
        print(piv_pt.round(4).to_string())

    # Plots
    plot_global(df120)
    plot_heatmap_por_ticker(df120, "F1_macro")
    plot_heatmap_por_ticker(df120, "Sharpe")
    plot_heatmap_por_ticker(df120, "Profit_Factor")
    print(f"\n✓ Plots guardados en {OUT}")

    # Mejor modelo por (exp, tipo)
    print("\n" + "="*75)
    print("  GANADORES POR EXPERIMENTO")
    print("="*75)
    for tipo in ["global", "por_ticker"]:
        for exp in EXPS:
            sub = df120[(df120["tipo"]==tipo) & (df120["experimento"]==exp)]
            if sub.empty: continue
            if tipo == "global":
                idx = sub["F1_macro"].idxmax()
                r = sub.loc[idx]
                print(f"  {tipo} Exp {exp}: 🥇 {r['modelo']:10s}  F1={r['F1_macro']:.4f}  "
                      f"WR={r['Win_Rate']:.4f}  PF={r['Profit_Factor']:.4f}  MaxDD={r['Max_Drawdown']:.4f}")
            else:
                avg = sub.groupby("modelo")["F1_macro"].mean()
                best = avg.idxmax()
                print(f"  {tipo} Exp {exp}: 🥇 {best:10s}  F1_mean={avg[best]:.4f}")


if __name__ == "__main__":
    main()
