"""Demo portfolio seed — reviewers see a populated app instantly (PRD §MVP-1).

A deliberately teachable mix: mega-cap tech (concentration story), a defensive
staple, a dividend telecom, and a broad-market ETF to compare against SPY.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from faro_api.db.models import Portfolio, Position

DEMO_NAME = "Demo Portfolio"

_DEMO_POSITIONS: list[tuple[str, str, str, date]] = [
    # (ticker, shares, cost basis per share, purchase date)
    ("AAPL", "25", "168.20", date(2024, 3, 15)),
    ("MSFT", "12", "402.50", date(2024, 1, 22)),
    ("NVDA", "18", "88.75", date(2024, 5, 10)),
    ("KO", "60", "59.10", date(2024, 2, 5)),
    ("VZ", "45", "40.30", date(2024, 6, 3)),
    ("VTI", "20", "252.40", date(2024, 4, 18)),
]


def seed_demo_portfolio(session: Session) -> Portfolio:
    """Create the demo portfolio if absent (idempotent)."""
    existing = session.query(Portfolio).filter_by(name=DEMO_NAME).one_or_none()
    if existing is not None:
        return existing

    portfolio = Portfolio(name=DEMO_NAME)
    portfolio.positions = [
        Position(
            ticker=ticker,
            shares=Decimal(shares),
            cost_basis=Decimal(cost),
            purchase_date=purchased,
        )
        for ticker, shares, cost, purchased in _DEMO_POSITIONS
    ]
    session.add(portfolio)
    session.commit()
    return portfolio
