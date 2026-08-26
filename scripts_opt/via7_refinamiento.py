"""
================================================================================
VÍA 7 — REFINAMIENTO POST-OPTUNA
================================================================================
Cinco técnicas que las vías 0-6 NO probaron. Todas se ejecutan en Exp B GLOBAL
(el experimento principal del paper), sobre el baseline v5 congelado.

Reglas del juego (R5 del PLAN_MAESTRO):
  - Se adopta una técnica solo si mejora ≥ 0.005 F1 O ≥ 0.10 Sharpe en test
    con la mejora superando 1 std de bootstrap.
  - Cualquier resultado (mejora o no) se documenta.

Técnicas:
  1) ISOTONIC CALIBRATION (post-training, per-class)
     Recalibra las probabilidades del modelo usando validación (2024),
     evalúa en test (2025). Puede mejorar el argmax cuando las probs están
     mal calibradas.

  2) THRESHOLD ECONÓMICO DE HOLD
     Busca τ tal que señal = HOLD si p_hold >= τ, argmax(BUY,SELL) si no.
     τ se elige en validación por Sharpe (no F1). Aplica también a la
     calibración isotónica.

  3) BLENDING LR + XGB POR SHARPE
     Combina probs(LR) y probs(XGB) con pesos (w, 1-w) buscados por Optuna
     para maximizar Sharpe en validación. Aplica en test.

  4) BLENDING 5-WAY POR F1
     Igual pero con los 5 modelos y objetivo F1-macro.

  5) SWA (Stochastic Weight Averaging) en deep
     Re-entrena LSTM, CNN, CNN-LSTM con SWA activado en las últimas 20
     épocas. Compara F1 y Sharpe vs baseline v5.

  6) RECENCY WEIGHTING en LR/XGB
     Pesa las muestras exponencialmente por antigüedad (más peso a datos
     recientes), con τ_medio-año buscado por Optuna en validación.

Uso:
    python scripts_opt/via7_refinamiento.py --step preds_val   # 15 min
    python scripts_opt/via7_refinamiento.py --step calibrar     #  2 min
    python scripts_opt/via7_refinamiento.py --step blending     #  5 min
    python scripts_opt/via7_refinamiento.py --step swa          # 45 min
    python scripts_opt/via7_refinamiento.py --step recency      # 15 min
    python scripts_opt/via7_refinamiento.py --step consolidar   # 10 s
    python scripts_opt/via7_refinamiento.py --step all          # todo secuencial

Salida:
    RESULTADOS_OPTIMIZADOS/v7/preds_val/{modelo}_B_GLOBAL.npz  (paso 1)
    RESULTADOS_OPTIMIZADOS/v7/tabla_refinamiento.csv           (consolidado)
    RESULTADOS_OPTIMIZADOS/docs/VIA7_REFINAMIENTO.md           (informe)
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("PYTHONUNBUFFERED", "1")
import sys, json, time, argparse, functools, warnings
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
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import f1_score
import optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)

from common import metricas_full

# ════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ════════════════════════════════════════════════════════════════════════════
OUT = Path("RESULTADOS_OPTIMIZADOS/v7")
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "preds_val").mkdir(exist_ok=True)
PREDS_TEST_DIR = Path("RESULTADOS_OPTIMIZADOS/v5/preds")
DOCS = Path("RESULTADOS_OPTIMIZADOS/docs")
CSV_RESULTADOS = OUT / "tabla_refinamiento.csv"

MODELOS = ["LR", "XGBoost", "LSTM", "CNN", "CNN-LSTM"]

# Baseline v5 (F1 en test 2025 Exp B GLOBAL) — sacado de tabla2_economicas_expB.md
BASELINE_V5 = {
    "LR":       {"f1": 0.4036, "win_rate": 0.5203, "profit_factor": 1.2695, "max_dd": -0.4530, "sharpe": 0.8946},
    "XGBoost":  {"f1": 0.3591, "win_rate": 0.4908, "profit_factor": 1.1111, "max_dd": -0.4985, "sharpe": 0.4620},
    "LSTM":     {"f1": 0.3688, "win_rate": 0.4901, "profit_factor": 0.9225, "max_dd": -0.6758, "sharpe": -0.3451},
    "CNN":      {"f1": 0.3590, "win_rate": 0.4842, "profit_factor": 0.9001, "max_dd": -0.7250, "sharpe": -0.4592},
    "CNN-LSTM": {"f1": 0.3723, "win_rate": 0.4844, "profit_factor": 0.9824, "max_dd": -0.6213, "sharpe": -0.0739},
}


# ════════════════════════════════════════════════════════════════════════════
# UTILIDADES DE BACKTEST
# ════════════════════════════════════════════════════════════════════════════

def backtest_metricas(y_pred, y_true, r_fwd, tk):
    """Devuelve F1 + métricas económicas replicando metricas_full, con claves
    normalizadas (sin sufijo _test)."""
    met = metricas_full(y_true, y_pred, r_forward=r_fwd, split_name="test")
    # normalizar claves (metricas_economicas las guarda con sufijo _test)
    out = {
        "f1_macro": met.get("f1_macro", 0.0),
        "sharpe": met.get("sharpe_test", 0.0),
        "max_dd": met.get("max_drawdown_test", 0.0),
        "win_rate": met.get("win_rate_test", 0.0),
        "profit_factor": met.get("profit_factor_test") or 0.0,
        "cumul_return": met.get("cumul_return_test", 0.0),
        "signal_buy": float((y_pred == 2).mean() * 100),
        "signal_hold": float((y_pred == 1).mean() * 100),
        "signal_sell": float((y_pred == 0).mean() * 100),
    }
    return out


def cargar_test(modelo: str, exp: str = "B", tipo: str = "global") -> dict:
    """Carga las probs y y-labels de test 2025 del baseline v5."""
    if tipo == "global":
        path = PREDS_TEST_DIR / f"{modelo}_{exp}_global_GLOBAL_v1.npz"
    else:
        raise ValueError(f"tipo={tipo} no implementado")
    d = np.load(path, allow_pickle=True)
    return {"probs": d["probs"], "y": d["y"], "r": d["r"], "tk": d["tk"], "fechas": d["fechas"]}


def cargar_val(modelo: str, exp: str = "B", tipo: str = "global") -> dict | None:
    """Carga probs de validación (2024) si existen; None si no."""
    path = OUT / "preds_val" / f"{modelo}_{exp}_{tipo}.npz"
    if not path.exists():
        return None
    d = np.load(path, allow_pickle=True)
    return {"probs": d["probs"], "y": d["y"], "r": d["r"], "tk": d["tk"], "fechas": d["fechas"]}


# ════════════════════════════════════════════════════════════════════════════
# PASO 1 — REGENERAR PROBS DE VALIDACIÓN (2024) PARA LOS 5 MODELOS
# ════════════════════════════════════════════════════════════════════════════

def paso_preds_val():
    """
    Genera las probs de validación (2024) para los 5 modelos usando los mismos
    hyperparams ganadores de Optuna en v5.

    IMPORTANTE:
      - LR/XGBoost: modo="final" (train=2018-2023). Se entrena solo con train,
        se predict_proba sobre val=2024 (out-of-sample) y sobre eval=2025.
      - Deep: modo="dev" (train=2018-2022, val=2023, eval=2024) porque en modo
        final el val=2024 tiene leak (se usó para early stopping). Aquí las
        probs sobre eval=2024 son out-of-sample.
    """
    from common_v5 import (Cfg, CFG_V4, correr, preparar, preparar_tabular,
                            SEEDS_5, SEEDS_DEFAULT)
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.utils.class_weight import compute_class_weight
    import xgboost as xgb

    print("=" * 70)
    print("PASO 1 — PROBS DE VALIDACIÓN (2024) PARA LOS 5 MODELOS")
    print("=" * 70)

    # Cargamos las configuraciones finalistas de v5 desde ganadores_dl.json / _clasicos.json
    with open("RESULTADOS_OPTIMIZADOS/v5/ganadores_dl.json") as f:
        gan_dl = json.load(f)
    with open("RESULTADOS_OPTIMIZADOS/v5/ganadores_clasicos.json") as f:
        gan_cls = json.load(f)

    # === LR y XGBoost — modo final ===
    for nombre in ["LR", "XGBoost"]:
        hp = gan_cls[nombre].get("params", {})
        escalador = hp.get("escalador", "standard")
        print(f"\n── {nombre} (params: {hp}) ──")

        t0 = time.time()
        datos = preparar_tabular("B", modo="final", tipo="global", escalador=escalador)
        Xtr, ytr = datos["X_train"], datos["y_train"]
        Xva, yva = datos["X_val"], datos["y_val"]
        Xev, yev = datos["X_eval"], datos["y_eval"]
        r_va, tk_va, f_va = datos["r_val"], datos["tk_val"], datos["f_val"]
        print(f"   n_train={len(ytr)} n_val(2024)={len(yva)} n_test(2025)={len(yev)}")

        # class weights basados en train
        w = compute_class_weight("balanced", classes=np.array([0, 1, 2]), y=ytr)
        class_w = {int(i): float(w[i]) for i in range(3)}
        sample_w = np.array([w[c] for c in ytr])

        if nombre == "LR":
            penalty = hp.get("penalty", "l2")
            C = hp.get("C", 1.0)
            kwargs = dict(penalty=penalty, C=C, solver="saga", max_iter=5000,
                          class_weight="balanced", random_state=42, n_jobs=-1,
                          tol=1e-4)
            if penalty == "elasticnet":
                kwargs["l1_ratio"] = hp.get("l1_ratio", 0.5)
            model = LogisticRegression(**kwargs)
            model.fit(Xtr, ytr)  # ya viene escalado por preparar_tabular
            probs_va = model.predict_proba(Xva)
        else:  # XGBoost
            model = xgb.XGBClassifier(
                n_estimators=int(hp.get("n_estimators", 500)),
                max_depth=int(hp.get("max_depth", 6)),
                learning_rate=float(hp.get("learning_rate", 0.05)),
                subsample=float(hp.get("subsample", 0.8)),
                colsample_bytree=float(hp.get("colsample_bytree", 0.8)),
                min_child_weight=int(hp.get("min_child_weight", 1)),
                reg_alpha=float(hp.get("reg_alpha", 0.0)),
                reg_lambda=float(hp.get("reg_lambda", 1.0)),
                gamma=float(hp.get("gamma", 0.0)),
                objective="multi:softprob", num_class=3,
                tree_method="hist", device="cuda",
                random_state=42, eval_metric="mlogloss", verbosity=0,
            )
            model.fit(Xtr, ytr, sample_weight=sample_w, verbose=False)
            probs_va = model.predict_proba(Xva)

        np.savez(OUT / "preds_val" / f"{nombre}_B_global.npz",
                 probs=probs_va, y=yva, r=r_va, tk=tk_va, fechas=f_va)
        f1 = f1_score(yva, probs_va.argmax(1), average="macro", zero_division=0)
        print(f"   F1 en val(2024): {f1:.4f}  ({time.time()-t0:.1f}s)")

    # === Deep — modo dev ===
    map_arch = {"LSTM": "lstm", "CNN": "cnn", "CNN-LSTM": "cnn_lstm"}
    for nombre in ["LSTM", "CNN", "CNN-LSTM"]:
        arch = map_arch[nombre]
        cfg_dict = gan_dl[arch]["cfg"].copy()
        # convertir lista a tuple para filtros
        if isinstance(cfg_dict.get("filtros"), list):
            cfg_dict["filtros"] = tuple(cfg_dict["filtros"])
        valid_keys = set(Cfg.__dataclass_fields__.keys())
        cfg_dict = {k: v for k, v in cfg_dict.items() if k in valid_keys}
        cfg = Cfg(**cfg_dict)

        print(f"\n── {nombre} (arch={arch}, lookback={cfg.lookback}, "
              f"loss={cfg.loss}, escalador={cfg.escalador}) ──")
        t0 = time.time()
        # modo dev: eval = 2024, out-of-sample real
        res = correr(cfg, exp="B", modo="dev", tipo="global",
                     semillas=SEEDS_DEFAULT, devolver_probs=True)
        probs_va = res["probs_eval"]
        yva = res["y_eval"]
        r_va = res["r_eval"]
        tk_va = res["tk_eval"]
        f_va = res["f_eval"]
        np.savez(OUT / "preds_val" / f"{nombre}_B_global.npz",
                 probs=probs_va, y=yva, r=r_va, tk=tk_va, fechas=f_va)
        print(f"   F1 en val(2024): {res['eval_f1_ens']:.4f}  ({time.time()-t0:.1f}s)")

    print(f"\n✓ Probs de val (2024) guardados en {OUT}/preds_val/")


# ════════════════════════════════════════════════════════════════════════════
# PASO 2 — CALIBRACIÓN ISOTÓNICA + THRESHOLD ECONÓMICO
# ════════════════════════════════════════════════════════════════════════════

def isotonic_calibrate(probs_train, y_train, probs_test):
    """Aplica isotonic regression por clase (one-vs-rest) y renormaliza."""
    calibradas = np.zeros_like(probs_test)
    for c in range(3):
        iso = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
        iso.fit(probs_train[:, c], (y_train == c).astype(float))
        calibradas[:, c] = iso.predict(probs_test[:, c])
    # Renormalizar
    calibradas = np.clip(calibradas, 1e-9, 1.0)
    calibradas /= calibradas.sum(axis=1, keepdims=True)
    return calibradas


def buscar_threshold_hold(probs_val, y_val, r_val, tk_val, criterio="sharpe"):
    """
    Busca τ tal que: señal = HOLD si p_hold >= τ, argmax(BUY,SELL) si no.
    Retorna (mejor_τ, mejor_valor_criterio).
    """
    mejor_tau, mejor_val = 0.5, -np.inf  # default = argmax normal cuando τ=0.5
    taus = np.linspace(0.0, 1.0, 41)  # cada 0.025
    for tau in taus:
        mask_hold = probs_val[:, 1] >= tau
        y_pred = np.where(mask_hold, 1, np.where(probs_val[:, 2] > probs_val[:, 0], 2, 0))
        met = backtest_metricas(y_pred, y_val, r_val, tk_val)
        val = met[criterio] if criterio in met else met.get("f1_macro", 0.0)
        if val > mejor_val:
            mejor_val = val
            mejor_tau = tau
    return mejor_tau, mejor_val


def paso_calibrar():
    """Aplica isotonic + threshold economico a los 5 modelos."""
    print("=" * 70)
    print("PASO 2 — CALIBRACIÓN ISOTÓNICA + THRESHOLD ECONÓMICO")
    print("=" * 70)
    filas = []

    for modelo in MODELOS:
        val = cargar_val(modelo)
        test = cargar_test(modelo)
        if val is None:
            print(f"⚠ Faltan probs_val para {modelo}, omitiendo (correr paso 1 primero)")
            continue

        # 2a) Baseline (argmax simple)
        pred_base = test["probs"].argmax(1)
        met_base = backtest_metricas(pred_base, test["y"], test["r"], test["tk"])

        # 2b) Isotonic solo
        probs_test_iso = isotonic_calibrate(val["probs"], val["y"], test["probs"])
        pred_iso = probs_test_iso.argmax(1)
        met_iso = backtest_metricas(pred_iso, test["y"], test["r"], test["tk"])

        # 2c) Threshold económico (τ_hold) sobre probs originales, por Sharpe en val
        tau_s, _ = buscar_threshold_hold(val["probs"], val["y"], val["r"], val["tk"], "sharpe")
        mask_hold = test["probs"][:, 1] >= tau_s
        pred_th = np.where(mask_hold, 1,
                           np.where(test["probs"][:, 2] > test["probs"][:, 0], 2, 0))
        met_th = backtest_metricas(pred_th, test["y"], test["r"], test["tk"])

        # 2d) Isotonic + Threshold económico
        # Recalibramos val (dev) también, y buscamos τ sobre esa calibración
        probs_val_iso = isotonic_calibrate(val["probs"], val["y"], val["probs"])
        tau_si, _ = buscar_threshold_hold(probs_val_iso, val["y"], val["r"], val["tk"], "sharpe")
        mask_hold_i = probs_test_iso[:, 1] >= tau_si
        pred_iso_th = np.where(mask_hold_i, 1,
                                np.where(probs_test_iso[:, 2] > probs_test_iso[:, 0], 2, 0))
        met_iso_th = backtest_metricas(pred_iso_th, test["y"], test["r"], test["tk"])

        for nombre, met, extra in [
            ("baseline", met_base, ""),
            ("isotonic", met_iso, ""),
            ("threshold", met_th, f"τ={tau_s:.3f}"),
            ("iso+threshold", met_iso_th, f"τ={tau_si:.3f}"),
        ]:
            filas.append({
                "modelo": modelo, "tecnica": nombre, "extra": extra,
                "f1": met["f1_macro"], "sharpe": met.get("sharpe", 0),
                "win_rate": met.get("win_rate", 0), "pf": met.get("profit_factor", 0),
                "max_dd": met.get("max_dd", 0),
                "signal_buy": met["signal_buy"], "signal_hold": met["signal_hold"],
                "signal_sell": met["signal_sell"],
            })

        print(f"\n── {modelo} ──")
        print(f"  baseline:      F1={met_base['f1_macro']:.4f} Sharpe={met_base.get('sharpe',0):+.3f} "
              f"WR={met_base.get('win_rate',0):.3f} MaxDD={met_base.get('max_dd',0):.3f}")
        print(f"  isotonic:      F1={met_iso['f1_macro']:.4f} Sharpe={met_iso.get('sharpe',0):+.3f}")
        print(f"  threshold:     F1={met_th['f1_macro']:.4f} Sharpe={met_th.get('sharpe',0):+.3f}  (τ={tau_s:.3f})")
        print(f"  iso+threshold: F1={met_iso_th['f1_macro']:.4f} Sharpe={met_iso_th.get('sharpe',0):+.3f}  (τ={tau_si:.3f})")

    df = pd.DataFrame(filas)
    df.to_csv(OUT / "calibracion.csv", index=False)
    print(f"\n✓ Guardado en {OUT}/calibracion.csv")
    return df


# ════════════════════════════════════════════════════════════════════════════
# PASO 3 — BLENDING (LR+XGB por Sharpe, 5-way por F1)
# ════════════════════════════════════════════════════════════════════════════

def paso_blending():
    print("=" * 70)
    print("PASO 3 — BLENDING (LR+XGB por Sharpe, 5-way por F1)")
    print("=" * 70)

    # Cargar todo val y test
    val_all, test_all = {}, {}
    for m in MODELOS:
        val_all[m] = cargar_val(m)
        test_all[m] = cargar_test(m)
    if any(v is None for v in val_all.values()):
        print("⚠ Faltan probs_val de algún modelo; correr paso 1 primero")
        return

    y_val = val_all["LR"]["y"]
    r_val = val_all["LR"]["r"]
    tk_val = val_all["LR"]["tk"]
    y_test = test_all["LR"]["y"]
    r_test = test_all["LR"]["r"]
    tk_test = test_all["LR"]["tk"]

    filas = []

    # 3a) Blending LR + XGB por Sharpe
    print("\n── Blending LR + XGB, objetivo Sharpe en val ──")

    def objetivo_lrxgb(trial):
        w = trial.suggest_float("w_lr", 0.0, 1.0)
        probs = w * val_all["LR"]["probs"] + (1 - w) * val_all["XGBoost"]["probs"]
        pred = probs.argmax(1)
        met = backtest_metricas(pred, y_val, r_val, tk_val)
        return met.get("sharpe", 0)

    study = optuna.create_study(direction="maximize",
                                 sampler=optuna.samplers.TPESampler(seed=42))
    study.optimize(objetivo_lrxgb, n_trials=50, show_progress_bar=False)
    w_lr = study.best_params["w_lr"]
    probs_test_lrxgb = w_lr * test_all["LR"]["probs"] + (1 - w_lr) * test_all["XGBoost"]["probs"]
    pred = probs_test_lrxgb.argmax(1)
    met = backtest_metricas(pred, y_test, r_test, tk_test)
    filas.append({"tecnica": "blend_lr_xgb_sharpe", "pesos": f"LR={w_lr:.3f},XGB={1-w_lr:.3f}",
                  **{k: met[k] for k in ["f1_macro"]},
                  "sharpe": met.get("sharpe", 0), "win_rate": met.get("win_rate", 0),
                  "profit_factor": met.get("profit_factor", 0), "max_dd": met.get("max_dd", 0)})
    print(f"  Pesos: LR={w_lr:.3f}, XGB={1-w_lr:.3f}")
    print(f"  F1={met['f1_macro']:.4f} Sharpe={met.get('sharpe',0):+.3f} "
          f"WR={met.get('win_rate',0):.3f} MaxDD={met.get('max_dd',0):.3f}")

    # 3b) Blending 5-way por F1-macro
    print("\n── Blending 5-way, objetivo F1-macro en val ──")

    def objetivo_5way_f1(trial):
        ws = np.array([trial.suggest_float(f"w_{m}", 0.0, 1.0) for m in MODELOS])
        ws = ws / (ws.sum() + 1e-9)
        probs = sum(ws[i] * val_all[m]["probs"] for i, m in enumerate(MODELOS))
        pred = probs.argmax(1)
        return f1_score(y_val, pred, average="macro", zero_division=0)

    study = optuna.create_study(direction="maximize",
                                 sampler=optuna.samplers.TPESampler(seed=42))
    study.optimize(objetivo_5way_f1, n_trials=100, show_progress_bar=False)
    ws = np.array([study.best_params[f"w_{m}"] for m in MODELOS])
    ws = ws / ws.sum()
    probs_test_5w = sum(ws[i] * test_all[m]["probs"] for i, m in enumerate(MODELOS))
    pred = probs_test_5w.argmax(1)
    met = backtest_metricas(pred, y_test, r_test, tk_test)
    filas.append({"tecnica": "blend_5way_f1",
                  "pesos": ",".join([f"{m}={ws[i]:.2f}" for i, m in enumerate(MODELOS)]),
                  **{k: met[k] for k in ["f1_macro"]},
                  "sharpe": met.get("sharpe", 0), "win_rate": met.get("win_rate", 0),
                  "profit_factor": met.get("profit_factor", 0), "max_dd": met.get("max_dd", 0)})
    print("  Pesos:", ", ".join([f"{m}={ws[i]:.2f}" for i, m in enumerate(MODELOS)]))
    print(f"  F1={met['f1_macro']:.4f} Sharpe={met.get('sharpe',0):+.3f}")

    # 3c) Blending 5-way por Sharpe
    print("\n── Blending 5-way, objetivo Sharpe en val ──")

    def objetivo_5way_sh(trial):
        ws = np.array([trial.suggest_float(f"w_{m}", 0.0, 1.0) for m in MODELOS])
        ws = ws / (ws.sum() + 1e-9)
        probs = sum(ws[i] * val_all[m]["probs"] for i, m in enumerate(MODELOS))
        pred = probs.argmax(1)
        return backtest_metricas(pred, y_val, r_val, tk_val).get("sharpe", 0)

    study = optuna.create_study(direction="maximize",
                                 sampler=optuna.samplers.TPESampler(seed=42))
    study.optimize(objetivo_5way_sh, n_trials=100, show_progress_bar=False)
    ws = np.array([study.best_params[f"w_{m}"] for m in MODELOS])
    ws = ws / ws.sum()
    probs_test_5w_sh = sum(ws[i] * test_all[m]["probs"] for i, m in enumerate(MODELOS))
    pred = probs_test_5w_sh.argmax(1)
    met = backtest_metricas(pred, y_test, r_test, tk_test)
    filas.append({"tecnica": "blend_5way_sharpe",
                  "pesos": ",".join([f"{m}={ws[i]:.2f}" for i, m in enumerate(MODELOS)]),
                  **{k: met[k] for k in ["f1_macro"]},
                  "sharpe": met.get("sharpe", 0), "win_rate": met.get("win_rate", 0),
                  "profit_factor": met.get("profit_factor", 0), "max_dd": met.get("max_dd", 0)})
    print("  Pesos:", ", ".join([f"{m}={ws[i]:.2f}" for i, m in enumerate(MODELOS)]))
    print(f"  F1={met['f1_macro']:.4f} Sharpe={met.get('sharpe',0):+.3f}")

    df = pd.DataFrame(filas)
    df.to_csv(OUT / "blending.csv", index=False)
    print(f"\n✓ Guardado en {OUT}/blending.csv")
    return df


# ════════════════════════════════════════════════════════════════════════════
# PASO 4 — SWA (Stochastic Weight Averaging) EN DEEP MODELS
# ════════════════════════════════════════════════════════════════════════════

def paso_swa():
    print("=" * 70)
    print("PASO 4 — SWA (Stochastic Weight Averaging) en deep models")
    print("=" * 70)
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.optim.swa_utils import AveragedModel, SWALR
    from common_v5 import (Cfg, CFG_V4, crear_modelo, preparar, hacer_loader,
                            pesos_clase, criterio_perdida, predecir_probs,
                            SEEDS_DEFAULT, DEVICE, fijar_semilla, _evaluar_loader)

    with open("RESULTADOS_OPTIMIZADOS/v5/ganadores_dl.json") as f:
        gan_dl = json.load(f)

    filas = []
    map_arch = {"LSTM": "lstm", "CNN": "cnn", "CNN-LSTM": "cnn_lstm"}
    for nombre in ["LSTM", "CNN", "CNN-LSTM"]:
        arch = map_arch[nombre]
        hp = gan_dl.get(arch, {}).get("params", {})
        cfg_dict = {**CFG_V4[arch].__dict__, **hp}
        valid_keys = set(Cfg.__dataclass_fields__.keys())
        cfg_dict = {k: v for k, v in cfg_dict.items() if k in valid_keys}
        cfg = Cfg(**cfg_dict)

        print(f"\n── {nombre} con SWA (últimas 20 épocas) ──")
        t0 = time.time()
        datos = preparar("B", modo="final", cfg=cfg, tipo="global")
        loaders = {
            "train": hacer_loader(datos["X_train"], datos["y_train"], cfg.batch, True),
            "val": hacer_loader(datos["X_val"], datos["y_val"], cfg.batch, False),
            "eval": hacer_loader(datos["X_eval"], datos["y_eval"], cfg.batch, False),
        }
        probs_l = []
        for semilla in SEEDS_DEFAULT:
            fijar_semilla(semilla)
            modelo = crear_modelo(cfg, datos["n_features"])
            swa_model = AveragedModel(modelo)
            w = pesos_clase(datos["y_train"], cfg.class_weight)
            crit = criterio_perdida(cfg, w)
            opt = optim.AdamW(modelo.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)
            swa_start = 40
            swa_scheduler = SWALR(opt, swa_lr=cfg.lr * 0.5)
            for ep in range(1, cfg.epochs + 1):
                modelo.train()
                for Xb, yb in loaders["train"]:
                    Xb, yb = Xb.to(DEVICE), yb.to(DEVICE)
                    opt.zero_grad()
                    loss = crit(modelo(Xb), yb)
                    loss.backward()
                    nn.utils.clip_grad_norm_(modelo.parameters(), cfg.grad_clip)
                    opt.step()
                if ep >= swa_start:
                    swa_model.update_parameters(modelo)
                    swa_scheduler.step()
            # BN update para SWA
            torch.optim.swa_utils.update_bn(loaders["train"], swa_model, device=DEVICE)
            probs = predecir_probs(swa_model, loaders["eval"])
            probs_l.append(probs)
        probs_ens = np.mean(probs_l, axis=0)
        pred = probs_ens.argmax(1)
        met = backtest_metricas(pred, datos["y_eval"], datos["r_eval"], datos["tk_eval"])
        filas.append({"modelo": nombre, "tecnica": "SWA (start=40, avg últimas 40 épocas)",
                      "f1": met["f1_macro"], "sharpe": met.get("sharpe", 0),
                      "win_rate": met.get("win_rate", 0), "pf": met.get("profit_factor", 0),
                      "max_dd": met.get("max_dd", 0),
                      "segundos": round(time.time() - t0, 1)})
        print(f"  F1={met['f1_macro']:.4f} Sharpe={met.get('sharpe',0):+.3f} "
              f"MaxDD={met.get('max_dd',0):.3f}  ({time.time()-t0:.1f}s)")

    df = pd.DataFrame(filas)
    df.to_csv(OUT / "swa.csv", index=False)
    print(f"\n✓ Guardado en {OUT}/swa.csv")
    return df


# ════════════════════════════════════════════════════════════════════════════
# PASO 5 — RECENCY WEIGHTING EN LR/XGB
# ════════════════════════════════════════════════════════════════════════════

def paso_recency():
    print("=" * 70)
    print("PASO 5 — RECENCY WEIGHTING TEMPORAL EN LR/XGB")
    print("=" * 70)
    from common_v5 import preparar_tabular
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.utils.class_weight import compute_class_weight
    import xgboost as xgb

    with open("RESULTADOS_OPTIMIZADOS/v5/ganadores_clasicos.json") as f:
        gan_cls = json.load(f)

    def _dias_desde_max(fechas):
        """Días entre cada fecha y el máximo, como float array."""
        f = pd.to_datetime(pd.Series(fechas))
        dias = (f.max() - f).dt.days.values.astype(float)
        return dias

    def _build_lr(hp):
        penalty = hp.get("penalty", "l2")
        C = hp.get("C", 1.0)
        kw = dict(penalty=penalty, C=C, solver="saga", max_iter=5000,
                  class_weight=None, random_state=42, n_jobs=-1, tol=1e-4)
        if penalty == "elasticnet":
            kw["l1_ratio"] = hp.get("l1_ratio", 0.5)
        return LogisticRegression(**kw)

    def _build_xgb(hp):
        return xgb.XGBClassifier(
            n_estimators=int(hp.get("n_estimators", 500)),
            max_depth=int(hp.get("max_depth", 6)),
            learning_rate=float(hp.get("learning_rate", 0.05)),
            subsample=float(hp.get("subsample", 0.8)),
            colsample_bytree=float(hp.get("colsample_bytree", 0.8)),
            min_child_weight=int(hp.get("min_child_weight", 1)),
            reg_alpha=float(hp.get("reg_alpha", 0.0)),
            reg_lambda=float(hp.get("reg_lambda", 1.0)),
            gamma=float(hp.get("gamma", 0.0)),
            objective="multi:softprob", num_class=3,
            tree_method="hist", device="cuda",
            random_state=42, eval_metric="mlogloss", verbosity=0,
        )

    filas = []
    for nombre in ["LR", "XGBoost"]:
        hp = gan_cls[nombre]["params"]
        escalador = hp.get("escalador", "standard")
        print(f"\n── {nombre} (penalty={hp.get('penalty','n/a')}, escalador={escalador}) ──")

        datos = preparar_tabular("B", modo="final", tipo="global", escalador=escalador)
        Xtr, ytr = datos["X_train"], datos["y_train"]
        Xva, yva = datos["X_val"], datos["y_val"]
        Xev, yev = datos["X_eval"], datos["y_eval"]
        r_ev, tk_ev = datos["r_eval"], datos["tk_eval"]

        dias_tr = _dias_desde_max(datos["f_train"])
        w_cls_tr = compute_class_weight("balanced", classes=np.array([0, 1, 2]), y=ytr)

        mejor = {"tau": None, "f1_val": -1}
        for tau_dias in [30, 90, 180, 365, 730, 1500, 3000, 999999]:
            w_time = np.exp(-dias_tr / tau_dias)
            w_final = w_time * np.array([w_cls_tr[c] for c in ytr])
            if nombre == "LR":
                model = _build_lr(hp)
            else:
                model = _build_xgb(hp)
            model.fit(Xtr, ytr, sample_weight=w_final)
            probs_va = model.predict_proba(Xva)
            f1_val = f1_score(yva, probs_va.argmax(1), average="macro", zero_division=0)
            marca = " *" if f1_val > mejor["f1_val"] else ""
            print(f"  τ={tau_dias:>7} días → F1_val={f1_val:.4f}{marca}")
            if f1_val > mejor["f1_val"]:
                mejor = {"tau": tau_dias, "f1_val": f1_val}

        # Refit con train+val con el mejor τ y evaluar en test 2025
        tau_dias = mejor["tau"]
        Xtv = np.vstack([Xtr, Xva])
        ytv = np.concatenate([ytr, yva])
        f_tv = np.concatenate([datos["f_train"], datos["f_val"]])
        dias_tv = _dias_desde_max(f_tv)
        w_cls_tv = compute_class_weight("balanced", classes=np.array([0, 1, 2]), y=ytv)
        w_time_tv = np.exp(-dias_tv / tau_dias)
        w_tv = w_time_tv * np.array([w_cls_tv[c] for c in ytv])

        if nombre == "LR":
            model = _build_lr(hp)
        else:
            model = _build_xgb(hp)
        model.fit(Xtv, ytv, sample_weight=w_tv)
        probs_ev = model.predict_proba(Xev)
        pred = probs_ev.argmax(1)
        met = backtest_metricas(pred, yev, r_ev, tk_ev)
        filas.append({"modelo": nombre, "tecnica": f"recency (τ={tau_dias} d)",
                      "f1": met["f1_macro"], "sharpe": met.get("sharpe", 0),
                      "win_rate": met.get("win_rate", 0),
                      "profit_factor": met.get("profit_factor", 0),
                      "max_dd": met.get("max_dd", 0)})
        print(f"  → Mejor τ={tau_dias} d, TEST 2025: F1={met['f1_macro']:.4f} "
              f"Sharpe={met.get('sharpe',0):+.3f} WR={met.get('win_rate',0):.3f}")

    df = pd.DataFrame(filas)
    df.to_csv(OUT / "recency.csv", index=False)
    print(f"\n✓ Guardado en {OUT}/recency.csv")
    return df


# ════════════════════════════════════════════════════════════════════════════
# PASO 6 — CONSOLIDAR
# ════════════════════════════════════════════════════════════════════════════

def paso_consolidar():
    print("=" * 70)
    print("PASO 6 — CONSOLIDAR RESULTADOS")
    print("=" * 70)
    filas = []
    # Baseline v5
    for m, met in BASELINE_V5.items():
        filas.append({"modelo": m, "tecnica": "baseline_v5",
                      "f1": met["f1"], "sharpe": met["sharpe"],
                      "win_rate": met["win_rate"], "pf": met["profit_factor"],
                      "max_dd": met["max_dd"]})
    # Cargar resultados
    for archivo, prefijo in [("calibracion.csv", "calibr"), ("blending.csv", "blend"),
                             ("swa.csv", "swa"), ("recency.csv", "recency")]:
        f = OUT / archivo
        if f.exists():
            sub = pd.read_csv(f)
            # normalizar columnas
            if "f1_macro" in sub.columns and "f1" not in sub.columns:
                sub["f1"] = sub["f1_macro"]
            for _, r in sub.iterrows():
                filas.append({
                    "modelo": r.get("modelo", "-"), "tecnica": f"{prefijo}:{r['tecnica']}",
                    "f1": r.get("f1", 0), "sharpe": r.get("sharpe", 0),
                    "win_rate": r.get("win_rate", 0), "pf": r.get("pf", 0),
                    "max_dd": r.get("max_dd", 0),
                })
    df = pd.DataFrame(filas)
    df = df.sort_values(["sharpe"], ascending=False)
    df.to_csv(CSV_RESULTADOS, index=False)
    print(df.to_string(index=False))
    print(f"\n✓ Consolidado en {CSV_RESULTADOS}")
    return df


# ════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", required=True,
                    choices=["preds_val", "calibrar", "blending", "swa", "recency",
                             "consolidar", "all"])
    args = ap.parse_args()

    if args.step in ("preds_val", "all"):
        paso_preds_val()
    if args.step in ("calibrar", "all"):
        paso_calibrar()
    if args.step in ("blending", "all"):
        paso_blending()
    if args.step in ("swa", "all"):
        paso_swa()
    if args.step in ("recency", "all"):
        paso_recency()
    if args.step in ("consolidar", "all"):
        paso_consolidar()


if __name__ == "__main__":
    main()
