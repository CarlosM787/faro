"""Beta & Jensen's alpha — hand-checks + scipy.linregress cross-check."""

import numpy as np
import pandas as pd
import pytest

from faro_api.quant import annualized_return, beta, jensens_alpha


def _benchmark_pair(gbm_returns: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Portfolio = 1.3×benchmark + noise → true beta ≈ 1.3."""
    rng = np.random.default_rng(7)
    noise = pd.Series(0.002 * rng.standard_normal(len(gbm_returns)), index=gbm_returns.index)
    return 1.3 * gbm_returns + noise, gbm_returns


class TestHandComputed:
    def test_beta_of_benchmark_with_itself_is_one(self, gbm_returns: pd.Series) -> None:
        assert beta(gbm_returns, gbm_returns) == pytest.approx(1.0)

    def test_beta_scales_linearly(self, gbm_returns: pd.Series) -> None:
        # r_p = 2·r_b exactly → Cov(2b, b)/Var(b) = 2
        assert beta(2.0 * gbm_returns, gbm_returns) == pytest.approx(2.0)

    def test_alpha_zero_when_portfolio_is_benchmark(self, gbm_returns: pd.Series) -> None:
        assert jensens_alpha(gbm_returns, gbm_returns, risk_free_rate=0.04) == pytest.approx(0.0)

    def test_alpha_formula(self, gbm_returns: pd.Series) -> None:
        rp, rb = _benchmark_pair(gbm_returns)
        rf = 0.04
        expected = annualized_return(rp) - (rf + beta(rp, rb) * (annualized_return(rb) - rf))
        assert jensens_alpha(rp, rb, risk_free_rate=rf) == pytest.approx(expected)


class TestCrossCheck:
    def test_beta_vs_scipy_linregress(self, gbm_returns: pd.Series) -> None:
        from scipy.stats import linregress

        rp, rb = _benchmark_pair(gbm_returns)
        ours = beta(rp, rb)
        theirs = float(linregress(rb.to_numpy(), rp.to_numpy()).slope)
        assert ours == pytest.approx(theirs, rel=1e-9)
        assert ours == pytest.approx(1.3, abs=0.05)  # recovers the true beta
