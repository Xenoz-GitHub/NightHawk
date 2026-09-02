"""Deterministic scenario definitions and world generation.

All randomness flows through a single `random.Random(seed)` instance, so the
same seed always yields the identical world. Generation is pure: no clock, no
I/O, no environment reads.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from nighthawk.models.core import Severity
from nighthawk.simulation.models import (
    ActionKind,
    DefenderSkill,
    DefensiveControl,
    DefensiveControlKind,
    HostRole,
    Objective,
    ObjectiveKind,
    ServiceKind,
    SimCredential,
    SimHost,
    SimIdentity,
    SimNetworkLink,
    SimService,
    SimVulnerability,
    WorldState,
)
from nighthawk.simulation.models import ScenarioError


@dataclass(frozen=True)
class ScenarioSpec:
    """Static definition of a scenario archetype."""

    id: str
    name: str
    description: str
    segments: tuple[str, ...]
    server_count: int
    workstation_count: int
    iot_count: int
    defender_baseline: float  # scales control strength by defender skill


SCENARIOS: dict[str, ScenarioSpec] = {
    "small_office": ScenarioSpec(
        id="small_office",
        name="Small Office",
        description=(
            "A 10-person office: a file server, a couple of workstations, "
            "a printer, and a flat network with minimal defenses."
        ),
        segments=("corp",),
        server_count=1,
        workstation_count=3,
        iot_count=1,
        defender_baseline=0.35,
    ),
    "saas_company": ScenarioSpec(
        id="saas_company",
        name="SaaS Company",
        description=(
            "A cloud-native product company: API servers, a database host, "
            "developer workstations, segmented DMZ and corp networks."
        ),
        segments=("dmz", "corp", "cloud"),
        server_count=3,
        workstation_count=3,
        iot_count=0,
        defender_baseline=0.55,
    ),
    "university": ScenarioSpec(
        id="university",
        name="University Network",
        description=(
            "A campus network with open wi-fi segments, lab machines, "
            "and a student-facing portal with legacy services."
        ),
        segments=("campus", "lab", "admin"),
        server_count=2,
        workstation_count=4,
        iot_count=1,
        defender_baseline=0.4,
    ),
    "healthcare_lab": ScenarioSpec(
        id="healthcare_lab",
        name="Healthcare Lab",
        description=(
            "A clinical research lab: workstation kiosks, a records server, "
            "and strict compliance-driven monitoring."
        ),
        segments=("clinic", "records"),
        server_count=2,
        workstation_count=2,
        iot_count=2,
        defender_baseline=0.65,
    ),
    "industrial_test": ScenarioSpec(
        id="industrial_test",
        name="Industrial Test Environment",
        description=(
            "A segregated OT test cell with engineering workstations, "
            "a historian server, and protocol gateway devices."
        ),
        segments=("plant", "engineering"),
        server_count=1,
        workstation_count=2,
        iot_count=2,
        defender_baseline=0.45,
    ),
    "cloud_startup": ScenarioSpec(
        id="cloud_startup",
        name="Cloud Startup",
        description=(
            "A small startup running everything in the cloud: container "
            "hosts, a managed database, and identity-centric defenses."
        ),
        segments=("cloud", "corp"),
        server_count=2,
        workstation_count=2,
        iot_count=0,
        defender_baseline=0.5,
    ),
}


def list_scenarios() -> list[str]:
    return sorted(SCENARIOS)



# --------------------------------------------------------------------------- #
# Generation pools
# --------------------------------------------------------------------------- #

_SKILL_SCALE = {
    DefenderSkill.RECRUIT: 0.6,
    DefenderSkill.ANALYST: 0.8,
    DefenderSkill.OPERATOR: 1.0,
    DefenderSkill.SPECIALIST: 1.2,
    DefenderSkill.BLACK_ICE: 1.45,
    DefenderSkill.NIGHTHAWK: 1.7,
}

_SERVER_OS = ["Ubuntu 22.04", "Ubuntu 24.04", "Windows Server 2022", "Debian 12"]
_WORKSTATION_OS = ["Windows 11", "Windows 10", "macOS 14", "Ubuntu 24.04"]
_IOT_OS = ["embedded-linux", "vxworks", "proprietary-rtos"]

_SERVER_TECH = ["nginx", "postgresql", "redis", "docker", "python", "node"]
_WORKSTATION_TECH = ["office-suite", "vpn-client", "browser", "git"]
_IOT_TECH = ["mqtt", "modbus", "custom-firmware"]

_SERVER_SERVICES = [ServiceKind.HTTPS, ServiceKind.HTTP, ServiceKind.SSH,
                    ServiceKind.DATABASE, ServiceKind.API]
_PORT_FOR_KIND = {
    ServiceKind.HTTP: 80, ServiceKind.HTTPS: 443, ServiceKind.SSH: 22,
    ServiceKind.SMB: 445, ServiceKind.RDP: 3389, ServiceKind.DNS: 53,
    ServiceKind.DATABASE: 5432, ServiceKind.API: 8443, ServiceKind.VPN: 1194,
    ServiceKind.EMAIL: 587,
}

_NAME_A = ["atlas", "borealis", "cobalt", "dusk", "ember", "falcon", "granite",
           "harbor", "iris", "juniper", "kestrel", "lumen"]
_NAME_B = ["db", "app", "web", "files", "gate", "lab", "ops", "vault"]
_PERSON_NAMES = ["j.alvarez", "k.chen", "m.okafor", "s.petrov", "r.nakamura",
                 "t.dubois", "a.whitfield", "l.moretti"]


def _skill_scale(skill: DefenderSkill) -> float:
    return _SKILL_SCALE[skill]


def _make_hosts(spec: ScenarioSpec, rng: random.Random, state: WorldState) -> list[str]:
    """Create hosts + services + links. Returns the list of host ids."""
    host_ids: list[str] = []
    counter = 0
    for _ in range(spec.server_count):
        counter += 1
        hid = f"h{counter}"
        host_ids.append(hid)
        state.hosts.append(SimHost(
            id=hid,
            hostname=f"{rng.choice(_NAME_A)}-{rng.choice(_NAME_B)}{counter:02d}",
            role=HostRole.SERVER,
            os=rng.choice(_SERVER_OS),
            technologies=rng.sample(_SERVER_TECH, k=rng.randint(2, 3)),
            segment=spec.segments[counter % len(spec.segments)],
        ))
    for _ in range(spec.workstation_count):
        counter += 1
        hid = f"h{counter}"
        host_ids.append(hid)
        state.hosts.append(SimHost(
            id=hid,
            hostname=f"{rng.choice(_NAME_A)}-ws{counter:02d}",
            role=HostRole.WORKSTATION,
            os=rng.choice(_WORKSTATION_OS),
            technologies=rng.sample(_WORKSTATION_TECH, k=rng.randint(1, 2)),
            segment=spec.segments[0],
        ))
    for _ in range(spec.iot_count):
        counter += 1
        hid = f"h{counter}"
        host_ids.append(hid)
        state.hosts.append(SimHost(
            id=hid,
            hostname=f"{rng.choice(_NAME_A)}-iot{counter:02d}",
            role=HostRole.IOT,
            os=rng.choice(_IOT_OS),
            technologies=rng.sample(_IOT_TECH, k=1),
            segment=spec.segments[-1],
        ))

    # services
    scounter = 0
    for host in state.hosts:
        if host.role == HostRole.SERVER:
            kinds = rng.sample(_SERVER_SERVICES, k=rng.randint(2, 4))
        elif host.role == HostRole.WORKSTATION:
            kinds = [ServiceKind.SMB] + rng.sample(
                [ServiceKind.RDP, ServiceKind.HTTP], k=rng.randint(0, 1))
        else:  # IOT
            kinds = [ServiceKind.HTTP]
        for kind in kinds:
            scounter += 1
            state.services.append(SimService(
                id=f"s{scounter}", host_id=host.id,
                port=_PORT_FOR_KIND[kind], kind=kind,
                version=f"{rng.randint(1, 9)}.{rng.randint(0, 9)}",
            ))

    # links: every host reaches the first server (star topology per segment,
    # plus cross-segment links through the first server of each segment)
    if host_ids:
        hub = host_ids[0]
        lcounter = 0
        seen = {(hub, hub)}
        for hid in host_ids[1:]:
            lcounter += 1
            seen.add((hub, hid))
            state.links.append(SimNetworkLink(from_id=hub, to_id=hid, kind="segment"))
        first_by_segment: dict[str, str] = {}
        for host in state.hosts:
            first_by_segment.setdefault(host.segment, host.id)
        anchors = [h for h in first_by_segment.values() if h != hub]
        for anchor in anchors:
            lcounter += 1
            state.links.append(SimNetworkLink(from_id=hub, to_id=anchor, kind="dmz"))
    return host_ids



def _make_social(
    spec: ScenarioSpec, rng: random.Random, state: WorldState, host_ids: list[str],
) -> None:
    """Identities, synthetic credentials, and defensive controls."""
    workstations = [h for h in state.hosts if h.role == HostRole.WORKSTATION]
    servers = [h for h in state.hosts if h.role == HostRole.SERVER]

    # identities: one per workstation, admins on the first server
    for i, host in enumerate(workstations):
        person = rng.choice(_PERSON_NAMES)
        state.identities.append(SimIdentity(
            id=f"i{i + 1}",
            name=person,
            role_title=rng.choice(["Analyst", "Developer", "Manager", "Designer"]),
            host_id=host.id,
        ))
    for j, server in enumerate(servers[:1]):
        state.identities.append(SimIdentity(
            id=f"i{len(state.identities) + 1}",
            name="svc.admin",
            role_title="System Administrator",
            host_id=server.id,
        ))

    # credentials: workstation users have a password granting SMB/RDP on
    # their own host; the admin has one granting SSH on every server
    for identity in state.identities:
        grants = (
            [ServiceKind.SSH] if identity.name == "svc.admin"
            else [ServiceKind.SMB, ServiceKind.RDP]
        )
        state.credentials.append(SimCredential(
            id=f"c{len(state.credentials) + 1}",
            username=identity.name,
            kind="password",
            grants=grants,
            identity_id=identity.id,
        ))

    # defensive controls, scaled by the scenario's defender baseline
    baseline = spec.defender_baseline
    catalog = [
        (DefensiveControlKind.EDR, [
            ActionKind.COLLECT_EVIDENCE, ActionKind.MOVE_TO]),
        (DefensiveControlKind.SIEM, [ActionKind.DISCOVER, ActionKind.ENUMERATE]),
        (DefensiveControlKind.NDR, [ActionKind.ENUMERATE, ActionKind.MOVE_TO]),
        (DefensiveControlKind.PATCH_MANAGEMENT, []),
        (DefensiveControlKind.MFA, []),
        (DefensiveControlKind.SEGMENTATION, [ActionKind.MOVE_TO]),
    ]
    for k, (kind, detects) in enumerate(catalog):
        state.controls.append(DefensiveControl(
            id=f"d{k + 1}",
            kind=kind,
            strength=min(1.0, max(0.05, baseline * rng.uniform(0.7, 1.3))),
            detects=detects,
        ))



def _make_vulns(
    spec: ScenarioSpec, rng: random.Random, state: WorldState,
) -> None:
    """Synthetic vulnerabilities matched to generated services/technologies."""
    service_kinds = {s.kind.value for s in state.services}
    techs = {t for h in state.hosts for t in h.technologies}
    candidates = sorted(service_kinds | techs)
    if not candidates:
        return
    vuln_templates = [
        ("CVE-2024-SIM-{n:04d}", "Rebound Shell Injection", Severity.HIGH, 2),
        ("CVE-2024-SIM-{n:04d}", "Ghost Path Traversal", Severity.MEDIUM, 3),
        ("CVE-2024-SIM-{n:04d}", "Whisper Credential Leak", Severity.HIGH, 3),
        ("CVE-2024-SIM-{n:04d}", "Nullpoint Deserialization", Severity.CRITICAL, 4),
        ("CVE-2024-SIM-{n:04d}", "Lattice Request Forgery", Severity.MEDIUM, 2),
        ("CVE-2024-SIM-{n:04d}", "Beacon Hardcoded Keys", Severity.HIGH, 1),
        ("CVE-2024-SIM-{n:04d}", "Marble Weak Crypto", Severity.LOW, 1),
    ]
    vuln_count = max(2, len(state.services) // 2)
    for i in range(vuln_count):
        cve, name, severity, difficulty = vuln_templates[i % len(vuln_templates)]
        state.vulnerabilities.append(SimVulnerability(
            id=f"v{i + 1}",
            name=name,
            severity=severity,
            affects=rng.choice(candidates),
            difficulty=difficulty,
            description=f"Synthetic weakness affecting {rng.choice(candidates)}.",
        ))


def _make_objectives(state: WorldState) -> None:
    state.objectives = [
        Objective(
            id="obj-recon",
            kind=ObjectiveKind.DISCOVER_HOSTS,
            required_count=max(2, len(state.hosts) // 2),
            description=f"Discover at least {max(2, len(state.hosts) // 2)} hosts.",
        ),
        Objective(
            id="obj-vulns",
            kind=ObjectiveKind.CONFIRM_VULNERABILITIES,
            required_count=2,
            description="Confirm 2 synthetic vulnerabilities.",
        ),
        Objective(
            id="obj-evidence",
            kind=ObjectiveKind.COLLECT_EVIDENCE,
            required_count=3,
            description="Collect 3 pieces of evidence.",
        ),
        Objective(
            id="obj-stealth",
            kind=ObjectiveKind.REMAIN_UNDETECTED,
            required_count=1,
            description="Finish with no CONFIRMED alerts.",
            is_primary=False,
        ),
    ]


def generate_world(
    scenario: str, seed: int, defender: DefenderSkill = DefenderSkill.OPERATOR,
) -> WorldState:
    """Generate a fully deterministic world for the given scenario + seed."""
    if scenario not in SCENARIOS:
        raise ScenarioError(
            f"Unknown scenario '{scenario}'. Available: {', '.join(sorted(SCENARIOS))}"
        )
    spec = SCENARIOS[scenario]
    rng = random.Random(seed)
    state = WorldState(scenario_id=scenario, seed=seed)
    host_ids = _make_hosts(spec, rng, state)
    _make_social(spec, rng, state, host_ids)
    _make_vulns(spec, rng, state)
    _make_objectives(state)

    # scale control strength by defender skill (deterministic transform)
    scale = _skill_scale(defender)
    for control in state.controls:
        control.strength = min(1.0, control.strength * scale)
    return state

