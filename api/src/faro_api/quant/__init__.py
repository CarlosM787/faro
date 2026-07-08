"""Faro quant engine — pure, first-principles financial mathematics.

Design contract (docs/TECH-NOTES.md):
- **Pure**: numpy/pandas in, numbers out. No I/O, no network, no DB.
- **First principles**: every metric implemented from its documented formula.
  No quant black-box libraries here (quantstats/scipy are used only in tests,
  as independent cross-checks).
- **Explicit assumptions**: 252 trading days/year, sample std (ddof=1),
  simple vs log returns always named explicitly.
"""

from faro_api.quant.ratios import sharpe_ratio, sortino_ratio
from faro_api.quant.returns import (
    annualized_return,
    annualized_volatility,
    log_returns,
    simple_returns,
)

__all__ = [
    "annualized_return",
    "annualized_volatility",
    "log_returns",
    "sharpe_ratio",
    "simple_returns",
    "sortino_ratio",
]
