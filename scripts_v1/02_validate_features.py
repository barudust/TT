"""
================================================================================
SCRIPT 2 — FEATURE VALIDATION
================================================================================
Lee los parquets generados por el Script 1 y aplica el método de validación
estadística apropiado para cada modelo:

    Regresión Logística → Pearson + VIF
    XGBoost             → SHAP values
    LSTM                → Spearman
    CNN-LSTM            → Spearman + autocorrelación por lag

Salida: tesis_ml_stocks/02_feature_validation/
    lr/          → correlaciones Pearson, VIF, gráficas
    xgboost/     → importancias SHAP, gráficas
    lstm/        → correlaciones Spearman, gráficas
    cnn_lstm/    → Spearman + autocorrelación, gráficas
    consolidado/ → tabla resumen y features recomendadas por modelo

Ejecutar después de Script 1.
Instalar: pip install scikit-learn xgboost shap matplotlib seaborn pyarrow scipy
================================================================================
"""

import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats

warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════════════════════

TICKERS      = ["AAPL", "NVDA", "TSLA", "AMZN", "MSFT", "GOOGL", "META"]
INPUT_DIR    = Path("tesis_ml_stocks/01_raw_datasets")
OUTPUT_DIR   = Path("tesis_ml_stocks/02_feature_validation")

# Período de entrenamiento del Experimento B para validación
# (solo se validan features sobre el split de entrenamiento para evitar leakage)
TRAIN_START  = "2020-01-01"
TRAIN_END    = "2023-12-31"

# Umbrales de decisión
P_VALOR_UMBRAL   = 0.05    # p-value máximo para Pearson y Spearman
VIF_UMBRAL       = 10.0    # VIF máximo aceptable para LR
SHAP_TOP_N       = 20      # Features a reportar en SHAP
CONSENSO_MINIMO  = 3       # Mínimo de tickers (de 7) para que una feature sea recomendada

# Columnas que NO son features (OHLCV crudo + columnas de target)
EXCLUIR_COLS = {
    "raw_open", "raw_high", "raw_low", "raw_close", "raw_volume",
    "target", "r_forward", "umbral_buy", "umbral_sell",
}

for sub in ["lr", "xgboost", "lstm", "cnn_lstm", "consolidado"]:
    (OUTPUT_DIR / sub).mkdir(parents=True, exist_ok=True)

# ══════════════════════════════════════════════════════════════════════════════
# UTILIDADES
# ══════════════════════════════════════════════════════════════════════════════

def cargar_train(ticker: str) -> pd.DataFrame:
    """Carga el parquet crudo y filtra al período de entrenamiento."""
    path = INPUT_DIR / f"{ticker}_raw.parquet"
    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró {path}. Ejecuta primero 01_build_raw_dataset.py")
    df = pd.read_parquet(path)
    mask = (df.index >= TRAIN_START) & (df.index <= TRAIN_END)
    return df[mask]


def get_feature_cols(df: pd.DataFrame) -> list:
    """Retorna las columnas de features (excluye OHLCV crudo y columnas de target)."""
    return [c for c in df.columns if c not in EXCLUIR_COLS]


def guardar_fig(fig, ruta: Path):
    fig.savefig(ruta, dpi=120, bbox_inches="tight")
    plt.close(fig)


PALETA = sns.diverging_palette(220, 20, as_cmap=True)


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 1 — REGRESIÓN LOGÍSTICA: PEARSON + VIF
# ══════════════════════════════════════════════════════════════════════════════

def calcular_vif(X: pd.DataFrame) -> pd.DataFrame:
    """
    VIF de cada feature mediante regresión OLS.
    VIF = 1 / (1 - R²) donde R² es de predecir esa feature con las demás.
    VIF > 10 indica multicolinealidad problemática.
    """
    from sklearn.linear_model import LinearRegression
    cols = X.columns.tolist()
    vif_rows = []
    arr = X.values
    for i, col in enumerate(cols):
        y_i   = arr[:, i]
        X_rest = np.delete(arr, i, axis=1)
        r2    = LinearRegression().fit(X_rest, y_i).score(X_rest, y_i)
        vif   = 1.0 / (1.0 - r2) if r2 < 1.0 else np.inf
        vif_rows.append({"feature": col, "vif": round(vif, 3)})
    return pd.DataFrame(vif_rows).sort_values("vif", ascending=False)


def validar_lr(ticker: str) -> dict:
    """Pearson vs target + VIF inter-features."""
    print(f"    [LR] {ticker}...", end=" ", flush=True)
    df   = cargar_train(ticker)
    feat_cols = get_feature_cols(df)
    X    = df[feat_cols].dropna()
    y    = df.loc[X.index, "target"]

    # Pearson de cada feature vs target
    rows = []
    for col in feat_cols:
        r, p = stats.pearsonr(X[col], y)
        rows.append({"feature": col, "pearson_r": round(r, 4), "p_value": round(p, 5)})
    df_p = pd.DataFrame(rows).sort_values("pearson_r", key=abs, ascending=False)
    df_p["significativa"] = df_p["p_value"] < P_VALOR_UMBRAL

    # VIF
    df_vif = calcular_vif(X)
    df_vif["vif_ok"] = df_vif["vif"] <= VIF_UMBRAL

    sig  = set(df_p[df_p["significativa"]]["feature"])
    good = set(df_vif[df_vif["vif_ok"]]["feature"])
    recomendadas = sorted(sig & good)

    print(f"sig={len(sig)}, vif_ok={len(good)}, rec={len(recomendadas)}")

    # Figura
    fig, axes = plt.subplots(1, 2, figsize=(18, max(6, len(feat_cols) * 0.3)))
    fig.suptitle(f"Reg. Logística — Pearson + VIF — {ticker}", fontsize=12, fontweight="bold")

    colores = ["#e74c3c" if s else "#bdc3c7" for s in df_p["significativa"]]
    axes[0].barh(df_p["feature"][::-1], df_p["pearson_r"].abs()[::-1], color=colores[::-1])
    axes[0].set_title(f"|Pearson r| vs Target  (rojo = p<{P_VALOR_UMBRAL})")
    axes[0].set_xlabel("|r|")
    axes[0].tick_params(axis="y", labelsize=7)

    colores_vif = ["#2ecc71" if ok else "#e74c3c" for ok in df_vif.sort_values("vif")["vif_ok"]]
    axes[1].barh(df_vif.sort_values("vif")["feature"],
                 df_vif.sort_values("vif")["vif"], color=colores_vif)
    axes[1].axvline(VIF_UMBRAL, color="black", linestyle="--", linewidth=1, label=f"VIF={VIF_UMBRAL}")
    axes[1].set_title(f"VIF  (verde = ≤{VIF_UMBRAL}, rojo = problemático)")
    axes[1].set_xlabel("VIF")
    axes[1].tick_params(axis="y", labelsize=7)
    axes[1].legend()

    plt.tight_layout()
    guardar_fig(fig, OUTPUT_DIR / "lr" / f"{ticker}_lr.png")

    return {"ticker": ticker, "pearson": df_p, "vif": df_vif,
            "recomendadas": recomendadas, "n_features": len(feat_cols)}


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 2 — XGBOOST: SHAP
# ══════════════════════════════════════════════════════════════════════════════

def validar_xgb(ticker: str) -> dict:
    """Entrena XGBoost exploratorio y calcula SHAP mean |value| por feature."""
    try:
        import xgboost as xgb
        import shap
    except ImportError:
        print("      ⚠ Instala: pip install xgboost shap")
        return {}

    print(f"    [XGB] {ticker}...", end=" ", flush=True)
    df   = cargar_train(ticker)
    feat_cols = get_feature_cols(df)
    X    = df[feat_cols].dropna()
    y    = df.loc[X.index, "target"]

    model = xgb.XGBClassifier(
        n_estimators=300, max_depth=5, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.8,
        eval_metric="mlogloss", random_state=42,
        n_jobs=-1, verbosity=0,
    )
    model.fit(X, y)

    explainer = shap.TreeExplainer(model)
    sv = explainer.shap_values(X)

    # sv puede ser lista (multiclase) o array 3D
    if isinstance(sv, list):
        mean_abs = np.mean([np.abs(s).mean(axis=0) for s in sv], axis=0)
    elif sv.ndim == 3:
        mean_abs = np.abs(sv).mean(axis=(0, 2))
    else:
        mean_abs = np.abs(sv).mean(axis=0)

    df_shap = pd.DataFrame({
        "feature":      feat_cols,
        "shap_mean_abs": mean_abs,
    }).sort_values("shap_mean_abs", ascending=False).reset_index(drop=True)
    df_shap["rank"] = df_shap.index + 1

    recomendadas = df_shap.head(SHAP_TOP_N)["feature"].tolist()
    print(f"top {SHAP_TOP_N} de {len(feat_cols)}")

    # Figura
    top = df_shap.head(SHAP_TOP_N)
    fig, ax = plt.subplots(figsize=(10, max(6, SHAP_TOP_N * 0.4)))
    colores = ["#2ecc71"] * SHAP_TOP_N
    ax.barh(top["feature"][::-1], top["shap_mean_abs"][::-1], color=colores)
    ax.set_title(f"XGBoost SHAP — Top {SHAP_TOP_N} features — {ticker}", fontsize=11, fontweight="bold")
    ax.set_xlabel("Mean |SHAP value|")
    ax.tick_params(axis="y", labelsize=8)
    plt.tight_layout()
    guardar_fig(fig, OUTPUT_DIR / "xgboost" / f"{ticker}_xgb.png")

    return {"ticker": ticker, "shap": df_shap, "recomendadas": recomendadas}


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 3 — LSTM: SPEARMAN
# ══════════════════════════════════════════════════════════════════════════════

def validar_lstm(ticker: str) -> dict:
    """Correlación de Spearman de cada feature vs target."""
    print(f"    [LSTM] {ticker}...", end=" ", flush=True)
    df   = cargar_train(ticker)
    feat_cols = get_feature_cols(df)
    X    = df[feat_cols].dropna()
    y    = df.loc[X.index, "target"]

    rows = []
    for col in feat_cols:
        r, p = stats.spearmanr(X[col], y)
        rows.append({"feature": col, "spearman_rho": round(r, 4), "p_value": round(p, 5)})
    df_sp = pd.DataFrame(rows).sort_values("spearman_rho", key=abs, ascending=False)
    df_sp["significativa"] = df_sp["p_value"] < P_VALOR_UMBRAL
    recomendadas = df_sp[df_sp["significativa"]]["feature"].tolist()

    print(f"sig={len(recomendadas)} de {len(feat_cols)}")

    # Figura
    fig, ax = plt.subplots(figsize=(10, max(6, len(feat_cols) * 0.3)))
    colores = ["#3498db" if s else "#bdc3c7" for s in df_sp["significativa"]]
    ax.barh(df_sp["feature"][::-1], df_sp["spearman_rho"].abs()[::-1], color=colores[::-1])
    ax.set_title(f"LSTM — Spearman |ρ| vs Target — {ticker}\n"
                 f"(azul = p<{P_VALOR_UMBRAL})", fontsize=11, fontweight="bold")
    ax.set_xlabel("|ρ|")
    ax.tick_params(axis="y", labelsize=7)
    plt.tight_layout()
    guardar_fig(fig, OUTPUT_DIR / "lstm" / f"{ticker}_lstm.png")

    return {"ticker": ticker, "spearman": df_sp, "recomendadas": recomendadas}


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 4 — CNN-LSTM: SPEARMAN + AUTOCORRELACIÓN
# ══════════════════════════════════════════════════════════════════════════════

def validar_cnn_lstm(ticker: str) -> dict:
    """Spearman vs target + autocorrelación para justificar ventana de lookback."""
    print(f"    [CNN] {ticker}...", end=" ", flush=True)
    df   = cargar_train(ticker)
    feat_cols = get_feature_cols(df)
    X    = df[feat_cols].dropna()
    y    = df.loc[X.index, "target"]

    # Spearman
    rows = []
    for col in feat_cols:
        r, p = stats.spearmanr(X[col], y)
        rows.append({"feature": col, "spearman_rho": round(r, 4), "p_value": round(p, 5)})
    df_sp = pd.DataFrame(rows).sort_values("spearman_rho", key=abs, ascending=False)
    df_sp["significativa"] = df_sp["p_value"] < P_VALOR_UMBRAL
    recomendadas = df_sp[df_sp["significativa"]]["feature"].tolist()

    # Autocorrelación de las top 6 features
    top6 = df_sp.head(6)["feature"].tolist()
    max_lag = 65

    fig, axes = plt.subplots(2, 1, figsize=(12, 12))
    fig.suptitle(f"CNN-LSTM — {ticker}", fontsize=12, fontweight="bold")

    colores = ["#9b59b6" if s else "#bdc3c7" for s in df_sp["significativa"]]
    axes[0].barh(df_sp["feature"][::-1], df_sp["spearman_rho"].abs()[::-1], color=colores[::-1])
    axes[0].set_title(f"Spearman |ρ| vs Target  (morado = p<{P_VALOR_UMBRAL})")
    axes[0].set_xlabel("|ρ|")
    axes[0].tick_params(axis="y", labelsize=7)

    palette = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c"]
    for i, feat in enumerate(top6):
        ac_vals = [stats.spearmanr(X[feat].iloc[lag:], X[feat].iloc[:-lag])[0]
                   for lag in range(1, max_lag)]
        axes[1].plot(range(1, max_lag), np.abs(ac_vals),
                     marker="o", markersize=2, label=feat, color=palette[i])
    axes[1].axvline(20, color="orange", linestyle=":", linewidth=1.5, label="lookback=20")
    axes[1].axvline(60, color="red",    linestyle=":", linewidth=1.5, label="lookback=60")
    axes[1].axhline(0.05, color="gray", linestyle="--", linewidth=0.8, label="|ρ|=0.05")
    axes[1].set_title("Autocorrelación Spearman por lag — justifica ventana de lookback")
    axes[1].set_xlabel("Lag (días)")
    axes[1].set_ylabel("|ρ autocorrelación|")
    axes[1].legend(fontsize=8, ncol=2)
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    guardar_fig(fig, OUTPUT_DIR / "cnn_lstm" / f"{ticker}_cnn.png")
    print(f"sig={len(recomendadas)}")

    return {"ticker": ticker, "spearman": df_sp, "recomendadas": recomendadas}


# ══════════════════════════════════════════════════════════════════════════════
# CONSOLIDADO Y REPORTE FINAL
# ══════════════════════════════════════════════════════════════════════════════

def consolidar(resultados: dict):
    """
    Genera tabla de porcentaje de tickers que recomiendan cada feature
    y lista de features recomendadas por consenso mínimo.
    """
    print("\n  Generando consolidado...")

    modelos = list(resultados.keys())

    # Recopilar todas las features que aparecieron en algún modelo
    all_feats = set()
    for mod, ticker_dict in resultados.items():
        for ticker, res in ticker_dict.items():
            if res:
                all_feats.update(res.get("recomendadas", []))

    # Contar en cuántos tickers cada feature es recomendada por cada modelo
    rows = {}
    for feat in sorted(all_feats):
        rows[feat] = {}
        for mod in modelos:
            cnt = sum(
                1 for ticker, res in resultados[mod].items()
                if res and feat in res.get("recomendadas", [])
            )
            rows[feat][mod] = cnt

    df_conteo = pd.DataFrame(rows).T
    df_conteo.index.name = "feature"
    df_pct = (df_conteo / len(TICKERS) * 100).round(1)

    # Guardar
    df_conteo.to_csv(OUTPUT_DIR / "consolidado" / "conteo_tickers_por_feature.csv")
    df_pct.to_csv(OUTPUT_DIR / "consolidado" / "porcentaje_tickers_por_feature.csv")

    # Features recomendadas por consenso
    recomendaciones_finales = {}
    for mod in modelos:
        col = df_conteo.get(mod, pd.Series(dtype=int))
        rec = sorted(col[col >= CONSENSO_MINIMO].index.tolist())
        recomendaciones_finales[mod] = rec

    pd.DataFrame(
        {mod: pd.Series(feats) for mod, feats in recomendaciones_finales.items()}
    ).to_csv(OUTPUT_DIR / "consolidado" / "features_recomendadas.csv", index=False)

    # Heatmap consolidado
    if not df_pct.empty:
        fig, ax = plt.subplots(figsize=(max(8, len(modelos) * 2), max(10, len(df_pct) * 0.4)))
        sns.heatmap(df_pct, ax=ax, annot=True, fmt=".0f", cmap="YlGn",
                    linewidths=0.3, cbar_kws={"label": "% tickers"}, vmin=0, vmax=100)
        ax.set_title(
            f"% de tickers (de {len(TICKERS)}) que recomiendan cada feature — por modelo\n"
            f"(consenso mínimo = {CONSENSO_MINIMO} tickers)",
            fontsize=11, fontweight="bold"
        )
        ax.tick_params(axis="x", labelsize=9)
        ax.tick_params(axis="y", labelsize=7)
        plt.tight_layout()
        guardar_fig(fig, OUTPUT_DIR / "consolidado" / "heatmap_consolidado.png")

    return df_pct, recomendaciones_finales


# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

def pipeline():
    print("=" * 70)
    print("  SCRIPT 2 — FEATURE VALIDATION")
    print(f"  Período de validación: {TRAIN_START} → {TRAIN_END} (Exp. B train)")
    print(f"  Consenso mínimo: {CONSENSO_MINIMO} de {len(TICKERS)} tickers")
    print("=" * 70)

    resultados = {
        "Logistica": {},
        "XGBoost":   {},
        "LSTM":      {},
        "CNN_LSTM":  {},
    }

    for ticker in TICKERS:
        print(f"\n{'═'*55}")
        print(f"  {ticker}")
        print(f"{'═'*55}")
        try:
            resultados["Logistica"][ticker] = validar_lr(ticker)
            resultados["XGBoost"][ticker]   = validar_xgb(ticker)
            resultados["LSTM"][ticker]      = validar_lstm(ticker)
            resultados["CNN_LSTM"][ticker]  = validar_cnn_lstm(ticker)
        except FileNotFoundError as e:
            print(f"  ⚠ {e}")

    # Consolidado
    df_pct, recomendadas = consolidar(resultados)

    # Imprimir resumen
    print("\n" + "=" * 70)
    print("  FEATURES RECOMENDADAS POR MODELO")
    print(f"  (presentes en ≥{CONSENSO_MINIMO} de {len(TICKERS)} tickers)")
    print("=" * 70)
    for mod, feats in recomendadas.items():
        print(f"\n  {mod} ({len(feats)} features):")
        for f in feats:
            pct = df_pct.loc[f, mod] if f in df_pct.index and mod in df_pct.columns else 0
            print(f"    ✓ {f:<30} ({pct:.0f}% de tickers)")

    print(f"\n✓ Reportes guardados en: {OUTPUT_DIR.resolve()}")
    print("\nSiguiente paso → ejecutar 03_build_model_datasets.py")
    print("  (el script lee features_recomendadas.csv automáticamente)")


if __name__ == "__main__":
    pipeline()
