"""Engine/session factory and FastAPI dependency."""

from collections.abc import Iterator
from pathlib import Path

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from faro_api.config import get_settings
from faro_api.db.models import Base

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def get_engine() -> Engine:
    global _engine, _session_factory
    if _engine is None:
        settings = get_settings()
        if settings.database_url.startswith("sqlite:///"):
            Path(settings.database_url.removeprefix("sqlite:///")).parent.mkdir(
                parents=True, exist_ok=True
            )
        _engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
        Base.metadata.create_all(_engine)
        _session_factory = sessionmaker(bind=_engine, expire_on_commit=False)
    return _engine


def get_session() -> Iterator[Session]:
    """FastAPI dependency yielding a transactional session."""
    get_engine()
    assert _session_factory is not None
    with _session_factory() as session:
        yield session
