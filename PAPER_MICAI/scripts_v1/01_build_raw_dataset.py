"""
================================================================================
SCRIPT 1 — BUILD RAW DATASET
================================================================================
Descarga datos de Yahoo Finance y calcula ~52 features técnicas para cada acción.
Agrega contexto de mercado (S&P500, VIX) y calcula el target de percentil 30/70.

Salida: tesis_ml_stocks/01_raw_datasets/
    {TICKER}_raw.parquet   — un archivo por acción con todas las features y el target

Ejecutar primero. Los scripts 02 y 03 dependen de esta salida.

Instalar dependencias:
    pip install yfinance pandas numpy scikit-learn ta pyarrow
================================================================================
"""

import warnings
import numpy as np
import pandas as pd
import yfinance as yf
from pathlib import Path

warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════════════════════

TICKERS = ["AAPL", "NVDA", "TSLA", "AMZN", "MSFT", "GOOGL", "META"]

# Contexto de mercado: S&P500 y VIX
MARKET_TICKERS = {
    "SPY": "SP500",   # ETF del S&P500
    "^VIX": "VIX",   # Índice de volatilidad implícita
}

# Descarga desde 2009 para tener suficiente warmup para indicadores de largo plazo
# (ej. MA200 necesita 200 días antes de producir valores válidos)
DOWNLOAD_START = "2013-01-01"
DOWNLOAD_END   = "2025-12-31"

# Target: percentil del retorno forward en ventana rodante de 252 días (1 año)
# BUY  si retorno forward >= percentil 70
# SELL si retorno forward <= percentil 30
# HOLD en otro caso
PERCENTIL_BUY  = 70
PERCENTIL_SELL = 30
VENTANA_PERCENTIL = 252   # días hábiles = 1 año aproximado

OUTPUT_DIR = Path("tesis_ml_stocks/01_raw_datasets")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ══════════════════════════════════════════════════════════════════════════════
# DESCARGA DE DATOS
# ══════════════════════════════════════════════════════════════════════════════

def descargar_ohlcv(ticker: str, start: str, end: str) -> pd.DataFrame:
    """Descarga datos OHLCV de Yahoo Finance y normaliza columnas."""
    df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.index = pd.to_datetime(df.index)
    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.dropna(inplace=True)
    return df


def descargar_mercado(start: str, end: str) -> pd.DataFrame:
    """
    Descarga SPY (proxy S&P500) y VIX.
    Retorna DataFrame con columnas: SP500_ret, SP500_vol20, VIX, VIX_change.
    """
    market = pd.DataFrame()

    # SPY — Retorno diario y volatilidad 20d
    spy = descargar_ohlcv("SPY", start, end)
    market["SP500_ret"]   = np.log(spy["Close"] / spy["Close"].shift(1))
    market["SP500_vol20"] = market["SP500_ret"].rolling(20).std() * np.sqrt(252)
    market["SP500_mom20"] = (spy["Close"] / spy["Close"].shift(19)) - 1

    # VIX — Nivel y cambio diario
    vix = yf.download("^VIX", start=start, end=end, auto_adjust=True, progress=False)
    if isinstance(vix.columns, pd.MultiIndex):
        vix.columns = vix.columns.get_level_values(0)
    vix.index = pd.to_datetime(vix.index)
    market["VIX"]        = vix["Close"]
    market["VIX_change"] = vix["Close"].pct_change()
    market["VIX_norm"]   = (vix["Close"] - vix["Close"].rolling(252).mean()) / (vix["Close"].rolling(252).std() + 1e-8)

    return market.dropna(how="all")


# ══════════════════════════════════════════════════════════════════════════════
# CÁLCULO DE FEATURES
# ══════════════════════════════════════════════════════════════════════════════

def _rsi(serie: pd.Series, periodo: int = 14) -> pd.Series:
    """RSI de Wilder mediante EMA."""
    delta = serie.diff()
    g = delta.clip(lower=0).ewm(alpha=1/periodo, min_periods=periodo, adjust=False).mean()
    l = (-delta.clip(upper=0)).ewm(alpha=1/periodo, min_periods=periodo, adjust=False).mean()
    return 100 - (100 / (1 + g / (l + 1e-8)))


def _atr(high: pd.Series, low: pd.Series, close: pd.Series, periodo: int = 14) -> pd.Series:
    """Average True Range."""
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low  - close.shift(1)).abs(),
    ], axis=1).max(axis=1)
    return tr.rolling(periodo).mean()


def _obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """On-Balance Volume."""
    return (np.sign(close.diff()) * volume).fillna(0).cumsum()


def _stochastic(high: pd.Series, low: pd.Series, close: pd.Series,
                k_period: int = 14, d_period: int = 3):
    """Stochastic Oscillator %K y %D."""
    lowest  = low.rolling(k_period).min()
    highest = high.rolling(k_period).max()
    k = 100 * (close - lowest) / (highest - lowest + 1e-8)
    d = k.rolling(d_period).mean()
    return k, d


def _macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """MACD, línea de señal e histograma."""
    ema_fast   = close.ewm(span=fast,   adjust=False).mean()
    ema_slow   = close.ewm(span=slow,   adjust=False).mean()
    macd_line  = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram  = macd_line - signal_line
    return macd_line, signal_line, histogram


def _cmf(high: pd.Series, low: pd.Series, close: pd.Series,
         volume: pd.Series, periodo: int = 20) -> pd.Series:
    """Chaikin Money Flow."""
    clv = ((close - low) - (high - close)) / (high - low + 1e-8)
    return (clv * volume).rolling(periodo).sum() / (volume.rolling(periodo).sum() + 1e-8)


def _mfi(high: pd.Series, low: pd.Series, close: pd.Series,
         volume: pd.Series, periodo: int = 14) -> pd.Series:
    """Money Flow Index."""
    tp = (high + low + close) / 3
    raw_mf = tp * volume
    pos = raw_mf.where(tp > tp.shift(1), 0).rolling(periodo).sum()
    neg = raw_mf.where(tp < tp.shift(1), 0).rolling(periodo).sum()
    return 100 - (100 / (1 + pos / (neg + 1e-8)))


def _williams_r(high: pd.Series, low: pd.Series, close: pd.Series,
                periodo: int = 14) -> pd.Series:
    """Williams %R."""
    highest = high.rolling(periodo).max()
    lowest  = low.rolling(periodo).min()
    return -100 * (highest - close) / (highest - lowest + 1e-8)


def _vwap_distancia(high, low, close, volume) -> pd.Series:
    """
    Distancia del precio al VWAP rodante de 20 días.
    VWAP = suma(Precio_tipico × Volumen) / suma(Volumen)
    """
    tp    = (high + low + close) / 3
    vwap  = (tp * volume).rolling(20).sum() / (volume.rolling(20).sum() + 1e-8)
    return (close - vwap) / (vwap + 1e-8)


def _pendiente_ma(ma: pd.Series, ventana: int = 5) -> pd.Series:
    """
    Pendiente normalizada de la MA en los últimos 'ventana' días.
    Indica si la MA está subiendo o bajando y con qué fuerza.
    """
    return (ma - ma.shift(ventana)) / (ma.shift(ventana) + 1e-8)


def calcular_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula las ~49 features técnicas sobre un DataFrame OHLCV.
    Retorna DataFrame con el mismo índice que df.
    Las primeras filas tendrán NaN por el warmup de indicadores.
    """
    out   = pd.DataFrame(index=df.index)
    c     = df["Close"]
    h     = df["High"]
    l     = df["Low"]
    o     = df["Open"]
    v     = df["Volume"]
    eps   = 1e-8

    # ── CATEGORÍA 1: Retornos logarítmicos ──────────────────────────────────
    out["ret_1d"]  = np.log(c / c.shift(1))
    out["ret_2d"]  = np.log(c / c.shift(2))
    out["ret_3d"]  = np.log(c / c.shift(3))
    out["ret_5d"]  = np.log(c / c.shift(5))
    out["ret_10d"] = np.log(c / c.shift(10))

    # ── CATEGORÍA 2: Momentum ────────────────────────────────────────────────
    out["mom_5d"]  = (c / c.shift(4))  - 1
    out["mom_10d"] = (c / c.shift(9))  - 1
    out["mom_20d"] = (c / c.shift(19)) - 1
    out["mom_60d"] = (c / c.shift(59)) - 1

    # ── CATEGORÍA 3: Medias móviles y tendencia ──────────────────────────────
    ma10  = c.rolling(10).mean()
    ma20  = c.rolling(20).mean()
    ma30  = c.rolling(30).mean()
    ma50  = c.rolling(50).mean()
    ma200 = c.rolling(200).mean()

    out["dist_ma10"]  = (c / ma10)  - 1
    out["dist_ma20"]  = (c / ma20)  - 1
    out["dist_ma30"]  = (c / ma30)  - 1
    out["dist_ma50"]  = (c / ma50)  - 1
    out["dist_ma200"] = (c / ma200) - 1

    # Cruces: posición relativa entre dos MAs (positivo = MA rápida > MA lenta)
    out["cruce_ma10_ma50"]  = (ma10 / ma50)  - 1
    out["cruce_ma20_ma50"]  = (ma20 / ma50)  - 1
    out["cruce_ma50_ma200"] = (ma50 / ma200) - 1

    # Pendiente normalizada de MA20 en últimos 5 días
    out["pendiente_ma20"] = _pendiente_ma(ma20, 5)

    # ── CATEGORÍA 4: Volatilidad ─────────────────────────────────────────────
    atr14 = _atr(h, l, c, 14)
    out["atr_14"]   = atr14
    out["atr_norm"] = atr14 / (c + eps)

    ret = out["ret_1d"]
    out["vol_5d"]  = ret.rolling(5).std()  * np.sqrt(252)
    out["vol_10d"] = ret.rolling(10).std() * np.sqrt(252)
    out["vol_20d"] = ret.rolling(20).std() * np.sqrt(252)
    out["vol_60d"] = ret.rolling(60).std() * np.sqrt(252)

    # Ratio volatilidad corto/largo: detecta expansión o compresión de volatilidad
    out["vol_ratio_5_20"]  = out["vol_5d"]  / (out["vol_20d"] + eps)
    out["vol_ratio_20_60"] = out["vol_20d"] / (out["vol_60d"] + eps)

    # ── CATEGORÍA 5: Osciladores técnicos ───────────────────────────────────
    out["rsi_14"] = _rsi(c, 14)
    out["rsi_7"]  = _rsi(c, 7)

    macd, macd_sig, macd_hist = _macd(c)
    out["macd"]      = macd      / (c + eps)   # normalizado por precio
    out["macd_sig"]  = macd_sig  / (c + eps)
    out["macd_hist"] = macd_hist / (c + eps)

    stoch_k, stoch_d = _stochastic(h, l, c)
    out["stoch_k"] = stoch_k
    out["stoch_d"] = stoch_d
    out["stoch_diff"] = stoch_k - stoch_d    # divergencia %K - %D

    out["williams_r"] = _williams_r(h, l, c)

    # ── CATEGORÍA 6: Volumen y flujo de dinero ───────────────────────────────
    out["vol_log"]   = np.log(v + 1)
    vol_ma20         = v.rolling(20).mean()
    out["vol_ratio"] = v / (vol_ma20 + eps)

    obv = _obv(c, v)
    obv_ma20 = obv.rolling(20).mean()
    out["obv_ratio"]   = (obv / (obv_ma20.abs() + eps)) - 1
    out["obv_pendiente"] = _pendiente_ma(obv, 5) / (c + eps)   # normalizado

    out["vwap_dist"] = _vwap_distancia(h, l, c, v)
    out["cmf_20"]    = _cmf(h, l, c, v, 20)
    out["mfi_14"]    = _mfi(h, l, c, v, 14)

    # Tendencia de volumen: ¿el volumen está creciendo o cayendo?
    out["vol_trend"] = (vol_ma20 / (v.rolling(60).mean() + eps)) - 1

    # ── CATEGORÍA 7: Características de velas japonesas ──────────────────────
    body    = (c - o).abs()
    rango   = h - l

    out["rango_rel"]         = rango / (c + eps)
    out["cambio_intra"]      = (c - o) / (o + eps)
    out["cuerpo_rel"]        = body / (rango + eps)    # qué parte del rango es cuerpo

    out["sombra_sup"] = (h - pd.concat([o, c], axis=1).max(axis=1)) / (atr14 + eps)
    out["sombra_inf"] = (pd.concat([o, c], axis=1).min(axis=1) - l) / (atr14 + eps)

    # Gap de apertura respecto al cierre anterior
    out["gap_apertura"] = (o - c.shift(1)) / (c.shift(1) + eps)

    # High/Low ratio: posición del cierre dentro del rango diario [0,1]
    out["hl_ratio"] = (c - l) / (rango + eps)

    # ── CATEGORÍA 8: Estacionalidad ──────────────────────────────────────────
    dia = df.index.dayofweek                     # 0=lunes … 4=viernes
    mes = df.index.month                         # 1..12

    out["dia_sin"] = np.sin(2 * np.pi * dia / 5)
    out["dia_cos"] = np.cos(2 * np.pi * dia / 5)
    out["mes_sin"] = np.sin(2 * np.pi * mes / 12)
    out["mes_cos"] = np.cos(2 * np.pi * mes / 12)

    semana_mes = df.index.to_series().apply(lambda d: (d.day - 1) // 7 + 1)
    out["semana_mes"] = (semana_mes - 2.5) / 2.5    # normalizado [-1, 1]

    return out


# ══════════════════════════════════════════════════════════════════════════════
# CÁLCULO DEL TARGET
# ══════════════════════════════════════════════════════════════════════════════

def calcular_target(close: pd.Series,
                    pct_buy:  int = PERCENTIL_BUY,
                    pct_sell: int = PERCENTIL_SELL,
                    ventana:  int = VENTANA_PERCENTIL) -> pd.DataFrame:
    """
    Target: Quintile Forward Return con umbrales de percentil rodante.

    Retorno forward de 1 día:
        r_fwd(t) = ln(Close_{t+1} / Close_t)

    Umbrales calculados sobre ventana rodante de 'ventana' días:
        umbral_buy(t)  = percentil_70 de los últimos 252 retornos forward
        umbral_sell(t) = percentil_30 de los últimos 252 retornos forward

    Clasificación:
        BUY  (2): r_fwd(t) >= umbral_buy(t)
        SELL (0): r_fwd(t) <= umbral_sell(t)
        HOLD (1): en otro caso

    Ventajas sobre umbral fijo alpha×sigma:
    - Se adapta automáticamente a regímenes bull/bear/lateral
    - Sin hiperparámetro alpha que justificar
    - Balance de clases garantizado ≈ 30% BUY / 40% HOLD / 30% SELL
    - Interpretable: "comprar cuando el retorno esperado está en el top 30% histórico"

    Retorna DataFrame con columnas: target, r_forward, umbral_buy, umbral_sell
    """
    r_fwd = np.log(close.shift(-1) / close)   # retorno del día siguiente

    # Percentiles rodantes calculados sobre los retornos forward históricos.
    # Se usa shift(1) para que el umbral del día t no incluya r_fwd(t).
    umbral_buy  = r_fwd.shift(1).rolling(ventana, min_periods=ventana//2).quantile(pct_buy  / 100)
    umbral_sell = r_fwd.shift(1).rolling(ventana, min_periods=ventana//2).quantile(pct_sell / 100)

    target = pd.Series(1, index=close.index, dtype=int)   # HOLD por defecto
    target[r_fwd >= umbral_buy]  = 2   # BUY
    target[r_fwd <= umbral_sell] = 0   # SELL

    return pd.DataFrame({
        "target":       target,
        "r_forward":    r_fwd,
        "umbral_buy":   umbral_buy,
        "umbral_sell":  umbral_sell,
    })


# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

def pipeline():
    print("=" * 70)
    print("  SCRIPT 1 — BUILD RAW DATASET")
    print("  Features: ~49 técnicas + 5 de mercado (SPY/VIX)")
    print("  Target  : Percentil 30/70 rodante de retorno forward 1d")
    print("=" * 70)

    # ── 1. Datos de mercado ──────────────────────────────────────────────────
    print("\n[1/3] Descargando datos de mercado (SPY, VIX)...")
    try:
        df_market = descargar_mercado(DOWNLOAD_START, DOWNLOAD_END)
        print(f"      SPY + VIX: {len(df_market)} días")
    except Exception as e:
        print(f"      ⚠ Error descargando mercado: {e}. Continuando sin features de mercado.")
        df_market = pd.DataFrame()

    # ── 2. Cada acción ───────────────────────────────────────────────────────
    print("\n[2/3] Calculando features por acción...")
    resumen = []

    for ticker in TICKERS:
        print(f"\n  {'─'*55}")
        print(f"  {ticker}")
        print(f"  {'─'*55}")

        # Descargar OHLCV
        try:
            df_raw = descargar_ohlcv(ticker, DOWNLOAD_START, DOWNLOAD_END)
            print(f"  Días descargados : {len(df_raw)}")
        except Exception as e:
            print(f"  ERROR al descargar {ticker}: {e}")
            continue

        # Calcular features técnicas
        df_feat = calcular_features(df_raw)

        # Agregar OHLCV crudo (para normalización local en CNN-LSTM)
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            df_feat[f"raw_{col.lower()}"] = df_raw[col]

        # Agregar features de mercado alineadas por fecha
        if not df_market.empty:
            df_feat = df_feat.join(df_market, how="left")
            df_feat[df_market.columns] = df_feat[df_market.columns].ffill()

        # Calcular target
        df_target = calcular_target(df_raw["Close"])
        df_feat = df_feat.join(df_target)

        # Eliminar filas con NaN (warmup de indicadores + último día sin target)
        df_feat.dropna(inplace=True)

        # Quitar el último día si r_forward es NaN por el shift(-1)
        df_feat = df_feat[df_feat["r_forward"].notna()]

        # Distribución del target
        dist = df_feat["target"].value_counts().sort_index()
        n    = len(df_feat)
        print(f"  Filas válidas    : {n}")
        print(f"  Rango de fechas  : {df_feat.index[0].date()} → {df_feat.index[-1].date()}")
        for k in [0, 1, 2]:
            etq = {0: "SELL", 1: "HOLD", 2: "BUY"}[k]
            cnt = dist.get(k, 0)
            print(f"  {etq}: {cnt:5d}  ({cnt/n*100:.1f}%)")

        # Guardar
        out_path = OUTPUT_DIR / f"{ticker}_raw.parquet"
        df_feat.to_parquet(out_path)
        print(f"  Guardado → {out_path}")
        print(f"  Columnas totales : {len(df_feat.columns)}")

        resumen.append({
            "Ticker"      : ticker,
            "N_filas"     : n,
            "Fecha_inicio": str(df_feat.index[0].date()),
            "Fecha_fin"   : str(df_feat.index[-1].date()),
            "N_features"  : len(df_feat.columns) - 5,   # excluye raw_* y target cols
            "SELL_%"      : round(dist.get(0, 0) / n * 100, 1),
            "HOLD_%"      : round(dist.get(1, 0) / n * 100, 1),
            "BUY_%"       : round(dist.get(2, 0) / n * 100, 1),
        })

    # ── 3. Resumen ───────────────────────────────────────────────────────────
    print("\n[3/3] Guardando resumen...")
    df_res = pd.DataFrame(resumen)
    df_res.to_csv(OUTPUT_DIR / "resumen_raw.csv", index=False)

    print("\n" + "=" * 70)
    print("  RESUMEN FINAL")
    print("=" * 70)
    print(df_res.to_string(index=False))

    print(f"\n✓ Datasets crudos guardados en: {OUTPUT_DIR.resolve()}")
    print("\nSiguiente paso → ejecutar 02_validate_features.py")


if __name__ == "__main__":
    pipeline()
