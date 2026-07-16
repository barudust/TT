"""
LightGBM — alternativa más rápida y a veces más precisa que XGBoost
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
                    cargar_dataset, cargar_global,
                    metricas_full, metricas_global_por_ticker,
                    guardar_json, imprimir_metricas, OUT_DIR)

import lightgbm as lgb
import optuna
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.metrics import f1_score

optuna.logging.set_verbosity(optuna.logging.WARNING)

OUT_LGB = OUT_DIR / "modelos_optimizados" / "lightgbm"
OUT_LGB.mkdir(parents=True, exist_ok=True)
RESULTS_CSV = OUT_LGB / "resultados_lgbm.csv"

N_TRIALS_TICKER = 30
N_TRIALS_GLOBAL = 50
SEEDS = [42, 1, 7]


def make_lgb(p, seed=42):
    return lgb.LGBMClassifier(
        n_estimators=p.get("n_estimators", 300),
        max_depth=p.get("max_depth", 6),
        learning_rate=p.get("learning_rate", 0.05),
        num_leaves=p.get("num_leaves", 31),
        min_child_samples=p.get("min_child_samples", 20),
        subsample=p.get("subsample", 0.8),
        colsample_bytree=p.get("colsample_bytree", 0.8),
        reg_alpha=p.get("reg_alpha", 0.0),
        reg_lambda=p.get("reg_lambda", 0.0),
        objective="multiclass", num_class=3, metric="multi_logloss",
        random_state=seed, n_jobs=-1, verbosity=-1,
        class_weight="balanced",
    )


def buscar_optuna(X_tr, y_tr, X_va, y_va, n_trials=N_TRIALS_TICKER, seed=42):
    def obj(t):
        p = {
            "n_estimators":      t.suggest_int("n_estimators", 200, 700),
            "max_depth":         t.suggest_int("max_depth", 4, 10),
            "num_leaves":        t.suggest_int("num_leaves", 15, 80),
            "learning_rate":     t.suggest_float("learning_rate", 0.01, 0.2, log=True),
            "min_child_samples": t.suggest_int("min_child_samples", 5, 50),
            "subsample":         t.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree":  t.suggest_float("colsample_bytree", 0.5, 1.0),
            "reg_alpha":         t.suggest_float("reg_alpha", 0.0, 2.0),
            "reg_lambda":        t.suggest_float("reg_lambda", 0.0, 2.0),
        }
        m = make_lgb(p, seed=seed)
        m.fit(X_tr, y_tr, eval_set=[(X_va, y_va)], callbacks=[lgb.early_stopping(20, verbose=False)])
        return 1.0 - f1_score(y_va, m.predict(X_va), average="macro", zero_division=0)
    s = optuna.create_study(direction="minimize", sampler=optuna.samplers.TPESampler(seed=seed))
    s.optimize(obj, n_trials=n_trials, show_progress_bar=False)
    return s.best_params


def soft_vote(models, X):
    return np.mean([m.predict_proba(X) for m in models], axis=0)


def fila(tipo, ticker, exp_id, met_val, met_test, n_feat):
    f = {
        "config_id": "LGBM-base", "modelo": "LightGBM",
        "tipo": tipo, "ticker": ticker, "experimento": exp_id,
        "n_features": n_feat, "n_seeds": len(SEEDS),
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


def correr_exp(exp_id):
    print(f"\n{'═'*70}\n  LightGBM  |  Exp {exp_id}\n{'═'*70}")
    out_dir = OUT_LGB / f"experimento_{exp_id}"
    out_dir.mkdir(parents=True, exist_ok=True)
    resultados = []

    print("\n  ── POR TICKER ──")
    for ticker in TICKERS:
        print(f"  >>> {ticker}", flush=True)
        d = cargar_dataset(ticker, exp_id)
        t0 = time.time()
        best = buscar_optuna(d["X_tr"], d["y_tr"], d["X_va"], d["y_va"], seed=42)
        print(f"    Optuna {N_TRIALS_TICKER}: {time.time()-t0:.0f}s", flush=True)

        X_full = np.vstack([d["X_tr"], d["X_va"]])
        y_full = np.concatenate([d["y_tr"], d["y_va"]])

        m_val_l, m_full_l = [], []
        for s in SEEDS:
            mv = make_lgb(best, seed=s)
            mv.fit(d["X_tr"], d["y_tr"], eval_set=[(d["X_va"], d["y_va"])],
                   callbacks=[lgb.early_stopping(20, verbose=False)])
            m_val_l.append(mv)
            mf = make_lgb(best, seed=s)
            mf.fit(X_full, y_full)
            m_full_l.append(mf)

        probs_va = soft_vote(m_val_l, d["X_va"])
        probs_te = soft_vote(m_full_l, d["X_te"])
        preds_va = probs_va.argmax(axis=1)
        preds_te = probs_te.argmax(axis=1)
        met_val  = metricas_full(d["y_va"], preds_va, split_name="val")
        met_test = metricas_full(d["y_te"], preds_te, r_forward=d["r_fwd_test"], split_name="test")
        imprimir_metricas(f"  {ticker} test", met_test)

        m_full_l[0].booster_.save_model(str(out_dir / f"{ticker}_modelo.txt"))
        meta = {"ticker": ticker, "experimento": exp_id, "tipo": "por_ticker",
                "modelo": "LightGBM", "best_params": best,
                "n_features": len(d["feat_cols"]), "n_seeds": len(SEEDS),
                "metricas_val": met_val, "metricas_test": met_test}
        guardar_json(meta, out_dir / f"{ticker}_metricas.json")
        resultados.append(fila("por_ticker", ticker, exp_id, met_val, met_test, len(d["feat_cols"])))

    # GLOBAL
    print("\n  ── GLOBAL ──")
    g = cargar_global(exp_id)
    t0 = time.time()
    best = buscar_optuna(g["X_tr"], g["y_tr"], g["X_va"], g["y_va"], n_trials=N_TRIALS_GLOBAL, seed=42)
    print(f"    Optuna global {N_TRIALS_GLOBAL}: {time.time()-t0:.0f}s", flush=True)

    X_full = np.vstack([g["X_tr"], g["X_va"]])
    y_full = np.concatenate([g["y_tr"], g["y_va"]])

    m_val_l, m_full_l = [], []
    for s in SEEDS:
        mv = make_lgb(best, seed=s)
        mv.fit(g["X_tr"], g["y_tr"], eval_set=[(g["X_va"], g["y_va"])],
               callbacks=[lgb.early_stopping(20, verbose=False)])
        m_val_l.append(mv)
        mf = make_lgb(best, seed=s)
        mf.fit(X_full, y_full)
        m_full_l.append(mf)

    probs_va = soft_vote(m_val_l, g["X_va"])
    probs_te = soft_vote(m_full_l, g["X_te"])
    preds_va = probs_va.argmax(axis=1)
    preds_te = probs_te.argmax(axis=1)
    met_val  = metricas_full(g["y_va"], preds_va, split_name="val")
    met_test = metricas_full(g["y_te"], preds_te, r_forward=g["r_fwd_test"], split_name="test")
    mt_pt = metricas_global_por_ticker(g["y_te"], preds_te, g["ticker_test"], g["r_fwd_test"])
    imprimir_metricas("  GLOBAL test", met_test)

    m_full_l[0].booster_.save_model(str(out_dir / "modelo_global.txt"))
    meta = {"ticker": "GLOBAL", "experimento": exp_id, "tipo": "global",
            "modelo": "LightGBM", "best_params": best,
            "n_features": len(g["feat_cols"]), "n_seeds": len(SEEDS),
            "metricas_val": met_val, "metricas_test": met_test,
            "metricas_test_por_ticker": mt_pt}
    guardar_json(meta, out_dir / "metricas_global.json")
    resultados.append(fila("global", "GLOBAL", exp_id, met_val, met_test, len(g["feat_cols"])))
    return resultados


def main():
    print("="*70)
    print("  LightGBM — alternative to XGBoost (often faster & similar accuracy)")
    print("="*70)
    todos = []
    t0 = time.time()
    for exp_id in EXPERIMENTOS:
        res = correr_exp(exp_id)
        todos.extend(res)
        pd.DataFrame(todos).to_csv(RESULTS_CSV, index=False)
    print(f"\nTiempo: {(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    main()
