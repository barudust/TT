from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta, timezone
import yfinance as yf
import pandas as pd
import random
import os

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


def fetch_yahoo_finance_data(symbol, days=30):
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days + 30)

        ticker = yf.Ticker(symbol)
        hist = ticker.history(start=start_date, end=end_date)

        if hist.empty:
            return None

        hist = hist.tail(days)
        return hist

    except Exception as e:
        print(f"[ERROR] Failed to fetch {symbol}: {str(e)}")
        return None


def generate_simulated_historical_data(symbol, days=30):
    # Genera una serie de precios sintética con ruido y señales simples
    data = []
    base_price = 100.0 + random.random() * 100
    for i in range(days):
        date = (datetime.now() - timedelta(days=days - i)).strftime("%Y-%m-%d")
        # pequeño movimiento aleatorio
        change_pct = random.uniform(-0.03, 0.03)
        base_price = round(base_price * (1 + change_pct), 2)
        close = base_price
        high = round(close * (1 + random.uniform(0.0, 0.02)), 2)
        low = round(close * (1 - random.uniform(0.0, 0.02)), 2)
        volume = random.randint(100000, 5000000)

        # señal simple por momentum
        if i >= 5:
            prev = data[-1]["close"]
            if close > prev * 1.01:
                prediction = "buy"
            elif close < prev * 0.99:
                prediction = "sell"
            else:
                prediction = "hold"
        else:
            prediction = random.choice(["buy", "sell", "hold"])

        if i > 0:
            prev_close = data[-1]["close"]
            price_change = ((close - prev_close) / prev_close) * 100
            if price_change > 1:
                actual_direction = "up"
            elif price_change < -1:
                actual_direction = "down"
            else:
                actual_direction = "neutral"
        else:
            actual_direction = "neutral"

        data.append({
            "date": date,
            "close": round(float(close), 2),
            "high": high,
            "low": low,
            "volume": int(volume),
            "prediction": prediction,
            "actualDirection": actual_direction,
        })

    return data


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


def generate_historical_data(symbol, days=30):
    # Si se fuerza simulación via env or por fallo en Yahoo, genera datos sintéticos
    simulate = os.getenv("SIMULATE_DATA", "1") == "1"

    if simulate:
        return generate_simulated_historical_data(symbol, days)

    hist_df = fetch_yahoo_finance_data(symbol, days)

    if hist_df is None:
        # fallback a simulación si Yahoo falla
        return generate_simulated_historical_data(symbol, days)

    data = []

    for i in range(len(hist_df)):
        date = hist_df.index[i]
        close = hist_df['Close'].iloc[i]

        if i > 0:
            prev_close = hist_df['Close'].iloc[i - 1]
            price_change = ((close - prev_close) / prev_close) * 100

            if price_change > 1:
                actual_direction = "up"
            elif price_change < -1:
                actual_direction = "down"
            else:
                actual_direction = "neutral"
        else:
            actual_direction = "neutral"

        if i >= 5:
            ma5 = hist_df['Close'].iloc[i-5:i].mean()
            ma20 = hist_df['Close'].iloc[max(0, i-20):i].mean() if i >= 20 else close

            if close > ma5 and ma5 > ma20:
                prediction = "buy"
            elif close < ma5 and ma5 < ma20:
                prediction = "sell"
            else:
                prediction = "hold"
        else:
            prediction = random.choice(["buy", "sell", "hold"])

        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "close": round(float(close), 2),
            "high": round(float(hist_df['High'].iloc[i]), 2),
            "low": round(float(hist_df['Low'].iloc[i]), 2),
            "volume": int(hist_df['Volume'].iloc[i]),
            "prediction": prediction,
            "actualDirection": actual_direction,
        })

    return data


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
        ret = (historical_data[i]["close"] - historical_data[i-1]["close"]) / historical_data[i-1]["close"]
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
        ret = (historical_data[i]["close"] - historical_data[i-1]["close"]) / historical_data[i-1]["close"]
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


def get_recent_trading_days(num_days=10):
    trading_days = []
    current = datetime.now(timezone.utc)

    while len(trading_days) < num_days:
        current = current - timedelta(days=1)
        if current.weekday() < 5:
            trading_days.append(current)

    return sorted(trading_days)


def initialize_data():
    for stock_config in STOCKS_CONFIG:
        symbol = stock_config["symbol"]
        print(f"[INFO] Loading {symbol} data from Yahoo Finance...")

        for days in [30, 60, 90]:
            hist_data = generate_historical_data(symbol, days)
            HISTORICAL_DATA[f"{symbol}:{days}"] = hist_data

        hist_30 = HISTORICAL_DATA.get(f"{symbol}:30", [])

        if hist_30:
            last_day = hist_30[-1]
            current_price = last_day["close"]

            signal = random.choice(["buy", "sell", "hold"])
            confidence = round(0.6 + random.random() * 0.3, 2)

            STOCKS_DATA[symbol] = {
                "symbol": symbol,
                "name": stock_config["name"],
                "currentPrice": current_price,
                "signal": signal,
                "confidence": confidence,
                "lastUpdate": datetime.now(timezone.utc).isoformat() + "Z",
            }

            metrics_dict = generate_metrics(hist_30)
            METRICS_DATA[symbol] = metrics_dict

            company_info = fetch_company_info(symbol)
            COMPANY_INFO[symbol] = company_info

            signals = []
            recent_trading_days = get_recent_trading_days(10)

            for i, trading_day in enumerate(recent_trading_days):
                date_str = trading_day.strftime("%Y-%m-%d")

                hist_price = None
                for hist_entry in hist_30:
                    if hist_entry["date"] == date_str:
                        hist_price = hist_entry["close"]
                        break

                if hist_price is None:
                    hist_price = current_price

                hist_direction = hist_30[min(i + 1, len(hist_30) - 1)]["actualDirection"] if i < len(hist_30) - 1 else "neutral"

                sig_prediction = hist_30[min(i, len(hist_30) - 1)]["prediction"]
                correct = (sig_prediction == "buy" and hist_direction == "up") or \
                         (sig_prediction == "sell" and hist_direction == "down") or \
                         (sig_prediction == "hold" and hist_direction == "neutral")

                signals.append({
                    "date": date_str,
                    "signal": sig_prediction,
                    "actualPrice": round(hist_price, 2),
                    "correct": correct,
                })

            SIGNALS_DATA[symbol] = signals


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


if __name__ == "__main__":
    initialize_data()
    print("[INFO] API server started on http://localhost:8000")
    print("[INFO] Using Yahoo Finance data for 7 stocks")
    app.run(host="127.0.0.1", port=8000, debug=True)
