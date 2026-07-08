"""Seed data: demo portfolio is created once and is idempotent."""

from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from faro_api.db.models import Base, Portfolio
from faro_api.db.seed import DEMO_NAME, seed_demo_portfolio


def _session() -> Session:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    return Session(engine, expire_on_commit=False)


def test_seed_creates_demo_portfolio() -> None:
    with _session() as session:
        portfolio = seed_demo_portfolio(session)
        assert portfolio.name == DEMO_NAME
        assert len(portfolio.positions) == 6
        tickers = {p.ticker for p in portfolio.positions}
        assert {"AAPL", "MSFT", "NVDA", "KO", "VZ", "VTI"} == tickers
        assert all(p.shares > Decimal(0) and p.cost_basis > Decimal(0) for p in portfolio.positions)


def test_seed_is_idempotent() -> None:
    with _session() as session:
        first = seed_demo_portfolio(session)
        second = seed_demo_portfolio(session)
        assert first.id == second.id
        assert session.query(Portfolio).count() == 1
