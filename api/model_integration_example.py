"""
EJEMPLO: Cómo integrar tus modelos de Deep Learning con la API local

Este archivo muestra cómo:
1. Entrenar/usar tus modelos
2. Enviar predicciones a la API
3. La app React las visualiza automáticamente
"""

import requests
from datetime import datetime

API_URL = "http://localhost:8000"

# ============================================================================
# EJEMPLO 1: Actualizar predicciones de una sola acción
# ============================================================================

def actualizar_prediccion_aapl():
    """
    Simula la salida de tu modelo LSTM/CNN-LSTM para AAPL

    En producción, aquí irían tus modelos:
    - Cargar el modelo entrenado
    - Hacer predicción
    - Enviar a la API
    """

    # Simular salida del modelo
    # En producción, reemplaza esto con tu modelo:
    # prediction = modelo.predict(datos_historicos)

    stock_data = {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "currentPrice": 175.50,  # El precio actual de tu fuente (Yahoo Finance, etc)
        "signal": "buy",  # Salida del modelo: "buy", "sell", "hold"
        "confidence": 0.82,  # Confianza del modelo (0-1)
        "lastUpdate": datetime.utcnow().isoformat() + "Z"
    }

    # Enviar a la API
    response = requests.post(
        f"{API_URL}/stocks/AAPL",
        json=stock_data
    )

    if response.status_code == 200:
        print(f"✅ AAPL actualizado: {stock_data['signal'].upper()} ({stock_data['confidence']*100:.0f}%)")
    else:
        print(f"❌ Error: {response.status_code}")


# ============================================================================
# EJEMPLO 2: Actualizar predicciones de TODAS las acciones
# ============================================================================

def actualizar_todas_predicciones():
    """
    Actualiza las 8 acciones con predicciones de tus modelos
    """

    STOCKS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM"]
    NOMBRES = {
        "AAPL": "Apple Inc.",
        "MSFT": "Microsoft Corporation",
        "GOOGL": "Alphabet Inc.",
        "AMZN": "Amazon.com Inc.",
        "TSLA": "Tesla Inc.",
        "META": "Meta Platforms Inc.",
        "NVDA": "NVIDIA Corporation",
        "JPM": "JPMorgan Chase & Co.",
    }

    stocks_data = []

    for symbol in STOCKS:
        # AQUÍ IRÍA TU CÓDIGO DE MODELO:
        # prediction = modelo.predict(datos_historicos[symbol])
        # confidence = modelo.get_confidence(datos_historicos[symbol])

        # Por ahora, simular predicciones
        import random
        signal = random.choice(["buy", "sell", "hold"])
        confidence = round(0.6 + random.random() * 0.3, 2)

        stock_data = {
            "symbol": symbol,
            "name": NOMBRES[symbol],
            "currentPrice": 100.0 + random.random() * 100,  # Reemplazar con precio real
            "signal": signal,
            "confidence": confidence,
            "lastUpdate": datetime.utcnow().isoformat() + "Z"
        }
        stocks_data.append(stock_data)

    # Enviar todas
    response = requests.post(
        f"{API_URL}/stocks",
        json=stocks_data
    )

    if response.status_code == 200:
        print(f"✅ Actualizadas {len(stocks_data)} acciones")
        for stock in stocks_data:
            print(f"   {stock['symbol']}: {stock['signal'].upper()} ({stock['confidence']*100:.0f}%)")
    else:
        print(f"❌ Error: {response.status_code}")


# ============================================================================
# EJEMPLO 3: Estructura completa con datos históricos y métricas
# ============================================================================

def actualizar_con_historico_y_metricas(symbol: str):
    """
    Actualiza una acción con:
    - Predicción actual
    - Datos históricos (30, 60, 90 días)
    - Métricas de rendimiento del modelo
    """

    # PASO 1: Actualizar predicción actual
    stock_data = {
        "symbol": symbol,
        "name": f"Stock {symbol}",
        "currentPrice": 150.00,
        "signal": "buy",
        "confidence": 0.78,
        "lastUpdate": datetime.utcnow().isoformat() + "Z"
    }

    response1 = requests.post(f"{API_URL}/stocks/{symbol}", json=stock_data)
    print(f"1️⃣  Predicción actualizada: {response1.status_code}")

    # PASO 2: Actualizar datos históricos
    historical_data = [
        {"date": "2026-02-26", "close": 145.00, "prediction": "sell", "actualDirection": "down"},
        {"date": "2026-02-27", "close": 148.50, "prediction": "hold", "actualDirection": "neutral"},
        {"date": "2026-02-28", "close": 152.00, "prediction": "buy", "actualDirection": "up"},
        {"date": "2026-03-01", "close": 151.50, "prediction": "buy", "actualDirection": "neutral"},
        {"date": "2026-03-02", "close": 150.00, "prediction": "buy", "actualDirection": "down"},
    ]

    response2 = requests.post(
        f"{API_URL}/stocks/{symbol}/history?days=30",
        json=historical_data
    )
    print(f"2️⃣  Histórico actualizado: {response2.status_code}")

    # PASO 3: Actualizar métricas del modelo
    metrics = {
        "accuracy": 0.72,
        "buyPrecision": 0.68,
        "sellPrecision": 0.75,
        "holdPrecision": 0.70,
        "f1Score": 0.71,
        "evaluationPeriod": 30,
        "totalPredictions": 150,
        "correctPredictions": 108
    }

    response3 = requests.post(f"{API_URL}/stocks/{symbol}/metrics", json=metrics)
    print(f"3️⃣  Métricas actualizadas: {response3.status_code}")

    print(f"\n✅ {symbol} completamente sincronizado")


# ============================================================================
# EJEMPLO 4: Ciclo diario para reentrenamiento (SCHEDULER)
# ============================================================================

def ciclo_diario_predicciones():
    """
    Función que se ejecutaría cada día al cierre del mercado.

    Con APScheduler (instalar con: pip install APScheduler):

    from apscheduler.schedulers.background import BackgroundScheduler

    scheduler = BackgroundScheduler()
    scheduler.add_job(ciclo_diario_predicciones, 'cron', hour=17)  # 5 PM
    scheduler.start()
    """

    print("⏰ Ejecutando ciclo diario de predicciones...")

    # 1. Obtener datos históricos (Yahoo Finance, API, etc)
    # datos = obtener_datos_mercado()

    # 2. Entrenar/actualizar modelos
    # modelos = entrenar_modelos(datos)

    # 3. Hacer predicciones para mañana
    # predicciones = modelos.predict(datos)

    # 4. Enviar a la API
    actualizar_todas_predicciones()

    print("✅ Ciclo de predicciones completado")


# ============================================================================
# USO
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("📊 Ejemplos de Integración de Modelos")
    print("="*60)

    print("\n1. Actualizar AAPL sola:")
    actualizar_prediccion_aapl()

    print("\n2. Actualizar TODAS las acciones:")
    actualizar_todas_predicciones()

    print("\n3. Actualizar con histórico y métricas:")
    actualizar_con_historico_y_metricas("AAPL")

    print("\n" + "="*60)
    print("✅ Todos los ejemplos completados")
    print("="*60)
    print("\nPróximos pasos:")
    print("- Integrar tus modelos LSTM/CNN-LSTM")
    print("- Conectar a APIs de precios reales (Yahoo Finance)")
    print("- Configurar scheduler para actualizaciones diarias")
