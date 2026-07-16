"""
================================================================================
CNN PURO — 5° modelo (sin LSTM)
================================================================================
Arquitectura:
  Input (B, lookback, n_features)
    → Transpose (B, n_features, lookback)
    → Conv1d block × 3 (filtros crecientes, BatchNorm, ReLU, Dropout)
    → MaxPool + AvgPool sobre dimensión temporal
    → Concatenar
    → Dense → Dropout → Dense → logits (3 clases)

Sin recurrencia, solo convoluciones 1D. Más rápido que LSTM/CNN-LSTM.
Multi-seed ensemble (3 seeds) para reducir varianza.
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("PYTHONUNBUFFERED", "1")
import sys, time, warnings, functools
import numpy as np
import pandas as pd
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception: pass
print = functools.partial(print, flush=True)
warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).parent))
from common import (TICKERS, EXPERIMENTOS, CLASES,
                    metricas_full, metricas_global_por_ticker,
                    guardar_json, imprimir_metricas, OUT_DIR, SPLITS,
                    cargar_raw, get_feature_cols)

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import MinMaxScaler
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import f1_score

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Dispositivo: {DEVICE}")

OUT_CNN = OUT_DIR / "modelos_optimizados" / "cnn_puro"
OUT_CNN.mkdir(parents=True, exist_ok=True)
RESULTS_CSV = OUT_CNN / "resultados_cnn_puro.csv"

LOOKBACKS  = [20, 60]
EPOCHS     = 100
BATCH_SIZE = 128
LR         = 1e-3
WD         = 1e-4
PATIENCE   = 20
SEEDS      = [42, 1, 7]


# ════════════════════════════════════════════════════════════════════════════
# ARQUITECTURA CNN PURO
# ════════════════════════════════════════════════════════════════════════════

class CNNPuro(nn.Module):
    """
    CNN 1D puro sin recurrencia.
    Bloques Conv1d con filtros crecientes, pooling al final.
    """
    def __init__(self, input_size, filters=[64, 128, 192], kernels=[3, 3, 3],
                 dropout=0.3, fc_dim=128, n_clases=3):
        super().__init__()
        layers = []
        in_ch = input_size
        for f, k in zip(filters, kernels):
            layers += [
                nn.Conv1d(in_ch, f, kernel_size=k, padding=k // 2),
                nn.BatchNorm1d(f),
                nn.ReLU(),
                nn.Dropout(dropout),
            ]
            in_ch = f
        self.cnn = nn.Sequential(*layers)
        # Global pooling: concatenamos max y avg pooling
        self.gap = nn.AdaptiveAvgPool1d(1)
        self.gmp = nn.AdaptiveMaxPool1d(1)
        pooled_dim = filters[-1] * 2  # avg + max
        self.fc = nn.Sequential(
            nn.Linear(pooled_dim, fc_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(fc_dim, n_clases),
        )
        self.config = {
            "input_size": input_size, "filters": filters, "kernels": kernels,
            "dropout": dropout, "fc_dim": fc_dim, "n_clases": n_clases,
        }

    def forward(self, x):
        # x: (B, T, C) → (B, C, T)
        x = x.transpose(1, 2)
        x = self.cnn(x)
        avg = self.gap(x).squeeze(-1)
        mx  = self.gmp(x).squeeze(-1)
        pooled = torch.cat([avg, mx], dim=1)
        return self.fc(pooled)


# ════════════════════════════════════════════════════════════════════════════
# DATOS (mismo preproc que LSTM)
# ════════════════════════════════════════════════════════════════════════════

EXCLUIR_COLS = {"raw_open", "raw_high", "raw_low", "raw_close", "raw_volume",
                "target", "r_forward", "umbral_buy", "umbral_sell"}


def split_temporal(df, exp_id):
    s = SPLITS[exp_id]
    def corte(rng): return df[(df.index >= rng[0]) & (df.index <= rng[1])]
    return corte(s["train"]), corte(s["val"]), corte(s["test"])


def construir_sec(feat_arr, target_arr, lookback):
    X, y = [], []
    for i in range(lookback, len(feat_arr)):
        X.append(feat_arr[i - lookback:i])
        y.append(target_arr[i])
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.int64)


def preparar_ticker(ticker, exp_id, lookback, feat_cols=None):
    df = cargar_raw(ticker)
    if feat_cols is None:
        feat_cols = get_feature_cols(df)
    df = df[feat_cols + ["target", "r_forward"]].dropna()
    tr, va, te = split_temporal(df, exp_id)
    r_fwd_test = te["r_forward"].values

    scaler = MinMaxScaler()
    Xtr = scaler.fit_transform(tr[feat_cols].values)
    Xva = scaler.transform(va[feat_cols].values)
    Xte = scaler.transform(te[feat_cols].values)

    X_tr, y_tr = construir_sec(Xtr, tr["target"].values, lookback)
    X_va, y_va = construir_sec(Xva, va["target"].values, lookback)
    X_te, y_te = construir_sec(Xte, te["target"].values, lookback)
    return {
        "X_tr": X_tr, "y_tr": y_tr,
        "X_va": X_va, "y_va": y_va,
        "X_te": X_te, "y_te": y_te,
        "r_fwd_test": r_fwd_test[lookback:],
        "feat_cols": feat_cols,
    }


def preparar_global(exp_id, lookback, feat_cols=None):
    Xtr_l, ytr_l = [], []
    Xva_l, yva_l = [], []
    Xte_l, yte_l = [], []
    rfwd_l, tk_l = [], []
    fc_ref = None
    for ticker in TICKERS:
        d = preparar_ticker(ticker, exp_id, lookback, feat_cols)
        Xtr_l.append(d["X_tr"]); ytr_l.append(d["y_tr"])
        Xva_l.append(d["X_va"]); yva_l.append(d["y_va"])
        Xte_l.append(d["X_te"]); yte_l.append(d["y_te"])
        rfwd_l.append(d["r_fwd_test"])
        tk_l.append(np.full(len(d["y_te"]), ticker))
        if fc_ref is None: fc_ref = d["feat_cols"]
    return {
        "X_tr": np.vstack(Xtr_l).astype(np.float32),
        "y_tr": np.concatenate(ytr_l),
        "X_va": np.vstack(Xva_l).astype(np.float32),
        "y_va": np.concatenate(yva_l),
        "X_te": np.vstack(Xte_l).astype(np.float32),
        "y_te": np.concatenate(yte_l),
        "r_fwd_test": np.concatenate(rfwd_l),
        "ticker_test": np.concatenate(tk_l),
        "feat_cols": fc_ref,
    }


# ════════════════════════════════════════════════════════════════════════════
# ENTRENAMIENTO
# ════════════════════════════════════════════════════════════════════════════

def make_loader(X, y, batch=BATCH_SIZE, shuffle=True):
    Xt = torch.from_numpy(X).float()
    yt = torch.from_numpy(y).long()
    return DataLoader(TensorDataset(Xt, yt), batch_size=batch,
                       shuffle=shuffle, pin_memory=True)


def entrenar(modelo, loader_tr, loader_va, class_weights, epochs=EPOCHS, patience=PATIENCE):
    criterio = nn.CrossEntropyLoss(weight=class_weights)
    opt = optim.AdamW(modelo.parameters(), lr=LR, weight_decay=WD)
    sched = optim.lr_scheduler.ReduceLROnPlateau(opt, mode="min", factor=0.5,
                                                   patience=8, min_lr=1e-6)
    best_va = float("inf"); sin_mej = 0; best_state = None
    for ep in range(1, epochs + 1):
        modelo.train()
        for Xb, yb in loader_tr:
            Xb = Xb.to(DEVICE, non_blocking=True); yb = yb.to(DEVICE, non_blocking=True)
            opt.zero_grad()
            loss = criterio(modelo(Xb), yb)
            loss.backward()
            nn.utils.clip_grad_norm_(modelo.parameters(), 1.0)
            opt.step()
        modelo.eval()
        loss_va = 0.0; preds, trues = [], []
        with torch.no_grad():
            for Xb, yb in loader_va:
                Xb = Xb.to(DEVICE); yb = yb.to(DEVICE)
                lo = modelo(Xb)
                loss_va += criterio(lo, yb).item()
                preds.extend(torch.argmax(lo, 1).cpu().numpy())
                trues.extend(yb.cpu().numpy())
        loss_va /= len(loader_va)
        f1_va = f1_score(trues, preds, average="macro", zero_division=0)
        sched.step(loss_va)
        if loss_va < best_va:
            best_va = loss_va; sin_mej = 0
            best_state = {k: v.detach().clone() for k, v in modelo.state_dict().items()}
        else:
            sin_mej += 1
        if ep % 20 == 0:
            print(f"      Ep{ep:3d}/{epochs} va_loss={loss_va:.4f} f1_va={f1_va:.3f}")
        if sin_mej >= patience:
            print(f"      Early stop ep{ep}")
            break
    if best_state: modelo.load_state_dict(best_state)
    return modelo


def predecir_logits(modelo, X, batch=256):
    modelo.eval(); out = []
    with torch.no_grad():
        for i in range(0, len(X), batch):
            xb = torch.from_numpy(X[i:i+batch]).float().to(DEVICE)
            out.append(modelo(xb).cpu().numpy())
    return np.vstack(out)


# ════════════════════════════════════════════════════════════════════════════
# UN EXPERIMENTO
# ════════════════════════════════════════════════════════════════════════════

def correr(exp_id, lookback):
    print(f"\n{'═'*70}\n  CNN PURO  |  Exp {exp_id}  |  lb={lookback}\n{'═'*70}")
    out_dir = OUT_CNN / f"lookback_{lookback}" / f"experimento_{exp_id}"
    out_dir.mkdir(parents=True, exist_ok=True)
    resultados = []

    print("\n  ── POR TICKER ──")
    for ticker in TICKERS:
        d = preparar_ticker(ticker, exp_id, lookback)
        if len(d["X_tr"]) < 100:
            print(f"  {ticker}: datos insuficientes"); continue
        cw_np = compute_class_weight("balanced", classes=np.array(CLASES), y=d["y_tr"])
        cw = torch.tensor(cw_np, dtype=torch.float32, device=DEVICE)
        loader_tr = make_loader(d["X_tr"], d["y_tr"], shuffle=True)
        loader_va = make_loader(d["X_va"], d["y_va"], shuffle=False)
        input_size = d["X_tr"].shape[2]

        logits_va_l, logits_te_l = [], []
        for s in SEEDS:
            torch.manual_seed(s); np.random.seed(s)
            m = CNNPuro(input_size=input_size).to(DEVICE)
            m = entrenar(m, loader_tr, loader_va, cw)
            logits_va_l.append(predecir_logits(m, d["X_va"]))
            logits_te_l.append(predecir_logits(m, d["X_te"]))

        probs_va = np.mean([F.softmax(torch.tensor(l), dim=1).numpy() for l in logits_va_l], axis=0)
        probs_te = np.mean([F.softmax(torch.tensor(l), dim=1).numpy() for l in logits_te_l], axis=0)
        preds_va = probs_va.argmax(axis=1)
        preds_te = probs_te.argmax(axis=1)
        met_val  = metricas_full(d["y_va"], preds_va, split_name="val")
        met_test = metricas_full(d["y_te"], preds_te, r_forward=d["r_fwd_test"], split_name="test")
        imprimir_metricas(f"  {ticker} test", met_test)

        torch.save({"state_dict": m.state_dict(), "config": m.config,
                    "input_size": input_size, "feat_cols": d["feat_cols"], "lookback": lookback},
                   out_dir / f"{ticker}_modelo.pt")
        meta = {"ticker": ticker, "experimento": exp_id, "lookback": lookback,
                "config_id": "CNN-puro", "tipo": "por_ticker", "modelo": "CNN",
                "arch_config": m.config, "n_features": input_size, "n_seeds": len(SEEDS),
                "metricas_val": met_val, "metricas_test": met_test}
        guardar_json(meta, out_dir / f"{ticker}_metricas.json")

        f = {"config_id": "CNN-puro", "modelo": "CNN", "tipo": "por_ticker",
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
             "test_signal_buy":  met_test["signal_distribution"]["BUY"]["pct"],
             "test_signal_hold": met_test["signal_distribution"]["HOLD"]["pct"],
             "test_signal_sell": met_test["signal_distribution"]["SELL"]["pct"]}
        for k in ["cumul_return_test","return_vs_bh_test","sharpe_test",
                  "max_drawdown_test","win_rate_test","profit_factor_test"]:
            f[k] = met_test.get(k)
        resultados.append(f)

    # GLOBAL
    print("\n  ── GLOBAL ──")
    g = preparar_global(exp_id, lookback)
    cw_np = compute_class_weight("balanced", classes=np.array(CLASES), y=g["y_tr"])
    cw = torch.tensor(cw_np, dtype=torch.float32, device=DEVICE)
    loader_tr = make_loader(g["X_tr"], g["y_tr"])
    loader_va = make_loader(g["X_va"], g["y_va"], shuffle=False)
    input_size = g["X_tr"].shape[2]
    print(f"  Train shape: {g['X_tr'].shape}")

    logits_va_l, logits_te_l = [], []
    for s in SEEDS:
        torch.manual_seed(s); np.random.seed(s)
        m = CNNPuro(input_size=input_size).to(DEVICE)
        m = entrenar(m, loader_tr, loader_va, cw)
        logits_va_l.append(predecir_logits(m, g["X_va"]))
        logits_te_l.append(predecir_logits(m, g["X_te"]))

    probs_va = np.mean([F.softmax(torch.tensor(l), dim=1).numpy() for l in logits_va_l], axis=0)
    probs_te = np.mean([F.softmax(torch.tensor(l), dim=1).numpy() for l in logits_te_l], axis=0)
    preds_va = probs_va.argmax(axis=1)
    preds_te = probs_te.argmax(axis=1)
    met_val  = metricas_full(g["y_va"], preds_va, split_name="val")
    met_test = metricas_full(g["y_te"], preds_te, r_forward=g["r_fwd_test"], split_name="test")
    mt_pt = metricas_global_por_ticker(g["y_te"], preds_te, g["ticker_test"], g["r_fwd_test"])
    imprimir_metricas("  GLOBAL test", met_test)

    torch.save({"state_dict": m.state_dict(), "config": m.config,
                "input_size": input_size, "feat_cols": g["feat_cols"], "lookback": lookback},
               out_dir / "modelo_global.pt")
    meta = {"ticker": "GLOBAL", "experimento": exp_id, "lookback": lookback,
            "config_id": "CNN-puro", "tipo": "global", "modelo": "CNN",
            "arch_config": m.config, "n_features": input_size, "n_seeds": len(SEEDS),
            "metricas_val": met_val, "metricas_test": met_test,
            "metricas_test_por_ticker": mt_pt}
    guardar_json(meta, out_dir / "metricas_global.json")
    f = {"config_id": "CNN-puro", "modelo": "CNN", "tipo": "global",
         "ticker": "GLOBAL", "experimento": exp_id, "lookback": lookback,
         "n_features": input_size, "n_seeds": len(SEEDS),
         "val_f1_macro":  met_val["f1_macro"],
         "test_f1_macro": met_test["f1_macro"],
         "test_f1_buy":   met_test["f1_buy"],
         "test_f1_hold":  met_test["f1_hold"],
         "test_f1_sell":  met_test["f1_sell"],
         "test_f1_buy_sell_avg": met_test["f1_buy_sell_avg"],
         "test_signal_buy":  met_test["signal_distribution"]["BUY"]["pct"],
         "test_signal_hold": met_test["signal_distribution"]["HOLD"]["pct"],
         "test_signal_sell": met_test["signal_distribution"]["SELL"]["pct"]}
    for k in ["cumul_return_test","return_vs_bh_test","sharpe_test",
              "max_drawdown_test","win_rate_test","profit_factor_test"]:
        f[k] = met_test.get(k)
    resultados.append(f)
    return resultados


def main():
    print("="*70)
    print("  CNN PURO — 5° modelo (sin LSTM)")
    print("="*70)
    if RESULTS_CSV.exists():
        df_prev = pd.read_csv(RESULTS_CSV)
        todos = df_prev.to_dict("records")
    else:
        todos = []

    t0 = time.time()
    for lb in LOOKBACKS:
        for exp_id in EXPERIMENTOS:
            # Skip si ya está
            df_check = pd.DataFrame(todos)
            if not df_check.empty:
                done = df_check[(df_check["experimento"]==exp_id) & (df_check["lookback"]==lb)]
                if len(done) == 8:  # 7 tickers + 1 global
                    print(f"\n  Skipping Exp {exp_id} lb={lb} (ya hecho)")
                    continue
                # remove partial
                todos = df_check[~((df_check["experimento"]==exp_id) & (df_check["lookback"]==lb))].to_dict("records")
            res = correr(exp_id, lb)
            todos.extend(res)
            pd.DataFrame(todos).to_csv(RESULTS_CSV, index=False)
    print(f"\nTiempo: {(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    main()
