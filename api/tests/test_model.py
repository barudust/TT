import pandas as pd
import pytest

from ml.features import FEATURE_COLUMNS
from ml.model import load_model, CLASS_TO_SIGNAL


def test_load_model_matches_feature_columns():
    model = load_model()
    assert set(model.feat_cols) == set(FEATURE_COLUMNS)
    assert len(model.feat_cols) == 61


def test_predict_row_shape():
    model = load_model()
    row = pd.Series({c: 0.0 for c in model.feat_cols})

    pred = model.predict_row(row)

    assert pred["signal"] in CLASS_TO_SIGNAL.values()
    assert 0.0 <= pred["confidence"] <= 1.0
    assert set(pred["probabilities"].keys()) == set(CLASS_TO_SIGNAL.values())
    assert pred["probabilities"][pred["signal"]] == pytest.approx(pred["confidence"])
    assert sum(pred["probabilities"].values()) == pytest.approx(1.0, rel=1e-6)


def test_predict_frame_matches_row_count():
    model = load_model()
    df = pd.DataFrame([{c: 0.0 for c in model.feat_cols} for _ in range(5)])

    preds = model.predict_frame(df)

    assert len(preds) == 5
    assert all(p["signal"] in CLASS_TO_SIGNAL.values() for p in preds)
