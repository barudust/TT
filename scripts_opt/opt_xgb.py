"""
================================================================================
OPTIMIZACIÓN — XGBOOST
================================================================================
Estrategia:
  - Búsqueda Optuna agresiva (100 trials por config)
  - Multi-seed averaging para reducir varianza
  - Probar varios sets de features (todas vs. consenso vs. importancia)
  - GPU acelerado
  - Soft voting de probabilidades entre seeds
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("PYTHONUNBUFFERED", "1")
import sys
import time
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

sys.path.insert(0, str(Path(__file__).parent))
from common import (TICKERS, EXPERIMENTOS, CLASES,
                    cargar_dataset, cargar_global,
                    metricas_full, metricas_global_por_ticker,
                    guardar_json, append_resultado, imprimir_metricas, OUT_DIR)

import xgboost as xgb
import optuna
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.metrics import f1_score

warnings.filterwarnings("ignore")
optuna.logging.set_verbosity(optuna.logging.WARNING)

# ════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ════════════════════════════════════════════════════════════════════════════

OUT_XGB = OUT_DIR / "modelos_optimizados" / "xgboost"
OUT_XGB.mkdir(parents=True, exist_ok=True)
RESULTS_CSV = OUT_XGB / "resultados_xgb_opt.csv"

N_TRIALS_PER_TICKER = 25   # por ticker (reducido para mayor velocidad)
N_TRIALS_GLOBAL     = 40   # global
SEEDS               = [42, 1, 7]

USE_GPU = True

CONFIGS = {
    "XGB-01-all":      dict(features="all",     monotonic=False),
    "XGB-02-top30":    dict(features="top30",   monotonic=False),
    "XGB-03-all-mono": dict(features="all",     monotonic=True),
}


# ════════════════════════════════════════════════════════════════════════════
# MODELO
# ════════════════════════════════════════════════════════════════════════════

def make_xgb(params, seed=42, monotonic_constraints=None):
    kwargs = dict(
        n_estimators      = params.get("n_estimators", 300),
        max_depth         = params.get("max_depth", 5),
        learning_rate     = params.get("learning_rate", 0.05),
        subsample         = params.get("subsample", 0.8),
        colsample_bytree  = params.get("colsample_bytree", 0.8),
        min_child_weight  = params.get("min_child_weight", 3),
        gamma             = params.get("gamma", 0.1),
        reg_alpha         = params.get("reg_alpha", 0.1),
        reg_lambda        = params.get("reg_lambda", 1.0),
        objective         = "multi:softprob",
        num_class         = 3,
        eval_metric       = "mlogloss",
        tree_method       = "hist",
        random_state      = seed,
        n_jobs            = -1,
        verbosity         = 0,
    )
    if USE_GPU:
        kwargs["device"] = "cuda"
    if monotonic_constraints is not None:
        kwargs["monotone_constraints"] = monotonic_constraints
    return xgb.XGBClassifier(**kwargs)


def buscar_optuna(X_tr, y_tr, X_va, y_va, n_trials, seed=42, monotonic=None):
    pesos_tr = compute_sample_weight("balanced", y=y_tr)
    def objective(trial):
        p = {
            "n_estimators":     trial.suggest_int("n_estimators", 150, 800),
            "max_depth":        trial.suggest_int("max_depth", 3, 9),
            "learning_rate":    trial.suggest_float("learning_rate", 0.005, 0.3, log=True),
            "subsample":        trial.suggest_float("subsample", 0.55, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.4, 1.0),
            "min_child_weight": trial.suggest_int("min_child_weight", 1, 12),
            "gamma":            trial.suggest_float("gamma", 0.0, 2.0),
            "reg_alpha":        trial.suggest_float("reg_alpha", 0.0, 3.0),
            "reg_lambda":       trial.suggest_float("reg_lambda", 0.1, 5.0),
        }
        m = make_xgb(p, seed=seed, monotonic_constraints=monotonic)
        m.fit(X_tr, y_tr, sample_weight=pesos_tr,
              eval_set=[(X_va, y_va)], verbose=False)
        return 1.0 - f1_score(y_va, m.predict(X_va), average="macro", zero_division=0)

    estudio = optuna.create_study(direction="minimize",
                                   sampler=optuna.samplers.TPESampler(seed=seed))
    estudio.optimize(objective, n_trials=n_trials, show_progress_bar=False)
    return estudio.best_params


def predecir_soft_vote(modelos, X):
    """Promedia probabilidades de varios modelos."""
    probs = np.mean([m.predict_proba(X) for m in modelos], axis=0)
    return probs.argmax(axis=1), probs


def filtrar_features(feat_cols, feat_sel):
    if feat_sel == "all":
        return feat_cols
    if feat_sel == "top30":
        # Lista heurística de features que tienden a aparecer en SHAP top
        prefs = [
            "SP500_ret", "SP500_mom20", "VIX", "VIX_change", "VIX_norm",
            "ret_1d", "ret_2d", "ret_3d", "ret_5d", "ret_10d",
            "mom_5d", "mom_10d", "mom_20d", "mom_60d",
            "dist_ma10", "dist_ma20", "dist_ma50",
            "atr_14", "atr_norm", "vol_5d", "vol_10d", "vol_20d",
            "vol_ratio_5_20",
            "rsi_7", "rsi_14", "stoch_k", "stoch_d", "stoch_diff",
            "williams_r", "macd_hist", "cmf_20", "mfi_14",
            "hl_ratio", "cuerpo_rel", "gap_apertura", "sombra_sup", "sombra_inf",
            "obv_pendiente", "vol_log", "vol_ratio",
        ]
        return [f for f in prefs if f in feat_cols][:30]
    return feat_cols


# ════════════════════════════════════════════════════════════════════════════
# UN EXPERIMENTO COMPLETO
# ════════════════════════════════════════════════════════════════════════════

def correr_config(config_id, config, exp_id):
    print(f"\n{'═'*70}")
    print(f"  Config: {config_id}  |  Exp {exp_id}  |  features={config['features']}  monotonic={config['monotonic']}")
    print(f"{'═'*70}")

    out_dir = OUT_XGB / config_id / f"experimento_{exp_id}"
    out_dir.mkdir(parents=True, exist_ok=True)

    resultados = []

    # ────────────────────── POR TICKER ──────────────────────
    print(f"\n  ── POR TICKER ─────────────────────────")
    for ticker in TICKERS:
        print(f"\n  >>> {ticker} <<<")
        d = cargar_dataset(ticker, exp_id)
        feat_cols = filtrar_features(d["feat_cols"], config["features"])
        d = cargar_dataset(ticker, exp_id, feat_cols)
        X_tr, y_tr = d["X_tr"], d["y_tr"]
        X_va, y_va = d["X_va"], d["y_va"]
        X_te, y_te = d["X_te"], d["y_te"]

        t0 = time.time()
        best = buscar_optuna(X_tr, y_tr, X_va, y_va, n_trials=N_TRIALS_PER_TICKER, seed=42)
        t_opt = time.time() - t0
        print(f"      Optuna {N_TRIALS_PER_TICKER} trials: {t_opt:.0f}s")

        # Multi-seed entrenamiento
        X_full = np.vstack([X_tr, X_va])
        y_full = np.concatenate([y_tr, y_va])
        pesos_full = compute_sample_weight("balanced", y=y_full)
        pesos_tr   = compute_sample_weight("balanced", y=y_tr)

        modelos_full, modelos_val = [], []
        for s in SEEDS:
            m_full = make_xgb(best, seed=s)
            m_full.fit(X_full, y_full, sample_weight=pesos_full, verbose=False)
            modelos_full.append(m_full)

            m_val = make_xgb(best, seed=s)
            m_val.fit(X_tr, y_tr, sample_weight=pesos_tr,
                      eval_set=[(X_va, y_va)], verbose=False)
            modelos_val.append(m_val)

        preds_va, _ = predecir_soft_vote(modelos_val, X_va)
        preds_te, _ = predecir_soft_vote(modelos_full, X_te)

        met_val  = metricas_full(y_va, preds_va, split_name="val")
        met_test = metricas_full(y_te, preds_te, r_forward=d["r_fwd_test"], split_name="test")

        imprimir_metricas(f"{ticker} val  (opt {t_opt:.0f}s)", met_val)
        imprimir_metricas(f"{ticker} test", met_test)

        # Guardar primer modelo (representativo)
        modelos_full[0].save_model(str(out_dir / f"{ticker}_modelo.json"))

        meta = {
            "ticker": ticker, "experimento": exp_id, "tipo": "por_ticker",
            "config_id": config_id, "modelo": "XGBoost",
            "best_params": best, "n_features": len(feat_cols),
            "n_seeds": len(SEEDS), "features": feat_cols,
            "metricas_val":  met_val,
            "metricas_test": met_test,
        }
        guardar_json(meta, out_dir / f"{ticker}_metricas.json")

        fila = {
            "config_id": config_id, "modelo": "XGBoost", "tipo": "por_ticker",
            "ticker": ticker, "experimento": exp_id,
            "n_features": len(feat_cols), "n_seeds": len(SEEDS),
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
            fila[k] = met_test.get(k, None)
        resultados.append(fila)

    # ────────────────────── GLOBAL ──────────────────────
    print(f"\n  ── GLOBAL ─────────────────────────")
    d_aux = cargar_dataset(TICKERS[0], exp_id)
    feat_cols = filtrar_features(d_aux["feat_cols"], config["features"])
    g = cargar_global(exp_id, feat_cols)
    X_tr, y_tr = g["X_tr"], g["y_tr"]
    X_va, y_va = g["X_va"], g["y_va"]
    X_te, y_te = g["X_te"], g["y_te"]

    t0 = time.time()
    best = buscar_optuna(X_tr, y_tr, X_va, y_va, n_trials=N_TRIALS_GLOBAL, seed=42)
    t_opt = time.time() - t0
    print(f"  Optuna global: {t_opt:.0f}s — best_params={best}")

    X_full = np.vstack([X_tr, X_va])
    y_full = np.concatenate([y_tr, y_va])
    pesos_full = compute_sample_weight("balanced", y=y_full)
    pesos_tr   = compute_sample_weight("balanced", y=y_tr)

    modelos_full, modelos_val = [], []
    for s in SEEDS:
        m_full = make_xgb(best, seed=s)
        m_full.fit(X_full, y_full, sample_weight=pesos_full, verbose=False)
        modelos_full.append(m_full)
        m_val = make_xgb(best, seed=s)
        m_val.fit(X_tr, y_tr, sample_weight=pesos_tr,
                  eval_set=[(X_va, y_va)], verbose=False)
        modelos_val.append(m_val)

    preds_va, _ = predecir_soft_vote(modelos_val, X_va)
    preds_te, probs_te = predecir_soft_vote(modelos_full, X_te)

    met_val  = metricas_full(y_va, preds_va, split_name="val")
    met_test = metricas_full(y_te, preds_te, r_forward=g["r_fwd_test"], split_name="test")
    met_por_ticker = metricas_global_por_ticker(
        y_te, preds_te, g["ticker_test"], g["r_fwd_test"])

    imprimir_metricas("GLOBAL val ", met_val)
    imprimir_metricas("GLOBAL test", met_test)
    print("  -- Por ticker en GLOBAL test --")
    for tk, m in met_por_ticker.items():
        imprimir_metricas(f"  {tk}", m)

    modelos_full[0].save_model(str(out_dir / "modelo_global.json"))
    meta = {
        "ticker": "GLOBAL", "experimento": exp_id, "tipo": "global",
        "config_id": config_id, "modelo": "XGBoost",
        "best_params": best, "n_features": len(feat_cols),
        "n_seeds": len(SEEDS), "features": feat_cols,
        "metricas_val":  met_val,
        "metricas_test": met_test,
        "metricas_test_por_ticker": met_por_ticker,
    }
    guardar_json(meta, out_dir / "metricas_global.json")

    fila = {
        "config_id": config_id, "modelo": "XGBoost", "tipo": "global",
        "ticker": "GLOBAL", "experimento": exp_id,
        "n_features": len(feat_cols), "n_seeds": len(SEEDS),
        "val_f1_macro":  met_val["f1_macro"],
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
        fila[k] = met_test.get(k, None)
    resultados.append(fila)

    return resultados


# ════════════════════════════════════════════════════════════════════════════
# PIPELINE
# ════════════════════════════════════════════════════════════════════════════

def pipeline(configs_a_correr=None):
    print("="*70)
    print("  OPTIMIZACIÓN XGBOOST — MULTI-CONFIG MULTI-SEED + OPTUNA")
    print(f"  GPU={'YES' if USE_GPU else 'NO'}  TRIALS=(ticker={N_TRIALS_PER_TICKER}, global={N_TRIALS_GLOBAL})  SEEDS={len(SEEDS)}")
    print("="*70)

    if configs_a_correr is None:
        configs_a_correr = list(CONFIGS.keys())

    t0 = time.time()
    todos = []
    for cfg_id in configs_a_correr:
        if cfg_id not in CONFIGS:
            print(f"⚠ Config {cfg_id} no existe, saltando.")
            continue
        cfg = CONFIGS[cfg_id]
        for exp_id in EXPERIMENTOS:
            res = correr_config(cfg_id, cfg, exp_id)
            todos.extend(res)
            df = pd.DataFrame(todos)
            df.to_csv(RESULTS_CSV, index=False)

    dur = time.time() - t0
    print(f"\n{'='*70}")
    print(f"  TIEMPO TOTAL: {dur/60:.1f} min")
    print(f"  Resultados → {RESULTS_CSV}")
    print(f"{'='*70}")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--configs", nargs="+", default=None)
    args = p.parse_args()
    pipeline(configs_a_correr=args.configs)
