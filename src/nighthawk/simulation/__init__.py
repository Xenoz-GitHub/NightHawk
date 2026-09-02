"""Sandboxed simulation engine (Phase 4).

Offline, deterministic tactical scenarios: same seed + same action sequence
always produce an identical state hash and event log. Zero network I/O,
zero database access, zero FastAPI imports — enforced by a regression test.
"""

from nighthawk.simulation.engine import SimulationEngine, from_scenario
from nighthawk.simulation.events import EventLog
from nighthawk.simulation.models import (
    ActionKind,
    DefenderSkill,
    DefensiveControl,
    DefensiveControlKind,
    HostRole,
    InformationState,
    InvalidActionError,
    Objective,
    ObjectiveKind,
    ServiceKind,
    SimAlert,
    SimCredential,
    SimHost,
    SimIdentity,
    SimNetworkLink,
    SimService,
    SimVulnerability,
    SimulationError,
    WorldState,
)
from nighthawk.simulation.scenario import ScenarioSpec, generate_world, list_scenarios

__all__ = [
    "SimulationEngine",
    "from_scenario",
    "EventLog",
    "generate_world",
    "list_scenarios",
    "ScenarioSpec",
    "ActionKind",
    "DefenderSkill",
    "DefensiveControl",
    "DefensiveControlKind",
    "HostRole",
    "InformationState",
    "InvalidActionError",
    "Objective",
    "ObjectiveKind",
    "ServiceKind",
    "SimAlert",
    "SimCredential",
    "SimHost",
    "SimIdentity",
    "SimNetworkLink",
    "SimService",
    "SimVulnerability",
    "SimulationError",
    "WorldState",
]
