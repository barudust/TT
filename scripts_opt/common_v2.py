"""Versión común que carga el dataset V2 con features ampliadas."""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import sys
import warnings
import numpy as np
import pandas as pd
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass

from common import (TICKERS, CLASES, NOMBRES, EXPERIMENTOS, SPLITS,
                    EXCLUIR_COLS, OUT_DIR,
                    metricas_full, metricas_clasificacion, metricas_economicas,
                    metricas_global_por_ticker,
                    guardar_json, append_resultado, imprimir_metricas)

RAW_DIR_V2 = Path("tesis_ml_stocks/01_raw_datasets_v2")


def cargar_raw_v2(ticker: str) -> pd.DataFrame:
    """Carga el dataset v2 con features expandidas."""
    return pd.read_parquet(RAW_DIR_V2 / f"{ticker}_raw_v2.parquet")


def get_feature_cols_v2(df: pd.DataFrame) -> list:
    """Lista columnas que son features (excluye target y OHLCV raw)."""
    return [c for c in df.columns if c not in EXCLUIR_COLS]


def split_temporal_v2(df: pd.DataFrame, exp_id: str):
    s = SPLITS[exp_id]
    def corte(rng):
        return df[(df.index >= rng[0]) & (df.index <= rng[1])]
    return corte(s["train"]), corte(s["val"]), corte(s["test"])


def cargar_dataset_v2(ticker: str, exp_id: str, feat_cols: list = None):
    df = cargar_raw_v2(ticker)
    if feat_cols is None:
        feat_cols = get_feature_cols_v2(df)
    else:
        feat_cols = [c for c in feat_cols if c in df.columns]

    cols_a_usar = feat_cols + ["target", "r_forward"]
    df = df[cols_a_usar].dropna()

    tr, va, te = split_temporal_v2(df, exp_id)
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


def cargar_global_v2(exp_id: str, feat_cols: list = None):
    Xtr_l, ytr_l = [], []
    Xva_l, yva_l = [], []
    Xte_l, yte_l = [], []
    rfwd_te_l    = []
    tk_te_l      = []
    feat_cols_ref = None

    for ticker in TICKERS:
        d = cargar_dataset_v2(ticker, exp_id, feat_cols)
        Xtr_l.append(d["X_tr"]); ytr_l.append(d["y_tr"])
        Xva_l.append(d["X_va"]); yva_l.append(d["y_va"])
        Xte_l.append(d["X_te"]); yte_l.append(d["y_te"])
        rfwd_te_l.append(d["r_fwd_test"])
        tk_te_l.append(np.full(len(d["y_te"]), ticker))
        if feat_cols_ref is None:
            feat_cols_ref = d["feat_cols"]

    return {
        "X_tr": np.vstack(Xtr_l), "y_tr": np.concatenate(ytr_l),
        "X_va": np.vstack(Xva_l), "y_va": np.concatenate(yva_l),
        "X_te": np.vstack(Xte_l), "y_te": np.concatenate(yte_l),
        "feat_cols": feat_cols_ref,
        "r_fwd_test": np.concatenate(rfwd_te_l),
        "ticker_test": np.concatenate(tk_te_l),
    }
