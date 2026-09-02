"""Domain ↔ ORM mappers.

Single location for converting between Pydantic domain models
(`nighthawk.models.core`) and SQLAlchemy rows (`nighthawk.database.models`).
No other module may hand-roll these conversions — this prevents competing
representations of the same entities.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from nighthawk.database.models import AssetDB, CampaignDB, EvidenceDB, FindingDB
from nighthawk.models.core import (
    Asset,
    Campaign,
    CampaignStatus,
    Evidence,
    Finding,
    Severity,
)


def _naive_to_utc(value: datetime | None) -> datetime | None:
    """SQLite returns naive datetimes; normalize to aware UTC for Pydantic."""
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def finding_db_to_domain(row: FindingDB) -> Finding:
    """Convert a FindingDB row to a domain Finding."""
    evidence = [
        Evidence(
            description=ev.description,
            source=ev.source,
            value=ev.value,
            timestamp=_naive_to_utc(ev.timestamp) or datetime.now(timezone.utc),
        )
        for ev in row.evidence
    ]
    return Finding(
        id=row.id,
        title=row.title,
        description=row.description,
        severity=Severity(row.severity.value if hasattr(row.severity, "value") else row.severity),
        confidence=row.confidence,
        category=row.category,
        asset_id=row.asset_id,
        evidence=evidence,
        remediation=row.remediation,
        references=list(row.references or []),
        created_at=_naive_to_utc(row.created_at) or datetime.now(timezone.utc),
        updated_at=_naive_to_utc(row.updated_at) or datetime.now(timezone.utc),
    )


def domain_to_finding_db(finding: Finding, campaign_id: Any = None) -> FindingDB:
    """Convert a domain Finding to a FindingDB row (evidence included)."""
    row = FindingDB(
        id=finding.id,
        campaign_id=campaign_id,
        title=finding.title,
        description=finding.description,
        severity=finding.severity,
        confidence=finding.confidence,
        category=finding.category,
        asset_id=str(finding.asset_id) if finding.asset_id else None,
        remediation=finding.remediation,
        references=list(finding.references),
    )
    row.evidence = [
        EvidenceDB(
            description=ev.description,
            source=ev.source,
            value=ev.value,
            timestamp=ev.timestamp,
        )
        for ev in finding.evidence
    ]
    return row


def asset_db_to_domain(row: AssetDB) -> Asset:
    """Convert an AssetDB row to a domain Asset."""
    return Asset(
        id=row.id,
        hostname=row.hostname,
        ip_addresses=list(row.ip_addresses or []),
        platform=row.platform or "unknown",
        os_name=row.os_name,
        os_version=row.os_version,
        services=list(row.services or []),
        technologies=list(row.technologies or []),
        metadata=dict(row.asset_metadata or {}),
        first_seen=_naive_to_utc(row.first_seen) or datetime.now(timezone.utc),
        last_seen=_naive_to_utc(row.last_seen) or datetime.now(timezone.utc),
    )


def domain_to_asset_db(asset: Asset, campaign_id: Any = None) -> AssetDB:
    """Convert a domain Asset to an AssetDB row."""
    return AssetDB(
        id=asset.id,
        campaign_id=campaign_id,
        hostname=asset.hostname,
        ip_addresses=list(asset.ip_addresses),
        platform=asset.platform,
        os_name=asset.os_name,
        os_version=asset.os_version,
        services=list(asset.services),
        technologies=list(asset.technologies),
        asset_metadata=dict(asset.metadata),
        first_seen=asset.first_seen,
        last_seen=asset.last_seen,
    )


def campaign_db_to_domain(row: CampaignDB) -> Campaign:
    """Convert a CampaignDB row to a domain Campaign."""
    return Campaign(
        id=row.id,
        name=row.name,
        scope_path=row.scope_path,
        status=CampaignStatus(row.status),
        targets=list(row.targets or []),
        error=row.error,
        created_at=_naive_to_utc(row.created_at) or datetime.now(timezone.utc),
        started_at=_naive_to_utc(row.started_at),
        completed_at=_naive_to_utc(row.completed_at),
        event_seq=row.event_seq or 0,
    )