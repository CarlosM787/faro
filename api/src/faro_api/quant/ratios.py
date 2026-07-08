"""Risk-adjusted performance ratios from first principles."""

import numpy as np
import pandas as pd

from faro_api.quant.returns import TRADING_DAYS


def _per_period_rate(annual_rate: float, periods_per_year: int) -> float:
    """De-annualize a rate geometrically: (1 + R)^(1/N) - 1."""
    return float((1.0 + annual_rate) ** (1.0 / periods_per_year) - 1.0)


def sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.0,
    periods_per_year: int = TRADING_DAYS,
) -> float:
    """Annualized Sharpe ratio (Sharpe, 1966).

    Formula: S = mean(r_t - rf_t) / std(r_t - rf_t, ddof=1) · √N
    where rf_t is the geometrically de-annualized risk-free rate.

    Reference: W. F. Sharpe, "Mutual Fund Performance", J. Business (1966).
    """
    if len(returns) < 2:
        return 0.0
    excess = returns - _per_period_rate(risk_free_rate, periods_per_year)
    std = float(excess.std(ddof=1))
    if std == 0.0:
        return 0.0
    return float(excess.mean()) / std * float(np.sqrt(periods_per_year))


def sortino_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.0,
    periods_per_year: int = TRADING_DAYS,
) -> float:
    """Annualized Sortino ratio — Sharpe with downside deviation only.

    Formula: So = mean(excess_t) · N / (DD · √N)
    where DD = √( mean( min(excess_t, 0)² ) ) · √N  (full-sample denominator,
    the convention used by quantstats — enables the cross-check test).

    Reference: Sortino & van der Meer, "Downside Risk", JPM (1991).
    """
    if len(returns) < 2:
        return 0.0
    excess = returns - _per_period_rate(risk_free_rate, periods_per_year)
    downside = np.minimum(excess.to_numpy(), 0.0)
    downside_dev = float(np.sqrt(np.mean(np.square(downside))))
    if downside_dev == 0.0:
        return 0.0
    return float(excess.mean()) / downside_dev * float(np.sqrt(periods_per_year))
