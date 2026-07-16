"""
Compara v1 (61 features) vs v3 (94 features) — para los 5 modelos × 3 exps × global+ticker.
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

OUT = Path("RESULTADOS_OPTIMIZADOS/reportes/v1_vs_v3")
OUT.mkdir(parents=True, exist_ok=True)


def load_v1():
    """Carga consolidación v1 (120 experimentos)."""
    p = "RESULTADOS_OPTIMIZADOS/reportes/final_120/120_experimentos.csv"
    if not Path(p).exists(): return None
    df = pd.read_csv(p)
    df["fuente"] = "v1 (61 features)"
    return df


def load_v3():
    """Carga v3 directamente del CSV de train_all_v3."""
    p = "RESULTADOS_OPTIMIZADOS/v3/resultados_v3.csv"
    if not Path(p).exists(): return None
    df = pd.read_csv(p)
    df["fuente"] = "v3 (94 features)"
    # rename cols to match v1
    df = df.rename(columns={
        "test_f1_macro": "F1_macro",
        "test_f1_buy": "F1_BUY", "test_f1_sell": "F1_SELL", "test_f1_hold": "F1_HOLD",
        "win_rate_test": "Win_Rate", "profit_factor_test": "Profit_Factor",
        "max_drawdown_test": "Max_Drawdown", "sharpe_test": "Sharpe",
        "cumul_return_test": "Cum_Return",
    })
    # Para modelos secuenciales, elegir mejor lookback
    sec_models = ["LSTM", "CNN", "CNN-LSTM"]
    sec = df[df["modelo"].isin(sec_models)]
    if not sec.empty and "lookback" in sec.columns:
        idx = sec.groupby(["modelo","tipo","ticker","experimento"])["F1_macro"].idxmax()
        sec_best = sec.loc[idx]
        no_sec = df[~df["modelo"].isin(sec_models)]
        df = pd.concat([no_sec, sec_best], ignore_index=True)
    return df


def main():
    print("="*70); print("  COMPARATIVA V1 vs V3 — features de mercado expandidas"); print("="*70)

    v1 = load_v1(); v3 = load_v3()
    if v1 is None: print("⚠ Sin v1"); return
    if v3 is None: print("⚠ Sin v3 todavía"); return

    print(f"  v1: {len(v1)} filas")
    print(f"  v3: {len(v3)} filas")

    MODEL_ORDER = ["LR", "XGBoost", "LSTM", "CNN", "CNN-LSTM"]
    EXPS = ["A", "B", "C"]

    # GLOBAL F1-macro: v1 vs v3
    print("\n  --- GLOBAL F1-macro: v1 → v3 ---")
    rows = []
    for model in MODEL_ORDER:
        for exp in EXPS:
            v1g = v1[(v1["modelo"]==model) & (v1["tipo"]=="global") & (v1["experimento"]==exp)]
            v3g = v3[(v3["modelo"]==model) & (v3["tipo"]=="global") & (v3["experimento"]==exp)]
            if v1g.empty and v3g.empty: continue
            r = {"modelo": model, "exp": exp,
                 "v1": round(v1g.iloc[0]["F1_macro"], 4) if not v1g.empty else None,
                 "v3": round(v3g.iloc[0]["F1_macro"], 4) if not v3g.empty else None}
            if r["v1"] is not None and r["v3"] is not None:
                r["delta"] = round(r["v3"] - r["v1"], 4)
            rows.append(r)
    df_g = pd.DataFrame(rows)
    print(df_g.to_string(index=False))
    df_g.to_csv(OUT / "F1_GLOBAL_v1_vs_v3.csv", index=False)

    # POR_TICKER mean F1
    print("\n  --- POR-TICKER mean F1-macro: v1 → v3 ---")
    rows = []
    for model in MODEL_ORDER:
        for exp in EXPS:
            v1t = v1[(v1["modelo"]==model) & (v1["tipo"]=="por_ticker") & (v1["experimento"]==exp)]
            v3t = v3[(v3["modelo"]==model) & (v3["tipo"]=="por_ticker") & (v3["experimento"]==exp)]
            r = {"modelo": model, "exp": exp,
                 "v1": round(v1t["F1_macro"].mean(), 4) if not v1t.empty else None,
                 "v3": round(v3t["F1_macro"].mean(), 4) if not v3t.empty else None}
            if r["v1"] is not None and r["v3"] is not None:
                r["delta"] = round(r["v3"] - r["v1"], 4)
            rows.append(r)
    df_pt = pd.DataFrame(rows)
    print(df_pt.to_string(index=False))
    df_pt.to_csv(OUT / "F1_PORTICKER_v1_vs_v3.csv", index=False)

    # SHARPE GLOBAL
    print("\n  --- GLOBAL Sharpe: v1 → v3 ---")
    rows = []
    for model in MODEL_ORDER:
        for exp in EXPS:
            v1g = v1[(v1["modelo"]==model) & (v1["tipo"]=="global") & (v1["experimento"]==exp)]
            v3g = v3[(v3["modelo"]==model) & (v3["tipo"]=="global") & (v3["experimento"]==exp)]
            if v1g.empty and v3g.empty: continue
            r = {"modelo": model, "exp": exp,
                 "v1": round(v1g.iloc[0]["Sharpe"], 3) if not v1g.empty else None,
                 "v3": round(v3g.iloc[0]["Sharpe"], 3) if not v3g.empty else None}
            if r["v1"] is not None and r["v3"] is not None:
                r["delta"] = round(r["v3"] - r["v1"], 3)
            rows.append(r)
    df_sh = pd.DataFrame(rows)
    print(df_sh.to_string(index=False))
    df_sh.to_csv(OUT / "Sharpe_GLOBAL_v1_vs_v3.csv", index=False)

    # Plot
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    for i, exp in enumerate(EXPS):
        ax = axes[i]
        sub = df_g[df_g["exp"]==exp]
        if sub.empty: continue
        x = np.arange(len(sub))
        w = 0.35
        ax.bar(x - w/2, sub["v1"].fillna(0).values, w, label="v1 (61)", color="#888888", edgecolor="black")
        ax.bar(x + w/2, sub["v3"].fillna(0).values, w, label="v3 (94)", color="#2ecc71", edgecolor="black")
        ax.set_xticks(x); ax.set_xticklabels(sub["modelo"].values, rotation=15)
        ax.set_title(f"Exp {exp} — GLOBAL", fontweight="bold")
        ax.axhline(0.333, color="red", linestyle="--", linewidth=1)
        ax.set_ylim(0, 0.50); ax.grid(axis="y", alpha=0.3)
        ax.legend(loc="lower left", fontsize=9)
        for j, (a, b) in enumerate(zip(sub["v1"].fillna(0).values, sub["v3"].fillna(0).values)):
            if a > 0: ax.text(j-w/2, a+0.005, f"{a:.3f}", ha="center", fontsize=8)
            if b > 0: ax.text(j+w/2, b+0.005, f"{b:.3f}", ha="center", fontsize=8)
    fig.suptitle("F1-Macro Test — v1 (61 features) vs v3 (94 features con mercado expandido)",
                 fontsize=14, fontweight="bold")
    plt.tight_layout()
    fig.savefig(OUT / "F1_v1_vs_v3.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\n✓ Plot guardado en {OUT}")


if __name__ == "__main__":
    main()
