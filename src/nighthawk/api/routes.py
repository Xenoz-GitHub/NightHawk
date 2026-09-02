"""API v1 campaign routes. Handlers are thin — logic lives in services."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from nighthawk.api.deps import get_campaign_service
from nighthawk.api.schemas import (
    CampaignCreateRequest,
    CampaignResponse,
    ProgressResponse,
)
from nighthawk.models.core import Asset, Campaign, Finding
from nighthawk.services import CampaignService

router = APIRouter(prefix="/api/v1", tags=["campaigns"])


@router.post("/campaigns", status_code=201, response_model=CampaignResponse)
async def create_campaign(
    req: CampaignCreateRequest,
    service: CampaignService = Depends(get_campaign_service),
) -> CampaignResponse:
    """Create a campaign. Targets outside scope are rejected with 403."""
    campaign = service.create(req.name, targets=req.targets)
    return CampaignResponse.from_domain(campaign)


@router.get("/campaigns", response_model=list[CampaignResponse])
async def list_campaigns(
    service: CampaignService = Depends(get_campaign_service),
) -> list[CampaignResponse]:
    return [CampaignResponse.from_domain(c) for c in service.list()]


@router.get("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: UUID,
    service: CampaignService = Depends(get_campaign_service),
) -> CampaignResponse:
    return CampaignResponse.from_domain(service.get(campaign_id))


@router.post("/campaigns/{campaign_id}/start", response_model=CampaignResponse)
async def start_campaign(
    campaign_id: UUID,
    service: CampaignService = Depends(get_campaign_service),
) -> CampaignResponse:
    return CampaignResponse.from_domain(service.start(campaign_id))


@router.post("/campaigns/{campaign_id}/pause", response_model=CampaignResponse)
async def pause_campaign(
    campaign_id: UUID,
    service: CampaignService = Depends(get_campaign_service),
) -> CampaignResponse:
    return CampaignResponse.from_domain(service.pause(campaign_id))


@router.post("/campaigns/{campaign_id}/resume", response_model=CampaignResponse)
async def resume_campaign(
    campaign_id: UUID,
    service: CampaignService = Depends(get_campaign_service),
) -> CampaignResponse:
    return CampaignResponse.from_domain(service.resume(campaign_id))


@router.post("/campaigns/{campaign_id}/stop", response_model=CampaignResponse)
async def stop_campaign(
    campaign_id: UUID,
    service: CampaignService = Depends(get_campaign_service),
) -> CampaignResponse:
    return CampaignResponse.from_domain(service.stop(campaign_id))


@router.get("/campaigns/{campaign_id}/progress", response_model=ProgressResponse)
async def get_campaign_progress(
    campaign_id: UUID,
    service: CampaignService = Depends(get_campaign_service),
) -> ProgressResponse:
    progress = service.get_progress(campaign_id)
    return ProgressResponse(
        findings=progress["findings"],
        assets=progress["assets"],
        by_severity=progress["by_severity"],
        max_severity=progress["max_severity"],
    )


@router.get("/campaigns/{campaign_id}/graph")
async def get_campaign_graph(
    campaign_id: UUID,
    service: CampaignService = Depends(get_campaign_service),
) -> dict:
    """Attack-surface graph in cytoscape-compatible JSON."""
    service.get(campaign_id)  # raises CampaignNotFoundError → 404
    from nighthawk.database import engine as db_engine_mod
    from nighthawk.graph.builder import GraphBuilder
    with db_engine_mod.get_session() as session:
        return GraphBuilder(session).build(campaign_id).to_cytoscape_json()


@router.get("/campaigns/{campaign_id}/findings", response_model=list[Finding])
async def list_campaign_findings(
    campaign_id: UUID,
    service: CampaignService = Depends(get_campaign_service),
) -> list[Finding]:
    return service.list_findings(campaign_id)


@router.get("/campaigns/{campaign_id}/assets", response_model=list[Asset])
async def list_campaign_assets(
    campaign_id: UUID,
    service: CampaignService = Depends(get_campaign_service),
) -> list[Asset]:
    return service.list_assets(campaign_id)
