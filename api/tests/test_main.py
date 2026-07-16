import pandas as pd
import pytest

import main
from tests.conftest import make_synthetic_ohlcv, make_synthetic_market


def _hist(prediction, actual_direction, close):
    return {"prediction": prediction, "actualDirection": actual_direction, "close": close}


def test_generate_metrics_empty():
    assert main.generate_metrics([]) == {}


def test_generate_metrics_known_values():
    # 4 dias: 2 aciertos (buy/up, sell/down), 2 fallos (hold/up, buy/down)
    historical = [
        _hist("buy", "up", 100),
        _hist("sell", "down", 95),
        _hist("hold", "up", 100),
        _hist("buy", "down", 98),
    ]

    m = main.generate_metrics(historical)

    assert m["totalPredictions"] == 4
    assert m["correctPredictions"] == 2
    assert m["accuracy"] == pytest.approx(0.5)
    assert m["signal_buy_pct"] == pytest.approx(50.0)
    assert m["signal_sell_pct"] == pytest.approx(25.0)
    assert m["signal_hold_pct"] == pytest.approx(25.0)


def test_rows_from_predictions_actual_direction_thresholds():
    dates = pd.bdate_range("2026-01-01", periods=3)
    feat = pd.DataFrame({
        "raw_open": [100.0, 101.0, 100.5],
        "raw_high": [101.0, 103.0, 101.5],
        "raw_low": [99.0, 100.5, 97.0],
        "raw_close": [100.0, 102.0, 98.0],  # +2% luego -3.9%
        "raw_volume": [1_000_000, 1_100_000, 1_050_000],
    }, index=dates)
    predictions = [
        {"signal": "hold", "confidence": 0.4},
        {"signal": "buy", "confidence": 0.5},
        {"signal": "sell", "confidence": 0.6},
    ]

    rows = main.rows_from_predictions(feat, predictions)

    assert rows[0]["actualDirection"] == "neutral"  # primer dia, sin referencia previa
    assert rows[1]["actualDirection"] == "up"        # 100 -> 102 (+2%)
    assert rows[2]["actualDirection"] == "down"       # 102 -> 98 (-3.9%)
    assert rows[1]["prediction"] == "buy"
    assert rows[1]["confidence"] == 0.5


def test_build_recent_signals_correct_flag():
    rows = [
        {"date": "2026-01-01", "prediction": "buy", "actualDirection": "up", "close": 100.0},
        {"date": "2026-01-02", "prediction": "sell", "actualDirection": "up", "close": 101.0},
    ]

    signals = main.build_recent_signals(rows, limit=10)

    assert signals[0]["correct"] is True
    assert signals[1]["correct"] is False
    assert signals[0]["actualPrice"] == 100.0


def test_initialize_data_end_to_end(monkeypatch):
    """
    Integracion: initialize_data() con Yahoo Finance mockeado (datos
    sinteticos deterministas) debe poblar cache en memoria + SQLite y dejar
    la API respondiendo con señales reales del modelo.
    """
    ohlcv_by_symbol = {
        cfg["symbol"]: make_synthetic_ohlcv(seed=hash(cfg["symbol"]) % 1000)
        for cfg in main.STOCKS_CONFIG
    }
    market = make_synthetic_market(next(iter(ohlcv_by_symbol.values())).index)

    monkeypatch.setattr(main, "fetch_market_context", lambda period: market)
    monkeypatch.setattr(main, "fetch_ohlcv", lambda symbol, period: ohlcv_by_symbol[symbol])
    monkeypatch.setattr(main, "fetch_company_info", lambda symbol: {
        "symbol": symbol, "sector": "Test", "industry": "Test",
    })

    main.STOCKS_DATA.clear()
    main.HISTORICAL_DATA.clear()
    main.SIGNALS_DATA.clear()
    main.METRICS_DATA.clear()
    main.COMPANY_INFO.clear()

    main.initialize_data()

    assert len(main.STOCKS_DATA) == len(main.STOCKS_CONFIG)
    for symbol, stock in main.STOCKS_DATA.items():
        assert stock["signal"] in ("buy", "sell", "hold")
        assert 0.0 <= stock["confidence"] <= 1.0

    client = main.app.test_client()
    resp = client.get("/stocks")
    body = resp.get_json()
    assert resp.status_code == 200
    assert body["success"] is True
    assert len(body["data"]) == len(main.STOCKS_CONFIG)

    import database
    import models
    session = database.get_session()
    try:
        assets = session.query(models.Asset).count()
        predictions = session.query(models.Prediction).count()
        assert assets == len(main.STOCKS_CONFIG)
        assert predictions > 0
    finally:
        session.close()
