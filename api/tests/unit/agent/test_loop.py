"""Agent loop with a scripted FakeProvider — no network, no models, no keys."""

import json
from collections.abc import AsyncIterator
from datetime import date
from decimal import Decimal

import pytest

from faro_api.agent.loop import run_agent
from faro_api.agent.provider import (
    AgentEvent,
    ChatOptions,
    Done,
    LLMProvider,
    Message,
    TextDelta,
    ToolCallRequest,
)
from faro_api.agent.tools import ToolExecutor
from faro_api.db.models import Position


class FakeProvider(LLMProvider):
    """Plays back a script: each round is a list of events."""

    name = "fake"
    model = "fake-1"

    def __init__(self, rounds: list[list[AgentEvent]]) -> None:
        self._rounds = rounds
        self.seen_messages: list[list[Message]] = []

    async def stream_chat(  # type: ignore[override]
        self, messages: list[Message], options: ChatOptions
    ) -> AsyncIterator[AgentEvent]:
        self.seen_messages.append([dict(m) for m in messages])
        for event in self._rounds.pop(0):
            yield event


class FakeExecutor(ToolExecutor):
    """Executes against canned results instead of live market data."""

    def __init__(self, results: dict[str, dict]) -> None:  # type: ignore[type-arg]
        self._results = results

    def execute(self, name: str, arguments: dict) -> str:  # type: ignore[type-arg, override]
        return json.dumps(self._results.get(name, {"error": "no canned result"}))


def _positions() -> list[Position]:
    return [
        Position(
            ticker="AAPL",
            shares=Decimal(10),
            cost_basis=Decimal(150),
            purchase_date=date(2024, 1, 1),
        )
    ]


async def _collect(gen) -> list[dict]:  # type: ignore[no-untyped-def, type-arg]
    return [event async for event in gen]


@pytest.mark.anyio
async def test_tool_round_then_answer() -> None:
    provider = FakeProvider(
        rounds=[
            [
                ToolCallRequest(id="c1", name="get_metric", arguments={"metric": "sharpe"}),
                Done(stop_reason="tool_use"),
            ],
            [TextDelta("Your Sharpe ratio is 0.55."), Done(stop_reason="end")],
        ]
    )
    executor = FakeExecutor({"get_metric": {"metric": "sharpe", "value": 0.5485}})

    events = await _collect(run_agent([], "how risky am I?", "en", executor, provider))

    kinds = [e["type"] for e in events]
    assert kinds == ["tool_call", "text", "done"]
    assert events[0]["name"] == "get_metric"
    assert events[-1]["grounding_violations"] == []  # 0.55 grounded in 0.5485

    # Second round must include the tool result in the conversation
    second_round = provider.seen_messages[1]
    assert any(m["role"] == "tool" and "0.5485" in m["content"] for m in second_round)


@pytest.mark.anyio
async def test_hallucination_is_flagged() -> None:
    provider = FakeProvider(
        rounds=[[TextDelta("You will definitely earn 42.5% next year!"), Done(stop_reason="end")]]
    )
    events = await _collect(run_agent([], "hi", "en", FakeExecutor({}), provider))
    assert events[-1]["grounding_violations"] == [42.5]


@pytest.mark.anyio
async def test_provider_error_surfaces_cleanly() -> None:
    provider = FakeProvider(rounds=[[Done(stop_reason="error", error="model offline")]])
    events = await _collect(run_agent([], "hi", "en", FakeExecutor({}), provider))
    assert events == [
        {"type": "done", "provider": "fake", "error": "model offline", "grounding_violations": []}
    ]


def test_real_executor_dispatches_summary() -> None:
    """ToolExecutor against a stubbed metrics service (sync, no network)."""

    class StubMetricsService:
        def full_metrics(self, positions):  # type: ignore[no-untyped-def]
            from datetime import datetime

            from faro_api.services.metrics_service import FullMetrics, PositionMetrics

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
                day_change_pct=0.002,
                annual_return=0.12,
                annual_volatility=0.16,
                sharpe=0.55,
                sortino=0.8,
                benchmark="SPY",
                beta=1.1,
                alpha=-0.03,
                var_hist_95=0.016,
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
                risk_free_rate=0.043,
                window_start=now,
                window_end=now,
                as_of=now,
                stale=False,
            )

    executor = ToolExecutor(_positions(), StubMetricsService(), market_data=None)  # type: ignore[arg-type]
    result = json.loads(executor.execute("get_portfolio_summary", {}))
    assert result["value"] == 3100.0
    assert result["positions"][0]["ticker"] == "AAPL"

    metric = json.loads(executor.execute("get_metric", {"metric": "sharpe"}))
    assert metric["value"] == 0.55

    unknown = json.loads(executor.execute("get_metric", {"metric": "magic"}))
    assert "error" in unknown
