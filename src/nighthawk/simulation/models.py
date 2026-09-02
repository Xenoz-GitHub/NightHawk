"""Synthetic simulation domain models.

Pure dataclasses and enums — no I/O, no frameworks, no external services.
The simulation is an offline, deterministic game world; nothing here may
import networking, database, or API machinery (enforced by tests).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from nighthawk.models.core import Severity


class SimulationError(Exception):
    """Base class for simulation failures."""


class InvalidActionError(SimulationError):
    """Raised for actions that are illegal right now. Never mutates state."""


class ScenarioError(SimulationError):
    """Raised for unknown scenario archetypes or malformed scenarios."""


class InformationState(str, Enum):
    """Fog-of-war knowledge level for world entities."""

    UNKNOWN = "unknown"
    OBSERVED = "observed"
    PROBABLE = "probable"
    CONFIRMED = "confirmed"

    @property
    def rank(self) -> int:
        return _INFO_RANK[self]

    def at_least(self, other: "InformationState") -> bool:
        return self.rank >= other.rank


_INFO_RANK = {
    InformationState.UNKNOWN: 0,
    InformationState.OBSERVED: 1,
    InformationState.PROBABLE: 2,
    InformationState.CONFIRMED: 3,
}


class HostRole(str, Enum):
    WORKSTATION = "workstation"
    SERVER = "server"
    NETWORK_DEVICE = "network_device"
    IOT = "iot"
    CLOUD_ENDPOINT = "cloud_endpoint"


class ServiceKind(str, Enum):
    HTTP = "http"
    HTTPS = "https"
    SSH = "ssh"
    SMB = "smb"
    RDP = "rdp"
    DNS = "dns"
    DATABASE = "database"
    API = "api"
    VPN = "vpn"
    EMAIL = "email"


class ActionKind(str, Enum):
    DISCOVER = "discover"
    INSPECT = "inspect"
    ENUMERATE = "enumerate"
    FINGERPRINT = "fingerprint"
    ANALYZE = "analyze"
    COLLECT_EVIDENCE = "collect_evidence"
    MOVE_TO = "move_to"
    INVESTIGATE = "investigate"
    CONTAIN = "contain"
    MONITOR = "monitor"


ATTACKER_ACTIONS = frozenset(
    {
        ActionKind.DISCOVER,
        ActionKind.INSPECT,
        ActionKind.ENUMERATE,
        ActionKind.FINGERPRINT,
        ActionKind.ANALYZE,
        ActionKind.COLLECT_EVIDENCE,
        ActionKind.MOVE_TO,
    }
)

DEFENDER_ACTIONS = frozenset(
    {
        ActionKind.INVESTIGATE,
        ActionKind.CONTAIN,
        ActionKind.MONITOR,
    }
)


class DefensiveControlKind(str, Enum):
    EDR = "edr"
    NDR = "ndr"
    SIEM = "siem"
    PATCH_MANAGEMENT = "patch_management"
    MFA = "mfa"
    SEGMENTATION = "segmentation"
    BACKUPS = "backups"


class ObjectiveKind(str, Enum):
    DISCOVER_HOSTS = "discover_hosts"
    CONFIRM_VULNERABILITIES = "confirm_vulnerabilities"
    COLLECT_EVIDENCE = "collect_evidence"
    OBTAIN_CREDENTIALS = "obtain_credentials"
    COMPROMISE_HOSTS = "compromise_hosts"
    REMAIN_UNDETECTED = "remain_undetected"


class DefenderSkill(str, Enum):
    RECRUIT = "recruit"
    ANALYST = "analyst"
    OPERATOR = "operator"
    SPECIALIST = "specialist"
    BLACK_ICE = "black_ice"
    NIGHTHAWK = "nighthawk"


def jsonify(value: Any) -> Any:
    """Recursively convert simulation objects into JSON-safe structures."""
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "__dataclass_fields__"):
        return {k: jsonify(v) for k, v in vars(value).items()}
    if isinstance(value, list):
        return [jsonify(v) for v in value]
    if isinstance(value, dict):
        return {k: jsonify(v) for k, v in value.items()}
    return value
# --------------------------------------------------------------------------- #
# World entities
# --------------------------------------------------------------------------- #


@dataclass
class SimHost:
    """A synthetic machine in the scenario world."""

    id: str
    hostname: str
    role: HostRole
    os: str
    technologies: list[str] = field(default_factory=list)
    segment: str = "corp"
    visibility: InformationState = InformationState.UNKNOWN
    compromised: bool = False


@dataclass
class SimService:
    """A synthetic network service exposed by a host."""

    id: str
    host_id: str
    port: int
    kind: ServiceKind
    version: str = ""
    visibility: InformationState = InformationState.UNKNOWN


@dataclass
class SimIdentity:
    """A synthetic user identity (no real credentials — game object only)."""

    id: str
    name: str
    role_title: str
    host_id: str | None = None
    visibility: InformationState = InformationState.UNKNOWN


@dataclass
class SimVulnerability:
    """A synthetic weakness that actions may confirm (never exploited for real)."""

    id: str
    name: str
    severity: Severity
    affects: str  # ServiceKind value or technology name
    difficulty: int = 3  # 1 (trivial) … 5 (expert)
    description: str = ""
    visibility: InformationState = InformationState.UNKNOWN


@dataclass
class SimCredential:
    """A synthetic credential (game material only — never real secrets)."""

    id: str
    username: str
    kind: str = "password"  # password | hash | key | token
    grants: list[ServiceKind] = field(default_factory=list)
    identity_id: str | None = None
    visibility: InformationState = InformationState.UNKNOWN


@dataclass
class SimNetworkLink:
    """A relationship between two hosts (segment adjacency, vpn, dmz)."""

    from_id: str
    to_id: str
    kind: str = "segment"  # segment | vpn | dmz | internet
    traversable: bool = True


@dataclass
class DefensiveControl:
    """A synthetic defensive capability that shapes detection and response."""

    id: str
    kind: DefensiveControlKind
    strength: float = 0.5  # 0.0 … 1.0
    detects: list[ActionKind] = field(default_factory=list)


@dataclass
class SimAlert:
    """A defender-side alert with confidence that can grow and decay."""

    id: str
    tick: int
    kind: str
    target_id: str
    confidence: InformationState = InformationState.OBSERVED
    status: str = "new"  # new | investigating | contained | closed
    description: str = ""


@dataclass
class Objective:
    """A scenario goal evaluated by the objectives module."""

    id: str
    kind: ObjectiveKind
    required_count: int = 1
    description: str = ""
    is_primary: bool = True


@dataclass
class SimulationEvent:
    """One immutable entry in the append-only simulation event log."""

    seq: int
    tick: int
    actor: str  # attacker | defender | world
    kind: str  # e.g. discovery.host, action.rejected, alert.raised
    message: str
    payload: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "seq": self.seq,
            "tick": self.tick,
            "actor": self.actor,
            "kind": self.kind,
            "message": self.message,
            "payload": jsonify(self.payload),
        }


# --------------------------------------------------------------------------- #
# World container
# --------------------------------------------------------------------------- #


@dataclass
class WorldState:
    """Fully serializable snapshot of the synthetic world.

    Every mutation during a simulation run happens to this object; because it
    round-trips through `to_dict`/`from_dict` losslessly, replay and snapshot
    equality are guaranteed by construction.
    """

    scenario_id: str
    seed: int
    tick: int = 0
    hosts: list[SimHost] = field(default_factory=list)
    services: list[SimService] = field(default_factory=list)
    identities: list[SimIdentity] = field(default_factory=list)
    vulnerabilities: list[SimVulnerability] = field(default_factory=list)
    credentials: list[SimCredential] = field(default_factory=list)
    links: list[SimNetworkLink] = field(default_factory=list)
    controls: list[DefensiveControl] = field(default_factory=list)
    alerts: list[SimAlert] = field(default_factory=list)
    objectives: list[Objective] = field(default_factory=list)

    # attacker progression
    attacker_position: str | None = None
    collected_evidence: list[dict] = field(default_factory=list)
    obtained_credentials: list[str] = field(default_factory=list)
    action_log: list[dict] = field(default_factory=list)

    # ---- indexes -------------------------------------------------------- #

    def host_index(self) -> dict[str, SimHost]:
        return {h.id: h for h in self.hosts}

    def services_on(self, host_id: str) -> list[SimService]:
        return [s for s in self.services if s.host_id == host_id]

    def hosts_in_segment(self, segment: str) -> list[SimHost]:
        return [h for h in self.hosts if h.segment == segment]

    # ---- serialization --------------------------------------------------- #

    def to_dict(self) -> dict:
        return jsonify(self)

    @classmethod
    def from_dict(cls, data: dict) -> "WorldState":
        state = cls(
            scenario_id=data["scenario_id"],
            seed=data["seed"],
            tick=data["tick"],
        )
        state.hosts = [
            SimHost(
                id=h["id"], hostname=h["hostname"], role=HostRole(h["role"]),
                os=h["os"], technologies=list(h["technologies"]),
                segment=h["segment"], visibility=InformationState(h["visibility"]),
                compromised=h["compromised"],
            )
            for h in data["hosts"]
        ]
        state.services = [
            SimService(
                id=s["id"], host_id=s["host_id"], port=s["port"],
                kind=ServiceKind(s["kind"]), version=s["version"],
                visibility=InformationState(s["visibility"]),
            )
            for s in data["services"]
        ]
        state.identities = [
            SimIdentity(
                id=i["id"], name=i["name"], role_title=i["role_title"],
                host_id=i["host_id"], visibility=InformationState(i["visibility"]),
            )
            for i in data["identities"]
        ]
        state.vulnerabilities = [
            SimVulnerability(
                id=v["id"], name=v["name"], severity=Severity(v["severity"]),
                affects=v["affects"], difficulty=v["difficulty"],
                description=v["description"],
                visibility=InformationState(v["visibility"]),
            )
            for v in data["vulnerabilities"]
        ]
        state.credentials = [
            SimCredential(
                id=c["id"], username=c["username"], kind=c["kind"],
                grants=[ServiceKind(g) for g in c["grants"]],
                identity_id=c["identity_id"],
                visibility=InformationState(c["visibility"]),
            )
            for c in data["credentials"]
        ]
        state.links = [SimNetworkLink(**l) for l in data["links"]]
        state.controls = [
            DefensiveControl(
                id=c["id"], kind=DefensiveControlKind(c["kind"]),
                strength=c["strength"], detects=[ActionKind(d) for d in c["detects"]],
            )
            for c in data["controls"]
        ]
        state.alerts = [
            SimAlert(
                id=a["id"], tick=a["tick"], kind=a["kind"], target_id=a["target_id"],
                confidence=InformationState(a["confidence"]), status=a["status"],
                description=a["description"],
            )
            for a in data["alerts"]
        ]
        state.objectives = [
            Objective(
                id=o["id"], kind=ObjectiveKind(o["kind"]),
                required_count=o["required_count"], description=o["description"],
                is_primary=o["is_primary"],
            )
            for o in data["objectives"]
        ]
        state.attacker_position = data["attacker_position"]
        state.collected_evidence = [dict(e) for e in data["collected_evidence"]]
        state.obtained_credentials = list(data["obtained_credentials"])
        state.action_log = [dict(a) for a in data["action_log"]]
        return state

    def state_hash(self) -> str:
        """Deterministic content hash — two states are equal iff hashes match."""
        import hashlib
        import json

        blob = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

