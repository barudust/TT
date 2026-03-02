"""
API Local para TradingSignals AI (Flask)
Reemplaza la funcionalidad de Supabase Edge Functions
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta, timezone
import json
import random

app = Flask(__name__)
CORS(app)

# Base de datos simulada en memoria
STOCKS_DATA = {}
HISTORICAL_DATA = {}
SIGNALS_DATA = {}
METRICS_DATA = {}

# Acciones a seguir
STOCKS_CONFIG = [
    {"symbol": "AAPL", "name": "Apple Inc."},
    {"symbol": "MSFT", "name": "Microsoft Corporation"},
    {"symbol": "GOOGL", "name": "Alphabet Inc."},
    {"symbol": "AMZN", "name": "Amazon.com Inc."},
    {"symbol": "TSLA", "name": "Tesla Inc."},
    {"symbol": "META", "name": "Meta Platforms Inc."},
    {"symbol": "NVDA", "name": "NVIDIA Corporation"},
    {"symbol": "JPM", "name": "JPMorgan Chase & Co."},
]

BASE_PRICES = {
    "AAPL": 175.00,
    "MSFT": 410.00,
    "GOOGL": 140.00,
    "AMZN": 175.00,
    "TSLA": 195.00,
    "META": 485.00,
    "NVDA": 875.00,
    "JPM": 195.00,
}

# ============================================================================
# UTILIDADES
# ============================================================================

def generate_historical_data(symbol, days=30):
    """Genera datos históricos simulados"""
    data = []
    base_price = BASE_PRICES.get(symbol, 100)
    current_price = base_price
    today = datetime(2026, 3, 2)

    for i in range(days - 1, -1, -1):
        date = today - timedelta(days=i)

        # Simular variación de precio (-3% a +3%)
        variation = (random.random() - 0.5) * 0.06
        current_price = current_price * (1 + variation)

        # Generar señal aleatoria pero realista
        rand = random.random()
        if variation > 0.01:
            actual_direction = "up"
            prediction = "buy" if rand > 0.3 else ("hold" if rand > 0.15 else "sell")
        elif variation < -0.01:
            actual_direction = "down"
            prediction = "sell" if rand > 0.3 else ("hold" if rand > 0.15 else "buy")
        else:
            actual_direction = "neutral"
            prediction = "hold" if rand > 0.5 else ("buy" if rand > 0.25 else "sell")

        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "close": round(current_price, 2),
            "prediction": prediction,
            "actualDirection": actual_direction,
        })

    return data

def generate_metrics(historical_data):
    """Genera métricas de rendimiento basadas en datos históricos"""
    correct = 0
    buy_correct = buy_total = 0
    sell_correct = sell_total = 0
    hold_correct = hold_total = 0

    for day in historical_data:
        prediction_correct = (
            (day["prediction"] == "buy" and day["actualDirection"] == "up") or
            (day["prediction"] == "sell" and day["actualDirection"] == "down") or
            (day["prediction"] == "hold" and day["actualDirection"] == "neutral")
        )

        if prediction_correct:
            correct += 1

        if day["prediction"] == "buy":
            buy_total += 1
            if day["actualDirection"] == "up":
                buy_correct += 1
        elif day["prediction"] == "sell":
            sell_total += 1
            if day["actualDirection"] == "down":
                sell_correct += 1
        elif day["prediction"] == "hold":
            hold_total += 1
            if day["actualDirection"] == "neutral":
                hold_correct += 1

    # Métricas de clasificación
    accuracy = round(correct / len(historical_data), 2) if len(historical_data) > 0 else 0
    buy_precision = round(buy_correct / buy_total, 2) if buy_total > 0 else 0
    sell_precision = round(sell_correct / sell_total, 2) if sell_total > 0 else 0
    hold_precision = round(hold_correct / hold_total, 2) if hold_total > 0 else 0

    # F1-Score macro
    f1_score = round(accuracy * 0.95, 2)

    # Simulación de estrategia de trading
    capital = 1000.0  # Capital inicial
    position = None  # None = sin posición, "long" = comprado
    trades = []
    trading_days = 0

    for i in range(len(historical_data)):
        day = historical_data[i]
        signal = day["prediction"]
        price = day["close"]

        # Ejecutar signal
        if signal == "buy" and position is None:
            position = price
            entry_price = price
            trading_days += 1
        elif signal == "sell" and position is not None:
            exit_price = price
            profit = ((exit_price - entry_price) / entry_price) * 100
            trades.append({
                "entry": entry_price,
                "exit": exit_price,
                "profit": profit
            })
            capital *= (1 + (exit_price - entry_price) / entry_price)
            position = None
            trading_days += 1
        elif signal == "hold" and position is not None:
            trading_days += 1

    # Cerrar posición abierta
    if position is not None and len(historical_data) > 0:
        final_price = historical_data[-1]["close"]
        profit = ((final_price - position) / position) * 100
        capital *= (1 + (final_price - position) / position)

    # Cálculos de rendimiento
    cumulative_return = ((capital - 1000) / 1000) * 100
    win_rate = (len([t for t in trades if t["profit"] > 0]) / len(trades) * 100) if trades else 0

    # Profit Factor
    gross_profit = sum([t["profit"] for t in trades if t["profit"] > 0])
    gross_loss = abs(sum([t["profit"] for t in trades if t["profit"] < 0]))
    profit_factor = round(gross_profit / gross_loss, 2) if gross_loss > 0 else 0

    # Sharpe Ratio (simplificado)
    daily_returns = []
    for i in range(1, len(historical_data)):
        ret = (historical_data[i]["close"] - historical_data[i-1]["close"]) / historical_data[i-1]["close"]
        daily_returns.append(ret)

    if daily_returns:
        avg_return = sum(daily_returns) / len(daily_returns)
        variance = sum([(r - avg_return)**2 for r in daily_returns]) / len(daily_returns)
        std_dev = variance ** 0.5
        sharpe_ratio = round((avg_return / std_dev * (252**0.5)), 2) if std_dev > 0 else 0
    else:
        sharpe_ratio = 0

    # Maximum Drawdown
    cumulative = 1000
    peak = 1000
    max_drawdown = 0
    for i in range(len(historical_data)):
        if i == 0:
            continue
        ret = (historical_data[i]["close"] - historical_data[i-1]["close"]) / historical_data[i-1]["close"]
        cumulative *= (1 + ret)
        if cumulative > peak:
            peak = cumulative
        drawdown = ((peak - cumulative) / peak) * 100
        if drawdown > max_drawdown:
            max_drawdown = drawdown

    # Exposición
    exposure = (trading_days / len(historical_data) * 100) if len(historical_data) > 0 else 0

    return {
        "accuracy": accuracy,
        "buyPrecision": buy_precision,
        "sellPrecision": sell_precision,
        "holdPrecision": hold_precision,
        "f1Score": f1_score,
        "evaluationPeriod": len(historical_data),
        "totalPredictions": len(historical_data),
        "correctPredictions": correct,
        # Métricas de estrategia
        "cumulativeReturn": round(cumulative_return, 2),
        "sharpeRatio": sharpe_ratio,
        "winRate": round(win_rate, 2),
        "profitFactor": profit_factor,
        "maxDrawdown": round(max_drawdown, 2),
        "numberOfTrades": len(trades),
        "exposure": round(exposure, 2),
        "finalCapital": round(capital, 2),
    }

def initialize_dummy_data():
    """Inicializa la BD con datos simulados"""
    for stock_config in STOCKS_CONFIG:
        symbol = stock_config["symbol"]

        # Generar datos históricos
        hist_data = generate_historical_data(symbol, 30)
        HISTORICAL_DATA[f"{symbol}:30"] = hist_data
        HISTORICAL_DATA[f"{symbol}:60"] = generate_historical_data(symbol, 60)
        HISTORICAL_DATA[f"{symbol}:90"] = generate_historical_data(symbol, 90)

        # Generar señal actual
        last_day = hist_data[-1]
        signal = random.choice(["buy", "sell", "hold"])
        confidence = round(0.6 + random.random() * 0.3, 2)

        # Crear stock
        STOCKS_DATA[symbol] = {
            "symbol": symbol,
            "name": stock_config["name"],
            "currentPrice": last_day["close"],
            "signal": signal,
            "confidence": confidence,
            "lastUpdate": datetime.now(timezone.utc).isoformat() + "Z",
        }

        # Generar métricas
        metrics_dict = generate_metrics(hist_data)
        METRICS_DATA[symbol] = metrics_dict

        # Generar historial de señales
        signals = []
        for i in range(10, 0, -1):
            date = (datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d")
            sig_type = random.choice(["buy", "sell", "hold"])
            base_price = STOCKS_DATA[symbol]["currentPrice"]
            variation = (random.random() - 0.5) * 0.05

            signals.append({
                "date": date,
                "signal": sig_type,
                "predictedPrice": round(base_price * (1 + variation), 2),
                "actualPrice": round(base_price * (1 + variation + (random.random() - 0.5) * 0.02), 2),
                "correct": random.random() > 0.3,
            })

        SIGNALS_DATA[symbol] = signals

# ============================================================================
# ENDPOINTS GET
# ============================================================================

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok"})

@app.route("/stocks", methods=["GET"])
def get_stocks():
    """Obtiene lista de todas las acciones con señales actuales"""
    stocks_list = list(STOCKS_DATA.values())
    return jsonify({"success": True, "data": stocks_list})

@app.route("/stocks/<symbol>", methods=["GET"])
def get_stock_detail(symbol):
    """Obtiene detalle de una acción específica"""
    if symbol not in STOCKS_DATA:
        return jsonify({"success": False, "error": f"Stock {symbol} not found"}), 404

    stock = STOCKS_DATA[symbol]
    recent_signals = SIGNALS_DATA.get(symbol, [])

    return jsonify({
        "success": True,
        "data": {
            **stock,
            "recentSignals": recent_signals,
        }
    })

@app.route("/stocks/<symbol>/history", methods=["GET"])
def get_historical_data(symbol):
    """Obtiene histórico de precios para una acción"""
    days = request.args.get("days", 30, type=int)
    key = f"{symbol}:{days}"

    if key not in HISTORICAL_DATA:
        return jsonify({"success": False, "error": f"History for {symbol} not found"}), 404

    return jsonify({"success": True, "data": HISTORICAL_DATA[key]})

@app.route("/stocks/<symbol>/metrics", methods=["GET"])
def get_performance_metrics(symbol):
    """Obtiene métricas de rendimiento de una acción"""
    if symbol not in METRICS_DATA:
        return jsonify({"success": False, "error": f"Metrics for {symbol} not found"}), 404

    return jsonify({"success": True, "data": METRICS_DATA[symbol]})

@app.route("/metrics", methods=["GET"])
def get_all_metrics():
    """Obtiene métricas de rendimiento de todas las acciones"""
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

# ============================================================================
# ENDPOINTS POST
# ============================================================================

@app.route("/stocks", methods=["POST"])
def update_stocks():
    """Actualiza la lista completa de acciones con nuevas señales"""
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
    """Actualiza una acción específica"""
    data = request.get_json()
    STOCKS_DATA[symbol] = data

    return jsonify({
        "success": True,
        "message": f"Updated {symbol}",
        "data": data
    })

@app.route("/stocks/<symbol>/history", methods=["POST"])
def update_historical_data(symbol):
    """Actualiza datos históricos de una acción"""
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
    """Actualiza métricas de rendimiento de una acción"""
    data = request.get_json()
    METRICS_DATA[symbol] = data

    return jsonify({
        "success": True,
        "message": f"Updated metrics for {symbol}",
        "data": data
    })

@app.route("/stocks/<symbol>/signals", methods=["POST"])
def update_signals(symbol):
    """Actualiza historial de señales de una acción"""
    data = request.get_json()
    SIGNALS_DATA[symbol] = data

    return jsonify({
        "success": True,
        "message": f"Updated {len(data)} signals for {symbol}",
        "data": data
    })

# ============================================================================
# INICIO
# ============================================================================

if __name__ == "__main__":
    initialize_dummy_data()
    print("[*] API iniciada en http://localhost:8000")
    print("[*] Flask en modo debug")
    app.run(host="0.0.0.0", port=8000, debug=True)
