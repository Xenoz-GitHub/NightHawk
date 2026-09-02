"""FastAPI dependency wiring: services and event hub."""

from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy.orm import Session

from nighthawk.database import engine as db_engine_mod
from nighthawk.events import EventHub, HUB
from nighthawk.services import CampaignService

_service: CampaignService | None = None


def get_campaign_service() -> CampaignService:
    """Process-wide CampaignService (creates tables on first use)."""
    global _service
    if _service is None:
        _service = CampaignService()
    return _service


def get_session() -> Iterator[Session]:
    """Yield a database session, always closing it afterwards."""
    session = db_engine_mod.get_session()
    try:
        yield session
    finally:
        session.close()


def get_event_hub() -> EventHub:
    """Process-wide event hub."""
    return HUB


def reset_services() -> None:
    """Drop cached service (used by tests to rebind to a temp database)."""
    global _service
    _service = None
