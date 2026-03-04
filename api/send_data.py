"""
Script para enviar datos simulados a la API local
Ejecutar después de que la API esté corriendo: python send_data.py
"""

import requests
import random
from datetime import datetime, timedelta

API_URL = "http://localhost:8000"

STOCKS_CONFIG = [
    {"symbol": "AAPL", "name": "Apple Inc."},
    {"symbol": "MSFT", "name": "Microsoft Corporation"},
    {"symbol": "GOOGL", "name": "Alphabet Inc."},
    {"symbol": "AMZN", "name": "Amazon.com Inc."},
    {"symbol": "TSLA", "name": "Tesla Inc."},
    {"symbol": "META", "name": "Meta Platforms Inc."},
    {"symbol": "NVDA", "name": "NVIDIA Corporation"},
]

BASE_PRICES = {
    "AAPL": 175.00,
    "MSFT": 410.00,
    "GOOGL": 140.00,
    "AMZN": 175.00,
    "TSLA": 195.00,
    "META": 485.00,
    "NVDA": 875.00,
}

def generate_stock_data(symbol: str) -> dict:
    """Genera datos simulados para una acción"""
    base_price = BASE_PRICES.get(symbol, 100)
    current_price = base_price * (1 + (random.random() - 0.5) * 0.05)
    signal = random.choice(["buy", "sell", "hold"])
    confidence = round(0.6 + random.random() * 0.3, 2)

    return {
        "symbol": symbol,
        "name": next(s["name"] for s in STOCKS_CONFIG if s["symbol"] == symbol),
        "currentPrice": round(current_price, 2),
        "signal": signal,
        "confidence": confidence,
        "lastUpdate": datetime.utcnow().isoformat() + "Z",
    }

def send_all_stocks():
    """Envía datos de todas las acciones a la API"""
    print("📤 Enviando datos de todas las acciones...")

    stocks = [generate_stock_data(s["symbol"]) for s in STOCKS_CONFIG]

    try:
        response = requests.post(f"{API_URL}/stocks", json=stocks)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Éxito: {result['message']}")
            print(f"   Acciones actualizadas:")
            for stock in stocks:
                print(f"   - {stock['symbol']}: ${stock['currentPrice']} ({stock['signal'].upper()})")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print(f"   Asegúrate de que la API está corriendo en {API_URL}")

def send_single_stock(symbol: str):
    """Envía datos de una acción individual"""
    print(f"📤 Enviando datos para {symbol}...")

    stock = generate_stock_data(symbol)

    try:
        response = requests.post(f"{API_URL}/stocks/{symbol}", json=stock)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Éxito: {result['message']}")
            print(f"   {symbol}: ${stock['currentPrice']} ({stock['signal'].upper()})")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def send_multiple_stocks(symbols: list):
    """Envía datos para múltiples acciones específicas"""
    print(f"📤 Enviando datos para {len(symbols)} acciones...")

    stocks = [generate_stock_data(sym) for sym in symbols if sym in [s["symbol"] for s in STOCKS_CONFIG]]

    try:
        response = requests.post(f"{API_URL}/stocks", json=stocks)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Éxito: {result['message']}")
            for stock in stocks:
                print(f"   - {stock['symbol']}: ${stock['currentPrice']} ({stock['signal'].upper()})")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🤖 TradingSignals AI - Generador de Datos Simulados")
    print("="*60)

    print("\nOpciones:")
    print("1. Enviar datos de TODAS las acciones")
    print("2. Enviar datos de una acción específica")
    print("3. Enviar datos de múltiples acciones")

    choice = input("\nElige una opción (1-3): ").strip()

    if choice == "1":
        send_all_stocks()

    elif choice == "2":
        print(f"\nAcciones disponibles: {', '.join([s['symbol'] for s in STOCKS_CONFIG])}")
        symbol = input("Ingresa el símbolo: ").upper().strip()
        if symbol in [s["symbol"] for s in STOCKS_CONFIG]:
            send_single_stock(symbol)
        else:
            print(f"❌ Símbolo '{symbol}' no válido")

    elif choice == "3":
        print(f"\nAcciones disponibles: {', '.join([s['symbol'] for s in STOCKS_CONFIG])}")
        symbols = input("Ingresa los símbolos separados por comas (ej: AAPL,MSFT,GOOGL): ").upper().split(",")
        symbols = [s.strip() for s in symbols]
        send_multiple_stocks(symbols)

    else:
        print("❌ Opción no válida")

    print("\n" + "="*60 + "\n")
