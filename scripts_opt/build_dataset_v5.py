"""
================================================================================
DATASET v5 — las 61 features originales + contexto de mercado ampliado
================================================================================
Solo Yahoo Finance, solo gratis. NO recalcula las 61 features ni el target: parte
de `tesis_ml_stocks/01_raw_datasets/` (que es la fuente de verdad del paper) y le
AÑADE columnas de contexto de mercado. Así, cualquier diferencia de resultado se
atribuye exclusivamente a la información nueva.

Salida: tesis_ml_stocks/01_raw_datasets_v5/{TICKER}_raw.parquet

Familias añadidas (símbolos verificados con historial completo 2013-2025):

  F1  curva de tasas (proxy con ETFs)  SHY, IEI, IEF, TLT
  F2  volatilidad                      ^VVIX, VIXY  (+ VIX ya presente)
  F3  crédito                          HYG, LQD
  F4  divisas y materias primas        DX-Y.NYB, GC=F, CL=F
  F5  sector y amplitud                XLK, SMH, QQQ, RSP, ^RUT  (+ SPY ya presente)
  F6  transversales                    ninguna descarga: se derivan de los 7 tickers

Nota: ^TNX/^FVX/^IRX/^TYX (índices de tasas del Tesoro) y ^VIX9D/^VIX3M ya NO
devuelven historial por yfinance — verificado el 2026-08-14, solo dan los últimos
~16 días. Por eso F1 y F2 usan proxies con ETFs. Son proxies y hay que
describirlos como tales en el paper.

Todas las derivadas son estacionarias (retornos, ratios o z-scores rodantes de
252 días); ningún nivel crudo entra como feature, y ningún estadístico usa
información futura.

    python scripts_opt/build_dataset_v5.py            # descarga y construye
    python scripts_opt/build_dataset_v5.py --verificar  # solo comprueba símbolos
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import sys
import time
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

sys.path.insert(0, str(Path(__file__).parent))
from common import TICKERS, RAW_DIR

import yfinance as yf

SALIDA = Path("tesis_ml_stocks/01_raw_datasets_v5")
CACHE = Path("tesis_ml_stocks/_cache_mercado_v5.parquet")
INICIO, FIN = "2012-01-01", "2025-12-31"

SIMBOLOS = {
    # F1 curva de tasas (proxy con ETFs de bonos por duración)
    "SHY": "b1_3", "IEI": "b3_7", "IEF": "b7_10", "TLT": "b20",
    # F2 volatilidad
    "^VVIX": "vvix", "VIXY": "vixy",
    # F3 crédito
    "HYG": "hyg", "LQD": "lqd",
    # F4 divisas y materias primas
    "DX-Y.NYB": "dxy", "GC=F": "oro", "CL=F": "petroleo",
    # F5 sector y amplitud
    "XLK": "xlk", "SMH": "smh", "QQQ": "qqq", "RSP": "rsp", "^RUT": "rut",
    "SPY": "spy", "^VIX": "vix",
}


def descargar_mercado() -> pd.DataFrame:
    if CACHE.exists():
        print(f"  usando cache {CACHE}")
        return pd.read_parquet(CACHE)
    filas = {}
    for sim, nombre in SIMBOLOS.items():
        d = yf.download(sim, start=INICIO, end=FIN, auto_adjust=True, progress=False)
        if len(d) == 0:
            print(f"  ⚠ {sim}: SIN DATOS — se omite")
            continue
        if isinstance(d.columns, pd.MultiIndex):
            d.columns = d.columns.get_level_values(0)
        filas[nombre] = d["Close"]
        print(f"  {sim:<10} {len(d):>5} días  desde {d.index.min().date()}")
        time.sleep(0.4)
    df = pd.DataFrame(filas)
    df.index = pd.to_datetime(df.index)
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(CACHE)
    return df


def _z(serie, ventana=252):
    """Z-score rodante causal (solo usa el pasado)."""
    m = serie.rolling(ventana, min_periods=60).mean()
    s = serie.rolling(ventana, min_periods=60).std()
    return (serie - m) / (s + 1e-8)


def _ret(serie, n):
    return np.log(serie / serie.shift(n))


def construir_features_mercado(mc: pd.DataFrame) -> pd.DataFrame:
    """
    Deriva las features de contexto a partir de los precios de cierre.

    Dos cuidados que importan: (1) las series se rellenan hacia adelante antes de
    calcular nada, porque cada calendario tiene festivos distintos y un solo día
    faltante dentro de una ventana móvil de 60 propaga NaN 60 días; (2) todas las
    ventanas llevan min_periods, por lo mismo. Sin esto se perdían 147 filas de
    2024-2025 y los modelos ya no se evaluarían sobre las mismas fechas.
    """
    mc = mc.ffill(limit=5)
    f = pd.DataFrame(index=mc.index)

    # ── F1 curva de tasas (proxy por duración) ──
    for col, nombre in (("b1_3", "shy"), ("b3_7", "iei"), ("b7_10", "ief"), ("b20", "tlt")):
        if col in mc:
            f[f"mkt_{nombre}_ret5"] = _ret(mc[col], 5)
    if "b20" in mc and "b1_3" in mc:
        # TLT/SHY sube cuando las tasas largas caen más que las cortas
        f["mkt_pendiente_curva"] = _z(mc["b20"] / mc["b1_3"])
        f["mkt_pendiente_curva_d20"] = (mc["b20"] / mc["b1_3"]).pct_change(20)
    if "b20" in mc:
        f["mkt_tlt_vol20"] = _ret(mc["b20"], 1).rolling(20, min_periods=15).std() * np.sqrt(252)

    # ── F2 volatilidad ──
    if "vvix" in mc:
        f["mkt_vvix_z"] = _z(mc["vvix"])
        f["mkt_vvix_d5"] = mc["vvix"].pct_change(5)
    if "vixy" in mc and "vix" in mc:
        f["mkt_contango_z"] = _z(mc["vixy"] / mc["vix"])
    if "vix" in mc and "spy" in mc:
        vol_real = _ret(mc["spy"], 1).rolling(20, min_periods=15).std() * np.sqrt(252) * 100
        f["mkt_prima_varianza"] = mc["vix"] - vol_real   # implícita menos realizada

    # ── F3 crédito ──
    if "hyg" in mc and "lqd" in mc:
        f["mkt_spread_credito_z"] = _z(mc["hyg"] / mc["lqd"])
        f["mkt_spread_credito_d20"] = (mc["hyg"] / mc["lqd"]).pct_change(20)
    if "hyg" in mc:
        f["mkt_hyg_ret5"] = _ret(mc["hyg"], 5)

    # ── F4 divisas y materias primas ──
    for col, nombre in (("dxy", "dxy"), ("oro", "oro"), ("petroleo", "petroleo")):
        if col in mc:
            f[f"mkt_{nombre}_ret5"] = _ret(mc[col], 5)
            f[f"mkt_{nombre}_vol20"] = _ret(mc[col], 1).rolling(20, min_periods=15).std() * np.sqrt(252)

    # ── F5 sector y amplitud ──
    for col in ("xlk", "smh", "qqq"):
        if col in mc:
            f[f"mkt_{col}_ret5"] = _ret(mc[col], 5)
    if "rsp" in mc and "spy" in mc:
        f["mkt_amplitud_z"] = _z(mc["rsp"] / mc["spy"])      # equiponderado vs capitalización
        f["mkt_amplitud_d20"] = (mc["rsp"] / mc["spy"]).pct_change(20)
    if "rut" in mc and "spy" in mc:
        f["mkt_small_large_d20"] = (mc["rut"] / mc["spy"]).pct_change(20)
    if "xlk" in mc and "spy" in mc:
        f["mkt_tech_vs_mercado_d20"] = (mc["xlk"] / mc["spy"]).pct_change(20)

    return f


def construir_transversales(cierres: pd.DataFrame, spy: pd.Series) -> dict:
    """
    F6: features que solo existen porque hay 7 tickers a la vez.
    No requieren ninguna descarga nueva.
    """
    rets = np.log(cierres / cierres.shift(1))
    mom20 = cierres / cierres.shift(20) - 1
    # rango percentil del momentum del ticker DENTRO del universo, día a día
    rank = mom20.rank(axis=1, pct=True)
    # SPY se alinea al calendario de las acciones rellenando hacia adelante: sin
    # esto, un festivo desalineado deja NaN en 60 días de beta/correlación
    spy_ret = np.log(spy.ffill() / spy.ffill().shift(1)).reindex(rets.index).ffill(limit=5)

    salida = {}
    for tk in cierres.columns:
        d = pd.DataFrame(index=cierres.index)
        d["xs_rank_mom20"] = rank[tk]
        d["xs_disp_universo"] = mom20.std(axis=1)
        cov = rets[tk].rolling(60, min_periods=40).cov(spy_ret)
        var = spy_ret.rolling(60, min_periods=40).var()
        d["xs_beta60"] = cov / (var + 1e-12)
        d["xs_corr60"] = rets[tk].rolling(60, min_periods=40).corr(spy_ret)
        d["xs_ret_rel_universo"] = rets[tk] - rets.mean(axis=1)
        salida[tk] = d
    return salida


def main(verificar=False):
    print("=" * 78)
    print("  DATASET v5 — 61 features originales + contexto de mercado ampliado")
    print("=" * 78)
    mc = descargar_mercado()
    print(f"\n  mercado: {mc.shape[1]} series, {len(mc)} días")
    if verificar:
        base = pd.read_parquet(RAW_DIR / "AAPL_raw.parquet")
        for c in mc.columns:
            cob = mc[c].reindex(base.index).notna().mean() * 100
            print(f"    {c:<12} cobertura vs calendario AAPL: {cob:5.1f}%")
        return

    fmkt = construir_features_mercado(mc)
    print(f"  features de mercado derivadas: {fmkt.shape[1]}")

    cierres = pd.DataFrame({tk: pd.read_parquet(RAW_DIR / f"{tk}_raw.parquet")["raw_close"]
                            for tk in TICKERS})
    xs = construir_transversales(cierres, mc["spy"])
    print(f"  features transversales: {xs[TICKERS[0]].shape[1]}")

    SALIDA.mkdir(parents=True, exist_ok=True)
    for tk in TICKERS:
        base = pd.read_parquet(RAW_DIR / f"{tk}_raw.parquet")
        n0 = base.shape[1]
        # alinear al calendario del ticker; rellenar solo hacia ADELANTE (nunca futuro)
        add = fmkt.reindex(base.index).ffill(limit=3)
        add = add.join(xs[tk].reindex(base.index))
        fusion = base.join(add)
        # las nuevas columnas necesitan warmup (z-scores de 252d): recortar el inicio
        fusion = fusion.loc[fusion.index >= "2013-12-31"]
        fusion.to_parquet(SALIDA / f"{tk}_raw.parquet")
        nuevas = fusion.shape[1] - n0
        nulos = fusion[add.columns].isna().mean().mean() * 100
        print(f"  {tk:<6} {n0} -> {fusion.shape[1]} columnas (+{nuevas})  "
              f"filas={len(fusion)}  nulos en nuevas={nulos:.1f}%")

    print(f"\n  → {SALIDA}")
    print("  Para usarlo:  export TT_DATASET=v5   (o TT_DATASET=v1 para el original)")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--verificar", action="store_true")
    main(**vars(p.parse_args()))
