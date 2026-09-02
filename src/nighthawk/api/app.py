"""FastAPI application and routes."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Any
from datetime import datetime, timezone
from uuid import uuid4

from nighthawk import __version__
from nighthawk.config.config import get_config

app = FastAPI(
    title="NIGHTHAWK API",
    description="Authorized red-team reconnaissance and assessment API",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)


class CampaignCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    scope_path: str | None = None


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


@app.post("/api/v1/campaigns")
async def create_campaign(req: CampaignCreateRequest) -> dict[str, Any]:
    return {
        "id": str(uuid4()),
        "name": req.name,
        "scope_path": req.scope_path,
        "status": "created",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/v1/campaigns/{id}")
async def get_campaign(id: str) -> dict[str, Any]:
    return {
        "id": id,
        "status": "running",
        "findings_count": 0,
        "assets_count": 0,
    }


@app.get("/api/v1/findings")
async def list_findings() -> list[dict[str, Any]]:
    return []


@app.get("/api/v1/assets")
async def list_assets() -> list[dict[str, Any]]:
    return []


@app.get("/api/v1/graph")
async def get_graph() -> dict[str, Any]:
    return {"nodes": [], "edges": [], "message": "Graph data requires assessment data."}
