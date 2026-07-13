"""Agent tool schemas + dispatch.

THE grounding guarantee lives here: every tool dispatches into the same
service layer the dashboard uses, so the copilot's numbers are the
dashboard's numbers. The agent has NO other source of figures.
"""

import json
from dataclasses import asdict
from typing import Any

from faro_api.agent.provider import ToolDef
from faro_api.db.models import Position
from faro_api.services.market_data import MarketDataService
from faro_api.services.metrics_service import MetricsService
from faro_api.services.scenario_service import Shock, run_price_shock

METRIC_NAMES = [
    "annual_return",
    "annual_volatility",
    "sharpe",
    "sortino",
    "beta",
    "alpha",
    "var_hist_95",
    "var_hist_99",
    "var_param_95",
    "var_param_99",
    "cvar_95",
    "max_drawdown",
    "hhi",
    "top_weight",
]

TOOL_DEFS: list[ToolDef] = [
    ToolDef(
        name="get_portfolio_summary",
        description=(
            "Current portfolio snapshot: total value, cost, P/L, day change, and "
            "per-position weights. Call this first for any portfolio question."
        ),
        parameters={"type": "object", "properties": {}, "required": []},
    ),
    ToolDef(
        name="get_metric",
        description=(
            "One computed risk/return metric for the portfolio (2-year daily window). "
            "Returns the exact value the dashboard shows."
        ),
        parameters={
            "type": "object",
            "properties": {
                "metric": {"type": "string", "enum": METRIC_NAMES, "description": "Metric name"}
            },
            "required": ["metric"],
        },
    ),
    ToolDef(
        name="get_position_detail",
        description=(
            "Detail for one holding: shares, value, P/L, portfolio weight, beta, and "
            "its share of total portfolio risk."
        ),
        parameters={
            "type": "object",
            "properties": {"ticker": {"type": "string", "description": "e.g. NVDA"}},
            "required": ["ticker"],
        },
    ),
    ToolDef(
        name="run_price_shock_scenario",
        description=(
            "Hypothetical instant price shock. Each shock: ticker ('*' = whole market) "
            "and pct change (-20 = drops 20%). Returns before/after values and impact."
        ),
        parameters={
            "type": "object",
            "properties": {
                "shocks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "ticker": {"type": "string"},
                            "pct": {"type": "number"},
                        },
                        "required": ["ticker", "pct"],
                    },
                }
            },
            "required": ["shocks"],
        },
    ),
    ToolDef(
        name="compare_to_benchmark",
        description=(
            "Portfolio vs benchmark (SPY): annualized returns, beta, alpha — the "
            "relative performance picture."
        ),
        parameters={"type": "object", "properties": {}, "required": []},
    ),
]


class ToolExecutor:
    """Executes tool calls against the shared service layer for one portfolio."""

    def __init__(
        self,
        positions: list[Position],
        metrics_service: MetricsService,
        market_data: MarketDataService,
    ) -> None:
        self._positions = positions
        self._metrics = metrics_service
        self._market_data = market_data

    def execute(self, name: str, arguments: dict[str, Any]) -> str:
        """Run a tool; always returns a JSON string (LLM-friendly)."""
        try:
            result = self._dispatch(name, arguments)
        except Exception as exc:  # tool boundary: report, never crash the loop
            result = {"error": f"{type(exc).__name__}: {exc}"}
        return json.dumps(result, default=str)

    def _dispatch(self, name: str, args: dict[str, Any]) -> dict[str, Any]:
        full = self._metrics.full_metrics(self._positions)  # single source of truth

        if name == "get_portfolio_summary":
            return {
                "value": round(full.value, 2),
                "cost": round(full.cost, 2),
                "pnl": round(full.pnl, 2),
                "pnl_pct": round(full.pnl_pct, 4),
                "day_change_pct": round(full.day_change_pct, 4),
                "as_of": full.as_of,
                "stale_data": full.stale,
                "positions": [
                    {"ticker": p.ticker, "weight": round(p.weight, 4), "value": round(p.value, 2)}
                    for p in full.positions
                ],
            }

        if name == "get_metric":
            metric = str(args.get("metric", ""))
            if metric not in METRIC_NAMES:
                return {"error": f"unknown metric '{metric}'", "available": METRIC_NAMES}
            payload: dict[str, Any] = {
                "metric": metric,
                "value": round(float(getattr(full, metric)), 6),
                "window": f"{full.window_start:%Y-%m-%d} to {full.window_end:%Y-%m-%d}",
                "risk_free_rate": full.risk_free_rate,
            }
            if metric.startswith("var_param"):
                payload["caveat"] = (
                    "Parametric VaR assumes normally distributed returns and can "
                    "understate fat-tail risk; mention this assumption and compare "
                    "with historical VaR when relevant."
                )
            return payload

        if name == "get_position_detail":
            ticker = str(args.get("ticker", "")).upper()
            match = next((p for p in full.positions if p.ticker == ticker), None)
            if match is None:
                return {
                    "error": f"{ticker} is not in this portfolio",
                    "holdings": [p.ticker for p in full.positions],
                }
            return {
                k: (round(v, 4) if isinstance(v, float) else v) for k, v in asdict(match).items()
            }

        if name == "run_price_shock_scenario":
            shocks = [
                Shock(ticker=str(s["ticker"]), pct=float(s["pct"])) for s in args.get("shocks", [])
            ]
            if not shocks:
                return {"error": "provide at least one shock"}
            tickers = sorted({p.ticker for p in self._positions})
            snap = self._market_data.get_closes(tickers)
            result = run_price_shock(self._positions, snap.closes.iloc[-1], shocks)
            return {
                "value_before": result.value_before,
                "value_after": result.value_after,
                "impact": result.impact,
                # Pre-formatted so small models can't misquote the fraction:
                "impact_percent": f"{result.impact_pct * 100:.2f}%",
                "positions": [asdict(p) for p in result.positions],
            }

        if name == "compare_to_benchmark":
            # Benchmark's own return provided explicitly so the model never
            # derives it (α = R_p − [R_f + β(R_b − R_f)] ⇒ R_b).
            rf = full.risk_free_rate
            bench_return = (
                rf + (full.annual_return - rf - full.alpha) / full.beta if full.beta else 0.0
            )
            return {
                "benchmark": full.benchmark,
                "portfolio_annual_return_percent": f"{full.annual_return * 100:.2f}%",
                "benchmark_annual_return_percent": f"{bench_return * 100:.2f}%",
                "beta": round(full.beta, 4),
                "alpha_annualized_percent": f"{full.alpha * 100:.2f}%",
                "window": f"{full.window_start:%Y-%m-%d} to {full.window_end:%Y-%m-%d}",
            }

        return {"error": f"unknown tool '{name}'"}
