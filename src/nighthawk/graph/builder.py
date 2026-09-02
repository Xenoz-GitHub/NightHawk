"""Build the attack-surface graph from persisted campaign rows.

Single source of truth for graph topology: asset → services/technologies,
asset → findings. Node ids are stable (`asset:<uuid>`, `service:<asset>:<name>`,
`technology:<name>`, `finding:<uuid>`) so clients can diff graphs across
polls and correlate `graph.updated` events.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from nighthawk.database.models import AssetDB, FindingDB
from nighthawk.graph.graph import AttackSurfaceGraph


def _asset_node_id(asset_id: UUID) -> str:
    return f"asset:{asset_id}"


def _finding_node_id(finding_id: UUID) -> str:
    return f"finding:{finding_id}"


class GraphBuilder:
    """Builds an :class:`AttackSurfaceGraph` for one campaign."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def build(self, campaign_id: UUID) -> AttackSurfaceGraph:
        graph = AttackSurfaceGraph()

        assets = (
            self._session.query(AssetDB)
            .filter(AssetDB.campaign_id == campaign_id)
            .all()
        )
        findings = (
            self._session.query(FindingDB)
            .filter(FindingDB.campaign_id == campaign_id)
            .all()
        )

        for asset in assets:
            node_id = _asset_node_id(asset.id)
            graph.add_node(
                "asset",
                node_id,
                label=asset.hostname or str(asset.id),
                platform=asset.platform,
                ip_addresses=list(asset.ip_addresses or []),
                first_seen=asset.first_seen.isoformat() if asset.first_seen else None,
                last_seen=asset.last_seen.isoformat() if asset.last_seen else None,
            )
            for service in asset.services or []:
                service_id = f"service:{asset.id}:{service}"
                graph.add_node("service", service_id, label=service)
                graph.add_edge(node_id, service_id, "has_service")
            for technology in asset.technologies or []:
                tech_id = f"technology:{technology}"
                graph.add_node("technology", tech_id, label=technology)
                graph.add_edge(node_id, tech_id, "runs")

        for finding in findings:
            finding_id = _finding_node_id(finding.id)
            graph.add_node(
                "finding",
                finding_id,
                label=finding.title,
                severity=finding.severity.value if finding.severity else None,
                category=finding.category,
            )
            if finding.asset_id:
                graph.add_edge(_asset_node_id(finding.asset_id), finding_id, "affects")

        return graph
