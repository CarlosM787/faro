"""Scenario engine — hand-computed shock arithmetic."""

from datetime import date
from decimal import Decimal

import pandas as pd
import pytest

from faro_api.db.models import Position
from faro_api.services.scenario_service import Shock, run_price_shock


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


PRICES = pd.Series({"AAPL": 300.0, "KO": 80.0})  # values: 3000 + 1600 = 4600


def test_single_ticker_shock() -> None:
    # AAPL -20%: 3000 → 2400; total 4600 → 4000; impact -600
    result = run_price_shock(_positions(), PRICES, [Shock(ticker="AAPL", pct=-20)])
    assert result.value_before == 4600.0
    assert result.value_after == 4000.0
    assert result.impact == -600.0
    assert result.impact_pct == pytest.approx(-600 / 4600)


def test_market_wide_shock() -> None:
    # '*' -10%: everything × 0.9 → 4140
    result = run_price_shock(_positions(), PRICES, [Shock(ticker="*", pct=-10)])
    assert result.value_after == pytest.approx(4140.0)


def test_shocks_compound() -> None:
    # market -10% AND AAPL -20%: AAPL 3000×0.9×0.8=2160, KO 1600×0.9=1440 → 3600
    result = run_price_shock(
        _positions(), PRICES, [Shock(ticker="*", pct=-10), Shock(ticker="AAPL", pct=-20)]
    )
    assert result.value_after == pytest.approx(3600.0)
    aapl = next(p for p in result.positions if p.ticker == "AAPL")
    assert aapl.value_after == pytest.approx(2160.0)
