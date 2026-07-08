"""Market data provider interface.

Providers return **daily adjusted close prices** — the canonical input for the
quant engine (splits/dividends folded in, so return series are economically
meaningful). All providers are free/keyless by design (see docs/TECH-NOTES.md).
"""

from abc import ABC, abstractmethod
from datetime import date

import pandas as pd


class MarketDataError(RuntimeError):
    """Raised when a provider cannot deliver data (network, unknown ticker…)."""


class MarketDataProvider(ABC):
    """Interface every market data source implements."""

    name: str

    @abstractmethod
    def get_daily_closes(self, ticker: str, start: date, end: date) -> pd.Series:
        """Return a Series of adjusted daily closes.

        Index: ``pd.DatetimeIndex`` (naive, daily, trading days only, ascending).
        Values: float64 adjusted close prices.
        Raises ``MarketDataError`` on failure.
        """
