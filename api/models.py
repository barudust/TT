from datetime import datetime

from sqlalchemy import (
    BigInteger, Column, Date, DateTime, ForeignKey, Integer, Numeric,
    String, UniqueConstraint,
)
from sqlalchemy.orm import relationship

from database import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), unique=True, nullable=False)
    name = Column(String(100))
    sector = Column(String(50))
    industry = Column(String(100))

    ohlcv = relationship("OHLCVDaily", back_populates="asset", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="asset", cascade="all, delete-orphan")
    metrics = relationship("Metric", back_populates="asset", cascade="all, delete-orphan")


class OHLCVDaily(Base):
    __tablename__ = "ohlcv_daily"
    __table_args__ = (UniqueConstraint("asset_id", "date", name="uq_ohlcv_asset_date"),)

    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Numeric)
    high = Column(Numeric)
    low = Column(Numeric)
    close = Column(Numeric)
    volume = Column(BigInteger)

    asset = relationship("Asset", back_populates="ohlcv")


class Prediction(Base):
    """Señal diaria generada por el modelo (buy/sell/hold) con su confianza."""
    __tablename__ = "predictions"
    __table_args__ = (UniqueConstraint("asset_id", "date", name="uq_prediction_asset_date"),)

    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    date = Column(Date, nullable=False)
    signal = Column(String(10), nullable=False)  # buy | sell | hold
    prob_buy = Column(Numeric)
    prob_hold = Column(Numeric)
    prob_sell = Column(Numeric)
    confidence = Column(Numeric)
    actual_price = Column(Numeric)
    correct = Column(Integer)  # 0/1, se resuelve un dia despues con el precio real
    model_version = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    asset = relationship("Asset", back_populates="predictions")


class Metric(Base):
    """Metricas de clasificacion + financieras agregadas por ventana (30/60/90 dias)."""
    __tablename__ = "metrics"
    __table_args__ = (UniqueConstraint("asset_id", "window_days", name="uq_metric_asset_window"),)

    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    window_days = Column(Integer, nullable=False)  # 30 | 60 | 90
    model_version = Column(String(50))

    accuracy = Column(Numeric)
    f1_macro = Column(Numeric)
    f1_buy = Column(Numeric)
    f1_sell = Column(Numeric)

    cumulative_return = Column(Numeric)
    return_vs_bh = Column(Numeric)
    sharpe_ratio = Column(Numeric)
    max_drawdown = Column(Numeric)
    win_rate = Column(Numeric)
    profit_factor = Column(Numeric)
    number_of_trades = Column(Integer)
    exposure = Column(Numeric)
    final_capital = Column(Numeric)

    signal_buy_pct = Column(Numeric)
    signal_hold_pct = Column(Numeric)
    signal_sell_pct = Column(Numeric)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    asset = relationship("Asset", back_populates="metrics")
