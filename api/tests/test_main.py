from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import main
from ml.target import etiquetas_reales
from tests.conftest import make_synthetic_ohlcv, make_synthetic_market


def _row(prediction, actual, next_return, confidence=0.4, date="2026-01-01"):
    return {"date": date, "prediction": prediction, "actualSignal": actual,
            "nextReturn": next_return, "confidence": confidence, "close": 100.0}


def test_generate_metrics_empty():
    assert main.generate_metrics([]) == {}


def test_generate_metrics_known_values():
    # 4 dias evaluados + 1 pendiente (el ultimo, sin cierre siguiente).
    rows = [
        _row("buy", "buy", 2.0),     # acierto, gana +2 %
        _row("sell", "sell", -1.0),  # acierto, gana +1 % (corto)
        _row("hold", "buy", 3.0),    # fallo, sin posicion
        _row("buy", "sell", -1.5),   # fallo, pierde 1.5 %
        _row("hold", None, None),    # pendiente
    ]

    m = main.generate_metrics(rows)

    assert m["totalPredictions"] == 5
    assert m["evaluatedPredictions"] == 4
    assert m["pendingPredictions"] == 1
    assert m["correctPredictions"] == 2
    assert m["accuracy"] == pytest.approx(0.5)
    # distribucion sobre las 5 señales emitidas
    assert m["signal_buy_pct"] == pytest.approx(40.0)
    assert m["signal_hold_pct"] == pytest.approx(40.0)
    assert m["signal_sell_pct"] == pytest.approx(20.0)
    # F1 reales (no precisiones): BUY 1 de 2 pred / 2 reales -> 0.5 ; SELL 1/1 pred, 1/2 reales -> 0.667 ; HOLD 0
    assert m["f1_buy"] == pytest.approx(0.5)
    assert m["f1_sell"] == pytest.approx(2 / 3, abs=1e-4)
    assert m["f1_hold"] == pytest.approx(0.0)
    assert m["f1_macro"] == pytest.approx((0.5 + 2 / 3 + 0) / 3, abs=1e-4)
    # estrategia: 3 dias con posicion (+2 %, +1 %, -1.5 %), 1 dia fuera
    assert m["numberOfTrades"] == 3
    assert m["sharpeRatio"] is None          # < MIN_DIAS_CON_POSICION: no interpretable
    assert m["profitFactor"] is None
    assert m["exposure"] == pytest.approx(75.0)
    assert m["winRate"] == pytest.approx(200 / 3, abs=0.01)
    esperado = (np.exp(np.log(1.02) - np.log(0.99) + np.log(0.985)) - 1) * 100
    assert m["cumulativeReturn"] == pytest.approx(esperado, abs=0.01)
    bh = (1.02 * 0.99 * 1.03 * 0.985 - 1) * 100
    assert m["bh_return"] == pytest.approx(bh, abs=0.01)
    assert m["maxDrawdown"] > 0


def test_generate_metrics_all_pending():
    m = main.generate_metrics([_row("hold", None, None)])
    assert m["evaluatedPredictions"] == 0
    assert "f1_macro" not in m


def test_rows_from_predictions_evalua_contra_el_dia_siguiente():
    dates = pd.bdate_range("2026-01-01", periods=3)
    feat = pd.DataFrame({
        "raw_open": [100.0, 101.0, 100.5],
        "raw_high": [101.0, 103.0, 101.5],
        "raw_low": [99.0, 100.5, 97.0],
        "raw_close": [100.0, 102.0, 98.0],
        "raw_volume": [1_000_000, 1_100_000, 1_050_000],
    }, index=dates)
    predictions = [
        {"signal": "buy", "confidence": 0.4, "probabilities": {"buy": 0.4, "hold": 0.35, "sell": 0.25}},
        {"signal": "sell", "confidence": 0.5, "probabilities": {"buy": 0.2, "hold": 0.3, "sell": 0.5}},
        {"signal": "hold", "confidence": 0.6, "probabilities": {"buy": 0.2, "hold": 0.6, "sell": 0.2}},
    ]
    # Umbrales conocidos: +-1 %. La señal del dia t se compara con t -> t+1.
    r = np.log(feat["raw_close"].shift(-1) / feat["raw_close"])
    reales = pd.DataFrame({
        "r_forward": r,
        "real": ["buy", "sell", None],
    }, index=dates)

    rows = main.rows_from_predictions(feat, predictions, reales)

    assert rows[0]["actualSignal"] == "buy"          # 100 -> 102
    assert rows[0]["nextReturn"] == pytest.approx(2.0)
    assert rows[0]["correct"] is True
    assert rows[1]["actualSignal"] == "sell"         # 102 -> 98
    assert rows[1]["correct"] is True
    assert rows[2]["actualSignal"] is None           # ultimo dia: pendiente
    assert rows[2]["nextReturn"] is None
    assert rows[2]["correct"] is None
    assert rows[1]["probabilities"]["sell"] == 0.5


def test_build_recent_signals_mas_reciente_primero():
    rows = [
        {"date": "2026-01-01", "prediction": "buy", "confidence": 0.4, "close": 100.0,
         "actualSignal": "buy", "nextReturn": 1.2, "correct": True},
        {"date": "2026-01-02", "prediction": "sell", "confidence": 0.4, "close": 101.0,
         "actualSignal": None, "nextReturn": None, "correct": None},
    ]

    signals = main.build_recent_signals(rows, limit=10)

    assert signals[0]["date"] == "2026-01-02"
    assert signals[0]["correct"] is None
    assert signals[1]["correct"] is True
    assert signals[1]["actualPrice"] == 100.0


def test_etiquetas_reales_semantica():
    close = pd.Series(100 * np.exp(np.cumsum(np.random.default_rng(0).normal(0, 0.01, 400))),
                      index=pd.bdate_range("2024-01-01", periods=400))
    et = etiquetas_reales(close)
    assert et["real"].iloc[-1] is None                    # sin cierre siguiente
    assert et["real"].iloc[:126].isna().all()             # sin historial para umbrales
    conocidas = et.dropna(subset=["real"])
    assert (conocidas.loc[conocidas.real == "buy", "r_forward"]
            >= conocidas.loc[conocidas.real == "buy", "umbral_buy"]).all()
    assert (conocidas.loc[conocidas.real == "sell", "r_forward"]
            <= conocidas.loc[conocidas.real == "sell", "umbral_sell"]).all()


RAW_AAPL = Path(__file__).resolve().parents[2] / "tesis_ml_stocks" / "01_raw_datasets" / "AAPL_raw.parquet"


@pytest.mark.skipif(not RAW_AAPL.exists(), reason="dataset de entrenamiento no disponible")
def test_etiquetas_reales_coinciden_con_el_target_de_entrenamiento():
    df = pd.read_parquet(RAW_AAPL)
    et = etiquetas_reales(df["raw_close"])
    mapa = {0: "sell", 1: "hold", 2: "buy"}
    # Solo donde la ventana de 252 dias ya esta completa: el parquet se recorto
    # despues de calcular el target, asi que sus primeros umbrales usaron
    # historial previo que aqui no existe.
    m = et["real"].notna() & (np.arange(len(df)) > 252)
    assert m.sum() > 2500
    assert (et.loc[m, "real"] == df.loc[m, "target"].map(mapa)).all()


def test_market_status_horario_y_feriados():
    ny = main.NYSE_TZ
    abierto = datetime(2026, 9, 29, 11, 0, tzinfo=ny)      # martes 11:00
    cerrado = datetime(2026, 9, 29, 17, 0, tzinfo=ny)      # martes 17:00
    feriado = datetime(2026, 9, 7, 11, 0, tzinfo=ny)       # Labor Day
    sabado = datetime(2026, 9, 26, 11, 0, tzinfo=ny)
    assert main.market_status(abierto)["isOpen"] is True
    assert main.market_status(cerrado)["isOpen"] is False
    assert main.market_status(feriado)["isTradingDay"] is False
    assert main.market_status(sabado)["isOpen"] is False


def test_sin_vela_en_curso_descarta_el_dia_mientras_nyse_esta_abierto():
    ny = main.NYSE_TZ
    df = pd.DataFrame({"Close": [1.0, 2.0]}, index=pd.to_datetime(["2026-09-29", "2026-09-30"]))
    assert len(main.sin_vela_en_curso(df, datetime(2026, 9, 30, 14, 45, tzinfo=ny))) == 1
    assert len(main.sin_vela_en_curso(df, datetime(2026, 9, 30, 16, 30, tzinfo=ny))) == 2
    assert len(main.sin_vela_en_curso(df, datetime(2026, 10, 1, 10, 0, tzinfo=ny))) == 2


def test_completar_catalogo_reintenta_solo_si_falta(monkeypatch):
    llamadas = []
    monkeypatch.setattr(main, "_initialize_data", lambda: llamadas.append(1))

    main.STOCKS_DATA.clear()
    main.completar_catalogo_si_falta()
    assert llamadas == [1]

    for cfg in main.STOCKS_CONFIG:
        main.STOCKS_DATA[cfg["symbol"]] = {}
    main.completar_catalogo_si_falta()
    assert llamadas == [1]          # catalogo completo: no recalcula
    main.STOCKS_DATA.clear()


def test_overrides_desactivados_por_defecto():
    client = main.app.test_client()
    resp = client.post("/stocks/AAPL", json={"signal": "buy"})
    assert resp.status_code == 403


def test_initialize_data_end_to_end(monkeypatch):
    """
    Integracion: initialize_data() con Yahoo Finance mockeado (datos
    sinteticos deterministas) debe poblar cache en memoria + SQLite y dejar
    la API respondiendo con señales reales del modelo.
    """
    ohlcv_by_symbol = {
        cfg["symbol"]: make_synthetic_ohlcv(n_days=420, seed=hash(cfg["symbol"]) % 1000)
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
        assert stock["confidence"] == pytest.approx(max(stock["probabilities"].values()))
        assert stock["lastUpdate"].endswith("Z") and "+00:00" not in stock["lastUpdate"]

    client = main.app.test_client()
    resp = client.get("/stocks")
    body = resp.get_json()
    assert resp.status_code == 200
    assert body["success"] is True
    assert len(body["data"]) == len(main.STOCKS_CONFIG)

    symbol = main.STOCKS_CONFIG[0]["symbol"]
    for days in main.WINDOWS:
        resp = client.get(f"/stocks/{symbol}/metrics?days={days}")
        assert resp.status_code == 200
        assert resp.get_json()["data"]["windowDays"] == days
        assert resp.get_json()["data"]["totalPredictions"] == days
    assert client.get(f"/stocks/{symbol}/metrics?days=45").status_code == 404
    assert len(client.get("/metrics?days=90").get_json()["data"]) == len(main.STOCKS_CONFIG)

    detail = client.get(f"/stocks/{symbol}").get_json()["data"]
    assert detail["recentSignals"][0]["correct"] is None      # hoy: aun sin resultado

    info = client.get("/model").get_json()["data"]
    assert info["nFeatures"] == len(main.load_model().feat_cols)
    assert info["target"]["percentileBuy"] == 70

    import database
    import models
    session = database.get_session()
    try:
        assets = session.query(models.Asset).count()
        predictions = session.query(models.Prediction).count()
        assert assets == len(main.STOCKS_CONFIG)
        assert predictions > 0
        assert session.query(models.Prediction).filter(models.Prediction.prob_hold.isnot(None)).count() == predictions
    finally:
        session.close()
