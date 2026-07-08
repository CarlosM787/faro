"""Portfolio and metrics endpoints."""

from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from faro_api.db.models import Portfolio, Position
from faro_api.db.session import get_session
from faro_api.services.market_data import get_market_data_service
from faro_api.services.metrics_service import MetricsService

router = APIRouter(prefix="/portfolios", tags=["portfolios"])


# --- response schemas ---


class PositionOut(BaseModel):
    id: int
    ticker: str
    shares: float
    cost_basis: float
    purchase_date: date


class PortfolioOut(BaseModel):
    id: int
    name: str
    base_currency: str
    positions: list[PositionOut]


class PositionMetricsOut(BaseModel):
    ticker: str
    shares: float
    last_price: float
    value: float
    cost: float
    pnl: float
    pnl_pct: float
    weight: float
    beta: float
    risk_contribution: float


class FullMetricsOut(BaseModel):
    value: float
    cost: float
    pnl: float
    pnl_pct: float
    day_change_pct: float
    annual_return: float
    annual_volatility: float
    sharpe: float
    sortino: float
    benchmark: str
    beta: float
    alpha: float
    var_hist_95: float
    var_hist_99: float
    var_param_95: float
    var_param_99: float
    cvar_95: float
    max_drawdown: float
    hhi: float
    top_weight: float
    positions: list[PositionMetricsOut]
    correlation_tickers: list[str]
    correlation: list[list[float]]
    risk_free_rate: float
    window_start: datetime
    window_end: datetime
    as_of: datetime
    stale: bool


class SeriesOut(BaseModel):
    dates: list[str]
    portfolio: list[float]
    benchmark: list[float] | None = None


# --- helpers ---


def _get_portfolio(session: Session, portfolio_id: int) -> Portfolio:
    portfolio = session.get(Portfolio, portfolio_id)
    if portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio


def get_metrics_service() -> MetricsService:
    return MetricsService(get_market_data_service())


SessionDep = Annotated[Session, Depends(get_session)]
MetricsDep = Annotated[MetricsService, Depends(get_metrics_service)]


# --- endpoints ---


class PortfolioIn(BaseModel):
    name: str


class PositionIn(BaseModel):
    ticker: str
    shares: float
    cost_basis: float
    purchase_date: date


@router.get("")
def list_portfolios(session: SessionDep) -> list[PortfolioOut]:
    return [PortfolioOut.model_validate(p, from_attributes=True) for p in session.query(Portfolio)]


@router.post("", status_code=201)
def create_portfolio(body: PortfolioIn, session: SessionDep) -> PortfolioOut:
    portfolio = Portfolio(name=body.name.strip())
    session.add(portfolio)
    session.commit()
    return PortfolioOut.model_validate(portfolio, from_attributes=True)


@router.patch("/{portfolio_id}")
def rename_portfolio(portfolio_id: int, body: PortfolioIn, session: SessionDep) -> PortfolioOut:
    portfolio = _get_portfolio(session, portfolio_id)
    portfolio.name = body.name.strip()
    session.commit()
    return PortfolioOut.model_validate(portfolio, from_attributes=True)


@router.delete("/{portfolio_id}", status_code=204)
def delete_portfolio(portfolio_id: int, session: SessionDep) -> None:
    session.delete(_get_portfolio(session, portfolio_id))
    session.commit()


@router.post("/{portfolio_id}/positions", status_code=201)
def add_position(portfolio_id: int, body: PositionIn, session: SessionDep) -> PositionOut:
    portfolio = _get_portfolio(session, portfolio_id)
    position = Position(
        portfolio_id=portfolio.id,
        ticker=body.ticker.strip().upper(),
        shares=Decimal(str(body.shares)),  # Decimal at the persistence boundary
        cost_basis=Decimal(str(body.cost_basis)),
        purchase_date=body.purchase_date,
    )
    session.add(position)
    session.commit()
    return PositionOut.model_validate(position, from_attributes=True)


@router.patch("/{portfolio_id}/positions/{position_id}")
def update_position(
    portfolio_id: int, position_id: int, body: PositionIn, session: SessionDep
) -> PositionOut:
    position = session.get(Position, position_id)
    if position is None or position.portfolio_id != portfolio_id:
        raise HTTPException(status_code=404, detail="Position not found")
    position.ticker = body.ticker.strip().upper()
    position.shares = Decimal(str(body.shares))
    position.cost_basis = Decimal(str(body.cost_basis))
    position.purchase_date = body.purchase_date
    session.commit()
    return PositionOut.model_validate(position, from_attributes=True)


@router.delete("/{portfolio_id}/positions/{position_id}", status_code=204)
def delete_position(portfolio_id: int, position_id: int, session: SessionDep) -> None:
    position = session.get(Position, position_id)
    if position is None or position.portfolio_id != portfolio_id:
        raise HTTPException(status_code=404, detail="Position not found")
    session.delete(position)
    session.commit()


@router.get("/{portfolio_id}")
def get_portfolio(portfolio_id: int, session: SessionDep) -> PortfolioOut:
    return PortfolioOut.model_validate(_get_portfolio(session, portfolio_id), from_attributes=True)


@router.get("/{portfolio_id}/metrics")
def get_metrics(portfolio_id: int, session: SessionDep, metrics: MetricsDep) -> FullMetricsOut:
    portfolio = _get_portfolio(session, portfolio_id)
    if not portfolio.positions:
        raise HTTPException(status_code=422, detail="Portfolio has no positions")
    full = metrics.full_metrics(portfolio.positions)
    payload = {**full.__dict__, "positions": [p.__dict__ for p in full.positions]}
    return FullMetricsOut(**payload)


@router.get("/{portfolio_id}/series")
def get_series(
    portfolio_id: int,
    session: SessionDep,
    metrics: MetricsDep,
    kind: Literal["value", "drawdown", "benchmark"] = "value",
) -> SeriesOut:
    portfolio = _get_portfolio(session, portfolio_id)
    if not portfolio.positions:
        raise HTTPException(status_code=422, detail="Portfolio has no positions")
    return SeriesOut(**metrics.series(portfolio.positions, kind))  # type: ignore[arg-type]
