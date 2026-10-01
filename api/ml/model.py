"""
Carga del modelo ganador (Regresion Logistica L2 + interactions, global, Exp B)
y su uso para inferencia de señales BUY/SELL/HOLD.

Actualizado 2026-08-25 al ganador de Vía 8 (LR + 15 interactions), que mejora
al baseline LR elasticnet en F1 (+0.023) y Sharpe (+0.23) sobre TEST 2025
(en validacion 2024 empatan; ver RESULTADOS_OPTIMIZADOS/docs/ANALISIS_HOLD_Y_GLOBAL.md).

Ver RESULTADOS_OPTIMIZADOS/INVESTIGACION_COMPLETA.md §7 para el analisis
completo que sustenta este modelo como ganador tras auditar 5 arquitecturas
(LR, XGBoost, LSTM, CNN, CNN-LSTM), 150 trials de Optuna, 6 tecnicas
post-Optuna (Vía 7) y 5 tecnicas de dataset (Vía 8).
"""
import os
import pickle
from pathlib import Path

import numpy as np

from .features import FEATURE_COLUMNS

MODEL_VERSION = "LR-v8-interactions-holdw090"  # debe coincidir con config_id del .pkl

# Clases del modelo: 0=SELL, 1=HOLD, 2=BUY (ver scripts_opt/common.py -> NOMBRES)
CLASS_TO_SIGNAL = {0: "sell", 1: "hold", 2: "buy"}

_DEFAULT_MODEL_PATH = Path(__file__).resolve().parent / "artifacts" / "lr_elasticnet_global_expB.pkl"


class SignalModel:
    def __init__(self, model, scaler, feat_cols, meta: dict | None = None):
        self.model = model
        self.scaler = scaler
        self.feat_cols = feat_cols
        # Metadatos del .pkl (hiperparametros, rango de entrenamiento, ...) para
        # que la API describa el modelo cargado en vez de texto fijo en el frontend.
        self.meta = meta or {}

    @staticmethod
    def _describir_pesos(hp: dict) -> str | None:
        """'balanced' o 'balanced, HOLD ×0.9' (el .pkl guarda los pesos efectivos)."""
        peso = hp.get("peso_hold")
        if peso is not None and peso != 1.0:
            return f"balanced, HOLD ×{peso:g}"
        cw = hp.get("class_weight")
        return cw if isinstance(cw, str) or cw is None else "personalizados"

    def describe(self) -> dict:
        hp = self.meta.get("hp", {})
        n_inter = len(self.meta.get("interaction_pairs", []))
        return {
            "version": MODEL_VERSION,
            "configId": self.meta.get("config_id", MODEL_VERSION),
            "algorithm": type(self.model).__name__,
            "penalty": hp.get("penalty", getattr(self.model, "penalty", None)),
            "C": hp.get("C", getattr(self.model, "C", None)),
            "classWeight": self._describir_pesos(hp),
            "scaler": type(self.scaler).__name__,
            "nFeatures": len(self.feat_cols),
            "nFeaturesBase": len(self.feat_cols) - n_inter,
            "nInteractions": n_inter,
            "classes": [CLASS_TO_SIGNAL[int(c)] for c in self.model.classes_],
            "trainRange": hp.get("rango_train"),
            "nTrainSamples": hp.get("n_samples"),
            "trainedAt": hp.get("fecha_entrenamiento"),
        }

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

    meta = {k: v for k, v in obj.items() if k not in ("model", "scaler", "feat_cols")}
    _model_cache = SignalModel(obj["model"], obj["scaler"], obj["feat_cols"], meta)
    return _model_cache
