"""
================================================================================
NIVELES DE SEGURIDAD — de la "confianza" del modelo a palabras
================================================================================
La plataforma mostraba la confianza como un porcentaje (p. ej. 38 %), que un
usuario sin contexto no puede interpretar: con tres opciones el azar es 33 % y
el modelo casi nunca pasa de 45 %. Este script traduce esa probabilidad a
niveles con palabras, con cortes elegidos por lo que de verdad pasó.

Cómo, sin mirar los años evaluados (origen rodante, igual que
`ajuste_hold_rolling.py`):
  - Para cada año Y de 2019 a 2025 se entrena el pipeline de producción
    actual (61 + 15 variables, RobustScaler global, LR L2 C=0.000165, pesos
    "balanced" con HOLD × 0.90) con [Y-6, Y-1] y se predice Y completo.
  - Confianza = probabilidad de la recomendación elegida.
  - Se mide el % de aciertos por tramo de confianza.

Resultado (2026-10-14): el acierto sube poco con la confianza (≈ 37 % en el
30 % de días menos seguros, ≈ 42 % en el 40 % más seguro; azar ≈ 34 %). Con
cuatro niveles los del medio no se distinguen, así que se usan TRES, cortados
en los percentiles 30 y 60 de la confianza:
    Nada segura · Poco segura · Medianamente segura
No existe un nivel "Segura": ningún tramo acierta ni la mitad de las veces.
Los cortes y aciertos se copian a `Frontend/src/app/format.ts`
(`NIVELES_SEGURIDAD`).

Uso (desde la raíz del repo, sin red):
    python scripts_opt/calibrar_niveles_confianza.py              # usa las predicciones guardadas
    python scripts_opt/calibrar_niveles_confianza.py --recalcular # reentrena 2019-2025 (~7 min)

Salida: RESULTADOS_OPTIMIZADOS/analisis_hold/9_niveles_seguridad.csv
        RESULTADOS_OPTIMIZADOS/analisis_hold/9_niveles_seguridad.json
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
from ajuste_hold_rolling import panel, predecir_anio, OUT
from entrenar_produccion import PESO_HOLD

ANIOS = list(range(2019, 2026))
PERCENTILES_CORTE = (0.30, 0.60)        # 3 niveles
PREDS = OUT / "9_predicciones_rolling_holdw090.csv.gz"


def main():
    if PREDS.exists() and "--recalcular" not in sys.argv:
        preds = pd.read_csv(PREDS)
        print(f"  usando predicciones guardadas: {PREDS}")
    else:
        d = panel(interactions=True)
        partes = []
        for anio in ANIOS:
            print(f"  entrenando para {anio} …")
            p = predecir_anio(d, anio, peso_hold=PESO_HOLD)
            partes.append(p[p.parte == "eval"])
        preds = pd.concat(partes, ignore_index=True)
        preds.to_csv(PREDS, index=False)

    P = preds[["p_sell", "p_hold", "p_buy"]].values
    pred = P.argmax(1)
    conf = P.max(1)
    acierto = pred == preds["y"].values

    # acierto esperado por azar con las mismas proporciones de lo real y lo predicho
    real = np.bincount(preds["y"].values, minlength=3) / len(preds)
    predp = np.bincount(pred, minlength=3) / len(pred)
    azar = float((real * predp).sum())

    cortes = np.quantile(conf, PERCENTILES_CORTE)
    bordes = [0.0, *cortes, 1.0]
    nivel = np.digitize(conf, cortes)  # 0..2
    tabla = pd.DataFrame({"nivel": nivel, "acierto": acierto, "conf": conf, "anio": preds["anio"]})
    resumen = tabla.groupby("nivel").agg(
        dias=("acierto", "size"), acierto_pct=("acierto", "mean"),
        conf_min=("conf", "min"), conf_max=("conf", "max"))
    resumen["acierto_pct"] = (resumen["acierto_pct"] * 100).round(1)
    resumen["pct_de_dias"] = (resumen["dias"] / len(tabla) * 100).round(1)

    # detalle fino: acierto por decil de confianza (para ver si los extremos se separan)
    deciles = pd.qcut(conf, 10, labels=False)
    tab_dec = pd.DataFrame({"decil": deciles, "acierto": acierto, "conf": conf}).groupby("decil").agg(
        dias=("acierto", "size"), acierto_pct=("acierto", "mean"), conf_min=("conf", "min"), conf_max=("conf", "max"))
    tab_dec["acierto_pct"] = (tab_dec["acierto_pct"] * 100).round(1)
    tab_dec.to_csv(OUT / "9_acierto_por_decil.csv")
    print("\n  Acierto por decil de confianza:")
    print(tab_dec.to_string())

    # estabilidad: acierto por nivel en cada año
    por_anio = (tabla.groupby(["anio", "nivel"])["acierto"].mean().unstack() * 100).round(1)

    resumen.to_csv(OUT / "9_niveles_seguridad.csv")
    json.dump({
        "cortes_confianza": [round(float(c), 4) for c in cortes],
        "acierto_por_nivel_pct": resumen["acierto_pct"].tolist(),
        "pct_de_dias_por_nivel": resumen["pct_de_dias"].tolist(),
        "acierto_global_pct": round(float(acierto.mean() * 100), 1),
        "acierto_azar_pct": round(azar * 100, 1),
        "acierto_por_anio_y_nivel_pct": {int(a): fila.tolist() for a, fila in por_anio.iterrows()},
        "anios": ANIOS,
        "modelo": f"LR-v8-interactions, peso HOLD x{PESO_HOLD}",
        "bordes": [round(float(b), 4) for b in bordes],
    }, open(OUT / "9_niveles_seguridad.json", "w", encoding="utf-8"), indent=2)

    print(f"\n  Cortes (percentiles {PERCENTILES_CORTE} de la confianza):", [round(float(c), 4) for c in cortes])
    print(resumen.to_string())
    print(f"\n  Acierto global {acierto.mean() * 100:.1f} % · azar con las mismas proporciones {azar * 100:.1f} %")
    print("\n  Acierto por año y nivel (%):")
    print(por_anio.to_string())


if __name__ == "__main__":
    main()
