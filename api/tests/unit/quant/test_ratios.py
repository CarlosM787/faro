"""Sharpe & Sortino — hand-computed references + quantstats cross-check."""

import math

import pandas as pd
import pytest

from faro_api.quant import sharpe_ratio, sortino_ratio


class TestHandComputed:
    def test_sharpe_zero_rf(self) -> None:
        # returns [0.01, 0.02, 0.03]: mean = 0.02
        # sample std = sqrt(((0.01)^2 + 0 + (0.01)^2)/2) = sqrt(0.0001) = 0.01
        # Sharpe = 0.02/0.01 * sqrt(252) = 2*sqrt(252)
        r = pd.Series([0.01, 0.02, 0.03])
        assert sharpe_ratio(r) == pytest.approx(2.0 * math.sqrt(252))

    def test_sharpe_rf_reduces_ratio(self) -> None:
        r = pd.Series([0.01, 0.02, 0.03])
        assert sharpe_ratio(r, risk_free_rate=0.05) < sharpe_ratio(r, risk_free_rate=0.0)

    def test_sortino_zero_rf(self) -> None:
        # returns [0.02, -0.01, 0.02, -0.01]: mean = 0.005
        # downside (vs 0): [0, -0.01, 0, -0.01]
        # DD = sqrt(mean of squares) = sqrt((0.0001+0.0001)/4) = sqrt(0.00005)
        # Sortino = 0.005/sqrt(0.00005) * sqrt(252)
        r = pd.Series([0.02, -0.01, 0.02, -0.01])
        expected = 0.005 / math.sqrt(0.00005) * math.sqrt(252)
        assert sortino_ratio(r) == pytest.approx(expected)

    def test_all_positive_returns_sortino_degenerate(self) -> None:
        # No downside at all → DD = 0 → defined as 0.0 (documented convention)
        assert sortino_ratio(pd.Series([0.01, 0.02, 0.02])) == 0.0


class TestCrossCheck:
    def test_sharpe_vs_quantstats(self, gbm_returns: pd.Series) -> None:
        import quantstats.stats as qs

        ours = sharpe_ratio(gbm_returns, risk_free_rate=0.0)
        theirs = float(qs.sharpe(gbm_returns, rf=0.0, periods=252, annualize=True))
        assert ours == pytest.approx(theirs, rel=1e-9)

    def test_sortino_vs_quantstats(self, gbm_returns: pd.Series) -> None:
        import quantstats.stats as qs

        ours = sortino_ratio(gbm_returns, risk_free_rate=0.0)
        theirs = float(qs.sortino(gbm_returns, rf=0.0, periods=252, annualize=True))
        assert ours == pytest.approx(theirs, rel=1e-9)
