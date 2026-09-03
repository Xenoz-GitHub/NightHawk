"""Typed models for authorized red-team missions.

These models describe work and evidence; they do not execute network actions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ExecutionMode(str, Enum):
    SIMULATION = "simulation"
    VALIDATE = "validate"
    AUTHORIZED_ACTIVE = "authorized-active"

    @property
    def requires_authorization(self) -> bool:
        return self is not ExecutionMode.SIMULATION


class RedTeamObjective(str, Enum):
    RECON = "recon"
    INITIAL_ACCESS = "initial-access"
    CREDENTIAL_AUDIT = "credential-audit"
    PRIVILEGE_ESCALATION = "privilege-escalation"
    LATERAL_MOVEMENT = "lateral-movement"
    DETECTION_VALIDATION = "detection-validation"
    EXFILTRATION_SIMULATION = "exfiltration-simulation"
    EVIDENCE_COLLECTION = "evidence-collection"


@dataclass(frozen=True)
class AttackStep:
    """A safe, auditable step in an attack-path plan."""

    id: str
    phase: str
    objective: RedTeamObjective
    technique: str
    safe_action: str
    requires: tuple[str, ...] = ()
    destructive: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "phase": self.phase,
            "objective": self.objective.value,
            "technique": self.technique,
            "safe_action": self.safe_action,
            "requires": list(self.requires),
            "destructive": self.destructive,
        }


@dataclass
class RedTeamMission:
    """A persisted red-team objective and its authorization context."""

    title: str
    objective: RedTeamObjective
    mode: ExecutionMode = ExecutionMode.SIMULATION
    targets: list[str] = field(default_factory=list)
    authorization_ref: str | None = None
    notes: str = ""

    def validate(self) -> None:
        if not self.title.strip():
            raise ValueError("Mission title must not be empty.")
        if self.mode.requires_authorization and not (
            self.authorization_ref and self.authorization_ref.strip()
        ):
            raise ValueError(
                f"Mode '{self.mode.value}' requires --authorization-ref."
            )
        if self.mode is ExecutionMode.AUTHORIZED_ACTIVE and not self.targets:
            raise ValueError(
                "authorized-active mode requires at least one --target."
            )
        if any(not target.strip() for target in self.targets):
            raise ValueError("Targets must not be empty.")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "title": self.title.strip(),
            "objective": self.objective.value,
            "mode": self.mode.value,
            "targets": [target.strip() for target in self.targets],
            "authorization_ref": self.authorization_ref,
            "notes": self.notes.strip(),
        }
