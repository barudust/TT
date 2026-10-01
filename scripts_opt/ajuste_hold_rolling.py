"""
================================================================================
AJUSTE DE LA REGLA DE DECISIÓN DE HOLD — selección por origen rodante
================================================================================
No cambia el target (30/70, h=1d) ni reentrena el modelo de producción: solo
elige cómo se convierte su vector de probabilidades en una señal.

Regla:  señal = argmax_c  w_c · P(c | x),   con w = (1, k, 1) para (SELL, HOLD, BUY)

Equivale a sumar log(k) al logit de HOLD (un desplazamiento del intercepto),
es decir, a una regla de decisión con costos / umbral por clase. Con k = 1 es
el argmax de siempre.

Cómo se elige k sin tocar los años de prueba (origen rodante):
  - Para cada año Y en 2019..2025 se entrena el MISMO pipeline de producción
    (`entrenar_produccion.py`: 61 features + 15 interactions, RobustScaler
    global, LR L2 C=0.000165, class_weight=balanced) con los 6 años previos
    [Y-6, Y-1] y se predice Y completo.
  - k se elige maximizando el F1-macro MEDIO de 2019-2024 (6 años de
    desarrollo). 2025 (test del paper) y 2026 (modelo de producción real,
    fuera de muestra, ver evaluar_produccion_2026.py) solo se usan para
    confirmar, nunca para elegir.
  - Se repite todo con el LR de 61 features sin interactions para responder
    si las interactions de Vía 8 aportan fuera del año en que se eligieron.

Uso (desde la raíz del repo, ~1 min, sin red):
    python scripts_opt/ajuste_hold_rolling.py

Salidas: RESULTADOS_OPTIMIZADOS/analisis_hold/7_*.csv y 7_ajuste_hold.json
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import sys, json, functools, warnings
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
from sklearn.metrics import f1_score, cohen_kappa_score
from scipy.stats import wilcoxon

from common import TICKERS, cargar_raw
from entrenar_produccion import FEATURES_BASE, LR_HP

OUT = Path("RESULTADOS_OPTIMIZADOS/analisis_hold")
OUT.mkdir(parents=True, exist_ok=True)
PARES = [tuple(p) for p in json.load(open("api/ml/artifacts/interaction_pairs.json"))["pairs"]]
# 2026 con el modelo de producción "balanced" (antes del ajuste de HOLD)
PROD_2026 = OUT / "6_produccion_2026_LR-v8-interactions-produccion.csv"

ANIOS_DESARROLLO = list(range(2019, 2025))   # para elegir k
ANIOS_CONFIRMACION = [2025]                  # + 2026 con el modelo de producción
VENTANA_TRAIN = 6                            # como Exp B
K_GRID = np.round(np.arange(0.80, 1.0001, 0.01), 2)
PESOS_HOLD = (0.95, 0.90, 0.85, 0.80)          # peso de clase de HOLD al reentrenar


def panel(interactions: bool) -> pd.DataFrame:
    partes = []
    for tk in TICKERS:
        df = cargar_raw(tk).copy()
        cols = list(FEATURES_BASE)
        if interactions:
            for a, b in PARES:
                df[f"{a}_x_{b}"] = df[a] * df[b]
                cols.append(f"{a}_x_{b}")
        df = df[cols + ["target", "r_forward"]].dropna()
        df["ticker"] = tk
        df["fecha"] = df.index
        partes.append(df.reset_index(drop=True))
    d = pd.concat(partes, ignore_index=True)
    d.attrs["features"] = cols
    return d


def predecir_anio(d: pd.DataFrame, anio: int, peso_hold: float = 1.0) -> pd.DataFrame:
    """Entrena con [anio-6, anio-1] (pipeline de producción) y predice `anio`.
    También devuelve las probabilidades sobre el último año de entrenamiento
    (`parte="train_ultimo_anio"`), que usan las reglas adaptativas para fijar
    su umbral inicial sin mirar el año evaluado.
    `peso_hold` multiplica el peso de clase "balanced" de HOLD al entrenar."""
    feats = d.attrs["features"]
    tr = d[(d.fecha >= f"{anio - VENTANA_TRAIN}-01-01") & (d.fecha <= f"{anio - 1}-12-31")]
    ev = d[(d.fecha >= f"{anio}-01-01") & (d.fecha <= f"{anio}-12-31")]
    y_tr = tr["target"].astype(int).values
    hp = dict(LR_HP)
    if peso_hold != 1.0:
        frec = np.bincount(y_tr, minlength=3) / len(y_tr)
        hp["class_weight"] = {c: 1 / (3 * frec[c]) * (peso_hold if c == 1 else 1.0) for c in range(3)}
    sc = RobustScaler().fit(tr[feats].values)
    lr = LogisticRegression(**hp).fit(sc.transform(tr[feats].values), y_tr)
    salidas = []
    for parte, sub in [("eval", ev), ("train_ultimo_anio", tr[tr.fecha >= f"{anio - 1}-01-01"])]:
        p = lr.predict_proba(sc.transform(sub[feats].values))     # columnas: SELL, HOLD, BUY
        salidas.append(pd.DataFrame({"anio": anio, "parte": parte, "fecha": sub.fecha.values,
                                     "ticker": sub.ticker.values, "y": sub["target"].astype(int).values,
                                     "r": sub["r_forward"].values,
                                     "p_sell": p[:, 0], "p_hold": p[:, 1], "p_buy": p[:, 2]}))
    return pd.concat(salidas, ignore_index=True)


def decidir(P: np.ndarray, k: float) -> np.ndarray:
    w = np.array([1.0, k, 1.0])
    return (P * w).argmax(1)


def metricas(y, pred, r, fechas):
    rs = np.nan_to_num(np.where(pred == 2, r, np.where(pred == 0, -r, 0.0)))
    port = pd.Series(rs).groupby(pd.Series(fechas)).mean()
    ops = rs[pred != 1]
    return {
        "f1_macro": f1_score(y, pred, average="macro", zero_division=0),
        "kappa": cohen_kappa_score(y, pred),
        "pred_hold_pct": (pred == 1).mean() * 100,
        "real_hold_pct": (y == 1).mean() * 100,
        "sharpe": float(np.sqrt(252) * rs.mean() / (rs.std() + 1e-12)),
        "sharpe_portafolio": float(np.sqrt(252) * port.mean() / (port.std() + 1e-12)),
        "win_rate": float((ops > 0).mean()) if len(ops) else np.nan,
        "exposicion_pct": (pred != 1).mean() * 100,
    }


def evaluar(preds: pd.DataFrame, etiqueta: str) -> pd.DataFrame:
    filas = []
    if "parte" in preds:
        preds = preds[preds.parte == "eval"]
    for anio, g in preds.groupby("anio"):
        P = g[["p_sell", "p_hold", "p_buy"]].values
        for k in K_GRID:
            filas.append({"features": etiqueta, "anio": anio, "k": k,
                          **metricas(g.y.values, decidir(P, k), g.r.values, g.fecha.values)})
    return pd.DataFrame(filas)


def margen_hold(P: np.ndarray) -> np.ndarray:
    """s = log P(HOLD) − log max(P(BUY), P(SELL)). El argmax normal es s > 0;
    multiplicar P(HOLD) por k equivale a exigir s > −log k."""
    return np.log(P[:, 1]) - np.log(np.maximum(P[:, 0], P[:, 2]))


def decidir_umbral(P: np.ndarray, tau) -> np.ndarray:
    direccion = np.where(P[:, 2] >= P[:, 0], 2, 0)
    return np.where(margen_hold(P) > tau, 1, direccion)


def reglas_adaptativas(preds: pd.DataFrame, pi: float = 0.40) -> pd.DataFrame:
    """Reglas que fijan la PROPORCIÓN de HOLD en vez de un factor constante.
    (a) por año: τ tal que en el último año de entrenamiento se prediga HOLD
        una fracción `pi` (la proporción de diseño de la etiqueta 30/70).
    (b) causal móvil: cada día τ_t = cuantil (1−pi) de los márgenes de los N
        días hábiles previos (7 tickers juntos); al inicio del año se usan los
        del último año de entrenamiento. Nunca usa información del día t ni
        posterior."""
    filas = []
    for anio, g in preds.groupby("anio"):
        tr = g[g.parte == "train_ultimo_anio"].sort_values("fecha")
        ev = g[g.parte == "eval"].sort_values(["fecha", "ticker"])
        P_ev = ev[["p_sell", "p_hold", "p_buy"]].values
        s_tr = margen_hold(tr[["p_sell", "p_hold", "p_buy"]].values)
        tau_anual = np.quantile(s_tr, 1 - pi)
        filas.append({"regla": f"proporción fija por año (π={pi})", "anio": anio,
                      **metricas(ev.y.values, decidir_umbral(P_ev, tau_anual), ev.r.values, ev.fecha.values)})
        hist = pd.DataFrame({"fecha": np.concatenate([tr.fecha.values, ev.fecha.values]),
                             "s": np.concatenate([s_tr, margen_hold(P_ev)])})
        por_dia = hist.groupby("fecha").s.apply(np.array)
        inicio = ev.fecha.min()
        for n in (63, 252):
            tau_dia = {}
            for i, f in enumerate(por_dia.index):
                if f < inicio:
                    continue
                previos = np.concatenate(por_dia.iloc[max(0, i - n):i].values)
                tau_dia[f] = np.quantile(previos, 1 - pi)
            tau = ev.fecha.map(tau_dia).values
            filas.append({"regla": f"proporción móvil causal (π={pi}, N={n})", "anio": anio,
                          **metricas(ev.y.values, decidir_umbral(P_ev, tau), ev.r.values, ev.fecha.values)})
    return pd.DataFrame(filas)


def main():
    resumen = {}
    todas = []
    preds_prod = d_prod = None
    for etiqueta, inter in [("61+15 interactions (producción)", True), ("61 base", False)]:
        d = panel(inter)
        preds = pd.concat([predecir_anio(d, a) for a in ANIOS_DESARROLLO + ANIOS_CONFIRMACION])
        todas.append(evaluar(preds, etiqueta))
        if inter:
            preds_prod, d_prod = preds, d
    tab = pd.concat(todas, ignore_index=True)

    # Alternativas que no son un factor constante (pipeline de producción)
    alt = [reglas_adaptativas(preds_prod)]
    for w in PESOS_HOLD:
        pw = pd.concat([predecir_anio(d_prod, a, peso_hold=w) for a in ANIOS_DESARROLLO + ANIOS_CONFIRMACION])
        e = evaluar(pw, "x")
        alt.append(e[e.k == 1.0].drop(columns=["features", "k"]).assign(regla=f"reentrenar con peso HOLD x{w}"))
    base_k1 = tab[tab.features.str.contains("producción") & (tab.k == 1.0)].drop(columns=["features", "k"])
    alt.append(base_k1.assign(regla="argmax normal (k=1)"))
    alt = pd.concat(alt, ignore_index=True)
    alt.to_csv(OUT / "7_reglas_alternativas_detalle.csv", index=False)
    alt["grupo"] = np.where(alt.anio.isin(ANIOS_DESARROLLO), "media 2019-2024", "2025")
    res_alt = alt.groupby(["regla", "grupo"])[["f1_macro", "kappa", "pred_hold_pct", "sharpe",
                                               "sharpe_portafolio"]].mean().unstack("grupo")
    print("=" * 78)
    print("Alternativas al factor constante (pipeline de producción, origen rodante)")
    print("=" * 78)
    print(res_alt.round(4).to_string())
    res_alt.to_csv(OUT / "7_reglas_alternativas_resumen.csv")
    # Selección del peso de HOLD SOLO con los años de desarrollo
    pesos = alt[alt.regla.str.startswith("reentrenar") | (alt.regla == "argmax normal (k=1)")]
    pesos = pesos[pesos.anio.isin(ANIOS_DESARROLLO)].groupby("regla")[["f1_macro", "kappa", "sharpe"]].mean()
    print()
    print("Peso de HOLD al reentrenar, media 2019-2024:")
    print(pesos.round(4).to_string())
    print(f"Elegido por F1 medio de desarrollo: {pesos.f1_macro.idxmax()}")
    resumen["peso_hold_elegido_por_f1_dev"] = pesos.f1_macro.idxmax()
    resumen["reglas_alternativas"] = {f"{a}|{b}": {r: round(float(v), 4) for r, v in res_alt[(a, b)].items()}
                                      for a, b in res_alt.columns}

    # 2026: modelo de producción real (entrenado 2018-2025), fuera de muestra
    if PROD_2026.exists():
        p26 = pd.read_csv(PROD_2026, parse_dates=["fecha"]).dropna(subset=["real"])
        mapa = {"sell": 0, "hold": 1, "buy": 2}
        p26 = pd.DataFrame({"anio": 2026, "fecha": p26.fecha.values, "ticker": p26.ticker.values,
                            "y": p26.real.map(mapa).values, "r": p26.r.values,
                            "p_sell": p26.p_sell.values, "p_hold": p26.p_hold.values,
                            "p_buy": p26.p_buy.values})
        tab = pd.concat([tab, evaluar(p26, "61+15 interactions (producción)")], ignore_index=True)
    tab.to_csv(OUT / "7_ajuste_hold_rolling_detalle.csv", index=False)

    for etiqueta in tab.features.unique():
        t = tab[tab.features == etiqueta]
        dev = t[t.anio.isin(ANIOS_DESARROLLO)].groupby("k")[["f1_macro", "kappa", "sharpe", "pred_hold_pct"]].mean()
        k_best = float(dev["f1_macro"].idxmax())
        # regla de "un error estándar": el k más cercano a 1 cuyo F1 medio no
        # está más de 1 EE por debajo del mejor (prefiere el ajuste más pequeño)
        se = t[(t.anio.isin(ANIOS_DESARROLLO)) & (t.k == k_best)].f1_macro.std(ddof=1) / np.sqrt(len(ANIOS_DESARROLLO))
        k_1se = float(max(k for k in dev.index if dev.loc[k, "f1_macro"] >= dev.loc[k_best, "f1_macro"] - se))
        print("=" * 78)
        print(etiqueta)
        print("=" * 78)
        print("Media 2019-2024 por k (selección):")
        print(dev.loc[[1.0, 0.95, 0.92, 0.90, 0.88, 0.85, 0.80]].round(4).to_string())
        print(f"k que maximiza F1 medio 2019-2024: {k_best}   |   k con regla 1-EE: {k_1se}")

        comp = []
        for anio in sorted(t.anio.unique()):
            a = t[(t.anio == anio) & (t.k == 1.0)].iloc[0]
            b = t[(t.anio == anio) & (t.k == k_best)].iloc[0]
            comp.append({"anio": anio, "rol": "desarrollo" if anio in ANIOS_DESARROLLO else "confirmación",
                         "f1_k1": a.f1_macro, f"f1_k{k_best}": b.f1_macro,
                         "kappa_k1": a.kappa, f"kappa_k{k_best}": b.kappa,
                         "hold_real": a.real_hold_pct, "hold_k1": a.pred_hold_pct, f"hold_k{k_best}": b.pred_hold_pct,
                         "sharpe_k1": a.sharpe, f"sharpe_k{k_best}": b.sharpe,
                         "sharpe_port_k1": a.sharpe_portafolio, f"sharpe_port_k{k_best}": b.sharpe_portafolio})
        comp = pd.DataFrame(comp)
        print(comp.round(3).to_string(index=False))
        dif_f1 = comp[f"f1_k{k_best}"] - comp["f1_k1"]
        dif_sh = comp[f"sharpe_k{k_best}"] - comp["sharpe_k1"]
        dev_mask = comp.rol == "desarrollo"
        print(f"Años en que k={k_best} mejora F1: {(dif_f1 > 0).sum()}/{len(comp)}  "
              f"(desarrollo {(dif_f1[dev_mask] > 0).sum()}/{dev_mask.sum()}, "
              f"confirmación {(dif_f1[~dev_mask] > 0).sum()}/{(~dev_mask).sum()})  | "
              f"Wilcoxon F1 p={wilcoxon(dif_f1).pvalue:.3f}  | ΔSharpe medio={dif_sh.mean():+.3f}")
        comp.to_csv(OUT / f"7_ajuste_hold_{'inter' if 'inter' in etiqueta else 'base'}.csv", index=False)
        resumen[etiqueta] = {"k_max_f1_dev": k_best, "k_1se_dev": k_1se,
                             "dev_medias_por_k": dev.round(4).reset_index().to_dict("records"),
                             "comparacion_por_anio": comp.round(4).to_dict("records"),
                             "anios_mejora_f1": int((dif_f1 > 0).sum()), "n_anios": len(comp),
                             "wilcoxon_p_f1": float(wilcoxon(dif_f1).pvalue),
                             "delta_sharpe_medio": float(dif_sh.mean())}

    # ¿Aportan las interactions fuera del año en que se eligieron? (k = 1)
    k1 = tab[tab.k == 1.0].pivot_table(index="anio", columns="features", values=["f1_macro", "sharpe"])
    print("\nInteractions vs base, k=1 (mismo pipeline, origen rodante):")
    print(k1.round(4).to_string())
    k1.to_csv(OUT / "7_interactions_vs_base_rolling.csv")
    resumen["interactions_vs_base_k1"] = {str(c): {int(a): round(float(v), 4) for a, v in k1[c].dropna().items()}
                                          for c in k1.columns}

    with open(OUT / "7_ajuste_hold.json", "w", encoding="utf-8") as f:
        json.dump(resumen, f, indent=2, ensure_ascii=False, default=float)
    print(f"\n✓ Resultados en {OUT}/7_*")


if __name__ == "__main__":
    main()
