"""
================================================================================
SCRIPT 3 — BUILD MODEL DATASETS
================================================================================
Lee los parquets crudos (Script 1) y las features recomendadas (Script 2),
luego genera los datasets finales listos para entrenar cada modelo.

Salida: tesis_ml_stocks/03_model_datasets/
    logistic_regression/
        experimento_A/  experimento_B/  experimento_C/
            {TICKER}_train.parquet
            {TICKER}_val.parquet
            {TICKER}_test.parquet

    xgboost/
        (misma estructura)

    lstm/
        lookback_20/  lookback_60/
            experimento_A/  experimento_B/  experimento_C/
                {TICKER}_X_train.npy  {TICKER}_y_train.npy  (+ val + test)

    cnn_lstm/
        lookback_20/  lookback_60/
            experimento_A/  experimento_B/  experimento_C/
                {TICKER}_X_train.npy  (shape: muestras × lookback × (features+5_OHLCV))

Ejecutar después del Script 2.
================================================================================
"""

import warnings
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler, MinMaxScaler

warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════════════════════

TICKERS      = ["AAPL", "NVDA", "TSLA", "AMZN", "MSFT", "GOOGL", "META"]
RAW_DIR      = Path("tesis_ml_stocks/01_raw_datasets")
VAL_DIR      = Path("tesis_ml_stocks/Validacion_B/consolidado")
OUTPUT_DIR   = Path("tesis_ml_stocks/03_model_datasets")

LOOKBACK_WINDOWS = [20, 60]

# Columnas OHLCV crudo para CNN-LSTM (normalización local por ventana)
OHLCV_COLS = ["raw_open", "raw_high", "raw_low", "raw_close", "raw_volume"]

# Experimentos: (nombre, train_start, train_end, val_start, val_end, test_start, test_end)
EXPERIMENTOS = {
    "A": {
        "desc":  "Máximo historial — Pandemia en validación",
        "train": ("2014-01-01", "2021-12-31"),
        "val":   ("2022-01-01", "2023-12-31"),
        "test":  ("2024-01-01", "2025-12-31"),
        "val_dir": Path("tesis_ml_stocks/Validacion_A/consolidado")
    },
    "B": {
        "desc":  "Ciclo completo post-COVID — RECOMENDADO",
        "train": ("2018-01-01", "2023-12-31"),
        "val":   ("2024-01-01", "2024-12-31"),
        "test":  ("2025-01-01", "2025-12-31"),
        "val_dir": Path("tesis_ml_stocks/Validacion_B/consolidado")
    },
    "C": {
        "desc":  "Era moderna — Robustez",
        "train": ("2020-01-01", "2023-12-31"),
        "val":   ("2024-01-01", "2024-12-31"),
        "test":  ("2025-01-01", "2025-12-31"),
        "val_dir": Path("tesis_ml_stocks/Validacion_C/consolidado")
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# CARGA DE FEATURES RECOMENDADAS
# ══════════════════════════════════════════════════════════════════════════════

def cargar_features_recomendadas(val_path: Path) -> dict:
    """
    Lee el CSV generado por el Script 2 con las features recomendadas por modelo.
    Retorna dict: {modelo: [lista de features]}
    """
    path = val_path / "features_recomendadas.csv"
    if not path.exists():
        raise FileNotFoundError(f"No se encontró {path}.")
    df = pd.read_csv(path)
    resultado = {}
    for col in df.columns:
        resultado[col] = df[col].dropna().tolist()
    return resultado


# ══════════════════════════════════════════════════════════════════════════════
# SPLIT TEMPORAL
# ══════════════════════════════════════════════════════════════════════════════

def split_temporal(df: pd.DataFrame, exp: dict):
    """Divide df en train/val/test según las fechas del experimento."""
    def corte(start, end):
        return df[(df.index >= start) & (df.index <= end)]
    return (
        corte(*exp["train"]),
        corte(*exp["val"]),
        corte(*exp["test"]),
    )


# ══════════════════════════════════════════════════════════════════════════════
# ESCALADO (fit solo en train)
# ══════════════════════════════════════════════════════════════════════════════

def escalar(tr, va, te, feat_cols, metodo):
    """
    metodo = 'standard' → StandardScaler para Regresión Logística
    metodo = 'minmax'   → MinMaxScaler [0,1] para LSTM y CNN-LSTM
    XGBoost no escala.

    CRÍTICO: el scaler se ajusta SOLO con train. Val y test solo se transforman.
    """
    scaler = StandardScaler() if metodo == "standard" else MinMaxScaler()

    tr_s = tr.copy(); tr_s[feat_cols] = scaler.fit_transform(tr[feat_cols])
    va_s = va.copy(); va_s[feat_cols] = scaler.transform(va[feat_cols])
    te_s = te.copy(); te_s[feat_cols] = scaler.transform(te[feat_cols])
    return tr_s, va_s, te_s, scaler


# ══════════════════════════════════════════════════════════════════════════════
# NORMALIZACIÓN LOCAL DE OHLCV (para CNN-LSTM)
# ══════════════════════════════════════════════════════════════════════════════

def normalizar_ohlcv_local(ventanas: np.ndarray) -> np.ndarray:
    """
    ventanas: shape (n, lookback, 5) — columnas: open, high, low, close, volume

    Normalización DENTRO de cada ventana:
    - Precios (open, high, low, close): dividir entre close del primer día de la ventana.
      Resultado: todos los precios son relativos al inicio de la ventana.
    - Volume: dividir entre el volumen máximo de la ventana.
      Resultado: [0, 1] dentro de cada ventana.

    Por qué normalización local y no global (MinMaxScaler):
    - El CNN aprende patrones de forma de velas (mecha larga, doji, engulfing).
      Esos patrones son relativos, no absolutos.
    - AAPL a 170 USD y NVDA a 800 USD no son comparables en escala absoluta.
    - La normalización local preserva exactamente la geometría de cada vela.
    """
    arr = ventanas.astype(float).copy()
    primer_close = arr[:, 0:1, 3:4]                           # shape (n, 1)
    arr[:, :, :4] = arr[:, :, :4] / (primer_close + 1e-8)  # precios relativos
    max_vol = arr[:, :, 4].max(axis=1, keepdims=True)       # shape (n, 1)
    arr[:, :, 4] = arr[:, :, 4] / (max_vol + 1e-8)         # volumen [0,1]
    return arr


# ══════════════════════════════════════════════════════════════════════════════
# CONSTRUCCIÓN DE SECUENCIAS
# ══════════════════════════════════════════════════════════════════════════════

def construir_lstm(feat_arr: np.ndarray, target_arr: np.ndarray,
                   lookback: int):
    """
    feat_arr:   (n_dias, n_features)  — features escaladas
    target_arr: (n_dias,)

    Retorna:
        X: (n_muestras, lookback, n_features)
        y: (n_muestras,)

    X[i] = ventana [i, i+lookback), y[i] = target del día i+lookback.
    Sin lookahead: la ventana no incluye el día a predecir.
    """
    X, y = [], []
    for i in range(lookback, len(feat_arr)):
        X.append(feat_arr[i - lookback:i])
        y.append(target_arr[i])
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.int32)


def construir_cnn_lstm(feat_arr: np.ndarray, ohlcv_arr: np.ndarray,
                       target_arr: np.ndarray, lookback: int):
    """
    Igual que LSTM pero concatena canales OHLCV normalizados localmente.

    feat_arr:   (n_dias, n_features)  — features escaladas (MinMaxScaler global)
    ohlcv_arr:  (n_dias, 5)           — OHLCV crudo (se normaliza localmente)

    Retorna:
        X: (n_muestras, lookback, n_features + 5)
        y: (n_muestras,)

    Las últimas 5 columnas de X son OHLCV normalizados por ventana:
        [...features_calculadas..., open_rel, high_rel, low_rel, close_rel, vol_norm]
    """
    X_feat, X_ohlcv, y = [], [], []
    for i in range(lookback, len(feat_arr)):
        X_feat.append(feat_arr[i - lookback:i])
        X_ohlcv.append(ohlcv_arr[i - lookback:i])
        y.append(target_arr[i])

    X_feat  = np.array(X_feat,  dtype=np.float32)
    X_ohlcv = np.array(X_ohlcv, dtype=np.float32)
    y       = np.array(y,        dtype=np.int32)

    X_ohlcv_norm = normalizar_ohlcv_local(X_ohlcv).astype(np.float32)
    X_final = np.concatenate([X_feat, X_ohlcv_norm], axis=2)
    return X_final, y


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO LR
# ══════════════════════════════════════════════════════════════════════════════

def procesar_lr(ticker, df_raw, feat_cols, exp_id, exp):
    """Genera parquets escalados con StandardScaler para Regresión Logística."""
    dir_out = OUTPUT_DIR / "logistic_regression" / f"experimento_{exp_id}"
    dir_out.mkdir(parents=True, exist_ok=True)

    cols_usar = [c for c in feat_cols if c in df_raw.columns]
    df = df_raw[cols_usar + ["target"]].dropna()

    tr, va, te = split_temporal(df, exp)
    if len(tr) < 50:
        return None

    tr_s, va_s, te_s, _ = escalar(tr, va, te, cols_usar, "standard")

    tr_s.to_parquet(dir_out / f"{ticker}_train.parquet")
    va_s.to_parquet(dir_out / f"{ticker}_val.parquet")
    te_s.to_parquet(dir_out / f"{ticker}_test.parquet")

    return {"train": len(tr_s), "val": len(va_s), "test": len(te_s),
            "n_features": len(cols_usar)}


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO XGBoost
# ══════════════════════════════════════════════════════════════════════════════

def procesar_xgb(ticker, df_raw, feat_cols, exp_id, exp):
    """Genera parquets SIN escalar para XGBoost (los árboles no necesitan escala)."""
    dir_out = OUTPUT_DIR / "xgboost" / f"experimento_{exp_id}"
    dir_out.mkdir(parents=True, exist_ok=True)

    cols_usar = [c for c in feat_cols if c in df_raw.columns]
    df = df_raw[cols_usar + ["target"]].dropna()

    tr, va, te = split_temporal(df, exp)
    if len(tr) < 50:
        return None

    tr.to_parquet(dir_out / f"{ticker}_train.parquet")
    va.to_parquet(dir_out / f"{ticker}_val.parquet")
    te.to_parquet(dir_out / f"{ticker}_test.parquet")

    return {"train": len(tr), "val": len(va), "test": len(te),
            "n_features": len(cols_usar)}


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO LSTM
# ══════════════════════════════════════════════════════════════════════════════

def procesar_lstm(ticker, df_raw, feat_cols, exp_id, exp, lookback):
    """Genera arrays .npy de secuencias para LSTM."""
    dir_out = OUTPUT_DIR / "lstm" / f"lookback_{lookback}" / f"experimento_{exp_id}"
    dir_out.mkdir(parents=True, exist_ok=True)

    cols_usar = [c for c in feat_cols if c in df_raw.columns]
    df = df_raw[cols_usar + ["target"]].dropna()

    tr, va, te = split_temporal(df, exp)
    if len(tr) < lookback + 50:
        return None

    tr_s, va_s, te_s, _ = escalar(tr, va, te, cols_usar, "minmax")

    for split_name, split_df in [("train", tr_s), ("val", va_s), ("test", te_s)]:
        X, y = construir_lstm(split_df[cols_usar].values, split_df["target"].values, lookback)
        np.save(dir_out / f"{ticker}_X_{split_name}.npy", X)
        np.save(dir_out / f"{ticker}_y_{split_name}.npy", y)

    X_tr, y_tr = construir_lstm(tr_s[cols_usar].values, tr_s["target"].values, lookback)
    return {"train": len(X_tr), "shape": X_tr.shape, "n_features": len(cols_usar)}


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO CNN-LSTM
# ══════════════════════════════════════════════════════════════════════════════

def procesar_cnn_lstm(ticker, df_raw, feat_cols, exp_id, exp, lookback):
    """
    Genera arrays .npy para CNN-LSTM.
    Shape final: (muestras, lookback, n_features + 5)
    Las últimas 5 columnas son OHLCV normalizados localmente por ventana.
    """
    dir_out = OUTPUT_DIR / "cnn_lstm" / f"lookback_{lookback}" / f"experimento_{exp_id}"
    dir_out.mkdir(parents=True, exist_ok=True)

    cols_usar = [c for c in feat_cols if c in df_raw.columns]

    # Verificar que los OHLCV crudos estén disponibles
    ohlcv_disponibles = [c for c in OHLCV_COLS if c in df_raw.columns]
    if len(ohlcv_disponibles) < 5:
        print(f"      ⚠ OHLCV crudo no disponible para {ticker}, omitiendo CNN-LSTM.")
        return None

    df = df_raw[cols_usar + ohlcv_disponibles + ["target"]].dropna()
    tr, va, te = split_temporal(df, exp)
    if len(tr) < lookback + 50:
        return None

    # Escalar features calculadas (MinMaxScaler global, fit en train)
    tr_s, va_s, te_s, _ = escalar(tr, va, te, cols_usar, "minmax")

    for split_name, split_df in [("train", tr_s), ("val", va_s), ("test", te_s)]:
        X, y = construir_cnn_lstm(
            feat_arr   = split_df[cols_usar].values,
            ohlcv_arr  = split_df[ohlcv_disponibles].values,
            target_arr = split_df["target"].values,
            lookback   = lookback,
        )
        np.save(dir_out / f"{ticker}_X_{split_name}.npy", X)
        np.save(dir_out / f"{ticker}_y_{split_name}.npy", y)

    X_tr, y_tr = construir_cnn_lstm(
        tr_s[cols_usar].values, tr_s[ohlcv_disponibles].values,
        tr_s["target"].values, lookback
    )
    return {
        "train": len(X_tr),
        "shape": X_tr.shape,
        "n_features_calculadas": len(cols_usar),
        "n_canales_ohlcv": 5,
        "n_canales_total": len(cols_usar) + 5,
    }


# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

def pipeline():
    print("=" * 70)
    print("  SCRIPT 3 — BUILD MODEL DATASETS")
    print("=" * 70)
    
    resumen = []
    

    for ticker in TICKERS:
        raw_path = RAW_DIR / f"{ticker}_raw.parquet"
        if not raw_path.exists():
            print(f"\n⚠ No se encontró {raw_path}, omitiendo {ticker}.")
            continue

        df_raw = pd.read_parquet(raw_path)

        print(f"\n{'═'*60}")
        print(f"  {ticker}  ({len(df_raw)} días disponibles)")
        print(f"{'═'*60}")

        for exp_id, exp in EXPERIMENTOS.items():
            print(f"\n  Experimento {exp_id}: {exp['desc']}")
            try:
                features_por_modelo = cargar_features_recomendadas(exp["val_dir"])
            except FileNotFoundError as e:
                print(f"    ⚠ {e} Omitiendo experimento.")
                continue

            # ── Regresión Logística ────────────────────────────────────────
            feats_lr = features_por_modelo.get("Logistica", [])
            res_lr = procesar_lr(ticker, df_raw, feats_lr, exp_id, exp)
            if res_lr:
                print(f"    [LR ]  train={res_lr['train']:5d}  val={res_lr['val']:4d}  "
                      f"test={res_lr['test']:4d}  feat={res_lr['n_features']}")
            else:
                print(f"    [LR ]  ⚠ datos insuficientes")

            # ── XGBoost ───────────────────────────────────────────────────
            feats_xgb = features_por_modelo.get("XGBoost", [])
            res_xgb = procesar_xgb(ticker, df_raw, feats_xgb, exp_id, exp)
            if res_xgb:
                print(f"    [XGB]  train={res_xgb['train']:5d}  val={res_xgb['val']:4d}  "
                      f"test={res_xgb['test']:4d}  feat={res_xgb['n_features']}")
            else:
                print(f"    [XGB]  ⚠ datos insuficientes")

            # ── LSTM y CNN-LSTM por lookback ───────────────────────────────
            feats_lstm    = features_por_modelo.get("LSTM", [])
            feats_cnn     = features_por_modelo.get("CNN_LSTM", [])

            for lb in LOOKBACK_WINDOWS:
                res_lstm = procesar_lstm(ticker, df_raw, feats_lstm, exp_id, exp, lb)
                if res_lstm:
                    print(f"    [LSTM lb={lb:2d}]  train={res_lstm['train']:5d}  "
                          f"shape={res_lstm['shape']}  feat={res_lstm['n_features']}")
                else:
                    print(f"    [LSTM lb={lb:2d}]  ⚠ datos insuficientes")

                res_cnn = procesar_cnn_lstm(ticker, df_raw, feats_cnn, exp_id, exp, lb)
                if res_cnn:
                    print(f"    [CNN  lb={lb:2d}]  train={res_cnn['train']:5d}  "
                          f"shape={res_cnn['shape']}  "
                          f"({res_cnn['n_features_calculadas']} feat + 5 OHLCV)")
                else:
                    print(f"    [CNN  lb={lb:2d}]  ⚠ datos insuficientes")

            resumen.append({
                "ticker": ticker, "experimento": exp_id,
                "lr_train":  res_lr["train"]  if res_lr  else 0,
                "xgb_train": res_xgb["train"] if res_xgb else 0,
            })

    # Guardar resumen
    pd.DataFrame(resumen).to_csv(OUTPUT_DIR / "resumen_model_datasets.csv", index=False)

    print("\n" + "=" * 70)
    print("✓ Todos los datasets de modelos generados.")
    print(f"✓ Guardados en: {OUTPUT_DIR.resolve()}")
    print("""
Estructura de carpetas:
  tesis_ml_stocks/03_model_datasets/
  ├── logistic_regression/
  │   └── experimento_[A|B|C]/
  │       └── {TICKER}_[train|val|test].parquet   ← StandardScaler
  ├── xgboost/
  │   └── experimento_[A|B|C]/
  │       └── {TICKER}_[train|val|test].parquet   ← sin escalar
  ├── lstm/
  │   └── lookback_[20|60]/
  │       └── experimento_[A|B|C]/
  │           ├── {TICKER}_X_train.npy  ← shape (n, lb, n_feat)
  │           └── {TICKER}_y_train.npy  ← shape (n,)
  └── cnn_lstm/
      └── lookback_[20|60]/
          └── experimento_[A|B|C]/
              ├── {TICKER}_X_train.npy  ← shape (n, lb, n_feat+5)
              └── {TICKER}_y_train.npy  ← shape (n,)
    """)


if __name__ == "__main__":
    pipeline()
