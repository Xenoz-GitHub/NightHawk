"""Objective evaluation — pure functions over the world state."""

from __future__ import annotations

from nighthawk.simulation.models import (
    InformationState,
    ObjectiveKind,
    WorldState,
)


def _count_for(world: WorldState, kind: ObjectiveKind) -> int:
    if kind is ObjectiveKind.DISCOVER_HOSTS:
        return sum(1 for h in world.hosts if h.visibility.at_least(InformationState.OBSERVED))
    if kind is ObjectiveKind.CONFIRM_VULNERABILITIES:
        return sum(1 for v in world.vulnerabilities if v.visibility is InformationState.CONFIRMED)
    if kind is ObjectiveKind.COLLECT_EVIDENCE:
        return len(world.collected_evidence)
    if kind is ObjectiveKind.OBTAIN_CREDENTIALS:
        return len(set(world.obtained_credentials))
    if kind is ObjectiveKind.COMPROMISE_HOSTS:
        return sum(1 for h in world.hosts if h.compromised)
    if kind is ObjectiveKind.REMAIN_UNDETECTED:
        confirmed = [a for a in world.alerts if a.confidence is InformationState.CONFIRMED]
        return 1 if not confirmed else 0
    return 0


def objective_progress(world: WorldState) -> dict[str, dict]:
    """Objective id -> {count, required, complete, kind, primary}."""
    result: dict[str, dict] = {}
    for objective in world.objectives:
        count = _count_for(world, objective.kind)
        result[objective.id] = {
            "kind": objective.kind.value,
            "count": count,
            "required": objective.required_count,
            "complete": count >= objective.required_count,
            "primary": objective.is_primary,
        }
    return result


def all_primary_complete(world: WorldState) -> bool:
    return all(
        entry["complete"]
        for entry in objective_progress(world).values()
        if entry["primary"]
    )
