"""
================================================================================
STACKING ENSEMBLE — Meta-modelo sobre 4 modelos base
================================================================================
1. Carga predicciones de LR, XGB, LSTM, CNN-LSTM (probabilidades + clase pred)
2. Construye features de meta-modelo:
   - probs softmax de cada modelo (3 probs × 4 modelos = 12 features)
   - clase predicha de cada modelo (4 features)
3. Entrena meta-modelo (LogisticRegression o XGBoost ligero) sobre val,
   evalúa sobre test.

Output: F1 final mejor que cualquier modelo individual.
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import sys, json, warnings, functools, pickle
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
                    cargar_dataset, cargar_global,
                    metricas_full, metricas_global_por_ticker,
                    guardar_json, imprimir_metricas, OUT_DIR)

import torch
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import f1_score
import xgboost as xgb
import pickle as pkl

OUT_STACK = OUT_DIR / "stacking"
OUT_STACK.mkdir(parents=True, exist_ok=True)
RESULTS_CSV = OUT_STACK / "resultados_stacking.csv"

MODELS_DIR = OUT_DIR / "modelos_optimizados"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Las mejores configs por modelo (basadas en F1 GLOBAL Exp B)
BEST_CONFIGS = {
    "LR":       {"config": "LR-02-elasticnet-all"},
    "XGB":      {"config": "XGB-01-all"},
    "LSTM":     {"config": "LSTM-02-bi", "lookback": 60},
    "CNN-LSTM": {"config": "CNN-01-base", "lookback": 20},
}


# ════════════════════════════════════════════════════════════════════════════
# CARGA DE MODELOS Y GENERACIÓN DE PROBS
# ════════════════════════════════════════════════════════════════════════════

def get_LR_probs(ticker, exp_id, X_va, X_te, tipo="por_ticker"):
    """Carga modelo LR optimizado y genera prob_va, prob_te."""
    cfg = BEST_CONFIGS["LR"]["config"]
    if tipo == "global":
        pkl_path = MODELS_DIR / "lr" / cfg / f"experimento_{exp_id}" / "modelo_global.pkl"
    else:
        pkl_path = MODELS_DIR / "lr" / cfg / f"experimento_{exp_id}" / f"{ticker}_modelo.pkl"
    if not pkl_path.exists():
        return None, None
    with open(pkl_path, "rb") as f:
        obj = pkl.load(f)
    scaler = obj["scaler"]
    model  = obj["model"]
    feat_cols = obj["feat_cols"]
    # Cargar datos consistentes con feat_cols guardados
    d = cargar_dataset(ticker, exp_id, feat_cols) if tipo == "por_ticker" \
        else cargar_global(exp_id, feat_cols)
    X_va_s = scaler.transform(d["X_va"])
    X_te_s = scaler.transform(d["X_te"])
    return model.predict_proba(X_va_s), model.predict_proba(X_te_s), d


def get_XGB_probs(ticker, exp_id, tipo="por_ticker"):
    cfg = BEST_CONFIGS["XGB"]["config"]
    if tipo == "global":
        m_path = MODELS_DIR / "xgboost" / cfg / f"experimento_{exp_id}" / "modelo_global.json"
    else:
        m_path = MODELS_DIR / "xgboost" / cfg / f"experimento_{exp_id}" / f"{ticker}_modelo.json"
    if not m_path.exists():
        return None, None, None
    model = xgb.XGBClassifier()
    model.load_model(str(m_path))
    # Cargar features all
    d = cargar_dataset(ticker, exp_id) if tipo == "por_ticker" \
        else cargar_global(exp_id)
    return model.predict_proba(d["X_va"]), model.predict_proba(d["X_te"]), d


def get_LSTM_probs(ticker, exp_id, tipo="por_ticker"):
    """Carga LSTM optimizado y genera probs."""
    sys.path.insert(0, str(Path(__file__).parent))
    from opt_lstm import LSTMClasificador, preparar_datos_ticker, preparar_datos_global
    cfg = BEST_CONFIGS["LSTM"]["config"]
    lb  = BEST_CONFIGS["LSTM"]["lookback"]
    if tipo == "global":
        m_path = MODELS_DIR / "lstm" / cfg / f"lookback_{lb}" / f"experimento_{exp_id}" / "modelo_global.pt"
    else:
        m_path = MODELS_DIR / "lstm" / cfg / f"lookback_{lb}" / f"experimento_{exp_id}" / f"{ticker}_modelo.pt"
    if not m_path.exists():
        return None, None, None
    ckpt = torch.load(m_path, map_location=DEVICE, weights_only=False)
    arch = ckpt["config"]
    modelo = LSTMClasificador(
        input_size=ckpt["input_size"], hidden=arch["hidden"],
        layers=arch["layers"], dropout=arch["dropout"],
        bidir=arch["bidir"], attn=arch["attn"]).to(DEVICE)
    modelo.load_state_dict(ckpt["state_dict"])
    modelo.eval()

    if tipo == "global":
        d = preparar_datos_global(exp_id, lb)
    else:
        d = preparar_datos_ticker(ticker, exp_id, lb)

    with torch.no_grad():
        probs_va = torch.softmax(modelo(torch.from_numpy(d["X_va"]).float().to(DEVICE)), dim=1).cpu().numpy()
        probs_te = torch.softmax(modelo(torch.from_numpy(d["X_te"]).float().to(DEVICE)), dim=1).cpu().numpy()
    return probs_va, probs_te, d


def get_CNN_probs(ticker, exp_id, tipo="por_ticker"):
    from opt_cnn_lstm import CNNLSTM, preparar_datos_cnn, preparar_datos_cnn_global
    cfg = BEST_CONFIGS["CNN-LSTM"]["config"]
    lb  = BEST_CONFIGS["CNN-LSTM"]["lookback"]
    if tipo == "global":
        m_path = MODELS_DIR / "cnn_lstm" / cfg / f"lookback_{lb}" / f"experimento_{exp_id}" / "modelo_global.pt"
    else:
        m_path = MODELS_DIR / "cnn_lstm" / cfg / f"lookback_{lb}" / f"experimento_{exp_id}" / f"{ticker}_modelo.pt"
    if not m_path.exists():
        return None, None, None
    ckpt = torch.load(m_path, map_location=DEVICE, weights_only=False)
    arch_cfg = ckpt["config"]
    modelo = CNNLSTM(input_size=ckpt["input_size"], config=arch_cfg).to(DEVICE)
    modelo.load_state_dict(ckpt["state_dict"])
    modelo.eval()

    if tipo == "global":
        d = preparar_datos_cnn_global(exp_id, lb)
    else:
        d = preparar_datos_cnn(ticker, exp_id, lb)
    with torch.no_grad():
        probs_va = torch.softmax(modelo(torch.from_numpy(d["X_va"]).float().to(DEVICE)), dim=1).cpu().numpy()
        probs_te = torch.softmax(modelo(torch.from_numpy(d["X_te"]).float().to(DEVICE)), dim=1).cpu().numpy()
    return probs_va, probs_te, d


# ════════════════════════════════════════════════════════════════════════════
# STACKING PARA UN TICKER (o GLOBAL)
# ════════════════════════════════════════════════════════════════════════════

def alinear_probs(*probs_lists, ys):
    """Las predicciones de modelos secuenciales (LSTM/CNN) tienen menos filas
    por el lookback. Alineamos todas a la longitud mínima desde el final.
    """
    min_va = min(p[0].shape[0] for p in probs_lists if p[0] is not None)
    min_te = min(p[1].shape[0] for p in probs_lists if p[1] is not None)
    out_va, out_te = [], []
    for probs_va, probs_te in probs_lists:
        if probs_va is None:
            out_va.append(np.full((min_va, 3), 1/3))
            out_te.append(np.full((min_te, 3), 1/3))
        else:
            out_va.append(probs_va[-min_va:])
            out_te.append(probs_te[-min_te:])
    y_va_aligned = ys["y_va"][-min_va:]
    y_te_aligned = ys["y_te"][-min_te:]
    r_fwd_aligned = ys["r_fwd_test"][-min_te:] if ys["r_fwd_test"] is not None else None
    return out_va, out_te, y_va_aligned, y_te_aligned, r_fwd_aligned


def stack_meta(probs_va_list, y_va, probs_te_list, meta_type="lr"):
    """Construye X_meta concatenando probs y entrena meta-modelo."""
    X_meta_va = np.concatenate(probs_va_list, axis=1)
    X_meta_te = np.concatenate(probs_te_list, axis=1)

    cw = compute_class_weight("balanced", classes=np.array([0, 1, 2]), y=y_va)
    cw_dict = {k: cw[i] for i, k in enumerate([0, 1, 2])}

    if meta_type == "lr":
        meta = LogisticRegression(C=1.0, max_iter=2000, class_weight=cw_dict,
                                   random_state=42, n_jobs=-1)
    else:
        meta = xgb.XGBClassifier(
            n_estimators=100, max_depth=3, learning_rate=0.1,
            objective="multi:softprob", num_class=3, eval_metric="mlogloss",
            tree_method="hist", random_state=42, n_jobs=-1, verbosity=0)
    meta.fit(X_meta_va, y_va)
    preds_te = meta.predict(X_meta_te)
    probs_te = meta.predict_proba(X_meta_te)
    return preds_te, probs_te, meta


# ════════════════════════════════════════════════════════════════════════════
# PIPELINE
# ════════════════════════════════════════════════════════════════════════════

def correr_exp(exp_id, meta_type="lr"):
    print(f"\n{'═'*70}\n  STACKING ({meta_type})  |  Exp {exp_id}\n{'═'*70}")
    resultados = []

    # ── POR TICKER ──
    print("\n  ── POR TICKER ──")
    for ticker in TICKERS:
        try:
            lr_va, lr_te, d_lr = get_LR_probs(ticker, exp_id)
        except Exception as e:
            print(f"  {ticker}: LR err {e}"); continue
        try:
            xgb_va, xgb_te, d_xg = get_XGB_probs(ticker, exp_id)
        except Exception as e:
            print(f"  {ticker}: XGB err {e}"); continue
        try:
            lstm_va, lstm_te, d_ls = get_LSTM_probs(ticker, exp_id)
        except Exception as e:
            print(f"  {ticker}: LSTM err {e}"); lstm_va, lstm_te, d_ls = None, None, None
        try:
            cnn_va, cnn_te, d_cn = get_CNN_probs(ticker, exp_id)
        except Exception as e:
            print(f"  {ticker}: CNN err {e}"); cnn_va, cnn_te, d_cn = None, None, None

        # Usar y_va/y_te del modelo secuencial más restrictivo (que tiene menos filas)
        ref = d_ls if d_ls is not None else (d_cn if d_cn is not None else d_lr)

        (probs_va_l, probs_te_l, y_va_a, y_te_a, r_fwd_a) = alinear_probs(
            (lr_va, lr_te), (xgb_va, xgb_te),
            (lstm_va, lstm_te), (cnn_va, cnn_te),
            ys={"y_va": ref["y_va"], "y_te": ref["y_te"], "r_fwd_test": ref["r_fwd_test"]})

        preds_te, probs_te, meta = stack_meta(probs_va_l, y_va_a, probs_te_l, meta_type)
        met = metricas_full(y_te_a, preds_te, r_forward=r_fwd_a, split_name="test")
        imprimir_metricas(f"  {ticker} stack", met)

        f = {
            "modelo": "STACKING-"+meta_type, "tipo": "por_ticker",
            "ticker": ticker, "experimento": exp_id,
            "test_f1_macro": met["f1_macro"],
            "test_f1_buy":   met["f1_buy"],
            "test_f1_hold":  met["f1_hold"],
            "test_f1_sell":  met["f1_sell"],
            "test_f1_buy_sell_avg": met["f1_buy_sell_avg"],
            "test_accuracy": met["accuracy"],
            "test_signal_buy":  met["signal_distribution"]["BUY"]["pct"],
            "test_signal_hold": met["signal_distribution"]["HOLD"]["pct"],
            "test_signal_sell": met["signal_distribution"]["SELL"]["pct"],
        }
        for k in ["cumul_return_test", "return_vs_bh_test", "sharpe_test",
                  "max_drawdown_test", "win_rate_test", "profit_factor_test"]:
            f[k] = met.get(k)
        resultados.append(f)

    # ── GLOBAL ──
    print("\n  ── GLOBAL ──")
    try:
        lr_va, lr_te, d_lr = get_LR_probs(None, exp_id, None, None, tipo="global")
    except Exception as e:
        print(f"  GLOBAL LR err: {e}"); return resultados
    try:
        xgb_va, xgb_te, d_xg = get_XGB_probs(None, exp_id, tipo="global")
    except Exception as e:
        print(f"  GLOBAL XGB err: {e}"); return resultados
    try:
        lstm_va, lstm_te, d_ls = get_LSTM_probs(None, exp_id, tipo="global")
    except Exception as e:
        print(f"  GLOBAL LSTM err: {e}"); lstm_va, lstm_te, d_ls = None, None, None
    try:
        cnn_va, cnn_te, d_cn = get_CNN_probs(None, exp_id, tipo="global")
    except Exception as e:
        print(f"  GLOBAL CNN err: {e}"); cnn_va, cnn_te, d_cn = None, None, None

    ref = d_ls if d_ls is not None else (d_cn if d_cn is not None else d_lr)
    (probs_va_l, probs_te_l, y_va_a, y_te_a, r_fwd_a) = alinear_probs(
        (lr_va, lr_te), (xgb_va, xgb_te),
        (lstm_va, lstm_te), (cnn_va, cnn_te),
        ys={"y_va": ref["y_va"], "y_te": ref["y_te"], "r_fwd_test": ref["r_fwd_test"]})

    preds_te, probs_te, meta = stack_meta(probs_va_l, y_va_a, probs_te_l, meta_type)
    met = metricas_full(y_te_a, preds_te, r_forward=r_fwd_a, split_name="test")
    imprimir_metricas("  GLOBAL stack", met)

    f = {
        "modelo": "STACKING-"+meta_type, "tipo": "global",
        "ticker": "GLOBAL", "experimento": exp_id,
        "test_f1_macro": met["f1_macro"],
        "test_f1_buy":   met["f1_buy"],
        "test_f1_hold":  met["f1_hold"],
        "test_f1_sell":  met["f1_sell"],
        "test_f1_buy_sell_avg": met["f1_buy_sell_avg"],
        "test_accuracy": met["accuracy"],
        "test_signal_buy":  met["signal_distribution"]["BUY"]["pct"],
        "test_signal_hold": met["signal_distribution"]["HOLD"]["pct"],
        "test_signal_sell": met["signal_distribution"]["SELL"]["pct"],
    }
    for k in ["cumul_return_test", "return_vs_bh_test", "sharpe_test",
              "max_drawdown_test", "win_rate_test", "profit_factor_test"]:
        f[k] = met.get(k)
    resultados.append(f)
    return resultados


def main():
    print("="*70)
    print("  STACKING ENSEMBLE — Meta-LR sobre 4 modelos optimizados")
    print("="*70)
    todos = []
    for exp_id in EXPERIMENTOS:
        for meta_type in ["lr", "xgb"]:
            res = correr_exp(exp_id, meta_type=meta_type)
            todos.extend(res)
            pd.DataFrame(todos).to_csv(RESULTS_CSV, index=False)

    if todos:
        df = pd.DataFrame(todos)
        for tipo in ["global", "por_ticker"]:
            sub = df[df["tipo"] == tipo]
            if sub.empty: continue
            print(f"\n  --- {tipo.upper()} ---")
            piv = sub.pivot_table(index="modelo", columns="experimento",
                                  values="test_f1_macro", aggfunc="mean")
            print(piv.round(4).to_string())


if __name__ == "__main__":
    main()
