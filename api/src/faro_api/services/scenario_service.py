"""Price-shock scenario engine — shared by the Scenarios page AND the agent tool.

One code path, two consumers: the same function answers the UI and the copilot,
so their numbers can never disagree.
"""

from dataclasses import dataclass

import pandas as pd

from faro_api.db.models import Position

MARKET = "*"  # shock every position


@dataclass(frozen=True)
class Shock:
    """A hypothetical instant price move: ticker (or '*') and percent change."""

    ticker: str
    pct: float  # -20 means -20%


@dataclass(frozen=True)
class PositionImpact:
    ticker: str
    value_before: float
    value_after: float
    impact: float


@dataclass(frozen=True)
class ScenarioResult:
    value_before: float
    value_after: float
    impact: float
    impact_pct: float
    positions: list[PositionImpact]


def run_price_shock(
    positions: list[Position], last_prices: pd.Series, shocks: list[Shock]
) -> ScenarioResult:
    """Apply instant price shocks and recompute portfolio value.

    V_after = Σ_i shares_i · P_i · (1 + s_i)  where s_i is the cumulative
    shock applied to ticker i (market-wide '*' shocks compound with
    ticker-specific ones).
    """
    factors: dict[str, float] = {}
    tickers = sorted({p.ticker for p in positions})
    for t in tickers:
        factor = 1.0
        for shock in shocks:
            if shock.ticker == MARKET or shock.ticker.upper() == t:
                factor *= 1.0 + shock.pct / 100.0
        factors[t] = factor

    impacts: list[PositionImpact] = []
    for t in tickers:
        shares = sum(float(p.shares) for p in positions if p.ticker == t)
        before = shares * float(last_prices[t])
        after = before * factors[t]
        impacts.append(
            PositionImpact(
                ticker=t,
                value_before=round(before, 2),
                value_after=round(after, 2),
                impact=round(after - before, 2),
            )
        )

    value_before = sum(i.value_before for i in impacts)
    value_after = sum(i.value_after for i in impacts)
    return ScenarioResult(
        value_before=round(value_before, 2),
        value_after=round(value_after, 2),
        impact=round(value_after - value_before, 2),
        impact_pct=(value_after - value_before) / value_before if value_before else 0.0,
        positions=impacts,
    )
