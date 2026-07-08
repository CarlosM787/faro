"""Returns & volatility — hand-computed references + quantstats cross-check."""

import math

import pandas as pd
import pytest

from faro_api.quant import (
    annualized_return,
    annualized_volatility,
    log_returns,
    simple_returns,
)


class TestHandComputed:
    def test_simple_returns(self, tiny_prices: pd.Series) -> None:
        r = simple_returns(tiny_prices)
        assert list(r.round(12)) == [0.10, -0.10, 0.10]

    def test_log_returns(self, tiny_prices: pd.Series) -> None:
        r = log_returns(tiny_prices)
        expected = [math.log(1.1), math.log(0.9), math.log(1.1)]
        assert r.to_numpy() == pytest.approx(expected)

    def test_annualized_return_geometric(self) -> None:
        # Two periods of +10%: growth = 1.21 over 2 days.
        # R_a = 1.21^(252/2) - 1  (hand-derived formula application)
        r = pd.Series([0.10, 0.10])
        assert annualized_return(r) == pytest.approx(1.21 ** (252 / 2) - 1)

    def test_annualized_vol(self) -> None:
        # returns [0.01, -0.01]: mean 0, sample std = sqrt(((0.01)^2+(0.01)^2)/1)
        #   = sqrt(0.0002) ; annualized = sqrt(0.0002)*sqrt(252)
        r = pd.Series([0.01, -0.01])
        assert annualized_volatility(r) == pytest.approx(math.sqrt(0.0002) * math.sqrt(252))

    def test_empty_and_degenerate(self) -> None:
        assert annualized_return(pd.Series(dtype=float)) == 0.0
        assert annualized_volatility(pd.Series([0.01])) == 0.0
        # total wipeout: -100% in one period → clamp at -1.0, not a complex number
        assert annualized_return(pd.Series([-1.0])) == -1.0


class TestCrossCheck:
    """Independent implementations (quantstats) on the GBM series."""

    def test_volatility_vs_quantstats(self, gbm_returns: pd.Series) -> None:
        import quantstats.stats as qs

        ours = annualized_volatility(gbm_returns)
        theirs = float(qs.volatility(gbm_returns, periods=252, annualize=True))
        assert ours == pytest.approx(theirs, rel=1e-9)

    def test_cagr_vs_manual_compound(self, gbm_returns: pd.Series) -> None:
        # Independent derivation: total growth raised to (252/n).
        growth = float((1 + gbm_returns).prod())
        expected = growth ** (252 / len(gbm_returns)) - 1
        assert annualized_return(gbm_returns) == pytest.approx(expected, rel=1e-12)
