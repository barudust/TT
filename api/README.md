# API Local - TradingSignals AI

Esta es la **API local con Flask** que reemplaza a Supabase. Contiene todos los endpoints para manejar predicciones de trading.

---

## 📁 Archivos

| Archivo | Descripción |
|---------|------------|
| `main.py` | API completa con Flask |
| `requirements.txt` | Dependencias de Python (Flask + Flask-CORS) |
| `send_data.py` | Script para enviar datos simulados |
| `model_integration_example.py` | Ejemplo de cómo integrar tus modelos |

---

## 🚀 Ejecutar la API

```bash
python main.py
```

O si tienes Python 3 explícitamente instalado:

```bash
python3 main.py
```

La API estará disponible en: **http://localhost:8000**

---

## 📤 Enviar Datos

```bash
python send_data.py
```

Elige una opción para actualizar predicciones.

---

## 🔗 Endpoints Disponibles

### Leer datos (GET)

```
GET /health                             # Health check
GET /stocks                             # Todas las acciones
GET /stocks/{symbol}                    # Una acción
GET /stocks/{symbol}/history?days=30    # Histórico de precios
GET /stocks/{symbol}/metrics            # Métricas de rendimiento
GET /metrics                            # Métricas de todas
```

### Enviar datos (POST)

```
POST /stocks                             # Actualizar todas
POST /stocks/{symbol}                    # Actualizar una
POST /stocks/{symbol}/history            # Actualizar histórico
POST /stocks/{symbol}/metrics            # Actualizar métricas
POST /stocks/{symbol}/signals            # Actualizar señales
```

---

## 💡 Integración de Modelos

Ver: `model_integration_example.py`

Pasos básicos:

1. Cargar datos históricos
2. Hacer predicción con tu modelo
3. Enviar con `POST /stocks/{symbol}`
4. La app React lo visualiza automáticamente

---

## 📊 Estructura de Datos

### Stock Actual

```json
{
  "symbol": "AAPL",
  "name": "Apple Inc.",
  "currentPrice": 175.30,
  "signal": "buy",          // "buy", "sell", "hold"
  "confidence": 0.78,       // 0-1
  "lastUpdate": "2026-03-02T18:00:00Z"
}
```

### Datos Históricos

```json
{
  "date": "2026-03-02",
  "close": 175.30,
  "prediction": "buy",
  "actualDirection": "up"
}
```

### Métricas

```json
{
  "accuracy": 0.72,
  "buyPrecision": 0.68,
  "sellPrecision": 0.75,
  "f1Score": 0.71,
  "evaluationPeriod": 30,
  "totalPredictions": 150,
  "correctPredictions": 108
}
```

---

## 🔧 Modificar la API

Para cambiar puertos, datos iniciales, o agregar endpoints:

Edita `main.py` y busca:
- Línea 319: `port=8000` ← cambiar puerto
- Línea 125: `initialize_dummy_data()` ← cambiar datos iniciales

---

## 🛠️ Tecnologías

- **Flask** - Microframework web ligero
- **Flask-CORS** - Soporte para CORS
- **Python 3.8+** - Lenguaje

¡Listo!
