"""Defender depth: skill presets, detection curves, alert decay, autopilot.

The defender is a deterministic, stateless policy over the world: given the
same world + skill + rng, `choose_defender_action` always picks the same
action. Nothing here touches I/O, clocks, or the database.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from nighthawk.simulation.actions import DETECTION_CURVES, detection_curve
from nighthawk.simulation.models import (
    ActionKind,
    DefenderSkill,
    InformationState,
    InvalidActionError,
    WorldState,
)

# ticks before an unattended alert decays one confidence level
ALERT_DECAY_TICKS = 3


@dataclass(frozen=True)
class DefenderPreset:
    """Behavioural profile for one skill tier."""

    skill: DefenderSkill
    label: str
    detection_multiplier: float      # scales control strength at generation
    response_latency: int            # ticks of patience before reacting
    respond_if_probable: bool        # investigate PROBABLE alerts proactively?
    description: str


SKILL_PRESETS: dict[DefenderSkill, DefenderPreset] = {
    DefenderSkill.RECRUIT: DefenderPreset(
        DefenderSkill.RECRUIT, "Recruit", 0.6, 2, False,
        "Slow to correlate alerts; only reacts to confirmed activity.",
    ),
    DefenderSkill.ANALYST: DefenderPreset(
        DefenderSkill.ANALYST, "Analyst", 0.8, 1, False,
        "Follows runbooks; investigates once an alert looks real.",
    ),
    DefenderSkill.OPERATOR: DefenderPreset(
        DefenderSkill.OPERATOR, "Operator", 1.0, 0, True,
        "Standard SOC operator; investigates probable leads immediately.",
    ),
    DefenderSkill.SPECIALIST: DefenderPreset(
        DefenderSkill.SPECIALIST, "Specialist", 1.2, 0, True,
        "Aggressive containment and fast triage across segments.",
    ),
    DefenderSkill.BLACK_ICE: DefenderPreset(
        DefenderSkill.BLACK_ICE, "Black Ice", 1.45, 0, True,
        "Elite monitoring: hunts for footholds before they land.",
    ),
    DefenderSkill.NIGHTHAWK: DefenderPreset(
        DefenderSkill.NIGHTHAWK, "Nighthawk", 1.7, 0, True,
        "Near-synthetic response; assumes the attacker has already moved.",
    ),
}


def decay_alerts(
    world: WorldState,
    current_tick: int,
    period: int = ALERT_DECAY_TICKS,
) -> list[dict]:
    """Age alerts: unattended confidence drops one level per period; alerts
    that decay below OBSERVED close and are removed. Pure and deterministic.

    Returns ``[{id, old, new, closed}]`` for the event log.
    """
    if period <= 0:
        return []
    changes: list[dict] = []
    remaining = []
    for alert in world.alerts:
        age = current_tick - alert.tick
        if age < period:
            remaining.append(alert)
            continue
        old = alert.confidence
        if old is InformationState.CONFIRMED:
            alert.confidence = InformationState.PROBABLE
            alert.status = "investigating"
            changes.append({"id": alert.id, "old": old.value,
                            "new": alert.confidence.value, "closed": False})
            remaining.append(alert)
        elif old is InformationState.PROBABLE:
            alert.confidence = InformationState.OBSERVED
            changes.append({"id": alert.id, "old": old.value,
                            "new": alert.confidence.value, "closed": False})
            remaining.append(alert)
        else:  # OBSERVED / UNKNOWN → stale, close it
            changes.append({"id": alert.id, "old": old.value,
                            "new": "closed", "closed": True})
    world.alerts = remaining
    return changes
def choose_defender_action(
    world: WorldState, skill: DefenderSkill, rng: random.Random,
) -> ActionKind | None:
    """Pick the defender's action for this tick (or None to pass).

    Priority: contain established footholds → investigate highest-confidence
    alerts → monitor while anything is open. `rng` is only used for
    deterministic tie-breaking, so behaviour stays reproducible.
    """
    preset = SKILL_PRESETS[skill]

    # 1. contain an established foothold (compromised host)
    for host in world.hosts:
        if host.compromised:
            if rng.random() < 0.9:  # containment mostly succeeds first try
                return ActionKind.CONTAIN

    # 2. investigate the most confident open alert worth attention
    active = sorted(
        (a for a in world.alerts if a.status != "closed"),
        key=lambda a: a.confidence.value, reverse=True,
    )
    if active:
        top = active[0]
        if top.confidence is InformationState.CONFIRMED or (
            preset.respond_if_probable
            and top.confidence is InformationState.PROBABLE
        ):
            if world.tick - top.tick >= preset.response_latency:
                return ActionKind.INVESTIGATE

    # 3. no leads to chase — monitor to sharpen next-tick detection
    if world.alerts:
        return ActionKind.MONITOR
    return None


def _investigate_target(world: WorldState) -> str | None:
    active = sorted(
        (a for a in world.alerts if a.status != "closed"),
        key=lambda a: a.confidence.value, reverse=True,
    )
    return active[0].id if active else None


def defender_turn(engine, skill: DefenderSkill, rng: random.Random) -> dict | None:
    """Run one autopilot defender turn through the engine.

    Returns the info payload of the chosen action, or None if the defender
    passed or the candidate action was illegal.
    """
    choice = choose_defender_action(engine.world, skill, rng)
    if choice is None:
        return None
    try:
        if choice is ActionKind.MONITOR:
            return engine.defender_act(choice)
        if choice is ActionKind.CONTAIN:
            target = next((h.id for h in engine.world.hosts if h.compromised), None)
        else:  # INVESTIGATE
            target = _investigate_target(engine.world)
        if target is None:
            return None
        return engine.defender_act(choice, target)
    except InvalidActionError:
        return None