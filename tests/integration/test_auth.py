"""Bearer-token auth: opt-in, guards /api/v1, structured 401s."""

import pytest
from fastapi.testclient import TestClient


def _auth_client(token: str, tmp_path, monkeypatch):
    db_path = tmp_path / "auth-test.db"
    monkeypatch.setenv("NIGHTHAWK_DATABASE_URL", f"sqlite:///{db_path.as_posix()}")
    monkeypatch.setenv("NIGHTHAWK_API_TOKEN", token)

    import nighthawk.config.config as config_mod
    from nighthawk.database import engine as db_engine_mod
    from nighthawk.api import deps

    monkeypatch.setattr(config_mod, "_CONFIG_INSTANCE", None)
    db_engine_mod.reset_engine()
    deps.reset_services()

    from nighthawk.api.app import create_app

    return TestClient(create_app())


class TestAuthEnabled:
    @pytest.fixture()
    def client(self, tmp_path, monkeypatch):
        return _auth_client("super-secret-token", tmp_path, monkeypatch)

    def test_missing_token_401(self, client):
        resp = client.get("/api/v1/campaigns")
        assert resp.status_code == 401
        body = resp.json()
        assert body["error"] == "http_error"
        assert "token" in body["detail"].lower()

    def test_wrong_token_401(self, client):
        resp = client.get(
            "/api/v1/campaigns",
            headers={"Authorization": "Bearer not-the-token"},
        )
        assert resp.status_code == 401

    def test_valid_token_allowed(self, client):
        resp = client.get(
            "/api/v1/campaigns",
            headers={"Authorization": "Bearer super-secret-token"},
        )
        assert resp.status_code == 200
        assert resp.json() == []

    def test_health_is_not_guarded(self, client):
        assert client.get("/health").status_code == 200


class TestAuthDisabled:
    def test_no_token_required_by_default(self, tmp_path, monkeypatch):
        client = _auth_client("", tmp_path, monkeypatch)
        assert client.get("/api/v1/campaigns").status_code == 200