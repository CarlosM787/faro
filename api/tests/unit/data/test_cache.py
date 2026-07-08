"""PriceCache behavior: cache-first, provider chain, stale degradation."""

from datetime import date

import pandas as pd
import pytest

from faro_api.data.cache import PriceCache
from faro_api.data.provider import MarketDataError, MarketDataProvider

START, END = date(2024, 1, 1), date(2024, 1, 10)


def _series(days: int = 8) -> pd.Series:
    idx = pd.bdate_range("2024-01-01", periods=days)
    return pd.Series([100.0 + i for i in range(days)], index=idx, name="TEST")


class FakeProvider(MarketDataProvider):
    name = "fake"

    def __init__(self, fail: bool = False, days: int = 8) -> None:
        self.fail = fail
        self.days = days
        self.calls = 0

    def get_daily_closes(self, ticker: str, start: date, end: date) -> pd.Series:
        self.calls += 1
        if self.fail:
            raise MarketDataError("boom")
        return _series(self.days)


def test_fetches_and_caches(tmp_path) -> None:  # type: ignore[no-untyped-def]
    provider = FakeProvider()
    cache = PriceCache([provider], tmp_path, max_age_hours=24)

    first = cache.get_history("TEST", START, END)
    assert first.source == "fake" and not first.stale
    assert len(first.closes) == 8

    second = cache.get_history("TEST", START, END)  # served from parquet, no refetch
    assert second.source == "cache" and not second.stale
    assert provider.calls == 1


def test_provider_chain_fallback(tmp_path) -> None:  # type: ignore[no-untyped-def]
    primary, fallback = FakeProvider(fail=True), FakeProvider()
    cache = PriceCache([primary, fallback], tmp_path, max_age_hours=24)

    result = cache.get_history("TEST", START, END)
    assert result.source == "fake"  # fallback's name
    assert primary.calls == 1 and fallback.calls == 1


def test_stale_cache_served_when_all_providers_fail(tmp_path) -> None:  # type: ignore[no-untyped-def]
    good = FakeProvider()
    cache = PriceCache([good], tmp_path, max_age_hours=0)  # instantly stale
    cache.get_history("TEST", START, END)  # populate parquet

    broken = PriceCache([FakeProvider(fail=True)], tmp_path, max_age_hours=0)
    result = broken.get_history("TEST", START, END)
    assert result.stale and result.source == "cache"
    assert len(result.closes) == 8


def test_no_data_anywhere_raises(tmp_path) -> None:  # type: ignore[no-untyped-def]
    cache = PriceCache([FakeProvider(fail=True)], tmp_path, max_age_hours=24)
    with pytest.raises(MarketDataError):
        cache.get_history("TEST", START, END)


def test_wider_range_forces_refetch(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """Regression: a fresh cache for a SHORT range must not satisfy a LONGER one."""
    provider = FakeProvider()
    cache = PriceCache([provider], tmp_path, max_age_hours=24)

    cache.get_history("TEST", date(2024, 1, 5), END)  # warm with a short window
    assert provider.calls == 1

    result = cache.get_history("TEST", date(2023, 1, 1), END)  # ask for ~1y more
    assert provider.calls == 2  # refetched — cached range didn't cover the start
    assert result.source == "fake"
