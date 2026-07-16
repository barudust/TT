"""
================================================================================
OPTIMIZACIÓN LR V2 — Features expandidas (181) + threshold calibration
================================================================================
Mejoras vs v1:
  - Usa dataset v2 con 181 features (rolling z-scores, lags, interacciones)
  - Threshold calibration por clase para corregir sesgo a SELL/HOLD
  - Grid search más amplio
  - Soft voting de probabilidades multi-seed (vs majority voting)
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("PYTHONUNBUFFERED", "1")
import sys
import time
import json
import pickle
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
warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).parent))
from common import (TICKERS, EXPERIMENTOS, CLASES, NOMBRES,
                    metricas_full, metricas_global_por_ticker,
                    guardar_json, imprimir_metricas, OUT_DIR)
from common_v2 import cargar_dataset_v2, cargar_global_v2

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import f1_score

OUT_LR_V2 = OUT_DIR / "modelos_optimizados_v2" / "lr"
OUT_LR_V2.mkdir(parents=True, exist_ok=True)
RESULTS_CSV = OUT_LR_V2 / "resultados_lr_v2.csv"

C_GRID = [0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0]
C_GRID_SAGA = [0.01, 0.1, 1.0, 10.0]
L1_RATIOS = [0.3, 0.5, 0.7]
SEEDS = [42, 1, 7, 2024, 100]

CONFIGS = {
    "LRv2-elasticnet-calib": dict(penalty="elasticnet", calib=True, scaler="robust"),
    "LRv2-l1-calib":         dict(penalty="l1",         calib=True, scaler="robust"),
    "LRv2-l2-calib":         dict(penalty="l2",         calib=True, scaler="standard"),
    "LRv2-elasticnet":       dict(penalty="elasticnet", calib=False, scaler="robust"),
}


def make_model(penalty, C, l1_ratio=None, seed=42):
    if penalty == "elasticnet":
        return LogisticRegression(
            penalty="elasticnet", solver="saga", l1_ratio=l1_ratio,
            C=C, max_iter=2000, class_weight="balanced",
            random_state=seed, n_jobs=-1, tol=1e-3)
    elif penalty == "l1":
        return LogisticRegression(
            penalty="l1", solver="saga", C=C, max_iter=2000,
            class_weight="balanced", random_state=seed, n_jobs=-1, tol=1e-3)
    else:
        return LogisticRegression(
            penalty="l2", solver="lbfgs", C=C, max_iter=2000,
            class_weight="balanced", random_state=seed, n_jobs=-1)


def buscar_hp(X_tr, y_tr, X_va, y_va, penalty, seed=42):
    mejor = {"f1": -1, "C": None, "l1_ratio": None}
    if penalty == "elasticnet":
        combos = [(c, r) for c in C_GRID_SAGA for r in L1_RATIOS]
    elif penalty == "l1":
        combos = [(c, None) for c in C_GRID_SAGA]
    else:
        combos = [(c, None) for c in C_GRID]

    for C, l1r in combos:
        try:
            m = make_model(penalty, C, l1r, seed=seed)
            m.fit(X_tr, y_tr)
            f1 = f1_score(y_va, m.predict(X_va), average="macro", zero_division=0)
            if f1 > mejor["f1"]:
                mejor = {"f1": f1, "C": C, "l1_ratio": l1r}
        except Exception as e:
            print(f"      ⚠ {penalty} C={C} l1={l1r}: {e}")
    return mejor


def soft_vote_probs(models, X):
    probs = np.mean([m.predict_proba(X) for m in models], axis=0)
    return probs


def calibrar_thresholds(probs_va, y_va):
    """Grid search restringido para evitar colapso de clases.
    Solo acepta calibraciones donde TODAS las clases predichas estén entre 15% y 60%
    (distribución real es ~30/40/30, así que esto es un constraint razonable).
    """
    mejor = {"f1": -1, "f_buy": 1.0, "f_sell": 1.0}
    factores = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
    n = len(y_va)
    for fb in factores:
        for fs in factores:
            p = probs_va.copy()
            p[:, 2] *= fb
            p[:, 0] *= fs
            pred = p.argmax(axis=1)
            # Constraint: cada clase entre 15% y 60%
            counts = np.bincount(pred, minlength=3)
            pcts = counts / n
            if pcts.min() < 0.15 or pcts.max() > 0.60:
                continue
            f1 = f1_score(y_va, pred, average="macro", zero_division=0)
            if f1 > mejor["f1"]:
                mejor = {"f1": f1, "f_buy": fb, "f_sell": fs}
    # Si no encontró calibración válida, usar identidad
    if mejor["f1"] < 0:
        mejor = {"f1": f1_score(y_va, probs_va.argmax(axis=1), average="macro", zero_division=0),
                 "f_buy": 1.0, "f_sell": 1.0}
    return mejor


def aplicar_thresholds(probs, f_buy, f_sell):
    p = probs.copy()
    p[:, 2] *= f_buy
    p[:, 0] *= f_sell
    return p.argmax(axis=1)


def fila_resultado(config_id, tipo, ticker, exp_id, met_val, met_test, hp,
                   n_features, n_seeds, calib_info):
    fila = {
        "config_id": config_id, "modelo": "LogisticRegression",
        "tipo": tipo, "ticker": ticker, "experimento": exp_id,
        "n_features": n_features, "n_seeds": n_seeds,
        "C": hp.get("C"), "l1_ratio": hp.get("l1_ratio"),
        "calib_f_buy": calib_info.get("f_buy") if calib_info else None,
        "calib_f_sell": calib_info.get("f_sell") if calib_info else None,
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
        fila[k] = met_test.get(k)
    return fila


def correr_config(config_id, config, exp_id):
    print(f"\n{'═'*70}")
    print(f"  {config_id}  |  Exp {exp_id}  |  penalty={config['penalty']}  "
          f"calib={config['calib']}  scaler={config['scaler']}")
    print(f"{'═'*70}")

    out_dir = OUT_LR_V2 / config_id / f"experimento_{exp_id}"
    out_dir.mkdir(parents=True, exist_ok=True)
    resultados = []

    # ────────── POR TICKER ──────────
    print("\n  ── POR TICKER ─────────────────────────")
    for ticker in TICKERS:
        d = cargar_dataset_v2(ticker, exp_id)
        n_feat = len(d["feat_cols"])

        sc = RobustScaler() if config["scaler"] == "robust" else StandardScaler()
        X_tr = sc.fit_transform(d["X_tr"])
        X_va = sc.transform(d["X_va"])
        X_te = sc.transform(d["X_te"])

        hp = buscar_hp(X_tr, d["y_tr"], X_va, d["y_va"], config["penalty"], seed=42)
        if hp["C"] is None:
            print(f"  {ticker}: ⚠ no converge")
            continue

        # Multi-seed
        X_full = np.vstack([X_tr, X_va])
        y_full = np.concatenate([d["y_tr"], d["y_va"]])

        # Modelos de val (entrenados solo con train) para calibrar
        models_val, models_full = [], []
        for s in SEEDS:
            m_val = make_model(config["penalty"], hp["C"], hp.get("l1_ratio"), seed=s)
            m_val.fit(X_tr, d["y_tr"])
            models_val.append(m_val)
            m_full = make_model(config["penalty"], hp["C"], hp.get("l1_ratio"), seed=s)
            m_full.fit(X_full, y_full)
            models_full.append(m_full)

        probs_va = soft_vote_probs(models_val, X_va)
        probs_te = soft_vote_probs(models_full, X_te)

        # Threshold calibration
        if config["calib"]:
            calib = calibrar_thresholds(probs_va, d["y_va"])
            preds_va = aplicar_thresholds(probs_va, calib["f_buy"], calib["f_sell"])
            preds_te = aplicar_thresholds(probs_te, calib["f_buy"], calib["f_sell"])
        else:
            calib = None
            preds_va = probs_va.argmax(axis=1)
            preds_te = probs_te.argmax(axis=1)

        met_val  = metricas_full(d["y_va"], preds_va, split_name="val")
        met_test = metricas_full(d["y_te"], preds_te, r_forward=d["r_fwd_test"], split_name="test")

        imprimir_metricas(f"{ticker} val ", met_val)
        imprimir_metricas(f"{ticker} test", met_test)

        with open(out_dir / f"{ticker}_modelo.pkl", "wb") as f:
            pickle.dump({"model": models_full[0], "scaler": sc, "hp": hp,
                         "calib": calib, "feat_cols": d["feat_cols"]}, f)

        meta = {
            "ticker": ticker, "experimento": exp_id, "tipo": "por_ticker",
            "config_id": config_id, "modelo": "LogisticRegression",
            "hp": hp, "calib": calib, "n_features": n_feat, "n_seeds": len(SEEDS),
            "metricas_val":  met_val, "metricas_test": met_test,
        }
        guardar_json(meta, out_dir / f"{ticker}_metricas.json")

        resultados.append(fila_resultado(
            config_id, "por_ticker", ticker, exp_id,
            met_val, met_test, hp, n_feat, len(SEEDS), calib))

    # ────────── GLOBAL ──────────
    print("\n  ── GLOBAL ─────────────────────────")
    g = cargar_global_v2(exp_id)
    n_feat = len(g["feat_cols"])

    sc = RobustScaler() if config["scaler"] == "robust" else StandardScaler()
    X_tr = sc.fit_transform(g["X_tr"])
    X_va = sc.transform(g["X_va"])
    X_te = sc.transform(g["X_te"])

    hp = buscar_hp(X_tr, g["y_tr"], X_va, g["y_va"], config["penalty"], seed=42)
    if hp["C"] is None:
        print("  GLOBAL: ⚠ no converge")
        return resultados

    X_full = np.vstack([X_tr, X_va])
    y_full = np.concatenate([g["y_tr"], g["y_va"]])

    models_val, models_full = [], []
    for s in SEEDS:
        m_val = make_model(config["penalty"], hp["C"], hp.get("l1_ratio"), seed=s)
        m_val.fit(X_tr, g["y_tr"])
        models_val.append(m_val)
        m_full = make_model(config["penalty"], hp["C"], hp.get("l1_ratio"), seed=s)
        m_full.fit(X_full, y_full)
        models_full.append(m_full)

    probs_va = soft_vote_probs(models_val, X_va)
    probs_te = soft_vote_probs(models_full, X_te)

    if config["calib"]:
        calib = calibrar_thresholds(probs_va, g["y_va"])
        preds_va = aplicar_thresholds(probs_va, calib["f_buy"], calib["f_sell"])
        preds_te = aplicar_thresholds(probs_te, calib["f_buy"], calib["f_sell"])
    else:
        calib = None
        preds_va = probs_va.argmax(axis=1)
        preds_te = probs_te.argmax(axis=1)

    met_val  = metricas_full(g["y_va"], preds_va, split_name="val")
    met_test = metricas_full(g["y_te"], preds_te, r_forward=g["r_fwd_test"], split_name="test")
    met_por_ticker = metricas_global_por_ticker(
        g["y_te"], preds_te, g["ticker_test"], g["r_fwd_test"])

    imprimir_metricas("GLOBAL val ", met_val)
    imprimir_metricas("GLOBAL test", met_test)

    with open(out_dir / "modelo_global.pkl", "wb") as f:
        pickle.dump({"model": models_full[0], "scaler": sc, "hp": hp,
                     "calib": calib, "feat_cols": g["feat_cols"]}, f)
    meta = {
        "ticker": "GLOBAL", "experimento": exp_id, "tipo": "global",
        "config_id": config_id, "modelo": "LogisticRegression",
        "hp": hp, "calib": calib, "n_features": n_feat, "n_seeds": len(SEEDS),
        "metricas_val":  met_val, "metricas_test": met_test,
        "metricas_test_por_ticker": met_por_ticker,
    }
    guardar_json(meta, out_dir / "metricas_global.json")

    resultados.append(fila_resultado(
        config_id, "global", "GLOBAL", exp_id,
        met_val, met_test, hp, n_feat, len(SEEDS), calib))
    return resultados


def pipeline(configs_a_correr=None):
    print("="*70)
    print("  OPT LR V2 — Features expandidas (181) + threshold calibration")
    print("="*70)

    if configs_a_correr is None:
        configs_a_correr = list(CONFIGS.keys())

    if RESULTS_CSV.exists():
        df_prev = pd.read_csv(RESULTS_CSV)
        df_prev = df_prev[~df_prev["config_id"].isin(configs_a_correr)]
        todos = df_prev.to_dict("records")
    else:
        todos = []

    t0 = time.time()
    for cfg_id in configs_a_correr:
        if cfg_id not in CONFIGS:
            continue
        cfg = CONFIGS[cfg_id]
        for exp_id in EXPERIMENTOS:
            res = correr_config(cfg_id, cfg, exp_id)
            todos.extend(res)
            pd.DataFrame(todos).to_csv(RESULTS_CSV, index=False)

    print(f"\n{'='*70}\nTiempo: {(time.time()-t0)/60:.1f} min  →  {RESULTS_CSV}\n{'='*70}")

    if todos:
        df = pd.DataFrame(todos)
        for tipo in ["global", "por_ticker"]:
            sub = df[df["tipo"] == tipo]
            if sub.empty: continue
            piv = sub.pivot_table(index="config_id", columns="experimento",
                                  values="test_f1_macro", aggfunc="mean")
            print(f"\n  --- {tipo.upper()} ---")
            print(piv.round(4).to_string())


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--configs", nargs="+", default=None)
    args = p.parse_args()
    pipeline(configs_a_correr=args.configs)
