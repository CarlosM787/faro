"""Market data service: aligned multi-ticker price history for the quant engine."""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from functools import lru_cache

import pandas as pd

from faro_api.config import get_settings
from faro_api.data.cache import PriceCache
from faro_api.data.stooq_provider import StooqProvider
from faro_api.data.yfinance_provider import YFinanceProvider

DEFAULT_LOOKBACK_DAYS = 730  # ~2 trading years — enough for stable metrics


@dataclass(frozen=True)
class MarketSnapshot:
    """Aligned adjusted-close history for a set of tickers."""

    closes: pd.DataFrame  # DatetimeIndex x ticker columns, float64
    as_of: datetime  # oldest refresh time across tickers
    stale: bool  # True if ANY ticker was served past max age
    # Distinct upstream sources ("yfinance", "stooq", "cache") — surfaced in the
    # UI because Stooq is split-adjusted only (dividends not folded in).
    sources: tuple[str, ...] = ("yfinance",)


class MarketDataService:
    """Facade over the provider chain + parquet cache."""

    def __init__(self, cache: PriceCache) -> None:
        self._cache = cache

    def get_closes(
        self, tickers: list[str], lookback_days: int = DEFAULT_LOOKBACK_DAYS
    ) -> MarketSnapshot:
        """Aligned daily closes for ``tickers`` over the lookback window.

        Rows with any missing ticker are dropped (inner join) so every series
        covers identical trading days — required for correlation/beta math.
        """
        end = date.today()
        start = end - timedelta(days=lookback_days)

        histories = [self._cache.get_history(t.upper(), start, end) for t in tickers]
        frame = pd.concat({h.ticker: h.closes for h in histories}, axis=1, join="inner")
        frame.columns = [h.ticker for h in histories]
        return MarketSnapshot(
            closes=frame.astype("float64"),
            as_of=min(h.as_of for h in histories),
            stale=any(h.stale for h in histories),
            sources=tuple(sorted({h.source for h in histories})),
        )


@lru_cache
def get_market_data_service() -> MarketDataService:
    """Singleton service wired to the free provider chain (yfinance → Stooq)."""
    settings = get_settings()
    cache = PriceCache(
        providers=[YFinanceProvider(), StooqProvider()],
        cache_dir=settings.data_dir / "cache",
        max_age_hours=settings.cache_max_age_hours,
    )
    return MarketDataService(cache)
