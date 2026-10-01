"""
================================================================================
CONFIRMACIÓN EN 2026 DE LAS DOS MEJORES ALTERNATIVAS PARA REDUCIR HOLD
================================================================================
`ajuste_hold_rolling.py` dejó dos candidatas (ninguna significativa en
2019-2024). Aquí se prueban sobre 2026, que ninguna regla vio al elegirse,
con datos reales de Yahoo y el mismo código de la API:

  0) Referencia: el modelo de producción con pesos "balanced" puros
     (reentrenado aquí igual que `entrenar_produccion.py`, para que la
     comparación no dependa de qué `.pkl` esté desplegado).
  A) Ese mismo modelo + regla de proporción móvil causal
     (π = 0.40, ventana de 252 días hábiles, 7 tickers juntos).
  B) Modelo de producción reentrenado igual que `entrenar_produccion.py`
     (2018-2025, mismas features e hiperparámetros) con el peso de clase de
     HOLD multiplicado por PESO_HOLD (de entrenar_produccion.py); argmax normal.

Requiere red. ~4 min (dos reentrenamientos + descarga de 7 tickers).

Uso:  python scripts_opt/ajuste_hold_2026.py
Salida: RESULTADOS_OPTIMIZADOS/analisis_hold/8_confirmacion_2026.csv
"""
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import cohen_kappa_score, f1_score
from sklearn.preprocessing import RobustScaler

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "api"))
sys.path.insert(0, str(RAIZ / "scripts_opt"))
from ml.features import FEATURE_COLUMNS, PARES_INTERACTION, build_feature_frame, fetch_market_context, fetch_ohlcv  # noqa: E402
from ml.target import etiquetas_reales  # noqa: E402
from common import TICKERS, cargar_raw  # noqa: E402
from entrenar_produccion import LR_HP, PESO_HOLD, pesos_de_clase  # noqa: E402
from evaluar_produccion_2026 import sin_vela_en_curso  # noqa: E402
from ajuste_hold_rolling import decidir_umbral, margen_hold  # noqa: E402

OUT = RAIZ / "RESULTADOS_OPTIMIZADOS" / "analisis_hold" / "8_confirmacion_2026.csv"
PI, N = 0.40, 252


def entrenar_con_peso_hold(peso: float):
    X, y = [], []
    for tk in TICKERS:
        df = cargar_raw(tk)
        df = df[(df.index >= "2018-01-01") & (df.index <= "2025-12-31")].copy()
        for a, b in PARES_INTERACTION:
            df[f"{a}_x_{b}"] = df[a] * df[b]
        df = df[FEATURE_COLUMNS + ["target"]].dropna()
        X.append(df[FEATURE_COLUMNS].values)
        y.append(df["target"].astype(int).values)
    X, y = np.vstack(X), np.concatenate(y)
    hp = {**LR_HP, "class_weight": pesos_de_clase(y, peso)}
    sc = RobustScaler().fit(X)
    return sc, LogisticRegression(**hp).fit(sc.transform(X), y)


def metricas(d, pred, etiqueta):
    real = d.real.map({"sell": 0, "hold": 1, "buy": 2}).values
    rs = np.where(pred == 2, d.r, np.where(pred == 0, -d.r, 0.0))
    port = pd.Series(rs).groupby(d.fecha.values).mean()
    return {"regla": etiqueta, "f1_macro": f1_score(real, pred, average="macro"),
            "kappa": cohen_kappa_score(real, pred), "pred_hold_pct": (pred == 1).mean() * 100,
            "real_hold_pct": (real == 1).mean() * 100,
            "sharpe": np.sqrt(252) * rs.mean() / rs.std(),
            "sharpe_portafolio": np.sqrt(252) * port.mean() / port.std()}


def main():
    sc_b, lr_b = entrenar_con_peso_hold(1.0)
    sc_w, lr_w = entrenar_con_peso_hold(PESO_HOLD)
    mercado = sin_vela_en_curso(fetch_market_context("3y"))
    filas = []
    for tk in ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]:
        ohlcv = sin_vela_en_curso(fetch_ohlcv(tk, "3y"))
        feat = build_feature_frame(ohlcv, mercado)
        X = feat[FEATURE_COLUMNS].values
        P = lr_b.predict_proba(sc_b.transform(X))
        Pw = lr_w.predict_proba(sc_w.transform(X))
        reales = etiquetas_reales(ohlcv["Close"]).reindex(feat.index)
        filas.append(pd.DataFrame({"fecha": feat.index, "ticker": tk,
                                   "p_sell": P[:, 0], "p_hold": P[:, 1], "p_buy": P[:, 2],
                                   "pred_peso": Pw.argmax(1),
                                   "real": reales["real"].values, "r": reales["r_forward"].values}))
    d = pd.concat(filas, ignore_index=True).sort_values(["fecha", "ticker"]).reset_index(drop=True)

    # Umbral causal: cuantil (1-π) de los márgenes de los N días hábiles previos
    d["s"] = margen_hold(d[["p_sell", "p_hold", "p_buy"]].values)
    por_dia = d.groupby("fecha").s.apply(np.array)
    tau = {}
    for i, f in enumerate(por_dia.index):
        if i >= N:
            tau[f] = np.quantile(np.concatenate(por_dia.iloc[i - N:i].values), 1 - PI)
    d["tau"] = d.fecha.map(tau)

    ev = d[(d.fecha >= "2026-01-01")].dropna(subset=["real", "tau"]).reset_index(drop=True)
    P = ev[["p_sell", "p_hold", "p_buy"]].values
    res = pd.DataFrame([
        metricas(ev, P.argmax(1), "balanced, argmax (modelo anterior)"),
        metricas(ev, decidir_umbral(P, ev.tau.values), f"balanced + proporción móvil causal (π={PI}, N={N})"),
        metricas(ev, ev.pred_peso.values, f"reentrenado con peso HOLD x{PESO_HOLD:g}"),
    ])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    res.to_csv(OUT, index=False)
    print(f"2026 fuera de muestra: {ev.fecha.min().date()} → {ev.fecha.max().date()}, n={len(ev)}")
    print(res.round(4).to_string(index=False))

    ev["mes"] = ev.fecha.dt.to_period("M")
    ev["pred_regla"] = decidir_umbral(P, ev.tau.values)
    mens = ev.groupby("mes").agg(hold_actual=("p_hold", lambda s: (P[s.index].argmax(1) == 1).mean() * 100),
                                 hold_regla=("pred_regla", lambda s: (s == 1).mean() * 100),
                                 hold_peso=("pred_peso", lambda s: (s == 1).mean() * 100),
                                 hold_real=("real", lambda s: (s == "hold").mean() * 100))
    print("\nHOLD por mes (%):")
    print(mens.round(1).to_string())


if __name__ == "__main__":
    main()
