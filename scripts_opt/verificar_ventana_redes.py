"""
================================================================================
VERIFICAR VENTANA DE LAS REDES — ¿cuánto pesa no ver el último día?
================================================================================
En `train_all_v4.seq()` y `common_v5._ventanas()` la ventana de entrada de las
redes es [i - lookback, i) y la etiqueta es la de la fila i, que describe el
movimiento C_i -> C_{i+1}. Es decir, las redes predicen ese movimiento sin ver
las variables del día i (el último cierre disponible); LR y XGBoost sí las ven.
No es fuga de información (es lo contrario: les falta un día), pero es una
asimetría entre modelos.

Este script mide su efecto con la LR de producción (sin interacciones), Exp B
global, test 2025: la misma LR con las variables del día t y con las del día
t-1. Resultado (2026-10-12): 0.3933 -> 0.3859 de F1-macro (-0.007).

    python scripts_opt/verificar_ventana_redes.py
"""
import sys
import warnings
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.preprocessing import RobustScaler

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).parent))
from common import TICKERS, cargar_raw, get_feature_cols

C_PRODUCCION = 0.00016491236228800314


def f1_con_rezago(rezago: int) -> float:
    """Entrena 2018-2023 y evalúa 2025 usando las variables de t - rezago."""
    X_tr, y_tr, X_te, y_te = [], [], [], []
    for tk in TICKERS:
        df = cargar_raw(tk)
        feat = get_feature_cols(df)
        df = df.assign(**{c: df[c].shift(rezago) for c in feat})
        df = df[feat + ["target"]].dropna()
        tr = df[(df.index >= "2018-01-01") & (df.index <= "2023-12-31")]
        te = df[(df.index >= "2025-01-01") & (df.index <= "2025-12-31")]
        sc = RobustScaler().fit(tr[feat])
        X_tr.append(sc.transform(tr[feat])); y_tr.append(tr["target"].values.astype(int))
        X_te.append(sc.transform(te[feat])); y_te.append(te["target"].values.astype(int))
    modelo = LogisticRegression(C=C_PRODUCCION, class_weight="balanced",
                                max_iter=3000, tol=1e-3)
    modelo.fit(np.vstack(X_tr), np.concatenate(y_tr))
    return f1_score(np.concatenate(y_te), modelo.predict(np.vstack(X_te)), average="macro")


if __name__ == "__main__":
    df = cargar_raw("AAPL")
    alineado = np.allclose(df["ret_1d"].shift(-1).dropna().values[:200],
                           df["r_forward"].values[:200])
    print(f"La etiqueta de la fila t es el movimiento t -> t+1: {alineado}")
    print(f"LR con variables del día t   : {f1_con_rezago(0):.4f}")
    print(f"LR con variables del día t-1 : {f1_con_rezago(1):.4f}")
