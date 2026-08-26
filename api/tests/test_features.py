import numpy as np
import pytest

from ml.features import (calcular_features, build_feature_frame,
                          FEATURE_COLUMNS, FEATURES_BASE)

# Solo columnas técnicas puras (excluye SPY/VIX que vienen del mercado y las
# 15 interactions que se calculan en build_feature_frame, no en
# calcular_features).
TECHNICAL_COLUMNS = [c for c in FEATURES_BASE
                     if not c.startswith(("SP500_", "VIX"))]


def test_calcular_features_has_all_technical_columns(synthetic_ohlcv):
    feat = calcular_features(synthetic_ohlcv)
    missing = set(TECHNICAL_COLUMNS) - set(feat.columns)
    assert not missing


def test_calcular_features_last_row_has_no_nan_after_warmup(synthetic_ohlcv):
    feat = calcular_features(synthetic_ohlcv)
    last_row = feat.iloc[-1][TECHNICAL_COLUMNS]
    assert not last_row.isna().any(), f"NaN inesperado: {last_row[last_row.isna()].index.tolist()}"


def test_ret_1d_matches_log_return(synthetic_ohlcv):
    feat = calcular_features(synthetic_ohlcv)
    c = synthetic_ohlcv["Close"]
    expected = np.log(c.iloc[-1] / c.iloc[-2])
    assert feat["ret_1d"].iloc[-1] == pytest.approx(expected, rel=1e-9)


def test_rsi_is_bounded(synthetic_ohlcv):
    feat = calcular_features(synthetic_ohlcv)
    rsi = feat["rsi_14"].dropna()
    assert (rsi >= 0).all() and (rsi <= 100).all()


def test_dist_ma10_positive_on_strictly_increasing_series(synthetic_ohlcv):
    # Serie monotona creciente: el precio siempre queda por encima de su
    # media movil rezagada, dist_ma10 debe ser positivo en la ultima fila.
    increasing = synthetic_ohlcv.copy()
    n = len(increasing)
    ramp = np.linspace(50, 150, n)
    for col in ["Open", "High", "Low", "Close"]:
        increasing[col] = ramp
    feat = calcular_features(increasing)
    assert feat["dist_ma10"].iloc[-1] > 0


def test_build_feature_frame_joins_market_and_drops_warmup(synthetic_ohlcv, synthetic_market):
    feat = build_feature_frame(synthetic_ohlcv, synthetic_market)

    assert not feat.empty
    missing = set(FEATURE_COLUMNS) - set(feat.columns)
    assert not missing

    last_row = feat.iloc[-1][FEATURE_COLUMNS]
    assert not last_row.isna().any()

    for col in ["raw_open", "raw_high", "raw_low", "raw_close", "raw_volume"]:
        assert col in feat.columns

    # El primer tramo (warmup de MA200/VIX rolling 252) debe haberse eliminado.
    assert len(feat) < len(synthetic_ohlcv)
