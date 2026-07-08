"""Return and volatility calculations from first principles."""

import numpy as np
import pandas as pd

TRADING_DAYS = 252  # US equity convention


def simple_returns(prices: pd.Series) -> pd.Series:
    """Simple (arithmetic) period returns.

    Formula: r_t = P_t / P_{t-1} - 1

    Args:
        prices: series of (adjusted) prices, ascending date index.
    Returns:
        Series of length ``len(prices) - 1``.
    """
    return (prices / prices.shift(1) - 1.0).dropna()


def log_returns(prices: pd.Series) -> pd.Series:
    """Continuously compounded (log) returns.

    Formula: r_t = ln(P_t / P_{t-1})

    Log returns are time-additive — the natural choice for statistical
    modeling; simple returns are used for portfolio aggregation.
    """
    return pd.Series(np.log(prices / prices.shift(1))).dropna()


def annualized_return(returns: pd.Series, periods_per_year: int = TRADING_DAYS) -> float:
    """Geometric (compound) annualized return from simple period returns.

    Formula: R_a = (Π(1 + r_t))^(N / n) - 1
    where n = number of observations, N = periods per year.

    Assumes ``returns`` are **simple** returns.
    """
    if returns.empty:
        return 0.0
    growth = float(np.prod(1.0 + returns.to_numpy(dtype="float64")))
    if growth <= 0.0:  # portfolio wiped out — annualization is meaningless
        return -1.0
    return float(growth ** (periods_per_year / len(returns)) - 1.0)


def annualized_volatility(returns: pd.Series, periods_per_year: int = TRADING_DAYS) -> float:
    """Annualized volatility (standard deviation of returns).

    Formula: σ_a = σ_period · √N
    with σ_period the **sample** standard deviation (ddof=1).
    """
    if len(returns) < 2:
        return 0.0
    return float(returns.std(ddof=1)) * float(np.sqrt(periods_per_year))
