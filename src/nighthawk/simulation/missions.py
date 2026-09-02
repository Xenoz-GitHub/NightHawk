"""Mission packs: briefings, objective sets, constraints, time limits.

A Mission binds a scenario archetype + defender skill + objective list into a
playable, deterministic scenario. `from_mission` returns an engine already
configured with the mission's time budget and objectives.
"""

from __future__ import annotations

from dataclasses import dataclass

from nighthawk.simulation.engine import SimulationEngine
from nighthawk.simulation.models import (
    DefenderSkill,
    Objective,
    ObjectiveKind,
    WorldState,
)
from nighthawk.simulation.objectives import objective_progress
from nighthawk.simulation.scenario import generate_world


@dataclass(frozen=True)
class Mission:
    id: str
    title: str
    briefing: str
    scenario: str
    difficulty: str        # presentational label (Recruit … Nighthawk)
    defender: DefenderSkill
    time_limit: int        # tick budget => engine.max_ticks
    objectives: tuple[Objective, ...]
    constraints: tuple[str, ...] = ()


def _obj(oid: str, kind: ObjectiveKind, count: int,
         description: str, primary: bool = True) -> Objective:
    return Objective(id=oid, kind=kind, required_count=count,
                     description=description, is_primary=primary)


MISSIONS: dict[str, Mission] = {
    "sentry": Mission(
        id="sentry",
        title="Sentry Down",
        briefing=(
            "A sleepy office LAN with a single file server. Map the network, "
            "confirm the exposed service weaknesses, and collect proof of "
            "exposure. Stay quiet — the local MSP does nightly log reviews."
        ),
        scenario="small_office",
        difficulty="Recruit",
        defender=DefenderSkill.RECRUIT,
        time_limit=18,
        objectives=(
            _obj("m1-recon", ObjectiveKind.DISCOVER_HOSTS, 3,
                 "Discover at least 3 hosts.", primary=True),
            _obj("m1-vulns", ObjectiveKind.CONFIRM_VULNERABILITIES, 2,
                 "Confirm 2 vulnerabilities.", primary=True),
            _obj("m1-evidence", ObjectiveKind.COLLECT_EVIDENCE, 2,
                 "Collect 2 pieces of evidence.", primary=True),
            _obj("m1-stealth", ObjectiveKind.REMAIN_UNDETECTED, 1,
                 "Finish with no confirmed alerts.", primary=False),
        ),
        constraints=("No real-world resources", "Offline sandbox only"),
    ),
    "quiet_rush": Mission(
        id="quiet_rush",
        title="Quiet Rush",
        briefing=(
            "A cloud SaaS startup is going public next week. Confirm the "
            "exposure on the public API tier and gather credentials before "
            "their SOC finishes onboarding."
        ),
        scenario="saas_company",
        difficulty="Operator",
        defender=DefenderSkill.OPERATOR,
        time_limit=16,
        objectives=(
            _obj("m2-recon", ObjectiveKind.DISCOVER_HOSTS, 4,
                 "Discover at least 4 hosts.", primary=True),
            _obj("m2-vulns", ObjectiveKind.CONFIRM_VULNERABILITIES, 3,
                 "Confirm 3 vulnerabilities.", primary=True),
            _obj("m2-creds", ObjectiveKind.OBTAIN_CREDENTIALS, 2,
                 "Harvest 2 credentials.", primary=False),
            _obj("m2-stealth", ObjectiveKind.REMAIN_UNDETECTED, 1,
                 "Finish with no confirmed alerts.", primary=True),
        ),
        constraints=("Defender reacts to probable leads immediately",),
    ),
    "campus_keys": Mission(
        id="campus_keys",
        title="Campus Keys",
        briefing=(
            "A university campus with open lab segments. Recover the "
            "credential that spans the administration segment before finals "
            "week traffic drowns the SOC."
        ),
        scenario="university",
        difficulty="Analyst",
        defender=DefenderSkill.ANALYST,
        time_limit=20,
        objectives=(
            _obj("m3-recon", ObjectiveKind.DISCOVER_HOSTS, 5,
                 "Discover at least 5 hosts.", primary=True),
            _obj("m3-creds", ObjectiveKind.OBTAIN_CREDENTIALS, 2,
                 "Harvest 2 credentials.", primary=True),
            _obj("m3-compromise", ObjectiveKind.COMPROMISE_HOSTS, 1,
                 "Compromise 1 host", primary=False),
            _obj("m3-evidence", ObjectiveKind.COLLECT_EVIDENCE, 2,
                 "Collect 2 pieces of evidence.", primary=True),
        ),
    ),
    "clinical": Mission(
        id="clinical",
        title="Clinical Breach",
        briefing=(
            "A clinical research lab under compliance watch. Confirm the "
            "weakness chain on the records server and exfiltrate synthetic "
            "evidence. The analyst team is sharp — triage is fast."
        ),
        scenario="healthcare_lab",
        difficulty="Specialist",
        defender=DefenderSkill.SPECIALIST,
        time_limit=14,
        objectives=(
            _obj("m4-recon", ObjectiveKind.DISCOVER_HOSTS, 3,
                 "Discover at least 3 hosts.", primary=True),
            _obj("m4-vulns", ObjectiveKind.CONFIRM_VULNERABILITIES, 2,
                 "Confirm 2 vulnerabilities.", primary=True),
            _obj("m4-evidence", ObjectiveKind.COLLECT_EVIDENCE, 1,
                 "Collect 1 piece of evidence.", primary=True),
            _obj("m4-stealth", ObjectiveKind.REMAIN_UNDETECTED, 1,
                 "Finish with no confirmed alerts.", primary=True),
        ),
        constraints=("Aggressive containment of any foothold",),
    ),
    "blackout": Mission(
        id="blackout",
        title="Blackout",
        briefing=(
            "Industrial OT test cell. Reach the historian server through an "
            "engineering workstation and plant synthetic proof of access "
            "without tripping the elite response team."
        ),
        scenario="industrial_test",
        difficulty="Black Ice",
        defender=DefenderSkill.BLACK_ICE,
        time_limit=12,
        objectives=(
            _obj("m5-move", ObjectiveKind.DISCOVER_HOSTS, 3,
                 "Reach and discover 3 hosts.", primary=True),
            _obj("m5-evidence", ObjectiveKind.COLLECT_EVIDENCE, 1,
                 "Collect 1 piece of evidence.", primary=True),
            _obj("m5-stealth", ObjectiveKind.REMAIN_UNDETECTED, 1,
                 "Finish with no confirmed alerts.", primary=True),
            _obj("m5-compromise", ObjectiveKind.COMPROMISE_HOSTS, 1,
                 "Compromise 1 host", primary=False),
        ),
        constraints=("Elite detection: probable alerts get investigated",),
    ),
    "cold_start": Mission(
        id="cold_start",
        title="Cold Start",
        briefing=(
            "A cloud-native startup hardened by a Nighthawk-grade defender. "
            "Move fast: discover, confirm, and exfiltrate synthetic evidence "
            "before the near-synthetic response catches on."
        ),
        scenario="cloud_startup",
        difficulty="Nighthawk",
        defender=DefenderSkill.NIGHTHAWK,
        time_limit=10,
        objectives=(
            _obj("m6-recon", ObjectiveKind.DISCOVER_HOSTS, 3,
                 "Discover at least 3 hosts.", primary=True),
            _obj("m6-evidence", ObjectiveKind.COLLECT_EVIDENCE, 1,
                 "Collect 1 piece of evidence.", primary=True),
            _obj("m6-vulns", ObjectiveKind.CONFIRM_VULNERABILITIES, 2,
                 "Confirm 2 vulnerabilities.", primary=True),
            _obj("m6-stealth", ObjectiveKind.REMAIN_UNDETECTED, 1,
                 "Finish with no confirmed alerts.", primary=True),
        ),
        constraints=("Tightest time budget in the catalogue",),
    ),
}


def list_missions() -> list[str]:
    return sorted(MISSIONS)


def build_world(mission_id: str, seed: int) -> WorldState:
    """Deterministic world for a mission with its objective set swapped in."""
    mission = MISSIONS[mission_id]
    world = generate_world(mission.scenario, seed, mission.defender)
    world.objectives = [Objective(**vars(o)) for o in mission.objectives]
    return world


def from_mission(mission_id: str, seed: int) -> SimulationEngine:
    """Engine pre-configured with the mission's world, objectives, time limit,
    and defender skill. Deterministic for a given (mission, seed)."""
    if mission_id not in MISSIONS:
        raise KeyError(
            f"Unknown mission '{mission_id}'. Available: {', '.join(list_missions())}"
        )
    mission = MISSIONS[mission_id]
    world = build_world(mission_id, seed)
    return SimulationEngine(world, max_ticks=mission.time_limit,
                            defender=mission.defender)


def mission_report(engine: SimulationEngine, mission: Mission) -> dict:
    """Human + machine-readable outcome report for a finished run."""
    card = engine.score()
    return {
        "mission": mission.id,
        "title": mission.title,
        "briefing": mission.briefing,
        "scenario": mission.scenario,
        "difficulty": mission.difficulty,
        "outcome": engine.outcome,
        "ticks_used": card["ticks_used"],
        "score": card,
        "objectives": objective_progress(engine.world),
    }