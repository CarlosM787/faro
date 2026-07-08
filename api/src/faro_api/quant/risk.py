"""Downside risk metrics: VaR (historical & parametric), CVaR, drawdown.

Sign convention: VaR/CVaR are reported as **positive loss fractions**
(e.g. 0.023 = "you'd lose 2.3% or more"). Drawdowns are **negative**
(a -25% drawdown is -0.25) — matching how each is conventionally quoted.
"""

import numpy as np
import pandas as pd


def _norm_ppf(p: float) -> float:
    """Inverse standard-normal CDF via Acklam's rational approximation.

    Implemented from first principles (the engine allows no scipy).
    Peter Acklam (2003), "An algorithm for computing the inverse normal
    cumulative distribution function" — max abs. error ≈ 1.15e-9.
    Cross-checked against scipy.stats.norm.ppf in tests.
    """
    if not 0.0 < p < 1.0:
        raise ValueError("p must be in (0, 1)")

    a = (
        -3.969683028665376e01,
        2.209460984245205e02,
        -2.759285104469687e02,
        1.383577518672690e02,
        -3.066479806614716e01,
        2.506628277459239e00,
    )
    b = (
        -5.447609879822406e01,
        1.615858368580409e02,
        -1.556989798598866e02,
        6.680131188771972e01,
        -1.328068155288572e01,
    )
    c = (
        -7.784894002430293e-03,
        -3.223964580411365e-01,
        -2.400758277161838e00,
        -2.549732539343734e00,
        4.374664141464968e00,
        2.938163982698783e00,
    )
    d = (7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e00, 3.754408661907416e00)
    p_low, p_high = 0.02425, 1 - 0.02425

    if p < p_low:  # lower tail
        q = np.sqrt(-2 * np.log(p))
        num = ((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]
        den = (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1
        return float(num / den)
    if p <= p_high:  # central region
        q = p - 0.5
        r = q * q
        num = (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q
        den = ((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1
        return float(num / den)
    # upper tail (mirror of lower)
    q = np.sqrt(-2 * np.log(1 - p))
    num = ((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]
    den = (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1
    return float(-num / den)


def historical_var(returns: pd.Series, confidence: float = 0.95) -> float:
    """Historical (empirical) Value-at-Risk.

    Formula: VaR_c = -Quantile(r, 1 - c)
    The (1-c) empirical quantile of the return distribution, sign-flipped
    to a positive loss. Makes no distributional assumption.
    """
    if returns.empty:
        return 0.0
    return float(-np.quantile(returns.to_numpy(dtype="float64"), 1.0 - confidence))


def parametric_var(returns: pd.Series, confidence: float = 0.95) -> float:
    """Parametric (variance–covariance) Value-at-Risk.

    Formula: VaR_c = -(μ + z_{1-c} · σ)
    with μ, σ the sample mean and std (ddof=1) of returns, and z the
    standard-normal quantile. **Assumes returns are normally distributed**
    — a documented simplification that understates fat-tail risk
    (the reason historical VaR is also provided).
    """
    if len(returns) < 2:
        return 0.0
    mu = float(returns.mean())
    sigma = float(returns.std(ddof=1))
    return -(mu + _norm_ppf(1.0 - confidence) * sigma)


def cvar(returns: pd.Series, confidence: float = 0.95) -> float:
    """Conditional VaR / Expected Shortfall (historical).

    Formula: CVaR_c = -E[ r | r ≤ Quantile(r, 1 - c) ]
    The average loss in the tail beyond the VaR threshold.
    """
    if returns.empty:
        return 0.0
    values = returns.to_numpy(dtype="float64")
    threshold = np.quantile(values, 1.0 - confidence)
    tail = values[values <= threshold]
    if tail.size == 0:
        return 0.0
    return float(-tail.mean())


def drawdown_series(prices: pd.Series) -> pd.Series:
    """Drawdown at each point: D_t = P_t / max(P_0..P_t) - 1  (≤ 0)."""
    return prices / prices.cummax() - 1.0


def max_drawdown(prices: pd.Series) -> float:
    """Maximum drawdown: min_t D_t — the worst peak-to-trough decline (≤ 0)."""
    if prices.empty:
        return 0.0
    return float(drawdown_series(prices).min())
