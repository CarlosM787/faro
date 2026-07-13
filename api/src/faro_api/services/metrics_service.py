"""Portfolio metrics service — bridges positions, market data, and the quant engine.

This is the single computation path used by BOTH the REST API and the agent's
tools (one engine, two consumers — the core architecture guarantee).
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

import numpy as np
import pandas as pd

from faro_api.config import get_settings
from faro_api.db.models import Position
from faro_api.quant import (
    annualized_return,
    annualized_volatility,
    beta,
    correlation_matrix,
    cvar,
    drawdown_series,
    herfindahl_index,
    historical_var,
    jensens_alpha,
    max_drawdown,
    parametric_var,
    risk_contributions,
    sharpe_ratio,
    simple_returns,
    sortino_ratio,
    top_weight,
)
from faro_api.services.market_data import MarketDataService

MAX_SERIES_POINTS = 500  # server-side downsampling (plan risk #5)

SeriesKind = Literal["value", "drawdown", "benchmark"]


def portfolio_value_series(positions: list[Position], closes: pd.DataFrame) -> pd.Series:
    """Daily portfolio market value: V_t = Σ_i shares_i · P_{i,t}.

    Uses float64 for the vectorized math (Decimal only at the DB boundary).
    """
    value = pd.Series(0.0, index=closes.index)
    for pos in positions:
        value = value + float(pos.shares) * closes[pos.ticker]
    return value


def _downsample(series: pd.Series, max_points: int = MAX_SERIES_POINTS) -> pd.Series:
    if len(series) <= max_points:
        return series
    step = len(series) / max_points
    idx = np.asarray([int(i * step) for i in range(max_points - 1)] + [len(series) - 1])
    return pd.Series(series.iloc[idx])


@dataclass(frozen=True)
class PositionMetrics:
    """Per-position detail (feeds the dashboard table and get_position_detail tool)."""

    ticker: str
    shares: float
    last_price: float
    value: float
    cost: float
    pnl: float
    pnl_pct: float
    weight: float
    beta: float
    risk_contribution: float


@dataclass(frozen=True)
class FullMetrics:
    """Complete risk/return picture for one portfolio."""

    # header
    value: float
    cost: float
    pnl: float
    pnl_pct: float
    day_change_pct: float
    # core (annualized)
    annual_return: float
    annual_volatility: float
    sharpe: float
    sortino: float
    # benchmark-relative
    benchmark: str
    beta: float
    alpha: float
    # downside risk (positive loss fractions; drawdown ≤ 0)
    var_hist_95: float
    var_hist_99: float
    var_param_95: float
    var_param_99: float
    cvar_95: float
    max_drawdown: float
    # structure
    hhi: float
    top_weight: float
    positions: list[PositionMetrics]
    correlation_tickers: list[str]
    correlation: list[list[float]]
    # provenance
    data_sources: list[str]
    risk_free_rate: float
    window_start: datetime
    window_end: datetime
    as_of: datetime
    stale: bool


class MetricsService:
    """Computes portfolio metrics from positions + market data."""

    def __init__(self, market_data: MarketDataService) -> None:
        self._market_data = market_data

    def full_metrics(self, positions: list[Position]) -> FullMetrics:
        """Every PRD metric in one pass over one aligned snapshot."""
        settings = get_settings()
        rf = settings.risk_free_rate
        bench = settings.benchmark_ticker

        tickers = sorted({p.ticker for p in positions})
        snap = self._market_data.get_closes(sorted({*tickers, bench}))
        asset_closes = snap.closes[tickers]
        bench_returns = simple_returns(snap.closes[bench])

        values = portfolio_value_series(positions, asset_closes)
        returns = simple_returns(values)
        asset_returns = asset_closes.pct_change().dropna()

        last = asset_closes.iloc[-1]
        total_value = float(values.iloc[-1])
        total_cost = sum(float(p.shares) * float(p.cost_basis) for p in positions)
        ticker_values = {
            t: sum(float(p.shares) for p in positions if p.ticker == t) * float(last[t])
            for t in tickers
        }
        weights = pd.Series(ticker_values) / total_value
        rc = risk_contributions(weights, asset_returns)

        position_metrics = []
        for t in tickers:
            shares = sum(float(p.shares) for p in positions if p.ticker == t)
            cost = sum(float(p.shares) * float(p.cost_basis) for p in positions if p.ticker == t)
            value = shares * float(last[t])
            position_metrics.append(
                PositionMetrics(
                    ticker=t,
                    shares=shares,
                    last_price=float(last[t]),
                    value=value,
                    cost=cost,
                    pnl=value - cost,
                    pnl_pct=(value - cost) / cost if cost else 0.0,
                    weight=float(weights[t]),
                    beta=beta(asset_returns[t], bench_returns),
                    risk_contribution=float(rc[t]),
                )
            )

        corr = correlation_matrix(asset_returns)
        return FullMetrics(
            value=total_value,
            cost=total_cost,
            pnl=total_value - total_cost,
            pnl_pct=(total_value - total_cost) / total_cost if total_cost else 0.0,
            day_change_pct=float(returns.iloc[-1]) if len(returns) else 0.0,
            annual_return=annualized_return(returns),
            annual_volatility=annualized_volatility(returns),
            sharpe=sharpe_ratio(returns, risk_free_rate=rf),
            sortino=sortino_ratio(returns, risk_free_rate=rf),
            benchmark=bench,
            beta=beta(returns, bench_returns),
            alpha=jensens_alpha(returns, bench_returns, risk_free_rate=rf),
            var_hist_95=historical_var(returns, 0.95),
            var_hist_99=historical_var(returns, 0.99),
            var_param_95=parametric_var(returns, 0.95),
            var_param_99=parametric_var(returns, 0.99),
            cvar_95=cvar(returns, 0.95),
            max_drawdown=max_drawdown(values),
            hhi=herfindahl_index(weights),
            top_weight=top_weight(weights),
            positions=position_metrics,
            correlation_tickers=tickers,
            correlation=[[round(float(v), 6) for v in row] for row in corr.to_numpy()],
            data_sources=list(snap.sources),
            risk_free_rate=rf,
            window_start=snap.closes.index.min().to_pydatetime(),
            window_end=snap.closes.index.max().to_pydatetime(),
            as_of=snap.as_of,
            stale=snap.stale,
        )

    def series(
        self, positions: list[Position], kind: SeriesKind
    ) -> dict[str, list[float] | list[str]]:
        """Chart series, downsampled server-side.

        - ``value``: portfolio market value V_t
        - ``drawdown``: D_t = V_t / cummax(V) - 1
        - ``benchmark``: portfolio vs benchmark, both normalized to 100
        """
        settings = get_settings()
        bench = settings.benchmark_ticker
        tickers = sorted({p.ticker for p in positions})
        snap = self._market_data.get_closes(sorted({*tickers, bench}))
        values = portfolio_value_series(positions, snap.closes[tickers])

        if kind == "value":
            data = _downsample(values)
            return {
                "dates": pd.DatetimeIndex(data.index).strftime("%Y-%m-%d").tolist(),
                "portfolio": data.round(2).tolist(),
            }
        if kind == "drawdown":
            data = _downsample(drawdown_series(values))
            return {
                "dates": pd.DatetimeIndex(data.index).strftime("%Y-%m-%d").tolist(),
                "portfolio": data.round(6).tolist(),
            }
        # benchmark comparison, both indexed to 100 at window start
        port = _downsample(100.0 * values / values.iloc[0])
        bench_series = snap.closes[bench]
        bench_norm = (100.0 * bench_series / bench_series.iloc[0]).reindex(port.index)
        return {
            "dates": pd.DatetimeIndex(port.index).strftime("%Y-%m-%d").tolist(),
            "portfolio": port.round(4).tolist(),
            "benchmark": bench_norm.round(4).tolist(),
        }
