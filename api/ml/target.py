"""
Etiqueta real (ground truth) de cada dia, con la MISMA definicion usada para
entrenar el modelo (`scripts_v1/01_build_raw_dataset.py::calcular_target`):

    r_fwd(t)       = ln(Close_{t+1} / Close_t)
    umbral_buy(t)  = percentil 70 de r_fwd en los 252 dias previos (sin incluir t)
    umbral_sell(t) = percentil 30 de r_fwd en los 252 dias previos (sin incluir t)

    BUY  si r_fwd(t) >= umbral_buy(t)
    SELL si r_fwd(t) <= umbral_sell(t)
    HOLD en otro caso

Sirve para evaluar las señales mostradas en la plataforma contra lo que
realmente paso el dia siguiente. A diferencia del dataset de entrenamiento
(que rellena con HOLD), aqui un dia sin cierre siguiente o sin historial
suficiente para los umbrales queda como None ("pendiente"): no se inventa.

Si el modelo se reentrena con otro horizonte o percentiles, estas constantes
deben cambiar igual.
"""
import numpy as np
import pandas as pd

HORIZONTE_DIAS = 1
PERCENTIL_BUY = 70
PERCENTIL_SELL = 30
VENTANA_PERCENTIL = 252


def etiquetas_reales(close: pd.Series) -> pd.DataFrame:
    """Retorna DataFrame (mismo indice que `close`) con r_forward, umbrales y
    `real` ∈ {"buy", "hold", "sell", None}."""
    r_fwd = np.log(close.shift(-HORIZONTE_DIAS) / close)
    historial = r_fwd.shift(1).rolling(VENTANA_PERCENTIL, min_periods=VENTANA_PERCENTIL // 2)
    umbral_buy = historial.quantile(PERCENTIL_BUY / 100)
    umbral_sell = historial.quantile(PERCENTIL_SELL / 100)

    conocido = r_fwd.notna() & umbral_buy.notna() & umbral_sell.notna()
    real = pd.Series(np.where(r_fwd >= umbral_buy, "buy",
                              np.where(r_fwd <= umbral_sell, "sell", "hold")),
                     index=close.index, dtype=object)
    real[~conocido] = None

    return pd.DataFrame({
        "r_forward": r_fwd,
        "umbral_buy": umbral_buy,
        "umbral_sell": umbral_sell,
        "real": real,
    })
