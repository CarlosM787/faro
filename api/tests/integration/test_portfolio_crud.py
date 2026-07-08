"""Portfolio/position CRUD round-trip through the API."""

from fastapi.testclient import TestClient

from faro_api.main import create_app


def test_crud_roundtrip(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    # Isolate DB per test run
    from faro_api import config
    from faro_api.db import session as db_session

    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'test.sqlite3'}")
    config.get_settings.cache_clear()
    db_session._engine = None

    with TestClient(create_app()) as client:
        created = client.post("/portfolios", json={"name": "CRUD Test"})
        assert created.status_code == 201
        pid = created.json()["id"]

        pos = client.post(
            f"/portfolios/{pid}/positions",
            json={
                "ticker": "aapl",
                "shares": 10,
                "cost_basis": 150.5,
                "purchase_date": "2024-01-15",
            },
        )
        assert pos.status_code == 201
        assert pos.json()["ticker"] == "AAPL"  # normalized to uppercase
        pos_id = pos.json()["id"]

        updated = client.patch(
            f"/portfolios/{pid}/positions/{pos_id}",
            json={
                "ticker": "AAPL",
                "shares": 12,
                "cost_basis": 149.0,
                "purchase_date": "2024-01-15",
            },
        )
        assert updated.status_code == 200 and updated.json()["shares"] == 12

        renamed = client.patch(f"/portfolios/{pid}", json={"name": "Renamed"})
        assert renamed.json()["name"] == "Renamed"

        assert client.delete(f"/portfolios/{pid}/positions/{pos_id}").status_code == 204
        assert client.get(f"/portfolios/{pid}").json()["positions"] == []
        assert client.delete(f"/portfolios/{pid}").status_code == 204
        assert client.get(f"/portfolios/{pid}").status_code == 404

    config.get_settings.cache_clear()
    db_session._engine = None
