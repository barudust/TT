"""
Módulo común para los scripts de optimización.
Funciones compartidas: carga de datos, métricas (clasificación + económicas),
y utilidades de reporte.
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import sys
import json
import warnings
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.metrics import classification_report, confusion_matrix, f1_score

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

warnings.filterwarnings("ignore")

# ════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN GLOBAL
# ════════════════════════════════════════════════════════════════════════════

TICKERS = ["AAPL", "NVDA", "TSLA", "AMZN", "MSFT", "GOOGL", "META"]
CLASES  = [0, 1, 2]
NOMBRES = {0: "SELL", 1: "HOLD", 2: "BUY"}

EXPERIMENTOS = {"A": "Maximo historial", "B": "Post-COVID (REC)", "C": "Era moderna"}

# Splits coherentes con script 03
SPLITS = {
    "A": {"train": ("2014-01-01", "2021-12-31"),
          "val":   ("2022-01-01", "2023-12-31"),
          "test":  ("2024-01-01", "2025-12-31")},
    "B": {"train": ("2018-01-01", "2023-12-31"),
          "val":   ("2024-01-01", "2024-12-31"),
          "test":  ("2025-01-01", "2025-12-31")},
    "C": {"train": ("2020-01-01", "2023-12-31"),
          "val":   ("2024-01-01", "2024-12-31"),
          "test":  ("2025-01-01", "2025-12-31")},
}

# Columnas que NUNCA son features
EXCLUIR_COLS = {
    "raw_open", "raw_high", "raw_low", "raw_close", "raw_volume",
    "target", "r_forward", "umbral_buy", "umbral_sell",
}

# Rutas estándar
BASE_DIR = Path("tesis_ml_stocks")
RAW_DIR  = BASE_DIR / "01_raw_datasets"
OUT_DIR  = Path("RESULTADOS_OPTIMIZADOS")


# ════════════════════════════════════════════════════════════════════════════
# CARGA DE DATOS
# ════════════════════════════════════════════════════════════════════════════

def cargar_raw(ticker: str) -> pd.DataFrame:
    """Carga el parquet crudo de un ticker (todas las features + target + raw OHLCV)."""
    return pd.read_parquet(RAW_DIR / f"{ticker}_raw.parquet")


def get_feature_cols(df: pd.DataFrame) -> list:
    """Lista columnas que son features (excluye target y OHLCV raw)."""
    return [c for c in df.columns if c not in EXCLUIR_COLS]


def split_temporal(df: pd.DataFrame, exp_id: str):
    """Divide df en (train, val, test) según SPLITS[exp_id]."""
    s = SPLITS[exp_id]
    def corte(rng):
        return df[(df.index >= rng[0]) & (df.index <= rng[1])]
    return corte(s["train"]), corte(s["val"]), corte(s["test"])


def cargar_dataset(ticker: str, exp_id: str, feat_cols: list = None):
    """
    Carga raw -> split -> retorna X_tr, y_tr, X_va, y_va, X_te, y_te, feat_cols, r_fwd_test.
    Si feat_cols=None, usa todas las features disponibles.
    """
    df = cargar_raw(ticker)
    if feat_cols is None:
        feat_cols = get_feature_cols(df)
    else:
        feat_cols = [c for c in feat_cols if c in df.columns]

    cols_a_usar = feat_cols + ["target", "r_forward"]
    df = df[cols_a_usar].dropna()

    tr, va, te = split_temporal(df, exp_id)
    r_fwd_test = te["r_forward"].values if "r_forward" in te.columns else None

    return {
        "X_tr": tr[feat_cols].values,
        "y_tr": tr["target"].values.astype(int),
        "X_va": va[feat_cols].values,
        "y_va": va["target"].values.astype(int),
        "X_te": te[feat_cols].values,
        "y_te": te["target"].values.astype(int),
        "feat_cols": feat_cols,
        "r_fwd_test": r_fwd_test,
        "fechas_test": te.index,
    }


def cargar_global(exp_id: str, feat_cols: list = None):
    """
    Concatena datos de todos los tickers para entrenamiento global.
    Retorna también ticker_te para poder calcular métricas por ticker en test.
    """
    Xtr_l, ytr_l = [], []
    Xva_l, yva_l = [], []
    Xte_l, yte_l = [], []
    rfwd_te_l    = []
    tk_te_l      = []
    feat_cols_ref = None

    for ticker in TICKERS:
        d = cargar_dataset(ticker, exp_id, feat_cols)
        Xtr_l.append(d["X_tr"]); ytr_l.append(d["y_tr"])
        Xva_l.append(d["X_va"]); yva_l.append(d["y_va"])
        Xte_l.append(d["X_te"]); yte_l.append(d["y_te"])
        rfwd_te_l.append(d["r_fwd_test"])
        tk_te_l.append(np.full(len(d["y_te"]), ticker))
        if feat_cols_ref is None:
            feat_cols_ref = d["feat_cols"]

    return {
        "X_tr": np.vstack(Xtr_l),
        "y_tr": np.concatenate(ytr_l),
        "X_va": np.vstack(Xva_l),
        "y_va": np.concatenate(yva_l),
        "X_te": np.vstack(Xte_l),
        "y_te": np.concatenate(yte_l),
        "feat_cols": feat_cols_ref,
        "r_fwd_test": np.concatenate(rfwd_te_l),
        "ticker_test": np.concatenate(tk_te_l),
    }


# ════════════════════════════════════════════════════════════════════════════
# MÉTRICAS
# ════════════════════════════════════════════════════════════════════════════

def metricas_clasificacion(y_true, y_pred, split_name: str = "test") -> dict:
    """F1-macro, F1 por clase, precision/recall, accuracy, matriz de confusión, distribución."""
    rep = classification_report(y_true, y_pred,
                                 target_names=["SELL", "HOLD", "BUY"],
                                 output_dict=True, zero_division=0)
    cm = confusion_matrix(y_true, y_pred, labels=CLASES).tolist()
    n  = len(y_pred)
    signal_dist = {
        NOMBRES[k]: {"n": int((y_pred == k).sum()),
                     "pct": round((y_pred == k).mean() * 100, 1)}
        for k in CLASES
    }
    return {
        "split":           split_name,
        "f1_macro":        round(f1_score(y_true, y_pred, average="macro", zero_division=0), 4),
        "f1_buy":          round(rep["BUY"]["f1-score"],   4),
        "f1_hold":         round(rep["HOLD"]["f1-score"],  4),
        "f1_sell":         round(rep["SELL"]["f1-score"],  4),
        "f1_buy_sell_avg": round((rep["BUY"]["f1-score"] + rep["SELL"]["f1-score"]) / 2, 4),
        "precision_buy":   round(rep["BUY"]["precision"],  4),
        "precision_sell":  round(rep["SELL"]["precision"], 4),
        "recall_buy":      round(rep["BUY"]["recall"],     4),
        "recall_sell":     round(rep["SELL"]["recall"],    4),
        "accuracy":        round(rep["accuracy"],          4),
        "signal_distribution": signal_dist,
        "confusion_matrix":    cm,
        "n_samples":           int(n),
        "dist_real":           {NOMBRES[k]: int((y_true == k).sum()) for k in CLASES},
    }


def metricas_economicas(y_pred, r_forward) -> dict:
    """
    Backtest simple sobre todo el test:
      BUY (2) -> +r ; SELL (0) -> -r ; HOLD (1) -> 0
    Retorna: cumul_return, return_vs_bh, sharpe, max_drawdown, win_rate, profit_factor.
    """
    if r_forward is None or len(r_forward) == 0:
        return {}
    n = min(len(y_pred), len(r_forward))
    pred = y_pred[:n]
    ret  = r_forward[:n]

    r_strat = np.where(pred == 2,  ret,
              np.where(pred == 0, -ret, 0.0))

    cumul = float(np.expm1(np.nansum(r_strat)))
    bh    = float(np.expm1(np.nansum(ret)))
    vs_bh = cumul - bh

    sharpe = float((np.nanmean(r_strat) / (np.nanstd(r_strat) + 1e-12)) * np.sqrt(252)) \
             if np.nanstd(r_strat) > 1e-8 else 0.0

    equity = np.exp(np.cumsum(np.nan_to_num(r_strat)))
    peak   = np.maximum.accumulate(equity)
    dd     = (equity - peak) / (peak + 1e-12)
    max_dd = float(dd.min())

    ops = r_strat[pred != 1]
    win_rate = float((ops > 0).mean()) if len(ops) > 0 else 0.0

    pos = ops[ops > 0].sum()
    neg = abs(ops[ops < 0].sum())
    pf  = float(pos / neg) if neg > 1e-8 else None

    return {
        "cumul_return_test":  round(cumul,  4),
        "return_vs_bh_test":  round(vs_bh,  4),
        "sharpe_test":        round(sharpe, 4),
        "max_drawdown_test":  round(max_dd, 4),
        "win_rate_test":      round(win_rate, 4),
        "profit_factor_test": round(pf, 4) if pf is not None else None,
    }


def metricas_full(y_true, y_pred, r_forward=None, split_name="test") -> dict:
    """Combina métricas de clasificación y económicas (si hay retornos)."""
    out = metricas_clasificacion(y_true, y_pred, split_name)
    if r_forward is not None and len(r_forward) > 10:
        out.update(metricas_economicas(y_pred, r_forward))
    return out


def metricas_global_por_ticker(y_true, y_pred, ticker_arr, r_fwd) -> dict:
    """Desagrega métricas del modelo global por ticker en el test."""
    out = {}
    for tk in TICKERS:
        mask = (ticker_arr == tk)
        if mask.sum() < 10:
            continue
        out[tk] = metricas_full(y_true[mask], y_pred[mask],
                                r_fwd[mask] if r_fwd is not None else None)
    return out


# ════════════════════════════════════════════════════════════════════════════
# UTILIDADES
# ════════════════════════════════════════════════════════════════════════════

def guardar_json(obj, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2, default=str)


def append_resultado(csv_path: Path, fila: dict):
    """Acumula resultados en un CSV (append). Crea el archivo si no existe."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df_nueva = pd.DataFrame([fila])
    if csv_path.exists():
        df_old = pd.read_csv(csv_path)
        df = pd.concat([df_old, df_nueva], ignore_index=True)
    else:
        df = df_nueva
    df.to_csv(csv_path, index=False)


def imprimir_metricas(prefix, met):
    eco = ""
    if "cumul_return_test" in met:
        eco = (f"  Ret={met['cumul_return_test']:.3f}  "
               f"Shar={met['sharpe_test']:.3f}  "
               f"WR={met['win_rate_test']:.3f}")
    print(f"  {prefix}  F1={met['f1_macro']:.3f} "
          f"B={met['f1_buy']:.3f} S={met['f1_sell']:.3f} H={met['f1_hold']:.3f}"
          f"{eco}")
