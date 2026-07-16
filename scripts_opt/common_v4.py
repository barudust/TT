"""
v4: SPLITS CORREGIDOS — test idéntico (2025) en los 3 experimentos.
Solo varía la cantidad de años de entrenamiento, val fijo en 2024.
"""
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

from common import (TICKERS, CLASES, NOMBRES, EXCLUIR_COLS, OUT_DIR,
                    metricas_full, metricas_clasificacion, metricas_economicas,
                    metricas_global_por_ticker,
                    guardar_json, imprimir_metricas, cargar_raw, get_feature_cols)

# SPLITS UNIFICADOS — mismo test (2025) en los 3 exps
SPLITS_V4 = {
    "A": {"train": ("2014-01-01", "2023-12-31"),  # 10 años train
          "val":   ("2024-01-01", "2024-12-31"),
          "test":  ("2025-01-01", "2025-12-31")},
    "B": {"train": ("2018-01-01", "2023-12-31"),  # 6 años train
          "val":   ("2024-01-01", "2024-12-31"),
          "test":  ("2025-01-01", "2025-12-31")},
    "C": {"train": ("2020-01-01", "2023-12-31"),  # 4 años train
          "val":   ("2024-01-01", "2024-12-31"),
          "test":  ("2025-01-01", "2025-12-31")},
}

EXPERIMENTOS = {"A": "10 años train", "B": "6 años train (REC)", "C": "4 años train"}


def cargar_dataset_v4(ticker, exp_id, feat_cols=None):
    df = cargar_raw(ticker)
    if feat_cols is None:
        feat_cols = get_feature_cols(df)
    else:
        feat_cols = [c for c in feat_cols if c in df.columns]
    cols = feat_cols + ["target", "r_forward"]
    df = df[cols].dropna()
    s = SPLITS_V4[exp_id]
    def corte(rng): return df[(df.index >= rng[0]) & (df.index <= rng[1])]
    tr, va, te = corte(s["train"]), corte(s["val"]), corte(s["test"])
    r_fwd = te["r_forward"].values if "r_forward" in te.columns else None
    return {
        "X_tr": tr[feat_cols].values, "y_tr": tr["target"].values.astype(int),
        "X_va": va[feat_cols].values, "y_va": va["target"].values.astype(int),
        "X_te": te[feat_cols].values, "y_te": te["target"].values.astype(int),
        "feat_cols": feat_cols, "r_fwd_test": r_fwd, "fechas_test": te.index,
    }


def cargar_global_v4(exp_id, feat_cols=None):
    Xtr_l, ytr_l, Xva_l, yva_l, Xte_l, yte_l, rfwd_l, tk_l = [],[],[],[],[],[],[],[]
    fc = None
    for ticker in TICKERS:
        d = cargar_dataset_v4(ticker, exp_id, feat_cols)
        Xtr_l.append(d["X_tr"]); ytr_l.append(d["y_tr"])
        Xva_l.append(d["X_va"]); yva_l.append(d["y_va"])
        Xte_l.append(d["X_te"]); yte_l.append(d["y_te"])
        rfwd_l.append(d["r_fwd_test"]); tk_l.append(np.full(len(d["y_te"]), ticker))
        if fc is None: fc = d["feat_cols"]
    return {
        "X_tr": np.vstack(Xtr_l), "y_tr": np.concatenate(ytr_l),
        "X_va": np.vstack(Xva_l), "y_va": np.concatenate(yva_l),
        "X_te": np.vstack(Xte_l), "y_te": np.concatenate(yte_l),
        "feat_cols": fc, "r_fwd_test": np.concatenate(rfwd_l),
        "ticker_test": np.concatenate(tk_l),
    }
