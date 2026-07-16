"""
================================================================================
SCRIPT 05 — ENTRENAMIENTO: XGBOOST
================================================================================
Entrena modelos XGBoost con búsqueda de hiperparámetros mediante Optuna.
Incluye SHAP para interpretabilidad post-entrenamiento.
Estrategias: por ticker y modelo global.

Métricas reportadas:
  Clasificación : f1_macro, f1_buy, f1_sell, f1_buy_sell_avg, accuracy
  Económicas    : cumul_return_90d, return_vs_bh_90d, sharpe_90d,
                  max_drawdown_90d, win_rate_90d, profit_factor_90d
  Distribución  : signal_distribution (% BUY / HOLD / SELL predichos)

Salida: tesis_ml_stocks/04_models/xgboost/
    por_ticker/experimento_[A|B|C]/{TICKER}_modelo.json
    por_ticker/experimento_[A|B|C]/{TICKER}_metricas.json
    por_ticker/experimento_[A|B|C]/{TICKER}_shap.png
    global/experimento_[A|B|C]/modelo_global.json
    resultados_xgb.csv

Dependencias: pip install xgboost optuna shap matplotlib scikit-learn pandas pyarrow
================================================================================
"""

import json
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.metrics import (f1_score, classification_report, confusion_matrix)
from sklearn.utils.class_weight import compute_sample_weight

warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════════════════════

TICKERS    = ["AAPL", "NVDA", "TSLA", "AMZN", "MSFT", "GOOGL", "META"]
DATA_DIR   = Path("tesis_ml_stocks/03_model_datasets/xgboost")
RAW_DIR    = Path("tesis_ml_stocks/01_raw_datasets")
OUTPUT_DIR = Path("tesis_ml_stocks/04_models/xgboost")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CLASES  = [0, 1, 2]
NOMBRES = {0: "SELL", 1: "HOLD", 2: "BUY"}

EXPERIMENTOS = {
    "A": "Máximo historial",
    "B": "Ciclo completo — RECOMENDADO",
    "C": "Era moderna",
}

EXPERIMENTOS_FECHAS = {
    "A": {"test": ("2024-01-01", "2025-12-31")},
    "B": {"test": ("2025-01-01", "2025-12-31")},
    "C": {"test": ("2025-01-01", "2025-12-31")},
}

N_TRIALS       = 30
VENTANA_ECON   = 90


# ══════════════════════════════════════════════════════════════════════════════
# UTILIDADES — CARGA DE DATOS
# ══════════════════════════════════════════════════════════════════════════════

def cargar_splits(ticker, exp_id):
    base = DATA_DIR / f"experimento_{exp_id}"
    train = pd.read_parquet(base / f"{ticker}_train.parquet")
    val   = pd.read_parquet(base / f"{ticker}_val.parquet")
    test  = pd.read_parquet(base / f"{ticker}_test.parquet")
    feat_cols = [c for c in train.columns if c != "target"]
    return (train[feat_cols].values, train["target"].values,
            val[feat_cols].values,   val["target"].values,
            test[feat_cols].values,  test["target"].values,
            feat_cols)


def cargar_retornos_test(ticker: str, exp_id: str) -> np.ndarray:
    """
    Carga los retornos forward reales del período de prueba desde el parquet crudo.
    Se usan para calcular métricas económicas sin lookahead.
    """
    path = RAW_DIR / f"{ticker}_raw.parquet"
    if not path.exists():
        return None
    df = pd.read_parquet(path)
    fechas = EXPERIMENTOS_FECHAS[exp_id]["test"]
    mask = (df.index >= fechas[0]) & (df.index <= fechas[1])
    df_test = df[mask]
    return df_test["r_forward"].values if "r_forward" in df_test.columns else None


# ══════════════════════════════════════════════════════════════════════════════
# MÉTRICAS ECONÓMICAS
# ══════════════════════════════════════════════════════════════════════════════

def calcular_metricas_economicas(y_pred: np.ndarray,
                                  r_forward: np.ndarray,
                                  ventana: int = VENTANA_ECON) -> dict:
    """
    Calcula métricas económicas sobre los primeros 'ventana' días del test.

    Lógica de simulación:
      BUY  (2): posición larga  → retorno = +r_forward
      SELL (0): posición corta  → retorno = -r_forward
      HOLD (1): sin posición    → retorno =  0

    Sin costos de transacción ni slippage (backtesting básico).
    """
    n = min(len(y_pred), len(r_forward))
    pred = y_pred[:n]
    ret  = r_forward[:n]

    r_strat = np.where(pred == 2,  ret,
              np.where(pred == 0, -ret, 0.0))

    # Retorno acumulado
    cumul_return = float(np.expm1(np.sum(r_strat)))

    # Retorno buy-and-hold en el mismo período
    bh_return    = float(np.expm1(np.sum(ret)))
    return_vs_bh = cumul_return - bh_return

    # Sharpe ratio anualizado (tasa libre de riesgo = 0)
    sharpe = float((r_strat.mean() / r_strat.std()) * np.sqrt(252)) \
             if r_strat.std() > 1e-8 else 0.0

    # Máximo drawdown
    equity      = np.exp(np.cumsum(r_strat))
    rolling_max = np.maximum.accumulate(equity)
    drawdowns   = (equity - rolling_max) / (rolling_max + 1e-8)
    max_drawdown = float(drawdowns.min())

    # Win rate (excluye días HOLD)
    operaciones = r_strat[pred != 1]
    win_rate    = float((operaciones > 0).mean()) if len(operaciones) > 0 else 0.0

    # Profit factor
    ganancias     = operaciones[operaciones > 0].sum()
    perdidas      = abs(operaciones[operaciones < 0].sum())
    profit_factor = float(ganancias / perdidas) if perdidas > 1e-8 else np.inf

    return {
        "cumul_return_test":  round(cumul_return,  4),
        "return_vs_bh_test":  round(return_vs_bh,  4),
        "sharpe_test":        round(sharpe,         4),
        "max_drawdown_test":  round(max_drawdown,   4),
        "win_rate_test":      round(win_rate,       4),
        "profit_factor_test": round(profit_factor,  4)
                                     if profit_factor != np.inf else None,
    }


# ══════════════════════════════════════════════════════════════════════════════
# MÉTRICAS DE CLASIFICACIÓN
# ══════════════════════════════════════════════════════════════════════════════

def calcular_metricas(y_true: np.ndarray,
                       y_pred: np.ndarray,
                       split_name: str,
                       r_forward: np.ndarray = None) -> dict:
    """
    Calcula métricas de clasificación y, si se proporcionan retornos,
    también las métricas económicas sobre la ventana de 90 días.
    """
    report = classification_report(y_true, y_pred,
                                   target_names=["SELL", "HOLD", "BUY"],
                                   output_dict=True, zero_division=0)
    cm = confusion_matrix(y_true, y_pred, labels=CLASES).tolist()

    # Distribución de señales predichas
    signal_dist = {
        NOMBRES[k]: {
            "n":   int((y_pred == k).sum()),
            "pct": round((y_pred == k).mean() * 100, 1),
        }
        for k in CLASES
    }

    metricas = {
        "split":               split_name,
        # ── Clasificación ────────────────────────────────────────────────────
        "f1_macro":            round(f1_score(y_true, y_pred, average="macro",
                                              zero_division=0), 4),
        "f1_buy":              round(report["BUY"]["f1-score"],   4),
        "f1_hold":             round(report["HOLD"]["f1-score"],  4),
        "f1_sell":             round(report["SELL"]["f1-score"],  4),
        "f1_buy_sell_avg":     round((report["BUY"]["f1-score"] +
                                      report["SELL"]["f1-score"]) / 2, 4),
        "precision_buy":       round(report["BUY"]["precision"],  4),
        "precision_sell":      round(report["SELL"]["precision"], 4),
        "recall_buy":          round(report["BUY"]["recall"],     4),
        "recall_sell":         round(report["SELL"]["recall"],    4),
        "accuracy":            round(report["accuracy"],          4),
        # ── Distribución de señales ──────────────────────────────────────────
        "signal_distribution": signal_dist,
        # ── Matriz de confusión ──────────────────────────────────────────────
        "confusion_matrix":    cm,
        "n_samples":           int(len(y_true)),
        "dist_real":           {NOMBRES[k]: int((y_true == k).sum()) for k in CLASES},
    }

    # Métricas económicas (solo si se proporcionan retornos)
    if r_forward is not None and len(r_forward) >= VENTANA_ECON:
        eco = calcular_metricas_economicas(y_pred, r_forward, VENTANA_ECON)
        metricas.update(eco)

    return metricas


# ══════════════════════════════════════════════════════════════════════════════
# MODELO XGBOOST
# ══════════════════════════════════════════════════════════════════════════════

def construir_modelo_xgb(params):
    import xgboost as xgb
    return xgb.XGBClassifier(
        n_estimators      = params["n_estimators"],
        max_depth         = params["max_depth"],
        learning_rate     = params["learning_rate"],
        subsample         = params["subsample"],
        colsample_bytree  = params["colsample_bytree"],
        min_child_weight  = params["min_child_weight"],
        gamma             = params["gamma"],
        reg_alpha         = params["reg_alpha"],
        reg_lambda        = params["reg_lambda"],
        objective         = "multi:softprob",
        num_class         = 3,
        eval_metric       = "mlogloss",
        tree_method       = "hist",
        device            = "cuda",
        random_state      = 42,
        n_jobs            = -1,
        verbosity         = 0,
    )


def buscar_hiperparametros(X_tr, y_tr, X_va, y_va):
    """Búsqueda bayesiana de hiperparámetros con Optuna."""
    try:
        import optuna
        optuna.logging.set_verbosity(optuna.logging.WARNING)
    except ImportError:
        print("      ⚠ Optuna no instalado. Usando parámetros por defecto.")
        return {
            "n_estimators": 300, "max_depth": 5, "learning_rate": 0.05,
            "subsample": 0.8, "colsample_bytree": 0.8, "min_child_weight": 3,
            "gamma": 0.1, "reg_alpha": 0.1, "reg_lambda": 1.0,
        }

    pesos_tr = compute_sample_weight("balanced", y=y_tr)

    def objective(trial):
        params = {
            "n_estimators":     trial.suggest_int("n_estimators", 100, 600),
            "max_depth":        trial.suggest_int("max_depth", 3, 8),
            "learning_rate":    trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
            "subsample":        trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
            "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
            "gamma":            trial.suggest_float("gamma", 0.0, 1.0),
            "reg_alpha":        trial.suggest_float("reg_alpha", 0.0, 2.0),
            "reg_lambda":       trial.suggest_float("reg_lambda", 0.5, 3.0),
        }
        modelo = construir_modelo_xgb(params)
        modelo.fit(X_tr, y_tr, sample_weight=pesos_tr,
                   eval_set=[(X_va, y_va)], verbose=False)
        f1 = f1_score(y_va, modelo.predict(X_va), average="macro", zero_division=0)
        return 1.0 - f1

    estudio = optuna.create_study(direction="minimize",
                                   sampler=optuna.samplers.TPESampler(seed=42))
    estudio.optimize(objective, n_trials=N_TRIALS, show_progress_bar=False)
    return estudio.best_params


def graficar_shap(modelo, X, feat_cols, ruta):
    """Genera gráfica SHAP de importancia de features."""
    try:
        import shap
        explainer = shap.TreeExplainer(modelo)
        sv = explainer.shap_values(X)
        if isinstance(sv, list):
            mean_abs = np.mean([np.abs(s).mean(axis=0) for s in sv], axis=0)
        elif sv.ndim == 3:
            mean_abs = np.abs(sv).mean(axis=(0, 2))
        else:
            mean_abs = np.abs(sv).mean(axis=0)
        df_shap = pd.DataFrame({"feature": feat_cols, "shap": mean_abs})
        df_shap = df_shap.sort_values("shap", ascending=True).tail(20)
        fig, ax = plt.subplots(figsize=(10, 7))
        ax.barh(df_shap["feature"], df_shap["shap"], color="#2ecc71")
        ax.set_title("SHAP Mean |value| — Top 20 features", fontsize=11)
        ax.set_xlabel("Mean |SHAP value|")
        ax.tick_params(axis="y", labelsize=8)
        plt.tight_layout()
        fig.savefig(ruta, dpi=120, bbox_inches="tight")
        plt.close(fig)
    except ImportError:
        pass


# ══════════════════════════════════════════════════════════════════════════════
# ENTRENAMIENTO POR TICKER
# ══════════════════════════════════════════════════════════════════════════════

def entrenar_por_ticker():
    print("\n" + "═"*65)
    print("  XGBOOST — POR TICKER")
    print("═"*65)

    resultados = []

    for exp_id, exp_desc in EXPERIMENTOS.items():
        print(f"\n── Experimento {exp_id}: {exp_desc}")
        dir_out = OUTPUT_DIR / "por_ticker" / f"experimento_{exp_id}"
        dir_out.mkdir(parents=True, exist_ok=True)

        for ticker in TICKERS:
            print(f"  {ticker}...", flush=True)
            try:
                X_tr, y_tr, X_va, y_va, X_te, y_te, feat_cols = \
                    cargar_splits(ticker, exp_id)
            except FileNotFoundError:
                print("    sin datos")
                continue

            # Retornos reales del período de prueba
            r_fwd_test = cargar_retornos_test(ticker, exp_id)

            # Búsqueda de hiperparámetros
            print(f"    Buscando hiperparámetros ({N_TRIALS} trials)...", end=" ")
            mejores_params = buscar_hiperparametros(X_tr, y_tr, X_va, y_va)
            print("OK")

            # Modelo final con train + val
            X_full     = np.vstack([X_tr, X_va])
            y_full     = np.concatenate([y_tr, y_va])
            pesos_full = compute_sample_weight("balanced", y=y_full)
            modelo_final = construir_modelo_xgb(mejores_params)
            modelo_final.fit(X_full, y_full, sample_weight=pesos_full, verbose=False)

            # Modelo de validación (solo train)
            pesos_tr  = compute_sample_weight("balanced", y=y_tr)
            modelo_val = construir_modelo_xgb(mejores_params)
            modelo_val.fit(X_tr, y_tr, sample_weight=pesos_tr,
                           eval_set=[(X_va, y_va)], verbose=False)

            # Métricas
            met_val  = calcular_metricas(y_va, modelo_val.predict(X_va),  "val")
            met_test = calcular_metricas(y_te, modelo_final.predict(X_te), "test",
                                         r_forward=r_fwd_test)

            eco = f"  Ret={met_test.get(f'cumul_return_{VENTANA_ECON}d','N/A')}  " \
                  f"Sharpe={met_test.get(f'sharpe_{VENTANA_ECON}d','N/A')}  " \
                  f"WR={met_test.get(f'win_rate_{VENTANA_ECON}d','N/A')}" \
                  if f"cumul_return_{VENTANA_ECON}d" in met_test else ""

            print(f"    Val F1={met_val['f1_macro']:.3f} "
                  f"BUY={met_val['f1_buy']:.3f} SELL={met_val['f1_sell']:.3f}  |  "
                  f"Test F1={met_test['f1_macro']:.3f} "
                  f"BUY={met_test['f1_buy']:.3f} SELL={met_test['f1_sell']:.3f}"
                  f"{eco}")

            # Guardar modelo y gráfica SHAP
            modelo_final.save_model(str(dir_out / f"{ticker}_modelo.json"))
            graficar_shap(modelo_val, X_va, feat_cols, dir_out / f"{ticker}_shap.png")

            # Guardar métricas
            meta = {
                "ticker": ticker, "experimento": exp_id,
                "tipo": "por_ticker", "modelo": "XGBoost",
                "mejores_params": mejores_params,
                "n_features": len(feat_cols), "features": feat_cols,
                "n_train": len(y_tr), "n_val": len(y_va), "n_test": len(y_te),
                "metricas_val":  met_val,
                "metricas_test": met_test,
            }
            with open(dir_out / f"{ticker}_metricas.json", "w") as f:
                json.dump(meta, f, indent=2)

            fila = {
                "modelo": "XGBoost", "tipo": "por_ticker",
                "ticker": ticker, "experimento": exp_id,
                "val_f1_macro":        met_val["f1_macro"],
                "val_f1_buy":          met_val["f1_buy"],
                "val_f1_sell":         met_val["f1_sell"],
                "test_f1_macro":       met_test["f1_macro"],
                "test_f1_buy":         met_test["f1_buy"],
                "test_f1_sell":        met_test["f1_sell"],
                "test_f1_buy_sell_avg": met_test["f1_buy_sell_avg"],
                "signal_pct_buy":      met_test["signal_distribution"]["BUY"]["pct"],
                "signal_pct_hold":     met_test["signal_distribution"]["HOLD"]["pct"],
                "signal_pct_sell":     met_test["signal_distribution"]["SELL"]["pct"],
            }
            for k in ["cumul_return_test", "return_vs_bh_test", "sharpe_test", "max_drawdown_test", "win_rate_test", "profit_factor_test"]:
                fila[k] = met_test.get(k, None)

            resultados.append(fila)

    return resultados


# ══════════════════════════════════════════════════════════════════════════════
# ENTRENAMIENTO GLOBAL
# ══════════════════════════════════════════════════════════════════════════════

def entrenar_global():
    print("\n" + "═"*65)
    print("  XGBOOST — MODELO GLOBAL")
    print("═"*65)

    resultados = []

    for exp_id, exp_desc in EXPERIMENTOS.items():
        print(f"\n── Experimento {exp_id}")
        dir_out = OUTPUT_DIR / "global" / f"experimento_{exp_id}"
        dir_out.mkdir(parents=True, exist_ok=True)

        trains, vals, tests = [], [], []
        r_fwd_tests   = []
        feat_cols_ref = None

        for ticker in TICKERS:
            try:
                X_tr, y_tr, X_va, y_va, X_te, y_te, feat_cols = \
                    cargar_splits(ticker, exp_id)
                trains.append((X_tr, y_tr))
                vals.append((X_va, y_va))
                tests.append((X_te, y_te))
                r = cargar_retornos_test(ticker, exp_id)
                if r is not None:
                    r_fwd_tests.append(r)
                if feat_cols_ref is None:
                    feat_cols_ref = feat_cols
            except FileNotFoundError:
                pass

        if not trains:
            continue

        X_tr = np.vstack([x for x,_ in trains])
        y_tr = np.concatenate([y for _,y in trains])
        X_va = np.vstack([x for x,_ in vals])
        y_va = np.concatenate([y for _,y in vals])
        X_te = np.vstack([x for x,_ in tests])
        y_te = np.concatenate([y for _,y in tests])
        r_fwd_global = np.concatenate(r_fwd_tests) if r_fwd_tests else None

        print(f"  Train={len(y_tr)}  Val={len(y_va)}  Test={len(y_te)}")
        print(f"  Buscando hiperparámetros ({N_TRIALS} trials)...", end=" ", flush=True)
        mejores_params = buscar_hiperparametros(X_tr, y_tr, X_va, y_va)
        print("OK")

        X_full     = np.vstack([X_tr, X_va])
        y_full     = np.concatenate([y_tr, y_va])
        pesos_full = compute_sample_weight("balanced", y=y_full)
        modelo_final = construir_modelo_xgb(mejores_params)
        modelo_final.fit(X_full, y_full, sample_weight=pesos_full, verbose=False)

        pesos_tr  = compute_sample_weight("balanced", y=y_tr)
        modelo_val = construir_modelo_xgb(mejores_params)
        modelo_val.fit(X_tr, y_tr, sample_weight=pesos_tr,
                       eval_set=[(X_va, y_va)], verbose=False)

        met_val  = calcular_metricas(y_va, modelo_val.predict(X_va),  "val")
        met_test = calcular_metricas(y_te, modelo_final.predict(X_te), "test",
                                     r_forward=r_fwd_global)

        print(f"  Val F1={met_val['f1_macro']:.3f}  "
              f"Test F1={met_test['f1_macro']:.3f}  "
              f"Ret={met_test.get(f'cumul_return_{VENTANA_ECON}d','N/A')}")

        modelo_final.save_model(str(dir_out / "modelo_global.json"))
        graficar_shap(modelo_val, X_va, feat_cols_ref, dir_out / "shap_global.png")

        meta = {
            "ticker": "GLOBAL", "experimento": exp_id,
            "tipo": "global", "modelo": "XGBoost",
            "mejores_params": mejores_params, "tickers_incluidos": TICKERS,
            "n_train": len(y_tr), "n_val": len(y_va), "n_test": len(y_te),
            "metricas_val":  met_val,
            "metricas_test": met_test,
        }
        with open(dir_out / "metricas_global.json", "w") as f:
            json.dump(meta, f, indent=2)

        fila = {
            "modelo": "XGBoost", "tipo": "global",
            "ticker": "GLOBAL", "experimento": exp_id,
            "val_f1_macro":        met_val["f1_macro"],
            "test_f1_macro":       met_test["f1_macro"],
            "test_f1_buy":         met_test["f1_buy"],
            "test_f1_sell":        met_test["f1_sell"],
            "test_f1_buy_sell_avg": met_test["f1_buy_sell_avg"],
            "signal_pct_buy":      met_test["signal_distribution"]["BUY"]["pct"],
            "signal_pct_hold":     met_test["signal_distribution"]["HOLD"]["pct"],
            "signal_pct_sell":     met_test["signal_distribution"]["SELL"]["pct"],
        }
        for k in ["cumul_return_test", "return_vs_bh_test", "sharpe_test", "max_drawdown_test", "win_rate_test", "profit_factor_test"]:
            fila[k] = met_test.get(k, None)

        resultados.append(fila)

    return resultados


# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE
# ══════════════════════════════════════════════════════════════════════════════

def pipeline():
    print("="*65)
    print("  SCRIPT 05 — XGBOOST")
    print("="*65)

    res = entrenar_por_ticker() + entrenar_global()
    df  = pd.DataFrame(res)
    df.to_csv(OUTPUT_DIR / "resultados_xgb.csv", index=False)

    print("\n" + "="*65)
    print("  RESUMEN — XGBOOST")
    print("="*65)
    cols_resumen = ["tipo", "ticker", "experimento",
                    "val_f1_macro", "test_f1_macro",
                    "cumul_return_test", "sharpe_test", "win_rate_test"]
    print(df[[c for c in cols_resumen if c in df.columns]].to_string(index=False))
    print(f"\n✓ Guardado en: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    pipeline()