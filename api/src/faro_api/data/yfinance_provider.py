"""Primary market data provider: Yahoo Finance via yfinance (free, keyless)."""

from datetime import date, timedelta
from typing import Any, cast

import pandas as pd

from faro_api.data.provider import MarketDataError, MarketDataProvider


class YFinanceProvider(MarketDataProvider):
    """Daily adjusted closes from Yahoo Finance."""

    name = "yfinance"

    def get_daily_closes(self, ticker: str, start: date, end: date) -> pd.Series:
        import yfinance  # local import: heavy, and keeps tests importable offline

        try:
            frame = cast(
                pd.DataFrame,
                yfinance.download(
                    ticker,
                    start=start.isoformat(),
                    # yfinance's `end` is exclusive; include the end date itself.
                    end=(end + timedelta(days=1)).isoformat(),
                    interval="1d",
                    auto_adjust=True,  # adjusted closes (splits + dividends)
                    progress=False,
                    threads=False,
                ),
            )
        except Exception as exc:
            raise MarketDataError(f"yfinance failed for {ticker}: {exc}") from exc

        if frame is None or frame.empty:
            raise MarketDataError(f"yfinance returned no data for {ticker}")

        closes: Any = frame["Close"]
        if isinstance(closes, pd.DataFrame):  # multi-index when batching tickers
            closes = closes[ticker] if ticker in closes.columns else closes.iloc[:, 0]
        series = pd.Series(closes, name=ticker).dropna().astype("float64")
        series.index = pd.DatetimeIndex(series.index).tz_localize(None).normalize()
        return series.sort_index()
