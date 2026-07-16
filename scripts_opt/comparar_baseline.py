"""
Compara resultados optimizados vs baseline original.
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import json
import warnings
import functools
import pandas as pd
from pathlib import Path

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass
print = functools.partial(print, flush=True)
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

OUT_DIR = Path("RESULTADOS_OPTIMIZADOS/reportes")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def cargar_baseline():
    dfs = []
    for modelo, path in BASELINE_CSVS.items():
        if not Path(path).exists():
            continue
        df = pd.read_csv(path)
        df["modelo"] = modelo
        df["config_id"] = "BASELINE"
        df["fuente"] = "baseline"
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()


def cargar_optimizado():
    dfs = []
    for modelo, path in OPT_CSVS.items():
        if not Path(path).exists():
            continue
        df = pd.read_csv(path)
        df["modelo"] = modelo
        df["fuente"] = "optimizado"
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()


def main():
    print("="*70)
    print("  COMPARATIVA BASELINE vs OPTIMIZADO")
    print("="*70)

    df_base = cargar_baseline()
    df_opt  = cargar_optimizado()
    print(f"\nBaseline: {len(df_base)} filas")
    print(f"Optimizado: {len(df_opt)} filas")

    if df_base.empty and df_opt.empty:
        print("⚠ Sin datos")
        return

    # Combinar
    df_all = pd.concat([df_base, df_opt], ignore_index=True, sort=False)

    # Para cada modelo, encontrar mejor F1-macro test (global vs por_ticker, baseline vs optimizado)
    print("\n" + "="*70)
    print("  MEJOR F1-MACRO TEST POR MODELO×TIPO×EXP (baseline vs optimizado)")
    print("="*70)

    for modelo in ["LogisticRegression", "XGBoost", "LSTM", "CNN-LSTM"]:
        print(f"\n--- {modelo} ---")
        for tipo in ["global", "por_ticker"]:
            sub = df_all[(df_all["modelo"] == modelo) & (df_all["tipo"] == tipo)]
            if sub.empty:
                continue
            # Agg por exp y fuente
            keys = ["fuente", "experimento"]
            if "lookback" in sub.columns:
                keys.append("lookback")
            agg = sub.groupby(keys)["test_f1_macro"].agg(["mean", "max", "count"]).round(4).reset_index()
            print(f"\n  {tipo.upper()}:")
            print(agg.to_string(index=False))

    # Mejor config por modelo
    print("\n" + "="*70)
    print("  MEJOR CONFIGURACIÓN POR MODELO (en F1-macro test)")
    print("="*70)
    for modelo in df_all["modelo"].unique():
        sub = df_all[df_all["modelo"] == modelo]
        if sub.empty:
            continue
        # Agrupar por config y tipo y exp
        keys = ["config_id", "tipo", "experimento"]
        if "lookback" in sub.columns:
            keys.append("lookback")
        agg = sub.groupby(keys, dropna=False).agg(
            f1_macro_mean=("test_f1_macro", "mean"),
            n=("test_f1_macro", "count"),
        ).reset_index()
        # Top 5 por F1 dentro de cada (tipo, exp)
        for tipo in ["global", "por_ticker"]:
            sub_t = agg[agg["tipo"] == tipo]
            if sub_t.empty:
                continue
            print(f"\n  {modelo} — {tipo}:")
            for exp in sorted(sub_t["experimento"].unique()):
                sub_e = sub_t[sub_t["experimento"] == exp].sort_values("f1_macro_mean", ascending=False).head(3)
                if not sub_e.empty:
                    print(f"    Exp {exp}: " + " | ".join(
                        f"{row['config_id']}({row.get('lookback','-')}): {row['f1_macro_mean']:.4f}"
                        for _, row in sub_e.iterrows()
                    ))

    # Guardar tabla combinada
    df_all.to_csv(OUT_DIR / "comparativa_baseline_vs_optimizado.csv", index=False)
    print(f"\n✓ Guardado en {OUT_DIR / 'comparativa_baseline_vs_optimizado.csv'}")


if __name__ == "__main__":
    main()
