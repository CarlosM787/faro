"""Copilot chat endpoints: SSE stream + per-portfolio history."""

import json
from collections.abc import AsyncIterator
from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from faro_api.agent.loop import run_agent
from faro_api.agent.provider import Message
from faro_api.agent.tools import ToolExecutor
from faro_api.db.models import ChatMessage, Portfolio
from faro_api.db.session import get_engine, get_session
from faro_api.services.market_data import get_market_data_service
from faro_api.services.metrics_service import MetricsService

router = APIRouter(prefix="/portfolios/{portfolio_id}/chat", tags=["chat"])

SessionDep = Annotated[Session, Depends(get_session)]

HISTORY_TURNS = 12  # context window discipline: last N messages only


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    language: Literal["en", "es"] = "en"


class ChatMessageOut(BaseModel):
    role: str
    content: str
    tool_calls: list[dict] | None = None  # type: ignore[type-arg]
    language: str
    created_at: datetime


def _load_portfolio(session: Session, portfolio_id: int) -> Portfolio:
    portfolio = session.get(Portfolio, portfolio_id)
    if portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    if not portfolio.positions:
        raise HTTPException(status_code=422, detail="Portfolio has no positions")
    return portfolio


@router.get("")
def get_history(portfolio_id: int, session: SessionDep) -> list[ChatMessageOut]:
    rows = (
        session.query(ChatMessage)
        .filter_by(portfolio_id=portfolio_id)
        .order_by(ChatMessage.created_at, ChatMessage.id)
        .all()
    )
    return [
        ChatMessageOut(
            role=r.role,
            content=r.content,
            tool_calls=json.loads(r.tool_calls_json) if r.tool_calls_json else None,
            language=r.language,
            created_at=r.created_at,
        )
        for r in rows
    ]


@router.post("")
async def chat(portfolio_id: int, body: ChatIn, session: SessionDep) -> StreamingResponse:
    """Stream the copilot's answer as SSE (`text`, `tool_call`, `done` events)."""
    portfolio = _load_portfolio(session, portfolio_id)
    positions = list(portfolio.positions)

    history_rows = (
        session.query(ChatMessage)
        .filter_by(portfolio_id=portfolio_id)
        .order_by(ChatMessage.created_at.desc(), ChatMessage.id.desc())
        .limit(HISTORY_TURNS)
        .all()
    )
    history: list[Message] = [
        {"role": r.role, "content": r.content} for r in reversed(history_rows)
    ]

    executor = ToolExecutor(
        positions=positions,
        metrics_service=MetricsService(get_market_data_service()),
        market_data=get_market_data_service(),
    )

    async def stream() -> AsyncIterator[str]:
        reply_parts: list[str] = []
        tool_calls: list[dict] = []  # type: ignore[type-arg]
        async for event in run_agent(history, body.message, body.language, executor):
            if event["type"] == "text":
                reply_parts.append(event["text"])
            elif event["type"] == "tool_call":
                tool_calls.append({"name": event["name"], "arguments": event["arguments"]})
            yield f"data: {json.dumps(event)}\n\n"

        # Persist the exchange after the stream completes (own session — the
        # request-scoped one is closed by the time the generator finishes).
        from sqlalchemy.orm import Session as SASession

        with SASession(get_engine()) as write_session:
            write_session.add(
                ChatMessage(
                    portfolio_id=portfolio_id,
                    role="user",
                    content=body.message,
                    language=body.language,
                )
            )
            write_session.add(
                ChatMessage(
                    portfolio_id=portfolio_id,
                    role="assistant",
                    content="".join(reply_parts),
                    tool_calls_json=json.dumps(tool_calls) if tool_calls else None,
                    language=body.language,
                )
            )
            write_session.commit()

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
