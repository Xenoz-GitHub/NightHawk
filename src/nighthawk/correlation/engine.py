"""Finding correlation engine."""

from typing import Any
from collections import defaultdict

from nighthawk.logging.setup import get_logger
from nighthawk.models.core import Finding

logger = get_logger("correlation")


class CorrelationEngine:
    """Correlates findings into attack-surface relationships."""

    def __init__(self) -> None:
        pass

    def correlate(self, findings: list[Finding]) -> list[dict[str, Any]]:
        """Build correlation groups based on asset, domain, technology, and temporal proximity."""
        groups = defaultdict(lambda: {
            "assets": set(),
            "domains": set(),
            "technologies": set(),
            "findings": [],
        })
        for finding in findings:
            key = finding.asset_id or finding.category
            group = groups[str(key)]
            group["findings"].append(finding)
            # Derive relationships from evidence
            for ev in finding.evidence:
                desc = ev.description.lower()
                if "domain" in desc or "host" in desc:
                    words = desc.split()
                    for w in words:
                        if "." in w and len(w) > 3:
                            group["domains"].add(w)
            # Technology correlation via category
            group["technologies"].add(finding.category)
        results = []
        for group_key, group in groups.items():
            results.append({
                "group_id": group_key,
                "assets": list(group["assets"]),
                "domains": list(group["domains"]),
                "technologies": list(group["technologies"]),
                "related_findings_count": len(group["findings"]),
                "findings_ids": [str(f.id) for f in group["findings"]],
            })
        return results
