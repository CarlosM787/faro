"""Benchmark-relative metrics: beta and Jensen's alpha."""

import pandas as pd

from faro_api.quant.returns import TRADING_DAYS, annualized_return


def beta(returns: pd.Series, benchmark_returns: pd.Series) -> float:
    """CAPM beta.

    Formula: β = Cov(r_p, r_b) / Var(r_b)   (sample covariance, ddof=1)

    Series are aligned on their index intersection first — beta over
    mismatched dates is meaningless.
    """
    joined = pd.concat([returns, benchmark_returns], axis=1, join="inner").dropna()
    if len(joined) < 2:
        return 0.0
    rp = joined.iloc[:, 0].to_numpy(dtype="float64")
    rb = joined.iloc[:, 1].to_numpy(dtype="float64")
    cov = float(pd.Series(rp).cov(pd.Series(rb)))  # ddof=1 by default
    var = float(pd.Series(rb).var(ddof=1))
    if var == 0.0:
        return 0.0
    return cov / var


def jensens_alpha(
    returns: pd.Series,
    benchmark_returns: pd.Series,
    risk_free_rate: float = 0.0,
    periods_per_year: int = TRADING_DAYS,
) -> float:
    """Jensen's alpha (annualized).

    Formula: α = R_p - [ R_f + β · (R_b - R_f) ]
    where R_p, R_b are annualized portfolio/benchmark returns.

    Reference: M. Jensen, "The Performance of Mutual Funds in the Period
    1945–1964", Journal of Finance (1968).
    """
    joined = pd.concat([returns, benchmark_returns], axis=1, join="inner").dropna()
    if len(joined) < 2:
        return 0.0
    rp_ann = annualized_return(joined.iloc[:, 0], periods_per_year)
    rb_ann = annualized_return(joined.iloc[:, 1], periods_per_year)
    b = beta(joined.iloc[:, 0], joined.iloc[:, 1])
    return rp_ann - (risk_free_rate + b * (rb_ann - risk_free_rate))
