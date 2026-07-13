"""One engine, two consumers — proven.

The dashboard (REST /metrics) and the copilot (agent tools) must report the
same numbers because they call the same MetricsService. This test computes
metrics both ways on deterministic synthetic data and asserts exact equality.
"""

import json
from datetime import date, datetime
from decimal import Decimal

import numpy as np
import pandas as pd

from faro_api.agent.tools import METRIC_NAMES, ToolExecutor
from faro_api.db.models import Position
from faro_api.services.market_data import MarketSnapshot
from faro_api.services.metrics_service import MetricsService


class FakeMarketData:
    """Deterministic 300-day GBM closes for AAPL, KO and SPY (seeded)."""

    def __init__(self) -> None:
        rng = np.random.default_rng(99)
        idx = pd.bdate_range("2025-01-01", periods=300)
        frame = pd.DataFrame(
            {
                t: 100.0 * np.exp(np.cumsum(0.0003 + 0.01 * rng.standard_normal(300)))
                for t in ("AAPL", "KO", "SPY")
            },
            index=idx,
        )
        self._frame = frame

    def get_closes(self, tickers: list[str], lookback_days: int = 730) -> MarketSnapshot:
        return MarketSnapshot(
            closes=self._frame[tickers],
            as_of=datetime(2026, 1, 1),
            stale=False,
            sources=("yfinance",),
        )


def _positions() -> list[Position]:
    return [
        Position(
            ticker="AAPL",
            shares=Decimal(10),
            cost_basis=Decimal(150),
            purchase_date=date(2024, 1, 1),
        ),
        Position(
            ticker="KO", shares=Decimal(20), cost_basis=Decimal(55), purchase_date=date(2024, 1, 1)
        ),
    ]


def test_agent_tool_numbers_equal_dashboard_numbers() -> None:
    market = FakeMarketData()
    service = MetricsService(market)  # type: ignore[arg-type]
    positions = _positions()

    dashboard = service.full_metrics(positions)  # what GET /metrics serves
    executor = ToolExecutor(positions, service, market)  # type: ignore[arg-type]

    # Every metric the agent can quote must equal the dashboard value exactly.
    for metric in METRIC_NAMES:
        tool_value = json.loads(executor.execute("get_metric", {"metric": metric}))["value"]
        assert tool_value == round(float(getattr(dashboard, metric)), 6), metric

    summary = json.loads(executor.execute("get_portfolio_summary", {}))
    assert summary["value"] == round(dashboard.value, 2)
    assert summary["pnl"] == round(dashboard.pnl, 2)

    detail = json.loads(executor.execute("get_position_detail", {"ticker": "AAPL"}))
    aapl = next(p for p in dashboard.positions if p.ticker == "AAPL")
    assert detail["weight"] == round(aapl.weight, 4)
    assert detail["beta"] == round(aapl.beta, 4)


def test_benchmark_tool_provides_benchmark_return_explicitly() -> None:
    """QA requirement: the model must never derive the benchmark's return."""
    market = FakeMarketData()
    service = MetricsService(market)  # type: ignore[arg-type]
    executor = ToolExecutor(_positions(), service, market)  # type: ignore[arg-type]

    result = json.loads(executor.execute("compare_to_benchmark", {}))
    assert "benchmark_annual_return_percent" in result
    assert result["benchmark_annual_return_percent"].endswith("%")
    assert "portfolio_annual_return_percent" in result
