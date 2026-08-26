"""Prueba combinada: mejor target (h=5d, q=0.25/0.75) + interactions."""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import sys, functools, warnings
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
from via8_dataset import (_cargar_panel, _construir_target, _preparar, _build_lr,
                           _build_xgb, _metricas_backtest, LR_HP, XGB_HP, TICKERS,
                           OUT, BASELINE, _top_features_lr)
from sklearn.utils.class_weight import compute_class_weight

print("=" * 70)
print("VÍA 8 — PRUEBAS COMBINADAS")
print("Combinaciones de las mejoras encontradas para ver si suman.")
print("=" * 70)

# Configs a probar
combos = [
    ("baseline (h=1d, 30/70, base features)", 1, 0.30, 0.70, "base"),
    ("h=5d, 25/75, base features", 5, 0.25, 0.75, "base"),
    ("h=5d, 30/70, base features", 5, 0.30, 0.70, "base"),
    ("h=1d, 30/70, base + interactions", 1, 0.30, 0.70, "inter"),
    ("h=5d, 25/75, base + interactions", 5, 0.25, 0.75, "inter"),
    ("h=5d, 30/70, base + interactions", 5, 0.30, 0.70, "inter"),
    ("h=5d, 25/75, base + inter + crossasset", 5, 0.25, 0.75, "inter+ca"),
    ("h=10d, 33/67, base + interactions", 10, 0.33, 0.67, "inter"),
]

# Cross-asset feature builder
def add_crossasset(dfs):
    import yfinance as yf
    cache = OUT / "_spy_xlk.parquet"
    if cache.exists():
        spx = pd.read_parquet(cache)
    else:
        spx = yf.download(["SPY", "XLK"], start="2013-01-01", end="2025-12-31",
                          auto_adjust=True, progress=False)["Close"]
        spx.columns = ["SPY", "XLK"]
    r_spy = np.log(spx["SPY"] / spx["SPY"].shift(1))
    r_xlk = np.log(spx["XLK"] / spx["XLK"].shift(1))
    rets = {tk: np.log(dfs[tk]["raw_close"] / dfs[tk]["raw_close"].shift(1)) for tk in TICKERS}
    rank = pd.DataFrame(rets).rank(axis=1, pct=True)
    dfs_new = {}
    for tk, df in dfs.items():
        d = df.copy()
        idx = d.index.intersection(r_spy.index)
        rtk = rets[tk].reindex(idx)
        rs = r_spy.reindex(idx)
        rx = r_xlk.reindex(idx)
        cov = rtk.rolling(20).cov(rs); var = rs.rolling(20).var()
        d["beta_spy_20d"] = (cov / (var + 1e-12)).reindex(d.index)
        d["corr_xlk_20d"] = rtk.rolling(20).corr(rx).reindex(d.index)
        d["rank_ret_7"] = rank[tk].reindex(d.index)
        dfs_new[tk] = d.dropna(subset=["beta_spy_20d", "corr_xlk_20d", "rank_ret_7"])
    return dfs_new

def add_inter(dfs, top):
    pares = [(top[i], top[j]) for i in range(len(top)) for j in range(i+1, len(top))]
    rng = np.random.default_rng(42)
    idxs = rng.choice(len(pares), size=15, replace=False)
    pares_sel = [pares[i] for i in idxs]
    dfs_new = {}
    for tk, df in dfs.items():
        d = df.copy()
        for a, b in pares_sel:
            d[f"{a}_x_{b}"] = df[a] * df[b]
        dfs_new[tk] = d
    return dfs_new

filas = []
for nombre, h, q_lo, q_hi, extra in combos:
    print(f"\n── {nombre} ──")
    # 1) regenerar target
    dfs = {}
    for tk in TICKERS:
        df = _cargar_panel(tk).copy()
        r_fwd, target = _construir_target(df, horizonte=h, q_lo=q_lo, q_hi=q_hi)
        df["r_forward_new"] = r_fwd
        df["target_new"] = target
        dfs[tk] = df

    # 2) top-10 features del baseline (usando el target ORIGINAL para determinar features)
    datos_ref = _preparar({tk: _cargar_panel(tk) for tk in TICKERS},
                          escalador=LR_HP["escalador"])
    top = _top_features_lr(datos_ref, n=10)

    # 3) agregar features extra
    if "inter" in extra:
        dfs = add_inter(dfs, top)
    if "ca" in extra:
        dfs = add_crossasset(dfs)

    datos = _preparar(dfs, escalador=LR_HP["escalador"],
                      usar_target_col="target_new", r_fwd_col="r_forward_new")
    print(f"  n_features={datos['n_features']}")

    # 4) entrenar LR y XGB
    y_class = np.array([0, 1, 2])
    w_cls = compute_class_weight("balanced", classes=y_class, y=datos["y_train"])
    sample_w = np.array([w_cls[c] for c in datos["y_train"]])
    for modelo_nombre, build, sw_ok in [("LR", _build_lr, False), ("XGBoost", _build_xgb, True)]:
        model = build(LR_HP if modelo_nombre == "LR" else XGB_HP)
        if sw_ok:
            model.fit(datos["X_train"], datos["y_train"], sample_weight=sample_w)
        else:
            model.fit(datos["X_train"], datos["y_train"])
        pred = model.predict(datos["X_eval"])
        met = _metricas_backtest(pred, datos["y_eval"],
                                    datos["r_eval"], datos["tk_eval"])
        filas.append({"combo": nombre, "modelo": modelo_nombre, **met})
        print(f"  {modelo_nombre:>8}  F1={met['f1']:.4f} Sharpe={met['sharpe']:+.3f} "
              f"WR={met['win_rate']:.3f} MaxDD={met['max_dd']:.3f}")

df = pd.DataFrame(filas)
df.to_csv(OUT / "combinados.csv", index=False)
print(f"\n✓ Guardado en {OUT}/combinados.csv")
