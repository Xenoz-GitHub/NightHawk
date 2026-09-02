"""Campaign service: lifecycle, persistence, scope validation, events.

Phase 1 backend. The CLI retains full local functionality; this service
exposes the same domain logic through a session-based API. All campaign
state transitions, persistence, and event emission live here — API routes
stay thin.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from nighthawk.config.config import get_config
from nighthawk.core.exceptions import (
    CampaignNotFoundError,
    DuplicateCampaignError,
    InvalidStateTransitionError,
    ScopeViolationError,
    ValidationError,
)
from nighthawk.database import engine as db_engine_mod
from nighthawk.database.models import AssetDB, CampaignDB, FindingDB, ScanResultDB
from nighthawk.events import HUB, Event, EventType, lifecycle_event
from nighthawk.logging.setup import get_logger
from nighthawk.models.core import Asset, Campaign, CampaignStatus, Finding, Severity
from nighthawk.scope.manager import ScopeManager
from nighthawk.services.mappers import (
    asset_db_to_domain,
    campaign_db_to_domain,
    domain_to_asset_db,
    domain_to_finding_db,
    finding_db_to_domain,
)

logger = get_logger("campaign_service")

# Allowed lifecycle transitions (terminal states have no outgoing edges).
_ALLOWED_TRANSITIONS: dict[CampaignStatus, set[CampaignStatus]] = {
    CampaignStatus.CREATED: {
        CampaignStatus.QUEUED, CampaignStatus.RUNNING, CampaignStatus.CANCELLED,
    },
    CampaignStatus.QUEUED: {CampaignStatus.RUNNING, CampaignStatus.CANCELLED},
    CampaignStatus.RUNNING: {
        CampaignStatus.PAUSED, CampaignStatus.COMPLETED,
        CampaignStatus.FAILED, CampaignStatus.CANCELLED,
    },
    CampaignStatus.PAUSED: {CampaignStatus.RUNNING, CampaignStatus.CANCELLED},
    CampaignStatus.COMPLETED: set(),
    CampaignStatus.FAILED: set(),
    CampaignStatus.CANCELLED: set(),
}

_SEVERITY_ORDER: dict[Severity, int] = {
    Severity.INFO: 0,
    Severity.LOW: 1,
    Severity.MEDIUM: 2,
    Severity.HIGH: 3,
    Severity.CRITICAL: 4,
}


class CampaignService:
    """Owns campaign lifecycle, persistence, and event fan-out."""

    def __init__(self, scope_path: str | None = None) -> None:
        cfg = get_config()
        self.scope = ScopeManager(scope_path or cfg.default_scope_path)
        # Bootstrap tables (no-op when they already exist).
        db_engine_mod.create_all()

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    def _get_row(self, session: Session, campaign_id: UUID) -> CampaignDB:
        row = session.get(CampaignDB, campaign_id)
        if row is None:
            raise CampaignNotFoundError(str(campaign_id))
        return row

    def _transition(self, row: CampaignDB, new_status: CampaignStatus) -> None:
        current = CampaignStatus(row.status)
        if new_status == current:
            return
        if new_status not in _ALLOWED_TRANSITIONS.get(current, set()):
            raise InvalidStateTransitionError(current.value, new_status.value)
        row.status = new_status.value

    def _publish(self, campaign_id: str, event: Event) -> None:
        HUB.publish(campaign_id, event)

    def _emit_lifecycle(
        self, campaign_id: UUID, event_type: EventType, seq: int,
        message: str = "", payload: dict[str, Any] | None = None,
    ) -> None:
        self._publish(
            str(campaign_id),
            lifecycle_event(event_type, campaign_id, seq, message, payload),
        )

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #

    def create(self, name: str, targets: list[str] | None = None) -> Campaign:
        """Create a campaign, validating every target against scope."""
        if not name or not name.strip():
            raise ValidationError("Campaign name must not be empty.")
        targets = [t.strip() for t in (targets or []) if t and t.strip()]
        for target in targets:
            try:
                self.scope.validate_target(target)
            except ScopeViolationError:
                logger.warning("campaign_target_rejected", target=target)
                raise

        with db_engine_mod.get_session() as session:
            name_clean = name.strip()
            existing = session.execute(
                select(CampaignDB).where(CampaignDB.name == name_clean)
            ).scalar_one_or_none()
            if existing is not None:
                raise DuplicateCampaignError(name_clean)
            row = CampaignDB(
                name=name_clean,
                scope_path=str(self.scope.config_path),
                status=CampaignStatus.CREATED.value,
                targets=targets,
            )
            session.add(row)
            session.flush()
            seq = row.touch_seq()
            session.commit()
            campaign = campaign_db_to_domain(row)
        self._emit_lifecycle(
            campaign.id, EventType.CAMPAIGN_CREATED, seq,
            payload={"name": campaign.name, "targets": targets},
        )
        return campaign

    def get(self, campaign_id: UUID) -> Campaign:
        with db_engine_mod.get_session() as session:
            return campaign_db_to_domain(self._get_row(session, campaign_id))

    def list(self) -> list[Campaign]:
        with db_engine_mod.get_session() as session:
            rows = session.scalars(
                select(CampaignDB).order_by(CampaignDB.created_at.desc())
            ).all()
            return [campaign_db_to_domain(r) for r in rows]

    def start(self, campaign_id: UUID) -> Campaign:
        """created/queued → running (emits queued + started events)."""
        with db_engine_mod.get_session() as session:
            row = self._get_row(session, campaign_id)
            current = CampaignStatus(row.status)
            if current not in (CampaignStatus.CREATED, CampaignStatus.QUEUED):
                raise InvalidStateTransitionError(current.value, "running")
            seq_events: list[tuple[EventType, int]] = []
            if current is CampaignStatus.CREATED:
                self._transition(row, CampaignStatus.QUEUED)
                session.flush()
                seq_events.append((EventType.CAMPAIGN_QUEUED, row.touch_seq()))
            self._transition(row, CampaignStatus.RUNNING)
            row.started_at = row.started_at or datetime.now(timezone.utc)
            session.flush()
            seq_events.append((EventType.CAMPAIGN_STARTED, row.touch_seq()))
            session.commit()
            campaign = campaign_db_to_domain(row)
        for event_type, seq in seq_events:
            self._emit_lifecycle(campaign_id, event_type, seq)
        return campaign

    def pause(self, campaign_id: UUID) -> Campaign:
        """running → paused; idempotent when already paused."""
        with db_engine_mod.get_session() as session:
            row = self._get_row(session, campaign_id)
            if CampaignStatus(row.status) is CampaignStatus.PAUSED:
                return campaign_db_to_domain(row)
            self._transition(row, CampaignStatus.PAUSED)
            session.flush()
            seq = row.touch_seq()
            session.commit()
            campaign = campaign_db_to_domain(row)
        self._emit_lifecycle(campaign_id, EventType.CAMPAIGN_PAUSED, seq)
        return campaign

    def resume(self, campaign_id: UUID) -> Campaign:
        """paused → running; idempotent when already running."""
        with db_engine_mod.get_session() as session:
            row = self._get_row(session, campaign_id)
            if CampaignStatus(row.status) is CampaignStatus.RUNNING:
                return campaign_db_to_domain(row)
            self._transition(row, CampaignStatus.RUNNING)
            session.flush()
            seq = row.touch_seq()
            session.commit()
            campaign = campaign_db_to_domain(row)
        self._emit_lifecycle(campaign_id, EventType.CAMPAIGN_RESUMED, seq)
        return campaign

    def stop(self, campaign_id: UUID) -> Campaign:
        """Cancel an active campaign; idempotent when already cancelled."""
        with db_engine_mod.get_session() as session:
            row = self._get_row(session, campaign_id)
            current = CampaignStatus(row.status)
            if current is CampaignStatus.CANCELLED:
                return campaign_db_to_domain(row)
            if current in (CampaignStatus.COMPLETED, CampaignStatus.FAILED):
                raise InvalidStateTransitionError(current.value, "cancelled")
            self._transition(row, CampaignStatus.CANCELLED)
            row.completed_at = datetime.now(timezone.utc)
            session.flush()
            seq = row.touch_seq()
            session.commit()
            campaign = campaign_db_to_domain(row)
        self._emit_lifecycle(campaign_id, EventType.CAMPAIGN_CANCELLED, seq)
        return campaign

    def complete(self, campaign_id: UUID, error: str | None = None) -> Campaign:
        """running → completed (or failed when error is provided)."""
        target = CampaignStatus.FAILED if error else CampaignStatus.COMPLETED
        with db_engine_mod.get_session() as session:
            row = self._get_row(session, campaign_id)
            self._transition(row, target)
            row.error = error
            row.completed_at = datetime.now(timezone.utc)
            session.flush()
            seq = row.touch_seq()
            session.commit()
            campaign = campaign_db_to_domain(row)
        event_type = EventType.CAMPAIGN_FAILED if error else EventType.CAMPAIGN_COMPLETED
        self._emit_lifecycle(campaign_id, event_type, seq, message=error or "")
        return campaign

    # ------------------------------------------------------------------ #
    # Data intake
    # ------------------------------------------------------------------ #

    def add_finding(self, campaign_id: UUID, finding: Finding) -> Finding:
        """Persist a finding under a campaign and emit finding.created."""
        with db_engine_mod.get_session() as session:
            row = self._get_row(session, campaign_id)
            if CampaignStatus(row.status) not in (
                CampaignStatus.RUNNING, CampaignStatus.PAUSED,
            ):
                raise InvalidStateTransitionError(
                    row.status, "add_finding (campaign not active)"
                )
            finding_row = domain_to_finding_db(finding, campaign_id=campaign_id)
            session.add(finding_row)
            session.flush()
            seq = row.touch_seq()
            session.commit()
            finding_id = finding_row.id
        self._publish(
            str(campaign_id),
            Event(
                type=EventType.FINDING_CREATED,
                campaign_id=campaign_id,
                seq=seq,
                message=finding.title,
                severity=finding.severity.value.lower(),
                payload={
                    "finding_id": str(finding_id),
                    "title": finding.title,
                    "severity": finding.severity.value,
                    "category": finding.category,
                    "confidence": finding.confidence,
                },
            ),
        )
        return finding

    def add_asset(self, campaign_id: UUID, asset: Asset) -> Asset:
        """Persist an asset under a campaign and emit discovery.asset."""
        with db_engine_mod.get_session() as session:
            row = self._get_row(session, campaign_id)
            asset_row = domain_to_asset_db(asset, campaign_id=campaign_id)
            session.add(asset_row)
            session.flush()
            seq = row.touch_seq()
            session.commit()
            stored = asset_db_to_domain(asset_row)
        self._publish(
            str(campaign_id),
            Event(
                type=EventType.DISCOVERY_ASSET,
                campaign_id=campaign_id,
                seq=seq,
                message=asset.hostname or str(asset.id),
                payload={
                    "asset_id": str(asset.id),
                    "hostname": asset.hostname,
                    "platform": asset.platform,
                },
            ),
        )
        return stored

    def record_scan_result(
        self, campaign_id: UUID, module: str, target: str, result: dict[str, Any],
    ) -> None:
        """Persist a raw scanner result (audit trail), no event emitted."""
        with db_engine_mod.get_session() as session:
            self._get_row(session, campaign_id)
            session.add(
                ScanResultDB(
                    campaign_id=campaign_id, module=module,
                    target=target, result_json=result,
                )
            )
            session.commit()

    # ------------------------------------------------------------------ #
    # Queries
    # ------------------------------------------------------------------ #

    def list_findings(self, campaign_id: UUID) -> list[Finding]:
        with db_engine_mod.get_session() as session:
            self._get_row(session, campaign_id)
            rows = session.scalars(
                select(FindingDB)
                .where(FindingDB.campaign_id == campaign_id)
                .order_by(FindingDB.created_at.desc())
            ).all()
            return [finding_db_to_domain(r) for r in rows]

    def list_assets(self, campaign_id: UUID) -> list[Asset]:
        with db_engine_mod.get_session() as session:
            self._get_row(session, campaign_id)
            rows = session.scalars(
                select(AssetDB)
                .where(AssetDB.campaign_id == campaign_id)
                .order_by(AssetDB.first_seen.desc())
            ).all()
            return [asset_db_to_domain(r) for r in rows]

    def get_progress(self, campaign_id: UUID) -> dict[str, Any]:
        """Summary counters for dashboards."""
        findings = self.list_findings(campaign_id)
        severity_counts: dict[str, int] = {}
        for f in findings:
            key = f.severity.value.lower()
            severity_counts[key] = severity_counts.get(key, 0) + 1
        max_severity = max(
            (f.severity for f in findings),
            key=lambda s: _SEVERITY_ORDER.get(s, -1),
            default=None,
        )
        return {
            "findings": len(findings),
            "assets": len(self.list_assets(campaign_id)),
            "by_severity": {
                "critical": severity_counts.get("critical", 0),
                "high": severity_counts.get("high", 0),
                "medium": severity_counts.get("medium", 0),
                "low": severity_counts.get("low", 0),
                "info": severity_counts.get("info", 0),
            },
            "max_severity": max_severity.value if max_severity else None,
        }
