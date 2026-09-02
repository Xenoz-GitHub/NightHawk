"""Shared fixtures for integration tests: isolated temp-database API client."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def api_client(tmp_path, monkeypatch):
    """TestClient bound to a throwaway SQLite database per test."""
    db_path = tmp_path / "nighthawk-test.db"
    monkeypatch.setenv("NIGHTHAWK_DATABASE_URL", f"sqlite:///{db_path.as_posix()}")

    import nighthawk.config.config as config_mod
    from nighthawk.database import engine as db_engine_mod
    from nighthawk.api import deps

    # Force config re-read so the temp database URL is picked up.
    monkeypatch.setattr(config_mod, "_CONFIG_INSTANCE", None)
    db_engine_mod.reset_engine()
    deps.reset_services()

    from nighthawk.api.app import app

    with TestClient(app) as client:
        yield client
    db_engine_mod.reset_engine()
