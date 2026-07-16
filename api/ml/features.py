"""
Ingenieria de features tecnicas + contexto de mercado (SPY/VIX).

Puerto exacto de la logica de calculo usada para entrenar los modelos en
`RESULTADOS_OPTIMIZADOS/` (ver `scripts_v1/01_build_raw_dataset.py` y `scripts_opt/common.py`
en la raiz del repo). Las formulas deben coincidir bit a bit con las de
entrenamiento: cualquier cambio aqui hace que las predicciones en vivo dejen
de ser comparables con las metricas reportadas en la tesis.
"""
import numpy as np
import pandas as pd
import yfinance as yf

# Debe coincidir con feat_cols del modelo ganador (metricas_global.json).
FEATURE_COLUMNS = [
    "ret_1d", "ret_2d", "ret_3d", "ret_5d", "ret_10d",
    "mom_5d", "mom_10d", "mom_20d", "mom_60d",
    "dist_ma10", "dist_ma20", "dist_ma30", "dist_ma50", "dist_ma200",
    "cruce_ma10_ma50", "cruce_ma20_ma50", "cruce_ma50_ma200", "pendiente_ma20",
    "atr_14", "atr_norm",
    "vol_5d", "vol_10d", "vol_20d", "vol_60d",
    "vol_ratio_5_20", "vol_ratio_20_60",
    "rsi_14", "rsi_7",
    "macd", "macd_sig", "macd_hist",
    "stoch_k", "stoch_d", "stoch_diff", "williams_r",
    "vol_log", "vol_ratio", "obv_ratio", "obv_pendiente",
    "vwap_dist", "cmf_20", "mfi_14", "vol_trend",
    "rango_rel", "cambio_intra", "cuerpo_rel", "sombra_sup", "sombra_inf",
    "gap_apertura", "hl_ratio",
    "dia_sin", "dia_cos", "mes_sin", "mes_cos", "semana_mes",
    "SP500_ret", "SP500_vol20", "SP500_mom20",
    "VIX", "VIX_change", "VIX_norm",
]

EPS = 1e-8


def fetch_ohlcv(ticker: str, period: str = "3y") -> pd.DataFrame:
    """Descarga OHLCV de Yahoo Finance y normaliza columnas."""
    df = yf.download(ticker, period=period, auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.index = pd.to_datetime(df.index)
    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.dropna(inplace=True)
    return df


def fetch_market_context(period: str = "3y") -> pd.DataFrame:
    """
    Descarga SPY (proxy S&P500) y VIX.
    Retorna DataFrame con columnas: SP500_ret, SP500_vol20, SP500_mom20,
    VIX, VIX_change, VIX_norm.
    """
    market = pd.DataFrame()

    spy = fetch_ohlcv("SPY", period)
    market["SP500_ret"] = np.log(spy["Close"] / spy["Close"].shift(1))
    market["SP500_vol20"] = market["SP500_ret"].rolling(20).std() * np.sqrt(252)
    market["SP500_mom20"] = (spy["Close"] / spy["Close"].shift(19)) - 1

    vix = yf.download("^VIX", period=period, auto_adjust=True, progress=False)
    if isinstance(vix.columns, pd.MultiIndex):
        vix.columns = vix.columns.get_level_values(0)
    vix.index = pd.to_datetime(vix.index)
    market["VIX"] = vix["Close"]
    market["VIX_change"] = vix["Close"].pct_change()
    market["VIX_norm"] = (vix["Close"] - vix["Close"].rolling(252).mean()) / (
        vix["Close"].rolling(252).std() + EPS
    )

    return market.dropna(how="all")


def _rsi(serie: pd.Series, periodo: int = 14) -> pd.Series:
    """RSI de Wilder mediante EMA."""
    delta = serie.diff()
    g = delta.clip(lower=0).ewm(alpha=1 / periodo, min_periods=periodo, adjust=False).mean()
    l = (-delta.clip(upper=0)).ewm(alpha=1 / periodo, min_periods=periodo, adjust=False).mean()
    return 100 - (100 / (1 + g / (l + EPS)))


def _atr(high: pd.Series, low: pd.Series, close: pd.Series, periodo: int = 14) -> pd.Series:
    """Average True Range."""
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs(),
    ], axis=1).max(axis=1)
    return tr.rolling(periodo).mean()


def _obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """On-Balance Volume."""
    return (np.sign(close.diff()) * volume).fillna(0).cumsum()


def _stochastic(high: pd.Series, low: pd.Series, close: pd.Series,
                 k_period: int = 14, d_period: int = 3):
    """Stochastic Oscillator %K y %D."""
    lowest = low.rolling(k_period).min()
    highest = high.rolling(k_period).max()
    k = 100 * (close - lowest) / (highest - lowest + EPS)
    d = k.rolling(d_period).mean()
    return k, d


def _macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """MACD, linea de señal e histograma."""
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def _cmf(high: pd.Series, low: pd.Series, close: pd.Series,
          volume: pd.Series, periodo: int = 20) -> pd.Series:
    """Chaikin Money Flow."""
    clv = ((close - low) - (high - close)) / (high - low + EPS)
    return (clv * volume).rolling(periodo).sum() / (volume.rolling(periodo).sum() + EPS)


def _mfi(high: pd.Series, low: pd.Series, close: pd.Series,
          volume: pd.Series, periodo: int = 14) -> pd.Series:
    """Money Flow Index."""
    tp = (high + low + close) / 3
    raw_mf = tp * volume
    pos = raw_mf.where(tp > tp.shift(1), 0).rolling(periodo).sum()
    neg = raw_mf.where(tp < tp.shift(1), 0).rolling(periodo).sum()
    return 100 - (100 / (1 + pos / (neg + EPS)))


def _williams_r(high: pd.Series, low: pd.Series, close: pd.Series,
                 periodo: int = 14) -> pd.Series:
    """Williams %R."""
    highest = high.rolling(periodo).max()
    lowest = low.rolling(periodo).min()
    return -100 * (highest - close) / (highest - lowest + EPS)


def _vwap_distancia(high, low, close, volume) -> pd.Series:
    """Distancia del precio al VWAP rodante de 20 dias."""
    tp = (high + low + close) / 3
    vwap = (tp * volume).rolling(20).sum() / (volume.rolling(20).sum() + EPS)
    return (close - vwap) / (vwap + EPS)


def _pendiente_ma(ma: pd.Series, ventana: int = 5) -> pd.Series:
    """Pendiente normalizada de la MA en los ultimos 'ventana' dias."""
    return (ma - ma.shift(ventana)) / (ma.shift(ventana) + EPS)


def calcular_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula las ~55 features tecnicas sobre un DataFrame OHLCV.
    Retorna DataFrame con el mismo indice que df. Las primeras filas
    tendran NaN por el warmup de indicadores (hasta 200 dias para MA200).
    """
    out = pd.DataFrame(index=df.index)
    c = df["Close"]
    h = df["High"]
    l = df["Low"]
    o = df["Open"]
    v = df["Volume"]

    out["ret_1d"] = np.log(c / c.shift(1))
    out["ret_2d"] = np.log(c / c.shift(2))
    out["ret_3d"] = np.log(c / c.shift(3))
    out["ret_5d"] = np.log(c / c.shift(5))
    out["ret_10d"] = np.log(c / c.shift(10))

    out["mom_5d"] = (c / c.shift(4)) - 1
    out["mom_10d"] = (c / c.shift(9)) - 1
    out["mom_20d"] = (c / c.shift(19)) - 1
    out["mom_60d"] = (c / c.shift(59)) - 1

    ma10 = c.rolling(10).mean()
    ma20 = c.rolling(20).mean()
    ma30 = c.rolling(30).mean()
    ma50 = c.rolling(50).mean()
    ma200 = c.rolling(200).mean()

    out["dist_ma10"] = (c / ma10) - 1
    out["dist_ma20"] = (c / ma20) - 1
    out["dist_ma30"] = (c / ma30) - 1
    out["dist_ma50"] = (c / ma50) - 1
    out["dist_ma200"] = (c / ma200) - 1

    out["cruce_ma10_ma50"] = (ma10 / ma50) - 1
    out["cruce_ma20_ma50"] = (ma20 / ma50) - 1
    out["cruce_ma50_ma200"] = (ma50 / ma200) - 1

    out["pendiente_ma20"] = _pendiente_ma(ma20, 5)

    atr14 = _atr(h, l, c, 14)
    out["atr_14"] = atr14
    out["atr_norm"] = atr14 / (c + EPS)

    ret = out["ret_1d"]
    out["vol_5d"] = ret.rolling(5).std() * np.sqrt(252)
    out["vol_10d"] = ret.rolling(10).std() * np.sqrt(252)
    out["vol_20d"] = ret.rolling(20).std() * np.sqrt(252)
    out["vol_60d"] = ret.rolling(60).std() * np.sqrt(252)

    out["vol_ratio_5_20"] = out["vol_5d"] / (out["vol_20d"] + EPS)
    out["vol_ratio_20_60"] = out["vol_20d"] / (out["vol_60d"] + EPS)

    out["rsi_14"] = _rsi(c, 14)
    out["rsi_7"] = _rsi(c, 7)

    macd, macd_sig, macd_hist = _macd(c)
    out["macd"] = macd / (c + EPS)
    out["macd_sig"] = macd_sig / (c + EPS)
    out["macd_hist"] = macd_hist / (c + EPS)

    stoch_k, stoch_d = _stochastic(h, l, c)
    out["stoch_k"] = stoch_k
    out["stoch_d"] = stoch_d
    out["stoch_diff"] = stoch_k - stoch_d

    out["williams_r"] = _williams_r(h, l, c)

    out["vol_log"] = np.log(v + 1)
    vol_ma20 = v.rolling(20).mean()
    out["vol_ratio"] = v / (vol_ma20 + EPS)

    obv = _obv(c, v)
    obv_ma20 = obv.rolling(20).mean()
    out["obv_ratio"] = (obv / (obv_ma20.abs() + EPS)) - 1
    out["obv_pendiente"] = _pendiente_ma(obv, 5) / (c + EPS)

    out["vwap_dist"] = _vwap_distancia(h, l, c, v)
    out["cmf_20"] = _cmf(h, l, c, v, 20)
    out["mfi_14"] = _mfi(h, l, c, v, 14)

    out["vol_trend"] = (vol_ma20 / (v.rolling(60).mean() + EPS)) - 1

    body = (c - o).abs()
    rango = h - l

    out["rango_rel"] = rango / (c + EPS)
    out["cambio_intra"] = (c - o) / (o + EPS)
    out["cuerpo_rel"] = body / (rango + EPS)

    out["sombra_sup"] = (h - pd.concat([o, c], axis=1).max(axis=1)) / (atr14 + EPS)
    out["sombra_inf"] = (pd.concat([o, c], axis=1).min(axis=1) - l) / (atr14 + EPS)

    out["gap_apertura"] = (o - c.shift(1)) / (c.shift(1) + EPS)
    out["hl_ratio"] = (c - l) / (rango + EPS)

    dia = df.index.dayofweek
    mes = df.index.month

    out["dia_sin"] = np.sin(2 * np.pi * dia / 5)
    out["dia_cos"] = np.cos(2 * np.pi * dia / 5)
    out["mes_sin"] = np.sin(2 * np.pi * mes / 12)
    out["mes_cos"] = np.cos(2 * np.pi * mes / 12)

    semana_mes = df.index.to_series().apply(lambda d: (d.day - 1) // 7 + 1)
    out["semana_mes"] = (semana_mes - 2.5) / 2.5

    return out


def build_feature_frame(df_ohlcv: pd.DataFrame, df_market: pd.DataFrame) -> pd.DataFrame:
    """
    Combina features tecnicas + contexto de mercado en un unico DataFrame,
    listo para seleccionar FEATURE_COLUMNS y alimentar al modelo.
    Conserva tambien Open/High/Low/Close/Volume crudos para uso del API
    (precio actual, historial de velas, etc.) y descarta filas con NaN
    (warmup de indicadores).
    """
    feat = calcular_features(df_ohlcv)

    for col in ["Open", "High", "Low", "Close", "Volume"]:
        feat[f"raw_{col.lower()}"] = df_ohlcv[col]

    if not df_market.empty:
        feat = feat.join(df_market, how="left")
        feat[df_market.columns] = feat[df_market.columns].ffill()

    feat.dropna(subset=FEATURE_COLUMNS, inplace=True)
    return feat
