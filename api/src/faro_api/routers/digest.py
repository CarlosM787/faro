"""Daily digest endpoint."""

from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from faro_api.agent.loop import get_provider
from faro_api.db.models import Portfolio
from faro_api.db.session import get_session
from faro_api.services.digest_service import DigestService
from faro_api.services.market_data import get_market_data_service
from faro_api.services.metrics_service import MetricsService

router = APIRouter(prefix="/portfolios/{portfolio_id}/digest", tags=["digest"])

SessionDep = Annotated[Session, Depends(get_session)]


class DigestIn(BaseModel):
    language: Literal["en", "es"] = "en"


class DigestOut(BaseModel):
    markdown: str
    facts: dict[str, Any]
    grounding_violations: list[float]
    provider: str
    error: str | None = None


@router.post("")
async def generate_digest(portfolio_id: int, body: DigestIn, session: SessionDep) -> DigestOut:
    portfolio = session.get(Portfolio, portfolio_id)
    if portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    if not portfolio.positions:
        raise HTTPException(status_code=422, detail="Portfolio has no positions")

    service = DigestService(MetricsService(get_market_data_service()))
    result = await service.generate(
        list(portfolio.positions), language=body.language, provider=get_provider()
    )
    return DigestOut(**result.__dict__)
