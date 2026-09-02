"""Transparent risk scoring engine."""

from typing import Any

from nighthawk.logging.setup import get_logger
from nighthawk.models.core import Finding, Severity

logger = get_logger("analysis")


class RiskEngine:
    """Calculate explainable risk scores from findings."""

    SEVERITY_MAP = {
        Severity.INFO: 10,
        Severity.LOW: 25,
        Severity.MEDIUM: 45,
        Severity.HIGH: 75,
        Severity.CRITICAL: 95,
    }

    def score_finding(self, finding: Finding) -> int:
        base = self.SEVERITY_MAP.get(finding.severity, 30)
        confidence_factor = finding.confidence * 15
        explanation = f"Base severity ({finding.severity.value}): {base}; Confidence ({finding.confidence}): +{confidence_factor:.1f}"
        score = min(100, int(base + confidence_factor))
        return score

    def explain_score(self, finding: Finding) -> dict[str, Any]:
        score = self.score_finding(finding)
        return {
            "finding_title": finding.title,
            "risk_score": score,
            "factors": {
                "severity": finding.severity.value,
                "confidence": finding.confidence,
                "evidence_count": len(finding.evidence),
            },
            "explanation": f"Risk {score}/100 — Severity: {finding.severity.value}, Confidence: {finding.confidence}, Evidence count: {len(finding.evidence)}",
        }
