import os
import sys
import tempfile
from pathlib import Path

# api/ debe estar en sys.path para que "import database", "import main",
# "from ml.features import ..." funcionen igual que cuando corre el server.
API_DIR = Path(__file__).resolve().parents[1]
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

# DATABASE_URL debe fijarse ANTES de que algo importe database.py (que crea
# el engine al importarse), para no tocar trading_system.db real del dev.
_TEST_DB_PATH = Path(tempfile.mkdtemp()) / "test_trading_system.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB_PATH.as_posix()}"

import numpy as np
import pandas as pd
import pytest


def make_synthetic_ohlcv(n_days: int = 320, seed: int = 0, start: str = "2024-01-01") -> pd.DataFrame:
    """OHLCV determinista (caminata aleatoria con semilla fija) para tests,
    sin llamadas de red. Suficientes dias habiles para el warmup de MA200."""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(start=start, periods=n_days)
    returns = rng.normal(loc=0.0003, scale=0.015, size=n_days)
    close = 100.0 * np.exp(np.cumsum(returns))
    high = close * (1 + np.abs(rng.normal(0, 0.005, n_days)))
    low = close * (1 - np.abs(rng.normal(0, 0.005, n_days)))
    open_ = close * (1 + rng.normal(0, 0.003, n_days))
    volume = rng.integers(1_000_000, 5_000_000, n_days)

    df = pd.DataFrame({
        "Open": open_, "High": high, "Low": low, "Close": close, "Volume": volume,
    }, index=dates)
    return df


def make_synthetic_market(index: pd.DatetimeIndex, seed: int = 1) -> pd.DataFrame:
    """Contexto de mercado (SPY/VIX) sintetico alineado al mismo indice."""
    rng = np.random.default_rng(seed)
    n = len(index)
    sp_ret = rng.normal(0.0002, 0.01, n)
    vix = 15 + np.abs(rng.normal(0, 5, n))

    market = pd.DataFrame(index=index)
    market["SP500_ret"] = sp_ret
    market["SP500_vol20"] = pd.Series(sp_ret, index=index).rolling(20).std() * np.sqrt(252)
    market["SP500_mom20"] = pd.Series(sp_ret, index=index).rolling(20).sum()
    market["VIX"] = vix
    market["VIX_change"] = pd.Series(vix, index=index).pct_change()
    market["VIX_norm"] = (
        (pd.Series(vix, index=index) - pd.Series(vix, index=index).rolling(252).mean())
        / (pd.Series(vix, index=index).rolling(252).std() + 1e-8)
    )
    return market


@pytest.fixture
def synthetic_ohlcv():
    return make_synthetic_ohlcv()


@pytest.fixture
def synthetic_market(synthetic_ohlcv):
    return make_synthetic_market(synthetic_ohlcv.index)
