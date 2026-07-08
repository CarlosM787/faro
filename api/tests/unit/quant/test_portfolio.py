"""Correlation, concentration, risk contribution — hand-checks + properties."""

import numpy as np
import pandas as pd
import pytest

from faro_api.quant import (
    correlation_matrix,
    herfindahl_index,
    risk_contributions,
    top_weight,
)


def _two_asset_returns() -> pd.DataFrame:
    rng = np.random.default_rng(11)
    n = 300
    a = 0.01 * rng.standard_normal(n)
    b = 0.6 * a + 0.008 * rng.standard_normal(n)  # positively correlated with A
    idx = pd.bdate_range("2024-01-01", periods=n)
    return pd.DataFrame({"A": a, "B": b}, index=idx)


class TestCorrelation:
    def test_matches_covariance_definition(self) -> None:
        # ρ_AB = Cov(A,B) / (σ_A σ_B), computed manually with numpy
        frame = _two_asset_returns()
        manual = float(
            np.cov(frame["A"], frame["B"], ddof=1)[0, 1]
            / (frame["A"].std(ddof=1) * frame["B"].std(ddof=1))
        )
        ours = float(correlation_matrix(frame).loc["A", "B"])
        assert ours == pytest.approx(manual, rel=1e-12)

    def test_diagonal_is_one(self) -> None:
        corr = correlation_matrix(_two_asset_returns())
        assert list(np.diag(corr)) == pytest.approx([1.0, 1.0])


class TestConcentration:
    def test_hhi_hand_computed(self) -> None:
        # weights [0.5, 0.3, 0.2] → 0.25 + 0.09 + 0.04 = 0.38
        w = pd.Series([0.5, 0.3, 0.2], index=["A", "B", "C"])
        assert herfindahl_index(w) == pytest.approx(0.38)
        assert top_weight(w) == pytest.approx(0.5)

    def test_hhi_bounds(self) -> None:
        equal = pd.Series([0.25] * 4)
        single = pd.Series([1.0])
        assert herfindahl_index(equal) == pytest.approx(0.25)  # 1/N floor
        assert herfindahl_index(single) == pytest.approx(1.0)  # max concentration


class TestRiskContribution:
    def test_sums_to_one(self) -> None:
        """Euler decomposition property: Σ RC_i = 1."""
        frame = _two_asset_returns()
        w = pd.Series([0.7, 0.3], index=["A", "B"])
        rc = risk_contributions(w, frame)
        assert float(rc.sum()) == pytest.approx(1.0)

    def test_single_asset_contributes_everything(self) -> None:
        frame = _two_asset_returns()
        w = pd.Series([1.0, 0.0], index=["A", "B"])
        rc = risk_contributions(w, frame)
        assert float(rc["A"]) == pytest.approx(1.0)
        assert float(rc["B"]) == pytest.approx(0.0)
