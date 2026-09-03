"""Simulation engine tests: turn flow, action validation, run lifecycle.

All runs are offline and deterministic (fixed seeds); no network I/O anywhere.
"""

import pytest

from nighthawk.simulation import (
    ActionKind,
    InvalidActionError,
    SimulationEngine,
    from_scenario,
    generate_world,
)
from nighthawk.simulation.models import (
    InformationState,
    SimAlert,
)


def make_engine(seed: int = 42) -> SimulationEngine:
    return from_scenario("small_office", seed)


class TestActionValidation:
    def test_discover_rejects_target(self):
        eng = make_engine()
        with pytest.raises(InvalidActionError, match="no target"):
            eng.attacker_act(ActionKind.DISCOVER, "h1")

    def test_inspect_undiscovered_host_rejected(self):
        eng = make_engine()
        with pytest.raises(InvalidActionError, match="not been discovered"):
            eng.attacker_act(ActionKind.INSPECT, "h2")

    def test_wrong_actor_rejected(self):
        eng = make_engine()
        with pytest.raises(InvalidActionError, match="not a defender action"):
            eng.defender_act(ActionKind.DISCOVER)

    def test_unknown_host_rejected(self):
        eng = make_engine()
        with pytest.raises(InvalidActionError, match="Unknown host"):
            eng.attacker_act(ActionKind.INSPECT, "no-such-host")

    def test_failed_action_does_not_mutate(self):
        eng = make_engine()
        before = eng.state_hash()
        with pytest.raises(InvalidActionError):
            eng.attacker_act(ActionKind.INSPECT, "no-such-host")
        assert eng.state_hash() == before

    def test_action_points_limit_actions_per_turn(self):
        eng = make_engine()
        eng.attacker_act(ActionKind.DISCOVER)
        eng.attacker_act(ActionKind.INSPECT, "h1")
        before = eng.state_hash()
        with pytest.raises(InvalidActionError, match="action points"):
            eng.attacker_act(ActionKind.ENUMERATE, "h1")
        assert eng.state_hash() == before

    def test_action_points_reset_after_turn(self):
        eng = make_engine()
        eng.attacker_act(ActionKind.DISCOVER)
        eng.attacker_act(ActionKind.INSPECT, "h1")
        eng.end_turn()
        eng.attacker_act(ActionKind.ENUMERATE, "h1")

    def test_detection_checks_each_action_in_a_turn(self, monkeypatch):
        eng = make_engine()
        calls = []

        def detect(world, rng, kind, target, tick, boost):
            calls.append((kind, target))
            return []

        monkeypatch.setattr("nighthawk.simulation.engine.detection_rolls", detect)
        eng.attacker_act(ActionKind.DISCOVER)
        eng.attacker_act(ActionKind.INSPECT, "h1")
        eng.end_turn()
        assert calls == [
            (ActionKind.DISCOVER, ""),
            (ActionKind.INSPECT, "h1"),
        ]

    def test_undo_restores_action_points(self):
        eng = make_engine()
        eng.attacker_act(ActionKind.DISCOVER)
        eng.end_turn()
        eng.attacker_act(ActionKind.INSPECT, "h1")
        eng.end_turn()
        assert eng.undo()
        eng.attacker_act(ActionKind.INSPECT, "h1")


class TestTurnFlow:
    def test_full_attack_path(self):
        eng = make_engine()
        info = eng.attacker_act(ActionKind.DISCOVER)
        assert info["changed"] == ["h1"]
        eng.end_turn()
        assert eng.world.hosts[0].visibility.at_least(InformationState.OBSERVED)

        eng.attacker_act(ActionKind.FINGERPRINT, "h1")
        eng.end_turn()
        vuln = next(
            v for v in eng.world.vulnerabilities
            if v.visibility is InformationState.PROBABLE
        )
        eng.attacker_act(ActionKind.ANALYZE, vuln.id)
        eng.end_turn()
        assert vuln.visibility is InformationState.CONFIRMED

        eng.attacker_act(ActionKind.COLLECT_EVIDENCE, "h1")
        eng.end_turn()
        assert len(eng.world.collected_evidence) == 1
        assert eng.world.hosts[0].compromised

    def test_event_log_is_monotonic(self):
        eng = make_engine()
        eng.attacker_act(ActionKind.DISCOVER)
        eng.end_turn()
        seqs = [e.seq for e in eng.log.all()]
        assert seqs == sorted(seqs)
        assert seqs[0] == 1
        assert eng.last_seq == len(seqs)

    def test_action_log_records_costs(self):
        eng = make_engine()
        eng.attacker_act(ActionKind.DISCOVER)
        eng.end_turn()
        assert eng.world.action_log[0]["actor"] == "attacker"
        assert eng.world.action_log[0]["kind"] == "discover"
        assert isinstance(eng.world.action_log[0]["cost"], int)

    def test_time_budget_expires(self):
        world = generate_world("small_office", 42)
        eng = SimulationEngine(world, max_ticks=3)
        card = eng.run_to_completion()
        assert eng.finished
        assert eng.outcome == "time_expired"
        assert card["ticks_used"] == 3

    def test_actions_rejected_after_finish(self):
        eng = SimulationEngine(generate_world("small_office", 42), max_ticks=2)
        eng.run_to_completion()
        with pytest.raises(InvalidActionError, match="finished"):
            eng.attacker_act(ActionKind.DISCOVER)


class TestDetectionPlumbing:
    def test_pending_detections_flush_on_end_turn(self, monkeypatch):
        eng = make_engine()
        alert = SimAlert(
            id="a1", tick=0, kind="detected.discover", target_id="h1",
            confidence=InformationState.OBSERVED, description="forced",
        )
        monkeypatch.setattr(
            "nighthawk.simulation.engine.detection_rolls",
            lambda world, rng, kind, target, tick, boost: [alert],
        )
        eng.attacker_act(ActionKind.DISCOVER)
        eng.end_turn()
        assert eng.world.alerts == [alert]
        assert any(e.kind == "alert.raised" for e in eng.log.all())

    def test_monitor_boost_consumed_each_turn(self):
        eng = make_engine()
        eng.defender_act(ActionKind.MONITOR)
        assert eng._monitor_boost == 0.15
        eng.end_turn()
        assert eng._monitor_boost == 0.0


class TestRunToCompletion:
    def test_scorecard_shape(self):
        eng = from_scenario("small_office", 7)
        card = eng.run_to_completion()
        assert set(card) == {
            "objective_points", "stealth_points", "efficiency_points",
            "total", "grade", "outcome", "ticks_used",
        }
        assert card["total"] == (
            card["objective_points"] + card["stealth_points"]
            + card["efficiency_points"]
        )
        assert card["outcome"] == "time_expired"

    def test_fresh_world_scores_full_stealth(self):
        world = generate_world("small_office", 42)
        eng = SimulationEngine(world)
        eng.end_turn()  # one quiet tick, no attacker actions
        assert eng.score()["stealth_points"] == 300
