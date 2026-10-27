"""
================================================================================
REPORTE V5 — tablas y figuras listas para el paper
================================================================================
Lee lo que dejaron `run_v5.py final` y `run_v5.py stats` y produce:

  RESULTADOS_OPTIMIZADOS/v5/reportes/
    tabla1_f1_global.csv/.md        F1-macro GLOBAL por modelo × experimento (v4 vs v5)
    tabla2_economicas_expB.csv/.md  métricas económicas del experimento principal
    tabla3_f1_porticker.csv/.md     media sobre los 7 tickers
    tabla4_busqueda.md              presupuesto de búsqueda por modelo (simetría)
    tabla5_ic_bootstrap.md          F1 con IC 95 % y significancia de las diferencias
    fig_optuna_historia.png         historia de optimización por arquitectura
    fig_optuna_importancias.png     importancia de hiperparámetros por arquitectura

Correr desde la raíz del repo:  python scripts_opt/reporte_v5.py
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import sys
import json
import functools
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass
print = functools.partial(print, flush=True)
warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "serif"
DPI = 220

V5 = Path("RESULTADOS_OPTIMIZADOS/v5")
OUT = V5 / "reportes"
OUT.mkdir(parents=True, exist_ok=True)
V4_CSV = Path("RESULTADOS_OPTIMIZADOS/v4/resultados_v4.csv")
DATASET = os.environ.get("TT_DATASET", "v1")


def _buscar(patrones):
    """Primer archivo existente entre varios patrones (los nombres cambiaron al
    añadir el sufijo de dataset; esto acepta las dos convenciones)."""
    for pat in patrones:
        hits = sorted(V5.glob(pat)) if "*" in pat else ([V5 / pat] if (V5 / pat).exists() else [])
        if hits:
            return hits[0]
    return None

ORDEN = ["LR", "XGBoost", "LSTM", "CNN", "CNN-LSTM"]
EXPS = ["A", "B", "C"]
NOMBRE_ARCH = {"lstm": "LSTM", "cnn": "CNN", "cnn_lstm": "CNN-LSTM"}


def _md(df, titulo=""):
    """DataFrame → tabla markdown."""
    cols = list(df.columns)
    out = []
    if titulo:
        out.append(f"**{titulo}**\n")
    out.append("| " + " | ".join(str(c) for c in cols) + " |")
    out.append("|" + "|".join("---" for _ in cols) + "|")
    for _, r in df.iterrows():
        out.append("| " + " | ".join(
            ("" if pd.isna(v) else (f"{v:.4f}" if isinstance(v, float) else str(v)))
            for v in r) + " |")
    return "\n".join(out) + "\n"


def _v4_global():
    """Tabla de v4 tal como la construyó consolidar_v4.py (mejor lookback por TEST)."""
    if not V4_CSV.exists():
        return None
    d = pd.read_csv(V4_CSV)
    d = d[d.tipo == "global"]
    sec = d[d.lookback.notna()]
    nsec = d[d.lookback.isna()]
    idx = sec.groupby(["modelo", "experimento"])["test_f1_macro"].idxmax()
    d = pd.concat([nsec, sec.loc[idx]])
    return d.pivot_table(index="modelo", columns="experimento", values="test_f1_macro")


def _v4_porticker():
    if not V4_CSV.exists():
        return None
    d = pd.read_csv(V4_CSV)
    d = d[d.tipo == "por_ticker"]
    sec = d[d.lookback.notna()]
    nsec = d[d.lookback.isna()]
    idx = sec.groupby(["modelo", "experimento", "ticker"])["test_f1_macro"].idxmax()
    d = pd.concat([nsec, sec.loc[idx]])
    return d.pivot_table(index="modelo", columns="experimento", values="test_f1_macro",
                         aggfunc="mean")


def tabla1(fin):
    g = fin[fin.tipo == "global"]
    v5 = g.pivot_table(index="modelo", columns="exp", values="test_f1_ens")
    v5s = g.pivot_table(index="modelo", columns="exp", values="test_f1_std")
    v4 = _v4_global()

    filas = []
    for m in ORDEN:
        if m not in v5.index:
            continue
        f = {"modelo": m}
        for e in EXPS:
            f[f"v4_{e}"] = round(v4.loc[m, e], 4) if v4 is not None and m in v4.index else np.nan
            f[f"v5_{e}"] = round(v5.loc[m, e], 4) if e in v5.columns else np.nan
            f[f"v5_{e}_std"] = round(v5s.loc[m, e], 4) if e in v5s.columns else np.nan
        vals = [f[f"v5_{e}"] for e in EXPS if not pd.isna(f.get(f"v5_{e}"))]
        f["v5_prom"] = round(float(np.mean(vals)), 4) if vals else np.nan
        v4vals = [f[f"v4_{e}"] for e in EXPS if not pd.isna(f.get(f"v4_{e}"))]
        f["v4_prom"] = round(float(np.mean(v4vals)), 4) if v4vals else np.nan
        f["delta_prom"] = round(f["v5_prom"] - f["v4_prom"], 4) \
            if not pd.isna(f["v5_prom"]) and not pd.isna(f["v4_prom"]) else np.nan
        filas.append(f)
    df = pd.DataFrame(filas)
    df.to_csv(OUT / "tabla1_f1_global.csv", index=False)
    (OUT / "tabla1_f1_global.md").write_text(
        _md(df, "F1-macro GLOBAL en test 2025 — v4 (publicado) vs v5 (protocolo corregido "
                "+ búsqueda simétrica)"), encoding="utf-8")
    return df


def tabla2(fin, exp="B"):
    g = fin[(fin.tipo == "global") & (fin.exp == exp)]
    cols = ["modelo", "test_f1_ens", "test_f1_std", "win_rate", "profit_factor",
            "max_dd", "sharpe", "signal_buy", "signal_hold", "signal_sell"]
    df = g[cols].copy()
    df["orden"] = df.modelo.apply(lambda m: ORDEN.index(m) if m in ORDEN else 99)
    df = df.sort_values("orden").drop(columns="orden")
    df.to_csv(OUT / f"tabla2_economicas_exp{exp}.csv", index=False)
    (OUT / f"tabla2_economicas_exp{exp}.md").write_text(
        _md(df, f"Métricas económicas, Exp {exp} GLOBAL (test 2025)"), encoding="utf-8")
    return df


def tabla3(fin):
    pt = fin[fin.tipo == "por_ticker"]
    if pt.empty:
        return None
    v5 = pt.pivot_table(index="modelo", columns="exp", values="test_f1_ens", aggfunc="mean")
    v4 = _v4_porticker()
    filas = []
    for m in ORDEN:
        if m not in v5.index:
            continue
        f = {"modelo": m}
        for e in EXPS:
            f[f"v4_{e}"] = round(v4.loc[m, e], 4) if v4 is not None and m in v4.index else np.nan
            f[f"v5_{e}"] = round(v5.loc[m, e], 4) if e in v5.columns else np.nan
        filas.append(f)
    df = pd.DataFrame(filas)
    df.to_csv(OUT / "tabla3_f1_porticker.csv", index=False)
    (OUT / "tabla3_f1_porticker.md").write_text(
        _md(df, "F1-macro promedio sobre los 7 tickers (modelos por-ticker), test 2025"),
        encoding="utf-8")
    return df


def tabla4():
    """Presupuesto de búsqueda por modelo — la evidencia de simetría para el revisor."""
    filas = []
    for arch, nombre in NOMBRE_ARCH.items():
        f = _buscar([f"estudios/{arch}_*_{DATASET}.csv", f"estudios/{arch}.csv"])
        if f is None:
            continue
        d = pd.read_csv(f)
        completos = d[d.state == "COMPLETE"] if "state" in d.columns else d
        n_hp = len([c for c in d.columns if c.startswith("params_")])
        filas.append(dict(modelo=nombre, metodo="Optuna TPE + MedianPruner",
                          trials=len(d), completos=len(completos),
                          hiperparametros=n_hp,
                          mejor_f1_dev=round(completos["value"].max(), 4) if len(completos) else np.nan))
    for nombre in ("LR", "XGBoost"):
        f = _buscar([f"estudios/{nombre}_{DATASET}.csv", f"estudios/{nombre}.csv"])
        if f is None:
            continue
        d = pd.read_csv(f)
        completos = d[d.state == "COMPLETE"] if "state" in d.columns else d
        n_hp = len([c for c in d.columns if c.startswith("params_")])
        filas.append(dict(modelo=nombre, metodo="Optuna TPE",
                          trials=len(d), completos=len(completos),
                          hiperparametros=n_hp,
                          mejor_f1_dev=round(completos["value"].max(), 4) if len(completos) else np.nan))
    if not filas:
        return None
    df = pd.DataFrame(filas)
    df["orden"] = df.modelo.apply(lambda m: ORDEN.index(m) if m in ORDEN else 99)
    df = df.sort_values("orden").drop(columns="orden")
    df.to_csv(OUT / "tabla4_busqueda.csv", index=False)
    (OUT / "tabla4_busqueda.md").write_text(
        _md(df, "Presupuesto de búsqueda de hiperparámetros por modelo "
                "(todos con el mismo protocolo; F1 medido en 2024, no en test)"),
        encoding="utf-8")
    return df


def tabla5(exp="B"):
    ic = _buscar([f"v6_ic_{exp}_{DATASET}.csv", f"v6_ic_{exp}.csv"])
    pares = _buscar([f"v6_pares_{exp}_{DATASET}.csv", f"v6_pares_{exp}.csv"])
    if ic is None:
        return None
    d1 = pd.read_csv(ic)
    txt = _md(d1, f"F1-macro con IC 95 % (bootstrap de bloques), Exp {exp} GLOBAL, test 2025")
    if pares is not None:
        d2 = pd.read_csv(pares)
        txt += "\n" + _md(d2, "Diferencias entre pares de modelos")
    (OUT / f"tabla5_ic_bootstrap_{exp}.md").write_text(txt, encoding="utf-8")
    return d1


def figura_optuna():
    archs = [(a, n) for a, n in NOMBRE_ARCH.items()
             if _buscar([f"estudios/{a}_*_{DATASET}.csv", f"estudios/{a}.csv"])]
    if not archs:
        return
    fig, axes = plt.subplots(1, len(archs), figsize=(4.2 * len(archs), 3.4), sharey=True)
    if len(archs) == 1:
        axes = [axes]
    for ax, (arch, nombre) in zip(axes, archs):
        d = pd.read_csv(_buscar([f"estudios/{arch}_*_{DATASET}.csv", f"estudios/{arch}.csv"]))
        v = d["value"]
        ax.scatter(d["number"], v, s=9, alpha=0.45, color="#4C72B0", label="trial")
        ax.plot(d["number"], v.cummax(), color="#C44E52", lw=1.8, label="mejor hasta aquí")
        ax.set_title(nombre, fontsize=11)
        ax.set_xlabel("trial")
        ax.grid(alpha=0.25, lw=0.5)
    axes[0].set_ylabel("F1-macro (2024)")
    axes[0].legend(fontsize=8, loc="lower right")
    fig.suptitle("Búsqueda de hiperparámetros con Optuna (TPE) — modelos profundos",
                 fontsize=12)
    fig.tight_layout()
    fig.savefig(OUT / "fig_optuna_historia.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)

    imps = [(a, n) for a, n in NOMBRE_ARCH.items()
            if _buscar([f"estudios/{a}_*_{DATASET}_importancias.json",
                        f"estudios/{a}_importancias.json"])]
    if not imps:
        return
    fig, axes = plt.subplots(1, len(imps), figsize=(4.2 * len(imps), 3.6))
    if len(imps) == 1:
        axes = [axes]
    for ax, (arch, nombre) in zip(axes, imps):
        d = json.load(open(_buscar([f"estudios/{arch}_*_{DATASET}_importancias.json", f"estudios/{arch}_importancias.json"]), encoding="utf-8"))
        items = sorted(d.items(), key=lambda kv: kv[1])[-8:]
        ax.barh([k for k, _ in items], [v for _, v in items], color="#55A868")
        ax.set_title(nombre, fontsize=11)
        ax.tick_params(labelsize=8)
        ax.grid(axis="x", alpha=0.25, lw=0.5)
    fig.suptitle("Importancia de hiperparámetros (fANOVA sobre los trials de Optuna)",
                 fontsize=12)
    fig.tight_layout()
    fig.savefig(OUT / "fig_optuna_importancias.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def main():
    fin_path = _buscar([f"resultados_finales_{DATASET}.csv", "resultados_finales.csv"])
    if fin_path is None:
        print("Faltan los resultados finales. Corre primero: python scripts_opt/run_v5.py final")
        fin = None
    else:
        fin = pd.read_csv(fin_path)

    if fin is not None:
        print("\n" + (OUT / "tabla1_f1_global.md").name)
        t1 = tabla1(fin)
        print(t1.to_string(index=False))
        print()
        t2 = tabla2(fin)
        print(t2.to_string(index=False))
        t3 = tabla3(fin)
        if t3 is not None:
            print()
            print(t3.to_string(index=False))

    t4 = tabla4()
    if t4 is not None:
        print()
        print(t4.to_string(index=False))
    t5 = tabla5()
    if t5 is not None:
        print()
        print(t5.to_string(index=False))

    figura_optuna()
    print(f"\nTodo en {OUT}")


if __name__ == "__main__":
    main()
