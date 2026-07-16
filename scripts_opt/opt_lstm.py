"""
================================================================================
OPTIMIZACIÓN — LSTM (PyTorch + CUDA)
================================================================================
Mejoras sobre baseline:
  - Bidirectional LSTM
  - Attention mechanism (opcional)
  - Focal loss para reducir colapso en clase mayoritaria
  - Label smoothing
  - Más features (todas, no solo consenso)
  - Multi-seed ensembling
  - Mixed precision training (AMP)
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("PYTHONUNBUFFERED", "1")
import sys
import time
import json
import warnings
import functools
import numpy as np
import pandas as pd
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass
print = functools.partial(print, flush=True)

sys.path.insert(0, str(Path(__file__).parent))
from common import (TICKERS, EXPERIMENTOS, CLASES,
                    cargar_dataset, cargar_global, get_feature_cols,
                    metricas_full, metricas_global_por_ticker,
                    guardar_json, imprimir_metricas, OUT_DIR, SPLITS)

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import MinMaxScaler
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import f1_score

warnings.filterwarnings("ignore")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Dispositivo: {DEVICE} - {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")

OUT_LSTM = OUT_DIR / "modelos_optimizados" / "lstm"
OUT_LSTM.mkdir(parents=True, exist_ok=True)
RESULTS_CSV = OUT_LSTM / "resultados_lstm_opt.csv"


# ════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ════════════════════════════════════════════════════════════════════════════

LOOKBACKS  = [20, 60]
EPOCHS     = 100
BATCH_SIZE = 128
LR         = 1e-3
WD         = 1e-4
PATIENCE   = 20
SEEDS      = [42, 1, 7]

# Configuraciones a probar
CONFIGS = {
    "LSTM-01-stack":      dict(arch="lstm",   bidir=False, attn=False, hidden=128, layers=2,
                                dropout=0.3, loss="ce", label_smooth=0.0),
    "LSTM-02-bi":         dict(arch="lstm",   bidir=True,  attn=False, hidden=128, layers=2,
                                dropout=0.3, loss="ce", label_smooth=0.0),
    "LSTM-03-bi-attn":    dict(arch="lstm",   bidir=True,  attn=True,  hidden=128, layers=2,
                                dropout=0.3, loss="ce", label_smooth=0.0),
    "LSTM-04-bi-focal":   dict(arch="lstm",   bidir=True,  attn=False, hidden=128, layers=2,
                                dropout=0.3, loss="focal", focal_gamma=2.0, label_smooth=0.0),
    "LSTM-05-bi-smooth":  dict(arch="lstm",   bidir=True,  attn=False, hidden=128, layers=2,
                                dropout=0.3, loss="ce", label_smooth=0.1),
    "LSTM-06-deeper":     dict(arch="lstm",   bidir=True,  attn=True,  hidden=192, layers=3,
                                dropout=0.4, loss="ce", label_smooth=0.05),
}


# ════════════════════════════════════════════════════════════════════════════
# ARQUITECTURA
# ════════════════════════════════════════════════════════════════════════════

class Attention(nn.Module):
    """Attention global sobre la secuencia."""
    def __init__(self, hidden_size):
        super().__init__()
        self.attn = nn.Linear(hidden_size, 1)

    def forward(self, x):
        # x: (B, T, H)
        scores = self.attn(x)                  # (B, T, 1)
        weights = F.softmax(scores, dim=1)     # (B, T, 1)
        return (x * weights).sum(dim=1)        # (B, H)


class LSTMClasificador(nn.Module):
    def __init__(self, input_size, hidden=128, layers=2,
                 dropout=0.3, bidir=False, attn=False, n_clases=3):
        super().__init__()
        self.bidir = bidir
        self.attn = attn
        self.lstm = nn.LSTM(
            input_size=input_size, hidden_size=hidden, num_layers=layers,
            batch_first=True, dropout=dropout if layers > 1 else 0.0,
            bidirectional=bidir)
        out_size = hidden * (2 if bidir else 1)
        if attn:
            self.attn_layer = Attention(out_size)
        self.norm    = nn.LayerNorm(out_size)
        self.dropout = nn.Dropout(dropout)
        self.fc      = nn.Linear(out_size, n_clases)

    def forward(self, x):
        out, _ = self.lstm(x)
        if self.attn:
            pooled = self.attn_layer(out)
        else:
            pooled = out[:, -1, :]
        pooled = self.norm(pooled)
        pooled = self.dropout(pooled)
        return self.fc(pooled)


class FocalLoss(nn.Module):
    """Focal loss multiclass: -(1-p_t)^gamma * log(p_t)."""
    def __init__(self, gamma=2.0, weight=None):
        super().__init__()
        self.gamma = gamma
        self.weight = weight

    def forward(self, logits, targets):
        ce = F.cross_entropy(logits, targets, weight=self.weight, reduction="none")
        pt = torch.exp(-ce)
        focal = ((1 - pt) ** self.gamma) * ce
        return focal.mean()


# ════════════════════════════════════════════════════════════════════════════
# SECUENCIAS
# ════════════════════════════════════════════════════════════════════════════

def construir_sec(feat_arr, target_arr, lookback):
    """Construye ventanas deslizantes."""
    X, y = [], []
    for i in range(lookback, len(feat_arr)):
        X.append(feat_arr[i - lookback:i])
        y.append(target_arr[i])
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.int64)


def preparar_datos_ticker(ticker, exp_id, lookback, feat_cols=None):
    """
    Carga datos del ticker (raw -> split -> escalado -> ventanas).
    Retorna X_tr, y_tr, X_va, y_va, X_te, y_te, r_fwd_test_alineado.
    """
    d = cargar_dataset(ticker, exp_id, feat_cols)
    X_tr_raw, y_tr_raw = d["X_tr"], d["y_tr"]
    X_va_raw, y_va_raw = d["X_va"], d["y_va"]
    X_te_raw, y_te_raw = d["X_te"], d["y_te"]
    r_fwd_test = d["r_fwd_test"]

    scaler = MinMaxScaler()
    X_tr_s = scaler.fit_transform(X_tr_raw)
    X_va_s = scaler.transform(X_va_raw)
    X_te_s = scaler.transform(X_te_raw)

    X_tr, y_tr = construir_sec(X_tr_s, y_tr_raw, lookback)
    X_va, y_va = construir_sec(X_va_s, y_va_raw, lookback)
    X_te, y_te = construir_sec(X_te_s, y_te_raw, lookback)
    # alinear r_fwd con y_te (omitir las primeras lookback filas)
    r_fwd_test_align = r_fwd_test[lookback:] if r_fwd_test is not None else None

    return {
        "X_tr": X_tr, "y_tr": y_tr,
        "X_va": X_va, "y_va": y_va,
        "X_te": X_te, "y_te": y_te,
        "r_fwd_test": r_fwd_test_align,
        "scaler": scaler,
        "feat_cols": d["feat_cols"],
    }


def preparar_datos_global(exp_id, lookback, feat_cols=None):
    """Concatena ventanas de todos los tickers, escalando POR TICKER (no compartido)."""
    Xtr_l, ytr_l = [], []
    Xva_l, yva_l = [], []
    Xte_l, yte_l = [], []
    rfwd_te_l    = []
    tk_te_l      = []
    feat_cols_ref = None

    for ticker in TICKERS:
        d = preparar_datos_ticker(ticker, exp_id, lookback, feat_cols)
        Xtr_l.append(d["X_tr"]); ytr_l.append(d["y_tr"])
        Xva_l.append(d["X_va"]); yva_l.append(d["y_va"])
        Xte_l.append(d["X_te"]); yte_l.append(d["y_te"])
        rfwd_te_l.append(d["r_fwd_test"])
        tk_te_l.append(np.full(len(d["y_te"]), ticker))
        if feat_cols_ref is None:
            feat_cols_ref = d["feat_cols"]

    return {
        "X_tr": np.vstack(Xtr_l).astype(np.float32),
        "y_tr": np.concatenate(ytr_l),
        "X_va": np.vstack(Xva_l).astype(np.float32),
        "y_va": np.concatenate(yva_l),
        "X_te": np.vstack(Xte_l).astype(np.float32),
        "y_te": np.concatenate(yte_l),
        "r_fwd_test": np.concatenate(rfwd_te_l),
        "ticker_test": np.concatenate(tk_te_l),
        "feat_cols": feat_cols_ref,
    }


# ════════════════════════════════════════════════════════════════════════════
# ENTRENAMIENTO
# ════════════════════════════════════════════════════════════════════════════

def make_loader(X, y, batch_size=BATCH_SIZE, shuffle=True):
    Xt = torch.from_numpy(X).float()
    yt = torch.from_numpy(y).long()
    return DataLoader(TensorDataset(Xt, yt), batch_size=batch_size,
                       shuffle=shuffle, pin_memory=True, num_workers=0)


def get_loss(config, class_weights):
    if config["loss"] == "focal":
        return FocalLoss(gamma=config.get("focal_gamma", 2.0), weight=class_weights)
    return nn.CrossEntropyLoss(weight=class_weights,
                                label_smoothing=config.get("label_smooth", 0.0))


def entrenar(modelo, loader_tr, loader_va, class_weights, config,
             epochs=EPOCHS, patience=PATIENCE):
    criterio = get_loss(config, class_weights)
    opt = optim.AdamW(modelo.parameters(), lr=LR, weight_decay=WD)
    sched = optim.lr_scheduler.ReduceLROnPlateau(opt, mode="min", factor=0.5,
                                                   patience=8, min_lr=1e-6)

    best_va = float("inf")
    sin_mej = 0
    best_state = None

    for epoch in range(1, epochs + 1):
        modelo.train()
        loss_tr = 0.0
        for Xb, yb in loader_tr:
            Xb = Xb.to(DEVICE, non_blocking=True)
            yb = yb.to(DEVICE, non_blocking=True)
            opt.zero_grad()
            loss = criterio(modelo(Xb), yb)
            loss.backward()
            nn.utils.clip_grad_norm_(modelo.parameters(), max_norm=1.0)
            opt.step()
            loss_tr += loss.item()
        loss_tr /= len(loader_tr)

        modelo.eval()
        loss_va = 0.0
        preds, trues = [], []
        with torch.no_grad():
            for Xb, yb in loader_va:
                Xb = Xb.to(DEVICE)
                yb = yb.to(DEVICE)
                logits = modelo(Xb)
                loss_va += criterio(logits, yb).item()
                preds.extend(torch.argmax(logits, 1).cpu().numpy())
                trues.extend(yb.cpu().numpy())
        loss_va /= len(loader_va)
        f1_va = f1_score(trues, preds, average="macro", zero_division=0)
        sched.step(loss_va)

        if loss_va < best_va:
            best_va = loss_va
            sin_mej = 0
            best_state = {k: v.detach().clone() for k, v in modelo.state_dict().items()}
        else:
            sin_mej += 1

        if epoch % 20 == 0:
            print(f"      Ep{epoch:3d}/{epochs}  tr={loss_tr:.4f}  va={loss_va:.4f}  f1_va={f1_va:.3f}")

        if sin_mej >= patience:
            print(f"      Early stop ep{epoch}")
            break

    if best_state:
        modelo.load_state_dict(best_state)
    return modelo


def predecir_logits(modelo, X, batch=256):
    modelo.eval()
    out = []
    with torch.no_grad():
        for i in range(0, len(X), batch):
            xb = torch.from_numpy(X[i:i+batch]).float().to(DEVICE)
            out.append(modelo(xb).cpu().numpy())
    return np.vstack(out)


# ════════════════════════════════════════════════════════════════════════════
# UN EXPERIMENTO
# ════════════════════════════════════════════════════════════════════════════

def correr_config(config_id, config, exp_id, lookback):
    print(f"\n{'═'*70}")
    print(f"  Config: {config_id}  |  Exp {exp_id}  |  Lookback={lookback}")
    print(f"  arch={config['arch']} bidir={config['bidir']} attn={config['attn']} "
          f"hidden={config['hidden']} layers={config['layers']} dropout={config['dropout']} "
          f"loss={config['loss']}")
    print(f"{'═'*70}")

    out_dir = OUT_LSTM / config_id / f"lookback_{lookback}" / f"experimento_{exp_id}"
    out_dir.mkdir(parents=True, exist_ok=True)

    resultados = []

    # ── POR TICKER ──
    print(f"\n  ── POR TICKER ─────────────────────────")
    for ticker in TICKERS:
        d = preparar_datos_ticker(ticker, exp_id, lookback)
        if len(d["X_tr"]) < 100:
            print(f"  {ticker}: datos insuficientes")
            continue

        cw_np = compute_class_weight("balanced", classes=np.array(CLASES), y=d["y_tr"])
        class_weights = torch.tensor(cw_np, dtype=torch.float32, device=DEVICE)

        loader_tr = make_loader(d["X_tr"], d["y_tr"], shuffle=True)
        loader_va = make_loader(d["X_va"], d["y_va"], shuffle=False)

        input_size = d["X_tr"].shape[2]

        # Multi-seed ensemble
        logits_va_list, logits_te_list = [], []
        for s in SEEDS:
            torch.manual_seed(s)
            np.random.seed(s)
            modelo = LSTMClasificador(
                input_size=input_size, hidden=config["hidden"],
                layers=config["layers"], dropout=config["dropout"],
                bidir=config["bidir"], attn=config["attn"]).to(DEVICE)
            modelo = entrenar(modelo, loader_tr, loader_va, class_weights, config)

            logits_va = predecir_logits(modelo, d["X_va"])
            logits_te = predecir_logits(modelo, d["X_te"])
            logits_va_list.append(logits_va)
            logits_te_list.append(logits_te)

        # Soft voting (promediar softmax)
        probs_va = np.mean([torch.softmax(torch.tensor(l), dim=1).numpy() for l in logits_va_list], axis=0)
        probs_te = np.mean([torch.softmax(torch.tensor(l), dim=1).numpy() for l in logits_te_list], axis=0)
        preds_va = probs_va.argmax(axis=1)
        preds_te = probs_te.argmax(axis=1)

        met_val  = metricas_full(d["y_va"], preds_va, split_name="val")
        met_test = metricas_full(d["y_te"], preds_te, r_forward=d["r_fwd_test"], split_name="test")

        imprimir_metricas(f"{ticker} val ", met_val)
        imprimir_metricas(f"{ticker} test", met_test)

        # Guardar último modelo (representativo)
        torch.save({"state_dict": modelo.state_dict(),
                    "input_size": input_size, "config": config,
                    "feat_cols": d["feat_cols"], "lookback": lookback},
                   out_dir / f"{ticker}_modelo.pt")

        meta = {
            "ticker": ticker, "experimento": exp_id, "lookback": lookback,
            "config_id": config_id, "tipo": "por_ticker", "modelo": "LSTM",
            "arch_config": config, "n_features": input_size, "n_seeds": len(SEEDS),
            "metricas_val":  met_val,
            "metricas_test": met_test,
        }
        guardar_json(meta, out_dir / f"{ticker}_metricas.json")

        fila = {
            "config_id": config_id, "modelo": "LSTM", "tipo": "por_ticker",
            "ticker": ticker, "experimento": exp_id, "lookback": lookback,
            "n_features": input_size, "n_seeds": len(SEEDS),
            "val_f1_macro":  met_val["f1_macro"],
            "val_f1_buy":    met_val["f1_buy"],
            "val_f1_sell":   met_val["f1_sell"],
            "test_f1_macro": met_test["f1_macro"],
            "test_f1_buy":   met_test["f1_buy"],
            "test_f1_hold":  met_test["f1_hold"],
            "test_f1_sell":  met_test["f1_sell"],
            "test_f1_buy_sell_avg": met_test["f1_buy_sell_avg"],
            "test_accuracy": met_test["accuracy"],
            "test_signal_buy":  met_test["signal_distribution"]["BUY"]["pct"],
            "test_signal_hold": met_test["signal_distribution"]["HOLD"]["pct"],
            "test_signal_sell": met_test["signal_distribution"]["SELL"]["pct"],
        }
        for k in ["cumul_return_test", "return_vs_bh_test", "sharpe_test",
                  "max_drawdown_test", "win_rate_test", "profit_factor_test"]:
            fila[k] = met_test.get(k, None)
        resultados.append(fila)

    # ── GLOBAL ──
    print(f"\n  ── GLOBAL ─────────────────────────")
    g = preparar_datos_global(exp_id, lookback)
    cw_np = compute_class_weight("balanced", classes=np.array(CLASES), y=g["y_tr"])
    class_weights = torch.tensor(cw_np, dtype=torch.float32, device=DEVICE)
    loader_tr = make_loader(g["X_tr"], g["y_tr"], shuffle=True)
    loader_va = make_loader(g["X_va"], g["y_va"], shuffle=False)
    input_size = g["X_tr"].shape[2]
    print(f"  Train shape: {g['X_tr'].shape}  Val: {g['X_va'].shape}  Test: {g['X_te'].shape}")

    logits_va_list, logits_te_list = [], []
    for s in SEEDS:
        torch.manual_seed(s)
        np.random.seed(s)
        modelo = LSTMClasificador(
            input_size=input_size, hidden=config["hidden"],
            layers=config["layers"], dropout=config["dropout"],
            bidir=config["bidir"], attn=config["attn"]).to(DEVICE)
        modelo = entrenar(modelo, loader_tr, loader_va, class_weights, config)
        logits_va_list.append(predecir_logits(modelo, g["X_va"]))
        logits_te_list.append(predecir_logits(modelo, g["X_te"]))

    probs_va = np.mean([torch.softmax(torch.tensor(l), dim=1).numpy() for l in logits_va_list], axis=0)
    probs_te = np.mean([torch.softmax(torch.tensor(l), dim=1).numpy() for l in logits_te_list], axis=0)
    preds_va = probs_va.argmax(axis=1)
    preds_te = probs_te.argmax(axis=1)

    met_val  = metricas_full(g["y_va"], preds_va, split_name="val")
    met_test = metricas_full(g["y_te"], preds_te, r_forward=g["r_fwd_test"], split_name="test")
    met_por_ticker = metricas_global_por_ticker(
        g["y_te"], preds_te, g["ticker_test"], g["r_fwd_test"])

    imprimir_metricas("GLOBAL val ", met_val)
    imprimir_metricas("GLOBAL test", met_test)
    print("  Por ticker en GLOBAL test:")
    for tk, m in met_por_ticker.items():
        imprimir_metricas(f"    {tk}", m)

    torch.save({"state_dict": modelo.state_dict(),
                "input_size": input_size, "config": config,
                "feat_cols": g["feat_cols"], "lookback": lookback},
               out_dir / "modelo_global.pt")

    meta = {
        "ticker": "GLOBAL", "experimento": exp_id, "lookback": lookback,
        "config_id": config_id, "tipo": "global", "modelo": "LSTM",
        "arch_config": config, "n_features": input_size, "n_seeds": len(SEEDS),
        "metricas_val":  met_val,
        "metricas_test": met_test,
        "metricas_test_por_ticker": met_por_ticker,
    }
    guardar_json(meta, out_dir / "metricas_global.json")

    fila = {
        "config_id": config_id, "modelo": "LSTM", "tipo": "global",
        "ticker": "GLOBAL", "experimento": exp_id, "lookback": lookback,
        "n_features": input_size, "n_seeds": len(SEEDS),
        "val_f1_macro":  met_val["f1_macro"],
        "test_f1_macro": met_test["f1_macro"],
        "test_f1_buy":   met_test["f1_buy"],
        "test_f1_hold":  met_test["f1_hold"],
        "test_f1_sell":  met_test["f1_sell"],
        "test_f1_buy_sell_avg": met_test["f1_buy_sell_avg"],
        "test_accuracy": met_test["accuracy"],
        "test_signal_buy":  met_test["signal_distribution"]["BUY"]["pct"],
        "test_signal_hold": met_test["signal_distribution"]["HOLD"]["pct"],
        "test_signal_sell": met_test["signal_distribution"]["SELL"]["pct"],
    }
    for k in ["cumul_return_test", "return_vs_bh_test", "sharpe_test",
              "max_drawdown_test", "win_rate_test", "profit_factor_test"]:
        fila[k] = met_test.get(k, None)
    resultados.append(fila)

    return resultados


# ════════════════════════════════════════════════════════════════════════════
# PIPELINE
# ════════════════════════════════════════════════════════════════════════════

def pipeline(configs_a_correr=None, lookbacks=None, experimentos=None):
    print("="*70)
    print("  OPTIMIZACIÓN LSTM — MULTI-CONFIG MULTI-SEED + AMP")
    print("="*70)

    if configs_a_correr is None:
        configs_a_correr = list(CONFIGS.keys())
    if lookbacks is None:
        lookbacks = LOOKBACKS
    if experimentos is None:
        experimentos = list(EXPERIMENTOS.keys())

    if RESULTS_CSV.exists():
        df_prev = pd.read_csv(RESULTS_CSV)
        # Solo eliminar entradas previas de las MISMAS configs Y MISMAS lookbacks Y MISMAS experimentos
        # que vamos a correr (no eliminar otras combinaciones)
        mask = pd.Series([False] * len(df_prev))
        for cfg_id in configs_a_correr:
            for lb in lookbacks:
                for exp_id in experimentos:
                    m = ((df_prev["config_id"] == cfg_id) &
                         (df_prev["experimento"] == exp_id) &
                         (df_prev["lookback"] == lb))
                    mask = mask | m
        df_prev = df_prev[~mask]
        todos = df_prev.to_dict("records")
    else:
        todos = []

    t0 = time.time()
    for cfg_id in configs_a_correr:
        if cfg_id not in CONFIGS:
            print(f"⚠ Config {cfg_id} no existe, saltando.")
            continue
        cfg = CONFIGS[cfg_id]
        for lb in lookbacks:
            for exp_id in experimentos:
                res = correr_config(cfg_id, cfg, exp_id, lb)
                todos.extend(res)
                pd.DataFrame(todos).to_csv(RESULTS_CSV, index=False)

    dur = time.time() - t0
    print(f"\n{'='*70}")
    print(f"  TIEMPO TOTAL: {dur/60:.1f} min")
    print(f"  Resultados → {RESULTS_CSV}")
    print(f"{'='*70}")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--configs", nargs="+", default=None)
    p.add_argument("--lookbacks", nargs="+", type=int, default=None)
    p.add_argument("--experimentos", nargs="+", default=None)
    args = p.parse_args()
    pipeline(configs_a_correr=args.configs, lookbacks=args.lookbacks,
             experimentos=args.experimentos)
