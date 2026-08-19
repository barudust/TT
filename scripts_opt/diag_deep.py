"""
================================================================================
DIAGNÓSTICO DE LOS MODELOS PROFUNDOS (v4)
================================================================================
Script de evidencia para `RESULTADOS_OPTIMIZADOS/docs/DIAGNOSTICO_MODELOS_PROFUNDOS.md`.
Reproduce las cuatro mediciones en las que se apoya ese documento:

  1. Costo real de UN entrenamiento (s/época, época de early-stop, s totales).
  2. Curvas train/val sin early stopping → ¿sobreajuste u optimización fallida?
  3. Efecto del MinMaxScaler sobre val/test.
  4. F1 de VALIDACIÓN de LR sobre exactamente los mismos datos (referencia).

NO toca el conjunto de test en ningún momento: todas las cifras son de train/val.
Se corre desde la raíz del repo:

    python scripts_opt/diag_deep.py                 # todo
    python scripts_opt/diag_deep.py --solo tiempos  # una sección

Tiempo total ≈ 4 min en una RTX 5060 Ti.
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("PYTHONUNBUFFERED", "1")
import sys
import json
import time
import functools
import warnings
import numpy as np
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass
print = functools.partial(print, flush=True)
warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).parent))

import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import f1_score

import train_all_v4 as v4
from common import CLASES, TICKERS, OUT_DIR
from common_v4 import cargar_global_v4, cargar_dataset_v4

DEVICE = v4.DEVICE
OUT_JSON = OUT_DIR / "docs" / "diag_deep_resultados.json"
LN3 = float(np.log(3))

resultados = {}


# ════════════════════════════════════════════════════════════════════════════
# 1. COSTO REAL DE UN ENTRENAMIENTO
# ════════════════════════════════════════════════════════════════════════════

def evaluar(modelo, X, y, crit, batch=512):
    """Loss y F1-macro de un split completo."""
    modelo.eval()
    loss = 0.0
    n = 0
    preds = []
    with torch.no_grad():
        for i in range(0, len(X), batch):
            xb = torch.from_numpy(X[i:i + batch]).float().to(DEVICE)
            yb = torch.from_numpy(y[i:i + batch]).long().to(DEVICE)
            logits = modelo(xb)
            loss += crit(logits, yb).item() * len(xb)
            n += len(xb)
            preds.append(logits.argmax(1).cpu().numpy())
    return loss / n, f1_score(y, np.concatenate(preds), average="macro", zero_division=0)


def entrenar_instrumentado(modelo, g, lr, epochs, patience, con_early_stop):
    """v4.entrenar_dl + registro por época de tiempo, train_loss/f1 y val_loss/f1."""
    cw_np = compute_class_weight("balanced", classes=np.array(CLASES), y=g["y_tr"])
    cw = torch.tensor(cw_np, dtype=torch.float32, device=DEVICE)
    crit = nn.CrossEntropyLoss(weight=cw)
    loader_tr = v4.make_loader(g["X_tr"], g["y_tr"])
    opt = optim.AdamW(modelo.parameters(), lr=lr, weight_decay=v4.WD)
    sch = optim.lr_scheduler.ReduceLROnPlateau(opt, mode="min", factor=0.5,
                                               patience=8, min_lr=1e-6)
    best = float("inf")
    sin = 0
    hist, t_epocas = [], []

    for ep in range(1, epochs + 1):
        t0 = time.time()
        modelo.train()
        for Xb, yb in loader_tr:
            Xb = Xb.to(DEVICE, non_blocking=True)
            yb = yb.to(DEVICE, non_blocking=True)
            opt.zero_grad()
            loss = crit(modelo(Xb), yb)
            loss.backward()
            nn.utils.clip_grad_norm_(modelo.parameters(), 1.0)
            opt.step()
        l_tr, f1_tr = evaluar(modelo, g["X_tr"], g["y_tr"], crit)
        l_va, f1_va = evaluar(modelo, g["X_va"], g["y_va"], crit)
        sch.step(l_va)
        t_epocas.append(time.time() - t0)
        hist.append(dict(ep=ep, train_loss=round(l_tr, 4), train_f1=round(f1_tr, 4),
                         val_loss=round(l_va, 4), val_f1=round(f1_va, 4)))
        if l_va < best:
            best, sin = l_va, 0
        else:
            sin += 1
        if con_early_stop and sin >= patience:
            break
    return hist, t_epocas


def seccion_tiempos():
    print("\n" + "=" * 78)
    print("  1) COSTO REAL DE UN ENTRENAMIENTO (config exacta de v4, Exp B)")
    print("=" * 78)

    casos = [("LSTM", v4.LSTMBi, 20), ("CNN", v4.CNNPuro, 20),
             ("CNN-LSTM", v4.CNNLSTM, 20), ("LSTM", v4.LSTMBi, 60)]
    datos = {}
    for lb in (20, 60):
        t0 = time.time()
        datos[lb] = v4.prep_seq_global("B", lb)
        print(f"  prep GLOBAL lb={lb}: {time.time()-t0:.1f}s  "
              f"train={datos[lb]['X_tr'].shape} val={datos[lb]['X_va'].shape} "
              f"test={datos[lb]['X_te'].shape}")

    filas = []
    for nombre, clase, lb in casos:
        g = datos[lb]
        torch.manual_seed(42)
        np.random.seed(42)
        m = clase(g["X_tr"].shape[2]).to(DEVICE)
        n_par = sum(p.numel() for p in m.parameters())
        t0 = time.time()
        hist, t_ep = entrenar_instrumentado(m, g, v4.LR_, v4.EPOCHS, v4.PATIENCE, True)
        dur = time.time() - t0
        ep_loss = min(hist, key=lambda h: h["val_loss"])
        ep_f1 = max(hist, key=lambda h: h["val_f1"])
        fila = dict(modelo=nombre, lookback=lb, n_params=n_par,
                    epocas_corridas=len(hist),
                    seg_por_epoca=round(float(np.mean(t_ep)), 3),
                    seg_entrenamiento=round(dur, 1),
                    epoca_elegida_por_val_loss=ep_loss["ep"],
                    val_f1_de_esa_epoca=ep_loss["val_f1"],
                    epoca_de_mejor_val_f1=ep_f1["ep"],
                    val_f1_maximo=ep_f1["val_f1"],
                    delta_por_cambiar_criterio=round(ep_f1["val_f1"] - ep_loss["val_f1"], 4))
        filas.append(fila)
        print(f"  {nombre:9s} lb={lb:2d}  {n_par:>8,} par  "
              f"{fila['seg_por_epoca']:.2f}s/época  para en ep{len(hist)}  "
              f"({fila['seg_entrenamiento']:.0f}s total)  "
              f"| época elegida por val_loss={ep_loss['ep']} (f1={ep_loss['val_f1']:.4f})  "
              f"mejor val_f1={ep_f1['val_f1']:.4f} en ep{ep_f1['ep']}")

    # costo per-ticker
    d = v4.prep_seq_ticker("AAPL", "B", 20)
    torch.manual_seed(42)
    np.random.seed(42)
    m = v4.LSTMBi(d["X_tr"].shape[2]).to(DEVICE)
    t0 = time.time()
    hist, t_ep = entrenar_instrumentado(m, d, v4.LR_, v4.EPOCHS, v4.PATIENCE, True)
    print(f"  LSTM AAPL (per-ticker)  {np.mean(t_ep):.3f}s/época  "
          f"para en ep{len(hist)}  ({time.time()-t0:.1f}s total)")
    filas.append(dict(modelo="LSTM-per-ticker-AAPL", lookback=20,
                      seg_por_epoca=round(float(np.mean(t_ep)), 3),
                      seg_entrenamiento=round(time.time() - t0, 1),
                      epocas_corridas=len(hist)))
    resultados["1_tiempos"] = filas


# ════════════════════════════════════════════════════════════════════════════
# 2. ¿SOBREAJUSTE U OPTIMIZACIÓN FALLIDA?
# ════════════════════════════════════════════════════════════════════════════

CONFIGS_DIAG = [
    dict(nombre="A_v4_default",   lr=1e-3, hidden=128, layers=2, dropout=0.3),
    dict(nombre="B_lr3e-4",       lr=3e-4, hidden=128, layers=2, dropout=0.3),
    dict(nombre="C_lr1e-4",       lr=1e-4, hidden=128, layers=2, dropout=0.3),
    dict(nombre="D_small_lr3e-4", lr=3e-4, hidden=32,  layers=1, dropout=0.3),
    dict(nombre="E_tiny_lr1e-3",  lr=1e-3, hidden=16,  layers=1, dropout=0.1),
]


def seccion_curvas(epochs=40):
    print("\n" + "=" * 78)
    print(f"  2) CURVAS train/val SIN early stopping ({epochs} épocas, LSTM, Exp B GLOBAL)")
    print(f"     Referencia: ln(3) = {LN3:.4f} = pérdida de un modelo que predice al azar")
    print("=" * 78)

    g = v4.prep_seq_global("B", 20)
    filas = []
    for cfg in CONFIGS_DIAG:
        torch.manual_seed(42)
        np.random.seed(42)
        m = v4.LSTMBi(g["X_tr"].shape[2], hidden=cfg["hidden"],
                      layers=cfg["layers"], dropout=cfg["dropout"]).to(DEVICE)
        hist, _ = entrenar_instrumentado(m, g, cfg["lr"], epochs, 10**9, False)
        mejor = max(hist, key=lambda h: h["val_f1"])
        min_val_loss = min(h["val_loss"] for h in hist)
        print(f"\n  --- {cfg['nombre']}  ({sum(p.numel() for p in m.parameters()):,} params) ---")
        print("   ep | train_loss train_f1 |  val_loss  val_f1")
        for h in hist:
            if h["ep"] <= 3 or h["ep"] % 10 == 0:
                print(f"   {h['ep']:2d} |    {h['train_loss']:.4f}   {h['train_f1']:.4f} |   "
                      f"{h['val_loss']:.4f}  {h['val_f1']:.4f}")
        print(f"   -> mejor val_f1={mejor['val_f1']:.4f} (ep{mejor['ep']})   "
              f"min val_loss={min_val_loss:.4f}   "
              f"{'NUNCA baja de ln(3)' if min_val_loss >= LN3 else 'baja de ln(3)'}")
        filas.append(dict(cfg=cfg, mejor_val_f1=mejor["val_f1"], epoca=mejor["ep"],
                          min_val_loss=round(min_val_loss, 4),
                          train_loss_final=hist[-1]["train_loss"],
                          train_f1_final=hist[-1]["train_f1"],
                          hist=hist))
    resultados["2_curvas"] = filas


# ════════════════════════════════════════════════════════════════════════════
# 3. EFECTO DEL ESCALADOR
# ════════════════════════════════════════════════════════════════════════════

def seccion_escalador():
    print("\n" + "=" * 78)
    print("  3) ¿EL MinMaxScaler APLASTA LAS FEATURES? (Exp B, escalado por ticker)")
    print("=" * 78)

    g = cargar_global_v4("B")
    feat = g["feat_cols"]
    Xtr_l, Xva_l, Xte_l = [], [], []
    for tk in TICKERS:
        d = cargar_dataset_v4(tk, "B")
        s = MinMaxScaler().fit(d["X_tr"])
        Xtr_l.append(s.transform(d["X_tr"]))
        Xva_l.append(s.transform(d["X_va"]))
        Xte_l.append(s.transform(d["X_te"]))
    Xtr, Xva, Xte = np.vstack(Xtr_l), np.vstack(Xva_l), np.vstack(Xte_l)

    std_tr = Xtr.std(axis=0)
    peores = np.argsort(std_tr)[:8]
    r = dict(
        std_mediana=round(float(np.median(std_tr)), 4),
        std_min=round(float(std_tr.min()), 5),
        std_max=round(float(std_tr.max()), 4),
        n_features_casi_constantes=int((std_tr < 0.05).sum()),
        n_features=len(feat),
        pct_val_fuera_de_rango=round(float(((Xva < 0) | (Xva > 1)).mean() * 100), 2),
        pct_test_fuera_de_rango=round(float(((Xte < 0) | (Xte > 1)).mean() * 100), 2),
        test_min=round(float(Xte.min()), 2), test_max=round(float(Xte.max()), 2),
        mas_aplastadas=[(feat[i], round(float(std_tr[i]), 4)) for i in peores],
    )
    print(f"  std por feature tras MinMax (train): mediana={r['std_mediana']} "
          f"min={r['std_min']} max={r['std_max']}")
    print(f"  features con std<0.05 (casi constantes): "
          f"{r['n_features_casi_constantes']}/{r['n_features']}")
    print(f"  más aplastadas: {r['mas_aplastadas']}")
    print(f"  valores fuera de [0,1] (sin clip): val={r['pct_val_fuera_de_rango']}%  "
          f"test={r['pct_test_fuera_de_rango']}%  (test va de {r['test_min']} a {r['test_max']})")

    z = StandardScaler().fit(g["X_tr"]).transform(g["X_te"])
    r["standard_test_min"] = round(float(z.min()), 1)
    r["standard_test_max"] = round(float(z.max()), 1)
    r["standard_pct_abs_z_mayor_5"] = round(float((np.abs(z) > 5).mean() * 100), 2)
    print(f"  comparación StandardScaler: test va de {r['standard_test_min']} a "
          f"{r['standard_test_max']}  (|z|>5 en {r['standard_pct_abs_z_mayor_5']}% de los valores)")
    resultados["3_escalador"] = r


# ════════════════════════════════════════════════════════════════════════════
# 4. REFERENCIA: LR SOBRE LOS MISMOS DATOS
# ════════════════════════════════════════════════════════════════════════════

def seccion_lr():
    print("\n" + "=" * 78)
    print("  4) LR elasticnet — F1 de TRAIN y VALIDACIÓN, Exp B GLOBAL")
    print("=" * 78)
    g = cargar_global_v4("B")
    sc = StandardScaler().fit(g["X_tr"])
    Xtr, Xva = sc.transform(g["X_tr"]), sc.transform(g["X_va"])
    filas = []
    for C in [0.01, 0.1, 1.0]:
        m = LogisticRegression(penalty="elasticnet", solver="saga", l1_ratio=0.5, C=C,
                               max_iter=2000, class_weight="balanced", random_state=42,
                               n_jobs=-1, tol=1e-3).fit(Xtr, g["y_tr"])
        f1_tr = f1_score(g["y_tr"], m.predict(Xtr), average="macro", zero_division=0)
        f1_va = f1_score(g["y_va"], m.predict(Xva), average="macro", zero_division=0)
        print(f"  C={C:<5}  train_f1={f1_tr:.4f}   val_f1={f1_va:.4f}")
        filas.append(dict(C=C, train_f1=round(f1_tr, 4), val_f1=round(f1_va, 4)))
    resultados["4_lr_referencia"] = filas


# ════════════════════════════════════════════════════════════════════════════

SECCIONES = {"tiempos": seccion_tiempos, "curvas": seccion_curvas,
             "escalador": seccion_escalador, "lr": seccion_lr}

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--solo", nargs="+", default=None, choices=list(SECCIONES))
    args = p.parse_args()

    print(f"Dispositivo: {DEVICE}")
    t0 = time.time()
    for nombre in (args.solo or list(SECCIONES)):
        SECCIONES[nombre]()

    # Fusionar con lo que ya hubiera: correr con --solo no debe borrar el resto.
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    previo = {}
    if OUT_JSON.exists():
        try:
            with open(OUT_JSON, encoding="utf-8") as f:
                previo = json.load(f)
        except Exception:
            pass
    previo.update(resultados)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(previo, f, indent=2, default=str)
    print(f"\n{'='*78}\n  Tiempo total: {(time.time()-t0)/60:.1f} min")
    print(f"  Resultados crudos → {OUT_JSON}\n{'='*78}")
