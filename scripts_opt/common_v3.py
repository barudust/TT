"""Loader del dataset v3 con 94 features (61 originales + 33 mercado extras)."""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import sys
import warnings
import numpy as np
import pandas as pd
from pathlib import Path

try: sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except: pass
warnings.filterwarnings("ignore")

from common import (TICKERS, CLASES, NOMBRES, EXPERIMENTOS, SPLITS,
                    EXCLUIR_COLS, OUT_DIR,
                    metricas_full, metricas_clasificacion, metricas_economicas,
                    metricas_global_por_ticker,
                    guardar_json, imprimir_metricas)

RAW_DIR_V3 = Path("tesis_ml_stocks/01_raw_datasets_v3")


def cargar_raw_v3(ticker):
    return pd.read_parquet(RAW_DIR_V3 / f"{ticker}_raw_v3.parquet")


def get_feature_cols_v3(df):
    return [c for c in df.columns if c not in EXCLUIR_COLS]


def cargar_dataset_v3(ticker, exp_id, feat_cols=None):
    df = cargar_raw_v3(ticker)
    if feat_cols is None:
        feat_cols = get_feature_cols_v3(df)
    else:
        feat_cols = [c for c in feat_cols if c in df.columns]

    cols = feat_cols + ["target", "r_forward"]
    df = df[cols].dropna()
    s = SPLITS[exp_id]
    def corte(rng): return df[(df.index >= rng[0]) & (df.index <= rng[1])]
    tr, va, te = corte(s["train"]), corte(s["val"]), corte(s["test"])
    r_fwd_test = te["r_forward"].values if "r_forward" in te.columns else None
    return {
        "X_tr": tr[feat_cols].values, "y_tr": tr["target"].values.astype(int),
        "X_va": va[feat_cols].values, "y_va": va["target"].values.astype(int),
        "X_te": te[feat_cols].values, "y_te": te["target"].values.astype(int),
        "feat_cols": feat_cols,
        "r_fwd_test": r_fwd_test,
        "fechas_test": te.index,
    }


def cargar_global_v3(exp_id, feat_cols=None):
    Xtr_l, ytr_l = [], []
    Xva_l, yva_l = [], []
    Xte_l, yte_l = [], []
    rfwd_te_l, tk_te_l = [], []
    fc_ref = None
    for ticker in TICKERS:
        d = cargar_dataset_v3(ticker, exp_id, feat_cols)
        Xtr_l.append(d["X_tr"]); ytr_l.append(d["y_tr"])
        Xva_l.append(d["X_va"]); yva_l.append(d["y_va"])
        Xte_l.append(d["X_te"]); yte_l.append(d["y_te"])
        rfwd_te_l.append(d["r_fwd_test"])
        tk_te_l.append(np.full(len(d["y_te"]), ticker))
        if fc_ref is None: fc_ref = d["feat_cols"]
    return {
        "X_tr": np.vstack(Xtr_l), "y_tr": np.concatenate(ytr_l),
        "X_va": np.vstack(Xva_l), "y_va": np.concatenate(yva_l),
        "X_te": np.vstack(Xte_l), "y_te": np.concatenate(yte_l),
        "feat_cols": fc_ref,
        "r_fwd_test": np.concatenate(rfwd_te_l),
        "ticker_test": np.concatenate(tk_te_l),
    }
