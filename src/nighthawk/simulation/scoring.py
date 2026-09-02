"""Deterministic scoring: objective points, stealth, efficiency, letter grade.

All inputs come from the world state; no randomness. Two replays of the same
action sequence always produce the same score.
"""

from __future__ import annotations

from nighthawk.simulation.models import (
    InformationState,
    ObjectiveKind,
    WorldState,
)

# points per unit of progress, by objective kind
POINTS: dict[ObjectiveKind, int] = {
    ObjectiveKind.DISCOVER_HOSTS: 100,
    ObjectiveKind.CONFIRM_VULNERABILITIES: 250,
    ObjectiveKind.COLLECT_EVIDENCE: 200,
    ObjectiveKind.OBTAIN_CREDENTIALS: 150,
    ObjectiveKind.COMPROMISE_HOSTS: 150,
    ObjectiveKind.REMAIN_UNDETECTED: 300,
}


def objective_points(world: WorldState) -> int:
    """Sum of points for every unit of completed objective progress."""
    total = 0
    for objective in world.objectives:
        kind = objective.kind
        if kind not in POINTS:
            continue
        unit = POINTS[kind]
        if kind is ObjectiveKind.DISCOVER_HOSTS:
            count = sum(
                1 for h in world.hosts
                if h.visibility.at_least(InformationState.OBSERVED)
            )
        elif kind is ObjectiveKind.CONFIRM_VULNERABILITIES:
            count = sum(
                1 for v in world.vulnerabilities
                if v.visibility is InformationState.CONFIRMED
            )
        elif kind is ObjectiveKind.COLLECT_EVIDENCE:
            count = len(world.collected_evidence)
        elif kind is ObjectiveKind.OBTAIN_CREDENTIALS:
            count = len(set(world.obtained_credentials))
        elif kind is ObjectiveKind.COMPROMISE_HOSTS:
            count = sum(1 for h in world.hosts if h.compromised)
        else:  # REMAIN_UNDETECTED
            confirmed = [
                a for a in world.alerts
                if a.confidence is InformationState.CONFIRMED
            ]
            count = 1 if not confirmed else 0
        total += unit * min(count, max(objective.required_count, 1))
    return total


def stealth_points(world: WorldState) -> int:
    """Reward for staying under confirmed detection."""
    confirmed = [a for a in world.alerts if a.confidence is InformationState.CONFIRMED]
    probable = [a for a in world.alerts if a.confidence is InformationState.PROBABLE]
    return max(0, 300 - 100 * len(confirmed) - 25 * len(probable))


def efficiency_points(world: WorldState, ticks_used: int) -> int:
    """Fewer ticks per meaningful action is better."""
    actions = len(world.action_log)
    if actions == 0:
        return 0
    per_action = ticks_used / actions
    if per_action <= 1.0:
        return 150
    if per_action >= 3.0:
        return 0
    return int(150 * (3.0 - per_action) / 2.0)


def letter_grade(total: int) -> str:
    if total >= 2000:
        return "S"
    if total >= 1600:
        return "A"
    if total >= 1200:
        return "B"
    if total >= 800:
        return "C"
    if total >= 400:
        return "D"
    return "F"


def score(world: WorldState, ticks_used: int) -> dict:
    """Full scorecard for a completed run."""
    obj = objective_points(world)
    stealth = stealth_points(world)
    efficiency = efficiency_points(world, ticks_used)
    total = obj + stealth + efficiency
    return {
        "objective_points": obj,
        "stealth_points": stealth,
        "efficiency_points": efficiency,
        "total": total,
        "grade": letter_grade(total),
    }
