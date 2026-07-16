"""
================================================================================
EXPANSIÓN DE DATOS DE MERCADO — Yahoo Finance gratis
================================================================================
Agrega features de mercado adicionales a las 61 actuales:
  - Yield curve: ^TNX (10Y), ^IRX (3M), ^TYX (30Y), spread 10Y-3M
  - DXY (dollar index)
  - Gold (GC=F), Oil (CL=F), Copper (HG=F)
  - Sectores: XLK (tech), XLF (fin), XLE (energy), XLY (cons disc)
  - Bond ETF: TLT (20+y bonds)
  - High yield: HYG
  - Volatility term: VIX9D, VIX3M (si disponibles), VVIX

Genera tesis_ml_stocks/01_raw_datasets_v3/ con features ampliadas.
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import sys, warnings, functools
import numpy as np
import pandas as pd
import yfinance as yf
from pathlib import Path

try: sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except: pass
print = functools.partial(print, flush=True)
warnings.filterwarnings("ignore")

OUT_DIR = Path("tesis_ml_stocks/01_raw_datasets_v3")
OUT_DIR.mkdir(parents=True, exist_ok=True)
RAW_DIR = Path("tesis_ml_stocks/01_raw_datasets")
TICKERS = ["AAPL", "NVDA", "TSLA", "AMZN", "MSFT", "GOOGL", "META"]

# Tickers extra de mercado (todo gratis en Yahoo)
MARKET_EXTRAS = {
    "TNX":   "^TNX",     # 10Y treasury yield
    "IRX":   "^IRX",     # 13W (3M) treasury yield
    "TYX":   "^TYX",     # 30Y treasury yield
    "DXY":   "DX-Y.NYB", # Dollar index
    "GOLD":  "GC=F",     # Gold futures
    "OIL":   "CL=F",     # Crude oil futures
    "COPPER":"HG=F",     # Copper futures
    "TLT":   "TLT",      # 20+ year Treasury ETF
    "HYG":   "HYG",      # High Yield Corp Bond ETF
    "LQD":   "LQD",      # Investment Grade Corp Bond ETF
    "XLK":   "XLK",      # Tech sector
    "XLF":   "XLF",      # Financial sector
    "XLE":   "XLE",      # Energy sector
    "XLY":   "XLY",      # Consumer Discretionary
}

DOWNLOAD_START = "2013-01-01"
DOWNLOAD_END   = "2025-12-31"


def descargar_extra(yf_ticker, name):
    try:
        df = yf.download(yf_ticker, start=DOWNLOAD_START, end=DOWNLOAD_END,
                         auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        if df.empty:
            print(f"  ⚠ {name} ({yf_ticker}): vacío")
            return None
        df.index = pd.to_datetime(df.index)
        return df["Close"].rename(f"{name}_close")
    except Exception as e:
        print(f"  ⚠ {name} ({yf_ticker}): {e}")
        return None


def build_market_features():
    """Descarga y construye features de mercado adicionales."""
    print("Descargando datos de mercado adicionales...")
    market = pd.DataFrame()

    for name, yf_t in MARKET_EXTRAS.items():
        s = descargar_extra(yf_t, name)
        if s is not None:
            market[f"{name}_close"] = s
            print(f"  ✓ {name}: {len(s)} días")

    if market.empty:
        return market

    # Calcular features derivadas
    print("\nCalculando features derivadas...")
    feats = pd.DataFrame(index=market.index)

    # Yields: niveles + spreads + cambios
    if "TNX_close" in market and "IRX_close" in market:
        feats["yield_10y"]    = market["TNX_close"]
        feats["yield_3m"]     = market["IRX_close"]
        feats["yield_spread_10y_3m"] = market["TNX_close"] - market["IRX_close"]
        feats["yield_10y_change5d"]  = market["TNX_close"].pct_change(5)
    if "TYX_close" in market and "TNX_close" in market:
        feats["yield_spread_30y_10y"] = market["TYX_close"] - market["TNX_close"]

    # DXY: nivel + retorno + z-score
    if "DXY_close" in market:
        feats["dxy_ret5d"]  = market["DXY_close"].pct_change(5)
        feats["dxy_ret20d"] = market["DXY_close"].pct_change(20)
        feats["dxy_z60"]    = ((market["DXY_close"] - market["DXY_close"].rolling(60).mean()) /
                                (market["DXY_close"].rolling(60).std() + 1e-8))

    # Gold / Oil / Copper
    for asset in ["GOLD", "OIL", "COPPER"]:
        col = f"{asset}_close"
        if col in market:
            feats[f"{asset.lower()}_ret5d"]  = market[col].pct_change(5)
            feats[f"{asset.lower()}_ret20d"] = market[col].pct_change(20)
            feats[f"{asset.lower()}_vol20"]  = market[col].pct_change().rolling(20).std() * np.sqrt(252)

    # Gold-Oil ratio (risk-on/off proxy)
    if "GOLD_close" in market and "OIL_close" in market:
        feats["gold_oil_ratio"] = market["GOLD_close"] / (market["OIL_close"] + 1e-8)

    # Bonds: TLT (long bonds), HYG (high yield), LQD (IG)
    for asset in ["TLT", "HYG", "LQD"]:
        col = f"{asset}_close"
        if col in market:
            feats[f"{asset.lower()}_ret5d"]  = market[col].pct_change(5)
            feats[f"{asset.lower()}_ret20d"] = market[col].pct_change(20)

    # Credit spread proxy: HYG vs LQD (high yield - investment grade)
    if "HYG_close" in market and "LQD_close" in market:
        feats["credit_spread_hyg_lqd"] = (market["HYG_close"].pct_change(20) -
                                          market["LQD_close"].pct_change(20))

    # Sector momentum
    for sector in ["XLK", "XLF", "XLE", "XLY"]:
        col = f"{sector}_close"
        if col in market:
            feats[f"{sector.lower()}_mom5d"]  = market[col].pct_change(5)
            feats[f"{sector.lower()}_mom20d"] = market[col].pct_change(20)

    print(f"\n  Features de mercado adicionales: {feats.shape[1]}")
    return feats


def main():
    print("="*70)
    print("  EXPANSIÓN DE DATOS DE MERCADO — Yahoo Finance gratis")
    print("="*70)

    market_extras = build_market_features()
    if market_extras.empty:
        print("⚠ No se pudieron descargar features extras"); return

    print(f"\nProcesando {len(TICKERS)} tickers...")
    for ticker in TICKERS:
        raw_path = RAW_DIR / f"{ticker}_raw.parquet"
        if not raw_path.exists():
            print(f"  ⚠ No existe {raw_path}"); continue
        df_orig = pd.read_parquet(raw_path)
        df_new = df_orig.join(market_extras, how="left")
        df_new[market_extras.columns] = df_new[market_extras.columns].ffill()
        df_new = df_new.dropna()
        out_path = OUT_DIR / f"{ticker}_raw_v3.parquet"
        df_new.to_parquet(out_path)
        n_extra = market_extras.shape[1]
        print(f"  ✓ {ticker}: {df_new.shape[0]} días × {df_new.shape[1]} cols (+{n_extra} extras)")

    print("\n✓ Datasets v3 listos en:", OUT_DIR)


if __name__ == "__main__":
    main()
