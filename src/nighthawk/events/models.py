"""Normalized event model for the NIGHTHAWK platform.

All events share a common envelope so the frontend can render one stream
regardless of origin (campaign lifecycle, discovery, findings, graph, errors).
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class EventType(str, Enum):
    """Canonical event types (dot-notation for frontend filtering)."""

    # Campaign lifecycle
    CAMPAIGN_CREATED = "campaign.created"
    CAMPAIGN_QUEUED = "campaign.queued"
    CAMPAIGN_STARTED = "campaign.started"
    CAMPAIGN_PAUSED = "campaign.paused"
    CAMPAIGN_RESUMED = "campaign.resumed"
    CAMPAIGN_STOPPED = "campaign.stopped"
    CAMPAIGN_COMPLETED = "campaign.completed"
    CAMPAIGN_FAILED = "campaign.failed"
    CAMPAIGN_CANCELLED = "campaign.cancelled"
    CAMPAIGN_PROGRESS = "campaign.progress"
    # Discovery
    DISCOVERY_ASSET = "discovery.asset"
    DISCOVERY_SERVICE = "discovery.service"
    # Findings
    FINDING_CREATED = "finding.created"
    # Graph
    GRAPH_UPDATED = "graph.updated"
    # Errors
    SCAN_ERROR = "scan.error"
    # Completion marker
    CAMPAIGN_DONE = "campaign.done"


class Event(BaseModel):
    """Normalized event envelope.

    `seq` is a per-campaign monotonic counter assigned by the persistence
    layer, letting clients detect gaps after a reconnect.
    """

    type: EventType
    campaign_id: UUID
    seq: int = Field(default=0, ge=0)
    timestamp: datetime = Field(default_factory=_utcnow)
    message: str = ""
    severity: str = "info"  # info | warning | error
    payload: dict[str, Any] = Field(default_factory=dict)

    def to_ws_dict(self) -> dict[str, Any]:
        """JSON-safe dict for WebSocket transport."""
        return {
            "type": self.type.value,
            "campaign_id": str(self.campaign_id),
            "seq": self.seq,
            "timestamp": self.timestamp.isoformat(),
            "message": self.message,
            "severity": self.severity,
            "payload": self.payload,
        }


def lifecycle_event(
    event_type: EventType,
    campaign_id: UUID,
    seq: int,
    message: str = "",
    payload: dict[str, Any] | None = None,
) -> Event:
    """Build a lifecycle event with consistent severity/message defaults."""
    return Event(
        type=event_type,
        campaign_id=campaign_id,
        seq=seq,
        message=message or event_type.value,
        payload=payload or {},
    )