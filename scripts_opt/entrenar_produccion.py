"""
================================================================================
ENTRENAR MODELO DE PRODUCCIÓN — LR + interactions (ganador Vía 8)
================================================================================
Regenera `api/ml/artifacts/lr_elasticnet_global_expB.pkl` con el ganador
actual de la investigación (después de v0-v8):

  - LR con penalty=l2, C=0.000165 (ganador Optuna v5)
  - RobustScaler (ganador Optuna v5)
  - 61 features base + 15 productos (interactions, Vía 8)
  - Pesos de clase "balanced" con el de HOLD multiplicado por PESO_HOLD
    (elegido en scripts_opt/ajuste_hold_rolling.py con los años 2019-2024 y
    confirmado en 2025/2026; ver docs/ANALISIS_HOLD_Y_GLOBAL.md §8). No cambia
    el target: solo cuánto pesa cada clase al entrenar.
  - Entrenado sobre TODO 2018-2025 (para producción, no evaluación)

Salidas actualizadas:
  api/ml/artifacts/lr_elasticnet_global_expB.pkl        (76 features)
  api/ml/artifacts/lr_elasticnet_global_expB.metrics.json (nuevas métricas)
  api/ml/artifacts/interaction_pairs.json               (los 15 pares)

Ver INVESTIGACION_COMPLETA.md §7 para el razonamiento completo.
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import sys, json, pickle, functools, warnings
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass
print = functools.partial(print, flush=True)
warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).parent))
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import f1_score, classification_report

from common import TICKERS, EXCLUIR_COLS, cargar_raw

OUT_ARTIFACTS = Path("api/ml/artifacts")
OUT_ARTIFACTS.mkdir(parents=True, exist_ok=True)


# ════════════════════════════════════════════════════════════════════════════
# CONFIG — Ganador de la investigación
# ════════════════════════════════════════════════════════════════════════════

# Hiperparámetros del LR ganador (Optuna v5)
LR_HP = {
    "penalty": "l2",
    "C": 0.00016491236228800314,
    "class_weight": "balanced",
    "solver": "saga",
    "max_iter": 5000,
    "tol": 1e-4,
    "random_state": 42,
    "n_jobs": -1,
}

# Peso extra de la clase HOLD al entrenar (1.0 = "balanced" puro). Ver docstring.
PESO_HOLD = 0.90
CONFIG_ID = f"LR-v8-interactions-holdw{int(round(PESO_HOLD * 100)):03d}"

ANALISIS = Path("RESULTADOS_OPTIMIZADOS/analisis_hold")


def pesos_de_clase(y: np.ndarray, peso_hold: float) -> dict:
    """'balanced' de scikit-learn (n / (3·n_c)) con HOLD (clase 1) × peso_hold."""
    frec = np.bincount(y, minlength=3) / len(y)
    return {c: float(1 / (3 * frec[c]) * (peso_hold if c == 1 else 1.0)) for c in range(3)}


def evidencia_ajuste_hold() -> dict:
    """Resume la evidencia del peso de HOLD desde los CSV de los análisis."""
    out = {"peso_hold": PESO_HOLD,
           "seleccion": "max F1-macro medio 2019-2024 por origen rodante (ajuste_hold_rolling.py)"}
    det = ANALISIS / "7_reglas_alternativas_detalle.csv"
    if det.exists():
        d = pd.read_csv(det)
        regla = f"reentrenar con peso HOLD x{PESO_HOLD:g}"
        for nombre, r in [("balanced", "argmax normal (k=1)"), (f"hold_x{PESO_HOLD:g}", regla)]:
            sub = d[d.regla == r]
            dev = sub[sub.anio.between(2019, 2024)]
            out[nombre] = {
                "dev_2019_2024": {k: round(float(dev[k].mean()), 4)
                                  for k in ["f1_macro", "kappa", "sharpe", "pred_hold_pct", "real_hold_pct"]},
                "test_2025": {k: round(float(sub[sub.anio == 2025][k].iloc[0]), 4)
                              for k in ["f1_macro", "kappa", "sharpe", "pred_hold_pct", "real_hold_pct"]},
            }
    conf = ANALISIS / "8_confirmacion_2026.csv"
    if conf.exists():
        c = pd.read_csv(conf)
        out["oos_2026"] = {row.regla: {k: round(float(getattr(row, k)), 4)
                                       for k in ["f1_macro", "kappa", "sharpe", "pred_hold_pct", "real_hold_pct"]}
                           for row in c.itertuples()}
    return out


# Features base (61) — deben coincidir con api/ml/features.py::FEATURE_COLUMNS
FEATURES_BASE = [
    "ret_1d", "ret_2d", "ret_3d", "ret_5d", "ret_10d",
    "mom_5d", "mom_10d", "mom_20d", "mom_60d",
    "dist_ma10", "dist_ma20", "dist_ma30", "dist_ma50", "dist_ma200",
    "cruce_ma10_ma50", "cruce_ma20_ma50", "cruce_ma50_ma200", "pendiente_ma20",
    "atr_14", "atr_norm",
    "vol_5d", "vol_10d", "vol_20d", "vol_60d",
    "vol_ratio_5_20", "vol_ratio_20_60",
    "rsi_14", "rsi_7",
    "macd", "macd_sig", "macd_hist",
    "stoch_k", "stoch_d", "stoch_diff", "williams_r",
    "vol_log", "vol_ratio", "obv_ratio", "obv_pendiente",
    "vwap_dist", "cmf_20", "mfi_14", "vol_trend",
    "rango_rel", "cambio_intra", "cuerpo_rel", "sombra_sup", "sombra_inf",
    "gap_apertura", "hl_ratio",
    "dia_sin", "dia_cos", "mes_sin", "mes_cos", "semana_mes",
    "SP500_ret", "SP500_vol20", "SP500_mom20",
    "VIX", "VIX_change", "VIX_norm",
]

# Los 10 features con mayor |coef| en LR baseline (v8 los descubrió)
TOP10 = ["VIX_norm", "vol_log", "VIX", "SP500_vol20", "SP500_ret",
         "rango_rel", "atr_norm", "vol_ratio", "SP500_mom20", "sombra_sup"]


def elegir_pares_interaction(top: list[str], n_pares: int = 15, seed: int = 42):
    """Los 15 pares elegidos por via8_dataset.py con seed=42 (reproducible)."""
    pares_all = [(top[i], top[j]) for i in range(len(top)) for j in range(i+1, len(top))]
    rng = np.random.default_rng(seed)
    idxs = rng.choice(len(pares_all), size=n_pares, replace=False)
    return [pares_all[i] for i in idxs]


# ════════════════════════════════════════════════════════════════════════════
# PIPELINE
# ════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("ENTRENAMIENTO DE MODELO DE PRODUCCIÓN")
    print("=" * 70)

    # 1) Cargar los 7 tickers
    print("\n[1] Cargando 7 tickers...")
    dfs = {}
    for tk in TICKERS:
        df = cargar_raw(tk)
        # Filtrar sólo 2018-2025 (Exp B extendido a test)
        m = (df.index >= "2018-01-01") & (df.index <= "2025-12-31")
        dfs[tk] = df[m].copy()
        print(f"    {tk}: {len(dfs[tk])} filas")

    # 2) Elegir pares de interactions
    pares_inter = elegir_pares_interaction(TOP10, n_pares=15, seed=42)
    print(f"\n[2] Pares de interactions ({len(pares_inter)}):")
    for a, b in pares_inter:
        print(f"    {a} × {b}")

    # 3) Construir X, y por ticker con features base + interactions
    print("\n[3] Construyendo dataset (base + interactions)...")
    X_all, y_all = [], []
    feat_cols = FEATURES_BASE + [f"{a}_x_{b}" for a, b in pares_inter]

    for tk in TICKERS:
        df = dfs[tk]
        # verificar features
        missing = [c for c in FEATURES_BASE if c not in df.columns]
        if missing:
            raise ValueError(f"{tk} no tiene features: {missing[:5]}...")

        X_base = df[FEATURES_BASE].copy()
        for a, b in pares_inter:
            X_base[f"{a}_x_{b}"] = df[a] * df[b]

        # eliminar NaN
        valid = X_base.notna().all(axis=1) & df["target"].notna()
        X_base = X_base[valid]
        y = df.loc[valid, "target"].astype(int).values
        X_all.append(X_base[feat_cols].values)
        y_all.append(y)

    X = np.vstack(X_all)
    y = np.concatenate(y_all)
    print(f"    Dataset final: {X.shape[0]} filas × {X.shape[1]} features")
    print(f"    Distribución target: {dict(zip(*np.unique(y, return_counts=True)))}")

    # 4) Escalar con RobustScaler (fit sobre TODO, para producción)
    print("\n[4] Escalando con RobustScaler (fit sobre train completo)...")
    scaler = RobustScaler()
    X_scaled = scaler.fit_transform(X)

    # 5) Entrenar LR (con TODOS los datos disponibles, sin validación separada
    #    porque es el modelo de PRODUCCIÓN — la evaluación honesta está en v8)
    print("\n[5] Entrenando LR con TODOS los datos 2018-2025...")
    hp = {**LR_HP, "class_weight": pesos_de_clase(y, PESO_HOLD)}
    print(f"    Hiperparámetros: {hp}")
    model = LogisticRegression(**hp)
    model.fit(X_scaled, y)

    # 6) F1 in-sample (referencia — no es evaluación honesta)
    pred = model.predict(X_scaled)
    f1_is = f1_score(y, pred, average="macro", zero_division=0)
    print(f"\n[6] F1-macro in-sample (para diagnóstico): {f1_is:.4f}")
    print(f"    Distribución de predicciones: {dict(zip(*np.unique(pred, return_counts=True)))}")

    # 7) Guardar
    print("\n[7] Guardando artefactos...")
    obj = {
        "model": model,
        "scaler": scaler,
        "hp": {
            **hp,
            "peso_hold": PESO_HOLD,
            "escalador": "robust",
            "config_id": CONFIG_ID,
            "fecha_entrenamiento": datetime.now().isoformat(),
            "n_features_base": len(FEATURES_BASE),
            "n_features_total": len(feat_cols),
            "n_pares_interactions": len(pares_inter),
            "rango_train": "2018-01-01 a 2025-12-31 (todos los datos)",
            "n_samples": int(len(y)),
            "f1_macro_test_2025_via8": 0.4133,  # de via8/interactions.csv (evalua sobre 2025)
            "sharpe_test_2025_via8": 0.914,
            "notas": "Ganador de Vía 8 + peso de HOLD. Ver RESULTADOS_OPTIMIZADOS/docs/ANALISIS_HOLD_Y_GLOBAL.md",
        },
        "feat_cols": feat_cols,
        "config_id": CONFIG_ID,
        "interaction_pairs": pares_inter,   # para inferencia
    }

    pkl_path = OUT_ARTIFACTS / "lr_elasticnet_global_expB.pkl"
    # Backup del anterior
    if pkl_path.exists():
        backup = OUT_ARTIFACTS / f"lr_elasticnet_global_expB_{datetime.now():%Y%m%d_%H%M%S}.pkl.bak"
        pkl_path.rename(backup)
        print(f"    Backup del anterior: {backup}")

    with open(pkl_path, "wb") as f:
        pickle.dump(obj, f)
    size_kb = pkl_path.stat().st_size / 1024
    print(f"    Modelo guardado: {pkl_path} ({size_kb:.1f} KB)")

    # 8) Guardar pares en JSON separado (para inspección y uso en features.py)
    pairs_json = OUT_ARTIFACTS / "interaction_pairs.json"
    with open(pairs_json, "w") as f:
        json.dump({"pairs": pares_inter, "seed": 42, "top10_used": TOP10,
                   "generated_by": "scripts_opt/entrenar_produccion.py"},
                  f, indent=2)
    print(f"    Pares guardados: {pairs_json}")

    # 9) Actualizar metrics.json
    metrics_path = OUT_ARTIFACTS / "lr_elasticnet_global_expB.metrics.json"
    metrics = {
        "modelo": "LR + interactions (Vía 8) con peso de HOLD ajustado",
        "config_id": CONFIG_ID,
        "n_features": len(feat_cols),
        "n_features_base": len(FEATURES_BASE),
        "n_interactions": len(pares_inter),
        "hp": {
            "penalty": LR_HP["penalty"],
            "C": LR_HP["C"],
            "class_weight": "balanced",
            "peso_hold": PESO_HOLD,
            "class_weight_efectivo": hp["class_weight"],
            "escalador": "robust",
            "solver": LR_HP["solver"],
        },
        "metricas_test_2025_via8_exp_b_global": {
            "f1_macro": 0.4133,
            "sharpe": 0.914,
            "win_rate": 0.532,
            "profit_factor": None,
            "max_dd": -0.523,
            "signal_buy_pct": None,
            "signal_hold_pct": None,
            "signal_sell_pct": None,
        },
        "baseline_lr_sin_interactions_test_2025": {
            "f1_macro": 0.3907,
            "sharpe": 0.683,
        },
        "delta_vs_baseline": {"f1_macro": +0.0226, "sharpe": +0.231},
        "nota_test_2025": ("Las cifras de Vía 8 son de TEST 2025 y con pesos 'balanced' puros. En "
                           "validación 2024 el LR con y sin interactions empatan (F1 0.325 vs 0.326)."),
        "ajuste_hold": evidencia_ajuste_hold(),
        "entrenamiento": {
            "rango": "2018-01-01 a 2025-12-31",
            "n_samples": int(len(y)),
            "tickers": TICKERS,
            "estrategia": "global (un modelo para los 7)",
            "fecha": datetime.now().isoformat(),
        },
        "referencia_investigacion": "RESULTADOS_OPTIMIZADOS/INVESTIGACION_COMPLETA.md",
    }
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"    Métricas guardadas: {metrics_path}")

    print("\n" + "=" * 70)
    print("✓ ENTRENAMIENTO COMPLETO")
    print("=" * 70)
    print(f"  Ganador: LR + 15 interactions (76 features total), peso HOLD x{PESO_HOLD}")
    print(f"  F1 test 2025 (via8): 0.4133 vs baseline 0.3907 (+0.023)")
    print(f"  Sharpe test 2025 (via8): +0.914 vs baseline +0.683 (+0.231)")
    print(f"  Modelo listo en {pkl_path}")


if __name__ == "__main__":
    main()
