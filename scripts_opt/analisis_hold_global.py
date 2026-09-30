"""
================================================================================
ANÁLISIS DEL MODELO ACTUAL: ¿POR QUÉ PREDICE TANTO HOLD? + 40/60 + GLOBAL vs POR-TICKER
================================================================================
No entrena ni despliega nada nuevo: sólo mide. Responde cuatro preguntas con
los mismos datos de Yahoo Finance (`tesis_ml_stocks/01_raw_datasets/`) y el
mismo protocolo de Vía 8 (Exp B: train 2018-2023, val 2024, test 2025):

  1) REPRODUCCIÓN. LR + 15 interactions (config de producción, C=0.000165,
     RobustScaler, class_weight=balanced) con escalador POR TICKER (como se
     evaluó en Vía 8) y con escalador GLOBAL (como lo entrena
     `entrenar_produccion.py`). ¿Cambia algo?

  2) ANATOMÍA DEL HOLD. Matriz de confusión, distribución real vs predicha,
     |retorno| por señal predicha, HOLD vs régimen de volatilidad (VIX_norm),
     forma de las probabilidades (confianza) y valor económico del HOLD
     (estrategia del modelo vs. la misma estrategia sin HOLD).

  3) PERCENTILES DEL TARGET. h=1d con q ∈ {20/80, 25/75, 30/70, 35/65, 40/60}
     (40/60 = "60/40": 40 % SELL, 20 % HOLD, 40 % BUY). Se reporta F1-macro,
     kappa de Cohen (comparable entre distribuciones de clases distintas),
     Sharpe y distribución predicha, en val 2024 y test 2025.
     Además: alternativa SIN reentrenar — desplazar el prior de HOLD
     (multiplicar P(HOLD) por k<1) y ver el trade-off HOLD% / F1 / Sharpe.

  4) GLOBAL vs POR-TICKER. (a) Los 5 modelos × 3 experimentos a partir de las
     predicciones guardadas de v5 (`RESULTADOS_OPTIMIZADOS/v5/preds/*.npz`),
     comparando manzanas con manzanas: el modelo global evaluado sobre las
     mismas filas de cada ticker que el modelo por-ticker. (b) La config de
     producción (LR + interactions) entrenada global vs 7 modelos por ticker.

Uso (desde la raíz del repo, ~1-2 min, sólo CPU, sin red):
    python scripts_opt/analisis_hold_global.py

Salidas: RESULTADOS_OPTIMIZADOS/analisis_hold/*.csv + resumen.json
Informe: RESULTADOS_OPTIMIZADOS/docs/ANALISIS_HOLD_Y_GLOBAL.md
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import sys, json, glob, functools, warnings
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
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import f1_score, cohen_kappa_score, confusion_matrix, precision_recall_fscore_support

from common import TICKERS, EXCLUIR_COLS, cargar_raw

OUT = Path("RESULTADOS_OPTIMIZADOS/analisis_hold")
OUT.mkdir(parents=True, exist_ok=True)
PREDS_V5 = Path("RESULTADOS_OPTIMIZADOS/v5/preds")
PARES_JSON = Path("api/ml/artifacts/interaction_pairs.json")

RANGOS = {
    "train": ("2018-01-01", "2023-12-31"),
    "val":   ("2024-01-01", "2024-12-31"),
    "test":  ("2025-01-01", "2025-12-31"),
}
# Hiperparámetros del modelo en producción (ganador Optuna v5, ver entrenar_produccion.py)
LR_KW = dict(penalty="l2", C=0.00016491236228800314, solver="saga", max_iter=5000,
             class_weight="balanced", random_state=42, n_jobs=-1, tol=1e-4)
NOMBRE = {0: "SELL", 1: "HOLD", 2: "BUY"}


# ════════════════════════════════════════════════════════════════════════════
# DATOS
# ════════════════════════════════════════════════════════════════════════════

def _pares():
    with open(PARES_JSON) as f:
        return [tuple(p) for p in json.load(f)["pairs"]]


def construir_target(df, horizonte, q_lo, q_hi, ventana=252):
    """Idéntico a via8_dataset._construir_target (percentiles rodantes, shift 1)."""
    close = df["raw_close"]
    r_fwd = np.log(close.shift(-horizonte) / close)
    lo = r_fwd.rolling(ventana, min_periods=ventana // 2).quantile(q_lo).shift(1)
    hi = r_fwd.rolling(ventana, min_periods=ventana // 2).quantile(q_hi).shift(1)
    y = np.where(r_fwd >= hi, 2, np.where(r_fwd <= lo, 0, 1))
    return r_fwd, pd.Series(y, index=df.index)


def cargar_paneles(q_lo=0.30, q_hi=0.70, horizonte=1, interactions=True):
    """dict{ticker: df} con 61 features (+15 interactions) y target_new/r_new."""
    pares = _pares() if interactions else []
    dfs = {}
    for tk in TICKERS:
        df = cargar_raw(tk).copy()
        for a, b in pares:
            df[f"{a}_x_{b}"] = df[a] * df[b]
        r_new, y_new = construir_target(df, horizonte, q_lo, q_hi)
        df["r_new"] = r_new
        df["y_new"] = y_new
        dfs[tk] = df
    return dfs


def preparar(dfs, escalador="por_ticker"):
    """X/y/r/tk/fecha por split. escalador: 'por_ticker' (Vía 8) o 'global' (producción)."""
    excl = set(EXCLUIR_COLS) | {"r_new", "y_new"}
    feat = [c for c in next(iter(dfs.values())).columns if c not in excl]
    partes = {s: [] for s in RANGOS}
    for tk, df in dfs.items():
        for s, (a, b) in RANGOS.items():
            sub = df[(df.index >= a) & (df.index <= b)]
            sub = sub[sub[feat + ["r_new", "y_new"]].notna().all(axis=1)]
            partes[s].append(pd.DataFrame({
                "tk": tk, "fecha": sub.index, "y": sub["y_new"].astype(int).values,
                "r": sub["r_new"].values, "VIX_norm": sub["VIX_norm"].values,
            }).assign(_X=list(sub[feat].values)))
    out = {"feat": feat}
    for s in RANGOS:
        d = pd.concat(partes[s], ignore_index=True)
        out[s] = {"X": np.vstack(d["_X"].values), "y": d["y"].values, "r": d["r"].values,
                  "tk": d["tk"].values, "fecha": pd.to_datetime(d["fecha"]).values,
                  "vix_norm": d["VIX_norm"].values}
    # escalado ajustado sólo con train
    if escalador == "global":
        sc = RobustScaler().fit(out["train"]["X"])
        for s in RANGOS:
            out[s]["X"] = sc.transform(out[s]["X"])
    else:
        for tk in TICKERS:
            m_tr = out["train"]["tk"] == tk
            sc = RobustScaler().fit(out["train"]["X"][m_tr])
            for s in RANGOS:
                m = out[s]["tk"] == tk
                out[s]["X"][m] = sc.transform(out[s]["X"][m])
    return out


# ════════════════════════════════════════════════════════════════════════════
# MÉTRICAS
# ════════════════════════════════════════════════════════════════════════════

def backtest(pred, r):
    """Mismo backtest que el paper/Vía 8: BUY=+r, SELL=-r, HOLD=0, serie apilada."""
    rs = np.nan_to_num(np.where(pred == 2, r, np.where(pred == 0, -r, 0.0)))
    sharpe = float(np.sqrt(252) * rs.mean() / (rs.std() + 1e-12))
    eq = np.exp(np.cumsum(rs)); peak = np.maximum.accumulate(eq)
    ops = rs[pred != 1]
    wr = float((ops > 0).mean()) if len(ops) else 0.0
    neg = abs(ops[ops < 0].sum())
    pf = float(ops[ops > 0].sum() / neg) if neg > 1e-8 else 0.0
    return {"sharpe": round(sharpe, 4), "win_rate": round(wr, 4),
            "profit_factor": round(pf, 4), "max_dd": round(float(((eq - peak) / peak).min()), 4)}


def sharpe_portafolio(pred, r, fechas):
    """Sharpe de un portafolio equiponderado de los 7 tickers (promedio diario)."""
    rs = np.nan_to_num(np.where(pred == 2, r, np.where(pred == 0, -r, 0.0)))
    diario = pd.Series(rs).groupby(pd.Series(fechas)).mean()
    return round(float(np.sqrt(252) * diario.mean() / (diario.std() + 1e-12)), 4)


def metricas(y, pred, r, fechas=None):
    p, rc, f, _ = precision_recall_fscore_support(y, pred, labels=[0, 1, 2], zero_division=0)
    m = {"f1_macro": round(f1_score(y, pred, average="macro", zero_division=0), 4),
         "kappa": round(cohen_kappa_score(y, pred), 4),
         **{f"f1_{NOMBRE[k].lower()}": round(f[k], 4) for k in range(3)},
         **{f"prec_{NOMBRE[k].lower()}": round(p[k], 4) for k in range(3)},
         **{f"recall_{NOMBRE[k].lower()}": round(rc[k], 4) for k in range(3)},
         **{f"real_{NOMBRE[k].lower()}_pct": round((y == k).mean() * 100, 1) for k in range(3)},
         **{f"pred_{NOMBRE[k].lower()}_pct": round((pred == k).mean() * 100, 1) for k in range(3)},
         **backtest(pred, r), "n": int(len(y))}
    if fechas is not None:
        m["sharpe_portafolio"] = sharpe_portafolio(pred, r, fechas)
    return m


def entrenar(d):
    return LogisticRegression(**LR_KW).fit(d["train"]["X"], d["train"]["y"])


# ════════════════════════════════════════════════════════════════════════════
# 1) REPRODUCCIÓN + 2) ANATOMÍA DEL HOLD
# ════════════════════════════════════════════════════════════════════════════

def paso_reproduccion_y_anatomia(resumen):
    print("=" * 78)
    print("1) REPRODUCCIÓN del modelo actual (LR + 15 interactions, 30/70, h=1d)")
    print("=" * 78)
    dfs = cargar_paneles(0.30, 0.70)
    filas, modelos = [], {}
    # (features, escalador): producción evaluada (Vía 8), producción tal cual se
    # entrena (escalador global) y el LR sin interactions como referencia.
    variantes = [("61+15 interactions", "por_ticker", dfs), ("61+15 interactions", "global", dfs),
                 ("61 base (sin interactions)", "por_ticker", cargar_paneles(0.30, 0.70, interactions=False))]
    for feats, esc, paneles in variantes:
        d = preparar(paneles, esc)
        mdl = entrenar(d)
        if feats.startswith("61+15"):
            modelos[esc] = (mdl, d)
        for s in ["val", "test"]:
            pr = mdl.predict(d[s]["X"])
            m = metricas(d[s]["y"], pr, d[s]["r"], d[s]["fecha"])
            filas.append({"features": feats, "escalador": esc, "split": s, **m})
            print(f"  {feats:27s} esc={esc:10s} {s:4s}  F1={m['f1_macro']:.4f} kappa={m['kappa']:.4f} "
                  f"Sharpe={m['sharpe']:+.3f}  pred B/H/S={m['pred_buy_pct']}/{m['pred_hold_pct']}/"
                  f"{m['pred_sell_pct']}  real B/H/S={m['real_buy_pct']}/{m['real_hold_pct']}/{m['real_sell_pct']}")
    pd.DataFrame(filas).to_csv(OUT / "1_reproduccion.csv", index=False)
    resumen["reproduccion"] = filas

    # ── 2) Anatomía del HOLD sobre el modelo evaluado (escalador por ticker) ──
    print("\n" + "=" * 78)
    print("2) ANATOMÍA DEL HOLD (test 2025, modelo evaluado en Vía 8)")
    print("=" * 78)
    mdl, d = modelos["por_ticker"]
    te = d["test"]
    proba = mdl.predict_proba(te["X"])
    pred = proba.argmax(1)
    y, r = te["y"], te["r"]

    cm = confusion_matrix(y, pred, labels=[0, 1, 2])
    cm_df = pd.DataFrame(cm, index=[f"real_{NOMBRE[k]}" for k in range(3)],
                         columns=[f"pred_{NOMBRE[k]}" for k in range(3)])
    cm_df.to_csv(OUT / "2a_matriz_confusion_test.csv")
    print("\n  Matriz de confusión (filas=real, columnas=predicho):")
    print(cm_df.to_string())

    # |retorno| siguiente por señal predicha
    abs_r = pd.DataFrame({"pred": [NOMBRE[k] for k in pred], "abs_r_pct": np.abs(r) * 100,
                          "real_hold": (y == 1)})
    tab_absr = abs_r.groupby("pred").agg(n=("abs_r_pct", "size"),
                                         abs_ret_medio_pct=("abs_r_pct", "mean"),
                                         abs_ret_mediana_pct=("abs_r_pct", "median"),
                                         pct_real_hold=("real_hold", "mean")).round(4)
    tab_absr["pct_real_hold"] = (tab_absr["pct_real_hold"] * 100).round(1)
    tab_absr.to_csv(OUT / "2b_abs_retorno_por_senal.csv")
    print("\n  |retorno del día siguiente| según la señal predicha:")
    print(tab_absr.to_string())

    # HOLD vs régimen de volatilidad (quintiles de VIX_norm)
    q = pd.qcut(te["vix_norm"], 5, labels=["Q1 (VIX bajo)", "Q2", "Q3", "Q4", "Q5 (VIX alto)"])
    reg = pd.DataFrame({"quintil_VIX_norm": q, "pred_hold": pred == 1, "real_hold": y == 1,
                        "abs_r_pct": np.abs(r) * 100})
    tab_vix = reg.groupby("quintil_VIX_norm", observed=True).agg(
        n=("pred_hold", "size"), pred_hold_pct=("pred_hold", "mean"),
        real_hold_pct=("real_hold", "mean"), abs_ret_medio_pct=("abs_r_pct", "mean"))
    tab_vix[["pred_hold_pct", "real_hold_pct"]] *= 100
    tab_vix = tab_vix.round(2)
    tab_vix.to_csv(OUT / "2c_hold_vs_vix.csv")
    print("\n  HOLD según régimen de volatilidad (VIX_norm = VIX vs su media de 252d):")
    print(tab_vix.to_string())

    # Forma de las probabilidades
    conf = proba.max(1)
    orden = np.sort(proba, axis=1)
    margen = orden[:, -1] - orden[:, -2]
    prob_stats = {
        "p_media_sell": round(float(proba[:, 0].mean()), 4),
        "p_media_hold": round(float(proba[:, 1].mean()), 4),
        "p_media_buy": round(float(proba[:, 2].mean()), 4),
        "confianza_min": round(float(conf.min()), 4),
        "confianza_p25": round(float(np.percentile(conf, 25)), 4),
        "confianza_mediana": round(float(np.median(conf)), 4),
        "confianza_p75": round(float(np.percentile(conf, 75)), 4),
        "confianza_max": round(float(conf.max()), 4),
        "margen_top1_top2_mediana": round(float(np.median(margen)), 4),
        "pct_margen_menor_2pp": round(float((margen < 0.02).mean() * 100), 1),
        "norma_coef_por_clase": {NOMBRE[k]: round(float(np.linalg.norm(mdl.coef_[i])), 4)
                                  for i, k in enumerate(mdl.classes_)},
        "intercepto_por_clase": {NOMBRE[k]: round(float(mdl.intercept_[i]), 4)
                                  for i, k in enumerate(mdl.classes_)},
    }
    # confianza por señal predicha y acierto por tramo de confianza
    tramos = pd.cut(conf, [0, 0.36, 0.38, 0.40, 0.45, 1.0])
    tab_conf = pd.DataFrame({"tramo_confianza": tramos, "acierto": pred == y,
                             "pred": [NOMBRE[k] for k in pred]}).groupby(
        "tramo_confianza", observed=True).agg(n=("acierto", "size"), accuracy=("acierto", "mean"))
    tab_conf["accuracy"] = (tab_conf["accuracy"] * 100).round(1)
    tab_conf.to_csv(OUT / "2d_accuracy_por_confianza.csv")
    prob_stats["confianza_mediana_por_senal"] = {
        NOMBRE[k]: round(float(np.median(conf[pred == k])), 4) for k in range(3) if (pred == k).any()}
    # "Voto dividido": en los días HOLD, ¿el modelo cree que NO habrá movimiento,
    # o cree que sí lo habrá pero no sabe hacia dónde?
    h = pred == 1
    prob_stats["voto_dividido"] = {
        "p_media_en_dias_hold": {"SELL": round(float(proba[h, 0].mean()), 4),
                                 "HOLD": round(float(proba[h, 1].mean()), 4),
                                 "BUY": round(float(proba[h, 2].mean()), 4)},
        "pct_hold_con_p_hold_menor_0.5": round(float((proba[h, 1] < 0.5).mean() * 100), 1),
        "pct_hold_con_p_buy_mas_p_sell_mayor_p_hold": round(
            float(((proba[h, 0] + proba[h, 2]) > proba[h, 1]).mean() * 100), 1),
    }
    print("\n  Probabilidades del modelo (confianza = prob. de la clase elegida):")
    for k, v in prob_stats.items():
        print(f"    {k}: {v}")
    print("\n  Accuracy por tramo de confianza:")
    print(tab_conf.to_string())

    # Valor económico del HOLD (val 2024 y test 2025): misma estrategia sin HOLD,
    # buy & hold, y 500 permutaciones aleatorias con la misma distribución B/H/S.
    valor = {}
    for s in ["val", "test"]:
        ds = d[s]
        p_s = mdl.predict_proba(ds["X"])
        pr_s = p_s.argmax(1)
        r_s = ds["r"]
        pred_sin_hold = np.where(p_s[:, 2] >= p_s[:, 0], 2, 0)
        rng = np.random.default_rng(42)
        sh_rand = [backtest(rng.permutation(pr_s), r_s)["sharpe"] for _ in range(500)]
        sh_mod = backtest(pr_s, r_s)["sharpe"]
        valor[s] = {
            "modelo": backtest(pr_s, r_s) | {"sharpe_portafolio": sharpe_portafolio(pr_s, r_s, ds["fecha"])},
            "modelo_sin_hold": backtest(pred_sin_hold, r_s) | {
                "sharpe_portafolio": sharpe_portafolio(pred_sin_hold, r_s, ds["fecha"])},
            "siempre_largo_buy_and_hold": backtest(np.full_like(pr_s, 2), r_s) | {
                "sharpe_portafolio": sharpe_portafolio(np.full_like(pr_s, 2), r_s, ds["fecha"])},
            "aleatorio_misma_distribucion_sharpe_p50": round(float(np.median(sh_rand)), 4),
            "aleatorio_misma_distribucion_sharpe_p95": round(float(np.percentile(sh_rand, 95)), 4),
            "pct_aleatorios_con_sharpe_mayor_o_igual_al_modelo": round(
                float((np.array(sh_rand) >= sh_mod).mean() * 100), 1),
        }
        print(f"\n  Valor económico del HOLD ({s}):")
        for k, v in valor[s].items():
            print(f"    {k}: {v}")

    # HOLD por ticker
    tab_tk = pd.DataFrame({"tk": te["tk"], "pred": pred, "y": y}).groupby("tk").apply(
        lambda g: pd.Series({"pred_hold_pct": round((g.pred == 1).mean() * 100, 1),
                             "real_hold_pct": round((g.y == 1).mean() * 100, 1),
                             "pred_buy_pct": round((g.pred == 2).mean() * 100, 1),
                             "pred_sell_pct": round((g.pred == 0).mean() * 100, 1)}))
    tab_tk.to_csv(OUT / "2e_hold_por_ticker.csv")
    print("\n  Distribución predicha por ticker (test 2025):")
    print(tab_tk.to_string())

    resumen["anatomia_hold"] = {"probabilidades": prob_stats, "valor_economico": valor,
                                "abs_retorno_por_senal": tab_absr.reset_index().to_dict("records"),
                                "hold_vs_vix": tab_vix.reset_index().astype({"quintil_VIX_norm": str}).to_dict("records")}
    return modelos


# ════════════════════════════════════════════════════════════════════════════
# 3) PERCENTILES DEL TARGET (incluye 40/60) + desplazamiento del prior de HOLD
# ════════════════════════════════════════════════════════════════════════════

def paso_percentiles(resumen, modelos):
    print("\n" + "=" * 78)
    print("3) PERCENTILES DEL TARGET (h=1d, LR + interactions, escalador por ticker)")
    print("=" * 78)
    filas = []
    for q_lo, q_hi in [(0.20, 0.80), (0.25, 0.75), (0.30, 0.70), (0.35, 0.65), (0.40, 0.60)]:
        d = preparar(cargar_paneles(q_lo, q_hi), "por_ticker")
        mdl = entrenar(d)
        for s in ["val", "test"]:
            pr = mdl.predict(d[s]["X"])
            m = metricas(d[s]["y"], pr, d[s]["r"], d[s]["fecha"])
            filas.append({"q": f"{int(q_lo*100)}/{int(q_hi*100)}", "split": s, **m})
            print(f"  q={q_lo:.2f}/{q_hi:.2f} {s:4s}  F1={m['f1_macro']:.4f} kappa={m['kappa']:+.4f} "
                  f"Sharpe={m['sharpe']:+.3f} WR={m['win_rate']:.3f}  real B/H/S="
                  f"{m['real_buy_pct']}/{m['real_hold_pct']}/{m['real_sell_pct']}  pred B/H/S="
                  f"{m['pred_buy_pct']}/{m['pred_hold_pct']}/{m['pred_sell_pct']}")
    tab = pd.DataFrame(filas)
    tab.to_csv(OUT / "3a_percentiles_target.csv", index=False)
    resumen["percentiles"] = filas

    # Alternativa sin reentrenar: bajar el peso de HOLD en la decisión
    print("\n  Desplazamiento del prior de HOLD (mismo modelo 30/70, sin reentrenar):")
    mdl, d = modelos["por_ticker"]
    filas2 = []
    for k in [1.00, 0.97, 0.95, 0.92, 0.90, 0.85, 0.80]:
        for s in ["val", "test"]:
            p = mdl.predict_proba(d[s]["X"]).copy()
            p[:, 1] *= k
            pr = p.argmax(1)
            m = metricas(d[s]["y"], pr, d[s]["r"], d[s]["fecha"])
            filas2.append({"factor_hold": k, "split": s, **m})
            print(f"    k={k:.2f} {s:4s}  HOLD pred={m['pred_hold_pct']:5.1f}%  F1={m['f1_macro']:.4f} "
                  f"kappa={m['kappa']:+.4f} Sharpe={m['sharpe']:+.3f}")
    pd.DataFrame(filas2).to_csv(OUT / "3b_prior_hold.csv", index=False)
    resumen["prior_hold"] = filas2


# ════════════════════════════════════════════════════════════════════════════
# 4) GLOBAL vs POR-TICKER
# ════════════════════════════════════════════════════════════════════════════

def _cargar_npz(path):
    z = np.load(path, allow_pickle=True)
    return pd.DataFrame({"tk": z["tk"], "fecha": z["fechas"], "y": z["y"], "r": z["r"],
                         "pred": z["probs"].argmax(1)})


def paso_global_vs_porticker(resumen):
    print("\n" + "=" * 78)
    print("4a) GLOBAL vs POR-TICKER — 5 modelos × 3 experimentos (predicciones v5)")
    print("=" * 78)
    filas_tk = []
    for modelo in ["LR", "XGBoost", "LSTM", "CNN", "CNN-LSTM"]:
        for exp in ["A", "B", "C"]:
            fg = PREDS_V5 / f"{modelo}_{exp}_global_GLOBAL_v1.npz"
            if not fg.exists():
                continue
            g = _cargar_npz(fg)
            for tk in TICKERS:
                fp = PREDS_V5 / f"{modelo}_{exp}_por_ticker_{tk}_v1.npz"
                if not fp.exists():
                    continue
                p = _cargar_npz(fp)
                gg = g[g.tk == tk].merge(p[["fecha", "pred"]], on="fecha", suffixes=("_g", "_pt"))
                for tipo, col in [("global", "pred_g"), ("por_ticker", "pred_pt")]:
                    pr = gg[col].values
                    filas_tk.append({"modelo": modelo, "exp": exp, "ticker": tk, "tipo": tipo,
                                     "n": len(gg),
                                     "f1_macro": f1_score(gg.y, pr, average="macro", zero_division=0),
                                     "sharpe": backtest(pr, gg.r.values)["sharpe"],
                                     "pred_hold_pct": (pr == 1).mean() * 100})
    det = pd.DataFrame(filas_tk)
    det.to_csv(OUT / "4a_global_vs_porticker_detalle.csv", index=False)

    piv = det.pivot_table(index=["modelo", "exp", "ticker"], columns="tipo",
                          values=["f1_macro", "sharpe"]).reset_index()
    piv.columns = ["_".join(c).strip("_") for c in piv.columns]
    piv["gana_global_f1"] = piv["f1_macro_global"] > piv["f1_macro_por_ticker"]
    piv["gana_global_sharpe"] = piv["sharpe_global"] > piv["sharpe_por_ticker"]
    res = piv.groupby(["modelo", "exp"]).agg(
        f1_global=("f1_macro_global", "mean"), f1_por_ticker=("f1_macro_por_ticker", "mean"),
        sharpe_global=("sharpe_global", "mean"), sharpe_por_ticker=("sharpe_por_ticker", "mean"),
        tickers_gana_global_f1=("gana_global_f1", "sum"),
        tickers_gana_global_sharpe=("gana_global_sharpe", "sum")).round(4)
    res["delta_f1_global_menos_pt"] = (res["f1_global"] - res["f1_por_ticker"]).round(4)
    res.to_csv(OUT / "4a_global_vs_porticker_resumen.csv")
    print(res.to_string())

    # Resumen por modelo (promediando los 3 experimentos) + test de signo
    from scipy.stats import binomtest, wilcoxon
    por_modelo = []
    for modelo, sub in piv.groupby("modelo"):
        dif = sub["f1_macro_global"] - sub["f1_macro_por_ticker"]
        dif_sh = sub["sharpe_global"] - sub["sharpe_por_ticker"]
        wins = int((dif > 0).sum()); n = int((dif != 0).sum())
        por_modelo.append({
            "modelo": modelo, "celdas": len(sub),
            "f1_global_medio": round(sub["f1_macro_global"].mean(), 4),
            "f1_por_ticker_medio": round(sub["f1_macro_por_ticker"].mean(), 4),
            "delta_f1_medio": round(dif.mean(), 4),
            "celdas_gana_global_f1": wins,
            "p_signo_f1": round(binomtest(wins, n, 0.5).pvalue, 4) if n else None,
            "p_wilcoxon_f1": round(wilcoxon(dif).pvalue, 4) if n else None,
            "sharpe_global_medio": round(sub["sharpe_global"].mean(), 3),
            "sharpe_por_ticker_medio": round(sub["sharpe_por_ticker"].mean(), 3),
            "celdas_gana_global_sharpe": int((dif_sh > 0).sum()),
        })
    por_modelo = pd.DataFrame(por_modelo)
    por_modelo.to_csv(OUT / "4a_global_vs_porticker_por_modelo.csv", index=False)
    print("\n  Por modelo (21 celdas = 3 experimentos × 7 tickers):")
    print(por_modelo.to_string(index=False))
    resumen["global_vs_porticker_v5"] = por_modelo.to_dict("records")

    # ── 4b) Config de producción: LR + interactions ──
    print("\n" + "=" * 78)
    print("4b) GLOBAL vs POR-TICKER — config de producción (LR + interactions, Exp B)")
    print("=" * 78)
    d = preparar(cargar_paneles(0.30, 0.70), "por_ticker")
    mdl_g = entrenar(d)
    filas = []
    for s in ["val", "test"]:
        pred_g = mdl_g.predict(d[s]["X"])
        pred_pt = np.zeros_like(pred_g)
        for tk in TICKERS:
            m_tr = d["train"]["tk"] == tk
            m_s = d[s]["tk"] == tk
            mdl_tk = LogisticRegression(**LR_KW).fit(d["train"]["X"][m_tr], d["train"]["y"][m_tr])
            pred_pt[m_s] = mdl_tk.predict(d[s]["X"][m_s])
        for tipo, pr in [("global", pred_g), ("por_ticker", pred_pt)]:
            m = metricas(d[s]["y"], pr, d[s]["r"], d[s]["fecha"])
            f1_tk = [f1_score(d[s]["y"][d[s]["tk"] == tk], pr[d[s]["tk"] == tk], average="macro")
                     for tk in TICKERS]
            filas.append({"tipo": tipo, "split": s, "f1_medio_por_ticker": round(float(np.mean(f1_tk)), 4),
                          **m})
            print(f"  {tipo:10s} {s:4s}  F1 agregado={m['f1_macro']:.4f}  F1 medio por ticker="
                  f"{np.mean(f1_tk):.4f}  Sharpe={m['sharpe']:+.3f}  pred HOLD={m['pred_hold_pct']}%")
    pd.DataFrame(filas).to_csv(OUT / "4b_global_vs_porticker_produccion.csv", index=False)
    resumen["global_vs_porticker_produccion"] = filas


def main():
    resumen = {}
    modelos = paso_reproduccion_y_anatomia(resumen)
    paso_percentiles(resumen, modelos)
    paso_global_vs_porticker(resumen)
    with open(OUT / "resumen.json", "w", encoding="utf-8") as f:
        json.dump(resumen, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n✓ Resultados en {OUT}/")


if __name__ == "__main__":
    main()
