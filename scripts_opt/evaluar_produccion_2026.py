"""
================================================================================
EVALUACIÓN FUERA DE MUESTRA DEL MODELO EN PRODUCCIÓN (2026 → hoy)
================================================================================
El `.pkl` de producción se entrenó con datos hasta 2025-12-31, así que todo
2026 es un periodo que el modelo nunca vio. Este script descarga datos reales
de Yahoo Finance con EXACTAMENTE el mismo código que usa la API
(`api/ml/features.py`, `api/ml/model.py`, `api/ml/target.py`), predice cada día
y lo compara con la etiqueta real del día siguiente.

Requiere red (Yahoo Finance). Los números cambian conforme pasan los días.

Uso (desde la raíz del repo):
    python scripts_opt/evaluar_produccion_2026.py

Salida: RESULTADOS_OPTIMIZADOS/analisis_hold/6_produccion_2026.csv (una fila por
día y ticker) y un resumen en consola.
"""
import sys
from datetime import datetime, timezone

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score, f1_score

API = Path(__file__).resolve().parents[1] / "api"
sys.path.insert(0, str(API))
from ml.features import build_feature_frame, fetch_market_context, fetch_ohlcv  # noqa: E402
from ml.model import load_model  # noqa: E402
from ml.target import etiquetas_reales  # noqa: E402

TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]
INICIO = "2026-01-01"
OUT = Path("RESULTADOS_OPTIMIZADOS/analisis_hold/6_produccion_2026.csv")
NY = ZoneInfo("America/New_York")


def sin_vela_en_curso(df):
    """Igual que api/main.py: descarta la vela de hoy si NYSE sigue abierto."""
    ahora = datetime.now(timezone.utc).astimezone(NY)
    if len(df) and df.index[-1].date() == ahora.date() and ahora.hour < 16:
        return df.iloc[:-1]
    return df


def resumen(d, etiqueta):
    rs = np.where(d.pred == "buy", d.r, np.where(d.pred == "sell", -d.r, 0.0))
    port = pd.Series(rs).groupby(d.fecha.values).mean()
    bh = pd.Series(d.r.values).groupby(d.fecha.values).mean()
    print(f"\n{etiqueta}  ({d.fecha.min().date()} → {d.fecha.max().date()}, n={len(d)})")
    print(f"  real  C/M/V: {(d.real == 'buy').mean():.1%} / {(d.real == 'hold').mean():.1%} / {(d.real == 'sell').mean():.1%}")
    print(f"  pred  C/M/V: {(d.pred == 'buy').mean():.1%} / {(d.pred == 'hold').mean():.1%} / {(d.pred == 'sell').mean():.1%}")
    print(f"  F1-macro={f1_score(d.real, d.pred, average='macro'):.4f}  kappa={cohen_kappa_score(d.real, d.pred):+.4f}  "
          f"accuracy={(d.real == d.pred).mean():.4f}")
    print(f"  Sharpe estrategia (apilado)={np.sqrt(252) * rs.mean() / rs.std():+.2f}  "
          f"portafolio 7 tickers={np.sqrt(252) * port.mean() / port.std():+.2f}  "
          f"| buy&hold portafolio={np.sqrt(252) * bh.mean() / bh.std():+.2f}")


def main():
    modelo = load_model()
    mercado = sin_vela_en_curso(fetch_market_context("3y"))
    filas = []
    for tk in TICKERS:
        ohlcv = sin_vela_en_curso(fetch_ohlcv(tk, "3y"))
        feat = build_feature_frame(ohlcv, mercado)
        preds = modelo.predict_frame(feat)
        reales = etiquetas_reales(ohlcv["Close"]).reindex(feat.index)
        filas.append(pd.DataFrame({
            "fecha": feat.index, "ticker": tk,
            "pred": [p["signal"] for p in preds],
            "confianza": [p["confidence"] for p in preds],
            "p_buy": [p["probabilities"]["buy"] for p in preds],
            "p_hold": [p["probabilities"]["hold"] for p in preds],
            "p_sell": [p["probabilities"]["sell"] for p in preds],
            "real": reales["real"].values, "r": reales["r_forward"].values,
            "VIX_norm": feat["VIX_norm"].values,
        }))
    d = pd.concat(filas, ignore_index=True)
    d = d[d.fecha >= INICIO]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    d.to_csv(OUT, index=False)

    ev = d.dropna(subset=["real"])
    resumen(ev, "2026 completo (fuera de muestra)")
    ultimos = ev[ev.fecha >= sorted(ev.fecha.unique())[-30]]
    resumen(ultimos, "Últimos 30 días hábiles evaluables")

    print("\n  Distribución predicha por mes (y VIX_norm medio):")
    d["mes"] = d.fecha.dt.to_period("M")
    tab = d.groupby("mes").pred.value_counts(normalize=True).unstack().fillna(0)
    tab["VIX_norm_medio"] = d.groupby("mes").VIX_norm.mean()
    print((tab * [100, 100, 100, 1]).round(1).to_string())
    print(f"\n✓ Detalle en {OUT}")


if __name__ == "__main__":
    main()
