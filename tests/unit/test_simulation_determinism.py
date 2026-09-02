"""Determinism: same seed + same actions ⇒ identical hash, log, and score.

Snapshot/restore round-trips must also preserve replay identity.
"""

import pytest

from nighthawk.simulation import (
    ActionKind,
    InformationState,
    SimulationEngine,
    WorldState,
    from_scenario,
    generate_world,
)


def _script(eng: SimulationEngine) -> None:
    """A fixed attacker/defender script over the small_office scenario."""
    info = eng.attacker_act(ActionKind.DISCOVER)
    eng.end_turn()
    target = info["changed"][0]

    eng.attacker_act(ActionKind.INSPECT, target)
    eng.defender_act(ActionKind.MONITOR)
    eng.end_turn()

    eng.attacker_act(ActionKind.FINGERPRINT, target)
    eng.end_turn()

    probable = [
        v for v in eng.world.vulnerabilities
        if v.visibility is InformationState.PROBABLE
    ]
    assert probable, "scenario must expose a fingerprintable vulnerability"
    eng.attacker_act(ActionKind.ANALYZE, probable[0].id)
    eng.end_turn()

    eng.attacker_act(ActionKind.COLLECT_EVIDENCE, target)
    eng.end_turn()


class TestReplayDeterminism:
    def test_same_seed_same_script_identical_world(self):
        a = from_scenario("small_office", 1234)
        b = from_scenario("small_office", 1234)
        _script(a)
        _script(b)
        assert a.state_hash() == b.state_hash()

    def test_same_seed_same_script_identical_event_log(self):
        a = from_scenario("small_office", 1234)
        b = from_scenario("small_office", 1234)
        _script(a)
        _script(b)
        assert a.log.to_list() == b.log.to_list()
        assert [al.id for al in a.world.alerts] == [al.id for al in b.world.alerts]
        assert a.world.action_log == b.world.action_log

    def test_same_seed_identical_scorecards(self):
        a = from_scenario("small_office", 1234)
        b = from_scenario("small_office", 1234)
        card_a = a.run_to_completion()
        card_b = b.run_to_completion()
        assert card_a == card_b

    def test_different_seed_diverges(self):
        a = from_scenario("small_office", 1234)
        b = from_scenario("small_office", 99)
        _script(a)
        _script(b)
        assert a.state_hash() != b.state_hash()


class TestSnapshotRestore:
    def test_restore_reproduces_exact_state(self):
        a = from_scenario("small_office", 1234)
        _script(a)
        snap = a.snapshot()

        b = from_scenario("small_office", 1234)
        b.restore(snap)
        assert b.state_hash() == a.state_hash()
        assert b.log.to_list() == a.log.to_list()
        assert b.finished == a.finished
        assert b.outcome == a.outcome

    def test_restored_engine_continues_deterministically(self):
        a = from_scenario("small_office", 1234)
        _script(a)
        snap = a.snapshot()

        b = from_scenario("small_office", 1234)
        b.restore(snap)
        a.attacker_act(ActionKind.DISCOVER)
        a.end_turn()
        b.attacker_act(ActionKind.DISCOVER)
        b.end_turn()
        assert a.state_hash() == b.state_hash()
        assert a.log.to_list() == b.log.to_list()

    def test_world_round_trip_via_dict(self):
        world = generate_world("small_office", 1234)
        clone = WorldState.from_dict(world.to_dict())
        assert clone.state_hash() == world.state_hash()
