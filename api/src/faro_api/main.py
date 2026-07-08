"""FastAPI application factory."""

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from faro_api import __version__
from faro_api.config import get_settings


def create_app() -> FastAPI:
    """Build the Faro API application."""
    settings = get_settings()
    app = FastAPI(
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

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {
            "status": "ok",
            "version": __version__,
            "llm_provider": settings.llm_provider,
        }

    return app


app = create_app()
