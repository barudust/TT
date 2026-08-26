"""
================================================================================
CALIBRACIÓN DE UMBRAL DE HOLD  (post-procesamiento, SIN reentrenar)
================================================================================
Objetivo: reducir el % de HOLD del modelo en producción (LR elasticnet global,
Exp B) manteniendo o mejorando Sharpe / drawdown / retorno del backtest.

Idea: el .pkl ya produce predict_proba de 3 clases. Hoy la señal sale por
argmax simple. Aquí barremos un umbral tau sobre la probabilidad de HOLD:

    señal = HOLD         si  p_hold >= tau
            argmax(BUY,SELL)  en caso contrario

Subir tau => menos HOLD, más operaciones. Para cada tau reportamos %HOLD,
Sharpe, retorno acumulado, max drawdown, win rate y F1-macro (de referencia),
reusando EXACTAMENTE las métricas de common.py para que sean comparables con
lo que ya está reportado.

NO toca el .pkl. Es una capa de decisión que luego se copia a api/.

Uso (desde la raíz del repo TT/):
    python scripts_opt/calibrar_hold.py
    python scripts_opt/calibrar_hold.py --exp B --pkl api/ml/artifacts/lr_elasticnet_global_expB.pkl
    python scripts_opt/calibrar_hold.py --exp B --cross A C   # valida el mismo modelo en otros periodos
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import sys
import pickle
import argparse
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import (cargar_global, metricas_economicas, metricas_clasificacion,
                    NOMBRES)  # NOMBRES: {0:SELL,1:HOLD,2:BUY}

# sklearn ordena classes_ = [0,1,2] => columnas de predict_proba: [SELL, HOLD, BUY]
IDX_SELL, IDX_HOLD, IDX_BUY = 0, 1, 2


# ────────────────────────────────────────────────────────────────────────────
# Regla de decisión
# ────────────────────────────────────────────────────────────────────────────
def decidir(proba, tau):
    """HOLD solo si p_hold >= tau; si no, el mayor entre BUY y SELL."""
    hold = proba[:, IDX_HOLD] >= tau
    buy_vs_sell = np.where(proba[:, IDX_BUY] >= proba[:, IDX_SELL], IDX_BUY, IDX_SELL)
    return np.where(hold, IDX_HOLD, buy_vs_sell)


def evaluar(y_true, pred, r_fwd):
    """Junta métricas económicas + F1 en una sola fila."""
    eco = metricas_economicas(pred, r_fwd)
    clf = metricas_clasificacion(y_true, pred)
    return {
        "pct_hold": clf["signal_distribution"]["HOLD"]["pct"],
        "pct_buy":  clf["signal_distribution"]["BUY"]["pct"],
        "pct_sell": clf["signal_distribution"]["SELL"]["pct"],
        "sharpe":       eco.get("sharpe_test"),
        "cumul_return": eco.get("cumul_return_test"),
        "return_vs_bh": eco.get("return_vs_bh_test"),
        "max_drawdown": eco.get("max_drawdown_test"),
        "win_rate":     eco.get("win_rate_test"),
        "profit_factor":eco.get("profit_factor_test"),
        "f1_macro":     clf["f1_macro"],
        "f1_buy":       clf["f1_buy"],
        "f1_sell":      clf["f1_sell"],
        "f1_hold":      clf["f1_hold"],
    }


# ────────────────────────────────────────────────────────────────────────────
# Carga del modelo en producción + reconstrucción del test set
# ────────────────────────────────────────────────────────────────────────────
def cargar_pkl(pkl_path):
    with open(pkl_path, "rb") as f:
        art = pickle.load(f)
    # el .pkl guarda {"model","scaler","hp","feat_cols","config_id"}
    return art["model"], art["scaler"], art["feat_cols"], art.get("config_id", "?")


def probas_del_modelo(model, scaler, feat_cols, exp_id):
    """Reconstruye el GLOBAL test set del experimento y devuelve proba + y_true + r_fwd + ticker."""
    g = cargar_global(exp_id, feat_cols)          # mismas features y orden que en training
    X_te = scaler.transform(g["X_te"])            # scaler fue fit en train
    proba = model.predict_proba(X_te)             # (n,3) = [SELL,HOLD,BUY]
    return proba, g["y_te"], g["r_fwd_test"], g["ticker_test"]


# ────────────────────────────────────────────────────────────────────────────
# Barrido de umbral
# ────────────────────────────────────────────────────────────────────────────
def barrer(proba, y_true, r_fwd, taus):
    filas = []
    # baseline = argmax normal (lo que corre hoy)
    base_pred = proba.argmax(axis=1)
    fila = {"tau": "baseline(argmax)"}
    fila.update(evaluar(y_true, base_pred, r_fwd))
    filas.append(fila)
    for tau in taus:
        pred = decidir(proba, tau)
        fila = {"tau": round(float(tau), 3)}
        fila.update(evaluar(y_true, pred, r_fwd))
        filas.append(fila)
    return pd.DataFrame(filas)


def guardar_probas_csv(proba, y_true, r_fwd, ticker, path):
    df = pd.DataFrame({
        "ticker":    ticker,
        "p_sell":    proba[:, IDX_SELL],
        "p_hold":    proba[:, IDX_HOLD],
        "p_buy":     proba[:, IDX_BUY],
        "y_true":    y_true,
        "y_true_lbl":[NOMBRES[int(v)] for v in y_true],
        "r_forward": r_fwd,
    })
    df.to_csv(path, index=False)
    return path


# ────────────────────────────────────────────────────────────────────────────
# Plot (opcional, si hay matplotlib)
# ────────────────────────────────────────────────────────────────────────────
def graficar(df, exp_id, out_png):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        print("  (matplotlib no disponible, se omite el gráfico)")
        return None
    d = df[df["tau"] != "baseline(argmax)"].copy()
    d["tau"] = d["tau"].astype(float)
    base = df[df["tau"] == "baseline(argmax)"].iloc[0]

    fig, ax1 = plt.subplots(figsize=(9, 5.5))
    ax1.plot(d["tau"], d["pct_hold"], color="#c0392b", marker="o", ms=3, label="% HOLD")
    ax1.axhline(base["pct_hold"], color="#c0392b", ls=":", alpha=.5)
    ax1.set_xlabel("umbral tau sobre p_hold")
    ax1.set_ylabel("% HOLD", color="#c0392b")
    ax1.tick_params(axis="y", labelcolor="#c0392b")

    ax2 = ax1.twinx()
    ax2.plot(d["tau"], d["sharpe"], color="#2471a3", marker="s", ms=3, label="Sharpe")
    ax2.axhline(base["sharpe"], color="#2471a3", ls=":", alpha=.5,
                label=f"Sharpe baseline={base['sharpe']:.3f}")
    ax2.set_ylabel("Sharpe (test)", color="#2471a3")
    ax2.tick_params(axis="y", labelcolor="#2471a3")

    fig.suptitle(f"Frontera HOLD vs Sharpe — Exp {exp_id} (global)")
    fig.tight_layout()
    fig.savefig(out_png, dpi=130)
    print(f"  Gráfico → {out_png}")
    return out_png


# ────────────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp", default="B", help="Experimento del test set principal (default B)")
    ap.add_argument("--pkl", default="api/ml/artifacts/lr_elasticnet_global_expB.pkl",
                    help="Ruta al .pkl en producción")
    ap.add_argument("--cross", nargs="*", default=[],
                    help="Otros experimentos donde validar el MISMO modelo (ej: --cross A C)")
    ap.add_argument("--tau-min", type=float, default=0.30)
    ap.add_argument("--tau-max", type=float, default=0.70)
    ap.add_argument("--tau-step", type=float, default=0.02)
    ap.add_argument("--outdir", default="RESULTADOS_OPTIMIZADOS/calibracion_hold")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    taus = np.arange(args.tau_min, args.tau_max + 1e-9, args.tau_step)

    model, scaler, feat_cols, cfg = cargar_pkl(args.pkl)
    print(f"Modelo cargado: {cfg}  |  {len(feat_cols)} features  |  clases={list(model.classes_)}")

    resumen = {}
    for exp_id in [args.exp, *args.cross]:
        print(f"\n{'='*70}\n  EXP {exp_id}\n{'='*70}")
        proba, y_true, r_fwd, ticker = probas_del_modelo(model, scaler, feat_cols, exp_id)

        # guardar probas crudas (materia prima para iterar)
        pcsv = guardar_probas_csv(proba, y_true, r_fwd, ticker,
                                  outdir / f"probas_exp{exp_id}.csv")
        print(f"  Probas por observación → {pcsv}  (n={len(y_true)})")

        df = barrer(proba, y_true, r_fwd, taus)
        rcsv = outdir / f"frontera_exp{exp_id}.csv"
        df.to_csv(rcsv, index=False)

        # tabla compacta a consola
        cols = ["tau", "pct_hold", "pct_buy", "pct_sell",
                "sharpe", "cumul_return", "max_drawdown", "win_rate", "f1_macro"]
        with pd.option_context("display.width", 160, "display.max_rows", None):
            print("\n" + df[cols].to_string(index=False))
        print(f"\n  Frontera → {rcsv}")
        graficar(df, exp_id, outdir / f"frontera_exp{exp_id}.png")

        # sugerencia automática: menor %HOLD cuyo Sharpe >= Sharpe baseline
        base = df[df["tau"] == "baseline(argmax)"].iloc[0]
        cand = df[(df["tau"] != "baseline(argmax)") & (df["sharpe"] >= base["sharpe"])]
        if not cand.empty:
            best = cand.sort_values("pct_hold").iloc[0]
            print(f"\n  >> Sugerencia (Sharpe >= baseline={base['sharpe']:.3f}): "
                  f"tau={best['tau']}  ->  HOLD {base['pct_hold']:.1f}% -> {best['pct_hold']:.1f}%  "
                  f"| Sharpe {base['sharpe']:.3f} -> {best['sharpe']:.3f}  "
                  f"| retorno {base['cumul_return']:.3f} -> {best['cumul_return']:.3f}  "
                  f"| maxDD {base['max_drawdown']:.3f} -> {best['max_drawdown']:.3f}")
            resumen[exp_id] = best["tau"]
        else:
            print("\n  >> Ningún tau mantiene el Sharpe baseline; revisar la frontera a mano.")

    if resumen:
        print(f"\n{'='*70}\n  tau sugerido por experimento: {resumen}\n{'='*70}")


if __name__ == "__main__":
    main()