"""Simulation engine: deterministic turn orchestration.

The engine never introduces its own randomness into state. Detection rolls
are seeded from the world-state hash, so two replays of the same action
sequence — even after a save/load round-trip — produce identical alerts,
identical event logs, and identical final state hashes.

Turn structure per tick:
  1. attacker acts (may raise alerts)
  2. defender acts (investigate / contain / monitor)
  3. detection roll for any attacker action this tick, then tick increments
"""

from __future__ import annotations

import random

from nighthawk.simulation.actions import (
    detection_rolls,
    spec as action_spec,
    apply_attacker_action,
    apply_defender_action,
)
from nighthawk.simulation.defender import ALERT_DECAY_TICKS, decay_alerts
from nighthawk.simulation.events import EventLog
from nighthawk.simulation.models import (
    ActionKind,
    DefenderSkill,
    InformationState,
    InvalidActionError,
    WorldState,
)
from nighthawk.simulation.objectives import all_primary_complete
from nighthawk.simulation.scenario import generate_world
from nighthawk.simulation.scoring import score as score_world

MONITOR_BOOST = 0.15
ACTION_POINTS_PER_TURN = 3


def from_scenario(
    scenario: str,
    seed: int,
    defender: DefenderSkill = DefenderSkill.OPERATOR,
) -> "SimulationEngine":
    """Build an engine over a freshly generated deterministic world."""
    return SimulationEngine(
        generate_world(scenario, seed, defender), defender=defender,
    )


class SimulationEngine:
    """Runs one deterministic offline simulation run."""

    def __init__(self, world: WorldState, log: EventLog | None = None,
                 max_ticks: int = 24,
                 defender: DefenderSkill = DefenderSkill.OPERATOR) -> None:
        self.world = world
        self.log = log if log is not None else EventLog()
        self.max_ticks = max_ticks
        self.finished = False
        self.outcome: str | None = None  # completed | time_expired
        self._monitor_boost = 0.0
        self._pending_actions: list[dict] = []  # attacker actions this tick
        self._attacker_points = ACTION_POINTS_PER_TURN
        self._defender_points = ACTION_POINTS_PER_TURN
        self._defender = defender
        self._scenario = world.scenario_id
        self._seed = world.seed
        self._checkpoints: list[dict] = []  # undo stack (snapshot dicts)

    # ---- introspection ------------------------------------------------- #

    @property
    def tick(self) -> int:
        return self.world.tick

    @property
    def last_seq(self) -> int:
        return self.log.last_seq

    @property
    def attacker_action_points(self) -> int:
        return self._attacker_points

    @property
    def defender_action_points(self) -> int:
        return self._defender_points

    def state_hash(self) -> str:
        return self.world.state_hash()

    # ---- snapshot / restore --------------------------------------------- #

    def snapshot(self) -> dict:
        """Full restore point: world state plus engine bookkeeping."""
        return {
            "world": self.world.to_dict(),
            "events": self.log.to_list(),
            "finished": self.finished,
            "outcome": self.outcome,
            "max_ticks": self.max_ticks,
            "pending_actions": [
                {**action, "kind": action["kind"].value}
                for action in self._pending_actions
            ],
            "attacker_points": self._attacker_points,
            "defender_points": self._defender_points,
        }

    def restore(self, snap: dict) -> None:
        self.world = WorldState.from_dict(snap["world"])
        self.log = EventLog.from_list(snap.get("events") or [])
        self.finished = bool(snap["finished"])
        self.outcome = snap["outcome"]
        self.max_ticks = int(snap["max_ticks"])
        self._monitor_boost = 0.0
        self._pending_actions = [
            {**action, "kind": ActionKind(action["kind"])}
            for action in snap.get("pending_actions", [])
        ]
        self._attacker_points = int(
            snap.get("attacker_points", ACTION_POINTS_PER_TURN)
        )
        self._defender_points = int(
            snap.get("defender_points", ACTION_POINTS_PER_TURN)
        )

    def _require_active(self) -> None:
        """Reject actions on a finished run without mutating anything."""
        if self.finished:
            raise InvalidActionError(
                f"Run is already finished (outcome: {self.outcome})."
            )

    # ---- public API ------------------------------------------------------ #

    def attacker_act(self, kind: ActionKind, target: str | None = None) -> dict:
        """Apply one attacker action. Raises InvalidActionError without mutating."""
        self._require_active()
        entry = action_spec(kind)
        if entry.actor != "attacker":
            raise InvalidActionError(f"{kind.value} is not an attacker action.")
        if entry.cost > self._attacker_points:
            raise InvalidActionError(
                f"Not enough attacker action points for {kind.value}; "
                f"need {entry.cost}, have {self._attacker_points}."
            )
        info = apply_attacker_action(self.world, kind, target)
        self._attacker_points -= entry.cost
        self._pending_actions.append(
            {"kind": kind, "target": target, "tick": self.world.tick}
        )
        self._log_action("attacker", info, entry.cost)
        return info

    def defender_act(self, kind: ActionKind, target: str | None = None) -> dict:
        """Apply one defender action. Raises InvalidActionError without mutating."""
        self._require_active()
        entry = action_spec(kind)
        if entry.actor != "defender":
            raise InvalidActionError(f"{kind.value} is not a defender action.")
        if entry.cost > self._defender_points:
            raise InvalidActionError(
                f"Not enough defender action points for {kind.value}; "
                f"need {entry.cost}, have {self._defender_points}."
            )
        info = apply_defender_action(self.world, kind, target)
        self._defender_points -= entry.cost
        if kind is ActionKind.MONITOR:
            self._monitor_boost = MONITOR_BOOST
        self._log_action("defender", info, entry.cost)
        return info

    def end_turn(self) -> int:
        """Run detection for this tick's attacker actions, advance the tick.
        Returns the tick number just completed."""
        self._require_active()
        self._push_checkpoint()
        completed_tick = self.tick_end(self._pending_actions)
        self._pending_actions = []
        self._attacker_points = ACTION_POINTS_PER_TURN
        self._defender_points = ACTION_POINTS_PER_TURN
        self._apply_decay(completed_tick)
        if self._check_terminal():
            return completed_tick
        self.world.tick += 1
        if self.world.tick >= self.max_ticks:
            self.finished = True
            self.outcome = "time_expired"
            self.log.append(
                self.world.tick, "world", "run.end",
                f"Tick budget exhausted; run ends with outcome '{self.outcome}'.",
            )
        return completed_tick

    def run_to_completion(self) -> dict:
        """Drive ticks until a terminal condition; returns the scorecard."""
        while not self.finished:
            self.end_turn()
        return self.score()

    # ---- replay / UX primitives ------------------------------------------ #

    def step(self) -> int:
        """Advance exactly one tick (alias for end_turn / pause-and-step)."""
        return self.end_turn()

    def restart(self) -> "SimulationEngine":
        """Rebuild an identical world from the stored scenario+seed, dropping
        all progress — the same seed always reproduces the same run."""
        self.world = generate_world(self._scenario, self._seed, self._defender)
        self.log = EventLog()
        self.finished = False
        self.outcome = None
        self._monitor_boost = 0.0
        self._pending_actions = []
        self._attacker_points = ACTION_POINTS_PER_TURN
        self._defender_points = ACTION_POINTS_PER_TURN
        self._checkpoints = []
        return self

    def undo(self) -> bool:
        """Rewind to the start of the previous tick. Returns False when the
        rewind stack is empty."""
        if not self._checkpoints:
            return False
        self.restore(self._checkpoints.pop())
        return True

    def replay_events(
        self, start_seq: int = 1, end_seq: int | None = None,
    ) -> list[dict]:
        """Event dicts in the inclusive [start_seq, end_seq] range."""
        out = []
        for e in self.log.all():
            if e.seq < start_seq:
                continue
            if end_seq is not None and e.seq > end_seq:
                break
            out.append(e.to_dict())
        return out

    def _push_checkpoint(self) -> None:
        self._checkpoints.append(self.snapshot())
        if len(self._checkpoints) > 64:
            self._checkpoints.pop(0)

    def _apply_decay(self, tick: int) -> list[dict]:
        """Let unattended alerts age one confidence level; log each change."""
        changes = decay_alerts(self.world, tick, ALERT_DECAY_TICKS)
        for change in changes:
            if change["closed"]:
                self.log.append(
                    tick, "world", "alert.decayed",
                    f"Alert {change['id']} closed after going stale.",
                    {"alert_id": change["id"], "closed": True},
                )
            else:
                self.log.append(
                    tick, "world", "alert.decayed",
                    f"Alert {change['id']} weakened to {change['new']}.",
                    {"alert_id": change["id"], "new": change["new"]},
                )
        return changes

    # ---- internals ------------------------------------------------------- #

    def tick_end(self, pending: list[dict]) -> int:
        """Detection for this tick's attacker actions; returns the tick used."""
        tick = self.world.tick
        boost = self._monitor_boost
        self._monitor_boost = 0.0
        rng = random.Random(f"{self.world.state_hash()}")
        for action in pending:
            kind: ActionKind = action["kind"]
            target = action["target"] or ""
            for alert in detection_rolls(self.world, rng, kind, target, tick, boost):
                self.world.alerts.append(alert)
                self.log.append(
                    tick, "world", "alert.raised", alert.description,
                    {"alert_id": alert.id, "confidence": alert.confidence.value,
                     "target": alert.target_id},
                )
        return tick

    def _log_action(self, actor: str, info: dict, cost: int) -> None:
        kind_str = info["kind"]
        tick = self.world.tick
        target = info["target"]
        self.log.append(
            tick, actor, "action.ok",
            f"{actor} {kind_str}" + (f" {target}" if target else ""),
            {"kind": kind_str, "target": target,
             "changed": info.get("changed", [])},
        )
        self.world.action_log.append(
            {"tick": tick, "actor": actor, "kind": kind_str,
             "target": target, "cost": cost}
        )

    def _check_terminal(self) -> bool:
        primaries = [o for o in self.world.objectives if o.is_primary]
        if primaries and all_primary_complete(self.world):
            self.finished = True
            self.outcome = "completed"
            self.log.append(
                self.world.tick, "world", "run.complete",
                "All primary objectives complete.",
            )
        return self.finished

    def score(self) -> dict:
        ticks_used = min(self.world.tick + 1, self.max_ticks)
        card = score_world(self.world, ticks_used)
        card["outcome"] = self.outcome
        card["ticks_used"] = ticks_used
        return card
