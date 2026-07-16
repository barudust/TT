"""
Carga del modelo ganador (Regresion Logistica elasticnet, global, Exp B)
y su uso para inferencia de señales BUY/SELL/HOLD.

Ver RESULTADOS_OPTIMIZADOS/GUIA_PROGRESO.md en la raiz del repo para el
analisis completo que declara este modelo como ganador
(F1-macro=0.4167, Sharpe test=1.25) frente a XGBoost, LightGBM, LSTM y
CNN-LSTM.
"""
import os
import pickle
from pathlib import Path

import numpy as np

from .features import FEATURE_COLUMNS

MODEL_VERSION = "LR-02-elasticnet-all_global_expB"

# Clases del modelo: 0=SELL, 1=HOLD, 2=BUY (ver scripts_opt/common.py -> NOMBRES)
CLASS_TO_SIGNAL = {0: "sell", 1: "hold", 2: "buy"}

_DEFAULT_MODEL_PATH = Path(__file__).resolve().parent / "artifacts" / "lr_elasticnet_global_expB.pkl"


class SignalModel:
    def __init__(self, model, scaler, feat_cols):
        self.model = model
        self.scaler = scaler
        self.feat_cols = feat_cols

    def predict_row(self, feature_row) -> dict:
        """
        feature_row: pandas.Series o dict-like indexable por FEATURE_COLUMNS.
        Retorna {"signal": "buy"|"sell"|"hold", "confidence": float,
                 "probabilities": {"buy": .., "sell": .., "hold": ..}}
        """
        x = np.asarray([[feature_row[c] for c in self.feat_cols]], dtype=float)
        x_scaled = self.scaler.transform(x)
        proba = self.model.predict_proba(x_scaled)[0]
        pred_class = int(np.argmax(proba))

        return {
            "signal": CLASS_TO_SIGNAL[pred_class],
            "confidence": float(proba[pred_class]),
            "probabilities": {
                CLASS_TO_SIGNAL[cls]: float(proba[i])
                for i, cls in enumerate(self.model.classes_)
            },
        }

    def predict_frame(self, df) -> list:
        """Aplica predict_row a cada fila de un DataFrame ordenado por fecha."""
        return [self.predict_row(row) for _, row in df[self.feat_cols].iterrows()]


_model_cache: SignalModel | None = None


def load_model(path: str | None = None) -> SignalModel:
    """Carga (una sola vez, con cache en proceso) el modelo ganador desde disco."""
    global _model_cache
    if _model_cache is not None:
        return _model_cache

    model_path = Path(path or os.getenv("MODEL_PATH", "")) if (path or os.getenv("MODEL_PATH")) else _DEFAULT_MODEL_PATH
    if not model_path.exists():
        raise FileNotFoundError(
            f"No se encontro el modelo en {model_path}. "
            f"Define MODEL_PATH en .env o copia el .pkl a api/ml/artifacts/."
        )

    with open(model_path, "rb") as f:
        obj = pickle.load(f)

    missing = set(FEATURE_COLUMNS) - set(obj["feat_cols"])
    if missing:
        raise ValueError(f"El modelo cargado no tiene las features esperadas: {missing}")

    _model_cache = SignalModel(obj["model"], obj["scaler"], obj["feat_cols"])
    return _model_cache
