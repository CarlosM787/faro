"""FastAPI application factory."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from faro_api import __version__
from faro_api.config import get_settings
from faro_api.db.seed import seed_demo_portfolio
from faro_api.db.session import get_engine
from faro_api.routers.portfolios import router as portfolios_router


@asynccontextmanager
async def _lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Create tables and seed the demo portfolio on startup (idempotent)."""
    with Session(get_engine()) as session:
        seed_demo_portfolio(session)
    yield


def create_app() -> FastAPI:
    """Build the Faro API application."""
    settings = get_settings()
    app = FastAPI(
        lifespan=_lifespan,
        title="Faro — AI Portfolio Copilot API",
        version=__version__,
        description=(
            "First-principles quant analytics with a tool-grounded LLM copilot. "
            "Educational tool — not investment advice."
        ),
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(portfolios_router)

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {
            "status": "ok",
            "version": __version__,
            "llm_provider": settings.llm_provider,
        }

    return app


app = create_app()
