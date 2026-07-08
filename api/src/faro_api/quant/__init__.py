"""Faro quant engine — pure, first-principles financial mathematics.

Design contract (docs/TECH-NOTES.md):
- **Pure**: numpy/pandas in, numbers out. No I/O, no network, no DB.
- **First principles**: every metric implemented from its documented formula.
  No quant black-box libraries here (quantstats/scipy are used only in tests,
  as independent cross-checks).
- **Explicit assumptions**: 252 trading days/year, sample std (ddof=1),
  simple vs log returns always named explicitly.
"""

from faro_api.quant.portfolio import (
    correlation_matrix,
    herfindahl_index,
    risk_contributions,
    top_weight,
)
from faro_api.quant.ratios import sharpe_ratio, sortino_ratio
from faro_api.quant.relative import beta, jensens_alpha
from faro_api.quant.returns import (
    annualized_return,
    annualized_volatility,
    log_returns,
    simple_returns,
)
from faro_api.quant.risk import (
    cvar,
    drawdown_series,
    historical_var,
    max_drawdown,
    parametric_var,
)

__all__ = [
    "annualized_return",
    "annualized_volatility",
    "beta",
    "correlation_matrix",
    "cvar",
    "drawdown_series",
    "herfindahl_index",
    "historical_var",
    "jensens_alpha",
    "log_returns",
    "max_drawdown",
    "parametric_var",
    "risk_contributions",
    "sharpe_ratio",
    "simple_returns",
    "sortino_ratio",
    "top_weight",
]
