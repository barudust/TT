"""
================================================================================
RUN V5 — ejecutor del plan maestro
================================================================================
Subcomandos (correr desde la raíz del repo):

    python scripts_opt/run_v5.py replicar     # G0: ¿el pipeline nuevo reproduce v4?
    python scripts_opt/run_v5.py ablacion     # V1: torneo de decisiones de protocolo
    python scripts_opt/run_v5.py optuna --arch lstm --trials 100
    python scripts_opt/run_v5.py clasicos     # V3: Optuna para LR y XGBoost
    python scripts_opt/run_v5.py final        # congela ganadores → 1 evaluación en test
    python scripts_opt/run_v5.py stats        # V6: bootstrap e IC de las diferencias

Todo lo que no sea `final` corre en modo dev (evalúa en 2024). `final` es el
único que toca 2025, una sola vez por configuración.
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("PYTHONUNBUFFERED", "1")
import sys
import json
import time
import argparse
import functools
import warnings
from dataclasses import asdict, replace
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

from common import TICKERS, metricas_full, metricas_global_por_ticker
from common_v5 import (Cfg, CFG_V4, SPLITS_V5, EXPERIMENTOS, DEVICE, OUT_V5, DATASET,
                       SEEDS_DEFAULT, SEEDS_5, preparar, preparar_tabular,
                       correr, entrenar_una_semilla, registrar, resumen,
                       fijar_semilla, crear_modelo, metricas_con_costos, WF_ANIOS)


def _n_params(cfg: Cfg, input_size: int = 61) -> int:
    return sum(p.numel() for p in crear_modelo(cfg, input_size).parameters())

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.utils.class_weight import compute_sample_weight
import xgboost as xgb

ARCHS = ("lstm", "cnn", "cnn_lstm")
NOMBRE_V4 = {"lstm": "LSTM", "cnn": "CNN", "cnn_lstm": "CNN-LSTM"}
EXP_PRINCIPAL = "B"

BASE_JSON = OUT_V5 / "base_v5.json"
GANADORES_DL = OUT_V5 / "ganadores_dl.json"
GANADORES_CLASICOS = (OUT_V5 / "ganadores_clasicos.json" if DATASET == "v1"
                      else OUT_V5 / f"ganadores_clasicos_{DATASET}.json")
PREDS_DIR = OUT_V5 / "preds"
PREDS_DIR.mkdir(parents=True, exist_ok=True)
(OUT_V5 / "estudios").mkdir(parents=True, exist_ok=True)


def _guardar_json(obj, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=str)


def _ganador_dl(dl: dict, arch: str, exp: str) -> dict:
    """Config ganadora para (arch, exp); si no se buscó en ese exp, usa la de B."""
    for clave in (f"{arch}|{exp}|{DATASET}", f"{arch}|B|{DATASET}",
                  f"{arch}|{exp}", f"{arch}|B", arch):
        if clave in dl:
            return dl[clave]
    raise KeyError(f"no hay configuración ganadora para {arch} (exp {exp})")


def _ganador_clasico(clas: dict, nombre: str, exp: str) -> dict:
    """Params ganadores para (modelo, exp); si no se buscó en ese exp, usa los de B."""
    for clave in (f"{nombre}|{exp}", f"{nombre}|B", nombre):
        if clave in clas:
            return clas[clave]
    raise KeyError(f"no hay parámetros ganadores para {nombre} (exp {exp})")


def _cargar_cfg(d: dict) -> Cfg:
    d = dict(d)
    if "filtros" in d and d["filtros"] is not None:
        d["filtros"] = tuple(d["filtros"])
    return Cfg(**d)


# ════════════════════════════════════════════════════════════════════════════
# G0 — REPLICACIÓN DE v4
# ════════════════════════════════════════════════════════════════════════════

def cmd_replicar(args):
    print("=" * 78)
    print("  G0 — ¿el pipeline v5 reproduce los números de v4?")
    print("  (modo final, alineado=False, criterio=val_loss, 3 semillas — como v4)")
    print("=" * 78)

    v4 = pd.read_csv("RESULTADOS_OPTIMIZADOS/v4/resultados_v4.csv")
    v4g = v4[(v4.tipo == "global")]
    filas = []
    for arch in ARCHS:
        for exp in ("A", "B", "C"):
            for lb in (20, 60):
                cfg = replace(CFG_V4[arch], lookback=lb)
                res = correr(cfg, exp, "final", "global", semillas=SEEDS_DEFAULT)
                registrar(res, via="V0-replicacion", modelo_nombre=NOMBRE_V4[arch],
                          notas="replicacion de v4")
                ref = v4g[(v4g.modelo == NOMBRE_V4[arch]) & (v4g.experimento == exp)
                          & (v4g.lookback == lb)]["test_f1_macro"]
                ref = float(ref.iloc[0]) if len(ref) else np.nan
                d = res["eval_f1_ens"] - ref
                filas.append(dict(modelo=NOMBRE_V4[arch], exp=exp, lookback=lb,
                                  v4=ref, v5=round(res["eval_f1_ens"], 4),
                                  delta=round(d, 4), ok=abs(d) <= 0.01))
                print(f"  {NOMBRE_V4[arch]:<9} exp{exp} lb{lb:<3} "
                      f"v4={ref:.4f}  v5={res['eval_f1_ens']:.4f}  "
                      f"delta={d:+.4f}  {'OK' if abs(d) <= 0.01 else 'REVISAR'}")

    df = pd.DataFrame(filas)
    df.to_csv(OUT_V5 / "g0_replicacion.csv", index=False)
    n_ok = int(df.ok.sum())
    print(f"\n  {n_ok}/{len(df)} dentro de ±0.01   "
          f"|delta| medio = {df.delta.abs().mean():.4f}   máx = {df.delta.abs().max():.4f}")
    print(f"  G0 {'PASA' if n_ok >= len(df) - 2 else 'NO PASA'} → {OUT_V5/'g0_replicacion.csv'}")


# ════════════════════════════════════════════════════════════════════════════
# V1 — TORNEO DE DECISIONES DE PROTOCOLO
# ════════════════════════════════════════════════════════════════════════════

def _variantes(decision, arch, base: Cfg):
    """Devuelve [(etiqueta, cfg), ...] para una decisión dada."""
    if decision == "D1_criterio":
        return [(c, replace(base, criterio=c))
                for c in ("val_loss", "val_f1", "val_f1_ma3")]
    if decision == "D2_alineado":
        return [("no", replace(base, alineado=False)), ("si", replace(base, alineado=True))]
    if decision == "D3_escalador":
        return [("minmax", replace(base, escalador="minmax")),
                ("standard", replace(base, escalador="standard")),
                ("robust_clip5", replace(base, escalador="robust", clip=5.0))]
    if decision == "D4_pesos":
        return [(c, replace(base, class_weight=c)) for c in ("balanced", "none", "sqrt")]
    if decision == "D5_pooling":
        if arch == "cnn":
            return [(c, replace(base, pool_cnn=c)) for c in ("gap_gmp", "gap", "flatten")]
        return [(c, replace(base, pooling=c)) for c in ("last", "meanmax", "attn")]
    if decision == "D6_refit":
        return [("no", replace(base, refit_trainval=False)),
                ("si", replace(base, refit_trainval=True))]
    raise ValueError(decision)


DECISIONES = ["D1_criterio", "D2_alineado", "D3_escalador",
              "D4_pesos", "D5_pooling", "D6_refit"]


def cmd_ablacion(args):
    """
    Torneo secuencial con bloqueo. La decisión se toma POR ARQUITECTURA (D5 ni
    siquiera comparte etiquetas entre ellas) con la regla R5: se adopta la
    variante solo si mejora >= 0.005 el F1 medio entre semillas Y esa mejora
    supera la desviación entre semillas. Si empata, se queda la de v4.
    D2 (ventanas alineadas) y D6 (refit con train+val) corrigen asimetrías reales
    frente a LR/XGBoost, así que se adoptan salvo que empeoren claramente.
    """
    print("=" * 78)
    print("  V1 — torneo de decisiones de protocolo")
    print("  modo dev: entrena 2018-2022, elige época con 2023, DECIDE con 2024")
    print("  Exp B GLOBAL, 5 semillas por variante")
    print("=" * 78)

    semillas = SEEDS_5
    base = {a: replace(CFG_V4[a]) for a in ARCHS}
    filas, adoptado = [], {}

    for dec in DECISIONES:
        print(f"\n  ── {dec} " + "─" * max(4, 58 - len(dec)))
        adoptado[dec] = {}
        for arch in ARCHS:
            variantes = _variantes(dec, arch, base[arch])
            etiqueta_base = variantes[0][0]
            puntajes = {}
            for etiqueta, cfg in variantes:
                res = correr(cfg, EXP_PRINCIPAL, "dev", "global", semillas=semillas)
                registrar(res, via=f"V1-{dec}", modelo_nombre=NOMBRE_V4[arch],
                          notas=f"variante={etiqueta}")
                resumen(res, f"{NOMBRE_V4[arch]:<9} {etiqueta}")
                puntajes[etiqueta] = (res["eval_f1_mean"], res["eval_f1_std"])
                filas.append(dict(decision=dec, arch=arch, variante=etiqueta,
                                  eval_f1_mean=round(res["eval_f1_mean"], 4),
                                  eval_f1_std=round(res["eval_f1_std"], 4),
                                  eval_f1_ens=round(res["eval_f1_ens"], 4),
                                  val_f1_ens=round(res["val_f1_ens"], 4),
                                  n_eval=res["n_eval"], segundos=res["segundos"]))

            m0, s0 = puntajes[etiqueta_base]
            elegida, motivo = etiqueta_base, "sin efecto (se queda la de v4)"

            if dec in ("D2_alineado", "D6_refit"):
                m1, _ = puntajes["si"]
                if m1 - m0 > -0.005:
                    elegida = "si"
                    motivo = f"adoptada por diseño (corrige asimetría), delta={m1-m0:+.4f}"
                else:
                    motivo = f"NO adoptada: empeora {m1-m0:+.4f}"
            else:
                cands = [(m - m0, e, m, s) for e, (m, s) in puntajes.items()
                         if e != etiqueta_base and (m - m0) >= 0.005 and (m - m0) > max(s, s0)]
                if cands:
                    d, e, m, s = max(cands)
                    elegida, motivo = e, f"adoptada, delta={d:+.4f} (std={s:.4f})"

            base[arch] = dict(variantes)[elegida]
            adoptado[dec][arch] = dict(elegida=elegida, motivo=motivo)
            print(f"    → {NOMBRE_V4[arch]:<9} {elegida}  [{motivo}]")

    pd.DataFrame(filas).to_csv(OUT_V5 / "v1_ablaciones.csv", index=False)
    _guardar_json({a: asdict(base[a]) for a in ARCHS}, BASE_JSON)
    _guardar_json(adoptado, OUT_V5 / "v1_decisiones.json")
    print(f"\n  Base v5 congelada → {BASE_JSON}")
    for a in ARCHS:
        print(f"    {a}: {base[a].id_corto()}")


# ════════════════════════════════════════════════════════════════════════════
# V2 — OPTUNA PARA LOS MODELOS PROFUNDOS
# ════════════════════════════════════════════════════════════════════════════

def _muestrear(trial, arch, base: Cfg) -> Cfg:
    comun = dict(
        # el criterio de época lo decide también Optuna: la ablación mostró que
        # vale +0.058 en LSTM y nada en CNN/CNN-LSTM, así que conviene por arquitectura
        criterio=trial.suggest_categorical("criterio", ["val_loss", "val_f1", "val_f1_ma3"]),
        lookback=trial.suggest_categorical("lookback", [10, 20, 40, 60]),
        dropout=trial.suggest_float("dropout", 0.0, 0.6),
        lr=trial.suggest_float("lr", 1e-5, 3e-3, log=True),
        weight_decay=trial.suggest_float("weight_decay", 1e-6, 1e-1, log=True),
        batch=trial.suggest_categorical("batch", [64, 128, 256, 512]),
        class_weight=trial.suggest_categorical("class_weight", ["balanced", "none", "sqrt"]),
        scheduler=trial.suggest_categorical("scheduler", ["plateau", "cosine", "none"]),
        grad_clip=trial.suggest_categorical("grad_clip", [0.5, 1.0, 5.0]),
        escalador=trial.suggest_categorical("escalador", ["minmax", "standard", "robust"]),
    )
    perdida = trial.suggest_categorical("loss", ["ce", "focal"])
    comun["loss"] = perdida
    if perdida == "ce":
        comun["label_smooth"] = trial.suggest_float("label_smooth", 0.0, 0.2)
    else:
        comun["focal_gamma"] = trial.suggest_float("focal_gamma", 0.5, 3.0)

    if arch == "cnn":
        n_bloques = trial.suggest_int("n_bloques", 1, 4)
        f0 = trial.suggest_int("filtros_base", 16, 256, log=True)
        comun.update(
            filtros=tuple(min(f0 * (2 ** i), 512) for i in range(n_bloques)),
            kernel=trial.suggest_categorical("kernel", [3, 5, 7]),
            dilatacion=trial.suggest_categorical("dilatacion", [1, 2]),
            batchnorm=trial.suggest_categorical("batchnorm", [True, False]),
            fc_dim=trial.suggest_int("fc_dim", 32, 256, log=True),
            pool_cnn=trial.suggest_categorical("pool_cnn", ["gap_gmp", "gap", "flatten"]),
        )
    else:
        comun.update(
            hidden=trial.suggest_int("hidden", 16, 256, log=True),
            layers=trial.suggest_int("layers", 1, 3),
            bidir=trial.suggest_categorical("bidir", [True, False]),
            pooling=trial.suggest_categorical("pooling", ["last", "meanmax", "attn"]),
        )
        if arch == "cnn_lstm":
            f0 = trial.suggest_int("filtros_base", 16, 128, log=True)
            comun["filtros"] = (f0, f0 * 2)
            comun["kernel"] = trial.suggest_categorical("kernel", [3, 5, 7])

    return replace(base, epochs=100, patience=20, **comun)


def cmd_optuna(args):
    import optuna
    optuna.logging.set_verbosity(optuna.logging.WARNING)

    base_todas = json.load(open(BASE_JSON, encoding="utf-8")) if BASE_JSON.exists() else None
    archs = [args.arch] if args.arch else list(ARCHS)
    exp_busqueda = getattr(args, "exp", None) or EXP_PRINCIPAL

    for arch in archs:
        base = _cargar_cfg(base_todas[arch]) if base_todas else replace(CFG_V4[arch])
        print("=" * 78)
        print(f"  V2 — Optuna {arch.upper()} exp{exp_busqueda}  ({args.trials} trials × 2 semillas)")
        print(f"  base: {base.id_corto()}   modo dev (época en 2023, objetivo = F1 2024)")
        print("=" * 78)

        semillas = (42, 1)

        def objetivo(trial):
            cfg = _muestrear(trial, arch, base)
            try:
                datos = preparar(exp_busqueda, "dev", cfg, "global")
                f1s = []
                for i, s in enumerate(semillas):
                    _, pe, _, _, _ = entrenar_una_semilla(
                        datos, cfg, s, trial=trial if i == 0 else None)
                    f1s.append(f1_score(datos["y_eval"], pe.argmax(1),
                                        average="macro", zero_division=0))
                return float(np.mean(f1s))
            except optuna.TrialPruned:
                raise
            except RuntimeError as e:      # OOM u otra config imposible
                print(f"    trial {trial.number} descartado: {type(e).__name__}")
                raise optuna.TrialPruned()

        estudio = optuna.create_study(
            study_name=f"v5_{arch}_exp{exp_busqueda}_{DATASET}_global",
            storage=f"sqlite:///{(OUT_V5/'optuna_v5.db').as_posix()}",
            load_if_exists=True, direction="maximize",
            sampler=optuna.samplers.TPESampler(seed=42, n_startup_trials=25,
                                               multivariate=True, group=True),
            pruner=optuna.pruners.MedianPruner(n_startup_trials=15, n_warmup_steps=10),
        )
        t0 = time.time()
        estudio.optimize(objetivo, n_trials=args.trials, show_progress_bar=False)
        dur = time.time() - t0

        df = estudio.trials_dataframe()
        df.to_csv(OUT_V5 / "estudios" / f"{arch}_{exp_busqueda}_{DATASET}.csv", index=False)
        completos = [t for t in estudio.trials if t.value is not None]
        print(f"\n  {len(completos)} trials completos / {len(estudio.trials)} "
              f"({dur/60:.1f} min, {dur/max(len(estudio.trials),1):.1f}s por trial)")
        print(f"  mejor F1(2024) = {estudio.best_value:.4f}")
        print(f"  mejores parámetros: {estudio.best_params}")

        try:
            imp = optuna.importance.get_param_importances(estudio)
            _guardar_json(imp, OUT_V5 / "estudios" / f"{arch}_{exp_busqueda}_{DATASET}_importancias.json")
            print("  importancia de hiperparámetros: " +
                  ", ".join(f"{k}={v:.3f}" for k, v in list(imp.items())[:6]))
        except Exception as e:
            print(f"  (no se pudo calcular importancia: {e})")

        # ── finalistas: top-5 con 5 semillas, se elige por 2024 ──
        print("\n  ── finalistas (5 semillas) ──")
        top = sorted(completos, key=lambda t: t.value, reverse=True)[:5]
        mejores = []
        for t in top:
            cfg = _muestrear(optuna.trial.FixedTrial(t.params), arch, base)
            res = correr(cfg, exp_busqueda, "dev", "global", semillas=SEEDS_5)
            registrar(res, via="V2-finalista", modelo_nombre=NOMBRE_V4[arch],
                      notas=f"trial={t.number}")
            resumen(res, f"trial {t.number}")
            mejores.append((res["eval_f1_mean"], res["eval_f1_std"], t.number, cfg, res))

        mejores.sort(key=lambda x: -x[0])
        mejor = mejores[0]
        # desempate: dentro de 1 desviación entre semillas, gana el modelo más chico
        for cand in mejores[1:]:
            if mejor[0] - cand[0] < mejor[1] and _n_params(cand[3]) < _n_params(mejor[3]):
                mejor = cand
        print(f"\n  → ganador {arch}: trial {mejor[2]}  "
              f"F1(decision)={mejor[0]:.4f}±{mejor[1]:.4f}")

        ganadores = json.load(open(GANADORES_DL, encoding="utf-8")) \
            if GANADORES_DL.exists() else {}
        ganadores[f"{arch}|{exp_busqueda}|{DATASET}"] = dict(cfg=asdict(mejor[3]), trial=mejor[2],
                               f1_2024_mean=round(mejor[0], 4),
                               f1_2024_std=round(mejor[1], 4),
                               n_trials=len(estudio.trials))
        _guardar_json(ganadores, GANADORES_DL)
        print(f"  guardado → {GANADORES_DL}")


# ════════════════════════════════════════════════════════════════════════════
# V3 — OPTUNA PARA LR Y XGBOOST (simetría de búsqueda)
# ════════════════════════════════════════════════════════════════════════════

def _fit_lr(p, datos, semilla, refit=False):
    cw = p.get("class_weight", "balanced")
    m = LogisticRegression(
        penalty=p["penalty"], C=p["C"],
        l1_ratio=p.get("l1_ratio") if p["penalty"] == "elasticnet" else None,
        solver="saga" if p["penalty"] in ("elasticnet", "l1") else "lbfgs",
        max_iter=3000, class_weight=None if cw == "none" else cw,
        random_state=semilla, n_jobs=-1, tol=1e-3)
    X, y = datos["X_train"], datos["y_train"]
    if refit:
        X = np.vstack([X, datos["X_val"]])
        y = np.concatenate([y, datos["y_val"]])
    m.fit(X, y)
    return m


def _fit_xgb(p, datos, semilla, refit=False):
    m = xgb.XGBClassifier(
        n_estimators=p["n_estimators"], max_depth=p["max_depth"],
        learning_rate=p["learning_rate"], subsample=p["subsample"],
        colsample_bytree=p["colsample_bytree"], min_child_weight=p["min_child_weight"],
        gamma=p["gamma"], reg_alpha=p["reg_alpha"], reg_lambda=p["reg_lambda"],
        objective="multi:softprob", num_class=3, eval_metric="mlogloss",
        tree_method="hist", device="cuda", random_state=semilla, n_jobs=-1, verbosity=0)
    X, y = datos["X_train"], datos["y_train"]
    if refit:
        X = np.vstack([X, datos["X_val"]])
        y = np.concatenate([y, datos["y_val"]])
    sw = compute_sample_weight("balanced", y=y)
    m.fit(X, y, sample_weight=sw, verbose=False)
    return m


def _correr_clasico(modelo, p, exp, modo, tipo="global", ticker=None,
                    semillas=SEEDS_5, refit=True, devolver_probs=False):
    t0 = time.time()
    esc = p.get("escalador", "standard")
    datos = preparar_tabular(exp, modo, tipo, ticker, escalador=esc)
    fit = _fit_lr if modelo == "LR" else _fit_xgb
    pv_l, pe_l, f1v, f1e = [], [], [], []
    for s in semillas:
        m = fit(p, datos, s, refit=False)
        pv = m.predict_proba(datos["X_val"])
        m2 = fit(p, datos, s, refit=True) if refit else m
        pe = m2.predict_proba(datos["X_eval"])
        pv_l.append(pv); pe_l.append(pe)
        f1v.append(f1_score(datos["y_val"], pv.argmax(1), average="macro", zero_division=0))
        f1e.append(f1_score(datos["y_eval"], pe.argmax(1), average="macro", zero_division=0))
    probs_val = np.mean(pv_l, axis=0)
    probs_eval = np.mean(pe_l, axis=0)
    met_val = metricas_full(datos["y_val"], probs_val.argmax(1), split_name="val")
    met_eval = metricas_full(datos["y_eval"], probs_eval.argmax(1),
                             r_forward=datos["r_eval"], split_name="eval")
    res = {"cfg": p, "exp": exp, "modo": modo, "tipo": tipo,
           "ticker": ticker or "GLOBAL",
           "n_train": len(datos["y_train"]), "n_val": len(datos["y_val"]),
           "n_eval": len(datos["y_eval"]),
           "met_val": met_val, "met_eval": met_eval,
           "val_f1_ens": met_val["f1_macro"], "eval_f1_ens": met_eval["f1_macro"],
           "val_f1_mean": float(np.mean(f1v)), "val_f1_std": float(np.std(f1v)),
           "eval_f1_mean": float(np.mean(f1e)), "eval_f1_std": float(np.std(f1e)),
           "epocas": [], "semillas": list(semillas),
           "segundos": round(time.time() - t0, 1)}
    if devolver_probs:
        res.update(probs_eval=probs_eval, y_eval=datos["y_eval"], r_eval=datos["r_eval"],
                   tk_eval=datos["tk_eval"], f_eval=datos["f_eval"],
                   probs_val=probs_val, y_val=datos["y_val"])
    return res


def cmd_clasicos(args):
    import optuna
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    exp_busqueda = getattr(args, "exp", None) or EXP_PRINCIPAL
    print("=" * 78)
    print(f"  V3 — Optuna para LR y XGBoost, exp{exp_busqueda} ({args.trials} trials cada uno)")
    print("  Mismo protocolo que los profundos: modo dev, objetivo = F1 del año de decisión")
    print("=" * 78)

    ganadores = (json.load(open(GANADORES_CLASICOS, encoding="utf-8"))
                 if GANADORES_CLASICOS.exists() else {})

    def obj_lr(trial):
        pen = trial.suggest_categorical("penalty", ["l1", "l2", "elasticnet"])
        p = dict(penalty=pen,
                 C=trial.suggest_float("C", 1e-4, 1e3, log=True),
                 class_weight=trial.suggest_categorical("class_weight", ["balanced", "none"]),
                 escalador=trial.suggest_categorical("escalador", ["standard", "robust"]))
        if pen == "elasticnet":
            p["l1_ratio"] = trial.suggest_float("l1_ratio", 0.0, 1.0)
        r = _correr_clasico("LR", p, exp_busqueda, "dev", semillas=(42,), refit=False)
        return r["eval_f1_mean"]

    def obj_xgb(trial):
        p = dict(n_estimators=trial.suggest_int("n_estimators", 150, 800),
                 max_depth=trial.suggest_int("max_depth", 2, 10),
                 learning_rate=trial.suggest_float("learning_rate", 0.005, 0.3, log=True),
                 subsample=trial.suggest_float("subsample", 0.5, 1.0),
                 colsample_bytree=trial.suggest_float("colsample_bytree", 0.3, 1.0),
                 min_child_weight=trial.suggest_int("min_child_weight", 1, 15),
                 gamma=trial.suggest_float("gamma", 0.0, 3.0),
                 reg_alpha=trial.suggest_float("reg_alpha", 0.0, 5.0),
                 reg_lambda=trial.suggest_float("reg_lambda", 0.1, 8.0),
                 escalador="standard")
        r = _correr_clasico("XGBoost", p, exp_busqueda, "dev", semillas=(42,), refit=False)
        return r["eval_f1_mean"]

    for nombre, objetivo in (("LR", obj_lr), ("XGBoost", obj_xgb)):
        estudio = optuna.create_study(
            study_name=f"v5_{nombre}_exp{exp_busqueda}_{DATASET}_global",
            storage=f"sqlite:///{(OUT_V5/'optuna_v5.db').as_posix()}",
            load_if_exists=True, direction="maximize",
            sampler=optuna.samplers.TPESampler(seed=42, n_startup_trials=25,
                                               multivariate=True, group=True))
        t0 = time.time()
        estudio.optimize(objetivo, n_trials=args.trials, show_progress_bar=False)
        estudio.trials_dataframe().to_csv(OUT_V5 / "estudios" / f"{nombre}_{exp_busqueda}_{DATASET}.csv", index=False)
        print(f"\n  {nombre}: {len(estudio.trials)} trials en {(time.time()-t0)/60:.1f} min")
        print(f"    mejor F1(2024)={estudio.best_value:.4f}  params={estudio.best_params}")

        p = dict(estudio.best_params)
        p.setdefault("escalador", "standard")
        res = _correr_clasico(nombre, p, exp_busqueda, "dev", semillas=SEEDS_5)
        registrar(res, via="V3-finalista", modelo_nombre=nombre, notas="mejor Optuna")
        resumen(res, f"{nombre} ganador")
        ganadores[f"{nombre}|{exp_busqueda}"] = dict(
            params=p, f1_dev_mean=round(res["eval_f1_mean"], 4),
            f1_dev_std=round(res["eval_f1_std"], 4), n_trials=len(estudio.trials))

    _guardar_json(ganadores, GANADORES_CLASICOS)
    print(f"\n  guardado → {GANADORES_CLASICOS}")


# ════════════════════════════════════════════════════════════════════════════
# FINAL — una sola evaluación en test (2025) por configuración congelada
# ════════════════════════════════════════════════════════════════════════════

def _guardar_preds(nombre, exp, tipo, ticker, res):
    f = PREDS_DIR / f"{nombre}_{exp}_{tipo}_{ticker}_{DATASET}.npz"
    extra = {}
    if "probs_val" in res:
        extra = {"probs_val": res["probs_val"], "y_val": res["y_val"]}
    np.savez_compressed(
        f, probs=res["probs_eval"], y=res["y_eval"], r=res["r_eval"],
        tk=res["tk_eval"], fechas=np.array([str(x) for x in res["f_eval"]]), **extra)


def cmd_final(args):
    print("=" * 78)
    print("  FINAL — configuraciones congeladas → 1 evaluación en TEST (2025)")
    print("=" * 78)

    dl = json.load(open(GANADORES_DL, encoding="utf-8"))
    clas = json.load(open(GANADORES_CLASICOS, encoding="utf-8"))
    filas = []

    for exp in (["B"] if args.solo_b else ["A", "B", "C"]):
        print(f"\n  ══ Experimento {exp} ══")
        for nombre in ("LR", "XGBoost"):
            info = _ganador_clasico(clas, nombre, exp)
            for tipo, tks in (("global", [None]), ("por_ticker", TICKERS)):
                if tipo == "por_ticker" and args.solo_global:
                    continue
                for tk in tks:
                    res = _correr_clasico(nombre, info["params"], exp, "final",
                                          tipo=tipo, ticker=tk, semillas=SEEDS_5,
                                          refit=True, devolver_probs=True)
                    registrar(res, via="FINAL", modelo_nombre=nombre,
                              notas="config congelada de V3")
                    _guardar_preds(nombre, exp, tipo, tk or "GLOBAL", res)
                    resumen(res, f"{nombre:<9} {tipo} {tk or 'GLOBAL'}")
                    filas.append(_fila_tabla(nombre, exp, tipo, tk or "GLOBAL", res))

        for arch in ARCHS:
            cfg = _cargar_cfg(_ganador_dl(dl, arch, exp)["cfg"])
            for tipo, tks in (("global", [None]), ("por_ticker", TICKERS)):
                if tipo == "por_ticker" and args.solo_global:
                    continue
                for tk in tks:
                    res = correr(cfg, exp, "final", tipo=tipo, ticker=tk,
                                 semillas=SEEDS_5, devolver_probs=True)
                    registrar(res, via="FINAL", modelo_nombre=NOMBRE_V4[arch],
                              notas="config congelada de V2")
                    _guardar_preds(NOMBRE_V4[arch], exp, tipo, tk or "GLOBAL", res)
                    resumen(res, f"{NOMBRE_V4[arch]:<9} {tipo} {tk or 'GLOBAL'}")
                    filas.append(_fila_tabla(NOMBRE_V4[arch], exp, tipo, tk or "GLOBAL", res))

    df = pd.DataFrame(filas)
    df.to_csv(OUT_V5 / "resultados_finales.csv", index=False)
    print(f"\n  → {OUT_V5/'resultados_finales.csv'}")


def _fila_tabla(nombre, exp, tipo, ticker, res):
    m = res["met_eval"]
    costos = {}
    if "probs_eval" in res:
        pred = res["probs_eval"].argmax(1)
        for bp in (5.0, 10.0):
            costos.update(metricas_con_costos(pred, res["r_eval"], res["tk_eval"], bp))
    return dict(modelo=nombre, dataset=DATASET, exp=exp, tipo=tipo, ticker=ticker,
                n_eval=res["n_eval"], **costos,
                test_f1_ens=round(res["eval_f1_ens"], 4),
                test_f1_mean=round(res["eval_f1_mean"], 4),
                test_f1_std=round(res["eval_f1_std"], 4),
                val_f1_ens=round(res["val_f1_ens"], 4),
                test_f1_buy=m["f1_buy"], test_f1_hold=m["f1_hold"], test_f1_sell=m["f1_sell"],
                sharpe=m.get("sharpe_test"), win_rate=m.get("win_rate_test"),
                profit_factor=m.get("profit_factor_test"), max_dd=m.get("max_drawdown_test"),
                signal_buy=m["signal_distribution"]["BUY"]["pct"],
                signal_hold=m["signal_distribution"]["HOLD"]["pct"],
                signal_sell=m["signal_distribution"]["SELL"]["pct"])


# ════════════════════════════════════════════════════════════════════════════
# WALK-FORWARD — ¿el ranking entre modelos se sostiene año a año?
# ════════════════════════════════════════════════════════════════════════════

def cmd_wf(args):
    """
    Seis pliegues con ventana de entrenamiento FIJA de 5 años que rueda:
    test 2020…2025, val = año anterior, train = los 5 años previos a la val.

    Responde la pregunta que los experimentos A/B/C no pueden responder, porque
    los tres comparten test=2025: ¿el orden entre modelos es una propiedad de los
    modelos o del año 2025?

    Aviso metodológico que hay que escribir en el paper: los hiperparámetros se
    fijaron con el año 2024 como conjunto de decisión, así que para los pliegues
    2020-2023 son información posterior al test. Es una forma débil de fuga (no
    afecta a los pesos, solo a la elección de arquitectura) y por eso este análisis
    se reporta como comprobación de ESTABILIDAD DEL ORDEN, no como estimación
    limpia de desempeño año a año. Con `--config-v4` se corre con las
    configuraciones originales del paper, que no vieron ningún año, y ahí la
    comparación sí es limpia.
    """
    filas = []
    if args.config_v4:
        dl_cfgs = {a: replace(CFG_V4[a], alineado=True) for a in ARCHS}
        clas = {"LR": dict(penalty="elasticnet", C=1.0, l1_ratio=0.5,
                           class_weight="balanced", escalador="standard"),
                "XGBoost": dict(n_estimators=400, max_depth=5, learning_rate=0.05,
                                subsample=0.8, colsample_bytree=0.8, min_child_weight=3,
                                gamma=0.1, reg_alpha=0.1, reg_lambda=1.0,
                                escalador="standard")}
        etiqueta = "v4"
    else:
        dl = json.load(open(GANADORES_DL, encoding="utf-8"))
        dl_cfgs = {a: _cargar_cfg(_ganador_dl(dl, a, "B")["cfg"]) for a in ARCHS}
        _c = json.load(open(GANADORES_CLASICOS, encoding="utf-8"))
        clas = {n: _ganador_clasico(_c, n, "B")["params"] for n in ("LR", "XGBoost")}
        etiqueta = "v5"

    print("=" * 78)
    print(f"  WALK-FORWARD ({etiqueta}) — 6 pliegues, ventana de train fija de 5 años")
    print("=" * 78)

    for anio in WF_ANIOS:
        exp = f"WF{anio}"
        print(f"\n  ══ test {anio}  (train {anio-6}-{anio-2}, val {anio-1}) ══")
        for nombre, p in clas.items():
            res = _correr_clasico(nombre, p, exp, "final", semillas=SEEDS_5,
                                  refit=True, devolver_probs=True)
            registrar(res, via=f"WF-{etiqueta}", modelo_nombre=nombre, notas=f"pliegue {anio}")
            _guardar_preds(f"WF{etiqueta}_{nombre}", exp, "global", "GLOBAL", res)
            resumen(res, f"{nombre:<9} {anio}")
            filas.append(_fila_tabla(nombre, exp, "global", "GLOBAL", res) | {"anio": anio})
        for arch, cfg in dl_cfgs.items():
            res = correr(cfg, exp, "final", "global", semillas=SEEDS_5, devolver_probs=True)
            registrar(res, via=f"WF-{etiqueta}", modelo_nombre=NOMBRE_V4[arch],
                      notas=f"pliegue {anio}")
            _guardar_preds(f"WF{etiqueta}_{NOMBRE_V4[arch]}", exp, "global", "GLOBAL", res)
            resumen(res, f"{NOMBRE_V4[arch]:<9} {anio}")
            filas.append(_fila_tabla(NOMBRE_V4[arch], exp, "global", "GLOBAL", res)
                         | {"anio": anio})

    df = pd.DataFrame(filas)
    salida = OUT_V5 / f"walkforward_{etiqueta}.csv"
    df.to_csv(salida, index=False)

    piv = df.pivot_table(index="modelo", columns="anio", values="test_f1_ens")
    piv["media"] = piv.mean(axis=1)
    piv["desv"] = df.pivot_table(index="modelo", columns="anio",
                                 values="test_f1_ens").std(axis=1)
    rank = df.pivot_table(index="modelo", columns="anio",
                          values="test_f1_ens").rank(ascending=False)
    piv["rank_medio"] = rank.mean(axis=1)
    print(f"\n  F1-macro por año de test ({etiqueta}):")
    print(piv.round(4).to_string())
    piv.round(4).to_csv(OUT_V5 / f"walkforward_{etiqueta}_resumen.csv")
    print(f"\n  → {salida}")


# ════════════════════════════════════════════════════════════════════════════
# V6 — ESTADÍSTICA
# ════════════════════════════════════════════════════════════════════════════

def _bootstrap_bloques(y, pred, n_boot=2000, bloque=20, semilla=42):
    rng = np.random.default_rng(semilla)
    n = len(y)
    n_bloques = int(np.ceil(n / bloque))
    inicios = np.arange(0, n - bloque + 1)
    out = np.empty(n_boot)
    for b in range(n_boot):
        idx = np.concatenate([np.arange(i, i + bloque)
                              for i in rng.choice(inicios, n_bloques)])[:n]
        out[b] = f1_score(y[idx], pred[idx], average="macro", zero_division=0)
    return out


def _bootstrap_diferencia(y, p1, p2, n_boot=2000, bloque=20, semilla=42):
    rng = np.random.default_rng(semilla)
    n = len(y)
    n_bloques = int(np.ceil(n / bloque))
    inicios = np.arange(0, n - bloque + 1)
    out = np.empty(n_boot)
    for b in range(n_boot):
        idx = np.concatenate([np.arange(i, i + bloque)
                              for i in rng.choice(inicios, n_bloques)])[:n]
        out[b] = (f1_score(y[idx], p1[idx], average="macro", zero_division=0)
                  - f1_score(y[idx], p2[idx], average="macro", zero_division=0))
    return out


def cmd_stats(args):
    from itertools import combinations
    print("=" * 78)
    print("  V6 — intervalos de confianza por bootstrap de bloques (test 2025)")
    print("=" * 78)

    exp = args.exp
    archivos = sorted(PREDS_DIR.glob(f"*_{exp}_global_GLOBAL_{args.dataset}.npz"))
    if not archivos:
        print(f"  No hay predicciones para exp={exp}. Corre primero `final`.")
        return

    datos = {}
    for f in archivos:
        nombre = f.stem.split(f"_{exp}_global_GLOBAL")[0]
        d = np.load(f, allow_pickle=True)
        datos[nombre] = (d["y"], d["probs"].argmax(1))

    n_ref = {k: len(v[0]) for k, v in datos.items()}
    if len(set(n_ref.values())) > 1:
        print(f"  ⚠ los modelos NO comparten filas: {n_ref}")
    else:
        print(f"  Todos los modelos evaluados sobre las mismas {list(n_ref.values())[0]} filas ✓")

    print("\n  F1-macro con IC 95 % (bootstrap de bloques de 20 días, 2000 remuestreos):")
    filas = []
    for nombre, (y, p) in sorted(datos.items()):
        b = _bootstrap_bloques(y, p, n_boot=args.n_boot)
        f1 = f1_score(y, p, average="macro", zero_division=0)
        lo, hi = np.percentile(b, [2.5, 97.5])
        print(f"    {nombre:<10} {f1:.4f}  IC95 [{lo:.4f}, {hi:.4f}]")
        filas.append(dict(modelo=nombre, f1=round(f1, 4), ic_lo=round(lo, 4),
                          ic_hi=round(hi, 4)))
    pd.DataFrame(filas).to_csv(OUT_V5 / f"v6_ic_{exp}_{args.dataset}.csv", index=False)

    print("\n  Diferencias entre pares (IC 95 % de la diferencia de F1):")
    pares = []
    for a, b in combinations(sorted(datos), 2):
        ya, pa = datos[a]
        yb, pb = datos[b]
        if len(ya) != len(yb):
            continue
        dif = _bootstrap_diferencia(ya, pa, pb, n_boot=args.n_boot)
        lo, hi = np.percentile(dif, [2.5, 97.5])
        d = (f1_score(ya, pa, average="macro", zero_division=0)
             - f1_score(yb, pb, average="macro", zero_division=0))
        sig = "SIGNIFICATIVA" if (lo > 0 or hi < 0) else "no significativa"
        print(f"    {a:<10} - {b:<10} {d:+.4f}  IC95 [{lo:+.4f}, {hi:+.4f}]  {sig}")
        pares.append(dict(modelo_a=a, modelo_b=b, dif=round(d, 4),
                          ic_lo=round(lo, 4), ic_hi=round(hi, 4),
                          significativa=(lo > 0 or hi < 0)))
    pd.DataFrame(pares).to_csv(OUT_V5 / f"v6_pares_{exp}_{args.dataset}.csv", index=False)
    print(f"\n  → {OUT_V5/f'v6_ic_{exp}.csv'} y {OUT_V5/f'v6_pares_{exp}.csv'}")


# ════════════════════════════════════════════════════════════════════════════

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("replicar")
    sub.add_parser("ablacion")

    po = sub.add_parser("optuna")
    po.add_argument("--arch", choices=ARCHS, default=None)
    po.add_argument("--trials", type=int, default=100)
    po.add_argument("--exp", choices=["A", "B", "C"], default=None)

    pc = sub.add_parser("clasicos")
    pc.add_argument("--trials", type=int, default=150)
    pc.add_argument("--exp", choices=["A", "B", "C"], default=None)

    pf = sub.add_parser("final")
    pf.add_argument("--solo-b", action="store_true")
    pf.add_argument("--solo-global", action="store_true")

    pw = sub.add_parser("wf")
    pw.add_argument("--config-v4", action="store_true",
                    help="usar las configuraciones originales del paper (sin fuga de hiperparámetros)")

    ps = sub.add_parser("stats")
    ps.add_argument("--exp", default="B")
    ps.add_argument("--n-boot", type=int, default=2000)
    ps.add_argument("--dataset", default="v1")

    args = p.parse_args()
    print(f"Dispositivo: {DEVICE} — "
          f"{__import__('torch').cuda.get_device_name(0) if DEVICE.type == 'cuda' else 'CPU'}")
    t0 = time.time()
    {"replicar": cmd_replicar, "ablacion": cmd_ablacion, "optuna": cmd_optuna,
     "clasicos": cmd_clasicos, "final": cmd_final, "stats": cmd_stats,
     "wf": cmd_wf}[args.cmd](args)
    print(f"\n[{args.cmd}] tiempo total: {(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    main()
