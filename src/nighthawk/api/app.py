"""FastAPI application factory with real persistence and event streaming."""

from __future__ import annotations

from typing import Any

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from nighthawk import __version__
from nighthawk.api.auth import require_auth
from nighthawk.api.errors import register_error_handlers
from nighthawk.api.routes import router as campaign_router
from nighthawk.api.ws import router as ws_router
from nighthawk.config.config import get_config
from nighthawk.logging.setup import configure_logging

configure_logging()


def create_app() -> FastAPI:
    """Build the application from the current configuration."""
    config = get_config()

    app = FastAPI(
        title="NIGHTHAWK API",
        description="Authorized red-team reconnaissance and assessment API",
        version=__version__,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Optional CORS allow-list (comma-separated NIGHTHAWK_CORS_ORIGINS).
    if config.cors_origins:
        origins = [o.strip() for o in config.cors_origins.split(",") if o.strip()]
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Bearer-token auth guards every API v1 route (no-op when no token set).
    app.include_router(
        campaign_router, dependencies=[Depends(require_auth)],
    )
    app.include_router(ws_router)
    register_error_handlers(app)

    @app.get("/health")
    async def health() -> dict[str, Any]:
        return {"status": "ok", "service": "nighthawk", "version": __version__}

    @app.get("/")
    async def root() -> dict[str, Any]:
        return {
            "service": "NIGHTHAWK",
            "version": __version__,
            "description": "Ethical red-team reconnaissance and attack-surface assessment platform.",
            "docs": "/docs",
        }

    return app


app = create_app()

