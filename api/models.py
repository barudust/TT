from database import db
from datetime import datetime

class Asset(db.Model):
    __tablename__ = 'assets'
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100))
    sector = db.Column(db.String(50))

class OHLCVDaily(db.Model):
    __tablename__ = 'ohlcv_daily'
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    open = db.Column(db.Numeric)
    high = db.Column(db.Numeric)
    low = db.Column(db.Numeric)
    close = db.Column(db.Numeric)
    volume = db.Column(db.BigInteger)

class FeaturesDaily(db.Model):
    __tablename__ = 'features_daily'
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    # Retornos y Momentum
    retorno_1d = db.Column(db.Numeric)
    retorno_2d = db.Column(db.Numeric)
    momentum_5d = db.Column(db.Numeric)
    momentum_20d = db.Column(db.Numeric)
    # Medias Móviles y Osciladores
    distancia_ma10 = db.Column(db.Numeric)
    distancia_ma30 = db.Column(db.Numeric)
    rsi_14 = db.Column(db.Numeric)
    atr_14 = db.Column(db.Numeric)
    atr_norm = db.Column(db.Numeric)
    volatilidad_20d = db.Column(db.Numeric)
    # Volumen y Flujo
    volumen_log = db.Column(db.Numeric)
    volumen_ratio = db.Column(db.Numeric)
    obv_ratio = db.Column(db.Numeric)
    # Análisis Intradiario y Velas
    rango_relativo = db.Column(db.Numeric)
    cambio_intradiario = db.Column(db.Numeric)
    sombra_superior = db.Column(db.Numeric)
    sombra_inferior = db.Column(db.Numeric)
    # Datos Temporales Cíclicos
    dia_semana_sin = db.Column(db.Numeric)
    dia_semana_cos = db.Column(db.Numeric)
    semana_mes = db.Column(db.Numeric)

class Predictions(db.Model):
    __tablename__ = 'predictions'
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    signal = db.Column(db.String(20))
    prob_buy = db.Column(db.Numeric)
    prob_hold = db.Column(db.Numeric)
    prob_sell = db.Column(db.Numeric)
    model_version = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class StrategyMetrics(db.Model):
    __tablename__ = 'strategy_metrics'
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    evaluation_date = db.Column(db.Date, nullable=False)
    model_version = db.Column(db.String(50))
    cumul_return = db.Column(db.Numeric)
    annual_return = db.Column(db.Numeric)
    sharpe_ratio = db.Column(db.Numeric)
    max_drawdown = db.Column(db.Numeric)
    win_rate = db.Column(db.Numeric)
    total_trades = db.Column(db.Integer)

class ModelMetrics(db.Model):
    __tablename__ = 'model_metrics'
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    evaluation_date = db.Column(db.Date, nullable=False)
    model_version = db.Column(db.String(50))
    accuracy = db.Column(db.Numeric)
    f1_macro = db.Column(db.Numeric)
    f1_buy = db.Column(db.Numeric)
    f1_hold = db.Column(db.Numeric)
    f1_sell = db.Column(db.Numeric)
    confusion_matrix = db.Column(db.JSON) # JSONB en Postgres