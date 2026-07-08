"""Portfolio metrics service — bridges positions, market data, and the quant engine.

This is the single computation path used by BOTH the REST API and the agent's
tools (one engine, two consumers — the core architecture guarantee).
"""

from dataclasses import dataclass
from datetime import datetime

import pandas as pd

from faro_api.config import get_settings
from faro_api.db.models import Position
from faro_api.quant import (
    annualized_return,
    annualized_volatility,
    sharpe_ratio,
    simple_returns,
    sortino_ratio,
)
from faro_api.services.market_data import MarketDataService, MarketSnapshot


def portfolio_value_series(positions: list[Position], closes: pd.DataFrame) -> pd.Series:
    """Daily portfolio market value: V_t = Σ_i shares_i · P_{i,t}.

    Uses float64 for the vectorized math (Decimal only at the DB boundary).
    """
    value = pd.Series(0.0, index=closes.index)
    for pos in positions:
        value = value + float(pos.shares) * closes[pos.ticker]
    return value


@dataclass(frozen=True)
class CoreMetrics:
    """Core risk/return metrics for one portfolio."""

    annual_return: float
    annual_volatility: float
    sharpe: float
    sortino: float
    risk_free_rate: float
    window_start: datetime
    window_end: datetime
    as_of: datetime
    stale: bool


class MetricsService:
    """Computes portfolio metrics from positions + market data."""

    def __init__(self, market_data: MarketDataService) -> None:
        self._market_data = market_data

    def _snapshot(self, positions: list[Position]) -> MarketSnapshot:
        tickers = sorted({p.ticker for p in positions})
        return self._market_data.get_closes(tickers)

    def core_metrics(self, positions: list[Position]) -> CoreMetrics:
        """Annualized return/vol + Sharpe/Sortino over the lookback window."""
        settings = get_settings()
        snap = self._snapshot(positions)
        returns = simple_returns(portfolio_value_series(positions, snap.closes))
        rf = settings.risk_free_rate
        return CoreMetrics(
            annual_return=annualized_return(returns),
            annual_volatility=annualized_volatility(returns),
            sharpe=sharpe_ratio(returns, risk_free_rate=rf),
            sortino=sortino_ratio(returns, risk_free_rate=rf),
            risk_free_rate=rf,
            window_start=snap.closes.index.min().to_pydatetime(),
            window_end=snap.closes.index.max().to_pydatetime(),
            as_of=snap.as_of,
            stale=snap.stale,
        )
