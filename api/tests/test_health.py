"""Smoke tests for the app factory and health endpoint."""

from fastapi.testclient import TestClient

from faro_api.main import create_app


def test_health_ok() -> None:
    client = TestClient(create_app())
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    # With no ANTHROPIC_API_KEY in CI, the fallback provider must be ollama.
    assert body["llm_provider"] in ("anthropic", "ollama")
