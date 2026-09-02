"""FastAPI application factory with real persistence and event streaming."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI

from nighthawk import __version__
from nighthawk.api.errors import register_error_handlers
from nighthawk.api.routes import router as campaign_router
from nighthawk.api.ws import router as ws_router
from nighthawk.logging.setup import configure_logging

configure_logging()

app = FastAPI(
    title="NIGHTHAWK API",
    description="Authorized red-team reconnaissance and assessment API",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(campaign_router)
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

