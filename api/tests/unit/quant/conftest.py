"""Shared quant test fixtures.

Two layers of verification (docs/TECH-NOTES.md):
1. Tiny hand-computed fixtures — expected values derived in comments.
2. A 2-year synthetic GBM series cross-checked against quantstats/scipy
   (independent implementations, dev-dependencies only).
"""

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def tiny_prices() -> pd.Series:
    """Prices chosen so returns are exactly [+10%, -10%, +10%].

    P = [100, 110, 99, 108.9]
    simple: 110/100-1 = 0.10 ; 99/110-1 = -0.10 ; 108.9/99-1 = 0.10
    log:    ln(1.1), ln(0.9), ln(1.1)
    """
    idx = pd.bdate_range("2024-01-01", periods=4)
    return pd.Series([100.0, 110.0, 99.0, 108.9], index=idx)


@pytest.fixture
def gbm_returns() -> pd.Series:
    """~2 years of synthetic daily returns (GBM), fixed seed → deterministic.

    drift 8%/yr, vol 20%/yr — plausible equity-like series.
    """
    rng = np.random.default_rng(42)
    n = 504
    mu, sigma, dt = 0.08, 0.20, 1.0 / 252.0
    log_r = (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * rng.standard_normal(n)
    idx = pd.bdate_range("2023-01-02", periods=n)
    return pd.Series(np.exp(log_r) - 1.0, index=idx)
