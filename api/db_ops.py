"""Helpers de upsert compartidos entre el refresco automático (main.persist_to_db)
y los endpoints POST de override manual."""
from datetime import date as date_cls

import models

# Mapea las claves del dict de metricas (generate_metrics / payload de POST) a
# las columnas de models.Metric.
METRIC_FIELD_MAP = {
    "accuracy": "accuracy",
    "f1_macro": "f1_macro",
    "f1_buy": "f1_buy",
    "f1_sell": "f1_sell",
    "cumulativeReturn": "cumulative_return",
    "return_vs_bh": "return_vs_bh",
    "sharpeRatio": "sharpe_ratio",
    "maxDrawdown": "max_drawdown",
    "winRate": "win_rate",
    "profitFactor": "profit_factor",
    "numberOfTrades": "number_of_trades",
    "exposure": "exposure",
    "finalCapital": "final_capital",
    "signal_buy_pct": "signal_buy_pct",
    "signal_hold_pct": "signal_hold_pct",
    "signal_sell_pct": "signal_sell_pct",
}


def parse_date(value) -> date_cls:
    if isinstance(value, date_cls):
        return value
    return date_cls.fromisoformat(str(value)[:10])


def get_or_create_asset(session, ticker: str, name: str | None = None) -> models.Asset:
    asset = session.query(models.Asset).filter_by(ticker=ticker).one_or_none()
    if asset is None:
        asset = models.Asset(ticker=ticker, name=name or ticker)
        session.add(asset)
        session.flush()
    elif name:
        asset.name = name
    return asset


def upsert_ohlcv(session, asset_id: int, date_: date_cls, **fields) -> models.OHLCVDaily:
    row = session.query(models.OHLCVDaily).filter_by(asset_id=asset_id, date=date_).one_or_none()
    if row is None:
        row = models.OHLCVDaily(asset_id=asset_id, date=date_)
        session.add(row)
    for k in ("open", "high", "low", "close", "volume"):
        if fields.get(k) is not None:
            setattr(row, k, fields[k])
    return row


def upsert_prediction(session, asset_id: int, date_: date_cls, signal: str, model_version: str | None = None, **fields) -> models.Prediction:
    row = session.query(models.Prediction).filter_by(asset_id=asset_id, date=date_).one_or_none()
    if row is None:
        row = models.Prediction(asset_id=asset_id, date=date_, signal=signal)
        session.add(row)
    else:
        row.signal = signal
    for k in ("prob_buy", "prob_hold", "prob_sell", "confidence", "actual_price", "correct"):
        if fields.get(k) is not None:
            setattr(row, k, fields[k])
    if model_version:
        row.model_version = model_version
    return row


def upsert_metric(session, asset_id: int, window_days: int, model_version: str | None = None, **fields) -> models.Metric:
    row = session.query(models.Metric).filter_by(asset_id=asset_id, window_days=window_days).one_or_none()
    if row is None:
        row = models.Metric(asset_id=asset_id, window_days=window_days)
        session.add(row)
    for k in METRIC_FIELD_MAP.values():
        if fields.get(k) is not None:
            setattr(row, k, fields[k])
    if model_version:
        row.model_version = model_version
    return row


def upsert_metric_from_payload(session, asset_id: int, window_days: int, payload: dict, model_version: str | None = None) -> models.Metric:
    """Igual que upsert_metric pero traduce nombres estilo API (cumulativeReturn, ...)."""
    mapped = {col: payload[key] for key, col in METRIC_FIELD_MAP.items() if key in payload}
    return upsert_metric(session, asset_id, window_days, model_version=model_version, **mapped)


def compute_correct(signal: str, actual_direction: str) -> bool:
    return (
        (signal == "buy" and actual_direction == "up") or
        (signal == "sell" and actual_direction == "down") or
        (signal == "hold" and actual_direction == "neutral")
    )
