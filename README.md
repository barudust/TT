# TradingSignals AI

Deep learning-based stock market price prediction system. Generates daily buy/sell/hold signals for 8 major stocks using LSTM and CNN-LSTM neural networks.

## Project Overview

TradingSignals AI is an educational platform that combines deep learning models with a modern web interface to predict stock market movements. The system analyzes historical price data to generate trading signals and displays comprehensive performance metrics.

- **Frontend:** React 18 + TypeScript + Tailwind CSS
- **Backend:** Flask REST API with in-memory data storage
- **State Management:** React Router for navigation
- **Charts:** Recharts for data visualization
- **Deep Learning:** LSTM and CNN-LSTM model architectures

## Tracked Stocks

The system monitors 8 major US stocks:
- **AAPL** - Apple Inc.
- **MSFT** - Microsoft Corporation
- **GOOGL** - Alphabet Inc.
- **AMZN** - Amazon.com Inc.
- **TSLA** - Tesla Inc.
- **META** - Meta Platforms Inc.
- **NVDA** - NVIDIA Corporation
- **JPM** - JPMorgan Chase & Co.

## Installation

### Prerequisites

- Node.js 18+ (https://nodejs.org/)
- Python 3.9+ (https://www.python.org/)
- Git (https://git-scm.com/)

### Frontend Setup

```bash
# Navigate to project root
cd TT

# Install Node dependencies
npm install

# Build Tailwind CSS
npm run build
```

### Backend Setup

```bash
# Create virtual environment (optional but recommended)
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install Python dependencies
cd api
pip install -r requirements.txt
```

## Configuration

### Environment Variables

Create a `.env.local` file in the project root (optional):

```
VITE_API_URL=http://localhost:8000
```

If not specified, the app automatically detects:
- Development: `http://localhost:8000`
- Production: `https://yourdomain.com:8000`

## Running the Project

Open **3 separate terminals**:

### Terminal 1: Backend API (Python)

```bash
cd api
python main.py
```

Expected output:
```
[INFO] API server started on http://localhost:8000
[INFO] Flask in debug mode
 * Running on http://0.0.0.0:8000
```

### Terminal 2: Frontend Development Server

```bash
npm run dev
```

Expected output:
```
VITE v5.0.0  ready in 100 ms

➜  Local:   http://localhost:5173/
```

### Terminal 3 (Optional): Data Injection

```bash
cd api
python send_data.py
```

This allows you to send simulated stock data updates programmatically.

## Accessing the Application

Open your browser and navigate to:
```
http://localhost:5173
```

## Project Structure

```
.
├── src/
│   ├── app/
│   │   ├── pages/
│   │   │   ├── Home.tsx          # Stock signals list
│   │   │   ├── StockDetail.tsx   # Detailed metrics and charts
│   │   │   ├── Performance.tsx   # Global performance comparison
│   │   │   └── About.tsx         # Project information
│   │   ├── components/           # Reusable UI components
│   │   ├── config/
│   │   │   └── api.ts            # API configuration
│   │   ├── Root.tsx              # Main layout component
│   │   └── routes.ts             # Route definitions
│   ├── styles/
│   └── main.tsx                  # React entry point
│
├── api/
│   ├── main.py                   # Flask API server
│   ├── send_data.py              # Data injection script
│   ├── requirements.txt           # Python dependencies
│   └── output_examples/           # Expected API response reference
│
├── public/
│   ├── manifest.json             # PWA manifest
│   └── service-worker.js         # Service worker for offline support
│
├── package.json                  # Node dependencies and scripts
├── vite.config.ts                # Vite configuration
├── tailwind.config.ts            # Tailwind CSS configuration
├── tsconfig.json                 # TypeScript configuration
└── README.md                     # This file
```

## API Endpoints

Full API documentation is available in [API_README.md](./API_README.md).

### Quick Reference

- `GET /health` - Health check
- `GET /stocks` - All stocks with current signals
- `GET /stocks/<symbol>` - Detailed data for a specific stock
- `GET /stocks/<symbol>/history?days=30` - Historical price data
- `GET /stocks/<symbol>/metrics` - Performance metrics for one stock
- `GET /metrics` - Aggregated metrics for all stocks

## Technologies

### Frontend Stack
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Recharts** - Data visualization
- **React Router 7** - Navigation
- **Lucide React** - Icons

### Backend Stack
- **Flask** - Web framework
- **Flask-CORS** - Cross-origin support
- **Python 3.9+** - Runtime

### Build & Deployment
- **PWA** - Progressive Web App support
- **Service Worker** - Offline caching
- **CORS** - Cross-origin requests

## Available Commands

```bash
# Development
npm run dev          # Start dev server
npm run build        # Build for production
npm run preview      # Preview production build locally

# Server commands (in api/ directory)
python main.py       # Start Flask server
python send_data.py  # Send test data to API
```

## Model Architecture

The system uses two neural network architectures:

### LSTM (Long Short-Term Memory)
- Handles sequential temporal dependencies
- Single-layer LSTM with 64 units
- Effective for time-series analysis

### CNN-LSTM (Hybrid Architecture)
- CNN layers for feature extraction
- LSTM layers for temporal patterns
- Combines local and temporal feature learning

Note: Current implementation uses simulated data. To integrate real trained models, implement the model prediction logic in the `/api` module.

## Metrics Explained

### Classification Metrics
- **Accuracy** - Percentage of correct direction predictions
- **Precision (BUY/SELL/HOLD)** - Accuracy for each signal type
- **F1-Score** - Harmonic mean of precision and recall

### Strategy Metrics
- **Cumulative Return** - Total simulated profit/loss percentage
- **Sharpe Ratio** - Risk-adjusted returns
- **Win Rate** - Percentage of profitable trades
- **Profit Factor** - Gross profit / Gross loss ratio
- **Max Drawdown** - Largest peak-to-trough decline
- **Exposure** - Percentage of days with open positions

## PWA Installation

The application is configured as a Progressive Web App (PWA):

### On Android
1. Open the app in Chrome browser
2. Tap menu (⋮) → "Install app"
3. App appears on home screen

### On iOS
1. Open Safari browser
2. Tap share → "Add to Home Screen"
3. App runs in fullscreen mode

## Contributing

This is an academic project (ESCOM IPN, 2026). For bug reports or improvements:
1. Create an issue describing the problem
2. Include steps to reproduce
3. Provide expected vs actual behavior

## License

Educational/Research Use Only - 2026

## Disclaimer

This project is for educational purposes. Trading signals generated are simulated and should not be used as financial advice. Always consult qualified financial professionals before making investment decisions.

---

**Developers:** Reyes Ramos David, Polvo Cuatianquiz Jesús Baruc
**Advisors:** Abdiel Reyes Vega, Emmanuel Juarez Carvajal
**Institution:** ESCOM (Escuela Superior de Cómputo) - IPN
