"""VaR/CVaR/drawdown — hand-computed references + scipy/quantstats cross-checks."""

import numpy as np
import pandas as pd
import pytest

from faro_api.quant import (
    cvar,
    drawdown_series,
    historical_var,
    max_drawdown,
    parametric_var,
)
from faro_api.quant.risk import _norm_ppf

# Ten fixed returns, sorted view for hand-derivation:
# [-0.05, -0.03, -0.01, 0.00, 0.01, 0.01, 0.02, 0.02, 0.03, 0.04]
TEN = pd.Series([0.01, -0.03, 0.02, 0.04, -0.05, 0.00, 0.02, 0.01, 0.03, -0.01])


class TestHandComputed:
    def test_historical_var_95(self) -> None:
        # 5th percentile of 10 sorted points (numpy linear interpolation):
        # position = 0.05*(10-1) = 0.45 → between -0.05 and -0.03:
        # -0.05 + 0.45*0.02 = -0.041 ; VaR = +0.041
        assert historical_var(TEN, 0.95) == pytest.approx(0.041)

    def test_cvar_95(self) -> None:
        # Tail: returns ≤ -0.041 → only -0.05 ; CVaR = 0.05
        assert cvar(TEN, 0.95) == pytest.approx(0.05)

    def test_parametric_var_formula(self) -> None:
        # Direct formula application with sample mu/sigma:
        mu, sigma = float(TEN.mean()), float(TEN.std(ddof=1))
        expected = -(mu + _norm_ppf(0.05) * sigma)
        assert parametric_var(TEN, 0.95) == pytest.approx(expected)
        assert parametric_var(TEN, 0.95) > 0  # a loss, positive by convention

    def test_max_drawdown(self) -> None:
        # Prices 100 → 120 → 90 → 100: worst = 90/120 - 1 = -0.25
        prices = pd.Series([100.0, 120.0, 90.0, 100.0])
        assert max_drawdown(prices) == pytest.approx(-0.25)
        dd = drawdown_series(prices)
        assert list(dd.round(10)) == [0.0, 0.0, -0.25, pytest.approx(100 / 120 - 1)]

    def test_empty_series_safe(self) -> None:
        empty = pd.Series(dtype=float)
        assert historical_var(empty) == 0.0
        assert cvar(empty) == 0.0
        assert max_drawdown(empty) == 0.0


class TestCrossCheck:
    def test_norm_ppf_vs_scipy(self) -> None:
        """Acklam approximation vs scipy across the domain (1e-8 tolerance)."""
        from scipy.stats import norm

        for p in [0.001, 0.01, 0.024, 0.05, 0.5, 0.95, 0.976, 0.99, 0.999]:
            assert _norm_ppf(p) == pytest.approx(float(norm.ppf(p)), abs=1e-8)

    def test_historical_var_vs_numpy_quantile(self, gbm_returns: pd.Series) -> None:
        expected = -float(np.quantile(gbm_returns.to_numpy(), 0.05))
        assert historical_var(gbm_returns, 0.95) == pytest.approx(expected)

    def test_max_drawdown_vs_quantstats(self, gbm_returns: pd.Series) -> None:
        import quantstats.stats as qs

        prices = 100.0 * (1 + gbm_returns).cumprod()
        ours = max_drawdown(prices)
        theirs = float(qs.max_drawdown(prices))
        assert ours == pytest.approx(theirs, rel=1e-9)
