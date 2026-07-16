"""
================================================================================
ANÁLISIS — FEATURE SELECTION ESTADÍSTICA vs TODAS LAS FEATURES
================================================================================
Compara:
  - BASELINE: features filtradas por Pearson+VIF (LR), SHAP (XGB), Spearman (LSTM/CNN/CNN-LSTM)
  - OPTIMIZADO: todas las 61 features

Métricas: F1-macro, Win Rate, Profit Factor, Max Drawdown
Modelos: LR, XGBoost, LSTM, CNN puro, CNN-LSTM
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

# Sources
SOURCES = {
    # filtradas: vienen del baseline original (script 04-07) que usó features del script 02
    "LR_filt":      ("tesis_ml_stocks/04_models/logistic_regression/resultados_lr.csv", "filtered"),
    "LR_all":       ("RESULTADOS_OPTIMIZADOS/modelos_optimizados/lr/resultados_lr_opt.csv",
                     "all", "LR-02-elasticnet-all"),
    "XGB_filt":     ("tesis_ml_stocks/04_models/xgboost/resultados_xgb.csv", "filtered"),
    "XGB_all":      ("RESULTADOS_OPTIMIZADOS/modelos_optimizados/xgboost/resultados_xgb_opt.csv",
                     "all", "XGB-01-all"),
    "LSTM_filt":    ("tesis_ml_stocks/04_models/lstm/resultados_lstm.csv", "filtered"),
    "LSTM_all":     ("RESULTADOS_OPTIMIZADOS/modelos_optimizados/lstm/resultados_lstm_opt.csv",
                     "all", "LSTM-02-bi"),
    "CNNLSTM_filt": ("tesis_ml_stocks/04_models/cnn_lstm/resultados_cnn_lstm.csv", "filtered"),
    "CNNLSTM_all":  ("RESULTADOS_OPTIMIZADOS/modelos_optimizados/cnn_lstm/resultados_cnn_lstm_opt.csv",
                     "all", "CNN-01-base"),
    "CNN_filt":     ("RESULTADOS_OPTIMIZADOS/modelos_optimizados/cnn_puro_filtradas/resultados_cnn_puro_filtradas.csv",
                     "filtered"),
    "CNN_all":      ("RESULTADOS_OPTIMIZADOS/modelos_optimizados/cnn_puro/resultados_cnn_puro.csv",
                     "all"),
}

# Mapping modelo display
MODEL_NAMES = {
    "LR":      "LogisticRegression",
    "XGB":     "XGBoost",
    "LSTM":    "LSTM",
    "CNNLSTM": "CNN-LSTM",
    "CNN":     "CNN",
}

OUT_DIR = Path("RESULTADOS_OPTIMIZADOS/reportes/feature_selection")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_source(key, info):
    """Carga el csv y filtra al config_id si aplica."""
    path = info[0]
    if not Path(path).exists():
        print(f"  ⚠ No existe {path}")
        return None
    df = pd.read_csv(path)
    if len(info) >= 3:  # config_id filter for optimized
        cfg = info[2]
        df = df[df["config_id"] == cfg]
    df["fuente_features"] = info[1]
    return df


def best_per_exp_tipo(df, model_key):
    """Devuelve mejor F1-macro test por (tipo, exp) para un modelo."""
    if df.empty: return pd.DataFrame()
    keys = ["tipo", "experimento"]
    if "lookback" in df.columns:
        keys.append("lookback")
    agg = df.groupby(keys, dropna=False).agg(
        f1_macro=("test_f1_macro", "max"),
        win_rate=("win_rate_test", "max"),
        profit_factor=("profit_factor_test", "max"),
        max_dd=("max_drawdown_test", "max"),  # max=min in absolute (less negative)
        sharpe=("sharpe_test", "max"),
        n=("test_f1_macro", "count"),
    ).reset_index()
    return agg


def main():
    print("="*75)
    print("  ANÁLISIS — Feature Selection Estadística vs Todas las 61 Features")
    print("="*75)

    all_data = []
    for key, info in SOURCES.items():
        df = load_source(key, info)
        if df is None: continue
        # Get model name
        parts = key.split("_")
        model_key = parts[0]
        df["modelo"] = MODEL_NAMES.get(model_key, model_key)
        df["features_source"] = parts[1]  # 'filt' or 'all'
        all_data.append(df)

    df_all = pd.concat(all_data, ignore_index=True, sort=False)
    print(f"\nTotal registros: {len(df_all)}")

    # Tabla GLOBAL comparativa
    print("\n" + "="*75)
    print("  COMPARATIVA GLOBAL — F1-macro test (mejor por modelo×exp×features)")
    print("="*75)
    rows_g = []
    for model in MODEL_NAMES.values():
        for exp in ["A", "B", "C"]:
            sub = df_all[(df_all["modelo"] == model) & (df_all["tipo"] == "global") &
                         (df_all["experimento"] == exp)]
            if sub.empty: continue
            for fs in ["filt", "all"]:
                ss = sub[sub["features_source"] == fs]
                if ss.empty: continue
                best = ss.sort_values("test_f1_macro", ascending=False).iloc[0]
                rows_g.append({
                    "modelo": model, "exp": exp, "features": fs,
                    "n_features": int(best.get("n_features", 0)) if not pd.isna(best.get("n_features")) else None,
                    "F1_macro": round(best["test_f1_macro"], 4),
                    "Win_Rate": round(best.get("win_rate_test", 0), 4) if pd.notna(best.get("win_rate_test")) else None,
                    "Profit_Factor": round(best.get("profit_factor_test", 0), 4) if pd.notna(best.get("profit_factor_test")) else None,
                    "Max_Drawdown": round(best.get("max_drawdown_test", 0), 4) if pd.notna(best.get("max_drawdown_test")) else None,
                })
    df_g = pd.DataFrame(rows_g)
    print(df_g.to_string(index=False))
    df_g.to_csv(OUT_DIR / "comparativa_GLOBAL.csv", index=False)

    # Pivots con deltas (all - filt)
    print("\n" + "="*75)
    print("  DELTAS (all features − filtered) — GLOBAL")
    print("="*75)
    metrica_cols = ["F1_macro", "Win_Rate", "Profit_Factor", "Max_Drawdown"]
    for metric in metrica_cols:
        piv = df_g.pivot_table(index="modelo", columns=["exp", "features"], values=metric)
        # Calcular deltas
        rows = []
        for model in MODEL_NAMES.values():
            if model not in piv.index: continue
            r = {"modelo": model}
            for exp in ["A", "B", "C"]:
                try:
                    v_all = piv.loc[model, (exp, "all")]
                    v_filt = piv.loc[model, (exp, "filt")]
                    r[f"Exp_{exp}_filt"] = round(v_filt, 4) if pd.notna(v_filt) else None
                    r[f"Exp_{exp}_all"]  = round(v_all,  4) if pd.notna(v_all) else None
                    r[f"Exp_{exp}_Δ"]    = round(v_all - v_filt, 4) if (pd.notna(v_all) and pd.notna(v_filt)) else None
                except KeyError:
                    pass
            rows.append(r)
        df_d = pd.DataFrame(rows)
        print(f"\n  --- {metric} ---")
        print(df_d.to_string(index=False))
        df_d.to_csv(OUT_DIR / f"deltas_GLOBAL_{metric}.csv", index=False)

    # Plot: F1 filt vs all
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    for i, exp in enumerate(["A", "B", "C"]):
        ax = axes[i]
        sub = df_g[df_g["exp"] == exp]
        if sub.empty: continue
        piv = sub.pivot(index="modelo", columns="features", values="F1_macro")
        # Reordenar modelos
        order = [m for m in ["LogisticRegression", "XGBoost", "LSTM", "CNN", "CNN-LSTM"] if m in piv.index]
        piv = piv.loc[order]
        x = np.arange(len(piv))
        w = 0.35
        f_vals = piv["filt"].fillna(0).values if "filt" in piv.columns else np.zeros(len(piv))
        a_vals = piv["all"].fillna(0).values  if "all"  in piv.columns else np.zeros(len(piv))
        ax.bar(x - w/2, f_vals, w, label="Filtradas (Pearson/VIF/SHAP/Spearman)", color="#888888", edgecolor="black")
        ax.bar(x + w/2, a_vals, w, label="Todas las 61", color="#2ecc71", edgecolor="black")
        ax.set_xticks(x); ax.set_xticklabels(piv.index, rotation=15)
        ax.set_title(f"Exp {exp}", fontweight="bold")
        ax.axhline(0.333, color="red", linestyle="--", linewidth=1)
        ax.set_ylim(0, 0.50)
        ax.grid(axis="y", alpha=0.3)
        ax.legend(loc="lower left", fontsize=8)
        for j, (f, a) in enumerate(zip(f_vals, a_vals)):
            if f > 0: ax.text(j-w/2, f+0.005, f"{f:.3f}", ha="center", fontsize=7)
            if a > 0: ax.text(j+w/2, a+0.005, f"{a:.3f}", ha="center", fontsize=7)
    fig.suptitle("F1-macro Test — Features Filtradas vs Todas las 61 (GLOBAL)",
                 fontsize=14, fontweight="bold")
    plt.tight_layout()
    fig.savefig(OUT_DIR / "F1_filt_vs_all_GLOBAL.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\n✓ Plot guardado en {OUT_DIR / 'F1_filt_vs_all_GLOBAL.png'}")


if __name__ == "__main__":
    main()
