"""
================================================================================
SCRIPT 08 — EVALUACIÓN COMPARATIVA DE LOS 4 MODELOS
================================================================================
Lee los resultados de los 4 scripts de entrenamiento y genera:

1. Tabla comparativa completa (F1, precisión, recall por clase)
2. Métricas financieras de backtesting (Sharpe, drawdown, win rate, etc.)
3. Curvas de equity vs Buy & Hold
4. Visualizaciones de matrices de confusión

Este script es el que responde la pregunta central de la tesis:
¿qué modelo predice mejor las señales de trading diarias?

Salida: tesis_ml_stocks/05_evaluation/
    comparativa_clasificacion.csv
    comparativa_financiera.csv
    figuras/equity_curves_{ticker}.png
    figuras/confusion_matrices_{ticker}.png
    reporte_final.csv

Dependencias: pip install pandas numpy matplotlib seaborn scikit-learn pyarrow
================================================================================
"""

import json
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from pathlib import Path

warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════════════════════

TICKERS    = ["AAPL", "NVDA", "TSLA", "AMZN", "MSFT", "GOOGL", "META"]
MODELS_DIR = Path("tesis_ml_stocks/04_models")
RAW_DIR    = Path("tesis_ml_stocks/01_raw_datasets")
OUTPUT_DIR = Path("tesis_ml_stocks/05_evaluation")
(OUTPUT_DIR / "figuras").mkdir(parents=True, exist_ok=True)

EXPERIMENTO_PRINCIPAL = "B"   # Para los análisis financieros
CLASES  = [0, 1, 2]
NOMBRES = {0: "SELL", 1: "HOLD", 2: "BUY"}

# Período de prueba del experimento B
TEST_START = "2023-01-01"
TEST_END   = "2024-12-31"


# ══════════════════════════════════════════════════════════════════════════════
# MÉTRICAS FINANCIERAS
# ══════════════════════════════════════════════════════════════════════════════

def calcular_metricas_financieras(fechas, señales, retornos_reales,
                                  nombre_modelo: str) -> dict:
    """
    Calcula métricas financieras de backtesting dado un vector de señales
    y los retornos reales del día siguiente.

    Supuestos del backtesting:
    - BUY (2):  retorno del día = retorno_real
    - HOLD (1): retorno del día = 0 (no se opera)
    - SELL (0): retorno del día = -retorno_real (posición corta)
    - Sin costos de transacción (primera aproximación)
    - Capital inicial normalizado a 1.0
    """
    # Retorno de la estrategia según la señal
    ret_estrategia = np.where(señales == 2, retornos_reales,
                     np.where(señales == 0, -retornos_reales, 0.0))

    # Buy & Hold: siempre invertido
    ret_bh = retornos_reales

    # Equity acumulado (product de (1 + r) diario)
    equity_est = (1 + ret_estrategia).cumprod()
    equity_bh  = (1 + ret_bh).cumprod()

    # Retorno acumulado
    cumul_ret = equity_est[-1] - 1.0
    cumul_bh  = equity_bh[-1] - 1.0

    # Retorno vs Buy & Hold
    ret_vs_bh = cumul_ret - cumul_bh

    # Sharpe ratio (sin risk-free, anualizado)
    n_dias   = len(ret_estrategia)
    mean_ret = ret_estrategia.mean()
    std_ret  = ret_estrategia.std()
    sharpe   = (mean_ret / (std_ret + 1e-10)) * np.sqrt(252) if std_ret > 0 else 0.0

    # Maximum Drawdown
    peak     = np.maximum.accumulate(equity_est)
    drawdown = (equity_est - peak) / peak
    max_dd   = drawdown.min()

    # Calmar ratio
    calmar = (cumul_ret / abs(max_dd)) if abs(max_dd) > 0 else 0.0

    # Win Rate: % de días donde se operó y se ganó
    dias_operados = (señales != 1)
    if dias_operados.sum() > 0:
        ganancias = ret_estrategia[dias_operados] > 0
        win_rate  = ganancias.mean()
    else:
        win_rate = 0.0

    # Profit Factor: suma ganancias / suma pérdidas (en días operados)
    ret_ops = ret_estrategia[dias_operados]
    sum_gan = ret_ops[ret_ops > 0].sum()
    sum_per = abs(ret_ops[ret_ops < 0].sum())
    profit_factor = (sum_gan / sum_per) if sum_per > 0 else np.inf

    # Retorno promedio por trade (cada cambio de señal = un trade)
    cambios = np.diff(señales, prepend=señales[0]) != 0
    n_trades = cambios.sum()
    avg_ret_trade = (ret_estrategia[dias_operados].sum() / n_trades
                     if n_trades > 0 else 0.0)

    return {
        "modelo":           nombre_modelo,
        "cumul_return":     round(float(cumul_ret * 100), 2),
        "cumul_bh":         round(float(cumul_bh * 100), 2),
        "return_vs_bh":     round(float(ret_vs_bh * 100), 2),
        "sharpe":           round(float(sharpe), 3),
        "max_drawdown":     round(float(max_dd * 100), 2),
        "calmar":           round(float(calmar), 3),
        "win_rate":         round(float(win_rate * 100), 2),
        "profit_factor":    round(float(profit_factor), 3),
        "n_trades":         int(n_trades),
        "avg_ret_trade":    round(float(avg_ret_trade * 100), 4),
        "n_dias":           int(n_dias),
        "equity_est":       equity_est.tolist(),
        "equity_bh":        equity_bh.tolist(),
        "fechas":           [str(f) for f in fechas],
    }


# ══════════════════════════════════════════════════════════════════════════════
# CARGA DE PREDICCIONES
# ══════════════════════════════════════════════════════════════════════════════

def cargar_predicciones_lr(ticker, exp_id="B", tipo="por_ticker"):
    """Regenera predicciones de LR cargando el modelo guardado."""
    import pickle
    if tipo == "por_ticker":
        base = MODELS_DIR / "logistic_regression" / "por_ticker" / f"experimento_{exp_id}"
        modelo_path = base / f"{ticker}_modelo.pkl"
    else:
        base = MODELS_DIR / "logistic_regression" / "global" / f"experimento_{exp_id}"
        modelo_path = base / "modelo_global.pkl"

    if not modelo_path.exists():
        return None

    from tesis_ml_stocks.scripts import load_lr_test_data
    # Se carga el parquet de test y se aplica el modelo
    test_path = (Path("tesis_ml_stocks/03_model_datasets/logistic_regression") /
                 f"experimento_{exp_id}" / f"{ticker}_test.parquet")
    if not test_path.exists():
        return None

    df = pd.read_parquet(test_path)
    feat_cols = [c for c in df.columns if c != "target"]
    X = df[feat_cols].values
    y_true = df["target"].values

    with open(modelo_path, "rb") as f:
        modelo = pickle.load(f)

    return modelo.predict(X), y_true


def cargar_predicciones_xgb(ticker, exp_id="B", tipo="por_ticker"):
    """Carga modelo XGBoost y genera predicciones en test."""
    try:
        import xgboost as xgb
    except ImportError:
        return None

    if tipo == "por_ticker":
        base = MODELS_DIR / "xgboost" / "por_ticker" / f"experimento_{exp_id}"
        modelo_path = base / f"{ticker}_modelo.json"
    else:
        base = MODELS_DIR / "xgboost" / "global" / f"experimento_{exp_id}"
        modelo_path = base / "modelo_global.json"

    test_path = (Path("tesis_ml_stocks/03_model_datasets/xgboost") /
                 f"experimento_{exp_id}" / f"{ticker}_test.parquet")

    if not modelo_path.exists() or not test_path.exists():
        return None

    df = pd.read_parquet(test_path)
    feat_cols = [c for c in df.columns if c != "target"]
    X = df[feat_cols].values; y_true = df["target"].values

    modelo = xgb.XGBClassifier()
    modelo.load_model(str(modelo_path))
    return modelo.predict(X), y_true


def cargar_predicciones_lstm(ticker, exp_id="B", lookback=20, tipo="por_ticker"):
    """Carga checkpoint LSTM y genera predicciones en test."""
    try:
        import torch
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from tesis_train_06_train_lstm import LSTMClasificador
    except ImportError:
        return None

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if tipo == "por_ticker":
        base = MODELS_DIR / "lstm" / "por_ticker" / f"lookback_{lookback}" / f"experimento_{exp_id}"
        ckpt_path = base / f"{ticker}_checkpoint.pt"
    else:
        base = MODELS_DIR / "lstm" / "global" / f"lookback_{lookback}" / f"experimento_{exp_id}"
        ckpt_path = base / "modelo_global_checkpoint.pt"

    npy_base = (Path("tesis_ml_stocks/03_model_datasets/lstm") /
                f"lookback_{lookback}" / f"experimento_{exp_id}")
    X_te = np.load(npy_base / f"{ticker}_X_test.npy")
    y_te = np.load(npy_base / f"{ticker}_y_test.npy")

    if not ckpt_path.exists():
        return None

    ckpt   = torch.load(ckpt_path, map_location=device)
    modelo = LSTMClasificador(input_size=ckpt["input_size"],
                              hidden_size=ckpt["hidden_size"],
                              n_layers=ckpt["n_layers"],
                              dropout=ckpt["dropout"]).to(device)
    modelo.load_state_dict(ckpt["state_dict"])
    modelo.eval()

    with torch.no_grad():
        Xt = torch.FloatTensor(X_te).to(device)
        preds = torch.argmax(modelo(Xt), dim=1).cpu().numpy()
    return preds, y_te


def cargar_predicciones_cnn_lstm(ticker, exp_id="B", lookback=20, tipo="por_ticker"):
    """Carga checkpoint CNN-LSTM y genera predicciones en test."""
    try:
        import torch
        from tesis_train_07_train_cnn_lstm import CNNLSTMClasificador
    except ImportError:
        return None

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if tipo == "por_ticker":
        base = MODELS_DIR / "cnn_lstm" / "por_ticker" / f"lookback_{lookback}" / f"experimento_{exp_id}"
        ckpt_path = base / f"{ticker}_checkpoint.pt"
    else:
        base = MODELS_DIR / "cnn_lstm" / "global" / f"lookback_{lookback}" / f"experimento_{exp_id}"
        ckpt_path = base / "modelo_global_checkpoint.pt"

    npy_base = (Path("tesis_ml_stocks/03_model_datasets/cnn_lstm") /
                f"lookback_{lookback}" / f"experimento_{exp_id}")
    X_te = np.load(npy_base / f"{ticker}_X_test.npy")
    y_te = np.load(npy_base / f"{ticker}_y_test.npy")

    if not ckpt_path.exists():
        return None

    ckpt   = torch.load(ckpt_path, map_location=device)
    modelo = CNNLSTMClasificador(**ckpt["config"]).to(device)
    modelo.load_state_dict(ckpt["state_dict"])
    modelo.eval()

    with torch.no_grad():
        Xt = torch.FloatTensor(X_te).to(device)
        preds = torch.argmax(modelo(Xt), dim=1).cpu().numpy()
    return preds, y_te


# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICAS
# ══════════════════════════════════════════════════════════════════════════════

COLORES_MODELO = {
    "LR":        "#3498db",
    "XGBoost":   "#2ecc71",
    "LSTM-20":   "#e74c3c",
    "LSTM-60":   "#c0392b",
    "CNN-20":    "#9b59b6",
    "CNN-60":    "#6c3483",
    "BH":        "#888888",
}


def graficar_equity_curves(resultados_fin, ticker, dir_out):
    """Curvas de equity de todos los modelos vs Buy & Hold para un ticker."""
    modelos_con_datos = [(nm, r) for nm, r in resultados_fin.items()
                         if r and "equity_est" in r]
    if not modelos_con_datos:
        return

    fig, ax = plt.subplots(figsize=(14, 6))
    n_dias = max(len(r["fechas"]) for _, r in modelos_con_datos)

    # Buy & Hold (solo una vez, todos coinciden)
    _, r0 = modelos_con_datos[0]
    fechas = r0["fechas"]
    ax.plot(range(len(r0["equity_bh"])), r0["equity_bh"],
            color=COLORES_MODELO["BH"], linewidth=1.5, linestyle="--",
            label=f"Buy & Hold ({r0['cumul_bh']:.1f}%)", alpha=0.7)

    for nombre, r in modelos_con_datos:
        color = COLORES_MODELO.get(nombre, "#333333")
        ax.plot(range(len(r["equity_est"])), r["equity_est"],
                color=color, linewidth=1.8,
                label=f"{nombre} ({r['cumul_return']:.1f}%)")

    ax.axhline(1.0, color="black", linewidth=0.5, linestyle=":")
    ax.set_title(f"Curvas de Equity — {ticker} — Período de Prueba",
                 fontsize=12, fontweight="bold")
    ax.set_xlabel("Días de trading")
    ax.set_ylabel("Equity (capital inicial = 1.0)")
    ax.legend(fontsize=9, ncol=2)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    fig.savefig(dir_out / f"equity_{ticker}.png", dpi=120, bbox_inches="tight")
    plt.close(fig)


def graficar_confusion_matrices(predicciones_dict, ticker, dir_out):
    """Matrices de confusión de los modelos disponibles para un ticker."""
    modelos = [(nm, p) for nm, p in predicciones_dict.items() if p is not None]
    if not modelos:
        return

    n = len(modelos)
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 5))
    if n == 1:
        axes = [axes]
    fig.suptitle(f"Matrices de Confusión — {ticker}", fontsize=12, fontweight="bold")

    for ax, (nombre, (y_pred, y_true)) in zip(axes, modelos):
        cm = pd.DataFrame(
            [[((y_pred == i) & (y_true == j)).sum() for j in CLASES] for i in CLASES],
            index=["Pred SELL","Pred HOLD","Pred BUY"],
            columns=["Real SELL","Real HOLD","Real BUY"],
        )
        sns.heatmap(cm, ax=ax, annot=True, fmt="d", cmap="Blues",
                    linewidths=0.5, cbar=False)
        ax.set_title(nombre, fontsize=10, fontweight="bold")
        ax.tick_params(axis="both", labelsize=8)

    plt.tight_layout()
    fig.savefig(dir_out / f"confusion_{ticker}.png", dpi=120, bbox_inches="tight")
    plt.close(fig)


def graficar_f1_comparativa(df_clas, dir_out):
    """Gráfica comparativa de F1-macro por modelo y ticker."""
    fig, ax = plt.subplots(figsize=(14, 7))

    pivot = df_clas.pivot_table(
        index="ticker", columns="modelo", values="test_f1_macro", aggfunc="max")
    pivot.plot(kind="bar", ax=ax, colormap="tab10", edgecolor="none", width=0.7)

    ax.axhline(0.33, color="red", linestyle="--", linewidth=1, label="Línea base (1/3)")
    ax.set_title("F1-Macro en Test por Modelo y Ticker",
                 fontsize=12, fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("F1-Macro")
    ax.tick_params(axis="x", rotation=0)
    ax.legend(title="Modelo", fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(0, 1)
    plt.tight_layout()
    fig.savefig(dir_out / "f1_comparativa_por_ticker.png", dpi=120, bbox_inches="tight")
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# CARGA CONSOLIDADA DE RESULTADOS
# ══════════════════════════════════════════════════════════════════════════════

def cargar_todos_los_json():
    """Lee todos los archivos metricas.json y los consolida."""
    registros = []
    patrones = [
        ("LR",       "logistic_regression"),
        ("XGBoost",  "xgboost"),
        ("LSTM",     "lstm"),
        ("CNN-LSTM", "cnn_lstm"),
    ]

    for nombre_modelo, carpeta in patrones:
        base = MODELS_DIR / carpeta
        for json_path in base.rglob("*metricas*.json"):
            try:
                with open(json_path) as f:
                    meta = json.load(f)
                met_t = meta.get("metricas_test", {})
                met_v = meta.get("metricas_val",  {})
                lb    = meta.get("lookback", "-")
                registros.append({
                    "modelo":       nombre_modelo,
                    "tipo":         meta.get("tipo", "?"),
                    "ticker":       meta.get("ticker", "?"),
                    "experimento":  meta.get("experimento", "?"),
                    "lookback":     lb,
                    "val_f1_macro":  met_v.get("f1_macro",  None),
                    "val_f1_buy":    met_v.get("f1_buy",    None),
                    "val_f1_sell":   met_v.get("f1_sell",   None),
                    "test_f1_macro": met_t.get("f1_macro",  None),
                    "test_f1_buy":   met_t.get("f1_buy",    None),
                    "test_f1_sell":  met_t.get("f1_sell",   None),
                    "test_accuracy": met_t.get("accuracy",  None),
                    "test_precision_buy":  met_t.get("precision_buy",  None),
                    "test_precision_sell": met_t.get("precision_sell", None),
                    "test_n_samples": met_t.get("n_samples", None),
                })
            except Exception as e:
                print(f"  ⚠ Error leyendo {json_path}: {e}")

    return pd.DataFrame(registros)


# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

def pipeline():
    print("="*65)
    print("  SCRIPT 08 — EVALUACIÓN COMPARATIVA")
    print("="*65)

    dir_fig = OUTPUT_DIR / "figuras"

    # ── 1. Consolidar métricas de clasificación ───────────────────────────
    print("\n[1/4] Cargando métricas de clasificación...")
    df_clas = cargar_todos_los_json()

    if df_clas.empty:
        print("  ⚠ No se encontraron archivos de métricas. "
              "Ejecuta los scripts 04-07 primero.")
        return

    df_clas.to_csv(OUTPUT_DIR / "comparativa_clasificacion.csv", index=False)
    print(f"  {len(df_clas)} registros cargados.")

    # ── 2. Tabla resumen ──────────────────────────────────────────────────
    print("\n[2/4] Generando tabla resumen...")
    resumen = (df_clas[df_clas["experimento"] == EXPERIMENTO_PRINCIPAL]
               .groupby(["modelo", "tipo", "lookback"])
               .agg(
                   f1_macro_mean  = ("test_f1_macro", "mean"),
                   f1_macro_std   = ("test_f1_macro", "std"),
                   f1_buy_mean    = ("test_f1_buy",   "mean"),
                   f1_sell_mean   = ("test_f1_sell",  "mean"),
               ).round(4).reset_index())

    print("\n  RESUMEN F1 PROMEDIO POR MODELO (Exp B, todos los tickers):")
    print(resumen.to_string(index=False))
    resumen.to_csv(OUTPUT_DIR / "resumen_f1_promedio.csv", index=False)

    # ── 3. Gráfica F1 comparativa ─────────────────────────────────────────
    print("\n[3/4] Generando gráficas...")
    df_graf = df_clas[
        (df_clas["experimento"] == EXPERIMENTO_PRINCIPAL) &
        (df_clas["tipo"] == "por_ticker") &
        (df_clas["ticker"] != "GLOBAL")
    ].copy()

    if not df_graf.empty:
        graficar_f1_comparativa(df_graf, dir_fig)
        print("  f1_comparativa_por_ticker.png generada")

    # ── 4. Métricas financieras ───────────────────────────────────────────
    print("\n[4/4] Calculando métricas financieras de backtesting...")
    print("  (Esto requiere que los modelos estén entrenados y los datos raw disponibles)")

    fin_registros = []

    for ticker in TICKERS:
        raw_path = RAW_DIR / f"{ticker}_raw.parquet"
        if not raw_path.exists():
            continue

        df_raw = pd.read_parquet(raw_path)
        mask   = (df_raw.index >= TEST_START) & (df_raw.index <= TEST_END)
        df_test = df_raw[mask].dropna(subset=["r_forward", "target"])

        if len(df_test) < 50:
            continue

        fechas   = df_test.index.tolist()
        r_fwd    = df_test["r_forward"].values

        # Buy & Hold baseline
        eq_bh = (1 + r_fwd).cumprod()
        bh_ret = eq_bh[-1] - 1.0

        print(f"\n  {ticker} — {len(df_test)} días de prueba")

        # Cargar predicciones de cada modelo desde sus JSON
        # (Las funciones de carga completa requieren los módulos de entrenamiento
        #  importados. Aquí se leen los resultados ya guardados.)
        for json_path in (MODELS_DIR / "logistic_regression" / "por_ticker" /
                          f"experimento_{EXPERIMENTO_PRINCIPAL}").glob(f"{ticker}_*.json"):
            try:
                with open(json_path) as f:
                    meta = json.load(f)
                # Las señales reales del test están en metricas_test["dist_pred"]
                # Para el backtest real se necesitan las predicciones día a día.
                # Este bloque es un placeholder: el backtest completo requiere
                # regenerar las predicciones desde los modelos guardados.
                print(f"    LR métricas test: F1={meta['metricas_test']['f1_macro']:.3f}")
            except Exception:
                pass

        fin_registros.append({
            "ticker": ticker,
            "buy_hold_return_pct": round(float(bh_ret * 100), 2),
            "n_dias_test": len(df_test),
        })

    df_fin = pd.DataFrame(fin_registros)
    if not df_fin.empty:
        df_fin.to_csv(OUTPUT_DIR / "baseline_bh.csv", index=False)
        print("\n  Baseline Buy & Hold por ticker:")
        print(df_fin.to_string(index=False))

    # ── Reporte final ─────────────────────────────────────────────────────
    print("\n" + "="*65)
    print("  ARCHIVOS GENERADOS EN 05_evaluation/")
    print("="*65)
    print("  comparativa_clasificacion.csv  — todas las métricas por modelo/ticker/exp")
    print("  resumen_f1_promedio.csv        — F1 promedio agrupado")
    print("  baseline_bh.csv                — retorno buy & hold por ticker")
    print("  figuras/f1_comparativa_por_ticker.png")
    print(f"\n✓ Guardado en: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    pipeline()
