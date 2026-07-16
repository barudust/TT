"""
================================================================================
SOFT VOTING ENSEMBLE — Promedio ponderado de probabilidades
================================================================================
Más simple y robusto que stacking. Busca pesos óptimos en val
para combinar las probs de los 4 modelos. Evita overfitting del meta-modelo.
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import sys, json, warnings, functools, pickle as pkl
from itertools import product
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
import xgboost as xgb
from sklearn.metrics import f1_score

OUT_SV = OUT_DIR / "soft_voting"
OUT_SV.mkdir(parents=True, exist_ok=True)
RESULTS_CSV = OUT_SV / "resultados_soft_voting.csv"
MODELS_DIR = OUT_DIR / "modelos_optimizados"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

BEST_CONFIGS = {
    "LR":       {"config": "LR-02-elasticnet-all"},
    "XGB":      {"config": "XGB-01-all"},
    "LSTM":     {"config": "LSTM-02-bi", "lookback": 60},
    "CNN-LSTM": {"config": "CNN-01-base", "lookback": 20},
}


# ════════════════════════════════════════════════════════════════════════════
# CARGADORES DE PROBS (cada uno usa su propio preprocesamiento)
# ════════════════════════════════════════════════════════════════════════════

def get_LR_probs(ticker, exp_id, tipo="por_ticker"):
    cfg = BEST_CONFIGS["LR"]["config"]
    if tipo == "global":
        pkl_path = MODELS_DIR / "lr" / cfg / f"experimento_{exp_id}" / "modelo_global.pkl"
    else:
        pkl_path = MODELS_DIR / "lr" / cfg / f"experimento_{exp_id}" / f"{ticker}_modelo.pkl"
    if not pkl_path.exists():
        return None, None, None
    with open(pkl_path, "rb") as f:
        obj = pkl.load(f)
    feat_cols = obj["feat_cols"]
    d = cargar_dataset(ticker, exp_id, feat_cols) if tipo == "por_ticker" \
        else cargar_global(exp_id, feat_cols)
    X_va_s = obj["scaler"].transform(d["X_va"])
    X_te_s = obj["scaler"].transform(d["X_te"])
    return obj["model"].predict_proba(X_va_s), obj["model"].predict_proba(X_te_s), d


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
    d = cargar_dataset(ticker, exp_id) if tipo == "por_ticker" else cargar_global(exp_id)
    return model.predict_proba(d["X_va"]), model.predict_proba(d["X_te"]), d


def get_LSTM_probs(ticker, exp_id, tipo="por_ticker"):
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
    modelo.load_state_dict(ckpt["state_dict"]); modelo.eval()
    d = preparar_datos_global(exp_id, lb) if tipo == "global" else preparar_datos_ticker(ticker, exp_id, lb)
    with torch.no_grad():
        pv = torch.softmax(modelo(torch.from_numpy(d["X_va"]).float().to(DEVICE)), dim=1).cpu().numpy()
        pt = torch.softmax(modelo(torch.from_numpy(d["X_te"]).float().to(DEVICE)), dim=1).cpu().numpy()
    return pv, pt, d


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
    modelo = CNNLSTM(input_size=ckpt["input_size"], config=ckpt["config"]).to(DEVICE)
    modelo.load_state_dict(ckpt["state_dict"]); modelo.eval()
    d = preparar_datos_cnn_global(exp_id, lb) if tipo == "global" else preparar_datos_cnn(ticker, exp_id, lb)
    with torch.no_grad():
        pv = torch.softmax(modelo(torch.from_numpy(d["X_va"]).float().to(DEVICE)), dim=1).cpu().numpy()
        pt = torch.softmax(modelo(torch.from_numpy(d["X_te"]).float().to(DEVICE)), dim=1).cpu().numpy()
    return pv, pt, d


# ════════════════════════════════════════════════════════════════════════════
# ALINEACIÓN Y BÚSQUEDA DE PESOS
# ════════════════════════════════════════════════════════════════════════════

def alinear(probs_list, y_va, y_te, r_fwd):
    """Toma lista de (pv, pt) - posibles None - retorna alineado al min len."""
    valid = [(pv, pt) for (pv, pt) in probs_list if pv is not None]
    if not valid:
        return None, None, None, None, None
    min_va = min(p[0].shape[0] for p in valid)
    min_te = min(p[1].shape[0] for p in valid)
    out_va = []
    out_te = []
    mask = []
    for pv, pt in probs_list:
        if pv is None:
            out_va.append(None); out_te.append(None); mask.append(False)
        else:
            out_va.append(pv[-min_va:])
            out_te.append(pt[-min_te:])
            mask.append(True)
    y_va_a = y_va[-min_va:]
    y_te_a = y_te[-min_te:]
    r_fwd_a = r_fwd[-min_te:] if r_fwd is not None else None
    return out_va, out_te, y_va_a, y_te_a, r_fwd_a


def buscar_pesos(probs_va_list, y_va):
    """Grid search sobre pesos w1,w2,w3,w4 (sum=1) que maximizan F1-macro val."""
    valid_idx = [i for i, p in enumerate(probs_va_list) if p is not None]
    if not valid_idx:
        return None
    # Grid search: cada peso en [0, 0.25, 0.5, 0.75, 1.0]; normalizamos
    vals = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    mejor = {"f1": -1, "w": None}
    n_valid = len(valid_idx)
    # iterar combinaciones de pesos
    for combo in product(vals, repeat=n_valid):
        s = sum(combo)
        if s < 1e-6:
            continue
        w = [c/s for c in combo]  # normalizar
        # combinar probs
        avg = np.zeros_like(probs_va_list[valid_idx[0]])
        for j, idx in enumerate(valid_idx):
            avg += w[j] * probs_va_list[idx]
        pred = avg.argmax(axis=1)
        f1 = f1_score(y_va, pred, average="macro", zero_division=0)
        if f1 > mejor["f1"]:
            full_w = [0.0] * len(probs_va_list)
            for j, idx in enumerate(valid_idx):
                full_w[idx] = w[j]
            mejor = {"f1": f1, "w": full_w}
    return mejor


def aplicar_pesos(probs_list, w):
    avg = None
    for i, p in enumerate(probs_list):
        if p is None or w[i] == 0:
            continue
        if avg is None:
            avg = w[i] * p
        else:
            avg += w[i] * p
    return avg


def correr_exp(exp_id):
    print(f"\n{'═'*70}\n  SOFT VOTING  |  Exp {exp_id}\n{'═'*70}")
    resultados = []

    print("\n  ── POR TICKER ──")
    for ticker in TICKERS:
        try:
            lr_pv, lr_pt, d_lr = get_LR_probs(ticker, exp_id)
            xgb_pv, xgb_pt, d_xg = get_XGB_probs(ticker, exp_id)
            lstm_pv, lstm_pt, d_ls = get_LSTM_probs(ticker, exp_id)
            cnn_pv, cnn_pt, d_cn = get_CNN_probs(ticker, exp_id)
        except Exception as e:
            print(f"  {ticker}: err {e}"); continue

        ref = d_ls if d_ls else (d_cn if d_cn else d_lr)
        probs_list = [(lr_pv, lr_pt), (xgb_pv, xgb_pt), (lstm_pv, lstm_pt), (cnn_pv, cnn_pt)]
        out_va, out_te, y_va_a, y_te_a, r_fwd_a = alinear(
            probs_list, ref["y_va"], ref["y_te"], ref["r_fwd_test"])

        w_res = buscar_pesos(out_va, y_va_a)
        if w_res is None:
            print(f"  {ticker}: sin pesos válidos"); continue
        w = w_res["w"]
        probs_te = aplicar_pesos(out_te, w)
        preds_te = probs_te.argmax(axis=1)
        met = metricas_full(y_te_a, preds_te, r_forward=r_fwd_a, split_name="test")
        print(f"  {ticker}: w={[round(x,2) for x in w]} f1={met['f1_macro']:.3f} "
              f"sh={met.get('sharpe_test', '-')}")
        resultados.append({
            "modelo": "SoftVoting", "tipo": "por_ticker",
            "ticker": ticker, "experimento": exp_id,
            "w_lr": w[0], "w_xgb": w[1], "w_lstm": w[2], "w_cnn": w[3],
            "test_f1_macro": met["f1_macro"],
            "test_f1_buy":   met["f1_buy"],
            "test_f1_hold":  met["f1_hold"],
            "test_f1_sell":  met["f1_sell"],
            "test_f1_buy_sell_avg": met["f1_buy_sell_avg"],
            "test_accuracy": met["accuracy"],
            "test_signal_buy":  met["signal_distribution"]["BUY"]["pct"],
            "test_signal_hold": met["signal_distribution"]["HOLD"]["pct"],
            "test_signal_sell": met["signal_distribution"]["SELL"]["pct"],
            "cumul_return_test":  met.get("cumul_return_test"),
            "return_vs_bh_test":  met.get("return_vs_bh_test"),
            "sharpe_test":        met.get("sharpe_test"),
            "max_drawdown_test":  met.get("max_drawdown_test"),
            "win_rate_test":      met.get("win_rate_test"),
            "profit_factor_test": met.get("profit_factor_test"),
        })

    # GLOBAL
    print("\n  ── GLOBAL ──")
    try:
        lr_pv, lr_pt, d_lr = get_LR_probs(None, exp_id, tipo="global")
        xgb_pv, xgb_pt, d_xg = get_XGB_probs(None, exp_id, tipo="global")
        lstm_pv, lstm_pt, d_ls = get_LSTM_probs(None, exp_id, tipo="global")
        cnn_pv, cnn_pt, d_cn = get_CNN_probs(None, exp_id, tipo="global")
    except Exception as e:
        print(f"  GLOBAL err {e}"); return resultados
    ref = d_ls if d_ls else (d_cn if d_cn else d_lr)
    probs_list = [(lr_pv, lr_pt), (xgb_pv, xgb_pt), (lstm_pv, lstm_pt), (cnn_pv, cnn_pt)]
    out_va, out_te, y_va_a, y_te_a, r_fwd_a = alinear(
        probs_list, ref["y_va"], ref["y_te"], ref["r_fwd_test"])
    w_res = buscar_pesos(out_va, y_va_a)
    if w_res is None:
        return resultados
    w = w_res["w"]
    probs_te = aplicar_pesos(out_te, w)
    preds_te = probs_te.argmax(axis=1)
    met = metricas_full(y_te_a, preds_te, r_forward=r_fwd_a, split_name="test")
    print(f"  GLOBAL: w={[round(x,2) for x in w]} f1={met['f1_macro']:.3f} "
          f"sh={met.get('sharpe_test', '-')}")
    resultados.append({
        "modelo": "SoftVoting", "tipo": "global",
        "ticker": "GLOBAL", "experimento": exp_id,
        "w_lr": w[0], "w_xgb": w[1], "w_lstm": w[2], "w_cnn": w[3],
        "test_f1_macro": met["f1_macro"],
        "test_f1_buy":   met["f1_buy"],
        "test_f1_hold":  met["f1_hold"],
        "test_f1_sell":  met["f1_sell"],
        "test_f1_buy_sell_avg": met["f1_buy_sell_avg"],
        "test_accuracy": met["accuracy"],
        "test_signal_buy":  met["signal_distribution"]["BUY"]["pct"],
        "test_signal_hold": met["signal_distribution"]["HOLD"]["pct"],
        "test_signal_sell": met["signal_distribution"]["SELL"]["pct"],
        "cumul_return_test":  met.get("cumul_return_test"),
        "return_vs_bh_test":  met.get("return_vs_bh_test"),
        "sharpe_test":        met.get("sharpe_test"),
        "max_drawdown_test":  met.get("max_drawdown_test"),
        "win_rate_test":      met.get("win_rate_test"),
        "profit_factor_test": met.get("profit_factor_test"),
    })
    return resultados


def main():
    print("="*70)
    print("  SOFT VOTING — Búsqueda de pesos óptimos por modelo")
    print("="*70)
    todos = []
    for exp_id in EXPERIMENTOS:
        res = correr_exp(exp_id)
        todos.extend(res)
        pd.DataFrame(todos).to_csv(RESULTS_CSV, index=False)

    if todos:
        df = pd.DataFrame(todos)
        print("\nGLOBAL F1-macro test:")
        print(df[df["tipo"]=="global"][["experimento","test_f1_macro",
              "w_lr","w_xgb","w_lstm","w_cnn"]].to_string(index=False))
        print("\nPor-ticker mean F1-macro test:")
        piv = df[df["tipo"]=="por_ticker"].pivot_table(
            index="experimento", values="test_f1_macro", aggfunc="mean")
        print(piv.round(4).to_string())


if __name__ == "__main__":
    main()
