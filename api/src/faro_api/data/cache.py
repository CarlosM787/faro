"""Parquet-on-disk price cache with staleness handling.

Strategy (plan risk #1 — yfinance rate limits / outages):
- Serve from parquet when fresh (< ``cache_max_age_hours`` old).
- Otherwise try providers in order (primary → fallback) and refresh the file.
- If every provider fails but a stale file exists, serve it with ``stale=True``
  — the app degrades gracefully offline instead of breaking.
"""

import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd

from faro_api.data.provider import MarketDataError, MarketDataProvider

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PriceHistory:
    """Adjusted daily closes for one ticker, with provenance."""

    ticker: str
    closes: pd.Series  # DatetimeIndex → float64
    as_of: datetime  # when the data was last refreshed
    stale: bool  # True when served past max age because providers failed
    source: str  # provider name or "cache"


class PriceCache:
    """Ticker → parquet file cache in front of a provider chain."""

    def __init__(
        self,
        providers: list[MarketDataProvider],
        cache_dir: Path,
        max_age_hours: float = 24.0,
    ) -> None:
        if not providers:
            raise ValueError("PriceCache needs at least one provider")
        self._providers = providers
        self._dir = cache_dir
        self._max_age = timedelta(hours=max_age_hours)
        self._dir.mkdir(parents=True, exist_ok=True)

    def _path(self, ticker: str) -> Path:
        return self._dir / f"{ticker.upper()}.parquet"

    def _read(self, ticker: str) -> tuple[pd.Series, datetime] | None:
        path = self._path(ticker)
        if not path.exists():
            return None
        frame = pd.read_parquet(path)
        series = frame["close"].astype("float64").rename(ticker)
        series.index = pd.DatetimeIndex(series.index)
        fetched_at = datetime.fromisoformat(str(frame.attrs.get("fetched_at", "")) or "1970-01-01")
        return series, fetched_at

    def _write(self, ticker: str, closes: pd.Series, fetched_at: datetime) -> None:
        frame = closes.rename("close").to_frame()
        frame.attrs["fetched_at"] = fetched_at.isoformat()
        frame.to_parquet(self._path(ticker))

    def get_history(self, ticker: str, start: date, end: date) -> PriceHistory:
        """Closes for [start, end], cache-first with graceful degradation."""
        cached = self._read(ticker)
        now = datetime.now()

        if cached is not None:
            closes, fetched_at = cached
            covers = bool(len(closes)) and closes.index.max() >= pd.Timestamp(end) - pd.Timedelta(
                days=4  # weekend/holiday tolerance at the range end
            )
            if now - fetched_at < self._max_age and covers:
                return PriceHistory(
                    ticker=ticker,
                    closes=closes.loc[str(start) : str(end)],
                    as_of=fetched_at,
                    stale=False,
                    source="cache",
                )

        errors: list[str] = []
        for provider in self._providers:
            try:
                closes = provider.get_daily_closes(ticker, start, end)
            except MarketDataError as exc:
                errors.append(str(exc))
                continue
            self._write(ticker, closes, now)
            return PriceHistory(
                ticker=ticker, closes=closes, as_of=now, stale=False, source=provider.name
            )

        if cached is not None:  # all providers down → stale cache beats no data
            closes, fetched_at = cached
            logger.warning("Serving STALE cache for %s (providers failed: %s)", ticker, errors)
            return PriceHistory(
                ticker=ticker,
                closes=closes.loc[str(start) : str(end)],
                as_of=fetched_at,
                stale=True,
                source="cache",
            )

        raise MarketDataError(f"No data for {ticker}: {'; '.join(errors)}")
