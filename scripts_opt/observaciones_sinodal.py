"""
================================================================================
OBSERVACIONES DE LA SINODAL (2026-10-26) — evidencia para responderlas
================================================================================
Subcomandos (correr desde la raíz del repo):

    python scripts_opt/observaciones_sinodal.py metricas
        ¿Se mide igual a los cinco modelos? Panel completo de métricas (F1,
        exactitud, exactitud balanceada, kappa, AUC, log-loss, Sharpe con y sin
        costos) de los cinco modelos en A, B y C, y comprobación de que los cinco
        se califican en las MISMAS filas. Sin entrenar nada (~10 s).

    python scripts_opt/observaciones_sinodal.py seleccion
        ¿Se eligió el modelo con la prueba? Con las predicciones guardadas de la
        prueba año por año (configuraciones de la Etapa 3, que no vieron ningún
        pliegue, y de la Etapa 4): validación contra prueba por modelo, rango
        medio, años ganados y qué pasaría si cada año se eligiera el modelo con
        mejor validación. Sin entrenar nada (~1 min por los bootstraps).

    python scripts_opt/observaciones_sinodal.py multicolinealidad [--sin-redes]
        ¿Por qué no se quita la multicolinealidad? VIF y correlaciones de las 61
        variables y comparación, con el protocolo final, de cada modelo con las
        61 variables contra el mismo modelo con un filtro VIF ≤ 10 (calculado solo
        con el entrenamiento de cada pliegue). GPU para las redes (~25 min).

    python scripts_opt/observaciones_sinodal.py dataset2026
        Reconstruye el dataset con datos hasta hoy en
        tesis_ml_stocks/01_raw_datasets_2026/ (no toca el dataset de la tesis).
        Requiere red.

    python scripts_opt/observaciones_sinodal.py ciega2026
        Prueba ciega: los cinco modelos con las configuraciones congeladas de la
        Etapa 4, entrenamiento 2020–2024, validación 2025 y prueba en 2026 (datos
        que ninguna decisión usó). Mismo esquema que la prueba año por año.

    python scripts_opt/observaciones_sinodal.py exportar_web
        Junta todo en Frontend/src/app/data/comparacion_modelos.json para la
        pestaña «Modelos» de la plataforma.

Salida: RESULTADOS_OPTIMIZADOS/observaciones_sinodal/
================================================================================
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import sys
import json
import argparse
import datetime as dt
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (f1_score, accuracy_score, balanced_accuracy_score,
                             cohen_kappa_score, roc_auc_score, log_loss)

sys.path.insert(0, str(Path(__file__).parent))
import common                                       # noqa: E402
import common_v5                                    # noqa: E402
import run_v5                                       # noqa: E402
from common import TICKERS                          # noqa: E402
from common_v5 import SPLITS_V5, SEEDS_5, correr, metricas_con_costos  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
OUT = RAIZ / "RESULTADOS_OPTIMIZADOS" / "observaciones_sinodal"
OUT.mkdir(parents=True, exist_ok=True)
PREDS_V5 = RAIZ / "RESULTADOS_OPTIMIZADOS" / "v5" / "preds"
PREDS_OUT = OUT / "preds"
PREDS_OUT.mkdir(parents=True, exist_ok=True)
DIR_2026 = RAIZ / "tesis_ml_stocks" / "01_raw_datasets_2026"
JSON_WEB = RAIZ / "Frontend" / "src" / "app" / "data" / "comparacion_modelos.json"

MODELOS = ["LR", "XGBoost", "LSTM", "CNN-LSTM", "CNN"]
NOMBRE = {"LR": "Regresión Logística", "XGBoost": "XGBoost", "LSTM": "LSTM",
          "CNN-LSTM": "CNN-LSTM", "CNN": "CNN 1D"}
ARCH = {"LSTM": "lstm", "CNN": "cnn", "CNN-LSTM": "cnn_lstm"}
WF_ANIOS = [2020, 2021, 2022, 2023, 2024, 2025]


# ════════════════════════════════════════════════════════════════════════════
# Utilidades
# ════════════════════════════════════════════════════════════════════════════

def panel_metricas(y, probs, r, tk) -> dict:
    """Las mismas métricas para cualquier modelo: solo dependen de y, probs y r."""
    pred = probs.argmax(1)
    p = np.clip(probs, 1e-9, 1)
    p = p / p.sum(1, keepdims=True)
    out = {
        "n": int(len(y)),
        "f1_macro": f1_score(y, pred, average="macro", zero_division=0),
        "exactitud": accuracy_score(y, pred),
        "exactitud_balanceada": balanced_accuracy_score(y, pred),
        "kappa": cohen_kappa_score(y, pred),
        "auc_macro": roc_auc_score(y, p, multi_class="ovr", average="macro"),
        "log_loss": log_loss(y, p, labels=[0, 1, 2]),
        "f1_vender": f1_score(y, pred, labels=[0], average="macro", zero_division=0),
        "f1_mantener": f1_score(y, pred, labels=[1], average="macro", zero_division=0),
        "f1_comprar": f1_score(y, pred, labels=[2], average="macro", zero_division=0),
        "pct_mantener": float(np.mean(pred == 1) * 100),
    }
    for bp in (0.0, 10.0):
        c = metricas_con_costos(pred, r, tk, bp)
        out[f"sharpe_{int(bp)}bp"] = c[f"sharpe_{int(bp)}bp"]
    out["rotacion"] = c["turnover_medio"]
    return {k: (round(float(v), 4) if isinstance(v, (float, np.floating)) else v)
            for k, v in out.items()}


def cargar_pred(path: Path):
    d = np.load(path, allow_pickle=True)
    return d["y"], d["probs"], d["r"], d["tk"], d["fechas"]


def bootstrap_dif(y, pa, pb, n_boot=2000):
    """Diferencia de F1-macro (a − b) con bootstrap por bloques de 20 días."""
    b = run_v5._bootstrap_diferencia(y, pa.argmax(1), pb.argmax(1), n_boot=n_boot)
    dif = (f1_score(y, pa.argmax(1), average="macro", zero_division=0)
           - f1_score(y, pb.argmax(1), average="macro", zero_division=0))
    lo, hi = np.percentile(b, [2.5, 97.5])
    return round(float(dif), 4), round(float(lo), 4), round(float(hi), 4), bool(lo > 0 or hi < 0)


def configs_etapa4():
    dl = json.load(open(run_v5.GANADORES_DL, encoding="utf-8"))
    clas = json.load(open(run_v5.GANADORES_CLASICOS, encoding="utf-8"))
    redes = {m: run_v5._cargar_cfg(run_v5._ganador_dl(dl, ARCH[m], "B")["cfg"]) for m in ARCH}
    clasicos = {m: run_v5._ganador_clasico(clas, m, "B")["params"] for m in ("LR", "XGBoost")}
    return clasicos, redes


def correr_modelo(nombre, exp, clasicos, redes):
    if nombre in clasicos:
        return run_v5._correr_clasico(nombre, clasicos[nombre], exp, "final",
                                      semillas=SEEDS_5, refit=True, devolver_probs=True)
    return correr(redes[nombre], exp, "final", "global", semillas=SEEDS_5, devolver_probs=True)


# ════════════════════════════════════════════════════════════════════════════
# 1. Métricas iguales para los cinco
# ════════════════════════════════════════════════════════════════════════════

def cmd_metricas(args):
    filas, mismas = [], []
    for exp in ("A", "B", "C"):
        ref = None
        for m in MODELOS:
            y, probs, r, tk, f = cargar_pred(PREDS_V5 / f"{m}_{exp}_global_GLOBAL_v1.npz")
            filas.append({"exp": exp, "modelo": m, **panel_metricas(y, probs, r, tk)})
            clave = (y.tobytes(), tk.tobytes(), f.tobytes())
            if ref is None:
                ref = clave
            mismas.append({"exp": exp, "modelo": m, "mismas_filas_que_LR": clave == ref})
    df = pd.DataFrame(filas)
    df.to_csv(OUT / "1_metricas_panel.csv", index=False)
    pd.DataFrame(mismas).to_csv(OUT / "1_mismas_filas.csv", index=False)
    print(df.to_string(index=False))
    print("\n¿Mismas filas en los cinco?", all(x["mismas_filas_que_LR"] for x in mismas))
    print("→", OUT / "1_metricas_panel.csv")


# ════════════════════════════════════════════════════════════════════════════
# 2. Cómo se elige el modelo
# ════════════════════════════════════════════════════════════════════════════

def _tabla_wf(etiqueta: str) -> pd.DataFrame:
    """Una fila por (modelo, año) con métricas de validación y de prueba."""
    filas = []
    for anio in WF_ANIOS:
        for m in MODELOS:
            f = PREDS_V5 / f"WF{etiqueta}_{m}_WF{anio}_global_GLOBAL_v1.npz"
            if not f.exists():
                continue
            d = np.load(f, allow_pickle=True)
            fila = {"config": etiqueta, "anio": anio, "modelo": m,
                    **panel_metricas(d["y"], d["probs"], d["r"], d["tk"])}
            if "probs_val" in d.files:
                fila["val_f1"] = round(float(f1_score(d["y_val"], d["probs_val"].argmax(1),
                                                      average="macro", zero_division=0)), 4)
            filas.append(fila)
    return pd.DataFrame(filas)


def cmd_seleccion(args):
    todo, resumenes, metas, difs = [], [], [], []
    for etiqueta, desc in (("v4", "Etapa 3 (configuraciones fijas: no vieron ningún pliegue)"),
                           ("v5", "Etapa 4 (configuraciones elegidas con 2024)")):
        t = _tabla_wf(etiqueta)
        todo.append(t)
        piv = t.pivot_table(index="modelo", columns="anio", values="f1_macro")
        rank = piv.rank(ascending=False)
        gana = (rank == 1).sum(axis=1)
        res = pd.DataFrame({
            "config": etiqueta, "descripcion": desc,
            "f1_prueba_media": piv.mean(axis=1).round(4),
            "f1_prueba_desv": piv.std(axis=1).round(4),
            "f1_validacion_media": t.pivot_table(index="modelo", values="val_f1").iloc[:, 0].round(4)
            if "val_f1" in t else np.nan,
            "rango_medio": rank.mean(axis=1).round(2),
            "anios_ganados": gana,
            "anios": piv.notna().sum(axis=1),
            "sharpe_medio": t.pivot_table(index="modelo", values="sharpe_0bp").iloc[:, 0].round(3),
            "sharpe_10bp_medio": t.pivot_table(index="modelo", values="sharpe_10bp").iloc[:, 0].round(3),
        }).reset_index()
        resumenes.append(res)

        # ¿Qué pasa si cada año se elige el modelo con mejor validación?
        if "val_f1" in t:
            for anio, g in t.groupby("anio"):
                elegido = g.loc[g["val_f1"].idxmax()]
                mejor = g.loc[g["f1_macro"].idxmax()]
                metas.append({"config": etiqueta, "anio": anio,
                              "elegido_por_validacion": elegido["modelo"],
                              "f1_prueba_del_elegido": elegido["f1_macro"],
                              "mejor_en_prueba": mejor["modelo"],
                              "f1_prueba_del_mejor": mejor["f1_macro"],
                              "corr_val_prueba": round(float(g[["val_f1", "f1_macro"]]
                                                             .corr(method="spearman").iloc[0, 1]), 3)})

        # LR contra cada modelo, juntando los seis años de prueba
        juntos = {}
        for m in MODELOS:
            ys, ps = [], []
            for anio in WF_ANIOS:
                f = PREDS_V5 / f"WF{etiqueta}_{m}_WF{anio}_global_GLOBAL_v1.npz"
                if f.exists():
                    d = np.load(f, allow_pickle=True)
                    ys.append(d["y"]); ps.append(d["probs"])
            if len(ys) == len(WF_ANIOS):
                juntos[m] = (np.concatenate(ys), np.concatenate(ps))
        for m in MODELOS[1:]:
            if m in juntos and "LR" in juntos:
                y = juntos["LR"][0]
                if np.array_equal(y, juntos[m][0]):
                    dif, lo, hi, sig = bootstrap_dif(y, juntos["LR"][1], juntos[m][1])
                    difs.append({"config": etiqueta, "comparacion": f"LR − {m}",
                                 "dif_f1": dif, "ic_lo": lo, "ic_hi": hi, "significativa": sig})

    pd.concat(todo).to_csv(OUT / "2_anio_por_anio_detalle.csv", index=False)
    r = pd.concat(resumenes)
    r.to_csv(OUT / "2_seleccion_resumen.csv", index=False)
    pd.DataFrame(metas).to_csv(OUT / "2_eleccion_por_validacion.csv", index=False)
    pd.DataFrame(difs).to_csv(OUT / "2_lr_contra_cada_uno_6anios.csv", index=False)
    print(r.to_string(index=False))
    print(pd.DataFrame(metas).to_string(index=False))
    print(pd.DataFrame(difs).to_string(index=False))


# ════════════════════════════════════════════════════════════════════════════
# 3. Multicolinealidad
# ════════════════════════════════════════════════════════════════════════════

def vif_todas(X: np.ndarray) -> np.ndarray:
    """VIF_j = (R⁻¹)_jj con R la matriz de correlación."""
    R = np.corrcoef(X, rowvar=False)
    return np.diag(np.linalg.pinv(R))


def filtro_vif(X: pd.DataFrame, umbral=10.0) -> list:
    """Quita la variable de mayor VIF hasta que todas queden ≤ umbral."""
    cols = list(X.columns)
    while True:
        v = vif_todas(X[cols].values)
        j = int(np.argmax(v))
        if v[j] <= umbral or len(cols) <= 2:
            return cols
        cols.pop(j)


def _train_crudo(exp: str) -> pd.DataFrame:
    rg = SPLITS_V5[exp]["final"]["train"]
    partes = []
    for tk in TICKERS:
        df = common_v5._panel(tk)
        partes.append(df[(df.index >= rg[0]) & (df.index <= rg[1])])
    df = pd.concat(partes)
    return df[[c for c in df.columns if c not in ("target", "r_forward")]]


_PANEL_ORIGINAL = common_v5._panel
_COLUMNAS = {"keep": None}


def _panel_filtrado(ticker):
    df = _PANEL_ORIGINAL(ticker)
    if _COLUMNAS["keep"] is None:
        return df
    return df[_COLUMNAS["keep"] + ["target", "r_forward"]]


def cmd_multicolinealidad(args):
    # 3a. Diagnóstico en el entrenamiento del Experimento B
    Xb = _train_crudo("B")
    R = Xb.corr()
    pares = [(a, b, R.loc[a, b]) for i, a in enumerate(R.columns)
             for b in R.columns[i + 1:] if abs(R.loc[a, b]) >= 0.8]
    pares.sort(key=lambda x: -abs(x[2]))
    v = pd.Series(vif_todas(Xb.values), index=Xb.columns).sort_values(ascending=False)
    keep_b = filtro_vif(Xb)
    diag = {"n_variables": int(Xb.shape[1]),
            "pares_r_mayor_0.9": int(sum(abs(p[2]) >= 0.9 for p in pares)),
            "pares_r_mayor_0.8": len(pares),
            "vif_mayor_10": int((v > 10).sum()),
            "vif_mayor_100": int((v > 100).sum()),
            "vif_max": round(float(v.iloc[0]), 1),
            "variables_tras_filtro_vif10_B": len(keep_b),
            "top_pares": [(a, b, round(float(c), 3)) for a, b, c in pares[:15]],
            "top_vif": [(k, round(float(x), 1)) for k, x in v.head(15).items()],
            "quedan_B": keep_b}
    json.dump(diag, open(OUT / "3_multicolinealidad_diagnostico.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2,
              default=lambda o: o.item() if hasattr(o, "item") else str(o))
    print(json.dumps({k: diag[k] for k in list(diag)[:7]}, ensure_ascii=False, indent=2,
                     default=lambda o: o.item() if hasattr(o, "item") else str(o)))

    # 3b. Con el protocolo final: todas las variables contra filtro VIF ≤ 10
    clasicos, redes = configs_etapa4()
    common_v5._panel = _panel_filtrado          # preparar*() lo buscan por nombre
    filas = []
    exps = ["A", "B", "C"] + [f"WF{a}" for a in WF_ANIOS]
    for exp in exps:
        _COLUMNAS["keep"] = None
        keep = filtro_vif(_train_crudo(exp))
        modelos = list(clasicos) + ([] if (args.sin_redes or exp.startswith("WF")) else list(redes))
        for m in modelos:
            for brazo, cols in (("todas_61", None), ("filtro_vif10", keep)):
                if m in redes and brazo == "todas_61":
                    continue    # ya existe en v5/resultados_finales.csv (mismo código)
                _COLUMNAS["keep"] = cols
                res = correr_modelo(m, exp, clasicos, redes)
                pm = panel_metricas(res["y_eval"], res["probs_eval"], res["r_eval"], res["tk_eval"])
                filas.append({"exp": exp, "modelo": m, "brazo": brazo,
                              "n_variables": len(cols) if cols else 61, **pm})
                print(f"  {exp:<7} {m:<9} {brazo:<13} F1={pm['f1_macro']:.4f}  "
                      f"Sharpe={pm['sharpe_0bp']:+.3f}", flush=True)
                pd.DataFrame(filas).to_csv(OUT / "3_multicolinealidad_resultados.csv", index=False)
    _COLUMNAS["keep"] = None
    common_v5._panel = _PANEL_ORIGINAL

    # Redes con las 61: del registro de la Etapa 4
    rf = pd.read_csv(RAIZ / "RESULTADOS_OPTIMIZADOS" / "v5" / "resultados_finales.csv")
    rf = rf[(rf.tipo == "global") & rf.modelo.isin(list(redes))]
    for _, x in rf.iterrows():
        filas.append({"exp": x.exp, "modelo": x.modelo, "brazo": "todas_61", "n_variables": 61,
                      "f1_macro": x.test_f1_ens, "sharpe_0bp": x.sharpe, "sharpe_10bp": x.sharpe_10bp})
    df = pd.DataFrame(filas)
    df.to_csv(OUT / "3_multicolinealidad_resultados.csv", index=False)
    piv = df.pivot_table(index=["modelo", "exp"], columns="brazo", values="f1_macro")
    piv["delta_todas_menos_filtro"] = piv["todas_61"] - piv["filtro_vif10"]
    print(piv.round(4).to_string())
    piv.round(4).to_csv(OUT / "3_multicolinealidad_resumen.csv")


# ════════════════════════════════════════════════════════════════════════════
# 4. Prueba ciega 2026
# ════════════════════════════════════════════════════════════════════════════

def cmd_dataset2026(args):
    ruta = RAIZ / "scripts_v1" / "01_build_raw_dataset.py"
    spec = importlib.util.spec_from_file_location("build_raw", ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.DOWNLOAD_END = dt.date.today().isoformat()      # yfinance: fin exclusivo
    mod.OUTPUT_DIR = DIR_2026
    DIR_2026.mkdir(parents=True, exist_ok=True)
    mod.pipeline()


def cmd_ciega2026(args):
    if not DIR_2026.exists():
        raise SystemExit("Falta el dataset: corre primero `dataset2026`.")
    common.RAW_DIR = DIR_2026                   # cargar_raw() lo lee en cada llamada
    common_v5._panel.cache_clear()
    SPLITS_V5["WF2026"] = {"final": {"train": ("2020-01-01", "2024-12-31"),
                                     "val": ("2025-01-01", "2025-12-31"),
                                     "eval": ("2026-01-01", "2026-12-31")}}
    SPLITS_V5["WF2026"]["dev"] = SPLITS_V5["WF2026"]["final"]
    clasicos, redes = configs_etapa4()
    probs, filas = {}, []
    for m in MODELOS:
        res = correr_modelo(m, "WF2026", clasicos, redes)
        np.savez_compressed(PREDS_OUT / f"ciega2026_{m}.npz", probs=res["probs_eval"],
                            y=res["y_eval"], r=res["r_eval"], tk=res["tk_eval"],
                            fechas=np.array([str(x) for x in res["f_eval"]]),
                            probs_val=res["probs_val"], y_val=res["y_val"])
        pm = panel_metricas(res["y_eval"], res["probs_eval"], res["r_eval"], res["tk_eval"])
        val = f1_score(res["y_val"], res["probs_val"].argmax(1), average="macro", zero_division=0)
        filas.append({"modelo": m, "val_f1_2025": round(float(val), 4), **pm})
        probs[m] = res
        print(f"  {m:<9} val2025={val:.4f}  F1 2026={pm['f1_macro']:.4f}  "
              f"Sharpe={pm['sharpe_0bp']:+.3f}  (n={pm['n']})", flush=True)
    df = pd.DataFrame(filas)
    rango = sorted({str(x)[:10] for x in probs["LR"]["f_eval"]})
    df["desde"], df["hasta"] = rango[0], rango[-1]
    df.to_csv(OUT / "4_ciega2026.csv", index=False)
    difs = []
    for m in MODELOS[1:]:
        y = probs["LR"]["y_eval"]
        if np.array_equal(y, probs[m]["y_eval"]):
            dif, lo, hi, sig = bootstrap_dif(y, probs["LR"]["probs_eval"], probs[m]["probs_eval"])
            difs.append({"comparacion": f"LR − {m}", "dif_f1": dif, "ic_lo": lo, "ic_hi": hi,
                         "significativa": sig})
    pd.DataFrame(difs).to_csv(OUT / "4_ciega2026_diferencias.csv", index=False)
    print(df.to_string(index=False))
    print(pd.DataFrame(difs).to_string(index=False))


# ════════════════════════════════════════════════════════════════════════════
# 5. Datos para la pestaña «Modelos» de la plataforma
# ════════════════════════════════════════════════════════════════════════════

def _leer(nombre):
    f = OUT / nombre
    return pd.read_csv(f) if f.exists() else None


def cmd_exportar_web(args):
    j = {"generado": dt.date.today().isoformat(), "modelos": MODELOS, "nombres": NOMBRE,
         "modelo_elegido": "LR"}
    panel = _leer("1_metricas_panel.csv")
    if panel is not None:
        j["experimentos"] = {exp: panel[panel.exp == exp].drop(columns="exp").to_dict("records")
                             for exp in ("A", "B", "C")}
    ic = []
    for exp in ("A", "B", "C"):
        f = RAIZ / "RESULTADOS_OPTIMIZADOS" / "v5" / f"v6_ic_{exp}_v1.csv"
        if f.exists():
            for _, x in pd.read_csv(f).iterrows():
                ic.append({"exp": exp, "modelo": x.modelo, "f1": round(x.f1, 4),
                           "lo": round(x.ic_lo, 4), "hi": round(x.ic_hi, 4)})
    j["intervalos"] = ic
    det = _leer("2_anio_por_anio_detalle.csv")
    if det is not None:
        j["anio_por_anio"] = det[["config", "anio", "modelo", "f1_macro", "sharpe_0bp",
                                  "sharpe_10bp"] + (["val_f1"] if "val_f1" in det else [])
                                 ].to_dict("records")
    for clave, archivo in (("seleccion", "2_seleccion_resumen.csv"),
                           ("eleccion_por_validacion", "2_eleccion_por_validacion.csv"),
                           ("lr_contra_cada_uno_6anios", "2_lr_contra_cada_uno_6anios.csv"),
                           ("ciega2026", "4_ciega2026.csv"),
                           ("ciega2026_diferencias", "4_ciega2026_diferencias.csv")):
        t = _leer(archivo)
        if t is not None:
            j[clave] = t.to_dict("records")
    mc = _leer("3_multicolinealidad_resultados.csv")
    if mc is not None:
        j["multicolinealidad"] = mc[["exp", "modelo", "brazo", "n_variables", "f1_macro"]].to_dict("records")
    f = OUT / "3_multicolinealidad_diagnostico.json"
    if f.exists():
        d = json.load(open(f, encoding="utf-8"))
        j["multicolinealidad_diagnostico"] = {k: d[k] for k in d if k != "quedan_B"}
    g = RAIZ / "RESULTADOS_OPTIMIZADOS" / "analisis_hold" / "4a_global_vs_porticker_por_modelo.csv"
    if g.exists():
        j["global_vs_por_accion"] = pd.read_csv(g)[["modelo", "celdas", "f1_global_medio",
                                                    "f1_por_ticker_medio", "celdas_gana_global_f1",
                                                    "p_signo_f1"]].to_dict("records")
    JSON_WEB.parent.mkdir(parents=True, exist_ok=True)
    json.dump(j, open(JSON_WEB, "w", encoding="utf-8"), ensure_ascii=False, indent=1,
              default=lambda o: o.item() if hasattr(o, "item") else str(o))
    print("→", JSON_WEB, f"({JSON_WEB.stat().st_size / 1024:.1f} KB)")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("metricas")
    sub.add_parser("seleccion")
    pm = sub.add_parser("multicolinealidad")
    pm.add_argument("--sin-redes", action="store_true")
    sub.add_parser("dataset2026")
    sub.add_parser("ciega2026")
    sub.add_parser("exportar_web")
    a = ap.parse_args()
    {"metricas": cmd_metricas, "seleccion": cmd_seleccion,
     "multicolinealidad": cmd_multicolinealidad, "dataset2026": cmd_dataset2026,
     "ciega2026": cmd_ciega2026, "exportar_web": cmd_exportar_web}[a.cmd](a)


if __name__ == "__main__":
    main()
