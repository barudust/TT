"""
================================================================================
SCRIPT 07 — ENTRENAMIENTO: CNN-LSTM (PyTorch + CUDA)
================================================================================
Arquitectura híbrida CNN-LSTM donde:
  - El bloque CNN extrae patrones locales de las velas japonesas y features
  - El bloque LSTM aprende dependencias temporales de largo plazo
Input: (batch, lookback, n_features + 5_OHLCV)
       Las últimas 5 columnas son los canales OHLCV normalizados localmente

Métricas reportadas:
  Clasificación : f1_macro, f1_buy, f1_sell, f1_buy_sell_avg, accuracy
  Económicas    : cumul_return_90d, return_vs_bh_90d, sharpe_90d,
                  max_drawdown_90d, win_rate_90d, profit_factor_90d
  Distribución  : signal_distribution (% BUY / HOLD / SELL predichos)

Salida: tesis_ml_stocks/04_models/cnn_lstm/
    por_ticker/lookback_[20|60]/experimento_[A|B|C]/{TICKER}_checkpoint.pt
    global/lookback_[20|60]/experimento_[A|B|C]/modelo_global_checkpoint.pt
    resultados_cnn_lstm.csv

Dependencias: pip install torch scikit-learn pandas numpy pyarrow
================================================================================
"""

import json
import warnings
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.metrics import f1_score, classification_report, confusion_matrix
from sklearn.utils.class_weight import compute_class_weight
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

warnings.filterwarnings("ignore")
torch.manual_seed(42)
np.random.seed(42)

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════════════════════

TICKERS    = ["AAPL", "NVDA", "TSLA", "AMZN", "MSFT", "GOOGL", "META"]
DATA_BASE  = Path("tesis_ml_stocks/03_model_datasets/cnn_lstm")
RAW_DIR    = Path("tesis_ml_stocks/01_raw_datasets")
OUTPUT_DIR = Path("tesis_ml_stocks/04_models/cnn_lstm")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CLASES  = [0, 1, 2]
NOMBRES = {0: "SELL", 1: "HOLD", 2: "BUY"}

LOOKBACKS    = [20, 60]
EXPERIMENTOS = {"A": "Máximo historial", "B": "RECOMENDADO", "C": "Era moderna"}

EXPERIMENTOS_FECHAS = {
    "A": {"test": ("2024-01-01", "2025-12-31")},
    "B": {"test": ("2025-01-01", "2025-12-31")},
    "C": {"test": ("2025-01-01", "2025-12-31")},
}

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Dispositivo de cómputo: {DEVICE}")
if DEVICE.type == "cuda":
    print(f"GPU: {torch.cuda.get_device_name(0)}")

EPOCHS      = 80
BATCH_SIZE  = 64
LR          = 1e-3
PATIENCE    = 15
CNN_FILTERS = [64, 128]
CNN_KERNELS = [3, 3]
CNN_DROPOUT = 0.2
LSTM_HIDDEN = 128
LSTM_LAYERS = 2
LSTM_DROPOUT = 0.3
VENTANA_ECON = 90


# ══════════════════════════════════════════════════════════════════════════════
# ARQUITECTURA CNN-LSTM
# ══════════════════════════════════════════════════════════════════════════════

class CNNLSTMClasificador(nn.Module):
    """
    Arquitectura CNN-LSTM para clasificación de señales de trading.
    Flujo:
        Input (batch, lookback, n_features)
          → Transponer a (batch, n_features, lookback)
          → Conv1d capa 1 + BatchNorm + ReLU + Dropout
          → Conv1d capa 2 + BatchNorm + ReLU + Dropout
          → Transponer de vuelta a (batch, lookback, n_filtros)
          → LSTM (n_layers, hidden_size)
          → Dropout + LayerNorm
          → Linear → logits (batch, 3)
    """
    def __init__(self, input_size: int,
                 cnn_filters=CNN_FILTERS, cnn_kernels=CNN_KERNELS,
                 cnn_dropout=CNN_DROPOUT, lstm_hidden=LSTM_HIDDEN,
                 lstm_layers=LSTM_LAYERS, lstm_dropout=LSTM_DROPOUT,
                 n_clases: int = 3):
        super().__init__()
        cnn_layers = []
        in_ch = input_size
        for out_ch, k in zip(cnn_filters, cnn_kernels):
            cnn_layers += [
                nn.Conv1d(in_channels=in_ch, out_channels=out_ch,
                          kernel_size=k, padding=k//2),
                nn.BatchNorm1d(out_ch),
                nn.ReLU(),
                nn.Dropout(cnn_dropout),
            ]
            in_ch = out_ch
        self.cnn = nn.Sequential(*cnn_layers)
        self.lstm = nn.LSTM(
            input_size   = cnn_filters[-1],
            hidden_size  = lstm_hidden,
            num_layers   = lstm_layers,
            batch_first  = True,
            dropout      = lstm_dropout if lstm_layers > 1 else 0.0,
        )
        self.dropout = nn.Dropout(lstm_dropout)
        self.norm    = nn.LayerNorm(lstm_hidden)
        self.fc      = nn.Linear(lstm_hidden, n_clases)
        self.config  = {
            "input_size": input_size, "cnn_filters": cnn_filters,
            "cnn_kernels": cnn_kernels, "cnn_dropout": cnn_dropout,
            "lstm_hidden": lstm_hidden, "lstm_layers": lstm_layers,
            "lstm_dropout": lstm_dropout, "n_clases": n_clases,
        }

    def forward(self, x):
        x = x.transpose(1, 2)
        x = self.cnn(x)
        x = x.transpose(1, 2)
        lstm_out, _ = self.lstm(x)
        out = lstm_out[:, -1, :]
        out = self.norm(out)
        out = self.dropout(out)
        return self.fc(out)


# ══════════════════════════════════════════════════════════════════════════════
# UTILIDADES — CARGA DE DATOS
# ══════════════════════════════════════════════════════════════════════════════

def cargar_splits(ticker, exp_id, lookback):
    base = DATA_BASE / f"lookback_{lookback}" / f"experimento_{exp_id}"
    X_tr = np.load(base / f"{ticker}_X_train.npy")
    y_tr = np.load(base / f"{ticker}_y_train.npy")
    X_va = np.load(base / f"{ticker}_X_val.npy")
    y_va = np.load(base / f"{ticker}_y_val.npy")
    X_te = np.load(base / f"{ticker}_X_test.npy")
    y_te = np.load(base / f"{ticker}_y_test.npy")
    return X_tr, y_tr, X_va, y_va, X_te, y_te


def cargar_retornos_test(ticker: str, exp_id: str) -> np.ndarray:
    """
    Carga los retornos forward reales del período de prueba desde el parquet crudo.
    Se usan para calcular métricas económicas sin lookahead.
    """
    path = RAW_DIR / f"{ticker}_raw.parquet"
    if not path.exists():
        return None
    df = pd.read_parquet(path)
    fechas = EXPERIMENTOS_FECHAS[exp_id]["test"]
    mask = (df.index >= fechas[0]) & (df.index <= fechas[1])
    df_test = df[mask]
    return df_test["r_forward"].values if "r_forward" in df_test.columns else None


# ══════════════════════════════════════════════════════════════════════════════
# MÉTRICAS ECONÓMICAS
# ══════════════════════════════════════════════════════════════════════════════

def calcular_metricas_economicas(y_pred: np.ndarray,
                                  r_forward: np.ndarray,
                                  ventana: int = VENTANA_ECON) -> dict:
    """
    Calcula métricas económicas sobre los primeros 'ventana' días del test.

    Lógica de simulación:
      BUY  (2): posición larga  → retorno = +r_forward
      SELL (0): posición corta  → retorno = -r_forward
      HOLD (1): sin posición    → retorno =  0

    Sin costos de transacción ni slippage (backtesting básico).
    """
    n = min(len(y_pred), len(r_forward))
    pred = y_pred[:n]
    ret  = r_forward[:n]

    r_strat = np.where(pred == 2,  ret,
              np.where(pred == 0, -ret, 0.0))

    cumul_return = float(np.expm1(np.sum(r_strat)))
    bh_return    = float(np.expm1(np.sum(ret)))
    return_vs_bh = cumul_return - bh_return

    sharpe = float((r_strat.mean() / r_strat.std()) * np.sqrt(252)) \
             if r_strat.std() > 1e-8 else 0.0

    equity       = np.exp(np.cumsum(r_strat))
    rolling_max  = np.maximum.accumulate(equity)
    drawdowns    = (equity - rolling_max) / (rolling_max + 1e-8)
    max_drawdown = float(drawdowns.min())

    operaciones   = r_strat[pred != 1]
    win_rate      = float((operaciones > 0).mean()) if len(operaciones) > 0 else 0.0

    ganancias     = operaciones[operaciones > 0].sum()
    perdidas      = abs(operaciones[operaciones < 0].sum())
    profit_factor = float(ganancias / perdidas) if perdidas > 1e-8 else np.inf

    return {
        "cumul_return_test":  round(cumul_return,  4),
        "return_vs_bh_test":  round(return_vs_bh,  4),
        "sharpe_test":        round(sharpe,         4),
        "max_drawdown_test":  round(max_drawdown,   4),
        "win_rate_test":      round(win_rate,       4),
        "profit_factor_test": round(profit_factor,  4)
                                     if profit_factor != np.inf else None,
    }


# ══════════════════════════════════════════════════════════════════════════════
# MÉTRICAS DE CLASIFICACIÓN
# ══════════════════════════════════════════════════════════════════════════════

def calcular_metricas(y_true: np.ndarray,
                       y_pred: np.ndarray,
                       split_name: str,
                       r_forward: np.ndarray = None) -> dict:
    """
    Calcula métricas de clasificación y, si se proporcionan retornos,
    también las métricas económicas sobre la ventana de 90 días.
    """
    report = classification_report(y_true, y_pred,
                                   target_names=["SELL", "HOLD", "BUY"],
                                   output_dict=True, zero_division=0)
    cm = confusion_matrix(y_true, y_pred, labels=CLASES).tolist()

    signal_dist = {
        NOMBRES[k]: {
            "n":   int((y_pred == k).sum()),
            "pct": round((y_pred == k).mean() * 100, 1),
        }
        for k in CLASES
    }

    metricas = {
        "split":               split_name,
        "f1_macro":            round(f1_score(y_true, y_pred, average="macro",
                                              zero_division=0), 4),
        "f1_buy":              round(report["BUY"]["f1-score"],   4),
        "f1_hold":             round(report["HOLD"]["f1-score"],  4),
        "f1_sell":             round(report["SELL"]["f1-score"],  4),
        "f1_buy_sell_avg":     round((report["BUY"]["f1-score"] +
                                      report["SELL"]["f1-score"]) / 2, 4),
        "precision_buy":       round(report["BUY"]["precision"],  4),
        "precision_sell":      round(report["SELL"]["precision"], 4),
        "recall_buy":          round(report["BUY"]["recall"],     4),
        "recall_sell":         round(report["SELL"]["recall"],    4),
        "accuracy":            round(report["accuracy"],          4),
        "signal_distribution": signal_dist,
        "confusion_matrix":    cm,
        "n_samples":           int(len(y_true)),
        "dist_real":           {NOMBRES[k]: int((y_true == k).sum()) for k in CLASES},
    }

    if r_forward is not None and len(r_forward) >= VENTANA_ECON:
        eco = calcular_metricas_economicas(y_pred, r_forward, VENTANA_ECON)
        metricas.update(eco)

    return metricas


# ══════════════════════════════════════════════════════════════════════════════
# UTILIDADES — PYTORCH
# ══════════════════════════════════════════════════════════════════════════════

def crear_dataloader(X, y, batch_size=BATCH_SIZE, shuffle=True):
    Xt = torch.FloatTensor(X).to(DEVICE)
    yt = torch.LongTensor(y).to(DEVICE)
    return DataLoader(TensorDataset(Xt, yt), batch_size=batch_size, shuffle=shuffle)


def calcular_class_weights(y):
    pesos = compute_class_weight("balanced", classes=np.array(CLASES), y=y)
    return torch.FloatTensor(pesos).to(DEVICE)


def predecir(modelo, X):
    modelo.eval()
    with torch.no_grad():
        Xt = torch.FloatTensor(X).to(DEVICE)
        return torch.argmax(modelo(Xt), dim=1).cpu().numpy()


def entrenar_ciclo(modelo, loader_tr, loader_va, class_weights,
                   epochs=EPOCHS, patience=PATIENCE):
    criterio    = nn.CrossEntropyLoss(weight=class_weights)
    optimizador = optim.Adam(modelo.parameters(), lr=LR, weight_decay=1e-4)
    scheduler   = optim.lr_scheduler.ReduceLROnPlateau(
        optimizador, mode="min", factor=0.5, patience=8, min_lr=1e-6)

    mejor_val_loss    = float("inf")
    epochs_sin_mejora = 0
    mejor_estado      = None
    historial         = []

    for epoch in range(1, epochs + 1):
        modelo.train()
        loss_tr = 0.0
        for Xb, yb in loader_tr:
            optimizador.zero_grad()
            loss = criterio(modelo(Xb), yb)
            loss.backward()
            nn.utils.clip_grad_norm_(modelo.parameters(), max_norm=1.0)
            optimizador.step()
            loss_tr += loss.item()
        loss_tr /= len(loader_tr)

        modelo.eval()
        loss_va = 0.0
        preds_va, true_va = [], []
        with torch.no_grad():
            for Xb, yb in loader_va:
                logits    = modelo(Xb)
                loss_va  += criterio(logits, yb).item()
                preds_va.extend(torch.argmax(logits, 1).cpu().numpy())
                true_va.extend(yb.cpu().numpy())
        loss_va /= len(loader_va)
        f1_va    = f1_score(true_va, preds_va, average="macro", zero_division=0)
        scheduler.step(loss_va)

        historial.append({"epoch": epoch, "loss_tr": loss_tr,
                          "loss_va": loss_va, "f1_va": f1_va})

        if loss_va < mejor_val_loss:
            mejor_val_loss    = loss_va
            epochs_sin_mejora = 0
            mejor_estado      = {k: v.clone() for k, v in modelo.state_dict().items()}
        else:
            epochs_sin_mejora += 1

        if epoch % 10 == 0:
            print(f"      Ep{epoch:3d}/{epochs} | "
                  f"loss_tr={loss_tr:.4f} loss_va={loss_va:.4f} f1_va={f1_va:.3f}")

        if epochs_sin_mejora >= patience:
            print(f"      Early stop en epoch {epoch}")
            break

    if mejor_estado:
        modelo.load_state_dict(mejor_estado)
    return modelo, historial


# ══════════════════════════════════════════════════════════════════════════════
# ENTRENAMIENTO POR TICKER
# ══════════════════════════════════════════════════════════════════════════════

def entrenar_por_ticker():
    print("\n" + "═"*65)
    print("  CNN-LSTM — POR TICKER")
    print("═"*65)

    resultados = []

    for lb in LOOKBACKS:
        for exp_id, exp_desc in EXPERIMENTOS.items():
            print(f"\n── Lookback={lb}  Experimento {exp_id}: {exp_desc}")
            dir_out = OUTPUT_DIR / "por_ticker" / f"lookback_{lb}" / f"experimento_{exp_id}"
            dir_out.mkdir(parents=True, exist_ok=True)

            for ticker in TICKERS:
                print(f"  {ticker}...")
                try:
                    X_tr, y_tr, X_va, y_va, X_te, y_te = \
                        cargar_splits(ticker, exp_id, lb)
                except FileNotFoundError:
                    print("    sin datos")
                    continue

                r_fwd_test = cargar_retornos_test(ticker, exp_id)
                input_size = X_tr.shape[2]
                cw         = calcular_class_weights(y_tr)
                loader_tr  = crear_dataloader(X_tr, y_tr)
                loader_va  = crear_dataloader(X_va, y_va, shuffle=False)

                modelo  = CNNLSTMClasificador(input_size=input_size).to(DEVICE)
                n_params = sum(p.numel() for p in modelo.parameters()
                               if p.requires_grad)
                print(f"    Parámetros entrenables: {n_params:,}")

                modelo, historial = entrenar_ciclo(modelo, loader_tr, loader_va, cw)

                met_val  = calcular_metricas(y_va, predecir(modelo, X_va), "val")
                met_test = calcular_metricas(y_te, predecir(modelo, X_te), "test",
                                             r_forward=r_fwd_test)

                eco = f"  Ret={met_test.get(f'cumul_return_{VENTANA_ECON}d','N/A')}  " \
                      f"Sharpe={met_test.get(f'sharpe_{VENTANA_ECON}d','N/A')}  " \
                      f"WR={met_test.get(f'win_rate_{VENTANA_ECON}d','N/A')}" \
                      if f"cumul_return_{VENTANA_ECON}d" in met_test else ""

                print(f"    Val  F1={met_val['f1_macro']:.3f} "
                      f"BUY={met_val['f1_buy']:.3f} SELL={met_val['f1_sell']:.3f}")
                print(f"    Test F1={met_test['f1_macro']:.3f} "
                      f"BUY={met_test['f1_buy']:.3f} SELL={met_test['f1_sell']:.3f}"
                      f"{eco}")

                torch.save({
                    "state_dict": modelo.state_dict(),
                    "config":     modelo.config,
                    "historial":  historial,
                }, dir_out / f"{ticker}_checkpoint.pt")

                meta = {
                    "ticker": ticker, "experimento": exp_id,
                    "lookback": lb, "tipo": "por_ticker", "modelo": "CNN-LSTM",
                    "arquitectura": modelo.config,
                    "entrenamiento": {
                        "n_params":       n_params,
                        "epochs_totales": len(historial),
                        "mejor_val_loss": min(h["loss_va"] for h in historial),
                    },
                    "n_train": len(y_tr), "n_val": len(y_va), "n_test": len(y_te),
                    "metricas_val":  met_val,
                    "metricas_test": met_test,
                }
                with open(dir_out / f"{ticker}_metricas.json", "w") as f:
                    json.dump(meta, f, indent=2)

                fila = {
                    "modelo": "CNN-LSTM", "tipo": "por_ticker",
                    "ticker": ticker, "experimento": exp_id, "lookback": lb,
                    "val_f1_macro":        met_val["f1_macro"],
                    "test_f1_macro":       met_test["f1_macro"],
                    "test_f1_buy":         met_test["f1_buy"],
                    "test_f1_sell":        met_test["f1_sell"],
                    "test_f1_buy_sell_avg": met_test["f1_buy_sell_avg"],
                    "signal_pct_buy":      met_test["signal_distribution"]["BUY"]["pct"],
                    "signal_pct_hold":     met_test["signal_distribution"]["HOLD"]["pct"],
                    "signal_pct_sell":     met_test["signal_distribution"]["SELL"]["pct"],
                }
                for k in ["cumul_return_test", "return_vs_bh_test", "sharpe_test", "max_drawdown_test", "win_rate_test", "profit_factor_test"]:
                    fila[k] = met_test.get(k, None)

                resultados.append(fila)

    return resultados


# ══════════════════════════════════════════════════════════════════════════════
# ENTRENAMIENTO GLOBAL
# ══════════════════════════════════════════════════════════════════════════════

def entrenar_global():
    print("\n" + "═"*65)
    print("  CNN-LSTM — MODELO GLOBAL")
    print("═"*65)

    resultados = []

    for lb in LOOKBACKS:
        for exp_id, exp_desc in EXPERIMENTOS.items():
            print(f"\n── Lookback={lb}  Experimento {exp_id}")
            dir_out = OUTPUT_DIR / "global" / f"lookback_{lb}" / f"experimento_{exp_id}"
            dir_out.mkdir(parents=True, exist_ok=True)

            trains, vals, tests = [], [], []
            r_fwd_tests = []
            input_size  = None

            for ticker in TICKERS:
                try:
                    X_tr, y_tr, X_va, y_va, X_te, y_te = \
                        cargar_splits(ticker, exp_id, lb)
                    trains.append((X_tr, y_tr))
                    vals.append((X_va, y_va))
                    tests.append((X_te, y_te))
                    r = cargar_retornos_test(ticker, exp_id)
                    if r is not None:
                        r_fwd_tests.append(r)
                    if input_size is None:
                        input_size = X_tr.shape[2]
                except FileNotFoundError:
                    pass

            if not trains:
                continue

            X_tr = np.vstack([x for x,_ in trains])
            y_tr = np.concatenate([y for _,y in trains])
            X_va = np.vstack([x for x,_ in vals])
            y_va = np.concatenate([y for _,y in vals])
            X_te = np.vstack([x for x,_ in tests])
            y_te = np.concatenate([y for _,y in tests])
            r_fwd_global = np.concatenate(r_fwd_tests) if r_fwd_tests else None

            print(f"  Train={len(y_tr)}  Val={len(y_va)}  Test={len(y_te)}")

            cw        = calcular_class_weights(y_tr)
            loader_tr = crear_dataloader(X_tr, y_tr)
            loader_va = crear_dataloader(X_va, y_va, shuffle=False)

            modelo = CNNLSTMClasificador(input_size=input_size).to(DEVICE)
            modelo, historial = entrenar_ciclo(modelo, loader_tr, loader_va, cw)

            met_val  = calcular_metricas(y_va, predecir(modelo, X_va), "val")
            met_test = calcular_metricas(y_te, predecir(modelo, X_te), "test",
                                         r_forward=r_fwd_global)

            print(f"  Val F1={met_val['f1_macro']:.3f}  "
                  f"Test F1={met_test['f1_macro']:.3f}  "
                  f"Ret={met_test.get(f'cumul_return_{VENTANA_ECON}d','N/A')}")

            torch.save({
                "state_dict": modelo.state_dict(),
                "config":     modelo.config,
                "historial":  historial,
            }, dir_out / "modelo_global_checkpoint.pt")

            meta = {
                "ticker": "GLOBAL", "experimento": exp_id, "lookback": lb,
                "tipo": "global", "modelo": "CNN-LSTM",
                "tickers_incluidos": TICKERS,
                "n_train": len(y_tr), "n_val": len(y_va), "n_test": len(y_te),
                "metricas_val":  met_val,
                "metricas_test": met_test,
            }
            with open(dir_out / "metricas_global.json", "w") as f:
                json.dump(meta, f, indent=2)

            fila = {
                "modelo": "CNN-LSTM", "tipo": "global",
                "ticker": "GLOBAL", "experimento": exp_id, "lookback": lb,
                "val_f1_macro":        met_val["f1_macro"],
                "test_f1_macro":       met_test["f1_macro"],
                "test_f1_buy":         met_test["f1_buy"],
                "test_f1_sell":        met_test["f1_sell"],
                "test_f1_buy_sell_avg": met_test["f1_buy_sell_avg"],
                "signal_pct_buy":      met_test["signal_distribution"]["BUY"]["pct"],
                "signal_pct_hold":     met_test["signal_distribution"]["HOLD"]["pct"],
                "signal_pct_sell":     met_test["signal_distribution"]["SELL"]["pct"],
            }
            for k in ["cumul_return_test", "return_vs_bh_test", "sharpe_test", "max_drawdown_test", "win_rate_test", "profit_factor_test"]:
                fila[k] = met_test.get(k, None)

            resultados.append(fila)

    return resultados


# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE
# ══════════════════════════════════════════════════════════════════════════════

def pipeline():
    print("="*65)
    print("  SCRIPT 07 — CNN-LSTM (PyTorch)")
    print(f"  Dispositivo: {DEVICE}")
    print("="*65)

    res = entrenar_por_ticker() + entrenar_global()
    df  = pd.DataFrame(res)
    df.to_csv(OUTPUT_DIR / "resultados_cnn_lstm.csv", index=False)

    print("\n" + "="*65)
    print("  RESUMEN — CNN-LSTM")
    print("="*65)
    cols_resumen = ["tipo", "ticker", "experimento", "lookback",
                    "val_f1_macro", "test_f1_macro",
                    "cumul_return_test", "sharpe_test", "win_rate_test"]
    print(df[[c for c in cols_resumen if c in df.columns]].to_string(index=False))
    print(f"\n✓ Guardado en: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    pipeline()