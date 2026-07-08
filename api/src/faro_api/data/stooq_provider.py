"""Fallback market data provider: Stooq daily CSV endpoint (free, keyless).

Note: Stooq serves *split-adjusted* (not dividend-adjusted) closes for US
tickers. Documented limitation — acceptable for a fallback whose job is to
keep the app functional if Yahoo breaks (see plan risk #1).
"""

import io
from datetime import date

import httpx
import pandas as pd

from faro_api.data.provider import MarketDataError, MarketDataProvider


class StooqProvider(MarketDataProvider):
    """Daily closes from stooq.com CSV export."""

    name = "stooq"
    _URL = "https://stooq.com/q/d/l/"

    def get_daily_closes(self, ticker: str, start: date, end: date) -> pd.Series:
        symbol = f"{ticker.lower()}.us"  # US listings; benchmark SPY works too
        params = {
            "s": symbol,
            "d1": start.strftime("%Y%m%d"),
            "d2": end.strftime("%Y%m%d"),
            "i": "d",
        }
        try:
            resp = httpx.get(self._URL, params=params, timeout=20.0)
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise MarketDataError(f"stooq request failed for {ticker}: {exc}") from exc

        text = resp.text
        if not text.startswith("Date,"):
            raise MarketDataError(f"stooq returned no data for {ticker}")

        frame = pd.read_csv(io.StringIO(text), parse_dates=["Date"], index_col="Date")
        if frame.empty or "Close" not in frame:
            raise MarketDataError(f"stooq returned empty data for {ticker}")

        series = frame["Close"].dropna().astype("float64").rename(ticker)
        series.index = pd.DatetimeIndex(series.index).normalize()
        return series.sort_index()
