"""
Reporte final completo:
- Tabla maestra con baseline + optimizado
- Mejor configuración por (modelo, tipo, exp)
- Plots comparativos
- Datos para tablas/figuras de tesis
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import json
import warnings
import functools
import numpy as np
import pandas as pd
from pathlib import Path

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass
print = functools.partial(print, flush=True)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore")

BASELINE_CSVS = {
    "LogisticRegression": "tesis_ml_stocks/04_models/logistic_regression/resultados_lr.csv",
    "XGBoost":            "tesis_ml_stocks/04_models/xgboost/resultados_xgb.csv",
    "LSTM":               "tesis_ml_stocks/04_models/lstm/resultados_lstm.csv",
    "CNN-LSTM":           "tesis_ml_stocks/04_models/cnn_lstm/resultados_cnn_lstm.csv",
}
OPT_CSVS = {
    "LogisticRegression": "RESULTADOS_OPTIMIZADOS/modelos_optimizados/lr/resultados_lr_opt.csv",
    "XGBoost":            "RESULTADOS_OPTIMIZADOS/modelos_optimizados/xgboost/resultados_xgb_opt.csv",
    "LSTM":               "RESULTADOS_OPTIMIZADOS/modelos_optimizados/lstm/resultados_lstm_opt.csv",
    "CNN-LSTM":           "RESULTADOS_OPTIMIZADOS/modelos_optimizados/cnn_lstm/resultados_cnn_lstm_opt.csv",
}

OUT = Path("RESULTADOS_OPTIMIZADOS/reportes")
FIG = OUT / "figuras"
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

MODEL_ORDER = ["LogisticRegression", "XGBoost", "LSTM", "CNN-LSTM"]
EXPS = ["A", "B", "C"]


def cargar_todo():
    dfs = []
    for modelo, path in BASELINE_CSVS.items():
        if Path(path).exists():
            d = pd.read_csv(path)
            d["modelo"] = modelo
            d["config_id"] = "BASELINE"
            d["fuente"] = "baseline"
            dfs.append(d)
    for modelo, path in OPT_CSVS.items():
        if Path(path).exists():
            d = pd.read_csv(path)
            d["modelo"] = modelo
            d["fuente"] = "optimizado"
            dfs.append(d)
    if not dfs:
        return pd.DataFrame()
    df = pd.concat(dfs, ignore_index=True, sort=False)
    return df


def mejor_por_modelo_tipo_exp(df):
    """Para cada (modelo, tipo, experimento), encuentra la configuración con mejor F1-macro promedio."""
    keys = ["modelo", "tipo", "experimento"]
    has_lb = "lookback" in df.columns
    # Para tipo=global, una sola fila por (modelo, config_id, exp, [lookback])
    # Para tipo=por_ticker, varias filas. Promediamos.
    grupo_cols = ["modelo", "config_id", "tipo", "experimento"]
    if has_lb:
        grupo_cols.append("lookback")
    agg = df.groupby(grupo_cols, dropna=False).agg(
        f1_macro_mean=("test_f1_macro", "mean"),
        f1_macro_std =("test_f1_macro", "std"),
        f1_buy_mean  =("test_f1_buy", "mean"),
        f1_sell_mean =("test_f1_sell", "mean"),
        sharpe_mean  =("sharpe_test", "mean"),
        cum_ret_mean =("cumul_return_test", "mean"),
        n_tickers    =("ticker", "count"),
    ).round(4).reset_index()

    # Best per (modelo, tipo, exp): max f1_macro_mean
    result = []
    for modelo in df["modelo"].unique():
        for tipo in df["tipo"].unique():
            for exp in EXPS:
                sub = agg[(agg["modelo"] == modelo) & (agg["tipo"] == tipo) & (agg["experimento"] == exp)]
                if sub.empty:
                    continue
                best = sub.sort_values("f1_macro_mean", ascending=False).iloc[0]
                result.append({
                    "modelo": modelo, "tipo": tipo, "experimento": exp,
                    "best_config_id": best["config_id"],
                    "best_lookback":  best.get("lookback", "-"),
                    "best_f1_macro":  best["f1_macro_mean"],
                    "best_f1_std":    best["f1_macro_std"],
                    "best_f1_buy":    best["f1_buy_mean"],
                    "best_f1_sell":   best["f1_sell_mean"],
                    "best_sharpe":    best["sharpe_mean"],
                    "best_cum_ret":   best["cum_ret_mean"],
                    "n_tickers":      best["n_tickers"],
                })
    return pd.DataFrame(result)


def plot_f1_comparativa(best_df):
    """Plot bar: F1-macro test por (modelo, exp) — separa global vs por_ticker."""
    for tipo in ["global", "por_ticker"]:
        sub = best_df[best_df["tipo"] == tipo]
        if sub.empty:
            continue
        piv = sub.pivot(index="modelo", columns="experimento", values="best_f1_macro")
        piv = piv.reindex(MODEL_ORDER)
        if piv.empty:
            continue
        fig, ax = plt.subplots(figsize=(11, 6))
        piv.plot(kind="bar", ax=ax, edgecolor="black", colormap="tab10", width=0.7)
        ax.axhline(0.333, color="red", linestyle="--", linewidth=1, label="Aleatorio (1/3)")
        ax.set_title(f"F1-Macro Test — Mejor Config Optimizada ({tipo.upper()})",
                     fontsize=13, fontweight="bold")
        ax.set_ylabel("F1-Macro (test)")
        ax.set_ylim(0, max(0.50, piv.max().max() * 1.15))
        ax.legend(title="Experimento")
        ax.tick_params(axis="x", rotation=0)
        ax.grid(axis="y", alpha=0.3)
        for cont in ax.containers:
            ax.bar_label(cont, fmt="%.3f", padding=2, fontsize=9)
        plt.tight_layout()
        fig.savefig(FIG / f"FINAL_f1_{tipo}.png", dpi=150, bbox_inches="tight")
        plt.close(fig)


def plot_baseline_vs_opt(df):
    """Plot comparando baseline vs optimizado F1-macro por modelo y exp."""
    keys = ["modelo", "fuente", "experimento", "tipo"]
    agg = df.groupby(keys, as_index=False)["test_f1_macro"].max()

    for tipo in ["global", "por_ticker"]:
        sub = agg[agg["tipo"] == tipo]
        if sub.empty:
            continue
        piv = sub.pivot_table(index=["modelo", "fuente"], columns="experimento", values="test_f1_macro")
        if piv.empty:
            continue
        # Reshape para gráfica
        piv_resh = piv.reset_index()
        modelos = MODEL_ORDER
        exps = EXPS
        x = np.arange(len(modelos))
        width = 0.4

        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        for i, exp in enumerate(exps):
            ax = axes[i]
            base_vals = [piv_resh[(piv_resh["modelo"]==m) & (piv_resh["fuente"]=="baseline")][exp].values
                         for m in modelos]
            opt_vals  = [piv_resh[(piv_resh["modelo"]==m) & (piv_resh["fuente"]=="optimizado")][exp].values
                         for m in modelos]
            base_vals = [v[0] if len(v) > 0 and not np.isnan(v[0]) else 0 for v in base_vals]
            opt_vals  = [v[0] if len(v) > 0 and not np.isnan(v[0]) else 0 for v in opt_vals]

            ax.bar(x - width/2, base_vals, width, label="Baseline", color="#888888", edgecolor="black")
            ax.bar(x + width/2, opt_vals,  width, label="Optimizado", color="#2ecc71", edgecolor="black")
            ax.set_xticks(x); ax.set_xticklabels(modelos, rotation=15)
            ax.set_title(f"Exp {exp}", fontweight="bold")
            ax.set_ylabel("F1-macro test" if i==0 else "")
            ax.axhline(0.333, color="red", linestyle="--", linewidth=1)
            ax.set_ylim(0, 0.50)
            ax.grid(axis="y", alpha=0.3)
            ax.legend(loc="upper left", fontsize=9)
            for j, (b, o) in enumerate(zip(base_vals, opt_vals)):
                if b > 0:
                    ax.text(j - width/2, b + 0.005, f"{b:.3f}", ha="center", fontsize=8)
                if o > 0:
                    ax.text(j + width/2, o + 0.005, f"{o:.3f}", ha="center", fontsize=8)

        fig.suptitle(f"Baseline vs Optimizado — F1-Macro Test ({tipo.upper()})",
                     fontsize=14, fontweight="bold")
        plt.tight_layout()
        fig.savefig(FIG / f"FINAL_baseline_vs_opt_{tipo}.png", dpi=150, bbox_inches="tight")
        plt.close(fig)


def plot_sharpe_por_ticker(df):
    """Heatmap: Sharpe por (modelo, ticker) en Exp B (por-ticker)."""
    sub = df[(df["experimento"] == "B") & (df["tipo"] == "por_ticker") & (df["fuente"] == "optimizado")]
    if sub.empty:
        return
    # Mejor config por modelo
    keys = ["modelo", "config_id"]
    if "lookback" in sub.columns:
        keys.append("lookback")
    agg_means = sub.groupby(keys)["test_f1_macro"].mean().reset_index()
    best_configs = agg_means.sort_values("test_f1_macro", ascending=False).drop_duplicates("modelo")
    merge_keys = ["modelo", "config_id"] + (["lookback"] if "lookback" in sub.columns else [])
    sub_best = sub.merge(best_configs[merge_keys], on=merge_keys, how="inner")

    piv = sub_best.pivot_table(index="modelo", columns="ticker", values="sharpe_test").reindex(MODEL_ORDER)
    if piv.empty:
        return
    fig, ax = plt.subplots(figsize=(11, 4))
    sns.heatmap(piv, ax=ax, annot=True, fmt=".2f", cmap="RdYlGn", center=0,
                vmin=-2, vmax=2, linewidths=0.5)
    ax.set_title("Sharpe Test por Ticker — Exp B — Mejor Config Optimizada",
                 fontweight="bold")
    plt.tight_layout()
    fig.savefig(FIG / "FINAL_sharpe_heatmap_B.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def main():
    print("="*70)
    print("  REPORTE FINAL — Optimización vs Baseline")
    print("="*70)

    df = cargar_todo()
    if df.empty:
        print("⚠ Sin datos")
        return
    print(f"Total registros: {len(df)} | Baseline: {len(df[df['fuente']=='baseline'])} | "
          f"Optimizado: {len(df[df['fuente']=='optimizado'])}")

    # Tabla maestra
    df.to_csv(OUT / "MAESTRA_baseline_optimizado.csv", index=False)

    # Mejor por (modelo, tipo, exp) en optimizado
    df_opt = df[df["fuente"] == "optimizado"]
    best_df = mejor_por_modelo_tipo_exp(df_opt)
    best_df.to_csv(OUT / "MEJOR_optimizado_por_modelo_tipo_exp.csv", index=False)
    print(f"\n✓ Mejor configuración OPTIMIZADA por modelo/tipo/exp:")
    print(best_df.to_string(index=False))

    # También mejor baseline para comparar
    df_base = df[df["fuente"] == "baseline"]
    best_base = mejor_por_modelo_tipo_exp(df_base)
    best_base.to_csv(OUT / "MEJOR_baseline_por_modelo_tipo_exp.csv", index=False)

    # Tabla unificada comparativa
    print("\n" + "="*70)
    print("  COMPARATIVA — F1-MACRO TEST (BASELINE vs OPTIMIZADO)")
    print("="*70)
    for tipo in ["global", "por_ticker"]:
        print(f"\n  --- {tipo.upper()} ---")
        rows = []
        for modelo in MODEL_ORDER:
            for exp in EXPS:
                base_row = best_base[(best_base["modelo"]==modelo) & (best_base["tipo"]==tipo) & (best_base["experimento"]==exp)]
                opt_row  = best_df[(best_df["modelo"]==modelo) & (best_df["tipo"]==tipo) & (best_df["experimento"]==exp)]
                if base_row.empty and opt_row.empty:
                    continue
                base_f1 = float(base_row.iloc[0]["best_f1_macro"]) if not base_row.empty else None
                opt_f1  = float(opt_row.iloc[0]["best_f1_macro"])  if not opt_row.empty  else None
                delta   = (opt_f1 - base_f1) if (base_f1 and opt_f1) else None
                rows.append({
                    "modelo": modelo, "exp": exp,
                    "baseline": round(base_f1, 4) if base_f1 else "-",
                    "optimizado": round(opt_f1, 4) if opt_f1 else "-",
                    "delta": round(delta, 4) if delta else "-",
                    "config_opt": opt_row.iloc[0]["best_config_id"] if not opt_row.empty else "-",
                })
        df_resumen = pd.DataFrame(rows)
        print(df_resumen.to_string(index=False))

    # Plots
    plot_f1_comparativa(best_df)
    plot_baseline_vs_opt(df)
    plot_sharpe_por_ticker(df)
    print(f"\n✓ Plots guardados en {FIG}")
    print(f"\n✓ Reportes:")
    print(f"  {OUT}/MAESTRA_baseline_optimizado.csv  ({len(df)} filas)")
    print(f"  {OUT}/MEJOR_optimizado_por_modelo_tipo_exp.csv")
    print(f"  {OUT}/MEJOR_baseline_por_modelo_tipo_exp.csv")


if __name__ == "__main__":
    main()
