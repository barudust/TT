"""
CNN puro con features FILTRADAS (Spearman del script 02).
Para comparar contra CNN puro con todas las 61 features.
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("PYTHONUNBUFFERED", "1")
import sys, time, warnings, functools
import numpy as np
import pandas as pd
from pathlib import Path

try: sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except: pass
print = functools.partial(print, flush=True)
warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).parent))
from common import (TICKERS, EXPERIMENTOS, CLASES,
                    metricas_full, metricas_global_por_ticker,
                    guardar_json, imprimir_metricas, OUT_DIR)
from opt_cnn_puro import CNNPuro, preparar_ticker, preparar_global, entrenar, make_loader, predecir_logits

import torch
import torch.nn.functional as F
from sklearn.utils.class_weight import compute_class_weight

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

OUT = OUT_DIR / "modelos_optimizados" / "cnn_puro_filtradas"
OUT.mkdir(parents=True, exist_ok=True)
RESULTS_CSV = OUT / "resultados_cnn_puro_filtradas.csv"

LOOKBACKS = [20, 60]
SEEDS = [42, 1, 7]


def cargar_feats_filtradas(exp_id):
    """Features Spearman-filtradas del script 02 (para LSTM/CNN-LSTM/CNN)."""
    df = pd.read_csv(f"tesis_ml_stocks/Validacion_{exp_id}/consolidado/features_recomendadas.csv")
    return df["LSTM"].dropna().tolist()  # mismas que CNN_LSTM


def correr(exp_id, lookback):
    feats = cargar_feats_filtradas(exp_id)
    print(f"\n{'═'*70}\n  CNN PURO FILTRADAS  |  Exp {exp_id}  |  lb={lookback}  |  feats={len(feats)}\n{'═'*70}")
    out_dir = OUT / f"lookback_{lookback}" / f"experimento_{exp_id}"
    out_dir.mkdir(parents=True, exist_ok=True)
    resultados = []

    print("\n  ── POR TICKER ──")
    for ticker in TICKERS:
        d = preparar_ticker(ticker, exp_id, lookback, feat_cols=feats)
        if len(d["X_tr"]) < 100:
            continue
        cw_np = compute_class_weight("balanced", classes=np.array(CLASES), y=d["y_tr"])
        cw = torch.tensor(cw_np, dtype=torch.float32, device=DEVICE)
        loader_tr = make_loader(d["X_tr"], d["y_tr"])
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
        met_val  = metricas_full(d["y_va"], probs_va.argmax(axis=1), split_name="val")
        met_test = metricas_full(d["y_te"], probs_te.argmax(axis=1), r_forward=d["r_fwd_test"], split_name="test")
        imprimir_metricas(f"  {ticker} test", met_test)

        f = {"config_id": "CNN-puro-filt", "modelo": "CNN", "tipo": "por_ticker",
             "ticker": ticker, "experimento": exp_id, "lookback": lookback,
             "n_features": input_size, "n_seeds": len(SEEDS),
             "test_f1_macro": met_test["f1_macro"],
             "test_f1_buy":   met_test["f1_buy"],
             "test_f1_hold":  met_test["f1_hold"],
             "test_f1_sell":  met_test["f1_sell"]}
        for k in ["cumul_return_test","return_vs_bh_test","sharpe_test",
                  "max_drawdown_test","win_rate_test","profit_factor_test"]:
            f[k] = met_test.get(k)
        resultados.append(f)

    # GLOBAL
    print("\n  ── GLOBAL ──")
    g = preparar_global(exp_id, lookback, feat_cols=feats)
    cw_np = compute_class_weight("balanced", classes=np.array(CLASES), y=g["y_tr"])
    cw = torch.tensor(cw_np, dtype=torch.float32, device=DEVICE)
    loader_tr = make_loader(g["X_tr"], g["y_tr"])
    loader_va = make_loader(g["X_va"], g["y_va"], shuffle=False)
    input_size = g["X_tr"].shape[2]
    logits_va_l, logits_te_l = [], []
    for s in SEEDS:
        torch.manual_seed(s); np.random.seed(s)
        m = CNNPuro(input_size=input_size).to(DEVICE)
        m = entrenar(m, loader_tr, loader_va, cw)
        logits_va_l.append(predecir_logits(m, g["X_va"]))
        logits_te_l.append(predecir_logits(m, g["X_te"]))
    probs_va = np.mean([F.softmax(torch.tensor(l), dim=1).numpy() for l in logits_va_l], axis=0)
    probs_te = np.mean([F.softmax(torch.tensor(l), dim=1).numpy() for l in logits_te_l], axis=0)
    met_test = metricas_full(g["y_te"], probs_te.argmax(axis=1), r_forward=g["r_fwd_test"], split_name="test")
    imprimir_metricas("  GLOBAL test", met_test)

    f = {"config_id": "CNN-puro-filt", "modelo": "CNN", "tipo": "global",
         "ticker": "GLOBAL", "experimento": exp_id, "lookback": lookback,
         "n_features": input_size, "n_seeds": len(SEEDS),
         "test_f1_macro": met_test["f1_macro"],
         "test_f1_buy":   met_test["f1_buy"],
         "test_f1_hold":  met_test["f1_hold"],
         "test_f1_sell":  met_test["f1_sell"]}
    for k in ["cumul_return_test","return_vs_bh_test","sharpe_test",
              "max_drawdown_test","win_rate_test","profit_factor_test"]:
        f[k] = met_test.get(k)
    resultados.append(f)
    return resultados


def main():
    todos = []
    for lb in LOOKBACKS:
        for exp_id in EXPERIMENTOS:
            res = correr(exp_id, lb)
            todos.extend(res)
            pd.DataFrame(todos).to_csv(RESULTS_CSV, index=False)


if __name__ == "__main__":
    main()
