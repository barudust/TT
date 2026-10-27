"""
================================================================================
COMMON V5 — núcleo del pipeline corregido
================================================================================
Reemplaza el camino de entrenamiento de `train_all_v4.py` arreglando lo que el
diagnóstico encontró (ver ../RESULTADOS_OPTIMIZADOS/docs/DIAGNOSTICO_MODELOS_PROFUNDOS.md):

  1. Registra SIEMPRE métricas de validación, no solo de test.
  2. Criterio de selección de época configurable (val_loss / val_f1 / val_f1_ma3),
     con early stopping sobre ESE criterio.
  3. Ventanas opcionalmente alineadas: todos los modelos se evalúan sobre las
     mismas fechas (sin perder las primeras `lookback` filas de cada split).
  4. Reentrenamiento opcional con train+val (paridad con LR/XGBoost).
  5. Listo para Optuna: `trial.report()` + `should_prune()`.

PROTOCOLO ANIDADO (la parte importante)
---------------------------------------
Para no elegir hiperparámetros mirando el mismo año con el que se eligió la época
(y mucho menos mirando test), cada experimento tiene dos modos:

  modo="dev"    train=2018-2022  val=2023 (elige época)  eval=2024 (elige config)
  modo="final"  train=2018-2023  val=2024 (elige época)  eval=2025 (TEST, una vez)

Toda la búsqueda (ablaciones, Optuna) ocurre en `dev`. `final` solo se corre con
la configuración ya congelada. Así el año 2025 se toca una sola vez por config.
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("PYTHONUNBUFFERED", "1")
import sys
import json
import time
import random
import functools
import warnings
from dataclasses import dataclass, field, asdict, replace
from pathlib import Path

import numpy as np
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass
print = functools.partial(print, flush=True)
warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).parent))

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import f1_score

from common import (TICKERS, CLASES, EXCLUIR_COLS, OUT_DIR,
                    metricas_full, metricas_global_por_ticker, cargar_raw,
                    get_feature_cols)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

OUT_V5 = OUT_DIR / "v5"
OUT_V5.mkdir(parents=True, exist_ok=True)
REGISTRO = OUT_V5 / "registro_runs.csv"


# ════════════════════════════════════════════════════════════════════════════
# SPLITS
# ════════════════════════════════════════════════════════════════════════════

# `final` es idéntico a SPLITS_V4 (lo que produjo los números del paper).
# `dev` desplaza todo un año hacia atrás para poder elegir configuración sin
# tocar 2025 ni reutilizar el año con el que se eligió la época.
SPLITS_V5 = {
    "A": {
        "dev":   {"train": ("2014-01-01", "2022-12-31"),
                  "val":   ("2023-01-01", "2023-12-31"),
                  "eval":  ("2024-01-01", "2024-12-31")},
        "final": {"train": ("2014-01-01", "2023-12-31"),
                  "val":   ("2024-01-01", "2024-12-31"),
                  "eval":  ("2025-01-01", "2025-12-31")},
    },
    "B": {
        "dev":   {"train": ("2018-01-01", "2022-12-31"),
                  "val":   ("2023-01-01", "2023-12-31"),
                  "eval":  ("2024-01-01", "2024-12-31")},
        "final": {"train": ("2018-01-01", "2023-12-31"),
                  "val":   ("2024-01-01", "2024-12-31"),
                  "eval":  ("2025-01-01", "2025-12-31")},
    },
    "C": {
        "dev":   {"train": ("2020-01-01", "2022-12-31"),
                  "val":   ("2023-01-01", "2023-12-31"),
                  "eval":  ("2024-01-01", "2024-12-31")},
        "final": {"train": ("2020-01-01", "2023-12-31"),
                  "val":   ("2024-01-01", "2024-12-31"),
                  "eval":  ("2025-01-01", "2025-12-31")},
    },
}

EXPERIMENTOS = {"A": "10 anios train", "B": "6 anios train (REC)", "C": "4 anios train"}

# ── Walk-forward: ventana de entrenamiento FIJA de 5 años que rueda año a año ──
# Aísla el efecto del año de test (la ventana no cambia de tamaño), que es
# justo lo que los tres experimentos A/B/C no pueden separar porque comparten
# test = 2025. Solo tiene modo "final": cada pliegue se evalúa una vez.
WF_ANIOS = [2020, 2021, 2022, 2023, 2024, 2025]
for _t in WF_ANIOS:
    SPLITS_V5[f"WF{_t}"] = {
        "final": {"train": (f"{_t-6}-01-01", f"{_t-2}-12-31"),
                  "val":   (f"{_t-1}-01-01", f"{_t-1}-12-31"),
                  "eval":  (f"{_t}-01-01", f"{_t}-12-31")},
    }
    SPLITS_V5[f"WF{_t}"]["dev"] = SPLITS_V5[f"WF{_t}"]["final"]


# ════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ════════════════════════════════════════════════════════════════════════════

@dataclass
class Cfg:
    # ── datos ──
    lookback: int = 20
    escalador: str = "minmax"          # minmax | standard | robust
    clip: float = 0.0                  # 0 = sin recorte; >0 recorta a ±clip tras escalar
    alineado: bool = False             # False = como v4 (pierde lookback filas por split)

    # ── arquitectura ──
    arch: str = "lstm"                 # lstm | cnn | cnn_lstm
    hidden: int = 128
    layers: int = 2
    dropout: float = 0.3
    bidir: bool = True
    pooling: str = "last"              # last | meanmax | attn
    filtros: tuple = (64, 128, 192)    # CNN / CNN-LSTM
    kernel: int = 3
    dilatacion: int = 1
    batchnorm: bool = True
    fc_dim: int = 128
    pool_cnn: str = "gap_gmp"          # gap_gmp | gap | flatten

    # ── entrenamiento ──
    epochs: int = 80
    patience: int = 15
    batch: int = 128
    lr: float = 1e-3
    weight_decay: float = 1e-4
    class_weight: str = "balanced"     # balanced | none | sqrt
    scheduler: str = "plateau"         # plateau | cosine | none
    grad_clip: float = 1.0
    criterio: str = "val_loss"         # val_loss | val_f1 | val_f1_ma3
    loss: str = "ce"                   # ce | focal
    label_smooth: float = 0.0
    focal_gamma: float = 2.0
    refit_trainval: bool = False

    def id_corto(self) -> str:
        return (f"{self.arch}_lb{self.lookback}_h{self.hidden}_l{self.layers}"
                f"_{self.criterio}{'_ali' if self.alineado else ''}"
                f"{'_refit' if self.refit_trainval else ''}")


# configuración que replica exactamente train_all_v4.py
CFG_V4 = dict(
    lstm=Cfg(arch="lstm", hidden=128, layers=2, dropout=0.3, bidir=True, pooling="last"),
    cnn=Cfg(arch="cnn", filtros=(64, 128, 192), kernel=3, dropout=0.3, fc_dim=128),
    # ojo: el CNN-LSTM de v4 es UNIdireccional (v4.CNNLSTM no pasa bidirectional)
    cnn_lstm=Cfg(arch="cnn_lstm", filtros=(64, 128), hidden=128, layers=2,
                 dropout=0.3, bidir=False),
)

SEEDS_DEFAULT = (42, 1, 7)
SEEDS_5 = (42, 1, 7, 2024, 100)


# ════════════════════════════════════════════════════════════════════════════
# DATOS
# ════════════════════════════════════════════════════════════════════════════

# Qué conjunto de features usar. "v1" = las 61 del paper; "v5" = esas 61 más 32
# columnas de contexto de mercado construidas por build_dataset_v5.py (solo Yahoo).
# Se elige con la variable de entorno TT_DATASET para no duplicar código.
DATASET = os.environ.get("TT_DATASET", "v1")
RAW_DIR_V5 = Path("tesis_ml_stocks/01_raw_datasets_v5")


@functools.lru_cache(maxsize=64)
def _panel(ticker: str) -> pd.DataFrame:
    """Parquet del ticker, ya recortado a features + target + r_forward."""
    if DATASET == "v5":
        df = pd.read_parquet(RAW_DIR_V5 / f"{ticker}_raw.parquet")
    else:
        df = cargar_raw(ticker)
    feat = get_feature_cols(df)
    return df[feat + ["target", "r_forward"]].dropna()


def _hacer_escalador(nombre: str):
    return {"minmax": MinMaxScaler, "standard": StandardScaler,
            "robust": RobustScaler}[nombre]()


def _ventanas(Z, y, fechas, lookback):
    """Ventanas deslizantes sobre una serie continua. Etiqueta = fila i, ventana = [i-lb, i)."""
    n = len(Z)
    if n <= lookback:
        return (np.empty((0, lookback, Z.shape[1]), np.float32),
                np.empty(0, np.int64), fechas[:0])
    idx = np.arange(lookback, n)
    X = np.stack([Z[i - lookback:i] for i in idx]).astype(np.float32)
    return X, y[idx].astype(np.int64), fechas[idx]


def preparar_ticker(ticker: str, exp: str, modo: str, cfg: Cfg) -> dict:
    """
    Devuelve secuencias de train/val/eval para un ticker.

    cfg.alineado=False → como v4: las ventanas se construyen DENTRO de cada split,
                         perdiendo las primeras `lookback` filas de val y eval.
    cfg.alineado=True  → ventanas sobre la serie continua, asignadas al split por
                         la fecha de la ETIQUETA. No hay leakage: el escalador se
                         ajusta solo con train y la ventana solo mira hacia atrás.
    """
    df = _panel(ticker)
    feat = [c for c in df.columns if c not in ("target", "r_forward")]
    rangos = SPLITS_V5[exp][modo]

    def mascara(r):
        return (df.index >= r[0]) & (df.index <= r[1])

    m_tr = mascara(rangos["train"])
    sc = _hacer_escalador(cfg.escalador)
    sc.fit(df.loc[m_tr, feat].values)

    def escalar(A):
        Z = sc.transform(A)
        if cfg.clip and cfg.clip > 0:
            Z = np.clip(Z, -cfg.clip, cfg.clip) if cfg.escalador != "minmax" \
                else np.clip(Z, -cfg.clip, 1 + cfg.clip)
        return Z

    salida = {}
    if cfg.alineado:
        Z = escalar(df[feat].values)
        y = df["target"].values
        r = df["r_forward"].values
        X_all, y_all, f_all = _ventanas(Z, y, df.index, cfg.lookback)
        r_all = r[cfg.lookback:]
        for nombre in ("train", "val", "eval"):
            rg = rangos[nombre]
            m = (f_all >= pd.Timestamp(rg[0])) & (f_all <= pd.Timestamp(rg[1]))
            salida[nombre] = (X_all[m], y_all[m], r_all[m], f_all[m])
    else:
        for nombre in ("train", "val", "eval"):
            sub = df[mascara(rangos[nombre])]
            Z = escalar(sub[feat].values)
            X, y, f = _ventanas(Z, sub["target"].values, sub.index, cfg.lookback)
            r = sub["r_forward"].values[cfg.lookback:]
            salida[nombre] = (X, y, r, f)

    salida["feat_cols"] = feat
    return salida


def preparar(exp: str, modo: str, cfg: Cfg, tipo: str = "global",
             ticker: str = None) -> dict:
    """tipo='global' concatena los 7 tickers; tipo='por_ticker' usa uno solo."""
    tks = TICKERS if tipo == "global" else [ticker]
    acum = {n: {"X": [], "y": [], "r": [], "f": [], "tk": []} for n in ("train", "val", "eval")}
    feat = None
    for tk in tks:
        d = preparar_ticker(tk, exp, modo, cfg)
        feat = d["feat_cols"]
        for n in ("train", "val", "eval"):
            X, y, r, f = d[n]
            acum[n]["X"].append(X); acum[n]["y"].append(y)
            acum[n]["r"].append(r); acum[n]["f"].append(f)
            acum[n]["tk"].append(np.full(len(y), tk))

    out = {"feat_cols": feat, "n_features": len(feat)}
    for n in ("train", "val", "eval"):
        out[f"X_{n}"] = np.vstack(acum[n]["X"]).astype(np.float32)
        out[f"y_{n}"] = np.concatenate(acum[n]["y"])
        out[f"r_{n}"] = np.concatenate(acum[n]["r"])
        out[f"tk_{n}"] = np.concatenate(acum[n]["tk"])
        out[f"f_{n}"] = np.concatenate(acum[n]["f"])
    return out


def preparar_tabular(exp: str, modo: str, tipo: str = "global", ticker: str = None,
                     escalador: str = "standard") -> dict:
    """
    Versión sin ventanas, para LR y XGBoost. Usa exactamente los mismos splits y
    las mismas fechas que `preparar(..., alineado=True, lookback=0)`, de modo que
    los cinco modelos se evalúan sobre las MISMAS filas (regla R4).
    El escalador se ajusta por ticker solo con train, igual que en el camino profundo.
    """
    tks = TICKERS if tipo == "global" else [ticker]
    rangos = SPLITS_V5[exp][modo]
    acum = {n: {"X": [], "y": [], "r": [], "f": [], "tk": []} for n in ("train", "val", "eval")}
    feat = None
    for tk in tks:
        df = _panel(tk)
        feat = [c for c in df.columns if c not in ("target", "r_forward")]
        m_tr = (df.index >= rangos["train"][0]) & (df.index <= rangos["train"][1])
        sc = _hacer_escalador(escalador)
        sc.fit(df.loc[m_tr, feat].values)
        for n in ("train", "val", "eval"):
            r = rangos[n]
            sub = df[(df.index >= r[0]) & (df.index <= r[1])]
            acum[n]["X"].append(sc.transform(sub[feat].values))
            acum[n]["y"].append(sub["target"].values.astype(int))
            acum[n]["r"].append(sub["r_forward"].values)
            acum[n]["f"].append(sub.index.values)
            acum[n]["tk"].append(np.full(len(sub), tk))

    out = {"feat_cols": feat, "n_features": len(feat)}
    for n in ("train", "val", "eval"):
        out[f"X_{n}"] = np.vstack(acum[n]["X"])
        out[f"y_{n}"] = np.concatenate(acum[n]["y"])
        out[f"r_{n}"] = np.concatenate(acum[n]["r"])
        out[f"tk_{n}"] = np.concatenate(acum[n]["tk"])
        out[f"f_{n}"] = np.concatenate(acum[n]["f"])
    return out


# ════════════════════════════════════════════════════════════════════════════
# MODELOS
# ════════════════════════════════════════════════════════════════════════════

class Atencion(nn.Module):
    def __init__(self, h):
        super().__init__()
        self.attn = nn.Linear(h, 1)

    def forward(self, x):
        w = F.softmax(self.attn(x), dim=1)
        return (x * w).sum(dim=1)


def _pool_secuencia(out, pooling, capa_attn=None):
    if pooling == "last":
        return out[:, -1, :]
    if pooling == "meanmax":
        return torch.cat([out.mean(dim=1), out.max(dim=1).values], dim=1)
    return capa_attn(out)


class LSTMNet(nn.Module):
    """Con pooling='last', bidir=True, hidden=128, layers=2 es idéntica a v4.LSTMBi."""

    def __init__(self, input_size, cfg: Cfg):
        super().__init__()
        self.cfg = cfg
        self.lstm = nn.LSTM(input_size, cfg.hidden, cfg.layers, batch_first=True,
                            dropout=cfg.dropout if cfg.layers > 1 else 0.0,
                            bidirectional=cfg.bidir)
        out = cfg.hidden * (2 if cfg.bidir else 1)
        self.attn = Atencion(out) if cfg.pooling == "attn" else None
        dim = out * (2 if cfg.pooling == "meanmax" else 1)
        self.norm = nn.LayerNorm(dim)
        self.drop = nn.Dropout(cfg.dropout)
        self.fc = nn.Linear(dim, 3)

    def forward(self, x):
        out, _ = self.lstm(x)
        p = _pool_secuencia(out, self.cfg.pooling, self.attn)
        return self.fc(self.drop(self.norm(p)))


class CNNNet(nn.Module):
    """Con filtros=(64,128,192), kernel=3, pool='gap_gmp' es idéntica a v4.CNNPuro."""

    def __init__(self, input_size, cfg: Cfg):
        super().__init__()
        self.cfg = cfg
        capas = []
        c_in = input_size
        pad = cfg.dilatacion * (cfg.kernel - 1) // 2
        for f in cfg.filtros:
            capas.append(nn.Conv1d(c_in, f, cfg.kernel, padding=pad,
                                   dilation=cfg.dilatacion))
            if cfg.batchnorm:
                capas.append(nn.BatchNorm1d(f))
            capas += [nn.ReLU(), nn.Dropout(cfg.dropout)]
            c_in = f
        self.cnn = nn.Sequential(*capas)
        self.gap = nn.AdaptiveAvgPool1d(1)
        self.gmp = nn.AdaptiveMaxPool1d(1)
        if cfg.pool_cnn == "gap_gmp":
            dim = cfg.filtros[-1] * 2
        elif cfg.pool_cnn == "gap":
            dim = cfg.filtros[-1]
        else:
            dim = cfg.filtros[-1] * cfg.lookback
        self.fc = nn.Sequential(nn.Linear(dim, cfg.fc_dim), nn.ReLU(),
                                nn.Dropout(cfg.dropout), nn.Linear(cfg.fc_dim, 3))

    def forward(self, x):
        x = self.cnn(x.transpose(1, 2))
        if self.cfg.pool_cnn == "gap_gmp":
            z = torch.cat([self.gap(x).squeeze(-1), self.gmp(x).squeeze(-1)], dim=1)
        elif self.cfg.pool_cnn == "gap":
            z = self.gap(x).squeeze(-1)
        else:
            z = x.flatten(1)
        return self.fc(z)


class CNNLSTMNet(nn.Module):
    """Con filtros=(64,128), hidden=128, layers=2 es idéntica a v4.CNNLSTM."""

    def __init__(self, input_size, cfg: Cfg):
        super().__init__()
        self.cfg = cfg
        capas = []
        c_in = input_size
        pad = cfg.dilatacion * (cfg.kernel - 1) // 2
        for f in cfg.filtros:
            capas.append(nn.Conv1d(c_in, f, cfg.kernel, padding=pad,
                                   dilation=cfg.dilatacion))
            if cfg.batchnorm:
                capas.append(nn.BatchNorm1d(f))
            capas += [nn.ReLU(), nn.Dropout(cfg.dropout)]
            c_in = f
        self.cnn = nn.Sequential(*capas)
        self.lstm = nn.LSTM(cfg.filtros[-1], cfg.hidden, cfg.layers, batch_first=True,
                            dropout=cfg.dropout if cfg.layers > 1 else 0.0,
                            bidirectional=cfg.bidir)
        out = cfg.hidden * (2 if cfg.bidir else 1)
        self.attn = Atencion(out) if cfg.pooling == "attn" else None
        dim = out * (2 if cfg.pooling == "meanmax" else 1)
        self.norm = nn.LayerNorm(dim)
        self.drop = nn.Dropout(cfg.dropout)
        self.fc = nn.Linear(dim, 3)

    def forward(self, x):
        x = self.cnn(x.transpose(1, 2)).transpose(1, 2)
        out, _ = self.lstm(x)
        p = _pool_secuencia(out, self.cfg.pooling, self.attn)
        return self.fc(self.drop(self.norm(p)))


def crear_modelo(cfg: Cfg, input_size: int) -> nn.Module:
    clase = {"lstm": LSTMNet, "cnn": CNNNet, "cnn_lstm": CNNLSTMNet}[cfg.arch]
    return clase(input_size, cfg).to(DEVICE)


class FocalLoss(nn.Module):
    def __init__(self, gamma=2.0, weight=None):
        super().__init__()
        self.gamma = gamma
        self.weight = weight

    def forward(self, logits, target):
        ce = F.cross_entropy(logits, target, weight=self.weight, reduction="none")
        return (((1 - torch.exp(-ce)) ** self.gamma) * ce).mean()


# ════════════════════════════════════════════════════════════════════════════
# ENTRENAMIENTO
# ════════════════════════════════════════════════════════════════════════════

def fijar_semilla(s: int):
    random.seed(s)
    np.random.seed(s)
    torch.manual_seed(s)
    torch.cuda.manual_seed_all(s)


def pesos_clase(y, modo):
    if modo == "none":
        return None
    w = compute_class_weight("balanced", classes=np.array(CLASES), y=y)
    if modo == "sqrt":
        w = np.sqrt(w)
        w = w / w.mean()
    return torch.tensor(w, dtype=torch.float32, device=DEVICE)


def hacer_loader(X, y, batch, shuffle):
    return DataLoader(TensorDataset(torch.from_numpy(X).float(),
                                    torch.from_numpy(y).long()),
                      batch_size=batch, shuffle=shuffle, pin_memory=True)


def criterio_perdida(cfg, w):
    if cfg.loss == "focal":
        return FocalLoss(gamma=cfg.focal_gamma, weight=w)
    return nn.CrossEntropyLoss(weight=w, label_smoothing=cfg.label_smooth)


@torch.no_grad()
def _evaluar_loader(modelo, loader, y, crit):
    """
    Pérdida y F1 de un split, recorriendo un DataLoader ya construido.

    Dos detalles que parecen cosméticos y NO lo son:
      - la pérdida es el promedio NO ponderado sobre lotes (no sobre muestras),
        exactamente como `train_all_v4.entrenar_dl`;
      - se recorre un DataLoader preconstruido en vez de trocear el array con
        `torch.from_numpy(...).to(cuda)` en cada época.
    Cambiar cualquiera de los dos altera el resultado final: la segunda variante
    mueve el estado del asignador de memoria de CUDA, y eso cambia el orden de
    reducción del backward no determinista de cuDNN en el LSTM. El efecto es
    ruido de coma flotante, pero el entrenamiento lo amplifica hasta ±0.02 de
    F1 en test (ver DIAGNOSTICO_MODELOS_PROFUNDOS.md, H6).
    """
    modelo.eval()
    perdida, n_lotes, preds = 0.0, 0, []
    for Xb, yb in loader:
        Xb = Xb.to(DEVICE)
        yb = yb.to(DEVICE)
        logits = modelo(Xb)
        perdida += crit(logits, yb).item()
        n_lotes += 1
        preds.append(logits.argmax(1).cpu().numpy())
    preds = np.concatenate(preds)
    return perdida / max(n_lotes, 1), f1_score(y, preds, average="macro", zero_division=0)


@torch.no_grad()
def predecir_probs(modelo, loader):
    modelo.eval()
    out = []
    for Xb, _ in loader:
        out.append(F.softmax(modelo(Xb.to(DEVICE)), dim=1).cpu().numpy())
    return np.vstack(out)


def entrenar(modelo, datos, cfg: Cfg, trial=None, epochs=None, con_val=True,
             loader_tr=None, loader_va=None):
    """
    Entrena y devuelve (modelo con el mejor checkpoint cargado, historial, mejor_epoca).
    Si con_val=False entrena `epochs` épocas fijas sin early stopping (para el refit).
    Los loaders se pasan ya construidos para no reconstruirlos por semilla.
    """
    w = pesos_clase(datos["y_train"], cfg.class_weight)
    crit = criterio_perdida(cfg, w)
    loader = loader_tr if loader_tr is not None else \
        hacer_loader(datos["X_train"], datos["y_train"], cfg.batch, True)
    if con_val and loader_va is None:
        loader_va = hacer_loader(datos["X_val"], datos["y_val"], cfg.batch, False)
    opt = optim.AdamW(modelo.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)

    n_ep = epochs or cfg.epochs
    if cfg.scheduler == "plateau":
        sch = optim.lr_scheduler.ReduceLROnPlateau(opt, mode="min", factor=0.5,
                                                   patience=8, min_lr=1e-6)
    elif cfg.scheduler == "cosine":
        sch = optim.lr_scheduler.CosineAnnealingLR(opt, T_max=n_ep, eta_min=1e-6)
    else:
        sch = None

    mejor_valor = -np.inf
    mejor_estado, mejor_epoca, sin_mejora = None, 0, 0
    hist = []

    for ep in range(1, n_ep + 1):
        modelo.train()
        for Xb, yb in loader:
            Xb = Xb.to(DEVICE, non_blocking=True)
            yb = yb.to(DEVICE, non_blocking=True)
            opt.zero_grad()
            perdida = crit(modelo(Xb), yb)
            perdida.backward()
            if cfg.grad_clip and cfg.grad_clip > 0:
                nn.utils.clip_grad_norm_(modelo.parameters(), cfg.grad_clip)
            opt.step()

        if not con_val:
            if sch is not None and cfg.scheduler == "cosine":
                sch.step()
            continue

        l_va, f1_va = _evaluar_loader(modelo, loader_va, datos["y_val"], crit)
        hist.append({"ep": ep, "val_loss": l_va, "val_f1": f1_va})

        if sch is not None:
            sch.step(l_va) if cfg.scheduler == "plateau" else sch.step()

        if cfg.criterio == "val_loss":
            valor = -l_va
        elif cfg.criterio == "val_f1":
            valor = f1_va
        else:  # val_f1_ma3
            ult = [h["val_f1"] for h in hist[-3:]]
            valor = float(np.mean(ult))

        if valor > mejor_valor + 1e-12:
            mejor_valor, mejor_epoca, sin_mejora = valor, ep, 0
            mejor_estado = {k: v.detach().clone() for k, v in modelo.state_dict().items()}
        else:
            sin_mejora += 1

        if trial is not None:
            trial.report(f1_va, ep)
            if trial.should_prune():
                import optuna
                raise optuna.TrialPruned()

        if sin_mejora >= cfg.patience:
            break

    if mejor_estado is not None:
        modelo.load_state_dict(mejor_estado)
    return modelo, hist, mejor_epoca


def construir_loaders(datos, cfg: Cfg) -> dict:
    """Loaders reutilizables para todas las semillas (igual que hace v4)."""
    return {
        "train": hacer_loader(datos["X_train"], datos["y_train"], cfg.batch, True),
        "val": hacer_loader(datos["X_val"], datos["y_val"], cfg.batch, False),
        "eval": hacer_loader(datos["X_eval"], datos["y_eval"], cfg.batch, False),
    }


def entrenar_una_semilla(datos, cfg: Cfg, semilla: int, trial=None, loaders=None):
    """Entrena una semilla completa (con refit opcional) y devuelve probs de val y eval."""
    if loaders is None:
        loaders = construir_loaders(datos, cfg)
    fijar_semilla(semilla)
    modelo = crear_modelo(cfg, datos["n_features"])
    modelo, hist, mejor_ep = entrenar(modelo, datos, cfg, trial=trial,
                                      loader_tr=loaders["train"], loader_va=loaders["val"])

    probs_val = predecir_probs(modelo, loaders["val"])

    if cfg.refit_trainval and mejor_ep > 0:
        datos_full = dict(datos)
        datos_full["X_train"] = np.vstack([datos["X_train"], datos["X_val"]])
        datos_full["y_train"] = np.concatenate([datos["y_train"], datos["y_val"]])
        loader_full = hacer_loader(datos_full["X_train"], datos_full["y_train"],
                                   cfg.batch, True)
        fijar_semilla(semilla)
        modelo = crear_modelo(cfg, datos["n_features"])
        modelo, _, _ = entrenar(modelo, datos_full, cfg, epochs=mejor_ep,
                                con_val=False, loader_tr=loader_full)

    probs_eval = predecir_probs(modelo, loaders["eval"])
    return probs_val, probs_eval, hist, mejor_ep, modelo


def correr(cfg: Cfg, exp: str, modo: str, tipo: str = "global", ticker: str = None,
           semillas=SEEDS_DEFAULT, trial=None, datos=None, devolver_probs=False):
    """
    Entrena `len(semillas)` modelos, ensambla por voto suave y devuelve métricas
    de val y de eval. En modo='dev', eval=2024; en modo='final', eval=2025 (TEST).
    """
    t0 = time.time()
    if datos is None:
        datos = preparar(exp, modo, cfg, tipo, ticker)

    loaders = construir_loaders(datos, cfg)
    probs_val_l, probs_eval_l, epocas, f1s_val, f1s_eval = [], [], [], [], []
    for s in semillas:
        pv, pe, hist, mejor_ep, _ = entrenar_una_semilla(datos, cfg, s, trial=trial,
                                                         loaders=loaders)
        probs_val_l.append(pv)
        probs_eval_l.append(pe)
        epocas.append(mejor_ep)
        f1s_val.append(f1_score(datos["y_val"], pv.argmax(1), average="macro", zero_division=0))
        f1s_eval.append(f1_score(datos["y_eval"], pe.argmax(1), average="macro", zero_division=0))

    probs_val = np.mean(probs_val_l, axis=0)
    probs_eval = np.mean(probs_eval_l, axis=0)
    pred_val = probs_val.argmax(1)
    pred_eval = probs_eval.argmax(1)

    met_val = metricas_full(datos["y_val"], pred_val, split_name="val")
    met_eval = metricas_full(datos["y_eval"], pred_eval,
                             r_forward=datos["r_eval"], split_name="eval")

    res = {
        "cfg": cfg, "exp": exp, "modo": modo, "tipo": tipo,
        "ticker": ticker or "GLOBAL",
        "n_train": len(datos["y_train"]), "n_val": len(datos["y_val"]),
        "n_eval": len(datos["y_eval"]),
        "met_val": met_val, "met_eval": met_eval,
        "val_f1_ens": met_val["f1_macro"], "eval_f1_ens": met_eval["f1_macro"],
        "val_f1_mean": float(np.mean(f1s_val)), "val_f1_std": float(np.std(f1s_val)),
        "eval_f1_mean": float(np.mean(f1s_eval)), "eval_f1_std": float(np.std(f1s_eval)),
        "epocas": epocas, "semillas": list(semillas),
        "segundos": round(time.time() - t0, 1),
    }
    if devolver_probs:
        res["probs_val"] = probs_val
        res["y_val"] = datos["y_val"]
        res["probs_eval"] = probs_eval
        res["y_eval"] = datos["y_eval"]
        res["r_eval"] = datos["r_eval"]
        res["tk_eval"] = datos["tk_eval"]
        res["f_eval"] = datos["f_eval"]
        res["datos"] = datos
    return res


# ════════════════════════════════════════════════════════════════════════════
# BACKTEST CON COSTOS DE TRANSACCIÓN
# ════════════════════════════════════════════════════════════════════════════

def metricas_con_costos(y_pred, r_fwd, tickers, costo_bp: float) -> dict:
    """
    Backtest descontando `costo_bp` puntos base por cada CAMBIO de posición.

    La posición es +1 (BUY), 0 (HOLD) o -1 (SELL); el costo de un día es
    |pos_t - pos_{t-1}| * bp/10000, así que pasar de -1 a +1 paga doble. El
    turnover se calcula POR TICKER (las filas globales vienen concatenadas por
    ticker, no intercaladas por fecha, y restar entre tickers no significaría nada).

    El paper omite costos a propósito (`paper.tex:162`); esto permite reportar
    cuánto aguanta cada estrategia antes de dejar de ser rentable.
    """
    pos = np.where(y_pred == 2, 1.0, np.where(y_pred == 0, -1.0, 0.0))
    r_neto = np.empty_like(pos, dtype=float)
    turnover_total = 0.0
    for tk in np.unique(tickers):
        m = tickers == tk
        p = pos[m]
        cambio = np.abs(np.diff(np.concatenate([[0.0], p])))
        costo = cambio * (costo_bp / 10000.0)
        r_neto[m] = p * np.nan_to_num(r_fwd[m]) - costo
        turnover_total += cambio.sum()

    sharpe = float((np.nanmean(r_neto) / (np.nanstd(r_neto) + 1e-12)) * np.sqrt(252)) \
        if np.nanstd(r_neto) > 1e-8 else 0.0
    return {
        f"sharpe_{int(costo_bp)}bp": round(sharpe, 4),
        f"retorno_{int(costo_bp)}bp": round(float(np.expm1(np.nansum(r_neto))), 4),
        "turnover_medio": round(float(turnover_total / max(len(pos), 1)), 4),
    }


# ════════════════════════════════════════════════════════════════════════════
# REGISTRO
# ════════════════════════════════════════════════════════════════════════════

def registrar(res: dict, via: str, notas: str = "", modelo_nombre: str = None):
    """Escribe una fila en el registro maestro. Nunca sobreescribe: siempre append."""
    cfg = res["cfg"]
    m_val, m_ev = res["met_val"], res["met_eval"]
    es_test = (res["modo"] == "final")
    fila = {
        "fecha_hora": time.strftime("%Y-%m-%d %H:%M:%S"),
        "via": via,
        "dataset": DATASET,
        "modelo": modelo_nombre or (cfg.arch if isinstance(cfg, Cfg) else str(cfg)),
        "exp": res["exp"], "modo": res["modo"], "tipo": res["tipo"],
        "ticker": res["ticker"],
        "lookback": cfg.lookback if isinstance(cfg, Cfg) else None,
        "config_json": json.dumps(asdict(cfg), default=str) if isinstance(cfg, Cfg) else json.dumps(cfg, default=str),
        "semillas": str(res["semillas"]),
        "n_train": res["n_train"], "n_val": res["n_val"], "n_eval": res["n_eval"],
        "val_f1_ens": round(res["val_f1_ens"], 4),
        "val_f1_mean": round(res["val_f1_mean"], 4),
        "val_f1_std": round(res["val_f1_std"], 4),
        "eval_f1_ens": round(res["eval_f1_ens"], 4),
        "eval_f1_mean": round(res["eval_f1_mean"], 4),
        "eval_f1_std": round(res["eval_f1_std"], 4),
        "eval_f1_buy": m_ev["f1_buy"], "eval_f1_hold": m_ev["f1_hold"],
        "eval_f1_sell": m_ev["f1_sell"],
        "eval_sharpe": m_ev.get("sharpe_test"),
        "eval_win_rate": m_ev.get("win_rate_test"),
        "eval_profit_factor": m_ev.get("profit_factor_test"),
        "eval_max_dd": m_ev.get("max_drawdown_test"),
        "eval_signal_buy": m_ev["signal_distribution"]["BUY"]["pct"],
        "eval_signal_hold": m_ev["signal_distribution"]["HOLD"]["pct"],
        "eval_signal_sell": m_ev["signal_distribution"]["SELL"]["pct"],
        "epocas": str(res["epocas"]),
        "segundos": res["segundos"],
        "es_evaluacion_en_test": es_test,
        "notas": notas,
    }
    df = pd.DataFrame([fila])
    if REGISTRO.exists():
        df.to_csv(REGISTRO, mode="a", header=False, index=False)
    else:
        df.to_csv(REGISTRO, index=False)
    return fila


def resumen(res: dict, prefijo: str = ""):
    m = res["met_eval"]
    eco = ""
    if "sharpe_test" in m:
        eco = f"  Sharpe={m['sharpe_test']:+.3f}"
    print(f"  {prefijo:<34} val_f1={res['val_f1_ens']:.4f} "
          f"(sem {res['val_f1_mean']:.4f}±{res['val_f1_std']:.4f})  "
          f"eval_f1={res['eval_f1_ens']:.4f} "
          f"(sem {res['eval_f1_mean']:.4f}±{res['eval_f1_std']:.4f}){eco}  "
          f"[{res['segundos']:.0f}s ep={res['epocas']}]")
