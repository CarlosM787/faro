"""Digest service with a scripted provider — facts and grounding behavior."""

from collections.abc import AsyncIterator
from datetime import date, datetime
from decimal import Decimal

import pytest

from faro_api.agent.provider import AgentEvent, ChatOptions, Done, LLMProvider, Message, TextDelta
from faro_api.db.models import Position
from faro_api.services.digest_service import DigestService
from faro_api.services.metrics_service import FullMetrics, PositionMetrics


class ScriptedProvider(LLMProvider):
    name = "fake"
    model = "fake-1"

    def __init__(self, text: str) -> None:
        self._text = text
        self.last_prompt = ""

    async def stream_chat(
        self, messages: list[Message], options: ChatOptions
    ) -> AsyncIterator[AgentEvent]:
        self.last_prompt = str(messages[-1]["content"])
        yield TextDelta(self._text)
        yield Done(stop_reason="end")


class StubMetricsService:
    def full_metrics(self, positions):  # type: ignore[no-untyped-def]
        pm = PositionMetrics(
            ticker="AAPL",
            shares=10,
            last_price=310.0,
            value=3100.0,
            cost=1500.0,
            pnl=1600.0,
            pnl_pct=1.0667,
            weight=1.0,
            beta=1.1,
            risk_contribution=1.0,
        )
        now = datetime(2026, 7, 8)
        return FullMetrics(
            value=3100.0,
            cost=1500.0,
            pnl=1600.0,
            pnl_pct=1.0667,
            day_change_pct=0.0016,
            annual_return=0.12,
            annual_volatility=0.16,
            sharpe=0.55,
            sortino=0.8,
            benchmark="SPY",
            beta=1.1,
            alpha=-0.03,
            var_hist_95=0.0162,
            var_hist_99=0.028,
            var_param_95=0.0163,
            var_param_99=0.03,
            cvar_95=0.023,
            max_drawdown=-0.18,
            hhi=1.0,
            top_weight=1.0,
            positions=[pm],
            correlation_tickers=["AAPL"],
            correlation=[[1.0]],
            data_sources=["yfinance"],
            risk_free_rate=0.043,
            window_start=now,
            window_end=now,
            as_of=now,
            stale=False,
        )


def _positions() -> list[Position]:
    return [
        Position(
            ticker="AAPL",
            shares=Decimal(10),
            cost_basis=Decimal(150),
            purchase_date=date(2024, 1, 1),
        )
    ]


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def test_facts_contain_key_figures() -> None:
    service = DigestService(StubMetricsService())  # type: ignore[arg-type]
    facts = service.build_facts(_positions(), include_earnings=False)
    assert facts["portfolio_value"] == 3100.0
    assert facts["day_change_percent"] == "0.16%"
    assert facts["var_95_percent_daily"] == "1.62%"
    assert facts["top_risk_contributors"][0]["ticker"] == "AAPL"


@pytest.mark.anyio
async def test_grounded_digest_passes() -> None:
    service = DigestService(StubMetricsService())  # type: ignore[arg-type]
    provider = ScriptedProvider("Portfolio at 3,100.00, up 0.16% today. Sharpe 0.55.")
    result = await service.generate(_positions(), "en", provider, include_earnings=False)
    assert result.grounding_violations == []
    assert "FACTS" in provider.last_prompt  # facts were embedded in the prompt


@pytest.mark.anyio
async def test_hallucinated_digest_flagged() -> None:
    service = DigestService(StubMetricsService())  # type: ignore[arg-type]
    provider = ScriptedProvider("Your portfolio soared 47.9% today!")
    result = await service.generate(_positions(), "en", provider, include_earnings=False)
    assert 47.9 in result.grounding_violations
