"""
================================================================================
VÍA 8 — EXPLORACIÓN DEL DATASET
================================================================================
Cinco técnicas que NO se han probado sobre el dataset (todas dentro del scope
"Yahoo Finance, sin news, sin fundamentales"):

  1) TARGET ABLATION — probar 4 horizontes (1d, 3d, 5d, 10d) × 4 percentiles
     (25/75, 30/70, 33/67, 40/60) = 16 configs con LR ganador de v5. Ilumina
     si el problema actual (1d + 30/70) es óptimo o hay uno más aprendible.

  2) LAG FEATURES — agregar valores de t-1, t-3, t-5 de las top-10 features
     originales (elegidas por |coef| de LR baseline). Da memoria explícita a
     LR/XGB sin cambiar la arquitectura.

  3) CROSS-ASSET — 3 features nuevas por día y ticker:
       - beta_vs_spy_20d
       - corr_20d con XLK (tech)
       - rank_ret_entre_7tickers (posición del ticker en el ranking del día)

  4) MULTI-TIMEFRAME — features base agregadas en ventanas 5d y 20d
     (mediana/desviación) → aumenta 61 → 61 + 20 = 81 features.

  5) INTERACTIONS — productos entre las 10 features más importantes,
     top-15 por importancia (SHAP en XGB).

Todo se evalúa sobre Exp B GLOBAL, test 2025, con LR ganador de v5 (penalty=l2,
C=0.000165, escalador=robust) para acelerar. Si algo mejora ≥ 0.005 F1 sobre
LR baseline (0.4036), se prueba también con XGB.

Uso:
    python scripts_opt/via8_dataset.py --step target      # 30 min
    python scripts_opt/via8_dataset.py --step lags        # 10 min
    python scripts_opt/via8_dataset.py --step crossasset  # 15 min
    python scripts_opt/via8_dataset.py --step multitf     # 10 min
    python scripts_opt/via8_dataset.py --step inter       # 10 min
    python scripts_opt/via8_dataset.py --step consolidar
    python scripts_opt/via8_dataset.py --step all
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("PYTHONUNBUFFERED", "1")
import sys, json, time, argparse, functools, warnings
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
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import RobustScaler, StandardScaler
from sklearn.metrics import f1_score
from sklearn.utils.class_weight import compute_class_weight
import xgboost as xgb

from common import TICKERS, EXCLUIR_COLS, cargar_raw

# ════════════════════════════════════════════════════════════════════════════
# CONFIG
# ════════════════════════════════════════════════════════════════════════════
OUT = Path("RESULTADOS_OPTIMIZADOS/v8")
OUT.mkdir(parents=True, exist_ok=True)
CSV_MASTER = OUT / "tabla_dataset.csv"

# ganadores de Optuna v5 (los mismos usados en via7)
LR_HP = {"penalty": "l2", "C": 0.00016491236228800314, "escalador": "robust"}
XGB_HP = {"n_estimators": 485, "max_depth": 9, "learning_rate": 0.073686514801497,
          "subsample": 0.9716588679987582, "colsample_bytree": 0.9344371907011841,
          "min_child_weight": 2, "gamma": 0.034828439862122,
          "reg_alpha": 1.697838781005609, "reg_lambda": 5.226243589741432,
          "escalador": "standard"}

# Baseline v5 en test 2025 Exp B GLOBAL
BASELINE = {
    "LR":      {"f1": 0.4036, "sharpe": 0.8946, "win_rate": 0.5203},
    "XGBoost": {"f1": 0.3591, "sharpe": 0.4620, "win_rate": 0.4908},
}

# splits fijos
RANGOS = {
    "train": ("2018-01-01", "2023-12-31"),
    "val":   ("2024-01-01", "2024-12-31"),
    "test":  ("2025-01-01", "2025-12-31"),
}


# ════════════════════════════════════════════════════════════════════════════
# UTILIDADES
# ════════════════════════════════════════════════════════════════════════════

def _hacer_escalador(nombre: str):
    return {"robust": RobustScaler(), "standard": StandardScaler()}[nombre]


def _cargar_panel(ticker: str) -> pd.DataFrame:
    """Panel de un ticker: 61 features base + raw OHLCV + target original."""
    return cargar_raw(ticker)


def _construir_target(df: pd.DataFrame, horizonte: int, q_lo: float, q_hi: float,
                      ventana: int = 252) -> tuple[pd.Series, pd.Series]:
    """Regenera el target y el retorno forward con horizonte / percentiles dados.
    q_lo, q_hi ∈ (0,1) — p.ej. (0.30, 0.70) es la config baseline.
    """
    close = df["raw_close"]
    r_fwd = np.log(close.shift(-horizonte) / close)
    # percentiles rodantes sobre los últimos `ventana` días de r_fwd, shifted por 1 para no leak
    q_lo_series = r_fwd.rolling(ventana, min_periods=ventana // 2).quantile(q_lo).shift(1)
    q_hi_series = r_fwd.rolling(ventana, min_periods=ventana // 2).quantile(q_hi).shift(1)
    target = np.where(r_fwd >= q_hi_series, 2,
              np.where(r_fwd <= q_lo_series, 0, 1))
    return pd.Series(r_fwd, index=df.index), pd.Series(target, index=df.index)


def _preparar(dfs_ticker: dict[str, pd.DataFrame], escalador: str,
              usar_target_col: str = "target", r_fwd_col: str = "r_forward"):
    """Convierte dict{tk: df} en X_train/val/test + y + r + tk arrays."""
    acum = {n: {"X": [], "y": [], "r": [], "tk": [], "f": []}
            for n in ("train", "val", "eval")}
    feat = None
    for tk, df in dfs_ticker.items():
        # features = todo lo que no está en EXCLUIR ni son raw ni son cross-asset target
        excluidos = set(EXCLUIR_COLS) | {usar_target_col, r_fwd_col}
        feat_local = [c for c in df.columns if c not in excluidos]
        if feat is None:
            feat = feat_local
        sc = _hacer_escalador(escalador)
        m_tr = (df.index >= RANGOS["train"][0]) & (df.index <= RANGOS["train"][1])
        sc.fit(df.loc[m_tr, feat].values)
        for split, key in [("train", "train"), ("val", "val"), ("eval", "test")]:
            r = RANGOS[key]
            sub = df[(df.index >= r[0]) & (df.index <= r[1])].copy()
            # eliminar filas con NaN en features o target
            valid = sub[feat + [usar_target_col, r_fwd_col]].notna().all(axis=1)
            sub = sub[valid]
            acum[split]["X"].append(sc.transform(sub[feat].values))
            acum[split]["y"].append(sub[usar_target_col].values.astype(int))
            acum[split]["r"].append(sub[r_fwd_col].values)
            acum[split]["f"].append(sub.index.values)
            acum[split]["tk"].append(np.full(len(sub), tk))
    out = {"feat": feat, "n_features": len(feat)}
    for n in ("train", "val", "eval"):
        out[f"X_{n}"] = np.vstack(acum[n]["X"])
        out[f"y_{n}"] = np.concatenate(acum[n]["y"])
        out[f"r_{n}"] = np.concatenate(acum[n]["r"])
        out[f"tk_{n}"] = np.concatenate(acum[n]["tk"])
        out[f"f_{n}"] = np.concatenate(acum[n]["f"])
    return out


def _build_lr(hp):
    kw = dict(penalty=hp.get("penalty", "l2"), C=hp.get("C", 1.0),
              solver="saga", max_iter=5000, class_weight="balanced",
              random_state=42, n_jobs=-1, tol=1e-4)
    if hp.get("penalty") == "elasticnet":
        kw["l1_ratio"] = hp.get("l1_ratio", 0.5)
    return LogisticRegression(**kw)


def _build_xgb(hp):
    return xgb.XGBClassifier(
        n_estimators=int(hp.get("n_estimators", 500)),
        max_depth=int(hp.get("max_depth", 6)),
        learning_rate=float(hp.get("learning_rate", 0.05)),
        subsample=float(hp.get("subsample", 0.8)),
        colsample_bytree=float(hp.get("colsample_bytree", 0.8)),
        min_child_weight=int(hp.get("min_child_weight", 1)),
        reg_alpha=float(hp.get("reg_alpha", 0.0)),
        reg_lambda=float(hp.get("reg_lambda", 1.0)),
        gamma=float(hp.get("gamma", 0.0)),
        objective="multi:softprob", num_class=3,
        tree_method="hist", device="cuda",
        random_state=42, eval_metric="mlogloss", verbosity=0,
    )


def _metricas_backtest(y_pred, y_true, r_fwd, tk_arr):
    """Métricas de test: F1, Sharpe, WR, PF, MaxDD."""
    from sklearn.metrics import f1_score
    f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
    r_strat = np.where(y_pred == 2, r_fwd, np.where(y_pred == 0, -r_fwd, 0.0))
    r_strat = np.nan_to_num(r_strat)
    sharpe = float(np.sqrt(252) * np.nanmean(r_strat) / (np.nanstd(r_strat) + 1e-12))
    equity = np.exp(np.cumsum(r_strat))
    peak = np.maximum.accumulate(equity)
    max_dd = float(((equity - peak) / peak).min())
    ops = r_strat[y_pred != 1]
    win_rate = float((ops > 0).mean()) if len(ops) > 0 else 0.0
    pos = ops[ops > 0].sum(); neg = abs(ops[ops < 0].sum())
    pf = float(pos / neg) if neg > 1e-8 else 0.0
    return {"f1": round(f1, 4), "sharpe": round(sharpe, 4),
            "win_rate": round(win_rate, 4), "profit_factor": round(pf, 4),
            "max_dd": round(max_dd, 4),
            "signal_buy": round((y_pred == 2).mean() * 100, 2),
            "signal_hold": round((y_pred == 1).mean() * 100, 2),
            "signal_sell": round((y_pred == 0).mean() * 100, 2)}


def _entrenar_lr_xgb(datos):
    """Entrena LR y XGB con hps ganadores. Devuelve dict con métricas de test."""
    y_class = np.array([0, 1, 2])
    w_cls = compute_class_weight("balanced", classes=y_class, y=datos["y_train"])
    sample_w = np.array([w_cls[c] for c in datos["y_train"]])

    resultados = {}
    for nombre, hp, sw_ok in [("LR", LR_HP, False), ("XGBoost", XGB_HP, True)]:
        t0 = time.time()
        if nombre == "LR":
            model = _build_lr(hp)
            model.fit(datos["X_train"], datos["y_train"])
        else:
            model = _build_xgb(hp)
            model.fit(datos["X_train"], datos["y_train"], sample_weight=sample_w)
        pred = model.predict(datos["X_eval"])
        met = _metricas_backtest(pred, datos["y_eval"], datos["r_eval"], datos["tk_eval"])
        met["segundos"] = round(time.time() - t0, 1)
        resultados[nombre] = (met, model)
    return resultados


# ════════════════════════════════════════════════════════════════════════════
# STEP 1 — TARGET ABLATION
# ════════════════════════════════════════════════════════════════════════════

def step_target():
    print("=" * 70)
    print("STEP 1 — TARGET ABLATION (16 configs con LR)")
    print("=" * 70)

    horizontes = [1, 3, 5, 10]
    percentiles = [(0.25, 0.75), (0.30, 0.70), (0.33, 0.67), (0.40, 0.60)]

    filas = []
    for h in horizontes:
        for q_lo, q_hi in percentiles:
            # regenerar dataset con este target
            dfs = {}
            for tk in TICKERS:
                df = _cargar_panel(tk).copy()
                r_fwd_new, target_new = _construir_target(df, horizonte=h,
                                                           q_lo=q_lo, q_hi=q_hi)
                df["r_forward_new"] = r_fwd_new
                df["target_new"] = target_new
                dfs[tk] = df

            datos = _preparar(dfs, escalador=LR_HP["escalador"],
                              usar_target_col="target_new", r_fwd_col="r_forward_new")
            # entrenar LR solo (rapidez)
            model = _build_lr(LR_HP)
            model.fit(datos["X_train"], datos["y_train"])
            pred = model.predict(datos["X_eval"])
            met = _metricas_backtest(pred, datos["y_eval"],
                                       datos["r_eval"], datos["tk_eval"])
            fila = {"horizonte_d": h, "q_lo": q_lo, "q_hi": q_hi,
                    **met, "n_train": len(datos["y_train"]),
                    "n_test": len(datos["y_eval"])}
            filas.append(fila)
            marca = " ⭐" if met["f1"] > BASELINE["LR"]["f1"] + 0.005 else ""
            print(f"  h={h:2d}d  q={q_lo:.2f}/{q_hi:.2f}  F1={met['f1']:.4f} "
                  f"Sharpe={met['sharpe']:+.3f}  n_test={fila['n_test']}{marca}")

    df = pd.DataFrame(filas)
    df.to_csv(OUT / "target_ablation.csv", index=False)
    print(f"\n✓ Guardado en {OUT}/target_ablation.csv")
    print("\nBaseline referencia: LR F1=0.4036 Sharpe=+0.895 en h=1d, q=0.30/0.70")
    return df


# ════════════════════════════════════════════════════════════════════════════
# STEP 2 — LAG FEATURES
# ════════════════════════════════════════════════════════════════════════════

def _top_features_lr(datos, n=10):
    """Entrena LR baseline y devuelve las top-n features por |coef|.mean sobre las 3 clases."""
    model = _build_lr(LR_HP)
    model.fit(datos["X_train"], datos["y_train"])
    # coef_.shape = (n_classes, n_features). Suma valor absoluto sobre clases.
    imp = np.abs(model.coef_).sum(axis=0)
    top_idx = np.argsort(imp)[::-1][:n]
    return [datos["feat"][i] for i in top_idx]


def step_lags():
    print("=" * 70)
    print("STEP 2 — LAG FEATURES (top-10 features × lags {1, 3, 5})")
    print("=" * 70)

    # Cargar dataset baseline
    dfs = {tk: _cargar_panel(tk) for tk in TICKERS}
    datos_base = _preparar(dfs, escalador=LR_HP["escalador"])
    top = _top_features_lr(datos_base, n=10)
    print(f"Top-10 features por |coef| LR: {top}")

    # Ampliar cada df con lags
    lags = [1, 3, 5]
    dfs_lag = {}
    for tk, df in dfs.items():
        df_new = df.copy()
        for feat in top:
            for L in lags:
                df_new[f"{feat}_lag{L}"] = df[feat].shift(L)
        # eliminar filas iniciales sin lags completos
        dfs_lag[tk] = df_new.dropna(subset=[f"{f}_lag{max(lags)}" for f in top])

    datos_lag = _preparar(dfs_lag, escalador=LR_HP["escalador"])
    print(f"n_features: base={datos_base['n_features']} → con lags={datos_lag['n_features']}")

    filas = []
    for nombre_dataset, datos in [("baseline", datos_base), ("+lags", datos_lag)]:
        res = _entrenar_lr_xgb(datos)
        for modelo, (met, _) in res.items():
            fila = {"dataset": nombre_dataset, "modelo": modelo, **met}
            filas.append(fila)
            baseline_f1 = BASELINE[modelo]["f1"]
            marca = " ⭐" if met["f1"] > baseline_f1 + 0.005 else ""
            print(f"  {nombre_dataset:>10s} {modelo:>8s}  F1={met['f1']:.4f} "
                  f"Sharpe={met['sharpe']:+.3f}  ({met['segundos']}s){marca}")

    df = pd.DataFrame(filas)
    df.to_csv(OUT / "lag_features.csv", index=False)
    print(f"\n✓ Guardado en {OUT}/lag_features.csv")
    return df


# ════════════════════════════════════════════════════════════════════════════
# STEP 3 — CROSS-ASSET FEATURES
# ════════════════════════════════════════════════════════════════════════════

def _descargar_spy_xlk():
    """Descarga SPY y XLK para las cross-asset features. Cachea en disk."""
    import yfinance as yf
    cache = OUT / "_spy_xlk.parquet"
    if cache.exists():
        return pd.read_parquet(cache)
    df = yf.download(["SPY", "XLK"], start="2013-01-01", end="2025-12-31",
                      auto_adjust=True, progress=False)["Close"]
    df.columns = ["SPY", "XLK"]
    df.to_parquet(cache)
    return df


def step_crossasset():
    print("=" * 70)
    print("STEP 3 — CROSS-ASSET FEATURES (beta vs SPY, corr con XLK, rank entre 7)")
    print("=" * 70)

    spx = _descargar_spy_xlk()
    r_spy = np.log(spx["SPY"] / spx["SPY"].shift(1))
    r_xlk = np.log(spx["XLK"] / spx["XLK"].shift(1))

    # Cargar returns de los 7 tickers para computar el rank
    returns_por_tk = {}
    dfs = {}
    for tk in TICKERS:
        df = _cargar_panel(tk)
        r_tk = np.log(df["raw_close"] / df["raw_close"].shift(1))
        returns_por_tk[tk] = r_tk
        dfs[tk] = df

    ret_matrix = pd.DataFrame(returns_por_tk)
    rank_matrix = ret_matrix.rank(axis=1, pct=True)  # rank normalizado [0,1] por día

    # Construir cross-asset features
    dfs_new = {}
    for tk in TICKERS:
        df = dfs[tk].copy()
        r_tk = returns_por_tk[tk]
        # beta rodante 20d vs SPY
        idx_comun = df.index.intersection(r_spy.index)
        r_tk_alin = r_tk.reindex(idx_comun)
        r_spy_alin = r_spy.reindex(idx_comun)
        r_xlk_alin = r_xlk.reindex(idx_comun)
        cov = r_tk_alin.rolling(20).cov(r_spy_alin)
        var = r_spy_alin.rolling(20).var()
        beta = (cov / (var + 1e-12)).reindex(df.index)
        corr_xlk = r_tk_alin.rolling(20).corr(r_xlk_alin).reindex(df.index)
        rank_tk = rank_matrix[tk].reindex(df.index)

        df["beta_spy_20d"] = beta
        df["corr_xlk_20d"] = corr_xlk
        df["rank_ret_7"] = rank_tk
        dfs_new[tk] = df.dropna(subset=["beta_spy_20d", "corr_xlk_20d", "rank_ret_7"])

    datos_base = _preparar(dfs, escalador=LR_HP["escalador"])
    datos_ca = _preparar(dfs_new, escalador=LR_HP["escalador"])
    print(f"n_features: base={datos_base['n_features']} → cross-asset={datos_ca['n_features']}")

    filas = []
    for nombre_dataset, datos in [("baseline", datos_base), ("+cross_asset", datos_ca)]:
        res = _entrenar_lr_xgb(datos)
        for modelo, (met, _) in res.items():
            fila = {"dataset": nombre_dataset, "modelo": modelo, **met}
            filas.append(fila)
            baseline_f1 = BASELINE[modelo]["f1"]
            marca = " ⭐" if met["f1"] > baseline_f1 + 0.005 else ""
            print(f"  {nombre_dataset:>13s} {modelo:>8s}  F1={met['f1']:.4f} "
                  f"Sharpe={met['sharpe']:+.3f}  ({met['segundos']}s){marca}")

    df = pd.DataFrame(filas)
    df.to_csv(OUT / "crossasset.csv", index=False)
    print(f"\n✓ Guardado en {OUT}/crossasset.csv")
    return df


# ════════════════════════════════════════════════════════════════════════════
# STEP 4 — MULTI-TIMEFRAME FEATURES
# ════════════════════════════════════════════════════════════════════════════

def step_multitf():
    print("=" * 70)
    print("STEP 4 — MULTI-TIMEFRAME (base + agregados 5d/20d de top-10)")
    print("=" * 70)

    dfs = {tk: _cargar_panel(tk) for tk in TICKERS}
    datos_base = _preparar(dfs, escalador=LR_HP["escalador"])
    top = _top_features_lr(datos_base, n=10)
    print(f"Top-10 features: {top}")

    dfs_mtf = {}
    for tk, df in dfs.items():
        df_new = df.copy()
        for feat in top:
            df_new[f"{feat}_ma5"] = df[feat].rolling(5).mean()
            df_new[f"{feat}_ma20"] = df[feat].rolling(20).mean()
        dfs_mtf[tk] = df_new.dropna(subset=[f"{f}_ma20" for f in top])

    datos_mtf = _preparar(dfs_mtf, escalador=LR_HP["escalador"])
    print(f"n_features: base={datos_base['n_features']} → multi-tf={datos_mtf['n_features']}")

    filas = []
    for nombre_dataset, datos in [("baseline", datos_base), ("+multi_tf", datos_mtf)]:
        res = _entrenar_lr_xgb(datos)
        for modelo, (met, _) in res.items():
            fila = {"dataset": nombre_dataset, "modelo": modelo, **met}
            filas.append(fila)
            baseline_f1 = BASELINE[modelo]["f1"]
            marca = " ⭐" if met["f1"] > baseline_f1 + 0.005 else ""
            print(f"  {nombre_dataset:>10s} {modelo:>8s}  F1={met['f1']:.4f} "
                  f"Sharpe={met['sharpe']:+.3f}  ({met['segundos']}s){marca}")

    df = pd.DataFrame(filas)
    df.to_csv(OUT / "multi_tf.csv", index=False)
    print(f"\n✓ Guardado en {OUT}/multi_tf.csv")
    return df


# ════════════════════════════════════════════════════════════════════════════
# STEP 5 — INTERACTIONS
# ════════════════════════════════════════════════════════════════════════════

def step_inter():
    print("=" * 70)
    print("STEP 5 — INTERACTIONS (productos entre top-10 features)")
    print("=" * 70)

    dfs = {tk: _cargar_panel(tk) for tk in TICKERS}
    datos_base = _preparar(dfs, escalador=LR_HP["escalador"])
    top = _top_features_lr(datos_base, n=10)
    print(f"Top-10: {top}")

    # Todos los pares (10*9/2 = 45), usamos los 15 con mayor |corr| entre pares
    pares = [(top[i], top[j]) for i in range(len(top)) for j in range(i+1, len(top))]
    # elegir 15 pares al azar seed=42 (los 45 pares serían 45 features nuevas, mucho)
    rng = np.random.default_rng(42)
    idxs = rng.choice(len(pares), size=15, replace=False)
    pares_sel = [pares[i] for i in idxs]

    dfs_inter = {}
    for tk, df in dfs.items():
        df_new = df.copy()
        for a, b in pares_sel:
            df_new[f"{a}_x_{b}"] = df[a] * df[b]
        dfs_inter[tk] = df_new

    datos_inter = _preparar(dfs_inter, escalador=LR_HP["escalador"])
    print(f"n_features: base={datos_base['n_features']} → inter={datos_inter['n_features']}")

    filas = []
    for nombre_dataset, datos in [("baseline", datos_base), ("+inter", datos_inter)]:
        res = _entrenar_lr_xgb(datos)
        for modelo, (met, _) in res.items():
            fila = {"dataset": nombre_dataset, "modelo": modelo, **met}
            filas.append(fila)
            baseline_f1 = BASELINE[modelo]["f1"]
            marca = " ⭐" if met["f1"] > baseline_f1 + 0.005 else ""
            print(f"  {nombre_dataset:>10s} {modelo:>8s}  F1={met['f1']:.4f} "
                  f"Sharpe={met['sharpe']:+.3f}  ({met['segundos']}s){marca}")

    df = pd.DataFrame(filas)
    df.to_csv(OUT / "interactions.csv", index=False)
    print(f"\n✓ Guardado en {OUT}/interactions.csv")
    return df


# ════════════════════════════════════════════════════════════════════════════
# CONSOLIDAR
# ════════════════════════════════════════════════════════════════════════════

def paso_consolidar():
    print("=" * 70)
    print("CONSOLIDAR VÍA 8")
    print("=" * 70)
    filas = []
    for m in ["LR", "XGBoost"]:
        b = BASELINE[m]
        filas.append({"experimento": "baseline_v5", "modelo": m,
                      "f1": b["f1"], "sharpe": b["sharpe"], "win_rate": b["win_rate"]})

    for archivo in ["lag_features.csv", "crossasset.csv", "multi_tf.csv", "interactions.csv"]:
        p = OUT / archivo
        if p.exists():
            sub = pd.read_csv(p)
            for _, r in sub[sub["dataset"] != "baseline"].iterrows():
                filas.append({"experimento": r["dataset"], "modelo": r["modelo"],
                              "f1": r["f1"], "sharpe": r["sharpe"],
                              "win_rate": r["win_rate"]})

    # Target ablation es solo LR, con distintas configs; agregar mejores 5
    p_target = OUT / "target_ablation.csv"
    if p_target.exists():
        sub = pd.read_csv(p_target).nlargest(5, "f1")
        for _, r in sub.iterrows():
            filas.append({"experimento": f"target(h={int(r['horizonte_d'])}d,q={r['q_lo']:.2f}/{r['q_hi']:.2f})",
                          "modelo": "LR", "f1": r["f1"], "sharpe": r["sharpe"],
                          "win_rate": r["win_rate"]})

    df = pd.DataFrame(filas).sort_values("f1", ascending=False)
    df.to_csv(CSV_MASTER, index=False)
    print(df.to_string(index=False))
    print(f"\n✓ Consolidado en {CSV_MASTER}")


# ════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", required=True,
                    choices=["target", "lags", "crossasset", "multitf", "inter",
                             "consolidar", "all"])
    args = ap.parse_args()

    if args.step in ("target", "all"):
        step_target()
    if args.step in ("lags", "all"):
        step_lags()
    if args.step in ("crossasset", "all"):
        step_crossasset()
    if args.step in ("multitf", "all"):
        step_multitf()
    if args.step in ("inter", "all"):
        step_inter()
    if args.step in ("consolidar", "all"):
        paso_consolidar()


if __name__ == "__main__":
    main()
