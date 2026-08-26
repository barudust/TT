"""Target ablation extendido: horizontes 2, 7d + percentil 0.20/0.80.
Confirma / refina la mejor combinación encontrada en el ablation inicial."""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import sys, functools, warnings
from pathlib import Path
import numpy as np
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass
print = functools.partial(print, flush=True)
warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).parent))
from via8_dataset import (_cargar_panel, _construir_target, _preparar, _build_lr,
                           _metricas_backtest, LR_HP, TICKERS, OUT, BASELINE)

print("=" * 70)
print("TARGET ABLATION EXTENDIDO — más horizontes y percentiles más extremos")
print("=" * 70)

horizontes = [2, 5, 7, 10]   # completar el barrido
percentiles = [(0.20, 0.80), (0.25, 0.75), (0.30, 0.70)]

filas = []
for h in horizontes:
    for q_lo, q_hi in percentiles:
        dfs = {}
        for tk in TICKERS:
            df = _cargar_panel(tk).copy()
            r_fwd_new, target_new = _construir_target(df, horizonte=h,
                                                       q_lo=q_lo, q_hi=q_hi)
            df["r_forward_new"] = r_fwd_new
            df["target_new"] = target_new
            dfs[tk] = df

        datos = _preparar(dfs, escalador=LR_HP["escalador"],
                          usar_target_col="target_new", r_fwd_col="r_forward_new")
        model = _build_lr(LR_HP)
        model.fit(datos["X_train"], datos["y_train"])
        pred = model.predict(datos["X_eval"])
        met = _metricas_backtest(pred, datos["y_eval"], datos["r_eval"], datos["tk_eval"])
        fila = {"horizonte_d": h, "q_lo": q_lo, "q_hi": q_hi,
                **met, "n_test": len(datos["y_eval"])}
        filas.append(fila)
        marca = " ⭐" if met["f1"] > BASELINE["LR"]["f1"] + 0.005 else ""
        print(f"  h={h:2d}d  q={q_lo:.2f}/{q_hi:.2f}  F1={met['f1']:.4f} "
              f"Sharpe={met['sharpe']:+.3f}{marca}")

df = pd.DataFrame(filas)
df.to_csv(OUT / "target_ablation_ext.csv", index=False)
print(f"\n✓ Guardado en {OUT}/target_ablation_ext.csv")
