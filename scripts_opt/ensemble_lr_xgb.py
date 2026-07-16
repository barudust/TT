"""
Simple ensemble — solo LR + XGB (los mejores). Búsqueda fina de peso.
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

import xgboost as xgb
from sklearn.metrics import f1_score

OUT_E = OUT_DIR / "ensemble_lr_xgb"
OUT_E.mkdir(parents=True, exist_ok=True)
RESULTS_CSV = OUT_E / "resultados_ensemble.csv"
MODELS_DIR = OUT_DIR / "modelos_optimizados"


def get_LR(ticker, exp_id, tipo="por_ticker"):
    p = (MODELS_DIR / "lr" / "LR-02-elasticnet-all" / f"experimento_{exp_id}" /
         ("modelo_global.pkl" if tipo == "global" else f"{ticker}_modelo.pkl"))
    if not p.exists(): return None, None, None
    with open(p, "rb") as f: o = pkl.load(f)
    d = cargar_dataset(ticker, exp_id, o["feat_cols"]) if tipo == "por_ticker" \
        else cargar_global(exp_id, o["feat_cols"])
    Xv = o["scaler"].transform(d["X_va"])
    Xt = o["scaler"].transform(d["X_te"])
    return o["model"].predict_proba(Xv), o["model"].predict_proba(Xt), d


def get_XGB(ticker, exp_id, tipo="por_ticker"):
    p = (MODELS_DIR / "xgboost" / "XGB-01-all" / f"experimento_{exp_id}" /
         ("modelo_global.json" if tipo == "global" else f"{ticker}_modelo.json"))
    if not p.exists(): return None, None, None
    m = xgb.XGBClassifier(); m.load_model(str(p))
    d = cargar_dataset(ticker, exp_id) if tipo == "por_ticker" else cargar_global(exp_id)
    return m.predict_proba(d["X_va"]), m.predict_proba(d["X_te"]), d


def buscar_peso(pv_lr, pv_xgb, y_va):
    mejor = {"w_lr": 1.0, "f1": -1}
    for w in np.linspace(0, 1, 21):  # 0, 0.05, 0.10, ..., 1.0
        avg = w * pv_lr + (1 - w) * pv_xgb
        pred = avg.argmax(axis=1)
        f1 = f1_score(y_va, pred, average="macro", zero_division=0)
        if f1 > mejor["f1"]:
            mejor = {"w_lr": w, "f1": f1}
    return mejor


def correr_exp(exp_id):
    print(f"\n{'═'*70}\n  Ensemble LR+XGB  |  Exp {exp_id}\n{'═'*70}")
    resultados = []

    print("\n  ── POR TICKER ──")
    for ticker in TICKERS:
        try:
            pv_lr, pt_lr, d_lr = get_LR(ticker, exp_id)
            pv_xg, pt_xg, d_xg = get_XGB(ticker, exp_id)
        except Exception as e:
            print(f"  {ticker}: err {e}"); continue
        if pv_lr is None or pv_xg is None: continue

        # Same indices (LR uses all data, XGB also uses all data)
        # But they may have small alignment due to dropna
        n_va = min(pv_lr.shape[0], pv_xg.shape[0])
        n_te = min(pt_lr.shape[0], pt_xg.shape[0])
        pv_lr = pv_lr[-n_va:]; pv_xg = pv_xg[-n_va:]
        pt_lr = pt_lr[-n_te:]; pt_xg = pt_xg[-n_te:]
        y_va = d_lr["y_va"][-n_va:]
        y_te = d_lr["y_te"][-n_te:]
        r_fwd = d_lr["r_fwd_test"][-n_te:] if d_lr["r_fwd_test"] is not None else None

        # Buscar peso
        res = buscar_peso(pv_lr, pv_xg, y_va)
        w = res["w_lr"]
        probs_te = w * pt_lr + (1 - w) * pt_xg
        preds_te = probs_te.argmax(axis=1)
        met = metricas_full(y_te, preds_te, r_forward=r_fwd, split_name="test")
        print(f"  {ticker}: w_lr={w:.2f} f1={met['f1_macro']:.3f} sh={met.get('sharpe_test','-')}")

        resultados.append({
            "modelo": "Ensemble-LR-XGB", "tipo": "por_ticker",
            "ticker": ticker, "experimento": exp_id,
            "w_lr": w, "w_xgb": 1 - w,
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
    try:
        pv_lr, pt_lr, d_lr = get_LR(None, exp_id, tipo="global")
        pv_xg, pt_xg, d_xg = get_XGB(None, exp_id, tipo="global")
    except Exception as e:
        print(f"  GLOBAL err {e}"); return resultados

    n_va = min(pv_lr.shape[0], pv_xg.shape[0])
    n_te = min(pt_lr.shape[0], pt_xg.shape[0])
    pv_lr = pv_lr[-n_va:]; pv_xg = pv_xg[-n_va:]
    pt_lr = pt_lr[-n_te:]; pt_xg = pt_xg[-n_te:]
    y_va = d_lr["y_va"][-n_va:]
    y_te = d_lr["y_te"][-n_te:]
    r_fwd = d_lr["r_fwd_test"][-n_te:]

    res = buscar_peso(pv_lr, pv_xg, y_va)
    w = res["w_lr"]
    probs_te = w * pt_lr + (1 - w) * pt_xg
    preds_te = probs_te.argmax(axis=1)
    met = metricas_full(y_te, preds_te, r_forward=r_fwd, split_name="test")
    print(f"  GLOBAL: w_lr={w:.2f} f1={met['f1_macro']:.3f} sh={met.get('sharpe_test','-')}")
    resultados.append({
        "modelo": "Ensemble-LR-XGB", "tipo": "global",
        "ticker": "GLOBAL", "experimento": exp_id,
        "w_lr": w, "w_xgb": 1 - w,
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
    print("  ENSEMBLE LR + XGBoost — Búsqueda fina de peso")
    print("="*70)
    todos = []
    for exp_id in EXPERIMENTOS:
        res = correr_exp(exp_id)
        todos.extend(res)
        pd.DataFrame(todos).to_csv(RESULTS_CSV, index=False)

    df = pd.DataFrame(todos)
    print("\nGLOBAL F1-macro test:")
    print(df[df["tipo"]=="global"][["experimento","test_f1_macro","w_lr","w_xgb"]].to_string(index=False))
    print("\nPor-ticker mean:")
    piv = df[df["tipo"]=="por_ticker"].pivot_table(
        index="experimento", values="test_f1_macro", aggfunc="mean").round(4)
    print(piv.to_string())


if __name__ == "__main__":
    main()
