"""
================================================================================
FEATURE ENGINEERING V2 — Features avanzadas
================================================================================
Crea features nuevos a partir de las 61 existentes:
  - Rolling z-scores (normalizan a régimen actual)
  - Lags (información histórica explícita)
  - Cross-features (interacciones entre indicadores)
  - Rolling statistics adicionales (skew, kurtosis)
  - Regime indicators (volatilidad alta vs baja)

Output: parquets nuevos con ~120-150 features.
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import sys
import warnings
import numpy as np
import pandas as pd
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass

warnings.filterwarnings("ignore")

RAW_DIR = Path("tesis_ml_stocks/01_raw_datasets")
OUT_DIR = Path("tesis_ml_stocks/01_raw_datasets_v2")
OUT_DIR.mkdir(parents=True, exist_ok=True)

TICKERS = ["AAPL", "NVDA", "TSLA", "AMZN", "MSFT", "GOOGL", "META"]

# Features clave a las que aplicamos transformaciones (de los 61 originales)
KEY_FEATURES_RSI    = ["rsi_7", "rsi_14"]
KEY_FEATURES_VOL    = ["vol_5d", "vol_10d", "vol_20d", "vol_60d", "atr_norm"]
KEY_FEATURES_MOM    = ["mom_5d", "mom_10d", "mom_20d", "mom_60d"]
KEY_FEATURES_RET    = ["ret_1d", "ret_2d", "ret_3d", "ret_5d", "ret_10d"]
KEY_FEATURES_DIST   = ["dist_ma10", "dist_ma20", "dist_ma50", "dist_ma200"]
KEY_FEATURES_VOLUME = ["vol_ratio", "obv_ratio", "cmf_20", "mfi_14"]
KEY_FEATURES_MARKET = ["SP500_ret", "VIX", "VIX_norm", "VIX_change"]

EXCLUIR_COLS = {
    "raw_open", "raw_high", "raw_low", "raw_close", "raw_volume",
    "target", "r_forward", "umbral_buy", "umbral_sell",
}


def rolling_zscore(s: pd.Series, window: int = 60) -> pd.Series:
    """Z-score rodante: cuantos sigmas está la observación del régimen reciente."""
    mean = s.rolling(window, min_periods=window // 2).mean()
    std  = s.rolling(window, min_periods=window // 2).std()
    return (s - mean) / (std + 1e-8)


def rolling_rank_pct(s: pd.Series, window: int = 60) -> pd.Series:
    """Percentil rodante: 0-1, donde está la observación en su distribución reciente."""
    return s.rolling(window, min_periods=window // 2).rank(pct=True)


def lag_feature(s: pd.Series, lag: int) -> pd.Series:
    """Lag explícito."""
    return s.shift(lag)


def cross_feature(s1: pd.Series, s2: pd.Series) -> pd.Series:
    """Producto o ratio entre dos features."""
    return s1 * s2


def expand_features(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica transformaciones a un DataFrame con las 61 features básicas."""
    out = df.copy()
    feat_cols = [c for c in df.columns if c not in EXCLUIR_COLS]

    # ── 1. Rolling z-scores (60 y 252 días) para features clave ─────────────
    for f in (KEY_FEATURES_RSI + KEY_FEATURES_VOL + KEY_FEATURES_MOM +
              KEY_FEATURES_RET + KEY_FEATURES_DIST + KEY_FEATURES_VOLUME +
              ["macd_hist", "stoch_k", "williams_r"]):
        if f in df.columns:
            out[f"{f}_z60"]  = rolling_zscore(df[f], 60)
            out[f"{f}_z252"] = rolling_zscore(df[f], 252)

    # ── 2. Rolling rank percentile (60 días) ────────────────────────────────
    for f in KEY_FEATURES_VOL + KEY_FEATURES_MOM + ["rsi_14", "atr_norm"]:
        if f in df.columns:
            out[f"{f}_rank60"] = rolling_rank_pct(df[f], 60)

    # ── 3. Lags de retornos y momentum ──────────────────────────────────────
    for f in ["ret_1d", "ret_5d", "mom_5d", "mom_10d", "rsi_14",
              "stoch_k", "macd_hist"]:
        if f in df.columns:
            for lag in [1, 2, 3, 5, 10]:
                out[f"{f}_lag{lag}"] = lag_feature(df[f], lag)

    # ── 4. Interacciones (cross-features) ───────────────────────────────────
    # Volatilidad × momentum: detecta breakouts
    if "vol_20d" in df.columns and "mom_5d" in df.columns:
        out["vol20_x_mom5"] = df["vol_20d"] * df["mom_5d"]
    if "vol_20d" in df.columns and "ret_1d" in df.columns:
        out["vol20_x_ret1d"] = df["vol_20d"] * df["ret_1d"]

    # RSI × Momentum
    if "rsi_14" in df.columns and "mom_10d" in df.columns:
        out["rsi14_x_mom10"] = df["rsi_14"] * df["mom_10d"] / 100

    # VIX × volatilidad propia
    if "VIX_norm" in df.columns and "vol_20d" in df.columns:
        out["vix_x_vol20"] = df["VIX_norm"] * df["vol_20d"]

    # Distancia MA × RSI (señales de sobrecompra/sobreventa)
    if "dist_ma50" in df.columns and "rsi_14" in df.columns:
        out["distma50_x_rsi"] = df["dist_ma50"] * (df["rsi_14"] - 50) / 50

    # Volumen ratio × dirección
    if "vol_ratio" in df.columns and "ret_1d" in df.columns:
        out["volratio_x_ret1d"] = df["vol_ratio"] * np.sign(df["ret_1d"])

    # ── 5. Rolling statistics adicionales ───────────────────────────────────
    if "ret_1d" in df.columns:
        out["ret_skew_20"] = df["ret_1d"].rolling(20).skew()
        out["ret_kurt_20"] = df["ret_1d"].rolling(20).kurt()

    # ── 6. Regime indicators ───────────────────────────────────────────────
    # Régimen de volatilidad: alta/baja respecto al histórico de 252d
    if "vol_20d" in df.columns:
        vol_high = df["vol_20d"].rolling(252, min_periods=126).quantile(0.7)
        out["regime_vol_high"] = (df["vol_20d"] > vol_high).astype(float)

    # Régimen de tendencia: precio sobre MA200 vs debajo
    if "dist_ma200" in df.columns:
        out["regime_trend_up"] = (df["dist_ma200"] > 0).astype(float)

    # Régimen de VIX: VIX alto = stress
    if "VIX" in df.columns:
        vix_high = df["VIX"].rolling(252, min_periods=126).quantile(0.7)
        out["regime_vix_high"] = (df["VIX"] > vix_high).astype(float)

    # ── 7. Diferencias y aceleraciones ─────────────────────────────────────
    for f in ["rsi_14", "stoch_k", "macd_hist", "vol_ratio", "VIX"]:
        if f in df.columns:
            out[f"{f}_diff1"] = df[f].diff(1)
            out[f"{f}_diff5"] = df[f].diff(5)

    # ── 8. Limpieza: reemplazar inf con NaN ─────────────────────────────────
    out = out.replace([np.inf, -np.inf], np.nan)

    return out


def procesar(ticker: str):
    raw_path = RAW_DIR / f"{ticker}_raw.parquet"
    if not raw_path.exists():
        print(f"  ⚠ No existe {raw_path}")
        return None
    df = pd.read_parquet(raw_path)
    print(f"\n  {ticker}: original {df.shape[0]} días × {df.shape[1]} cols")

    df_new = expand_features(df)
    # Drop rows con NaN en las nuevas features
    df_new = df_new.dropna()
    print(f"    Expandido: {df_new.shape[0]} días × {df_new.shape[1]} cols "
          f"(+{df_new.shape[1] - df.shape[1]} features)")

    out_path = OUT_DIR / f"{ticker}_raw_v2.parquet"
    df_new.to_parquet(out_path)
    print(f"    Guardado → {out_path}")
    return df_new


def main():
    print("=" * 70)
    print("  FEATURE ENGINEERING V2 — Expansión de features")
    print("=" * 70)

    for ticker in TICKERS:
        procesar(ticker)

    print("\n✓ Todos los datasets v2 generados en:", OUT_DIR)


if __name__ == "__main__":
    main()
