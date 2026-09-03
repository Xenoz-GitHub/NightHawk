"""Deterministic, non-executing red-team attack-path plans."""

from __future__ import annotations

from nighthawk.redteam.models import AttackStep, RedTeamObjective


_COMMON_RECON = AttackStep(
    "recon", "reconnaissance", RedTeamObjective.RECON,
    "asset-discovery", "Enumerate only approved domains, hosts, and services.",
)

_PLANS: dict[RedTeamObjective, tuple[AttackStep, ...]] = {
    RedTeamObjective.RECON: (_COMMON_RECON,),
    RedTeamObjective.INITIAL_ACCESS: (
        _COMMON_RECON,
        AttackStep("exposure", "initial-access", RedTeamObjective.INITIAL_ACCESS,
                   "exposure-validation", "Validate an identified exposure without exploitation.", ("recon",)),
        AttackStep("proof", "evidence", RedTeamObjective.EVIDENCE_COLLECTION,
                   "evidence-capture", "Capture redacted, reproducible proof of the finding.", ("exposure",)),
    ),
    RedTeamObjective.CREDENTIAL_AUDIT: (
        _COMMON_RECON,
        AttackStep("secret-audit", "credential-access", RedTeamObjective.CREDENTIAL_AUDIT,
                   "credential-audit", "Search approved repositories and systems for exposed secrets; never test them against third parties.", ("recon",)),
        AttackStep("proof", "evidence", RedTeamObjective.EVIDENCE_COLLECTION,
                   "evidence-capture", "Redact and hash evidence before storage.", ("secret-audit",)),
    ),
    RedTeamObjective.PRIVILEGE_ESCALATION: (
        _COMMON_RECON,
        AttackStep("config-audit", "privilege-escalation", RedTeamObjective.PRIVILEGE_ESCALATION,
                   "configuration-audit", "Review authorized host configuration for excessive privileges.", ("recon",)),
        AttackStep("proof", "evidence", RedTeamObjective.EVIDENCE_COLLECTION,
                   "evidence-capture", "Record the permission path and remediation evidence.", ("config-audit",)),
    ),
    RedTeamObjective.LATERAL_MOVEMENT: (
        _COMMON_RECON,
        AttackStep("path-map", "discovery", RedTeamObjective.LATERAL_MOVEMENT,
                   "trust-mapping", "Map approved network and identity relationships without authenticating to new systems.", ("recon",)),
        AttackStep("path-proof", "evidence", RedTeamObjective.EVIDENCE_COLLECTION,
                   "attack-path-evidence", "Document the reachable path and required control points.", ("path-map",)),
    ),
    RedTeamObjective.DETECTION_VALIDATION: (
        _COMMON_RECON,
        AttackStep("canary", "detection", RedTeamObjective.DETECTION_VALIDATION,
                   "canary-event", "Emit a harmless, uniquely tagged test event in the approved environment.", ("recon",)),
        AttackStep("review", "detection", RedTeamObjective.DETECTION_VALIDATION,
                   "alert-review", "Compare telemetry and alert timing against the expected control.", ("canary",)),
    ),
    RedTeamObjective.EXFILTRATION_SIMULATION: (
        _COMMON_RECON,
        AttackStep("stage", "collection", RedTeamObjective.EXFILTRATION_SIMULATION,
                   "canary-staging", "Stage synthetic canary data only; do not copy real sensitive data.", ("recon",)),
        AttackStep("egress", "exfiltration-simulation", RedTeamObjective.EXFILTRATION_SIMULATION,
                   "egress-control-test", "Test approved egress monitoring with a harmless canary payload.", ("stage",)),
    ),
    RedTeamObjective.EVIDENCE_COLLECTION: (
        _COMMON_RECON,
        AttackStep("proof", "evidence", RedTeamObjective.EVIDENCE_COLLECTION,
                   "evidence-capture", "Capture redacted, reproducible proof with source and timestamp.", ("recon",)),
    ),
}


def build_attack_path(objective: RedTeamObjective) -> tuple[AttackStep, ...]:
    """Return the deterministic plan for an objective."""
    return _PLANS[objective]
