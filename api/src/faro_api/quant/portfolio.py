"""Portfolio-structure metrics: correlation, concentration, risk contribution."""

import numpy as np
import pandas as pd


def correlation_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    """Pairwise Pearson correlation of asset returns.

    Formula: ρ_ij = Cov(r_i, r_j) / (σ_i · σ_j)
    Delegates to ``DataFrame.corr()`` (pandas implements exactly this);
    verified manually against the covariance definition in tests.
    """
    return returns.corr()


def herfindahl_index(weights: pd.Series) -> float:
    """Herfindahl–Hirschman concentration index.

    Formula: HHI = Σ w_i²
    1/N (equal-weight floor) … 1.0 (single position).
    """
    w = weights.to_numpy(dtype="float64")
    return float(np.sum(np.square(w)))


def top_weight(weights: pd.Series) -> float:
    """Largest single-position weight — the simplest concentration flag."""
    if weights.empty:
        return 0.0
    return float(weights.max())


def risk_contributions(weights: pd.Series, returns: pd.DataFrame) -> pd.Series:
    """Fractional contribution of each asset to portfolio variance.

    Formula: RC_i = w_i · Cov(r_i, r_p) / σ_p²   with  r_p = Σ w_i r_i
    Property: Σ RC_i = 1 (asserted in tests) — this is the Euler
    decomposition of portfolio variance.
    """
    aligned = returns[weights.index.tolist()]
    cov = aligned.cov().to_numpy(dtype="float64")  # sample covariance (ddof=1)
    w = weights.to_numpy(dtype="float64")
    port_var = float(w @ cov @ w)
    if port_var == 0.0:
        return pd.Series(0.0, index=weights.index)
    contrib = w * (cov @ w) / port_var
    return pd.Series(contrib, index=weights.index)
