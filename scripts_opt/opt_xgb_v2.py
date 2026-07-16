"""
OPT XGBoost V2 — Features expandidas (181) + multi-seed + Optuna acelerado
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("PYTHONUNBUFFERED", "1")
import sys, time, warnings, functools
import numpy as np
import pandas as pd
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception: pass
print = functools.partial(print, flush=True)
warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).parent))
from common import (TICKERS, EXPERIMENTOS, CLASES,
                    metricas_full, metricas_global_por_ticker,
                    guardar_json, imprimir_metricas, OUT_DIR)
from common_v2 import cargar_dataset_v2, cargar_global_v2

import xgboost as xgb
import optuna
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.metrics import f1_score

optuna.logging.set_verbosity(optuna.logging.WARNING)

OUT_XGB_V2 = OUT_DIR / "modelos_optimizados_v2" / "xgboost"
OUT_XGB_V2.mkdir(parents=True, exist_ok=True)
RESULTS_CSV = OUT_XGB_V2 / "resultados_xgb_v2.csv"

N_TRIALS_TICKER = 30
N_TRIALS_GLOBAL = 50
SEEDS = [42, 1, 7]
USE_GPU = True


def make_xgb(p, seed=42):
    k = dict(
        n_estimators=p.get("n_estimators", 300),
        max_depth=p.get("max_depth", 5),
        learning_rate=p.get("learning_rate", 0.05),
        subsample=p.get("subsample", 0.8),
        colsample_bytree=p.get("colsample_bytree", 0.8),
        min_child_weight=p.get("min_child_weight", 3),
        gamma=p.get("gamma", 0.1),
        reg_alpha=p.get("reg_alpha", 0.1),
        reg_lambda=p.get("reg_lambda", 1.0),
        objective="multi:softprob", num_class=3, eval_metric="mlogloss",
        tree_method="hist", random_state=seed, n_jobs=-1, verbosity=0)
    if USE_GPU:
        k["device"] = "cuda"
    return xgb.XGBClassifier(**k)


def buscar_optuna(X_tr, y_tr, X_va, y_va, n_trials=N_TRIALS_TICKER, seed=42):
    sw = compute_sample_weight("balanced", y=y_tr)
    def obj(t):
        p = {
            "n_estimators":     t.suggest_int("n_estimators", 200, 700),
            "max_depth":        t.suggest_int("max_depth", 3, 8),
            "learning_rate":    t.suggest_float("learning_rate", 0.01, 0.2, log=True),
            "subsample":        t.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": t.suggest_float("colsample_bytree", 0.4, 1.0),
            "min_child_weight": t.suggest_int("min_child_weight", 1, 10),
            "gamma":            t.suggest_float("gamma", 0.0, 1.5),
            "reg_alpha":        t.suggest_float("reg_alpha", 0.0, 2.5),
            "reg_lambda":       t.suggest_float("reg_lambda", 0.5, 4.0),
        }
        m = make_xgb(p, seed=seed)
        m.fit(X_tr, y_tr, sample_weight=sw,
              eval_set=[(X_va, y_va)], verbose=False)
        return 1.0 - f1_score(y_va, m.predict(X_va), average="macro", zero_division=0)
    s = optuna.create_study(direction="minimize", sampler=optuna.samplers.TPESampler(seed=seed))
    s.optimize(obj, n_trials=n_trials, show_progress_bar=False)
    return s.best_params


def soft_vote(models, X):
    return np.mean([m.predict_proba(X) for m in models], axis=0)


def calibrar(probs_va, y_va):
    mejor = {"f1": -1, "f_buy": 1.0, "f_sell": 1.0}
    for fb in [0.6, 0.8, 1.0, 1.2, 1.5, 1.8]:
        for fs in [0.6, 0.8, 1.0, 1.2, 1.5, 1.8]:
            p = probs_va.copy()
            p[:, 2] *= fb; p[:, 0] *= fs
            f1 = f1_score(y_va, p.argmax(axis=1), average="macro", zero_division=0)
            if f1 > mejor["f1"]:
                mejor = {"f1": f1, "f_buy": fb, "f_sell": fs}
    return mejor


def aplicar(probs, fb, fs):
    p = probs.copy(); p[:, 2] *= fb; p[:, 0] *= fs
    return p.argmax(axis=1)


def fila(config_id, tipo, ticker, exp_id, met_val, met_test, n_feat, calib):
    f = {
        "config_id": config_id, "modelo": "XGBoost",
        "tipo": tipo, "ticker": ticker, "experimento": exp_id,
        "n_features": n_feat, "n_seeds": len(SEEDS),
        "calib_f_buy":  calib.get("f_buy")  if calib else None,
        "calib_f_sell": calib.get("f_sell") if calib else None,
        "val_f1_macro":  met_val["f1_macro"],
        "val_f1_buy":    met_val["f1_buy"],
        "val_f1_sell":   met_val["f1_sell"],
        "test_f1_macro": met_test["f1_macro"],
        "test_f1_buy":   met_test["f1_buy"],
        "test_f1_hold":  met_test["f1_hold"],
        "test_f1_sell":  met_test["f1_sell"],
        "test_f1_buy_sell_avg": met_test["f1_buy_sell_avg"],
        "test_accuracy": met_test["accuracy"],
        "test_signal_buy":  met_test["signal_distribution"]["BUY"]["pct"],
        "test_signal_hold": met_test["signal_distribution"]["HOLD"]["pct"],
        "test_signal_sell": met_test["signal_distribution"]["SELL"]["pct"],
    }
    for k in ["cumul_return_test", "return_vs_bh_test", "sharpe_test",
              "max_drawdown_test", "win_rate_test", "profit_factor_test"]:
        f[k] = met_test.get(k)
    return f


def correr_exp(exp_id, config_id="XGBv2-calib"):
    print(f"\n{'═'*70}\n  XGB v2 calib  |  Exp {exp_id}\n{'═'*70}")
    out_dir = OUT_XGB_V2 / config_id / f"experimento_{exp_id}"
    out_dir.mkdir(parents=True, exist_ok=True)
    resultados = []

    print("\n  ── POR TICKER ──")
    for ticker in TICKERS:
        print(f"\n  >>> {ticker}", flush=True)
        d = cargar_dataset_v2(ticker, exp_id)
        t0 = time.time()
        best = buscar_optuna(d["X_tr"], d["y_tr"], d["X_va"], d["y_va"], seed=42)
        print(f"      Optuna {N_TRIALS_TICKER}: {time.time()-t0:.0f}s", flush=True)

        X_full = np.vstack([d["X_tr"], d["X_va"]])
        y_full = np.concatenate([d["y_tr"], d["y_va"]])
        sw_full = compute_sample_weight("balanced", y=y_full)
        sw_tr   = compute_sample_weight("balanced", y=d["y_tr"])

        m_val_l, m_full_l = [], []
        for s in SEEDS:
            mv = make_xgb(best, seed=s)
            mv.fit(d["X_tr"], d["y_tr"], sample_weight=sw_tr,
                   eval_set=[(d["X_va"], d["y_va"])], verbose=False)
            m_val_l.append(mv)
            mf = make_xgb(best, seed=s)
            mf.fit(X_full, y_full, sample_weight=sw_full, verbose=False)
            m_full_l.append(mf)

        probs_va = soft_vote(m_val_l, d["X_va"])
        probs_te = soft_vote(m_full_l, d["X_te"])

        calib = calibrar(probs_va, d["y_va"])
        preds_va = aplicar(probs_va, calib["f_buy"], calib["f_sell"])
        preds_te = aplicar(probs_te, calib["f_buy"], calib["f_sell"])

        met_val  = metricas_full(d["y_va"], preds_va, split_name="val")
        met_test = metricas_full(d["y_te"], preds_te, r_forward=d["r_fwd_test"], split_name="test")
        imprimir_metricas(f"{ticker} val ", met_val)
        imprimir_metricas(f"{ticker} test", met_test)

        m_full_l[0].save_model(str(out_dir / f"{ticker}_modelo.json"))
        meta = {"ticker": ticker, "experimento": exp_id, "tipo": "por_ticker",
                "config_id": config_id, "modelo": "XGBoost",
                "best_params": best, "calib": calib,
                "n_features": len(d["feat_cols"]), "n_seeds": len(SEEDS),
                "metricas_val": met_val, "metricas_test": met_test}
        guardar_json(meta, out_dir / f"{ticker}_metricas.json")
        resultados.append(fila(config_id, "por_ticker", ticker, exp_id, met_val, met_test, len(d["feat_cols"]), calib))

    # GLOBAL
    print("\n  ── GLOBAL ──")
    g = cargar_global_v2(exp_id)
    t0 = time.time()
    best = buscar_optuna(g["X_tr"], g["y_tr"], g["X_va"], g["y_va"], n_trials=N_TRIALS_GLOBAL, seed=42)
    print(f"      Optuna global: {time.time()-t0:.0f}s", flush=True)

    X_full = np.vstack([g["X_tr"], g["X_va"]])
    y_full = np.concatenate([g["y_tr"], g["y_va"]])
    sw_full = compute_sample_weight("balanced", y=y_full)
    sw_tr   = compute_sample_weight("balanced", y=g["y_tr"])

    m_val_l, m_full_l = [], []
    for s in SEEDS:
        mv = make_xgb(best, seed=s)
        mv.fit(g["X_tr"], g["y_tr"], sample_weight=sw_tr,
               eval_set=[(g["X_va"], g["y_va"])], verbose=False)
        m_val_l.append(mv)
        mf = make_xgb(best, seed=s)
        mf.fit(X_full, y_full, sample_weight=sw_full, verbose=False)
        m_full_l.append(mf)

    probs_va = soft_vote(m_val_l, g["X_va"])
    probs_te = soft_vote(m_full_l, g["X_te"])
    calib = calibrar(probs_va, g["y_va"])
    preds_va = aplicar(probs_va, calib["f_buy"], calib["f_sell"])
    preds_te = aplicar(probs_te, calib["f_buy"], calib["f_sell"])

    met_val  = metricas_full(g["y_va"], preds_va, split_name="val")
    met_test = metricas_full(g["y_te"], preds_te, r_forward=g["r_fwd_test"], split_name="test")
    mt_pt = metricas_global_por_ticker(g["y_te"], preds_te, g["ticker_test"], g["r_fwd_test"])
    imprimir_metricas("GLOBAL val ", met_val)
    imprimir_metricas("GLOBAL test", met_test)

    m_full_l[0].save_model(str(out_dir / "modelo_global.json"))
    meta = {"ticker": "GLOBAL", "experimento": exp_id, "tipo": "global",
            "config_id": config_id, "modelo": "XGBoost",
            "best_params": best, "calib": calib,
            "n_features": len(g["feat_cols"]), "n_seeds": len(SEEDS),
            "metricas_val": met_val, "metricas_test": met_test,
            "metricas_test_por_ticker": mt_pt}
    guardar_json(meta, out_dir / "metricas_global.json")
    resultados.append(fila(config_id, "global", "GLOBAL", exp_id, met_val, met_test, len(g["feat_cols"]), calib))

    return resultados


def pipeline():
    print("="*70)
    print("  XGB V2 — Features expandidas (181) + multi-seed + threshold calib")
    print("="*70)
    if RESULTS_CSV.exists():
        df_prev = pd.read_csv(RESULTS_CSV)
        df_prev = df_prev[df_prev["config_id"] != "XGBv2-calib"]
        todos = df_prev.to_dict("records")
    else:
        todos = []
    t0 = time.time()
    for exp_id in EXPERIMENTOS:
        res = correr_exp(exp_id)
        todos.extend(res)
        pd.DataFrame(todos).to_csv(RESULTS_CSV, index=False)
    print(f"\nTiempo: {(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    pipeline()
