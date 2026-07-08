"""Portfolio and metrics endpoints."""

from datetime import date, datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from faro_api.db.models import Portfolio
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


@router.get("")
def list_portfolios(session: SessionDep) -> list[PortfolioOut]:
    return [PortfolioOut.model_validate(p, from_attributes=True) for p in session.query(Portfolio)]


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
