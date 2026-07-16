"""
Confidence filtering sobre LR-v1 (mejor modelo): solo predice BUY/SELL si
la probabilidad supera un umbral; si no, HOLD. Esto reduce número de trades
pero mejora precision y Sharpe.
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import sys, warnings, functools, pickle as pkl
import numpy as np
import pandas as pd
from pathlib import Path

try: sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except: pass
print = functools.partial(print, flush=True)
warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).parent))
from common import (TICKERS, EXPERIMENTOS, cargar_dataset, cargar_global,
                    metricas_full, metricas_global_por_ticker,
                    imprimir_metricas, OUT_DIR)
from sklearn.metrics import f1_score

OUT_CF = OUT_DIR / "lr_confidence_filter"
OUT_CF.mkdir(parents=True, exist_ok=True)
RESULTS_CSV = OUT_CF / "resultados_cf.csv"
MODELS_DIR = OUT_DIR / "modelos_optimizados"


def get_LR_probs(ticker, exp_id, tipo="por_ticker"):
    p = (MODELS_DIR / "lr" / "LR-02-elasticnet-all" / f"experimento_{exp_id}" /
         ("modelo_global.pkl" if tipo == "global" else f"{ticker}_modelo.pkl"))
    if not p.exists(): return None, None, None
    with open(p, "rb") as f: o = pkl.load(f)
    d = cargar_dataset(ticker, exp_id, o["feat_cols"]) if tipo == "por_ticker" \
        else cargar_global(exp_id, o["feat_cols"])
    Xv = o["scaler"].transform(d["X_va"])
    Xt = o["scaler"].transform(d["X_te"])
    return o["model"].predict_proba(Xv), o["model"].predict_proba(Xt), d


def apply_filter(probs, conf_buy, conf_sell):
    """Si max prob clase BUY > conf_buy → BUY. Si max prob clase SELL > conf_sell → SELL.
    Si argmax es HOLD, mantener HOLD."""
    pred = probs.argmax(axis=1)
    for i in range(len(probs)):
        if pred[i] == 2 and probs[i, 2] < conf_buy:
            pred[i] = 1  # downgrade to HOLD
        elif pred[i] == 0 and probs[i, 0] < conf_sell:
            pred[i] = 1
    return pred


def buscar_thresholds(probs_va, y_va, criterio="f1"):
    """Maximiza criterio (f1 o sharpe-proxy) en val variando confiance."""
    mejor = {"score": -np.inf, "cb": 0.34, "cs": 0.34}
    for cb in np.linspace(0.34, 0.65, 12):
        for cs in np.linspace(0.34, 0.65, 12):
            pred = apply_filter(probs_va, cb, cs)
            f1 = f1_score(y_va, pred, average="macro", zero_division=0)
            if f1 > mejor["score"]:
                mejor = {"score": f1, "cb": cb, "cs": cs}
    return mejor


def correr_exp(exp_id):
    print(f"\n{'═'*70}\n  CONFIDENCE FILTER LR  |  Exp {exp_id}\n{'═'*70}")
    resultados = []

    print("\n  ── POR TICKER ──")
    for ticker in TICKERS:
        probs_va, probs_te, d = get_LR_probs(ticker, exp_id)
        if probs_va is None: continue
        thr = buscar_thresholds(probs_va, d["y_va"])
        preds_te = apply_filter(probs_te, thr["cb"], thr["cs"])
        met = metricas_full(d["y_te"], preds_te, r_forward=d["r_fwd_test"], split_name="test")
        print(f"  {ticker}: cb={thr['cb']:.2f} cs={thr['cs']:.2f} "
              f"f1={met['f1_macro']:.3f} sh={met.get('sharpe_test','-')}")
        resultados.append({
            "modelo": "LR-confidence-filter", "tipo": "por_ticker",
            "ticker": ticker, "experimento": exp_id,
            "conf_buy": thr["cb"], "conf_sell": thr["cs"],
            "test_f1_macro": met["f1_macro"],
            "test_f1_buy":   met["f1_buy"],
            "test_f1_hold":  met["f1_hold"],
            "test_f1_sell":  met["f1_sell"],
            "test_f1_buy_sell_avg": met["f1_buy_sell_avg"],
            "test_accuracy": met["accuracy"],
            "test_signal_buy":  met["signal_distribution"]["BUY"]["pct"],
            "test_signal_hold": met["signal_distribution"]["HOLD"]["pct"],
            "test_signal_sell": met["signal_distribution"]["SELL"]["pct"],
            "cumul_return_test":  met.get("cumul_return_test"),
            "return_vs_bh_test":  met.get("return_vs_bh_test"),
            "sharpe_test":        met.get("sharpe_test"),
            "max_drawdown_test":  met.get("max_drawdown_test"),
            "win_rate_test":      met.get("win_rate_test"),
            "profit_factor_test": met.get("profit_factor_test"),
        })

    # GLOBAL
    print("\n  ── GLOBAL ──")
    probs_va, probs_te, d = get_LR_probs(None, exp_id, tipo="global")
    if probs_va is None: return resultados
    thr = buscar_thresholds(probs_va, d["y_va"])
    preds_te = apply_filter(probs_te, thr["cb"], thr["cs"])
    met = metricas_full(d["y_te"], preds_te, r_forward=d["r_fwd_test"], split_name="test")
    print(f"  GLOBAL: cb={thr['cb']:.2f} cs={thr['cs']:.2f} "
          f"f1={met['f1_macro']:.3f} sh={met.get('sharpe_test','-')}")
    resultados.append({
        "modelo": "LR-confidence-filter", "tipo": "global",
        "ticker": "GLOBAL", "experimento": exp_id,
        "conf_buy": thr["cb"], "conf_sell": thr["cs"],
        "test_f1_macro": met["f1_macro"],
        "test_f1_buy":   met["f1_buy"],
        "test_f1_hold":  met["f1_hold"],
        "test_f1_sell":  met["f1_sell"],
        "test_f1_buy_sell_avg": met["f1_buy_sell_avg"],
        "test_accuracy": met["accuracy"],
        "test_signal_buy":  met["signal_distribution"]["BUY"]["pct"],
        "test_signal_hold": met["signal_distribution"]["HOLD"]["pct"],
        "test_signal_sell": met["signal_distribution"]["SELL"]["pct"],
        "cumul_return_test":  met.get("cumul_return_test"),
        "return_vs_bh_test":  met.get("return_vs_bh_test"),
        "sharpe_test":        met.get("sharpe_test"),
        "max_drawdown_test":  met.get("max_drawdown_test"),
        "win_rate_test":      met.get("win_rate_test"),
        "profit_factor_test": met.get("profit_factor_test"),
    })
    return resultados


def main():
    print("="*70)
    print("  LR CONFIDENCE FILTER — Solo trade cuando hay confianza")
    print("="*70)
    todos = []
    for exp_id in EXPERIMENTOS:
        res = correr_exp(exp_id)
        todos.extend(res)
        pd.DataFrame(todos).to_csv(RESULTS_CSV, index=False)

    df = pd.DataFrame(todos)
    print("\nGLOBAL F1 / Sharpe:")
    print(df[df["tipo"]=="global"][["experimento","test_f1_macro","sharpe_test",
          "test_signal_buy","test_signal_hold","test_signal_sell",
          "conf_buy","conf_sell"]].to_string(index=False))


if __name__ == "__main__":
    main()
