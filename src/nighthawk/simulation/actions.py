"""Action catalogue: applicability validation and deterministic effects.

Every mutation of the world flows through `apply_attacker_action` /
`apply_defender_action`. Validation raises `InvalidActionError` *before* any
mutation, so rejected actions never dirty the state.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from nighthawk.simulation.models import (
    ActionKind,
    HostRole,
    InformationState,
    InvalidActionError,
    SimAlert,
    WorldState,
)


@dataclass(frozen=True)
class ActionSpec:
    kind: ActionKind
    actor: str  # attacker | defender
    cost: int  # action points
    description: str


ACTION_SPECS: dict[ActionKind, ActionSpec] = {
    spec.kind: spec
    for spec in [
        ActionSpec(ActionKind.DISCOVER, "attacker", 1,
                   "Map hosts reachable from the current position."),
        ActionSpec(ActionKind.INSPECT, "attacker", 1,
                   "Observe services exposed by a known host."),
        ActionSpec(ActionKind.ENUMERATE, "attacker", 2,
                   "Surface identities and credentials around a host."),
        ActionSpec(ActionKind.FINGERPRINT, "attacker", 1,
                   "Confirm technologies and probable weaknesses."),
        ActionSpec(ActionKind.ANALYZE, "attacker", 2,
                   "Confirm a probable vulnerability."),
        ActionSpec(ActionKind.COLLECT_EVIDENCE, "attacker", 2,
                   "Collect proof of exposure from a host."),
        ActionSpec(ActionKind.MOVE_TO, "attacker", 1,
                   "Relocate the operator to another host."),
        ActionSpec(ActionKind.INVESTIGATE, "defender", 2,
                   "Escalate an alert's confidence."),
        ActionSpec(ActionKind.CONTAIN, "defender", 3,
                   "Isolate a host and evict the attacker."),
        ActionSpec(ActionKind.MONITOR, "defender", 1,
                   "Sharpen detection for the next tick."),
    ]
}

# relative noisiness of each attacker action (multiplies control strength)
NOISE = {
    ActionKind.DISCOVER: 0.10,
    ActionKind.INSPECT: 0.15,
    ActionKind.ENUMERATE: 0.30,
    ActionKind.FINGERPRINT: 0.20,
    ActionKind.ANALYZE: 0.25,
    ActionKind.COLLECT_EVIDENCE: 0.35,
    ActionKind.MOVE_TO: 0.40,
}


def spec(kind: ActionKind) -> ActionSpec:
    return ACTION_SPECS[kind]


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #


def _host(world: WorldState, host_id: str | None):
    index = world.host_index()
    if host_id not in index:
        raise InvalidActionError(f"Unknown host '{host_id}'.")
    return index[host_id]


def _reachable(world: WorldState, from_host_id: str | None) -> set[str]:
    """Host ids reachable from the attacker's current position."""
    if from_host_id is None:
        # initial foothold options: edge servers
        edge = {
            h.id for h in world.hosts
            if h.role == HostRole.SERVER and h.segment in ("dmz", "corp")
        }
        if not edge and world.hosts:
            edge = {world.hosts[0].id}
        return edge
    linked: set[str] = set()
    for link in world.links:
        if link.from_id == from_host_id and link.traversable:
            linked.add(link.to_id)
        if link.to_id == from_host_id and link.traversable:
            linked.add(link.from_id)
    current = world.host_index().get(from_host_id)
    if current is not None:
        linked |= {h.id for h in world.hosts_in_segment(current.segment)}
    return linked


def _controls_detecting(world: WorldState, kind: ActionKind) -> list[float]:
    return [c.strength for c in world.controls if kind in c.detects]


def detection_rolls(
    world: WorldState, rng: random.Random, kind: ActionKind,
    target_id: str, tick: int, monitor_boost: float = 0.0,
) -> list[SimAlert]:
    """Roll detection for an attacker action; returns any new alerts."""
    alerts: list[SimAlert] = []
    for strength in _controls_detecting(world, kind):
        chance = min(0.95, strength * NOISE[kind] + monitor_boost)
        if rng.random() < chance:
            alerts.append(SimAlert(
                id=f"a{len(world.alerts) + len(alerts) + 1}",
                tick=tick,
                kind=f"detected.{kind.value}",
                target_id=target_id,
                confidence=InformationState.OBSERVED,
                description=f"{kind.value} on {target_id} noticed by monitoring.",
            ))
    return alerts

# --------------------------------------------------------------------------- #
# mutation entry points — validate first, then mutate, never both at once
# --------------------------------------------------------------------------- #


def _reveal(entity, level: InformationState) -> bool:
    if entity.visibility.at_least(level):
        return False
    entity.visibility = level
    return True


def _reveal_host(world: WorldState, host: SimHost, level: InformationState) -> bool:
    return _reveal(host, level)


def _services_of(world: WorldState, host_id: str) -> list[SimService]:
    return [s for s in world.services if s.host_id == host_id]


def _identities_of(world: WorldState, host_id: str) -> list[SimIdentity]:
    return [i for i in world.identities if i.host_id == host_id]


def _host_tech_or_service_kinds(world: WorldState, host: SimHost) -> set[str]:
    kinds = {s.kind.value for s in _services_of(world, host.id)}
    return kinds | set(host.technologies)


def _log_action(world: WorldState, tick: int, actor: str, kind: ActionKind,
                target: str | None, cost: int) -> None:
    world.action_log.append({
        "tick": tick, "actor": actor, "kind": kind.value,
        "target": target, "cost": cost,
    })


def apply_attacker_action(
    world: WorldState, kind: ActionKind, target: str | None,
) -> dict:
    """Validate then apply one attacker action. Returns an info payload.

    Raises InvalidActionError without mutating state when illegal.
    """
    spec_entry = ACTION_SPECS[kind]
    if spec_entry.actor != "attacker":
        raise InvalidActionError(f"{kind.value} is not an attacker action.")
    info: dict = {"kind": kind.value, "target": target, "changed": []}

    if kind is ActionKind.DISCOVER:
        if target is not None:
            raise InvalidActionError("discover takes no target.")
        revealed = []
        for hid in sorted(_reachable(world, world.attacker_position)):
            host = world.host_index()[hid]
            if _reveal_host(world, host, InformationState.OBSERVED):
                revealed.append(hid)
        info["changed"] = revealed
        return info

    if kind is ActionKind.INSPECT:
        host = _host(world, target)
        if not host.visibility.at_least(InformationState.OBSERVED):
            raise InvalidActionError(f"Host '{target}' has not been discovered yet.")
        info["changed"] = [s.id for s in _services_of(world, host.id)
                           if _reveal(s, InformationState.OBSERVED)]
        return info

    if kind is ActionKind.ENUMERATE:
        host = _host(world, target)
        if not host.visibility.at_least(InformationState.OBSERVED):
            raise InvalidActionError(f"Host '{target}' has not been discovered yet.")
        changed = [i.id for i in _identities_of(world, host.id)
                   if _reveal(i, InformationState.OBSERVED)]
        ids = {i.id for i in _identities_of(world, host.id)}
        creds = [c for c in world.credentials if c.identity_id in ids]
        changed += [c.id for c in creds if _reveal(c, InformationState.OBSERVED)]
        info["changed"] = changed
        return info

    if kind is ActionKind.FINGERPRINT:
        host = _host(world, target)
        if not host.visibility.at_least(InformationState.OBSERVED):
            raise InvalidActionError(f"Host '{target}' has not been discovered yet.")
        changed = []
        if _reveal_host(world, host, InformationState.PROBABLE):
            changed.append(host.id)
        surface = _host_tech_or_service_kinds(world, host)
        for vuln in world.vulnerabilities:
            if vuln.affects in surface and _reveal(vuln, InformationState.PROBABLE):
                changed.append(vuln.id)
        info["changed"] = changed
        return info

    if kind is ActionKind.ANALYZE:
        vuln = next((v for v in world.vulnerabilities if v.id == target), None)
        if vuln is None:
            raise InvalidActionError(f"Unknown vulnerability '{target}'.")
        if not vuln.visibility.at_least(InformationState.PROBABLE):
            raise InvalidActionError(
                f"Vulnerability '{target}' must be fingerprinted before analysis.")
        vuln.visibility = InformationState.CONFIRMED
        info["changed"] = [vuln.id]
        return info

    if kind is ActionKind.COLLECT_EVIDENCE:
        host = _host(world, target)
        surface = _host_tech_or_service_kinds(world, host)
        confirmed = [v for v in world.vulnerabilities
                     if v.affects in surface
                     and v.visibility is InformationState.CONFIRMED]
        if not confirmed:
            raise InvalidActionError(
                f"No confirmed vulnerability on '{target}'; nothing to collect.")
        vuln = confirmed[0]
        evidence = {
            "id": f"e{len(world.collected_evidence) + 1}",
            "host_id": host.id, "vuln_id": vuln.id, "tick": world.tick,
        }
        world.collected_evidence.append(evidence)
        # demonstrated impact: host counts as compromised, local creds exposed
        host.compromised = True
        ids = {i.id for i in _identities_of(world, host.id)}
        harvested = [c for c in world.credentials
                     if c.identity_id in ids
                     and not c.visibility.at_least(InformationState.OBSERVED)]
        for cred in harvested:
            cred.visibility = InformationState.CONFIRMED
            world.obtained_credentials.append(cred.id)
        info["changed"] = [evidence["id"]] + [c.id for c in harvested]
        info["evidence"] = evidence
        return info

    if kind is ActionKind.MOVE_TO:
        host = _host(world, target)
        reachable = _reachable(world, world.attacker_position)
        if host.id not in reachable:
            raise InvalidActionError(
                f"Host '{target}' is not reachable from the current position.")
        world.attacker_position = host.id
        info["changed"] = [host.id]
        return info

    raise InvalidActionError(f"Unhandled attacker action '{kind.value}'.")


def apply_defender_action(
    world: WorldState, kind: ActionKind, target: str | None,
) -> dict:
    """Validate then apply one defender action."""
    spec_entry = ACTION_SPECS[kind]
    if spec_entry.actor != "defender":
        raise InvalidActionError(f"{kind.value} is not a defender action.")
    info: dict = {"kind": kind.value, "target": target, "changed": []}

    if kind is ActionKind.INVESTIGATE:
        alert = next((a for a in world.alerts if a.id == target), None)
        if alert is None:
            raise InvalidActionError(f"Unknown alert '{target}'.")
        if alert.confidence is InformationState.CONFIRMED:
            raise InvalidActionError(f"Alert '{target}' is already confirmed.")
        # escalate one information level per investigation
        next_level = {
            InformationState.UNKNOWN: InformationState.OBSERVED,
            InformationState.OBSERVED: InformationState.PROBABLE,
            InformationState.PROBABLE: InformationState.CONFIRMED,
            InformationState.CONFIRMED: InformationState.CONFIRMED,
        }[alert.confidence]
        alert.confidence = next_level
        if next_level is InformationState.CONFIRMED:
            alert.status = "confirmed"
        info["changed"] = [alert.id]
        return info

    if kind is ActionKind.CONTAIN:
        host = _host(world, target)
        changed = []
        for link in world.links:
            if target in (link.from_id, link.to_id) and link.traversable:
                link.traversable = False
                changed.append(f"{link.from_id}->{link.to_id}")
        if world.attacker_position == target:
            world.attacker_position = None  # evicted
        if host.compromised:
            host.compromised = False
            changed.append(f"{host.id}:evicted")
        info["changed"] = changed
        return info

    if kind is ActionKind.MONITOR:
        if target is not None:
            raise InvalidActionError("monitor takes no target.")
        info["changed"] = []  # effect: detection boost on the next attacker action
        return info

    raise InvalidActionError(f"Unhandled defender action '{kind.value}'.")
