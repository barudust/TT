"""
================================================================================
TRAIN ALL — los 5 modelos con dataset v3 (94 features) en una sola corrida
================================================================================
Modelos: LR (elasticnet), XGBoost (Optuna), LSTM (BiLSTM), CNN puro, CNN-LSTM
Para cada (modelo, exp, ticker/global, lookback?):
  - Mismas configs ganadoras del v1
  - Multi-seed=3 (rápido)
  - Métricas: F1-macro, Win Rate, Profit Factor, Max Drawdown

Salida: RESULTADOS_OPTIMIZADOS/v3/resultados_v3.csv (~120 filas)
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("PYTHONUNBUFFERED", "1")
import sys, time, warnings, functools, pickle
import numpy as np
import pandas as pd
from pathlib import Path

try: sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except: pass
print = functools.partial(print, flush=True)
warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).parent))
from common import (TICKERS, EXPERIMENTOS, CLASES, SPLITS,
                    metricas_full, metricas_global_por_ticker,
                    guardar_json, imprimir_metricas, OUT_DIR)
from common_v3 import cargar_dataset_v3, cargar_global_v3, cargar_raw_v3, get_feature_cols_v3

import time
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.utils.class_weight import compute_class_weight, compute_sample_weight
from sklearn.metrics import f1_score
import xgboost as xgb

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Dispositivo: {DEVICE}")

OUT_V3 = OUT_DIR / "v3"
OUT_V3.mkdir(parents=True, exist_ok=True)
RESULTS_CSV = OUT_V3 / "resultados_v3.csv"

SEEDS_DL = [42, 1, 7]
SEEDS_ML = [42, 1, 7, 2024, 100]
EPOCHS = 80; BATCH = 128; LR_ = 1e-3; WD = 1e-4; PATIENCE = 15
LOOKBACKS = [20, 60]

EXCLUIR = {"raw_open","raw_high","raw_low","raw_close","raw_volume",
           "target","r_forward","umbral_buy","umbral_sell"}


# ════════════════════════════════════════════════════════════════════════════
# MODELOS
# ════════════════════════════════════════════════════════════════════════════

def make_lr(C, l1_ratio=0.5, seed=42):
    return LogisticRegression(penalty="elasticnet", solver="saga",
        l1_ratio=l1_ratio, C=C, max_iter=2000, class_weight="balanced",
        random_state=seed, n_jobs=-1, tol=1e-3)


def make_xgb(p, seed=42):
    return xgb.XGBClassifier(
        n_estimators=p["n_estimators"], max_depth=p["max_depth"],
        learning_rate=p["learning_rate"], subsample=p["subsample"],
        colsample_bytree=p["colsample_bytree"], min_child_weight=p["min_child_weight"],
        gamma=p["gamma"], reg_alpha=p["reg_alpha"], reg_lambda=p["reg_lambda"],
        objective="multi:softprob", num_class=3, eval_metric="mlogloss",
        tree_method="hist", device="cuda", random_state=seed, n_jobs=-1, verbosity=0)


class LSTMBi(nn.Module):
    def __init__(self, input_size, hidden=128, layers=2, dropout=0.3):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden, layers, batch_first=True,
                            dropout=dropout if layers>1 else 0, bidirectional=True)
        out = hidden*2
        self.norm = nn.LayerNorm(out); self.drop = nn.Dropout(dropout)
        self.fc = nn.Linear(out, 3)
    def forward(self, x):
        out, _ = self.lstm(x)
        h = self.norm(out[:, -1, :])
        return self.fc(self.drop(h))


class CNNPuro(nn.Module):
    def __init__(self, input_size, filters=[64,128,192], dropout=0.3, fc_dim=128):
        super().__init__()
        layers = []
        c_in = input_size
        for f in filters:
            layers += [nn.Conv1d(c_in, f, 3, padding=1), nn.BatchNorm1d(f), nn.ReLU(), nn.Dropout(dropout)]
            c_in = f
        self.cnn = nn.Sequential(*layers)
        self.gap = nn.AdaptiveAvgPool1d(1); self.gmp = nn.AdaptiveMaxPool1d(1)
        self.fc = nn.Sequential(nn.Linear(filters[-1]*2, fc_dim), nn.ReLU(),
                                nn.Dropout(dropout), nn.Linear(fc_dim, 3))
    def forward(self, x):
        x = x.transpose(1,2)
        x = self.cnn(x)
        return self.fc(torch.cat([self.gap(x).squeeze(-1), self.gmp(x).squeeze(-1)], dim=1))


class CNNLSTM(nn.Module):
    """CNN-01-base equivalente: stack [64,128] → LSTM 128h."""
    def __init__(self, input_size, filters=[64,128], lstm_hidden=128, lstm_layers=2,
                 dropout=0.3):
        super().__init__()
        layers = []
        c_in = input_size
        for f in filters:
            layers += [nn.Conv1d(c_in, f, 3, padding=1), nn.BatchNorm1d(f), nn.ReLU(), nn.Dropout(dropout)]
            c_in = f
        self.cnn = nn.Sequential(*layers)
        self.lstm = nn.LSTM(filters[-1], lstm_hidden, lstm_layers, batch_first=True,
                            dropout=dropout if lstm_layers>1 else 0)
        self.norm = nn.LayerNorm(lstm_hidden); self.drop = nn.Dropout(dropout)
        self.fc = nn.Linear(lstm_hidden, 3)
    def forward(self, x):
        x = x.transpose(1,2); x = self.cnn(x); x = x.transpose(1,2)
        out, _ = self.lstm(x)
        return self.fc(self.drop(self.norm(out[:, -1, :])))


# ════════════════════════════════════════════════════════════════════════════
# DATOS SECUENCIALES
# ════════════════════════════════════════════════════════════════════════════

def split_temp(df, exp_id):
    s = SPLITS[exp_id]
    def cut(r): return df[(df.index>=r[0]) & (df.index<=r[1])]
    return cut(s["train"]), cut(s["val"]), cut(s["test"])


def seq(arr, target, lb):
    X, y = [], []
    for i in range(lb, len(arr)):
        X.append(arr[i-lb:i]); y.append(target[i])
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.int64)


def prep_seq_ticker(ticker, exp_id, lookback):
    df = cargar_raw_v3(ticker)
    feat = get_feature_cols_v3(df)
    df = df[feat + ["target", "r_forward"]].dropna()
    tr, va, te = split_temp(df, exp_id)
    r_fwd = te["r_forward"].values
    sc = MinMaxScaler()
    Xtr = sc.fit_transform(tr[feat].values)
    Xva = sc.transform(va[feat].values)
    Xte = sc.transform(te[feat].values)
    X_tr, y_tr = seq(Xtr, tr["target"].values, lookback)
    X_va, y_va = seq(Xva, va["target"].values, lookback)
    X_te, y_te = seq(Xte, te["target"].values, lookback)
    return {"X_tr":X_tr, "y_tr":y_tr, "X_va":X_va, "y_va":y_va,
            "X_te":X_te, "y_te":y_te, "r_fwd_test": r_fwd[lookback:],
            "feat_cols": feat}


def prep_seq_global(exp_id, lookback):
    Xtr_l, ytr_l, Xva_l, yva_l, Xte_l, yte_l, rfwd_l, tk_l = [],[],[],[],[],[],[],[]
    fc = None
    for tk in TICKERS:
        d = prep_seq_ticker(tk, exp_id, lookback)
        Xtr_l.append(d["X_tr"]); ytr_l.append(d["y_tr"])
        Xva_l.append(d["X_va"]); yva_l.append(d["y_va"])
        Xte_l.append(d["X_te"]); yte_l.append(d["y_te"])
        rfwd_l.append(d["r_fwd_test"]); tk_l.append(np.full(len(d["y_te"]), tk))
        if fc is None: fc = d["feat_cols"]
    return {"X_tr":np.vstack(Xtr_l).astype(np.float32), "y_tr":np.concatenate(ytr_l),
            "X_va":np.vstack(Xva_l).astype(np.float32), "y_va":np.concatenate(yva_l),
            "X_te":np.vstack(Xte_l).astype(np.float32), "y_te":np.concatenate(yte_l),
            "r_fwd_test":np.concatenate(rfwd_l), "ticker_test":np.concatenate(tk_l),
            "feat_cols": fc}


# ════════════════════════════════════════════════════════════════════════════
# ENTRENAMIENTOS
# ════════════════════════════════════════════════════════════════════════════

def make_loader(X, y, batch=BATCH, shuffle=True):
    return DataLoader(TensorDataset(torch.from_numpy(X).float(), torch.from_numpy(y).long()),
                       batch_size=batch, shuffle=shuffle, pin_memory=True)


def entrenar_dl(modelo, loader_tr, loader_va, cw, epochs=EPOCHS, patience=PATIENCE):
    crit = nn.CrossEntropyLoss(weight=cw)
    opt = optim.AdamW(modelo.parameters(), lr=LR_, weight_decay=WD)
    sch = optim.lr_scheduler.ReduceLROnPlateau(opt, mode="min", factor=0.5, patience=8, min_lr=1e-6)
    best=float("inf"); sin=0; best_st=None
    for ep in range(1, epochs+1):
        modelo.train()
        for Xb, yb in loader_tr:
            Xb=Xb.to(DEVICE, non_blocking=True); yb=yb.to(DEVICE, non_blocking=True)
            opt.zero_grad(); loss=crit(modelo(Xb), yb); loss.backward()
            nn.utils.clip_grad_norm_(modelo.parameters(), 1.0); opt.step()
        modelo.eval(); loss_va=0
        with torch.no_grad():
            for Xb, yb in loader_va:
                Xb=Xb.to(DEVICE); yb=yb.to(DEVICE)
                loss_va += crit(modelo(Xb), yb).item()
        loss_va /= len(loader_va); sch.step(loss_va)
        if loss_va < best:
            best=loss_va; sin=0
            best_st={k:v.detach().clone() for k,v in modelo.state_dict().items()}
        else: sin+=1
        if sin >= patience: break
    if best_st: modelo.load_state_dict(best_st)
    return modelo


def predecir_dl(modelo, X, batch=256):
    modelo.eval(); out=[]
    with torch.no_grad():
        for i in range(0, len(X), batch):
            xb = torch.from_numpy(X[i:i+batch]).float().to(DEVICE)
            out.append(F.softmax(modelo(xb), dim=1).cpu().numpy())
    return np.vstack(out)


def fila(modelo, tipo, ticker, exp_id, lookback, met_test):
    f = {"modelo": modelo, "tipo": tipo, "ticker": ticker,
         "experimento": exp_id, "lookback": lookback,
         "test_f1_macro":  met_test["f1_macro"],
         "test_f1_buy":    met_test["f1_buy"],
         "test_f1_sell":   met_test["f1_sell"],
         "test_f1_hold":   met_test["f1_hold"],
         "test_f1_buy_sell_avg": met_test["f1_buy_sell_avg"],
         "test_signal_buy":  met_test["signal_distribution"]["BUY"]["pct"],
         "test_signal_hold": met_test["signal_distribution"]["HOLD"]["pct"],
         "test_signal_sell": met_test["signal_distribution"]["SELL"]["pct"]}
    for k in ["cumul_return_test","return_vs_bh_test","sharpe_test",
              "max_drawdown_test","win_rate_test","profit_factor_test"]:
        f[k] = met_test.get(k)
    return f


def append_row(row, resultados):
    resultados.append(row)
    pd.DataFrame(resultados).to_csv(RESULTS_CSV, index=False)


# ════════════════════════════════════════════════════════════════════════════
# CORRIDAS POR MODELO
# ════════════════════════════════════════════════════════════════════════════

def run_lr(exp_id, resultados):
    print(f"\n  ── LR | Exp {exp_id} ──")
    # POR TICKER
    for tk in TICKERS:
        d = cargar_dataset_v3(tk, exp_id)
        sc = StandardScaler()
        Xtr = sc.fit_transform(d["X_tr"]); Xva = sc.transform(d["X_va"]); Xte = sc.transform(d["X_te"])
        # Buscar C en {0.01, 0.1, 1.0} con l1_ratio=0.5
        best_C=None; best_f1=-1
        for C in [0.01, 0.1, 1.0]:
            try:
                m = make_lr(C, 0.5, 42); m.fit(Xtr, d["y_tr"])
                f1 = f1_score(d["y_va"], m.predict(Xva), average="macro", zero_division=0)
                if f1>best_f1: best_f1=f1; best_C=C
            except: pass
        if best_C is None: continue
        # Multi-seed con majority voting
        Xfull = np.vstack([Xtr, Xva]); yfull = np.concatenate([d["y_tr"], d["y_va"]])
        preds_te = []
        for s in SEEDS_ML:
            m = make_lr(best_C, 0.5, s); m.fit(Xfull, yfull)
            preds_te.append(m.predict(Xte))
        preds_final = np.apply_along_axis(lambda x: np.bincount(x, minlength=3).argmax(),
                                          axis=0, arr=np.array(preds_te))
        met = metricas_full(d["y_te"], preds_final, r_forward=d["r_fwd_test"])
        imprimir_metricas(f"  LR {tk:6s}", met)
        append_row(fila("LR", "por_ticker", tk, exp_id, None, met), resultados)

    # GLOBAL
    g = cargar_global_v3(exp_id)
    sc = StandardScaler()
    Xtr = sc.fit_transform(g["X_tr"]); Xva = sc.transform(g["X_va"]); Xte = sc.transform(g["X_te"])
    best_C=None; best_f1=-1
    for C in [0.01, 0.1, 1.0]:
        try:
            m = make_lr(C, 0.5, 42); m.fit(Xtr, g["y_tr"])
            f1 = f1_score(g["y_va"], m.predict(Xva), average="macro", zero_division=0)
            if f1>best_f1: best_f1=f1; best_C=C
        except: pass
    Xfull = np.vstack([Xtr, Xva]); yfull = np.concatenate([g["y_tr"], g["y_va"]])
    preds_te = []
    for s in SEEDS_ML:
        m = make_lr(best_C, 0.5, s); m.fit(Xfull, yfull)
        preds_te.append(m.predict(Xte))
    preds_final = np.apply_along_axis(lambda x: np.bincount(x, minlength=3).argmax(),
                                      axis=0, arr=np.array(preds_te))
    met = metricas_full(g["y_te"], preds_final, r_forward=g["r_fwd_test"])
    imprimir_metricas("  LR GLOBAL", met)
    append_row(fila("LR", "global", "GLOBAL", exp_id, None, met), resultados)


def run_xgb(exp_id, resultados):
    import optuna
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    print(f"\n  ── XGB | Exp {exp_id} ──")

    def buscar_optuna(X_tr, y_tr, X_va, y_va, n_trials=25):
        sw = compute_sample_weight("balanced", y=y_tr)
        def obj(t):
            p = {
                "n_estimators":     t.suggest_int("n_estimators", 200, 600),
                "max_depth":        t.suggest_int("max_depth", 3, 8),
                "learning_rate":    t.suggest_float("learning_rate", 0.01, 0.2, log=True),
                "subsample":        t.suggest_float("subsample", 0.6, 1.0),
                "colsample_bytree": t.suggest_float("colsample_bytree", 0.4, 1.0),
                "min_child_weight": t.suggest_int("min_child_weight", 1, 10),
                "gamma":            t.suggest_float("gamma", 0.0, 1.5),
                "reg_alpha":        t.suggest_float("reg_alpha", 0.0, 2.5),
                "reg_lambda":       t.suggest_float("reg_lambda", 0.5, 4.0),
            }
            m = make_xgb(p, 42)
            m.fit(X_tr, y_tr, sample_weight=sw, eval_set=[(X_va, y_va)], verbose=False)
            return 1 - f1_score(y_va, m.predict(X_va), average="macro", zero_division=0)
        s = optuna.create_study(direction="minimize", sampler=optuna.samplers.TPESampler(seed=42))
        s.optimize(obj, n_trials=n_trials, show_progress_bar=False)
        return s.best_params

    for tk in TICKERS:
        d = cargar_dataset_v3(tk, exp_id)
        best = buscar_optuna(d["X_tr"], d["y_tr"], d["X_va"], d["y_va"], n_trials=20)
        Xfull = np.vstack([d["X_tr"], d["X_va"]]); yfull = np.concatenate([d["y_tr"], d["y_va"]])
        sw_full = compute_sample_weight("balanced", y=yfull)
        probs_te = []
        for s in SEEDS_DL:
            m = make_xgb(best, s); m.fit(Xfull, yfull, sample_weight=sw_full, verbose=False)
            probs_te.append(m.predict_proba(d["X_te"]))
        preds = np.mean(probs_te, axis=0).argmax(axis=1)
        met = metricas_full(d["y_te"], preds, r_forward=d["r_fwd_test"])
        imprimir_metricas(f"  XGB {tk:6s}", met)
        append_row(fila("XGBoost", "por_ticker", tk, exp_id, None, met), resultados)

    g = cargar_global_v3(exp_id)
    best = buscar_optuna(g["X_tr"], g["y_tr"], g["X_va"], g["y_va"], n_trials=40)
    Xfull = np.vstack([g["X_tr"], g["X_va"]]); yfull = np.concatenate([g["y_tr"], g["y_va"]])
    sw_full = compute_sample_weight("balanced", y=yfull)
    probs_te = []
    for s in SEEDS_DL:
        m = make_xgb(best, s); m.fit(Xfull, yfull, sample_weight=sw_full, verbose=False)
        probs_te.append(m.predict_proba(g["X_te"]))
    preds = np.mean(probs_te, axis=0).argmax(axis=1)
    met = metricas_full(g["y_te"], preds, r_forward=g["r_fwd_test"])
    imprimir_metricas("  XGB GLOBAL", met)
    append_row(fila("XGBoost", "global", "GLOBAL", exp_id, None, met), resultados)


def run_dl(model_class, model_name, exp_id, lookback, resultados, label):
    print(f"\n  ── {model_name} lb={lookback} | Exp {exp_id} ──")
    for tk in TICKERS:
        d = prep_seq_ticker(tk, exp_id, lookback)
        if len(d["X_tr"]) < 100: continue
        cw_np = compute_class_weight("balanced", classes=np.array(CLASES), y=d["y_tr"])
        cw = torch.tensor(cw_np, dtype=torch.float32, device=DEVICE)
        loader_tr = make_loader(d["X_tr"], d["y_tr"])
        loader_va = make_loader(d["X_va"], d["y_va"], shuffle=False)
        input_size = d["X_tr"].shape[2]
        probs_te_l = []
        for s in SEEDS_DL:
            torch.manual_seed(s); np.random.seed(s)
            m = model_class(input_size).to(DEVICE)
            m = entrenar_dl(m, loader_tr, loader_va, cw)
            probs_te_l.append(predecir_dl(m, d["X_te"]))
        preds = np.mean(probs_te_l, axis=0).argmax(axis=1)
        met = metricas_full(d["y_te"], preds, r_forward=d["r_fwd_test"])
        imprimir_metricas(f"  {label} {tk:6s}", met)
        append_row(fila(model_name, "por_ticker", tk, exp_id, lookback, met), resultados)

    g = prep_seq_global(exp_id, lookback)
    cw_np = compute_class_weight("balanced", classes=np.array(CLASES), y=g["y_tr"])
    cw = torch.tensor(cw_np, dtype=torch.float32, device=DEVICE)
    loader_tr = make_loader(g["X_tr"], g["y_tr"])
    loader_va = make_loader(g["X_va"], g["y_va"], shuffle=False)
    input_size = g["X_tr"].shape[2]
    probs_te_l = []
    for s in SEEDS_DL:
        torch.manual_seed(s); np.random.seed(s)
        m = model_class(input_size).to(DEVICE)
        m = entrenar_dl(m, loader_tr, loader_va, cw)
        probs_te_l.append(predecir_dl(m, g["X_te"]))
    preds = np.mean(probs_te_l, axis=0).argmax(axis=1)
    met = metricas_full(g["y_te"], preds, r_forward=g["r_fwd_test"])
    imprimir_metricas(f"  {label} GLOBAL", met)
    append_row(fila(model_name, "global", "GLOBAL", exp_id, lookback, met), resultados)


# ════════════════════════════════════════════════════════════════════════════
# PIPELINE
# ════════════════════════════════════════════════════════════════════════════

def main():
    print("="*70)
    print("  TRAIN ALL V3 — 5 modelos × 3 exps + dataset 94 features")
    print("="*70)

    if RESULTS_CSV.exists():
        df_prev = pd.read_csv(RESULTS_CSV)
        resultados = df_prev.to_dict("records")
        print(f"  Resumiendo con {len(resultados)} resultados previos")
    else:
        resultados = []

    t0 = time.time()
    for exp_id in EXPERIMENTOS:
        print(f"\n{'═'*70}\n  EXPERIMENTO {exp_id}\n{'═'*70}")
        run_lr(exp_id, resultados)
        run_xgb(exp_id, resultados)
        for lb in LOOKBACKS:
            run_dl(LSTMBi, "LSTM", exp_id, lb, resultados, f"LSTM{lb}")
            run_dl(CNNPuro, "CNN", exp_id, lb, resultados, f"CNN{lb}")
            run_dl(CNNLSTM, "CNN-LSTM", exp_id, lb, resultados, f"CNNL{lb}")

    print(f"\n{'='*70}\nTiempo total: {(time.time()-t0)/60:.1f} min")
    print(f"Resultados: {RESULTS_CSV}")


if __name__ == "__main__":
    main()
