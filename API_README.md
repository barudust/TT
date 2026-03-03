# TradingSignals AI - API Documentation

Complete REST API reference for the Flask backend server.

## Base URL

```
http://localhost:8000
```

## Response Format

All endpoints return JSON responses with the following structure:

### Success Response
```json
{
  "success": true,
  "data": {},
  "message": "Optional message"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error description"
}
```

---

## GET Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Description:** Simple health check to verify API is running.

**Response:**
```json
{
  "status": "ok"
}
```

**Example:**
```bash
curl http://localhost:8000/health
```

---

### 2. Get All Stocks

**Endpoint:** `GET /stocks`

**Description:** Returns list of all tracked stocks with current signal information.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "currentPrice": 175.42,
      "signal": "buy",
      "confidence": 0.82,
      "lastUpdate": "2026-03-02T20:45:30.123456Z"
    },
    {
      "symbol": "MSFT",
      "name": "Microsoft Corporation",
      "currentPrice": 410.15,
      "signal": "hold",
      "confidence": 0.71,
      "lastUpdate": "2026-03-02T20:45:30.123456Z"
    }
  ]
}
```

**Fields:**
| Field | Type | Description |
|-------|------|-------------|
| symbol | string | Stock ticker symbol |
| name | string | Company name |
| currentPrice | float | Latest closing price |
| signal | string | Prediction: "buy", "sell", or "hold" |
| confidence | float | Signal confidence (0.0-1.0) |
| lastUpdate | string | ISO 8601 timestamp |

**Example:**
```bash
curl http://localhost:8000/stocks
```

---

### 3. Get Stock Detail

**Endpoint:** `GET /stocks/<symbol>`

**Description:** Detailed information for a specific stock including recent signals.

**Parameters:**
- `symbol` (path, required): Stock ticker (e.g., "AAPL")

**Response:**
```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "currentPrice": 175.42,
    "signal": "buy",
    "confidence": 0.82,
    "lastUpdate": "2026-03-02T20:45:30.123456Z",
    "recentSignals": [
      {
        "date": "2026-03-02",
        "signal": "buy",
        "predictedPrice": 176.50,
        "actualPrice": 175.42,
        "correct": true
      },
      {
        "date": "2026-03-01",
        "signal": "hold",
        "predictedPrice": 175.20,
        "actualPrice": 174.80,
        "correct": true
      }
    ]
  }
}
```

**Error Response (404):**
```json
{
  "success": false,
  "error": "Stock XXXX not found"
}
```

**Example:**
```bash
curl http://localhost:8000/stocks/AAPL
```

---

### 4. Get Historical Price Data

**Endpoint:** `GET /stocks/<symbol>/history`

**Description:** Historical price data and predictions for a stock over specified days.

**Parameters:**
- `symbol` (path, required): Stock ticker
- `days` (query, optional): Number of days (30, 60, or 90). Default: 30

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "date": "2026-02-02",
      "close": 172.15,
      "prediction": "buy",
      "actualDirection": "up"
    },
    {
      "date": "2026-02-03",
      "close": 173.42,
      "prediction": "buy",
      "actualDirection": "up"
    },
    {
      "date": "2026-03-02",
      "close": 175.42,
      "prediction": "buyx",
      "actualDirection": "up"
    }
  ]
}
```

**Fields:**
| Field | Type | Description |
|-------|------|-------------|
| date | string | Date in YYYY-MM-DD format |
| close | float | Closing price for the day |
| prediction | string | Model prediction: "buy", "sell", "hold" |
| actualDirection | string | Price movement: "up", "down", "neutral" |

**Valid days:** 30, 60, 90

**Example:**
```bash
# 30-day history (default)
curl http://localhost:8000/stocks/AAPL/history

# 60-day history
curl http://localhost:8000/stocks/AAPL/history?days=60

# 90-day history
curl http://localhost:8000/stocks/AAPL/history?days=90
```

---

### 5. Get Stock Metrics

**Endpoint:** `GET /stocks/<symbol>/metrics`

**Description:** Performance metrics for a specific stock.

**Parameters:**
- `symbol` (path, required): Stock ticker

**Response:**
```json
{
  "success": true,
  "data": {
    "accuracy": 0.65,
    "buyPrecision": 0.72,
    "sellPrecision": 0.58,
    "holdPrecision": 0.64,
    "f1Score": 0.62,
    "evaluationPeriod": 30,
    "totalPredictions": 30,
    "correctPredictions": 19,
    "cumulativeReturn": 12.45,
    "sharpeRatio": 1.23,
    "winRate": 68.5,
    "profitFactor": 2.15,
    "maxDrawdown": 5.32,
    "numberOfTrades": 13,
    "exposure": 83.33,
    "finalCapital": 1124.50
  }
}
```

**Metrics Explanation:**

**Classification Metrics:**
| Metric | Range | Description |
|--------|-------|-------------|
| accuracy | 0-1 | Overall prediction accuracy |
| buyPrecision | 0-1 | Accuracy of buy signals only |
| sellPrecision | 0-1 | Accuracy of sell signals only |
| holdPrecision | 0-1 | Accuracy of hold signals only |
| f1Score | 0-1 | Harmonic mean of precision and recall |

**Strategy Metrics:**
| Metric | Unit | Description |
|--------|------|-------------|
| cumulativeReturn | % | Total profit/loss from $1000 initial capital |
| sharpeRatio | ratio | Risk-adjusted return (higher is better) |
| winRate | % | Percentage of profitable trades |
| profitFactor | ratio | Gross profit divided by gross loss |
| maxDrawdown | % | Largest peak-to-trough decline |
| numberOfTrades | count | Total trades executed |
| exposure | % | Days with open positions |
| finalCapital | $ | Final portfolio value (simulated) |

**Other:**
| Metric | Type | Description |
|--------|------|-------------|
| evaluationPeriod | days | Number of days analyzed |
| totalPredictions | count | Total predictions made |
| correctPredictions | count | Correct predictions count |

**Example:**
```bash
curl http://localhost:8000/stocks/AAPL/metrics
```

---

### 6. Get All Stocks Metrics

**Endpoint:** `GET /metrics`

**Description:** Aggregated metrics for all 8 tracked stocks.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "accuracy": 0.65,
      "buyPrecision": 0.72,
      "sellPrecision": 0.58,
      "holdPrecision": 0.64,
      "f1Score": 0.62,
      "evaluationPeriod": 30,
      "totalPredictions": 30,
      "correctPredictions": 19,
      "cumulativeReturn": 12.45,
      "sharpeRatio": 1.23,
      "winRate": 68.5,
      "profitFactor": 2.15,
      "maxDrawdown": 5.32,
      "numberOfTrades": 13,
      "exposure": 83.33,
      "finalCapital": 1124.50
    },
    {
      "symbol": "MSFT",
      "name": "Microsoft Corporation",
      "accuracy": 0.58,
      "buyPrecision": 0.65,
      ...
    }
  ]
}
```

**Returns:** Array of metric objects (one per stock) with identical structure to individual stock metrics.

**Example:**
```bash
curl http://localhost:8000/metrics
```

---

## POST Endpoints

### 1. Update All Stocks

**Endpoint:** `POST /stocks`

**Description:** Update signal data for multiple stocks at once.

**Request Body:**
```json
[
  {
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "currentPrice": 176.50,
    "signal": "buy",
    "confidence": 0.85,
    "lastUpdate": "2026-03-02T21:00:00Z"
  },
  {
    "symbol": "MSFT",
    "name": "Microsoft Corporation",
    "currentPrice": 411.20,
    "signal": "sell",
    "confidence": 0.79,
    "lastUpdate": "2026-03-02T21:00:00Z"
  }
]
```

**Response:**
```json
{
  "success": true,
  "message": "Updated 2 stocks",
  "data": [...]
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/stocks \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "currentPrice": 176.50,
    "signal": "buy",
    "confidence": 0.85,
    "lastUpdate": "2026-03-02T21:00:00Z"
  }'
```

---

### 2. Update Single Stock

**Endpoint:** `POST /stocks/<symbol>`

**Description:** Update signal data for a specific stock.

**Parameters:**
- `symbol` (path, required): Stock ticker

**Request Body:**
```json
{
  "symbol": "AAPL",
  "name": "Apple Inc.",
  "currentPrice": 176.50,
  "signal": "buy",
  "confidence": 0.85,
  "lastUpdate": "2026-03-02T21:00:00Z"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Updated AAPL",
  "data": {...}
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/stocks/AAPL \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "currentPrice": 176.50,
    "signal": "buy",
    "confidence": 0.85,
    "lastUpdate": "2026-03-02T21:00:00Z"
  }'
```

---

### 3. Update Historical Data

**Endpoint:** `POST /stocks/<symbol>/history`

**Description:** Update historical price and prediction data for a stock.

**Parameters:**
- `symbol` (path, required): Stock ticker
- `days` (query, optional): Period for this history (30, 60, 90). Default: 30

**Request Body:**
```json
[
  {
    "date": "2026-02-01",
    "close": 171.50,
    "prediction": "hold",
    "actualDirection": "neutral"
  },
  {
    "date": "2026-02-02",
    "close": 172.15,
    "prediction": "buy",
    "actualDirection": "up"
  },
  {
    "date": "2026-03-02",
    "close": 176.50,
    "prediction": "buy",
    "actualDirection": "up"
  }
]
```

**Response:**
```json
{
  "success": true,
  "message": "Updated history for AAPL (30 days)",
  "data": [...]
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/stocks/AAPL/history?days=30" \
  -H "Content-Type: application/json" \
  -d '[...]'
```

---

### 4. Update Stock Metrics

**Endpoint:** `POST /stocks/<symbol>/metrics`

**Description:** Update performance metrics for a stock.

**Parameters:**
- `symbol` (path, required): Stock ticker

**Request Body:**
```json
{
  "accuracy": 0.68,
  "buyPrecision": 0.75,
  "sellPrecision": 0.61,
  "holdPrecision": 0.67,
  "f1Score": 0.65,
  "evaluationPeriod": 30,
  "totalPredictions": 30,
  "correctPredictions": 20,
  "cumulativeReturn": 15.32,
  "sharpeRatio": 1.35,
  "winRate": 70.2,
  "profitFactor": 2.28,
  "maxDrawdown": 4.87,
  "numberOfTrades": 14,
  "exposure": 85.0,
  "finalCapital": 1153.20
}
```

**Response:**
```json
{
  "success": true,
  "message": "Updated metrics for AAPL",
  "data": {...}
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/stocks/AAPL/metrics \
  -H "Content-Type: application/json" \
  -d '{
    "accuracy": 0.68,
    "buyPrecision": 0.75,
    ...
  }'
```

---

### 5. Update Signal History

**Endpoint:** `POST /stocks/<symbol>/signals`

**Description:** Update recent signal history for a stock.

**Parameters:**
- `symbol` (path, required): Stock ticker

**Request Body:**
```json
[
  {
    "date": "2026-02-21",
    "signal": "sell",
    "predictedPrice": 173.20,
    "actualPrice": 172.50,
    "correct": true
  },
  {
    "date": "2026-02-22",
    "signal": "hold",
    "predictedPrice": 172.80,
    "actualPrice": 173.15,
    "correct": true
  },
  {
    "date": "2026-03-02",
    "signal": "buy",
    "predictedPrice": 176.30,
    "actualPrice": 176.50,
    "correct": true
  }
]
```

**Response:**
```json
{
  "success": true,
  "message": "Updated 10 signals for AAPL",
  "data": [...]
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/stocks/AAPL/signals \
  -H "Content-Type: application/json" \
  -d '[...]'
```

---

## Error Handling

### Common Error Responses

**404 - Not Found**
```json
{
  "success": false,
  "error": "Stock XXXX not found"
}
```

**400 - Bad Request**
```json
{
  "success": false,
  "error": "Expected list of stocks"
}
```

---

## Testing Endpoints

### Using cURL

```bash
# Test API health
curl http://localhost:8000/health

# Get all stocks
curl http://localhost:8000/stocks

# Get specific stock
curl http://localhost:8000/stocks/AAPL

# Get 30-day history
curl "http://localhost:8000/stocks/AAPL/history?days=30"

# Get metrics
curl http://localhost:8000/stocks/AAPL/metrics

# Update stock (requires valid JSON)
curl -X POST http://localhost:8000/stocks/AAPL \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","currentPrice":176.50,"signal":"buy"}'
```

### Using Python

```python
import requests
import json

API_URL = "http://localhost:8000"

# Get all stocks
response = requests.get(f"{API_URL}/stocks")
print(response.json())

# Get specific stock
response = requests.get(f"{API_URL}/stocks/AAPL")
print(response.json())

# Update stock
data = {
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "currentPrice": 176.50,
    "signal": "buy",
    "confidence": 0.85,
    "lastUpdate": "2026-03-02T21:00:00Z"
}
response = requests.post(
    f"{API_URL}/stocks/AAPL",
    json=data,
    headers={"Content-Type": "application/json"}
)
print(response.json())
```

---

## Integration Notes

1. **Data Validation:** The API performs minimal validation. Ensure input data is properly formatted.

2. **In-Memory Storage:** All data is stored in memory. Server restart clears all data.

3. **CORS:** CORS is enabled for all origins. Safe for local development.

4. **Timeouts:** No specific timeout configured. Default Flask timeouts apply.

5. **Rate Limiting:** Not implemented. Add if deploying to production.

6. **Authentication:** Not implemented. Add security layer before production use.

---

**API Version:** 1.0.0
**Framework:** Flask 3.0.0
**Updated:** 2026-03-02
