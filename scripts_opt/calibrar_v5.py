"""
================================================================================
CALIBRACIÓN DE LA CAPA DE DECISIÓN
================================================================================
El paper señala que los modelos predicen muy pocos BUY frente al 30 % real
(`paper.tex:301`: LR predice 18 %). Eso no se arregla reentrenando: se arregla
en la capa de decisión, que es gratis porque opera sobre probabilidades ya
calculadas.

Se prueban dos ajustes, AMBOS calibrados solo en validación (2024) y aplicados
una vez a test (2025):

  1. Pesos por clase: argmax_k (p_k * w_k), con w_HOLD fijo en 1 y w_SELL, w_BUY
     buscados en malla. Es equivalente a mover los umbrales de decisión.
  2. Escalado por temperatura: p^(1/T) renormalizado, con T ajustada por log-loss.

Se reporta F1-macro, Sharpe y distribución de señales antes y después.

    python scripts_opt/calibrar_v5.py            # Exp B GLOBAL, los 5 modelos
    python scripts_opt/calibrar_v5.py --exp A
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import sys
import json
import functools
import warnings
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

from sklearn.metrics import f1_score, log_loss
from common import metricas_full
from common_v5 import OUT_V5, SEEDS_5, correr, registrar, metricas_con_costos
import run_v5 as R


def _pesos_optimos(probs_val, y_val, n=21, lo=0.4, hi=2.5):
    """Malla sobre (w_sell, w_buy) maximizando F1-macro en validación."""
    rejilla = np.geomspace(lo, hi, n)
    mejor, mejor_f1 = (1.0, 1.0), -1.0
    for ws in rejilla:
        for wb in rejilla:
            w = np.array([ws, 1.0, wb])
            f1 = f1_score(y_val, (probs_val * w).argmax(1),
                          average="macro", zero_division=0)
            if f1 > mejor_f1:
                mejor_f1, mejor = f1, (ws, wb)
    return np.array([mejor[0], 1.0, mejor[1]]), mejor_f1


def _temperatura_optima(probs_val, y_val, n=41):
    """T que minimiza log-loss en validación (p^(1/T) renormalizado)."""
    mejor_T, mejor_ll = 1.0, np.inf
    for T in np.geomspace(0.3, 4.0, n):
        p = np.power(np.clip(probs_val, 1e-9, 1), 1.0 / T)
        p = p / p.sum(1, keepdims=True)
        ll = log_loss(y_val, p, labels=[0, 1, 2])
        if ll < mejor_ll:
            mejor_ll, mejor_T = ll, T
    return mejor_T


def _aplicar_T(probs, T):
    p = np.power(np.clip(probs, 1e-9, 1), 1.0 / T)
    return p / p.sum(1, keepdims=True)


def _resumen(nombre, etiqueta, y, pred, r, tk):
    m = metricas_full(y, pred, r_forward=r)
    c = metricas_con_costos(pred, r, tk, 5.0)
    d = m["signal_distribution"]
    print(f"    {etiqueta:<22} F1={m['f1_macro']:.4f}  Sharpe={m.get('sharpe_test', 0):+.3f}  "
          f"Sharpe5pb={c['sharpe_5bp']:+.3f}  "
          f"señales B/H/S = {d['BUY']['pct']:.0f}/{d['HOLD']['pct']:.0f}/{d['SELL']['pct']:.0f}%")
    return dict(modelo=nombre, variante=etiqueta, f1=m["f1_macro"],
                sharpe=m.get("sharpe_test"), sharpe_5bp=c["sharpe_5bp"],
                win_rate=m.get("win_rate_test"), profit_factor=m.get("profit_factor_test"),
                pct_buy=d["BUY"]["pct"], pct_hold=d["HOLD"]["pct"], pct_sell=d["SELL"]["pct"])


def main(exp="B"):
    print("=" * 78)
    print(f"  CALIBRACIÓN DE LA CAPA DE DECISIÓN — Exp {exp} GLOBAL")
    print("  pesos y temperatura ajustados en 2024, aplicados una vez a 2025")
    print("=" * 78)

    dl = json.load(open(R.GANADORES_DL, encoding="utf-8"))
    clas = json.load(open(R.GANADORES_CLASICOS, encoding="utf-8"))
    filas = []

    trabajos = [(n, "clasico", info["params"]) for n, info in clas.items()]
    trabajos += [(R.NOMBRE_V4[a], "dl", R._cargar_cfg(R._ganador_dl(dl, a, exp)["cfg"]))
                 for a in R.ARCHS]

    for nombre, tipo, cfg in trabajos:
        print(f"\n  ── {nombre} ──")
        if tipo == "clasico":
            res = R._correr_clasico(nombre, cfg, exp, "final", semillas=SEEDS_5,
                                    refit=True, devolver_probs=True)
        else:
            res = correr(cfg, exp, "final", "global", semillas=SEEDS_5, devolver_probs=True)

        pv, yv = res["probs_val"], res["y_val"]
        pe, ye = res["probs_eval"], res["y_eval"]
        r, tk = res["r_eval"], res["tk_eval"]

        filas.append(_resumen(nombre, "sin calibrar", ye, pe.argmax(1), r, tk))

        w, f1v = _pesos_optimos(pv, yv)
        print(f"    pesos óptimos en val: SELL={w[0]:.2f} HOLD=1.00 BUY={w[2]:.2f} "
              f"(F1 val {f1_score(yv, pv.argmax(1), average='macro', zero_division=0):.4f} "
              f"→ {f1v:.4f})")
        filas.append(_resumen(nombre, "pesos por clase", ye, (pe * w).argmax(1), r, tk))

        T = _temperatura_optima(pv, yv)
        peT = _aplicar_T(pe, T)
        print(f"    temperatura óptima en val: T={T:.2f}")
        filas.append(_resumen(nombre, "temperatura", ye, peT.argmax(1), r, tk))

        wT, _ = _pesos_optimos(_aplicar_T(pv, T), yv)
        filas.append(_resumen(nombre, "temperatura + pesos", ye, (peT * wT).argmax(1), r, tk))

    df = pd.DataFrame(filas)
    salida = OUT_V5 / f"calibracion_exp{exp}.csv"
    df.to_csv(salida, index=False)
    print(f"\n{'='*78}")
    print("  Resumen (test 2025, mejor variante por modelo según F1):")
    mejor = df.loc[df.groupby("modelo")["f1"].idxmax()]
    print(mejor[["modelo", "variante", "f1", "sharpe", "pct_buy"]].to_string(index=False))
    print(f"\n  → {salida}")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--exp", default="B")
    main(**vars(p.parse_args()))
