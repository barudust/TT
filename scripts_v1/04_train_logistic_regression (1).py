"""
================================================================================
SCRIPT 04 — ENTRENAMIENTO: REGRESIÓN LOGÍSTICA
================================================================================
Entrena modelos de Regresión Logística multinomial para clasificación de señales
de trading (BUY=2, HOLD=1, SELL=0).

Estrategias:
  - Por ticker: un modelo independiente por cada una de las 7 acciones
  - Global:     un modelo único entrenado con todos los tickers combinados

Métricas reportadas:
  Clasificación : f1_macro, f1_buy, f1_sell, accuracy
  Económicas    : cumul_return_90d, return_vs_bh_90d, sharpe_90d,
                  max_drawdown_90d, win_rate_90d, profit_factor_90d
  Distribución  : signal_distribution (% BUY / HOLD / SELL predichos)

Salida: tesis_ml_stocks/04_models/logistic_regression/
    por_ticker/experimento_[A|B|C]/{TICKER}_modelo.pkl
    por_ticker/experimento_[A|B|C]/{TICKER}_metricas.json
    global/experimento_[A|B|C]/modelo_global.pkl
    global/experimento_[A|B|C]/metricas_global.json
    resultados_lr.csv   ← tabla comparativa de todos los experimentos

Dependencias: pip install scikit-learn pandas numpy pyarrow
================================================================================
"""

import json
import warnings
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (classification_report, f1_score,
                              confusion_matrix)
from sklearn.utils.class_weight import compute_class_weight

warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════════════════════

TICKERS    = ["AAPL", "NVDA", "TSLA", "AMZN", "MSFT", "GOOGL", "META"]
DATA_DIR   = Path("tesis_ml_stocks/03_model_datasets/logistic_regression")
RAW_DIR    = Path("tesis_ml_stocks/01_raw_datasets")
OUTPUT_DIR = Path("tesis_ml_stocks/04_models/logistic_regression")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CLASES  = [0, 1, 2]
NOMBRES = {0: "SELL", 1: "HOLD", 2: "BUY"}

EXPERIMENTOS = {
    "A": "Máximo historial (2013-2024)",
    "B": "Ciclo completo post-COVID — RECOMENDADO",
    "C": "Era moderna (2020-2024)",
}

EXPERIMENTOS_FECHAS = {
    "A": {"test": ("2022-01-01", "2024-12-31")},
    "B": {"test": ("2023-01-01", "2024-12-31")},
    "C": {"test": ("2024-01-01", "2024-12-31")},
}

C_VALORES = [0.001, 0.01, 0.1, 1.0, 10.0]
VENTANA_ECONOMICA = 90  # días para métricas económicas


# ══════════════════════════════════════════════════════════════════════════════
# UTILIDADES — CARGA DE DATOS
# ══════════════════════════════════════════════════════════════════════════════

def cargar_splits(ticker: str, exp_id: str):
    """Carga train/val/test para un ticker y experimento."""
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
                                  ventana: int = VENTANA_ECONOMICA) -> dict:
    """
    Calcula métricas económicas sobre los primeros 'ventana' días del test.

    Lógica de simulación:
      BUY  (2): posición larga  → retorno = +r_forward
      SELL (0): posición corta  → retorno = -r_forward
      HOLD (1): sin posición    → retorno =  0

    Sin costos de transacción ni slippage (backtesting básico).

    Parámetros
    ----------
    y_pred    : señales predichas (0, 1, 2)
    r_forward : retornos logarítmicos reales del día siguiente
    ventana   : número de días a evaluar (default 90)

    Retorna
    -------
    dict con cumul_return, return_vs_bh, sharpe, max_drawdown,
    win_rate, profit_factor — todos sobre la ventana especificada.
    """
    n = min(len(y_pred), len(r_forward))
    pred = y_pred[:n]
    ret  = r_forward[:n]

    # Retorno diario de la estrategia
    r_strat = np.where(pred == 2, ret,
              np.where(pred == 0, -ret, 0.0))

    # ── Retorno acumulado ────────────────────────────────────────────────────
    cumul_return = float(np.expm1(np.sum(r_strat)))

    # ── Retorno buy-and-hold en el mismo período ─────────────────────────────
    bh_return = float(np.expm1(np.sum(ret)))
    return_vs_bh = cumul_return - bh_return

    # ── Sharpe ratio (anualizado, tasa libre de riesgo = 0) ──────────────────
    if r_strat.std() > 1e-8:
        sharpe = float((r_strat.mean() / r_strat.std()) * np.sqrt(252))
    else:
        sharpe = 0.0

    # ── Máximo drawdown ──────────────────────────────────────────────────────
    equity = np.exp(np.cumsum(r_strat))
    rolling_max = np.maximum.accumulate(equity)
    drawdowns = (equity - rolling_max) / (rolling_max + 1e-8)
    max_drawdown = float(drawdowns.min())

    # ── Win rate ─────────────────────────────────────────────────────────────
    operaciones = r_strat[pred != 1]          # excluye HOLD
    if len(operaciones) > 0:
        win_rate = float((operaciones > 0).mean())
    else:
        win_rate = 0.0

    # ── Profit factor ─────────────────────────────────────────────────────────
    ganancias = operaciones[operaciones > 0].sum()
    perdidas  = abs(operaciones[operaciones < 0].sum())
    profit_factor = float(ganancias / perdidas) if perdidas > 1e-8 else np.inf

    return {
        "cumul_return_test":   round(cumul_return,  4),
        "return_vs_bh_test":   round(return_vs_bh,  4),
        "sharpe_test":         round(sharpe,         4),
        "max_drawdown_test":   round(max_drawdown,   4),
        "win_rate_test":       round(win_rate,       4),
        "profit_factor_test":  round(profit_factor,  4) if profit_factor != np.inf else None,
    }


# ══════════════════════════════════════════════════════════════════════════════
# MÉTRICAS DE CLASIFICACIÓN
# ══════════════════════════════════════════════════════════════════════════════

def calcular_metricas(y_true: np.ndarray,
                       y_pred: np.ndarray,
                       y_prob: np.ndarray,
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
    total = len(y_pred)
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
        "n_samples":           total,
        "dist_real":           {NOMBRES[k]: int((y_true == k).sum()) for k in CLASES},
    }

    # ── Métricas económicas (solo si se proporcionan retornos) ───────────────
    if r_forward is not None and len(r_forward) >= VENTANA_ECONOMICA:
        eco = calcular_metricas_economicas(y_pred, r_forward, VENTANA_ECONOMICA)
        metricas.update(eco)

    return metricas


# ══════════════════════════════════════════════════════════════════════════════
# ENTRENAMIENTO
# ══════════════════════════════════════════════════════════════════════════════

def buscar_mejor_C(X_tr, y_tr, X_va, y_va) -> float:
    """Grid search manual sobre C usando F1-macro en validación."""
    mejor_c, mejor_f1 = C_VALORES[0], -1.0
    pesos = compute_class_weight("balanced", classes=np.array(CLASES), y=y_tr)
    cw    = {k: pesos[i] for i, k in enumerate(CLASES)}
    for c in C_VALORES:
        m = LogisticRegression(C=c, class_weight=cw, max_iter=2000,
                               solver="lbfgs", random_state=42, n_jobs=-1)
        m.fit(X_tr, y_tr)
        f1 = f1_score(y_va, m.predict(X_va), average="macro", zero_division=0)
        if f1 > mejor_f1:
            mejor_f1, mejor_c = f1, c
    return mejor_c


def entrenar_modelo(X_tr, y_tr, C: float) -> LogisticRegression:
    """Entrena el modelo final con el C óptimo."""
    pesos = compute_class_weight("balanced", classes=np.array(CLASES), y=y_tr)
    cw    = {k: pesos[i] for i, k in enumerate(CLASES)}
    m = LogisticRegression(C=C, class_weight=cw, max_iter=2000,
                           solver="lbfgs", random_state=42, n_jobs=-1)
    m.fit(X_tr, y_tr)
    return m


def imprimir_resumen(ticker, exp_id, metricas_val, metricas_test, C):
    v, t = metricas_val, metricas_test
    eco  = f"  Ret={t.get('cumul_return_90d','N/A'):.3f}  " \
           f"Sharpe={t.get('sharpe_90d','N/A'):.3f}  " \
           f"WR={t.get('win_rate_90d','N/A'):.3f}" \
           if 'cumul_return_90d' in t else ""
    print(f"    C={C:.3f}  |  "
          f"Val  F1={v['f1_macro']:.3f} BUY={v['f1_buy']:.3f} SELL={v['f1_sell']:.3f}  |  "
          f"Test F1={t['f1_macro']:.3f} BUY={t['f1_buy']:.3f} SELL={t['f1_sell']:.3f}"
          f"{eco}")


# ══════════════════════════════════════════════════════════════════════════════
# ENTRENAMIENTO POR TICKER
# ══════════════════════════════════════════════════════════════════════════════

def entrenar_por_ticker():
    print("\n" + "═"*65)
    print("  REGRESIÓN LOGÍSTICA — POR TICKER")
    print("═"*65)

    resultados = []

    for exp_id, exp_desc in EXPERIMENTOS.items():
        print(f"\n── Experimento {exp_id}: {exp_desc}")
        dir_out = OUTPUT_DIR / "por_ticker" / f"experimento_{exp_id}"
        dir_out.mkdir(parents=True, exist_ok=True)

        for ticker in TICKERS:
            print(f"  {ticker}...", end=" ", flush=True)
            try:
                X_tr, y_tr, X_va, y_va, X_te, y_te, feat_cols = \
                    cargar_splits(ticker, exp_id)
            except FileNotFoundError:
                print("sin datos")
                continue

            # Retornos reales del período de prueba para métricas económicas
            r_fwd_test = cargar_retornos_test(ticker, exp_id)

            # Búsqueda de C óptimo en validación
            mejor_C = buscar_mejor_C(X_tr, y_tr, X_va, y_va)

            # Modelo final entrenado con train + val
            X_full = np.vstack([X_tr, X_va])
            y_full = np.concatenate([y_tr, y_va])
            modelo_final = entrenar_modelo(X_full, y_full, mejor_C)

            # Modelo de validación entrenado solo con train
            modelo_val = entrenar_modelo(X_tr, y_tr, mejor_C)

            # Métricas
            met_val  = calcular_metricas(
                y_va, modelo_val.predict(X_va),
                modelo_val.predict_proba(X_va), "val"
            )
            met_test = calcular_metricas(
                y_te, modelo_final.predict(X_te),
                modelo_final.predict_proba(X_te), "test",
                r_forward=r_fwd_test
            )

            imprimir_resumen(ticker, exp_id, met_val, met_test, mejor_C)

            # Guardar modelo
            with open(dir_out / f"{ticker}_modelo.pkl", "wb") as f:
                pickle.dump(modelo_final, f)

            # Guardar métricas
            meta = {
                "ticker": ticker, "experimento": exp_id,
                "tipo": "por_ticker", "modelo": "LogisticRegression",
                "mejor_C": mejor_C, "n_features": len(feat_cols),
                "features": feat_cols,
                "n_train": len(y_tr), "n_val": len(y_va), "n_test": len(y_te),
                "metricas_val":  met_val,
                "metricas_test": met_test,
            }
            with open(dir_out / f"{ticker}_metricas.json", "w") as f:
                json.dump(meta, f, indent=2)

            fila = {
                "modelo": "LogisticRegression", "tipo": "por_ticker",
                "ticker": ticker, "experimento": exp_id,
                "C": mejor_C,
                "val_f1_macro":  met_val["f1_macro"],
                "val_f1_buy":    met_val["f1_buy"],
                "val_f1_sell":   met_val["f1_sell"],
                "test_f1_macro": met_test["f1_macro"],
                "test_f1_buy":   met_test["f1_buy"],
                "test_f1_sell":  met_test["f1_sell"],
                "test_f1_buy_sell_avg": met_test["f1_buy_sell_avg"],
                "signal_pct_buy":  met_test["signal_distribution"]["BUY"]["pct"],
                "signal_pct_hold": met_test["signal_distribution"]["HOLD"]["pct"],
                "signal_pct_sell": met_test["signal_distribution"]["SELL"]["pct"],
            }
            # Agregar métricas económicas si están disponibles
            for k in ["cumul_return_test", "return_vs_bh_test", "sharpe_test", "max_drawdown_test", "win_rate_test", "profit_factor_test"]:
                fila[k] = met_test.get(k, None)

            resultados.append(fila)

    return resultados


# ══════════════════════════════════════════════════════════════════════════════
# ENTRENAMIENTO GLOBAL
# ══════════════════════════════════════════════════════════════════════════════

def entrenar_global():
    print("\n" + "═"*65)
    print("  REGRESIÓN LOGÍSTICA — MODELO GLOBAL (todos los tickers)")
    print("═"*65)

    resultados = []

    for exp_id, exp_desc in EXPERIMENTOS.items():
        print(f"\n── Experimento {exp_id}: {exp_desc}")
        dir_out = OUTPUT_DIR / "global" / f"experimento_{exp_id}"
        dir_out.mkdir(parents=True, exist_ok=True)

        trains, vals, tests = [], [], []
        r_fwd_tests = []
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
                print(f"  ⚠ {ticker} sin datos, omitido del global")

        if not trains:
            continue

        X_tr = np.vstack([x for x, _ in trains])
        y_tr = np.concatenate([y for _, y in trains])
        X_va = np.vstack([x for x, _ in vals])
        y_va = np.concatenate([y for _, y in vals])
        X_te = np.vstack([x for x, _ in tests])
        y_te = np.concatenate([y for _, y in tests])

        # Para el modelo global concatenamos los retornos de todos los tickers
        r_fwd_global = np.concatenate(r_fwd_tests) if r_fwd_tests else None

        print(f"  Train={len(y_tr)}  Val={len(y_va)}  Test={len(y_te)}")

        mejor_C = buscar_mejor_C(X_tr, y_tr, X_va, y_va)

        X_full = np.vstack([X_tr, X_va])
        y_full = np.concatenate([y_tr, y_va])
        modelo_final = entrenar_modelo(X_full, y_full, mejor_C)

        modelo_val = entrenar_modelo(X_tr, y_tr, mejor_C)
        met_val  = calcular_metricas(
            y_va, modelo_val.predict(X_va),
            modelo_val.predict_proba(X_va), "val"
        )
        met_test = calcular_metricas(
            y_te, modelo_final.predict(X_te),
            modelo_final.predict_proba(X_te), "test",
            r_forward=r_fwd_global
        )

        print(f"  C={mejor_C}  Val F1={met_val['f1_macro']:.3f}  "
              f"Test F1={met_test['f1_macro']:.3f}  "
              f"Ret={met_test.get('cumul_return_90d','N/A')}")

        with open(dir_out / "modelo_global.pkl", "wb") as f:
            pickle.dump(modelo_final, f)

        meta = {
            "ticker": "GLOBAL", "experimento": exp_id,
            "tipo": "global", "modelo": "LogisticRegression",
            "mejor_C": mejor_C, "tickers_incluidos": TICKERS,
            "n_features": len(feat_cols_ref or []),
            "n_train": len(y_tr), "n_val": len(y_va), "n_test": len(y_te),
            "metricas_val":  met_val,
            "metricas_test": met_test,
        }
        with open(dir_out / "metricas_global.json", "w") as f:
            json.dump(meta, f, indent=2)

        fila = {
            "modelo": "LogisticRegression", "tipo": "global",
            "ticker": "GLOBAL", "experimento": exp_id,
            "C": mejor_C,
            "val_f1_macro":  met_val["f1_macro"],
            "test_f1_macro": met_test["f1_macro"],
            "test_f1_buy":   met_test["f1_buy"],
            "test_f1_sell":  met_test["f1_sell"],
            "test_f1_buy_sell_avg": met_test["f1_buy_sell_avg"],
            "signal_pct_buy":  met_test["signal_distribution"]["BUY"]["pct"],
            "signal_pct_hold": met_test["signal_distribution"]["HOLD"]["pct"],
            "signal_pct_sell": met_test["signal_distribution"]["SELL"]["pct"],
        }
        for k in ["cumul_return_test", "return_vs_bh_test", "sharpe_test", "max_drawdown_test", "win_rate_test", "profit_factor_test"]:
            fila[k] = met_test.get(k, None)

        resultados.append(fila)

    return resultados


# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

def pipeline():
    print("="*65)
    print("  SCRIPT 04 — REGRESIÓN LOGÍSTICA")
    print("="*65)

    res_ticker = entrenar_por_ticker()
    res_global = entrenar_global()

    todos = res_ticker + res_global
    df = pd.DataFrame(todos)
    df.to_csv(OUTPUT_DIR / "resultados_lr.csv", index=False)

    print("\n" + "="*65)
    print("  RESUMEN — REGRESIÓN LOGÍSTICA")
    print("="*65)
    cols_resumen = ["tipo", "ticker", "experimento",
                    "val_f1_macro", "test_f1_macro",
                    "cumul_return_test", "sharpe_test", "win_rate_test"]
    print(df[[c for c in cols_resumen if c in df.columns]].to_string(index=False))
    print(f"\n✓ Modelos y métricas guardados en: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    pipeline()