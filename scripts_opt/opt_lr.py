"""
================================================================================
OPTIMIZACIÓN — REGRESIÓN LOGÍSTICA
================================================================================
Estrategia:
  - Probar varias configuraciones (penalty, C, l1_ratio, polynomial features)
  - Comparar selección de features (consenso vs. todas vs. top-shap)
  - Threshold tuning por clase
  - Multi-seed para reportar varianza

Salida: RESULTADOS_OPTIMIZADOS/modelos_optimizados/lr/
"""
import os
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUNBUFFERED"] = "1"
import sys
import time
import json
import pickle
import warnings
import functools
import numpy as np
import pandas as pd
from pathlib import Path

# Configure UTF-8 reconfiguration if supported (Python 3.7+)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass

# Force prints to flush
print = functools.partial(print, flush=True)
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import f1_score

sys.path.insert(0, str(Path(__file__).parent))
from common import (TICKERS, EXPERIMENTOS, CLASES,
                    cargar_dataset, cargar_global,
                    metricas_full, metricas_global_por_ticker,
                    guardar_json, append_resultado, imprimir_metricas, OUT_DIR)

warnings.filterwarnings("ignore")

# ════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ════════════════════════════════════════════════════════════════════════════

OUT_LR = OUT_DIR / "modelos_optimizados" / "lr"
OUT_LR.mkdir(parents=True, exist_ok=True)
RESULTS_CSV = OUT_LR / "resultados_lr_opt.csv"

C_GRID = [0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0]
# Reducido para saga + elasticnet (más lento)
C_GRID_SAGA = [0.01, 0.1, 1.0, 10.0]
L1_RATIOS = [0.2, 0.5, 0.8]
SEEDS = [42, 1, 7, 2024, 100]
MAX_ITER_LBFGS = 2000
MAX_ITER_SAGA  = 1500   # Más bajo, suficiente para convergencia rápida

# Configuraciones a probar
CONFIGS = {
    "LR-01-l2-all":         dict(penalty="l2",         poly=False, features="all", calib=False),
    "LR-02-elasticnet-all": dict(penalty="elasticnet", poly=False, features="all", calib=False),
    "LR-03-l1-all":         dict(penalty="l1",         poly=False, features="all", calib=False),
    "LR-04-l2-poly":        dict(penalty="l2",         poly=True,  features="all", calib=False),
    "LR-05-l2-shap":        dict(penalty="l2",         poly=False, features="shap_top20", calib=False),
    "LR-06-elasticnet-calib":  dict(penalty="elasticnet", poly=False, features="all", calib=True),
    "LR-07-l1-calib":          dict(penalty="l1",         poly=False, features="all", calib=True),
}


# ════════════════════════════════════════════════════════════════════════════
# UTILIDADES
# ════════════════════════════════════════════════════════════════════════════

def construir_modelo(penalty, C, l1_ratio=None, seed=42):
    if penalty == "elasticnet":
        return LogisticRegression(
            penalty="elasticnet", solver="saga",
            l1_ratio=l1_ratio, C=C, max_iter=MAX_ITER_SAGA,
            class_weight="balanced", random_state=seed,
            n_jobs=-1, tol=1e-3)
    elif penalty == "l1":
        return LogisticRegression(
            penalty="l1", solver="saga",
            C=C, max_iter=MAX_ITER_SAGA, class_weight="balanced",
            random_state=seed, n_jobs=-1, tol=1e-3)
    else:  # l2
        return LogisticRegression(
            penalty="l2", solver="lbfgs",
            C=C, max_iter=MAX_ITER_LBFGS, class_weight="balanced",
            random_state=seed, n_jobs=-1)


def buscar_hp(X_tr, y_tr, X_va, y_va, penalty, seed=42):
    """Búsqueda grid sobre C (y l1_ratio si elasticnet). Selecciona por F1-macro val."""
    mejor = {"f1_va": -1, "C": None, "l1_ratio": None}
    if penalty == "elasticnet":
        combinaciones = [(c, r) for c in C_GRID_SAGA for r in L1_RATIOS]
    elif penalty == "l1":
        combinaciones = [(c, None) for c in C_GRID_SAGA]
    else:
        combinaciones = [(c, None) for c in C_GRID]

    for C, l1r in combinaciones:
        try:
            m = construir_modelo(penalty, C, l1r, seed=seed)
            m.fit(X_tr, y_tr)
            f1 = f1_score(y_va, m.predict(X_va), average="macro", zero_division=0)
            if f1 > mejor["f1_va"]:
                mejor = {"f1_va": f1, "C": C, "l1_ratio": l1r}
        except Exception:
            continue
    return mejor


def calibrar_thresholds(probs_va, y_va):
    """
    Encuentra factores de ajuste multiplicativos para las probabilidades de BUY/SELL
    que maximizan F1-macro en validación.
    Retorna (factor_buy, factor_sell). Aplicar: probs[:, 2] *= factor_buy, probs[:, 0] *= factor_sell.
    """
    mejor_f1, mejor_factores = -1, (1.0, 1.0)
    factores = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.8, 2.0]
    for fb in factores:
        for fs in factores:
            p = probs_va.copy()
            p[:, 2] *= fb
            p[:, 0] *= fs
            pred = p.argmax(axis=1)
            f1 = f1_score(y_va, pred, average="macro", zero_division=0)
            if f1 > mejor_f1:
                mejor_f1, mejor_factores = f1, (fb, fs)
    return mejor_factores


def aplicar_calibracion(probs, factores):
    p = probs.copy()
    p[:, 2] *= factores[0]
    p[:, 0] *= factores[1]
    return p.argmax(axis=1)


def aplicar_poly(X_tr, X_va, X_te, max_features=50):
    """
    PolynomialFeatures con interaction_only y degree=2 puede explotar la dimensionalidad.
    Limitamos al top-N por varianza para mantenerlo manejable.
    """
    if X_tr.shape[1] > max_features:
        # Pre-seleccionar columnas con mayor varianza para reducir dimensionalidad
        var = X_tr.var(axis=0)
        idx = np.argsort(-var)[:max_features]
        X_tr_red = X_tr[:, idx]
        X_va_red = X_va[:, idx]
        X_te_red = X_te[:, idx]
    else:
        X_tr_red, X_va_red, X_te_red = X_tr, X_va, X_te

    poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
    X_tr_p = poly.fit_transform(X_tr_red)
    X_va_p = poly.transform(X_va_red)
    X_te_p = poly.transform(X_te_red)
    return X_tr_p, X_va_p, X_te_p


def filtrar_shap_top(feat_cols, top_n=20):
    """Carga importancias SHAP del Script 02 si están disponibles, o usa heurística."""
    # Lista por defecto basada en consenso de exp B (top-20 importantes)
    candidatos_globales = [
        "ret_1d", "ret_2d", "ret_3d", "ret_5d", "ret_10d",
        "mom_5d", "mom_10d", "mom_20d", "mom_60d",
        "dist_ma10", "dist_ma20", "dist_ma50",
        "atr_norm", "vol_5d", "vol_10d", "vol_20d",
        "rsi_7", "rsi_14", "stoch_k", "stoch_d", "williams_r",
        "macd_hist", "cmf_20", "mfi_14",
        "hl_ratio", "cuerpo_rel", "gap_apertura",
        "SP500_ret", "VIX_norm", "VIX_change",
    ]
    feats = [f for f in candidatos_globales if f in feat_cols][:top_n]
    return feats


def fila_resultado(config_id, tipo, ticker, exp_id, met_val, met_test, hp, n_features, seeds_used):
    fila = {
        "config_id":   config_id,
        "modelo":      "LogisticRegression",
        "tipo":        tipo,
        "ticker":      ticker,
        "experimento": exp_id,
        "n_features":  n_features,
        "C":           hp.get("C"),
        "l1_ratio":    hp.get("l1_ratio"),
        "n_seeds":     seeds_used,
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
    return fila


# ════════════════════════════════════════════════════════════════════════════
# UN EXPERIMENTO COMPLETO POR (CONFIG, EXP_ID)
# ════════════════════════════════════════════════════════════════════════════

def correr_config(config_id, config, exp_id, multi_seed=True):
    """Corre la configuración para todos los tickers (por-ticker) + global."""
    penalty  = config["penalty"]
    use_poly = config["poly"]
    feat_sel = config["features"]

    seeds = SEEDS if multi_seed else [SEEDS[0]]
    print(f"\n{'═'*70}")
    print(f"  Config: {config_id}  |  Exp {exp_id}  |  penalty={penalty}  poly={use_poly}  features={feat_sel}")
    print(f"{'═'*70}")

    out_dir = OUT_LR / config_id / f"experimento_{exp_id}"
    out_dir.mkdir(parents=True, exist_ok=True)

    resultados = []

    # ════════════════════════════════════════════════════════════════════════
    # POR TICKER
    # ════════════════════════════════════════════════════════════════════════
    print(f"\n  ── POR TICKER ─────────────────────────")
    for ticker in TICKERS:
        d = cargar_dataset(ticker, exp_id)
        feat_cols = d["feat_cols"]
        if feat_sel == "shap_top20":
            feat_cols = filtrar_shap_top(feat_cols, 20)
            d = cargar_dataset(ticker, exp_id, feat_cols)

        # Escalado (StandardScaler fit en train)
        scaler = StandardScaler()
        X_tr = scaler.fit_transform(d["X_tr"])
        X_va = scaler.transform(d["X_va"])
        X_te = scaler.transform(d["X_te"])

        # Polynomial features (si aplica)
        if use_poly:
            X_tr, X_va, X_te = aplicar_poly(X_tr, X_va, X_te)
        n_feat = X_tr.shape[1]

        # Búsqueda de HP en seed=42
        hp = buscar_hp(X_tr, d["y_tr"], X_va, d["y_va"], penalty, seed=42)
        if hp["C"] is None:
            print(f"  {ticker}: ⚠ no convergió")
            continue

        # Multi-seed entrenamiento sobre train+val con HP óptimo, evaluado en test
        X_full = np.vstack([X_tr, X_va])
        y_full = np.concatenate([d["y_tr"], d["y_va"]])

        preds_va_seeds, preds_te_seeds = [], []
        for s in seeds:
            m_val = construir_modelo(penalty, hp["C"], hp.get("l1_ratio"), seed=s)
            m_val.fit(X_tr, d["y_tr"])
            preds_va_seeds.append(m_val.predict(X_va))

            m_full = construir_modelo(penalty, hp["C"], hp.get("l1_ratio"), seed=s)
            m_full.fit(X_full, y_full)
            preds_te_seeds.append(m_full.predict(X_te))

        # Mayoría votada como predicción final
        preds_va = np.apply_along_axis(lambda x: np.bincount(x, minlength=3).argmax(),
                                       axis=0, arr=np.array(preds_va_seeds))
        preds_te = np.apply_along_axis(lambda x: np.bincount(x, minlength=3).argmax(),
                                       axis=0, arr=np.array(preds_te_seeds))

        met_val  = metricas_full(d["y_va"], preds_va, split_name="val")
        met_test = metricas_full(d["y_te"], preds_te, r_forward=d["r_fwd_test"], split_name="test")

        imprimir_metricas(f"{ticker} val ", met_val)
        imprimir_metricas(f"{ticker} test", met_test)

        # Guardar modelo final (último seed) — útil para inspeccionar coefs
        with open(out_dir / f"{ticker}_modelo.pkl", "wb") as f:
            pickle.dump({"model": m_full, "scaler": scaler, "hp": hp,
                         "feat_cols": feat_cols, "config_id": config_id}, f)

        meta = {
            "ticker": ticker, "experimento": exp_id, "tipo": "por_ticker",
            "config_id": config_id, "modelo": "LogisticRegression",
            "hp": hp, "n_features": n_feat, "n_seeds": len(seeds),
            "feat_cols": feat_cols,
            "metricas_val":  met_val,
            "metricas_test": met_test,
        }
        guardar_json(meta, out_dir / f"{ticker}_metricas.json")

        fila = fila_resultado(config_id, "por_ticker", ticker, exp_id,
                              met_val, met_test, hp, n_feat, len(seeds))
        resultados.append(fila)

    # ════════════════════════════════════════════════════════════════════════
    # GLOBAL
    # ════════════════════════════════════════════════════════════════════════
    print(f"\n  ── GLOBAL ─────────────────────────")
    feat_cols = None
    if feat_sel == "shap_top20":
        # Determinar top desde primer ticker
        d_aux = cargar_dataset(TICKERS[0], exp_id)
        feat_cols = filtrar_shap_top(d_aux["feat_cols"], 20)

    g = cargar_global(exp_id, feat_cols)
    feat_cols = g["feat_cols"]

    scaler = StandardScaler()
    X_tr = scaler.fit_transform(g["X_tr"])
    X_va = scaler.transform(g["X_va"])
    X_te = scaler.transform(g["X_te"])
    if use_poly:
        X_tr, X_va, X_te = aplicar_poly(X_tr, X_va, X_te)
    n_feat = X_tr.shape[1]

    hp = buscar_hp(X_tr, g["y_tr"], X_va, g["y_va"], penalty, seed=42)
    if hp["C"] is None:
        print("  GLOBAL: ⚠ no convergió")
        return resultados

    X_full = np.vstack([X_tr, X_va])
    y_full = np.concatenate([g["y_tr"], g["y_va"]])

    preds_va_seeds, preds_te_seeds = [], []
    for s in seeds:
        m_val = construir_modelo(penalty, hp["C"], hp.get("l1_ratio"), seed=s)
        m_val.fit(X_tr, g["y_tr"])
        preds_va_seeds.append(m_val.predict(X_va))

        m_full = construir_modelo(penalty, hp["C"], hp.get("l1_ratio"), seed=s)
        m_full.fit(X_full, y_full)
        preds_te_seeds.append(m_full.predict(X_te))

    preds_va = np.apply_along_axis(lambda x: np.bincount(x, minlength=3).argmax(),
                                   axis=0, arr=np.array(preds_va_seeds))
    preds_te = np.apply_along_axis(lambda x: np.bincount(x, minlength=3).argmax(),
                                   axis=0, arr=np.array(preds_te_seeds))

    met_val  = metricas_full(g["y_va"], preds_va, split_name="val")
    met_test = metricas_full(g["y_te"], preds_te, r_forward=g["r_fwd_test"], split_name="test")
    met_por_ticker = metricas_global_por_ticker(
        g["y_te"], preds_te, g["ticker_test"], g["r_fwd_test"])

    imprimir_metricas("GLOBAL val ", met_val)
    imprimir_metricas("GLOBAL test", met_test)

    with open(out_dir / "modelo_global.pkl", "wb") as f:
        pickle.dump({"model": m_full, "scaler": scaler, "hp": hp,
                     "feat_cols": feat_cols, "config_id": config_id}, f)

    meta = {
        "ticker": "GLOBAL", "experimento": exp_id, "tipo": "global",
        "config_id": config_id, "modelo": "LogisticRegression",
        "hp": hp, "n_features": n_feat, "n_seeds": len(seeds),
        "feat_cols": feat_cols,
        "metricas_val":  met_val,
        "metricas_test": met_test,
        "metricas_test_por_ticker": met_por_ticker,
    }
    guardar_json(meta, out_dir / "metricas_global.json")

    fila = fila_resultado(config_id, "global", "GLOBAL", exp_id,
                          met_val, met_test, hp, n_feat, len(seeds))
    resultados.append(fila)

    return resultados


# ════════════════════════════════════════════════════════════════════════════
# PIPELINE PRINCIPAL
# ════════════════════════════════════════════════════════════════════════════

def pipeline(configs_a_correr=None):
    print("="*70)
    print("  OPTIMIZACIÓN LOGISTIC REGRESSION — MULTI-CONFIG MULTI-SEED")
    print("="*70)

    if configs_a_correr is None:
        configs_a_correr = list(CONFIGS.keys())

    # Cargar resultados previos (acumular en vez de sobrescribir)
    if RESULTS_CSV.exists():
        df_prev = pd.read_csv(RESULTS_CSV)
        # Limpiar entradas previas de las configs que vamos a correr (sobreescribir, no duplicar)
        df_prev = df_prev[~df_prev["config_id"].isin(configs_a_correr)]
        todos = df_prev.to_dict("records")
        print(f"  Reanudando con {len(todos)} registros previos en CSV")
    else:
        todos = []

    t0 = time.time()
    for cfg_id in configs_a_correr:
        if cfg_id not in CONFIGS:
            print(f"⚠ Config {cfg_id} no existe, saltando.")
            continue
        cfg = CONFIGS[cfg_id]
        for exp_id in EXPERIMENTOS:
            res = correr_config(cfg_id, cfg, exp_id, multi_seed=True)
            todos.extend(res)
            df = pd.DataFrame(todos)
            df.to_csv(RESULTS_CSV, index=False)

    dur = time.time() - t0
    print(f"\n{'='*70}")
    print(f"  TIEMPO TOTAL: {dur/60:.1f} min")
    print(f"  Resultados → {RESULTS_CSV}")
    print(f"{'='*70}")

    # Resumen
    if todos:
        df = pd.DataFrame(todos)
        for tipo in ["global", "por_ticker"]:
            sub = df[df["tipo"] == tipo]
            if sub.empty:
                continue
            print(f"\n  RESUMEN {tipo.upper()} — F1-macro test:")
            piv = sub.pivot_table(index="config_id", columns="experimento",
                                  values="test_f1_macro", aggfunc="mean")
            print(piv.round(4).to_string())


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--configs", nargs="+", default=None,
                   help="Lista de config IDs a correr (default: todos)")
    args = p.parse_args()
    pipeline(configs_a_correr=args.configs)
