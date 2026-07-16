"""
================================================================================
OPTIMIZACIÓN — CNN-LSTM (PyTorch + CUDA)
================================================================================
Mejoras sobre baseline:
  - Multi-kernel CNN (paralelo, Inception-style)
  - BiLSTM después de la CNN
  - Attention pooling temporal
  - Focal loss
  - Label smoothing
  - Más features (todas)
  - Multi-seed ensemble
  - OHLCV normalizadas localmente como canales adicionales
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("PYTHONUNBUFFERED", "1")
import sys
import time
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
                    cargar_raw,
                    metricas_full, metricas_global_por_ticker,
                    guardar_json, imprimir_metricas, OUT_DIR, SPLITS,
                    get_feature_cols)

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

OUT_CNN = OUT_DIR / "modelos_optimizados" / "cnn_lstm"
OUT_CNN.mkdir(parents=True, exist_ok=True)
RESULTS_CSV = OUT_CNN / "resultados_cnn_lstm_opt.csv"

OHLCV_COLS = ["raw_open", "raw_high", "raw_low", "raw_close", "raw_volume"]

LOOKBACKS  = [20, 60]
EPOCHS     = 100
BATCH_SIZE = 128
LR         = 1e-3
WD         = 1e-4
PATIENCE   = 20
SEEDS      = [42, 1, 7]


# ════════════════════════════════════════════════════════════════════════════
# CONFIGURACIONES
# ════════════════════════════════════════════════════════════════════════════

CONFIGS = {
    "CNN-01-base":         dict(cnn_type="stack", filters=[64, 128], kernels=[3, 3],
                                 lstm_hidden=128, lstm_layers=2, bidir=False, attn=False,
                                 dropout=0.3, loss="ce", label_smooth=0.0),
    "CNN-02-bi":           dict(cnn_type="stack", filters=[64, 128], kernels=[3, 3],
                                 lstm_hidden=128, lstm_layers=2, bidir=True, attn=False,
                                 dropout=0.3, loss="ce", label_smooth=0.0),
    "CNN-03-bi-attn":      dict(cnn_type="stack", filters=[64, 128], kernels=[3, 3],
                                 lstm_hidden=128, lstm_layers=2, bidir=True, attn=True,
                                 dropout=0.3, loss="ce", label_smooth=0.0),
    "CNN-04-multikernel":  dict(cnn_type="multi", filters=[64], kernels=[3, 5, 7],
                                 lstm_hidden=128, lstm_layers=2, bidir=True, attn=False,
                                 dropout=0.3, loss="ce", label_smooth=0.0),
    "CNN-05-focal":        dict(cnn_type="stack", filters=[64, 128], kernels=[3, 3],
                                 lstm_hidden=128, lstm_layers=2, bidir=True, attn=False,
                                 dropout=0.3, loss="focal", focal_gamma=2.0, label_smooth=0.0),
    "CNN-06-deeper":       dict(cnn_type="stack", filters=[64, 128, 192], kernels=[3, 3, 3],
                                 lstm_hidden=192, lstm_layers=3, bidir=True, attn=True,
                                 dropout=0.4, loss="ce", label_smooth=0.05),
}


# ════════════════════════════════════════════════════════════════════════════
# ARQUITECTURAS
# ════════════════════════════════════════════════════════════════════════════

class StackCNN(nn.Module):
    """CNN serial: secuencia de Conv1d -> BN -> ReLU -> Dropout."""
    def __init__(self, in_ch, filters, kernels, dropout):
        super().__init__()
        layers = []
        c_in = in_ch
        for f, k in zip(filters, kernels):
            layers += [
                nn.Conv1d(c_in, f, kernel_size=k, padding=k//2),
                nn.BatchNorm1d(f),
                nn.ReLU(),
                nn.Dropout(dropout),
            ]
            c_in = f
        self.body = nn.Sequential(*layers)
        self.out_ch = filters[-1]

    def forward(self, x):  # x: (B, C, T)
        return self.body(x)


class MultiKernelCNN(nn.Module):
    """CNN paralelo con múltiples kernels (Inception-style)."""
    def __init__(self, in_ch, filters_per_branch, kernels, dropout):
        super().__init__()
        f = filters_per_branch[0]
        self.branches = nn.ModuleList()
        for k in kernels:
            self.branches.append(nn.Sequential(
                nn.Conv1d(in_ch, f, kernel_size=k, padding=k//2),
                nn.BatchNorm1d(f),
                nn.ReLU(),
                nn.Dropout(dropout),
            ))
        self.out_ch = f * len(kernels)

    def forward(self, x):
        outs = [b(x) for b in self.branches]
        return torch.cat(outs, dim=1)


class Attention(nn.Module):
    def __init__(self, hidden):
        super().__init__()
        self.attn = nn.Linear(hidden, 1)
    def forward(self, x):
        # x: (B, T, H)
        w = F.softmax(self.attn(x), dim=1)
        return (x * w).sum(dim=1)


class CNNLSTM(nn.Module):
    def __init__(self, input_size, config):
        super().__init__()
        if config["cnn_type"] == "stack":
            self.cnn = StackCNN(input_size, config["filters"], config["kernels"], config["dropout"])
        else:
            self.cnn = MultiKernelCNN(input_size, config["filters"], config["kernels"], config["dropout"])

        self.lstm = nn.LSTM(input_size=self.cnn.out_ch,
                             hidden_size=config["lstm_hidden"],
                             num_layers=config["lstm_layers"],
                             batch_first=True,
                             dropout=config["dropout"] if config["lstm_layers"] > 1 else 0.0,
                             bidirectional=config["bidir"])
        lstm_out = config["lstm_hidden"] * (2 if config["bidir"] else 1)
        self.use_attn = config.get("attn", False)
        if self.use_attn:
            self.attn = Attention(lstm_out)
        self.norm = nn.LayerNorm(lstm_out)
        self.dropout = nn.Dropout(config["dropout"])
        self.fc = nn.Linear(lstm_out, 3)

    def forward(self, x):
        # x: (B, T, C)
        x = x.transpose(1, 2)             # (B, C, T)
        x = self.cnn(x)                   # (B, C', T)
        x = x.transpose(1, 2)             # (B, T, C')
        out, _ = self.lstm(x)             # (B, T, H)
        if self.use_attn:
            pooled = self.attn(out)
        else:
            pooled = out[:, -1, :]
        pooled = self.norm(pooled)
        pooled = self.dropout(pooled)
        return self.fc(pooled)


class FocalLoss(nn.Module):
    def __init__(self, gamma=2.0, weight=None):
        super().__init__()
        self.gamma = gamma
        self.weight = weight
    def forward(self, logits, targets):
        ce = F.cross_entropy(logits, targets, weight=self.weight, reduction="none")
        pt = torch.exp(-ce)
        return (((1 - pt) ** self.gamma) * ce).mean()


# ════════════════════════════════════════════════════════════════════════════
# DATOS
# ════════════════════════════════════════════════════════════════════════════

def normalizar_ohlcv_local(arr):
    """arr: (n, lookback, 5). Precios relativos al close[0], volumen /max."""
    arr = arr.astype(np.float32).copy()
    primer_close = arr[:, 0:1, 3:4]
    arr[:, :, :4] = arr[:, :, :4] / (primer_close + 1e-8)
    max_vol = arr[:, :, 4].max(axis=1, keepdims=True)
    arr[:, :, 4] = arr[:, :, 4] / (max_vol + 1e-8)
    return arr


def split_temporal(df, exp_id):
    s = SPLITS[exp_id]
    def corte(rng): return df[(df.index >= rng[0]) & (df.index <= rng[1])]
    return corte(s["train"]), corte(s["val"]), corte(s["test"])


def preparar_datos_cnn(ticker, exp_id, lookback, feat_cols=None):
    df = cargar_raw(ticker)
    if feat_cols is None:
        feat_cols = get_feature_cols(df)
    cols_a_usar = feat_cols + OHLCV_COLS + ["target", "r_forward"]
    df = df[cols_a_usar].dropna()
    tr, va, te = split_temporal(df, exp_id)
    r_fwd_test = te["r_forward"].values

    scaler = MinMaxScaler()
    Xtr_s = scaler.fit_transform(tr[feat_cols].values)
    Xva_s = scaler.transform(va[feat_cols].values)
    Xte_s = scaler.transform(te[feat_cols].values)
    OHLCV_tr = tr[OHLCV_COLS].values
    OHLCV_va = va[OHLCV_COLS].values
    OHLCV_te = te[OHLCV_COLS].values
    y_tr = tr["target"].values
    y_va = va["target"].values
    y_te = te["target"].values

    def construir(feats, ohlcv, y, lb):
        Xf, Xo, yy = [], [], []
        for i in range(lb, len(feats)):
            Xf.append(feats[i - lb:i])
            Xo.append(ohlcv[i - lb:i])
            yy.append(y[i])
        Xf = np.array(Xf, dtype=np.float32)
        Xo = np.array(Xo, dtype=np.float32)
        Xo = normalizar_ohlcv_local(Xo)
        X = np.concatenate([Xf, Xo], axis=2)
        return X, np.array(yy, dtype=np.int64)

    X_tr, y_tr_seq = construir(Xtr_s, OHLCV_tr, y_tr, lookback)
    X_va, y_va_seq = construir(Xva_s, OHLCV_va, y_va, lookback)
    X_te, y_te_seq = construir(Xte_s, OHLCV_te, y_te, lookback)
    r_fwd_test_align = r_fwd_test[lookback:]

    return {
        "X_tr": X_tr, "y_tr": y_tr_seq,
        "X_va": X_va, "y_va": y_va_seq,
        "X_te": X_te, "y_te": y_te_seq,
        "r_fwd_test": r_fwd_test_align,
        "feat_cols": feat_cols,
    }


def preparar_datos_cnn_global(exp_id, lookback, feat_cols=None):
    Xtr_l, ytr_l = [], []
    Xva_l, yva_l = [], []
    Xte_l, yte_l = [], []
    rfwd_te_l, tk_te_l = [], []
    feat_cols_ref = None
    for ticker in TICKERS:
        d = preparar_datos_cnn(ticker, exp_id, lookback, feat_cols)
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
    if config.get("loss") == "focal":
        return FocalLoss(gamma=config.get("focal_gamma", 2.0), weight=class_weights)
    return nn.CrossEntropyLoss(weight=class_weights,
                                label_smoothing=config.get("label_smooth", 0.0))


def entrenar(modelo, loader_tr, loader_va, class_weights, config,
             epochs=EPOCHS, patience=PATIENCE):
    criterio = get_loss(config, class_weights)
    opt = optim.AdamW(modelo.parameters(), lr=LR, weight_decay=WD)
    sched = optim.lr_scheduler.ReduceLROnPlateau(opt, mode="min", factor=0.5,
                                                   patience=8, min_lr=1e-6)
    best_va = float("inf"); sin_mej = 0; best_state = None
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
                Xb = Xb.to(DEVICE); yb = yb.to(DEVICE)
                logits = modelo(Xb)
                loss_va += criterio(logits, yb).item()
                preds.extend(torch.argmax(logits, 1).cpu().numpy())
                trues.extend(yb.cpu().numpy())
        loss_va /= len(loader_va)
        f1_va = f1_score(trues, preds, average="macro", zero_division=0)
        sched.step(loss_va)

        if loss_va < best_va:
            best_va = loss_va; sin_mej = 0
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
    print(f"  cnn={config['cnn_type']} filt={config['filters']} kers={config['kernels']} "
          f"bidir={config['bidir']} attn={config['attn']} loss={config.get('loss','ce')}")
    print(f"{'═'*70}")

    out_dir = OUT_CNN / config_id / f"lookback_{lookback}" / f"experimento_{exp_id}"
    out_dir.mkdir(parents=True, exist_ok=True)

    resultados = []

    # ── POR TICKER ──
    print(f"\n  ── POR TICKER ─────────────────────────")
    for ticker in TICKERS:
        d = preparar_datos_cnn(ticker, exp_id, lookback)
        if len(d["X_tr"]) < 100:
            continue
        cw_np = compute_class_weight("balanced", classes=np.array(CLASES), y=d["y_tr"])
        class_weights = torch.tensor(cw_np, dtype=torch.float32, device=DEVICE)
        loader_tr = make_loader(d["X_tr"], d["y_tr"], shuffle=True)
        loader_va = make_loader(d["X_va"], d["y_va"], shuffle=False)
        input_size = d["X_tr"].shape[2]

        logits_va_list, logits_te_list = [], []
        for s in SEEDS:
            torch.manual_seed(s); np.random.seed(s)
            modelo = CNNLSTM(input_size, config).to(DEVICE)
            modelo = entrenar(modelo, loader_tr, loader_va, class_weights, config)
            logits_va_list.append(predecir_logits(modelo, d["X_va"]))
            logits_te_list.append(predecir_logits(modelo, d["X_te"]))

        probs_va = np.mean([torch.softmax(torch.tensor(l), dim=1).numpy() for l in logits_va_list], axis=0)
        probs_te = np.mean([torch.softmax(torch.tensor(l), dim=1).numpy() for l in logits_te_list], axis=0)
        preds_va = probs_va.argmax(axis=1)
        preds_te = probs_te.argmax(axis=1)

        met_val  = metricas_full(d["y_va"], preds_va, split_name="val")
        met_test = metricas_full(d["y_te"], preds_te, r_forward=d["r_fwd_test"], split_name="test")

        imprimir_metricas(f"{ticker} val ", met_val)
        imprimir_metricas(f"{ticker} test", met_test)

        torch.save({"state_dict": modelo.state_dict(),
                    "input_size": input_size, "config": config,
                    "feat_cols": d["feat_cols"], "lookback": lookback},
                   out_dir / f"{ticker}_modelo.pt")

        meta = {
            "ticker": ticker, "experimento": exp_id, "lookback": lookback,
            "config_id": config_id, "tipo": "por_ticker", "modelo": "CNN-LSTM",
            "arch_config": config, "n_features": input_size, "n_seeds": len(SEEDS),
            "metricas_val":  met_val, "metricas_test": met_test,
        }
        guardar_json(meta, out_dir / f"{ticker}_metricas.json")

        fila = {
            "config_id": config_id, "modelo": "CNN-LSTM", "tipo": "por_ticker",
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
    g = preparar_datos_cnn_global(exp_id, lookback)
    cw_np = compute_class_weight("balanced", classes=np.array(CLASES), y=g["y_tr"])
    class_weights = torch.tensor(cw_np, dtype=torch.float32, device=DEVICE)
    loader_tr = make_loader(g["X_tr"], g["y_tr"], shuffle=True)
    loader_va = make_loader(g["X_va"], g["y_va"], shuffle=False)
    input_size = g["X_tr"].shape[2]
    print(f"  Train shape: {g['X_tr'].shape}")

    logits_va_list, logits_te_list = [], []
    for s in SEEDS:
        torch.manual_seed(s); np.random.seed(s)
        modelo = CNNLSTM(input_size, config).to(DEVICE)
        modelo = entrenar(modelo, loader_tr, loader_va, class_weights, config)
        logits_va_list.append(predecir_logits(modelo, g["X_va"]))
        logits_te_list.append(predecir_logits(modelo, g["X_te"]))

    probs_va = np.mean([torch.softmax(torch.tensor(l), dim=1).numpy() for l in logits_va_list], axis=0)
    probs_te = np.mean([torch.softmax(torch.tensor(l), dim=1).numpy() for l in logits_te_list], axis=0)
    preds_va = probs_va.argmax(axis=1)
    preds_te = probs_te.argmax(axis=1)

    met_val  = metricas_full(g["y_va"], preds_va, split_name="val")
    met_test = metricas_full(g["y_te"], preds_te, r_forward=g["r_fwd_test"], split_name="test")
    met_por_ticker = metricas_global_por_ticker(g["y_te"], preds_te, g["ticker_test"], g["r_fwd_test"])

    imprimir_metricas("GLOBAL val ", met_val)
    imprimir_metricas("GLOBAL test", met_test)
    for tk, m in met_por_ticker.items():
        imprimir_metricas(f"    {tk}", m)

    torch.save({"state_dict": modelo.state_dict(),
                "input_size": input_size, "config": config,
                "feat_cols": g["feat_cols"], "lookback": lookback},
               out_dir / "modelo_global.pt")
    meta = {
        "ticker": "GLOBAL", "experimento": exp_id, "lookback": lookback,
        "config_id": config_id, "tipo": "global", "modelo": "CNN-LSTM",
        "arch_config": config, "n_features": input_size, "n_seeds": len(SEEDS),
        "metricas_val":  met_val, "metricas_test": met_test,
        "metricas_test_por_ticker": met_por_ticker,
    }
    guardar_json(meta, out_dir / "metricas_global.json")

    fila = {
        "config_id": config_id, "modelo": "CNN-LSTM", "tipo": "global",
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
    print("  OPTIMIZACIÓN CNN-LSTM — MULTI-CONFIG MULTI-SEED")
    print("="*70)
    if configs_a_correr is None:
        configs_a_correr = list(CONFIGS.keys())
    if lookbacks is None:
        lookbacks = LOOKBACKS
    if experimentos is None:
        experimentos = list(EXPERIMENTOS.keys())

    if RESULTS_CSV.exists():
        df_prev = pd.read_csv(RESULTS_CSV)
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
