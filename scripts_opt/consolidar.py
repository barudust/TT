"""
================================================================================
CONSOLIDACIÓN — Reportes finales de los 4 modelos optimizados
================================================================================
Lee los CSV de resultados de los 4 modelos optimizados y produce:
  - reportes/resumen_global.csv   (todos los resultados unificados)
  - reportes/mejor_config_por_modelo.json
  - reportes/comparativa_final.csv
  - reportes/figuras/*.png
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import sys
import json
import warnings
import functools
import numpy as np
import pandas as pd
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass
print = functools.partial(print, flush=True)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore")

BASE = Path("RESULTADOS_OPTIMIZADOS")
MODELOS_DIR = BASE / "modelos_optimizados"
OUT = BASE / "reportes"
(OUT / "figuras").mkdir(parents=True, exist_ok=True)

CSV_PATHS = {
    "LogisticRegression": MODELOS_DIR / "lr"       / "resultados_lr_opt.csv",
    "XGBoost":            MODELOS_DIR / "xgboost"  / "resultados_xgb_opt.csv",
    "LSTM":               MODELOS_DIR / "lstm"     / "resultados_lstm_opt.csv",
    "CNN-LSTM":           MODELOS_DIR / "cnn_lstm" / "resultados_cnn_lstm_opt.csv",
}


def cargar_todo():
    dfs = []
    for modelo, path in CSV_PATHS.items():
        if not path.exists():
            print(f"  ⚠ No existe {path}")
            continue
        df = pd.read_csv(path)
        df["modelo"] = modelo
        dfs.append(df)
        print(f"  ✓ {modelo}: {len(df)} filas desde {path.name}")
    if not dfs:
        return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True)


def mejor_config_por_modelo(df):
    """Para cada modelo, selecciona la config con mayor F1-macro test promedio."""
    if df.empty:
        return {}
    out = {}
    for modelo in df["modelo"].unique():
        sub = df[df["modelo"] == modelo]
        # Para cada (config, tipo, exp, lookback), promedio sobre tickers
        if "lookback" in sub.columns:
            agg = sub.groupby(["config_id", "tipo", "experimento", "lookback"],
                              dropna=False)["test_f1_macro"].mean().reset_index()
        else:
            agg = sub.groupby(["config_id", "tipo", "experimento"])["test_f1_macro"].mean().reset_index()
        if agg.empty:
            continue
        idx = agg["test_f1_macro"].idxmax()
        mejor = agg.loc[idx].to_dict()
        out[modelo] = mejor
    return out


def hacer_tabla_resumen(df):
    """Tabla con F1-macro test promedio por modelo×tipo×exp."""
    if df.empty:
        return pd.DataFrame()
    grupo_cols = ["modelo", "config_id", "tipo", "experimento"]
    if "lookback" in df.columns:
        grupo_cols.append("lookback")
    agg = df.groupby(grupo_cols, dropna=False).agg(
        f1_macro_mean=("test_f1_macro", "mean"),
        f1_macro_std =("test_f1_macro", "std"),
        f1_buy_mean  =("test_f1_buy",   "mean"),
        f1_sell_mean =("test_f1_sell",  "mean"),
        f1_buy_sell_avg=("test_f1_buy_sell_avg", "mean"),
        sharpe_mean  =("sharpe_test",  "mean"),
        cum_ret_mean =("cumul_return_test", "mean"),
        n_tickers    =("ticker", "count"),
    ).round(4).reset_index()
    return agg


def graficar_comparativa(df, out_dir):
    """Gráfica de barras con F1-macro promedio por (modelo, exp), separado global/por_ticker."""
    if df.empty:
        return
    for tipo in ["global", "por_ticker"]:
        sub = df[df["tipo"] == tipo]
        if sub.empty:
            continue
        # Usar el mejor config por (modelo, exp, lookback?)
        keys = ["modelo", "config_id", "experimento"]
        if "lookback" in sub.columns:
            keys.append("lookback")
        agg = sub.groupby(keys)["test_f1_macro"].mean().reset_index()
        # Pick best config per (modelo, exp)
        best = (agg.sort_values("test_f1_macro", ascending=False)
                   .drop_duplicates(["modelo", "experimento"])
                   .sort_values(["modelo", "experimento"]))

        fig, ax = plt.subplots(figsize=(12, 6))
        piv = best.pivot(index="modelo", columns="experimento", values="test_f1_macro")
        piv.plot(kind="bar", ax=ax, edgecolor="black", colormap="tab10", width=0.7)
        ax.axhline(0.333, color="red", linestyle="--", linewidth=1, label="Aleatorio (1/3)")
        ax.set_title(f"F1-macro Test — Mejor Config por Modelo ({tipo.upper()})",
                     fontsize=12, fontweight="bold")
        ax.set_ylabel("F1-macro (test)")
        ax.set_ylim(0, max(0.55, piv.max().max() * 1.1))
        ax.legend(title="Experimento")
        ax.tick_params(axis="x", rotation=0)
        ax.grid(axis="y", alpha=0.3)
        for cont in ax.containers:
            ax.bar_label(cont, fmt="%.3f", padding=2, fontsize=8)
        plt.tight_layout()
        fig.savefig(out_dir / f"f1_macro_{tipo}_por_modelo_exp.png", dpi=120, bbox_inches="tight")
        plt.close(fig)


def graficar_por_ticker(df, out_dir):
    """Heatmap F1-macro por (modelo, ticker) para cada experimento."""
    if df.empty:
        return
    sub = df[df["tipo"] == "por_ticker"]
    if sub.empty:
        return
    for exp_id in sub["experimento"].unique():
        sub_e = sub[sub["experimento"] == exp_id]
        # mejor config por modelo
        keys = ["modelo", "config_id", "ticker"]
        if "lookback" in sub_e.columns:
            keys.append("lookback")
        agg = sub_e.groupby(keys)["test_f1_macro"].mean().reset_index()
        # mejor config por modelo (criterio: media sobre tickers)
        agg["mean_per_config"] = agg.groupby(["modelo", "config_id"] +
            (["lookback"] if "lookback" in agg.columns else []))["test_f1_macro"].transform("mean")
        idx = (agg.sort_values("mean_per_config", ascending=False)
                  .drop_duplicates("modelo")
                  [["modelo", "config_id"] + (["lookback"] if "lookback" in agg.columns else [])])
        merge_keys = ["modelo", "config_id"] + (["lookback"] if "lookback" in agg.columns else [])
        best_df = agg.merge(idx, on=merge_keys, how="inner")

        piv = best_df.pivot_table(index="modelo", columns="ticker", values="test_f1_macro")
        if piv.empty:
            continue
        fig, ax = plt.subplots(figsize=(11, 5))
        sns.heatmap(piv, ax=ax, annot=True, fmt=".3f", cmap="YlGn", vmin=0.20, vmax=0.55,
                    linewidths=0.5)
        ax.set_title(f"F1-macro Test por Ticker — Exp {exp_id} — Mejor Config por Modelo")
        plt.tight_layout()
        fig.savefig(out_dir / f"heatmap_por_ticker_exp_{exp_id}.png", dpi=120, bbox_inches="tight")
        plt.close(fig)


def graficar_sharpe(df, out_dir):
    """Sharpe promedio por modelo y experimento."""
    if df.empty or "sharpe_test" not in df.columns:
        return
    for tipo in ["global", "por_ticker"]:
        sub = df[df["tipo"] == tipo]
        if sub.empty:
            continue
        keys = ["modelo", "config_id", "experimento"]
        if "lookback" in sub.columns:
            keys.append("lookback")
        agg = sub.groupby(keys)["sharpe_test"].mean().reset_index()
        best = (agg.sort_values("sharpe_test", ascending=False)
                   .drop_duplicates(["modelo", "experimento"])
                   .sort_values(["modelo", "experimento"]))
        fig, ax = plt.subplots(figsize=(12, 6))
        piv = best.pivot(index="modelo", columns="experimento", values="sharpe_test")
        piv.plot(kind="bar", ax=ax, edgecolor="black", colormap="tab10", width=0.7)
        ax.axhline(0.0, color="black", linewidth=0.5)
        ax.set_title(f"Sharpe Test — Mejor Config por Modelo ({tipo.upper()})",
                     fontsize=12, fontweight="bold")
        ax.set_ylabel("Sharpe anualizado")
        ax.legend(title="Experimento")
        ax.tick_params(axis="x", rotation=0)
        ax.grid(axis="y", alpha=0.3)
        for cont in ax.containers:
            ax.bar_label(cont, fmt="%.2f", padding=2, fontsize=8)
        plt.tight_layout()
        fig.savefig(out_dir / f"sharpe_{tipo}_por_modelo_exp.png", dpi=120, bbox_inches="tight")
        plt.close(fig)


def main():
    print("="*70)
    print("  CONSOLIDACIÓN DE RESULTADOS OPTIMIZADOS")
    print("="*70)

    df = cargar_todo()
    if df.empty:
        print("  ⚠ No hay resultados aún.")
        return

    print(f"\nTotal de registros: {len(df)}")

    # Tabla resumen
    df.to_csv(OUT / "resumen_global.csv", index=False)
    print(f"  ✓ resumen_global.csv guardado ({len(df)} filas)")

    resumen = hacer_tabla_resumen(df)
    resumen.to_csv(OUT / "comparativa_final.csv", index=False)
    print(f"  ✓ comparativa_final.csv guardado ({len(resumen)} filas)")

    mejor = mejor_config_por_modelo(df)
    with open(OUT / "mejor_config_por_modelo.json", "w") as f:
        json.dump(mejor, f, indent=2, default=str)
    print(f"  ✓ mejor_config_por_modelo.json guardado")

    # Gráficas
    fig_dir = OUT / "figuras"
    graficar_comparativa(df, fig_dir)
    graficar_por_ticker(df, fig_dir)
    graficar_sharpe(df, fig_dir)
    print(f"  ✓ Figuras guardadas en {fig_dir}")

    # Imprimir resumen amigable
    print("\n" + "="*70)
    print("  RESUMEN — F1-MACRO PROMEDIO POR MODELO×EXPERIMENTO (mejor config)")
    print("="*70)
    for tipo in ["global", "por_ticker"]:
        sub = df[df["tipo"] == tipo]
        if sub.empty:
            continue
        keys = ["modelo", "config_id", "experimento"]
        if "lookback" in sub.columns:
            keys.append("lookback")
        agg = sub.groupby(keys)["test_f1_macro"].mean().reset_index()
        best = (agg.sort_values("test_f1_macro", ascending=False)
                   .drop_duplicates(["modelo", "experimento"]))
        piv = best.pivot(index="modelo", columns="experimento", values="test_f1_macro").round(4)
        print(f"\n  --- {tipo.upper()} ---")
        print(piv.to_string())


if __name__ == "__main__":
    main()
