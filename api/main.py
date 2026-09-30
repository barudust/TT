import os
import threading
import time
from datetime import datetime, date, time as dtime, timezone
from functools import wraps
from zoneinfo import ZoneInfo

import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sklearn.metrics import f1_score
import yfinance as yf

import database
import db_ops
from ml.features import fetch_ohlcv, fetch_market_context, build_feature_frame
from ml.model import load_model, MODEL_VERSION
from ml.target import (etiquetas_reales, HORIZONTE_DIAS, PERCENTIL_BUY,
                       PERCENTIL_SELL, VENTANA_PERCENTIL)

load_dotenv()

app = Flask(__name__)
CORS(app)

# NYSE cierra 16:00 hora de Nueva York; se espera 30 min para que Yahoo
# Finance termine de publicar los datos EOD. ZoneInfo maneja el cambio a
# horario de verano automaticamente (requiere el paquete `tzdata` en Windows).
NYSE_TZ = ZoneInfo("America/New_York")
REFRESH_HOUR = int(os.getenv("REFRESH_HOUR", "16"))
REFRESH_MINUTE = int(os.getenv("REFRESH_MINUTE", "30"))

# Horario regular y feriados oficiales de NYSE (fuente: calendario publicado por
# NYSE). Solo se usa para indicar en la interfaz si el mercado esta abierto; las
# señales no dependen de esto (se calculan con el cierre del ultimo dia habil).
NYSE_OPEN = dtime(9, 30)
NYSE_CLOSE = dtime(16, 0)
NYSE_HOLIDAYS = {
    date(2026, 1, 1), date(2026, 1, 19), date(2026, 2, 16), date(2026, 4, 3),
    date(2026, 5, 25), date(2026, 6, 19), date(2026, 7, 3), date(2026, 9, 7),
    date(2026, 11, 26), date(2026, 12, 25),
    date(2027, 1, 1), date(2027, 1, 18), date(2027, 2, 15), date(2027, 3, 26),
    date(2027, 5, 31), date(2027, 6, 18), date(2027, 7, 5), date(2027, 9, 6),
    date(2027, 11, 25), date(2027, 12, 24),
}

# Los endpoints POST de "override manual" permiten escribir señales/metricas que
# NO salen del modelo. Estan desactivados salvo que se pida explicitamente
# (p.ej. para pruebas locales), para que todo lo que muestra la plataforma
# provenga del modelo y de datos reales.
MANUAL_OVERRIDES_ENABLED = os.getenv("ENABLE_MANUAL_OVERRIDES", "0") == "1"

WINDOWS = (30, 60, 90)
SIGNALS = ("buy", "hold", "sell")
# Con muy pocos dias con posicion, Sharpe y profit factor no son interpretables
# (p.ej. 1 sola operacion en 29 dias da Sharpe = sqrt(252/28) = 3.0 siempre).
MIN_DIAS_CON_POSICION = 5

STOCKS_DATA = {}
HISTORICAL_DATA = {}
SIGNALS_DATA = {}
METRICS_DATA = {}   # {symbol: {30: {...}, 60: {...}, 90: {...}}}
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

# Reintentos para fallas transitorias de red/Yahoo Finance, sobre todo en el
# arranque en frio (el plan free de Render duerme la API y yfinance a veces
# falla la primera llamada tras despertar).
FETCH_RETRY_ATTEMPTS = int(os.getenv("FETCH_RETRY_ATTEMPTS", "3"))
FETCH_RETRY_DELAY_SECONDS = int(os.getenv("FETCH_RETRY_DELAY_SECONDS", "5"))

# Si tras un refresco faltan acciones (tipicamente: Yahoo falla justo en el
# arranque en frio de Render), el scheduler vuelve a intentar cada N minutos
# hasta completar el catalogo, sin esperar a que alguien pulse "Actualizar".
CATALOG_RETRY_MINUTES = int(os.getenv("CATALOG_RETRY_MINUTES", "2"))

# Evita dos recalculos simultaneos (arranque, /admin/refresh, scheduler).
_INIT_LOCK = threading.Lock()


def _with_retries(fn, *, label):
    last_exc = None
    for attempt in range(1, FETCH_RETRY_ATTEMPTS + 1):
        try:
            return fn()
        except Exception as e:
            last_exc = e
            if attempt < FETCH_RETRY_ATTEMPTS:
                print(f"[WARN] {label}: intento {attempt}/{FETCH_RETRY_ATTEMPTS} fallo ({e}). "
                      f"Reintentando en {FETCH_RETRY_DELAY_SECONDS}s...")
                time.sleep(FETCH_RETRY_DELAY_SECONDS)
    raise last_exc


def _utc_now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sin_vela_en_curso(df, now=None):
    """
    Mientras NYSE esta abierto, Yahoo Finance devuelve la vela del dia en curso
    con el precio intradia como "Close". El modelo se entreno con cierres
    diarios, asi que esa fila se descarta hasta que el mercado cierre; si no,
    la señal "del dia" saldria de un precio que todavia no es el cierre.
    """
    if df is None or df.empty:
        return df
    now_ny = (now or datetime.now(timezone.utc)).astimezone(NYSE_TZ)
    if df.index[-1].date() == now_ny.date() and now_ny.time() < NYSE_CLOSE:
        return df.iloc[:-1]
    return df


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


def rows_from_predictions(feat_df, predictions, reales=None):
    """
    Combina OHLCV real + predicciones del modelo + lo que realmente paso al dia
    siguiente, en la forma que consume el frontend (ver docs/API.md).

    La señal del dia t se calcula con el cierre de t y apuesta por el
    movimiento t -> t+1, asi que se evalua contra la etiqueta real de ESE
    movimiento, con la misma definicion que en entrenamiento (percentiles
    30/70 rodantes, ver ml/target.py). El ultimo dia todavia no tiene cierre
    siguiente: actualSignal, nextReturn y correct quedan en None (pendiente).

    `reales` es la salida de etiquetas_reales() sobre el historial completo de
    cierres; si no se pasa, se calcula con los cierres de `feat_df`.
    """
    if reales is None:
        reales = etiquetas_reales(feat_df["raw_close"])
    reales = reales.reindex(feat_df.index)

    rows = []
    for i, (idx_date, pred) in enumerate(zip(feat_df.index, predictions)):
        real = reales["real"].iloc[i]
        r_fwd = reales["r_forward"].iloc[i]
        known = isinstance(real, str) and not np.isnan(r_fwd)

        rows.append({
            "date": idx_date.strftime("%Y-%m-%d"),
            "open": round(float(feat_df["raw_open"].iloc[i]), 2),
            "close": round(float(feat_df["raw_close"].iloc[i]), 2),
            "high": round(float(feat_df["raw_high"].iloc[i]), 2),
            "low": round(float(feat_df["raw_low"].iloc[i]), 2),
            "volume": int(feat_df["raw_volume"].iloc[i]),
            "prediction": pred["signal"],
            "confidence": round(pred["confidence"], 4),
            "probabilities": {k: round(float(v), 4) for k, v in pred.get("probabilities", {}).items()},
            "actualSignal": real if known else None,
            # retorno simple del cierre t al cierre t+1, en %
            "nextReturn": round(float(np.expm1(r_fwd)) * 100, 4) if known else None,
            "correct": (pred["signal"] == real) if known else None,
        })

    return rows


def build_recent_signals(rows, limit=10):
    """Ultimas `limit` señales (la mas reciente primero) con su resultado real."""
    return [{
        "date": r["date"],
        "signal": r["prediction"],
        "confidence": r["confidence"],
        "actualPrice": r["close"],
        "actualSignal": r["actualSignal"],
        "nextReturn": r["nextReturn"],
        "correct": r["correct"],
    } for r in reversed(rows[-limit:])]


def generate_metrics(rows):
    """
    Metricas de la ventana, con la metodologia de la tesis:

    - Clasificacion: F1-macro y F1 por clase contra la etiqueta real
      (percentiles 30/70), solo sobre dias cuyo resultado ya se conoce.
    - Estrategia: cada dia BUY = +r, SELL = -r, HOLD = 0, con
      r = ln(C_{t+1}/C_t) (posicion abierta al cierre de t y cerrada al cierre
      de t+1, sin costos). Sharpe, drawdown, win rate y profit factor son de
      ESA estrategia; buy & hold se reporta aparte como referencia.
    """
    if not rows:
        return {}

    total = len(rows)
    preds_all = [r["prediction"] for r in rows]
    metrics = {
        "periodStart": rows[0]["date"],
        "periodEnd": rows[-1]["date"],
        "totalPredictions": total,
        "avgConfidence": round(float(np.mean([r["confidence"] for r in rows])), 4),
        **{f"signal_{s}_pct": round(preds_all.count(s) / total * 100, 2) for s in SIGNALS},
    }

    ev = [r for r in rows if r.get("actualSignal") is not None and r.get("nextReturn") is not None]
    metrics["evaluatedPredictions"] = len(ev)
    metrics["pendingPredictions"] = total - len(ev)
    if not ev:
        return metrics

    y_true = [r["actualSignal"] for r in ev]
    y_pred = [r["prediction"] for r in ev]
    correct = sum(t == p for t, p in zip(y_true, y_pred))
    f1_por_clase = f1_score(y_true, y_pred, labels=list(SIGNALS), average=None, zero_division=0)

    r = np.log1p(np.array([row["nextReturn"] for row in ev]) / 100)
    pos = np.array([1 if p == "buy" else -1 if p == "sell" else 0 for p in y_pred])
    strat = pos * r

    def _sharpe(x):
        sd = x.std()
        return float(np.sqrt(252) * x.mean() / sd) if sd > 0 else 0.0

    equity = np.exp(np.concatenate([[0.0], np.cumsum(strat)]))
    peak = np.maximum.accumulate(equity)
    max_dd = float(((peak - equity) / peak).max()) * 100

    traded = strat[pos != 0]
    gains = traded[traded > 0].sum()
    losses = abs(traded[traded < 0].sum())
    suficientes = len(traded) >= MIN_DIAS_CON_POSICION
    cum = float(np.expm1(strat.sum())) * 100
    bh = float(np.expm1(r.sum())) * 100

    metrics.update({
        "correctPredictions": int(correct),
        "accuracy": round(correct / len(ev), 4),
        "f1_macro": round(float(np.mean(f1_por_clase)), 4),
        **{f"f1_{s}": round(float(v), 4) for s, v in zip(SIGNALS, f1_por_clase)},
        "cumulativeReturn": round(cum, 2),
        "bh_return": round(bh, 2),
        "return_vs_bh": round(cum - bh, 2),
        "sharpeRatio": round(_sharpe(strat), 2) if suficientes else None,
        "bh_sharpe": round(_sharpe(r), 2),
        "maxDrawdown": round(max_dd, 2),
        "winRate": round(float((traded > 0).mean()) * 100, 2) if len(traded) else None,
        "profitFactor": round(float(gains / losses), 2) if suficientes and losses > 0 else None,
        "numberOfTrades": int(len(traded)),
        "exposure": round(float((pos != 0).mean()) * 100, 2),
        "finalCapital": round(1000.0 * (1 + cum / 100), 2),
    })
    return metrics


def market_status(now=None):
    now_ny = (now or datetime.now(timezone.utc)).astimezone(NYSE_TZ)
    trading_day = now_ny.weekday() < 5 and now_ny.date() not in NYSE_HOLIDAYS
    is_open = trading_day and NYSE_OPEN <= now_ny.time() < NYSE_CLOSE
    return {
        "isOpen": is_open,
        "isTradingDay": trading_day,
        "nowNewYork": now_ny.isoformat(),
        "regularHours": "09:30-16:00 America/New_York",
        "dailyRefresh": f"{REFRESH_HOUR:02d}:{REFRESH_MINUTE:02d} America/New_York (L-V)",
    }


def persist_to_db(session, symbol, name, company_info, rows, metrics_by_window):
    asset = db_ops.get_or_create_asset(session, symbol, name)
    asset.sector = company_info.get("sector")
    asset.industry = company_info.get("industry")

    for row in rows:
        d = db_ops.parse_date(row["date"])
        db_ops.upsert_ohlcv(
            session, asset.id, d,
            open=row["open"], high=row["high"], low=row["low"],
            close=row["close"], volume=row["volume"],
        )
        probs = row.get("probabilities", {})
        db_ops.upsert_prediction(
            session, asset.id, d, row["prediction"], model_version=MODEL_VERSION,
            prob_buy=probs.get("buy"), prob_hold=probs.get("hold"), prob_sell=probs.get("sell"),
            confidence=row["confidence"], actual_price=row["close"],
            correct=None if row["correct"] is None else int(row["correct"]),
        )

    for window_days, m in metrics_by_window.items():
        if not m:
            continue
        db_ops.upsert_metric_from_payload(session, asset.id, window_days, m, model_version=MODEL_VERSION)

    session.commit()


def initialize_data():
    with _INIT_LOCK:
        _initialize_data()


def completar_catalogo_si_falta():
    """Reintenta la carga si el catalogo quedo incompleto; si ya hay otro
    recalculo en curso, no hace nada."""
    if len(STOCKS_DATA) >= len(STOCKS_CONFIG):
        return
    if not _INIT_LOCK.acquire(blocking=False):
        return
    try:
        print(f"[RETRY] Catalogo incompleto ({len(STOCKS_DATA)}/{len(STOCKS_CONFIG)}). Reintentando carga...")
        _initialize_data()
    finally:
        _INIT_LOCK.release()


def _initialize_data():
    database.init_db()
    model = load_model()
    session = database.get_session()

    print("[INFO] Descargando contexto de mercado (SPY, VIX)...")
    try:
        market = _with_retries(
            lambda: sin_vela_en_curso(fetch_market_context(FEATURE_LOOKBACK_PERIOD)),
            label="contexto de mercado",
        )
    except Exception as e:
        print(f"[ERROR] No se pudo descargar contexto de mercado tras {FETCH_RETRY_ATTEMPTS} intentos: {e}")
        market = None

    for stock_config in STOCKS_CONFIG:
        symbol = stock_config["symbol"]
        print(f"[INFO] Procesando {symbol}...")

        if market is None:
            print(f"[WARN] {symbol}: se omite (sin contexto de mercado).")
            continue

        def _fetch_and_predict(symbol=symbol):
            ohlcv = sin_vela_en_curso(fetch_ohlcv(symbol, FEATURE_LOOKBACK_PERIOD))
            feat = build_feature_frame(ohlcv, market)
            if feat.empty:
                raise ValueError("historial insuficiente tras calcular indicadores")
            return ohlcv, feat, model.predict_frame(feat)

        try:
            ohlcv, feat, predictions = _with_retries(_fetch_and_predict, label=symbol)
        except Exception as e:
            print(f"[WARN] {symbol}: fallo al calcular señales reales tras {FETCH_RETRY_ATTEMPTS} intentos ({e}). Se omite.")
            continue

        # Etiquetas reales sobre el historial completo de cierres (no solo las
        # filas que sobreviven al warmup de indicadores) para que los umbrales
        # rodantes de 252 dias esten completos, igual que en entrenamiento.
        rows = rows_from_predictions(feat, predictions, etiquetas_reales(ohlcv["Close"]))

        for days in WINDOWS:
            HISTORICAL_DATA[f"{symbol}:{days}"] = rows[-days:]

        last_row = rows[-1]

        STOCKS_DATA[symbol] = {
            "symbol": symbol,
            "name": stock_config["name"],
            "currentPrice": last_row["close"],
            "signal": last_row["prediction"],
            "confidence": last_row["confidence"],
            "probabilities": last_row["probabilities"],
            "dataDate": last_row["date"],
            "lastUpdate": _utc_now_iso(),
            "modelVersion": MODEL_VERSION,
        }

        metrics_by_window = {days: generate_metrics(rows[-days:]) for days in WINDOWS}
        METRICS_DATA[symbol] = metrics_by_window

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


def _window_arg():
    days = request.args.get("days", 30, type=int)
    return days if days in WINDOWS else None


@app.route("/health", methods=["GET"])
def health_check():
    # Siempre 200 (Render solo necesita saber que el proceso responde); el
    # conteo permite ver desde fuera si la carga de datos ya se completo.
    return jsonify({"status": "ok", "stocksLoaded": len(STOCKS_DATA), "stocksExpected": len(STOCKS_CONFIG)})


@app.route("/model", methods=["GET"])
def get_model_info():
    """Describe el modelo cargado (leido del .pkl) y la definicion de la etiqueta."""
    info = load_model().describe()
    info["target"] = {
        "horizonDays": HORIZONTE_DIAS,
        "percentileSell": PERCENTIL_SELL,
        "percentileBuy": PERCENTIL_BUY,
        "rollingWindowDays": VENTANA_PERCENTIL,
    }
    info["strategy"] = "global (un solo modelo para los 7 tickers)"
    info["tickers"] = [c["symbol"] for c in STOCKS_CONFIG]
    return jsonify({"success": True, "data": info})


@app.route("/market-status", methods=["GET"])
def get_market_status():
    return jsonify({"success": True, "data": market_status()})


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
    days = _window_arg()
    metrics = METRICS_DATA.get(symbol, {}).get(days)
    if not metrics:
        return jsonify({"success": False, "error": f"Metrics for {symbol} ({days} days) not found"}), 404

    return jsonify({"success": True, "data": {**metrics, "windowDays": days}})


@app.route("/metrics", methods=["GET"])
def get_all_metrics():
    days = _window_arg()
    all_metrics = []

    for symbol, stock in STOCKS_DATA.items():
        metrics = METRICS_DATA.get(symbol, {}).get(days)
        if metrics:
            all_metrics.append({
                "symbol": symbol,
                "name": stock["name"],
                "windowDays": days,
                **metrics,
            })

    return jsonify({"success": True, "data": all_metrics})


@app.route("/stocks/<symbol>/info", methods=["GET"])
def get_company_info(symbol):
    if symbol not in COMPANY_INFO:
        return jsonify({"success": False, "error": f"Info for {symbol} not found"}), 404

    return jsonify({"success": True, "data": COMPANY_INFO[symbol]})


def manual_override(fn):
    """Bloquea los endpoints de override salvo con ENABLE_MANUAL_OVERRIDES=1."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not MANUAL_OVERRIDES_ENABLED:
            return jsonify({
                "success": False,
                "error": "Overrides manuales desactivados: todos los datos provienen del modelo "
                         "(ENABLE_MANUAL_OVERRIDES=1 para habilitarlos en pruebas locales).",
            }), 403
        return fn(*args, **kwargs)
    return wrapper


def _persist_stock_override(session, stock):
    """Best-effort: upsert Asset + la Prediction/OHLCV de hoy a partir de un
    override manual parcial (ver POST /stocks). No falla el request si algo
    falta; estos endpoints son para pruebas/demos, no la ruta caliente."""
    symbol = stock.get("symbol")
    if not symbol:
        return
    asset = db_ops.get_or_create_asset(session, symbol, stock.get("name"))
    today = date.today()
    if stock.get("currentPrice") is not None:
        db_ops.upsert_ohlcv(session, asset.id, today, close=stock["currentPrice"])
    if stock.get("signal"):
        db_ops.upsert_prediction(
            session, asset.id, today, stock["signal"], model_version="manual-override",
            confidence=stock.get("confidence"),
        )


@app.route("/stocks", methods=["POST"])
@manual_override
def update_stocks():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({"success": False, "error": "Expected list of stocks"}), 400

    session = database.get_session()
    try:
        for stock in data:
            if "symbol" in stock:
                STOCKS_DATA[stock["symbol"]] = stock
                try:
                    _persist_stock_override(session, stock)
                except Exception as e:
                    print(f"[WARN] No se pudo persistir override de {stock.get('symbol')}: {e}")
        session.commit()
    finally:
        session.close()

    return jsonify({
        "success": True,
        "message": f"Updated {len(data)} stocks",
        "data": data
    })


@app.route("/stocks/<symbol>", methods=["POST"])
@manual_override
def update_stock(symbol):
    data = request.get_json()
    STOCKS_DATA[symbol] = data

    session = database.get_session()
    try:
        _persist_stock_override(session, {**data, "symbol": symbol})
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"[WARN] No se pudo persistir override de {symbol}: {e}")
    finally:
        session.close()

    return jsonify({
        "success": True,
        "message": f"Updated {symbol}",
        "data": data
    })


@app.route("/stocks/<symbol>/history", methods=["POST"])
@manual_override
def update_historical_data(symbol):
    data = request.get_json()
    days = request.args.get("days", 30, type=int)
    key = f"{symbol}:{days}"
    HISTORICAL_DATA[key] = data

    if isinstance(data, list):
        session = database.get_session()
        try:
            asset = db_ops.get_or_create_asset(session, symbol)
            for row in data:
                if not row.get("date"):
                    continue
                d = db_ops.parse_date(row["date"])
                if any(row.get(k) is not None for k in ("open", "high", "low", "close", "volume")):
                    db_ops.upsert_ohlcv(
                        session, asset.id, d,
                        open=row.get("open"), high=row.get("high"), low=row.get("low"),
                        close=row.get("close"), volume=row.get("volume"),
                    )
                if row.get("prediction"):
                    correct = row.get("correct")
                    db_ops.upsert_prediction(
                        session, asset.id, d, row["prediction"], model_version="manual-override",
                        confidence=row.get("confidence"), actual_price=row.get("close"),
                        correct=int(correct) if correct is not None else None,
                    )
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"[WARN] No se pudo persistir historial override de {symbol}: {e}")
        finally:
            session.close()

    return jsonify({
        "success": True,
        "message": f"Updated history for {symbol} ({days} days)",
        "data": data
    })


@app.route("/stocks/<symbol>/metrics", methods=["POST"])
@manual_override
def update_metrics(symbol):
    data = request.get_json()
    days = _window_arg() or 30
    METRICS_DATA.setdefault(symbol, {})[days] = data

    session = database.get_session()
    try:
        asset = db_ops.get_or_create_asset(session, symbol)
        db_ops.upsert_metric_from_payload(session, asset.id, days, data, model_version="manual-override")
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"[WARN] No se pudo persistir metricas override de {symbol}: {e}")
    finally:
        session.close()

    return jsonify({
        "success": True,
        "message": f"Updated metrics for {symbol} ({days} days)",
        "data": data
    })


@app.route("/stocks/<symbol>/signals", methods=["POST"])
@manual_override
def update_signals(symbol):
    data = request.get_json()
    SIGNALS_DATA[symbol] = data

    if isinstance(data, list):
        session = database.get_session()
        try:
            asset = db_ops.get_or_create_asset(session, symbol)
            for sig in data:
                if not sig.get("date") or not sig.get("signal"):
                    continue
                d = db_ops.parse_date(sig["date"])
                correct = sig.get("correct")
                db_ops.upsert_prediction(
                    session, asset.id, d, sig["signal"], model_version="manual-override",
                    actual_price=sig.get("actualPrice"),
                    correct=int(correct) if correct is not None else None,
                )
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"[WARN] No se pudo persistir señales override de {symbol}: {e}")
        finally:
            session.close()

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


def scheduled_refresh():
    print("[SCHEDULER] Refresco automatico post-cierre de mercado...")
    try:
        initialize_data()
    except Exception as e:
        print(f"[SCHEDULER] Error en refresco automatico: {e}")


def start_scheduler():
    """
    Refresca datos y señales cada dia habil despues del cierre de NYSE.
    Nota: si se corre con varios workers (p.ej. gunicorn -w N), cada worker
    tendria su propio scheduler y el refresco se ejecutaria N veces; para
    ese caso conviene mover esto a un proceso/cron externo que llame a
    POST /admin/refresh una sola vez.
    """
    scheduler = BackgroundScheduler(timezone=NYSE_TZ)
    scheduler.add_job(
        scheduled_refresh,
        CronTrigger(day_of_week="mon-fri", hour=REFRESH_HOUR, minute=REFRESH_MINUTE, timezone=NYSE_TZ),
        id="daily_refresh",
        replace_existing=True,
    )
    scheduler.add_job(
        completar_catalogo_si_falta,
        IntervalTrigger(minutes=CATALOG_RETRY_MINUTES),
        id="completar_catalogo",
        replace_existing=True,
    )
    scheduler.start()
    return scheduler


if __name__ == "__main__":
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", "8000"))
    debug_mode = os.getenv("FLASK_DEBUG", "1") == "1"

    initialize_data()
    scheduler = start_scheduler()
    print(f"[INFO] API server started on http://{host}:{port}")
    print(f"[INFO] Refresco automatico: L-V {REFRESH_HOUR:02d}:{REFRESH_MINUTE:02d} hora de Nueva York")
    try:
        app.run(host=host, port=port, debug=debug_mode, use_reloader=False)
    finally:
        scheduler.shutdown(wait=False)
