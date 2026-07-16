from datetime import datetime, date, timezone

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import yfinance as yf

import database
import models
from ml.features import fetch_ohlcv, fetch_market_context, build_feature_frame
from ml.model import load_model, MODEL_VERSION

load_dotenv()

app = Flask(__name__)
CORS(app)

STOCKS_DATA = {}
HISTORICAL_DATA = {}
SIGNALS_DATA = {}
METRICS_DATA = {}
COMPANY_INFO = {}

STOCKS_CONFIG = [
    {"symbol": "AAPL", "name": "Apple Inc."},
    {"symbol": "MSFT", "name": "Microsoft Corporation"},
    {"symbol": "GOOGL", "name": "Alphabet Inc."},
    {"symbol": "AMZN", "name": "Amazon.com Inc."},
    {"symbol": "TSLA", "name": "Tesla Inc."},
    {"symbol": "META", "name": "Meta Platforms Inc."},
    {"symbol": "NVDA", "name": "NVIDIA Corporation"},
]

# Historial suficiente para el warmup de indicadores (MA200, VIX rolling 252d)
FEATURE_LOOKBACK_PERIOD = "3y"


def fetch_company_info(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        return {
            "symbol": symbol,
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "marketCap": info.get("marketCap", 0),
            "employees": info.get("fullTimeEmployees", 0),
            "website": info.get("website", ""),
            "peRatio": info.get("trailingPE", 0),
            "pegRatio": info.get("pegRatio", 0),
            "dividendYield": info.get("dividendYield", 0),
            "beta": info.get("beta", 0),
            "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh", 0),
            "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow", 0),
            "averageVolume": info.get("averageVolume", 0),
        }
    except Exception as e:
        print(f"[ERROR] Failed to fetch info for {symbol}: {str(e)}")
        return {}


def rows_from_predictions(feat_df, predictions):
    """
    Combina OHLCV real + predicciones del modelo en la forma que consume
    el frontend (ver docs/API.md). actualDirection se deriva del cambio de
    precio real dia a dia (no es informacion futura: para el ultimo dia
    disponible queda como "neutral" porque aun no hay cierre siguiente).
    """
    rows = []
    closes = feat_df["raw_close"].tolist()
    dates = feat_df.index

    for i, (idx_date, pred) in enumerate(zip(dates, predictions)):
        close = float(closes[i])
        if i > 0:
            prev_close = closes[i - 1]
            price_change = ((close - prev_close) / prev_close) * 100
            if price_change > 1:
                actual_direction = "up"
            elif price_change < -1:
                actual_direction = "down"
            else:
                actual_direction = "neutral"
        else:
            actual_direction = "neutral"

        rows.append({
            "date": idx_date.strftime("%Y-%m-%d"),
            "open": round(float(feat_df["raw_open"].iloc[i]), 2),
            "close": round(close, 2),
            "high": round(float(feat_df["raw_high"].iloc[i]), 2),
            "low": round(float(feat_df["raw_low"].iloc[i]), 2),
            "volume": int(feat_df["raw_volume"].iloc[i]),
            "prediction": pred["signal"],
            "confidence": round(pred["confidence"], 4),
            "actualDirection": actual_direction,
        })

    return rows


def build_recent_signals(rows, limit=10):
    """Ultimas `limit` señales con su acierto/error frente al movimiento real."""
    recent = rows[-limit:]
    signals = []
    for r in recent:
        correct = (
            (r["prediction"] == "buy" and r["actualDirection"] == "up") or
            (r["prediction"] == "sell" and r["actualDirection"] == "down") or
            (r["prediction"] == "hold" and r["actualDirection"] == "neutral")
        )
        signals.append({
            "date": r["date"],
            "signal": r["prediction"],
            "actualPrice": r["close"],
            "correct": correct,
        })
    return signals


def generate_metrics(historical_data):
    # Devuelve las métricas esperadas por el frontend (nombres estandarizados)
    if not historical_data:
        return {}

    total = len(historical_data)
    buy_count = sum(1 for d in historical_data if d["prediction"] == "buy")
    sell_count = sum(1 for d in historical_data if d["prediction"] == "sell")
    hold_count = sum(1 for d in historical_data if d["prediction"] == "hold")

    signal_buy_pct = round(buy_count / total * 100, 2) if total > 0 else 0
    signal_sell_pct = round(sell_count / total * 100, 2) if total > 0 else 0
    signal_hold_pct = round(hold_count / total * 100, 2) if total > 0 else 0

    correct = 0
    buy_correct = sell_correct = 0
    buy_total = sell_total = 0

    for d in historical_data:
        pred = d["prediction"]
        actual = d["actualDirection"]
        ok = (pred == "buy" and actual == "up") or (pred == "sell" and actual == "down") or (pred == "hold" and actual == "neutral")
        if ok:
            correct += 1
        if pred == "buy":
            buy_total += 1
            if actual == "up":
                buy_correct += 1
        if pred == "sell":
            sell_total += 1
            if actual == "down":
                sell_correct += 1

    accuracy = round(correct / total, 4) if total > 0 else 0
    f1_buy = round((buy_correct / buy_total) if buy_total > 0 else 0, 4)
    f1_sell = round((sell_correct / sell_total) if sell_total > 0 else 0, 4)
    f1_macro = round(((f1_buy + f1_sell) / 2) if (f1_buy or f1_sell) else accuracy, 4)

    capital = 1000.0
    position = None
    entry_price = None
    trades = []
    trading_days = 0

    for d in historical_data:
        sig = d["prediction"]
        price = d["close"]
        if sig == "buy" and position is None:
            position = price
            entry_price = price
            trading_days += 1
        elif sig == "sell" and position is not None:
            exit_price = price
            profit_pct = ((exit_price - entry_price) / entry_price) * 100
            trades.append({"entry": entry_price, "exit": exit_price, "profit": profit_pct})
            capital *= (1 + (exit_price - entry_price) / entry_price)
            position = None
            entry_price = None
            trading_days += 1
        elif sig == "hold" and position is not None:
            trading_days += 1

    if position is not None:
        final_price = historical_data[-1]["close"]
        capital *= (1 + (final_price - position) / position)

    cumulative_return = round(((capital - 1000.0) / 1000.0) * 100, 2)

    bh_return = 0
    if total > 1:
        bh_return = round(((historical_data[-1]["close"] - historical_data[0]["close"]) / historical_data[0]["close"]) * 100, 2)

    return_vs_bh = round(cumulative_return - bh_return, 2)

    win_rate = round((len([t for t in trades if t["profit"] > 0]) / len(trades) * 100) if trades else 0, 2)

    gross_profit = sum([t["profit"] for t in trades if t["profit"] > 0])
    gross_loss = abs(sum([t["profit"] for t in trades if t["profit"] < 0]))
    profit_factor = round(gross_profit / gross_loss, 2) if gross_loss > 0 else 0

    daily_returns = []
    for i in range(1, total):
        ret = (historical_data[i]["close"] - historical_data[i - 1]["close"]) / historical_data[i - 1]["close"]
        daily_returns.append(ret)

    if daily_returns:
        avg = sum(daily_returns) / len(daily_returns)
        var = sum([(r - avg) ** 2 for r in daily_returns]) / len(daily_returns)
        std = var ** 0.5
        sharpe = round((avg / std * (252 ** 0.5)), 2) if std > 0 else 0
    else:
        sharpe = 0

    cumulative = 1000.0
    peak = 1000.0
    max_dd = 0
    for i in range(1, total):
        ret = (historical_data[i]["close"] - historical_data[i - 1]["close"]) / historical_data[i - 1]["close"]
        cumulative *= (1 + ret)
        if cumulative > peak:
            peak = cumulative
        dd = ((peak - cumulative) / peak) * 100
        if dd > max_dd:
            max_dd = dd

    exposure = round((trading_days / total * 100), 2) if total > 0 else 0

    return {
        "accuracy": round(accuracy, 4),
        "f1_macro": f1_macro,
        "f1_buy": f1_buy,
        "f1_sell": f1_sell,
        "cumulativeReturn": cumulative_return,
        "return_vs_bh": return_vs_bh,
        "sharpeRatio": sharpe,
        "maxDrawdown": round(max_dd, 2),
        "winRate": win_rate,
        "profitFactor": profit_factor,
        "numberOfTrades": len(trades),
        "exposure": exposure,
        "finalCapital": round(capital, 2),
        "evaluationPeriod": total,
        "signal_buy_pct": signal_buy_pct,
        "signal_hold_pct": signal_hold_pct,
        "signal_sell_pct": signal_sell_pct,
        "totalPredictions": total,
        "correctPredictions": correct,
    }


def persist_to_db(session, symbol, name, company_info, rows, metrics_by_window):
    asset = session.query(models.Asset).filter_by(ticker=symbol).one_or_none()
    if asset is None:
        asset = models.Asset(ticker=symbol, name=name)
        session.add(asset)
        session.flush()

    asset.name = name
    asset.sector = company_info.get("sector")
    asset.industry = company_info.get("industry")

    session.query(models.OHLCVDaily).filter_by(asset_id=asset.id).delete()
    session.query(models.Prediction).filter_by(asset_id=asset.id).delete()

    for row in rows:
        d = datetime.strptime(row["date"], "%Y-%m-%d").date()
        session.add(models.OHLCVDaily(
            asset_id=asset.id, date=d,
            open=row["open"], high=row["high"], low=row["low"],
            close=row["close"], volume=row["volume"],
        ))
        session.add(models.Prediction(
            asset_id=asset.id, date=d, signal=row["prediction"],
            confidence=row["confidence"], actual_price=row["close"],
            model_version=MODEL_VERSION,
        ))

    for window_days, m in metrics_by_window.items():
        if not m:
            continue
        metric = session.query(models.Metric).filter_by(asset_id=asset.id, window_days=window_days).one_or_none()
        if metric is None:
            metric = models.Metric(asset_id=asset.id, window_days=window_days)
            session.add(metric)
        metric.model_version = MODEL_VERSION
        metric.accuracy = m.get("accuracy")
        metric.f1_macro = m.get("f1_macro")
        metric.f1_buy = m.get("f1_buy")
        metric.f1_sell = m.get("f1_sell")
        metric.cumulative_return = m.get("cumulativeReturn")
        metric.return_vs_bh = m.get("return_vs_bh")
        metric.sharpe_ratio = m.get("sharpeRatio")
        metric.max_drawdown = m.get("maxDrawdown")
        metric.win_rate = m.get("winRate")
        metric.profit_factor = m.get("profitFactor")
        metric.number_of_trades = m.get("numberOfTrades")
        metric.exposure = m.get("exposure")
        metric.final_capital = m.get("finalCapital")
        metric.signal_buy_pct = m.get("signal_buy_pct")
        metric.signal_hold_pct = m.get("signal_hold_pct")
        metric.signal_sell_pct = m.get("signal_sell_pct")

    session.commit()


def initialize_data():
    database.init_db()
    model = load_model()
    session = database.get_session()

    print("[INFO] Descargando contexto de mercado (SPY, VIX)...")
    try:
        market = fetch_market_context(FEATURE_LOOKBACK_PERIOD)
    except Exception as e:
        print(f"[ERROR] No se pudo descargar contexto de mercado: {e}")
        market = None

    for stock_config in STOCKS_CONFIG:
        symbol = stock_config["symbol"]
        print(f"[INFO] Procesando {symbol}...")

        if market is None:
            print(f"[WARN] {symbol}: se omite (sin contexto de mercado).")
            continue

        try:
            ohlcv = fetch_ohlcv(symbol, FEATURE_LOOKBACK_PERIOD)
            feat = build_feature_frame(ohlcv, market)
            if feat.empty:
                raise ValueError("historial insuficiente tras calcular indicadores")
            predictions = model.predict_frame(feat)
        except Exception as e:
            print(f"[WARN] {symbol}: fallo al calcular señales reales ({e}). Se omite.")
            continue

        rows = rows_from_predictions(feat, predictions)

        for days in [30, 60, 90]:
            HISTORICAL_DATA[f"{symbol}:{days}"] = rows[-days:]

        last_row = rows[-1]

        STOCKS_DATA[symbol] = {
            "symbol": symbol,
            "name": stock_config["name"],
            "currentPrice": last_row["close"],
            "signal": last_row["prediction"],
            "confidence": last_row["confidence"],
            "lastUpdate": datetime.now(timezone.utc).isoformat() + "Z",
        }

        metrics_by_window = {
            days: generate_metrics(HISTORICAL_DATA[f"{symbol}:{days}"])
            for days in [30, 60, 90]
        }
        METRICS_DATA[symbol] = metrics_by_window[30]

        company_info = fetch_company_info(symbol)
        COMPANY_INFO[symbol] = company_info

        SIGNALS_DATA[symbol] = build_recent_signals(rows, limit=10)

        try:
            persist_to_db(session, symbol, stock_config["name"], company_info, rows, metrics_by_window)
        except Exception as e:
            session.rollback()
            print(f"[WARN] {symbol}: fallo al persistir en base de datos ({e}).")

    session.close()
    print(f"[INFO] Listo. {len(STOCKS_DATA)}/{len(STOCKS_CONFIG)} acciones con señal real del modelo {MODEL_VERSION}.")


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})


@app.route("/stocks", methods=["GET"])
def get_stocks():
    stocks_list = list(STOCKS_DATA.values())
    return jsonify({"success": True, "data": stocks_list})


@app.route("/stocks/<symbol>", methods=["GET"])
def get_stock_detail(symbol):
    if symbol not in STOCKS_DATA:
        return jsonify({"success": False, "error": f"Stock {symbol} not found"}), 404

    stock = STOCKS_DATA[symbol]
    recent_signals = SIGNALS_DATA.get(symbol, [])
    company_info = COMPANY_INFO.get(symbol, {})

    return jsonify({
        "success": True,
        "data": {
            **stock,
            "recentSignals": recent_signals,
            "companyInfo": company_info,
        }
    })


@app.route("/stocks/<symbol>/history", methods=["GET"])
def get_historical_data(symbol):
    days = request.args.get("days", 30, type=int)
    key = f"{symbol}:{days}"

    if key not in HISTORICAL_DATA:
        return jsonify({"success": False, "error": f"History for {symbol} not found"}), 404

    return jsonify({"success": True, "data": HISTORICAL_DATA[key]})


@app.route("/stocks/<symbol>/metrics", methods=["GET"])
def get_performance_metrics(symbol):
    if symbol not in METRICS_DATA:
        return jsonify({"success": False, "error": f"Metrics for {symbol} not found"}), 404

    return jsonify({"success": True, "data": METRICS_DATA[symbol]})


@app.route("/metrics", methods=["GET"])
def get_all_metrics():
    all_metrics = []

    for symbol, stock in STOCKS_DATA.items():
        metrics = METRICS_DATA.get(symbol)
        if metrics:
            all_metrics.append({
                "symbol": symbol,
                "name": stock["name"],
                **metrics,
            })

    return jsonify({"success": True, "data": all_metrics})


@app.route("/stocks/<symbol>/info", methods=["GET"])
def get_company_info(symbol):
    if symbol not in COMPANY_INFO:
        return jsonify({"success": False, "error": f"Info for {symbol} not found"}), 404

    return jsonify({"success": True, "data": COMPANY_INFO[symbol]})


@app.route("/stocks", methods=["POST"])
def update_stocks():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({"success": False, "error": "Expected list of stocks"}), 400

    for stock in data:
        if "symbol" in stock:
            STOCKS_DATA[stock["symbol"]] = stock

    return jsonify({
        "success": True,
        "message": f"Updated {len(data)} stocks",
        "data": data
    })


@app.route("/stocks/<symbol>", methods=["POST"])
def update_stock(symbol):
    data = request.get_json()
    STOCKS_DATA[symbol] = data

    return jsonify({
        "success": True,
        "message": f"Updated {symbol}",
        "data": data
    })


@app.route("/stocks/<symbol>/history", methods=["POST"])
def update_historical_data(symbol):
    data = request.get_json()
    days = request.args.get("days", 30, type=int)
    key = f"{symbol}:{days}"
    HISTORICAL_DATA[key] = data

    return jsonify({
        "success": True,
        "message": f"Updated history for {symbol} ({days} days)",
        "data": data
    })


@app.route("/stocks/<symbol>/metrics", methods=["POST"])
def update_metrics(symbol):
    data = request.get_json()
    METRICS_DATA[symbol] = data

    return jsonify({
        "success": True,
        "message": f"Updated metrics for {symbol}",
        "data": data
    })


@app.route("/stocks/<symbol>/signals", methods=["POST"])
def update_signals(symbol):
    data = request.get_json()
    SIGNALS_DATA[symbol] = data

    return jsonify({
        "success": True,
        "message": f"Updated {len(data)} signals for {symbol}",
        "data": data
    })


@app.route("/admin/refresh", methods=["POST"])
def refresh_data():
    """Vuelve a descargar datos de mercado y recalcular señales con el modelo."""
    try:
        initialize_data()
        return jsonify({"success": True, "message": f"Refrescado. {len(STOCKS_DATA)} acciones activas."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    initialize_data()
    print("[INFO] API server started on http://localhost:8000")
    app.run(host="127.0.0.1", port=8000, debug=True, use_reloader=False)
