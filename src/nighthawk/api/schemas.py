"""Pydantic request/response schemas and structured error envelope."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from nighthawk.models.core import Campaign


class CampaignCreateRequest(BaseModel):
    """POST /api/v1/campaigns request body."""

    name: str = Field(..., min_length=1, max_length=128)
    targets: list[str] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    """Structured error envelope returned by every error path."""

    error: str
    detail: str | None = None
    target: str | None = None
    current_state: str | None = None
    requested_state: str | None = None


class ProgressResponse(BaseModel):
    findings: int
    assets: int
    by_severity: dict[str, int]
    max_severity: str | None


class CampaignResponse(BaseModel):
    """Campaign representation returned by lifecycle endpoints."""

    id: UUID
    name: str
    scope_path: str | None
    status: str
    targets: list[str]
    error: str | None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    event_seq: int

    @classmethod
    def from_domain(cls, campaign: Campaign) -> "CampaignResponse":
        return cls(
            id=campaign.id,
            name=campaign.name,
            scope_path=campaign.scope_path,
            status=campaign.status.value,
            targets=campaign.targets,
            error=campaign.error,
            created_at=campaign.created_at,
            started_at=campaign.started_at,
            completed_at=campaign.completed_at,
            event_seq=campaign.event_seq,
        )
