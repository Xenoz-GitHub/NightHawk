"""Phase 6: mission packs, scoring/objective resolution, replay primitives."""

import pytest

from nighthawk.simulation import (
    ActionKind,
    InformationState,
    ObjectiveKind,
    SimAlert,
    from_mission,
    from_scenario,
    list_missions,
    list_scenarios,
    mission_report,
)
from nighthawk.simulation.missions import MISSIONS


class TestMissionCatalogue:
    def test_catalogue_has_six_missions(self):
        assert sorted(MISSIONS) == sorted(list_missions())
        assert len(MISSIONS) == 6

    def test_every_mission_maps_to_a_real_scenario(self):
        scenarios = set(list_scenarios())
        for mission in MISSIONS.values():
            assert mission.scenario in scenarios
            assert mission.briefing.strip()
            assert mission.time_limit > 0
            assert mission.defender is not None

    def test_every_mission_has_at_least_one_primary(self):
        for mission in MISSIONS.values():
            assert any(o.is_primary for o in mission.objectives)

    def test_unknown_mission_raises(self):
        with pytest.raises(KeyError):
            from_mission("nope", 1)


class TestFromMission:
    def test_configures_engine(self):
        for mission_id in list_missions():
            eng = from_mission(mission_id, 7)
            assert eng.max_ticks == MISSIONS[mission_id].time_limit
            assert eng._defender == MISSIONS[mission_id].defender
            assert [o.id for o in eng.world.objectives] == \
                [o.id for o in MISSIONS[mission_id].objectives]

    def test_objective_kinds_are_engine_scored(self):
        eng = from_mission("sentry", 7)
        kinds = [o.kind for o in eng.world.objectives]
        assert ObjectiveKind.DISCOVER_HOSTS in kinds
        assert ObjectiveKind.COLLECT_EVIDENCE in kinds


class TestMissionDeterminism:
    def test_identical_runs_identical_state(self):
        a = from_mission("quiet_rush", 42)
        b = from_mission("quiet_rush", 42)
        a.attacker_act(ActionKind.DISCOVER)
        a.step()
        b.attacker_act(ActionKind.DISCOVER)
        b.step()
        assert a.state_hash() == b.state_hash()
        assert a.log.to_list() == b.log.to_list()

    def test_different_seeds_diverge(self):
        a = from_mission("clinical", 42)
        b = from_mission("clinical", 43)
        a.attacker_act(ActionKind.DISCOVER)
        a.step()
        b.attacker_act(ActionKind.DISCOVER)
        b.step()
        assert a.state_hash() != b.state_hash()

    def test_full_replay_identical_scorecards(self):
        def run(seed):
            eng = from_mission("sentry", seed)
            card = eng.run_to_completion()
            return card, eng.log.to_list()
        assert run(11) == run(11)
class TestObjectiveResolution:
    def test_satisfied_primaries_mark_run_complete(self):
        eng = from_mission("sentry", 3)
        world = eng.world
        for host in world.hosts[:3]:
            host.visibility = InformationState.OBSERVED
        for vuln in world.vulnerabilities[:2]:
            vuln.visibility = InformationState.CONFIRMED
        for i in range(2):
            world.collected_evidence.append({
                "id": f"e{i+1}",
                "host_id": world.hosts[i].id,
                "vuln_id": world.vulnerabilities[i].id,
                "tick": 0,
            })
        eng.step()
        assert eng.finished
        assert eng.outcome == "completed"

    def test_report_shape(self):
        eng = from_mission("sentry", 3)
        eng.run_to_completion()
        report = mission_report(eng, MISSIONS["sentry"])
        assert set(report) == {
            "mission", "title", "briefing", "scenario", "difficulty",
            "outcome", "ticks_used", "score", "objectives",
        }
        assert report["mission"] == "sentry"
        assert "m1-recon" in report["objectives"]


class TestReplayPrimitives:
    def test_step_advances_exactly_one_tick(self):
        eng = from_scenario("small_office", 5)
        assert eng.tick == 0
        eng.attacker_act(ActionKind.DISCOVER)
        eng.step()
        assert eng.tick == 1

    def test_undo_rewinds_to_pre_tick_state(self):
        eng = from_scenario("small_office", 5)
        eng.attacker_act(ActionKind.DISCOVER)
        pre = eng.state_hash()
        eng.step()
        assert eng.tick == 1
        assert eng.undo()
        assert eng.tick == 0
        assert eng.state_hash() == pre

    def test_undo_stack_exhausts(self):
        eng = from_scenario("small_office", 5)
        assert not eng.undo()
        eng.step()
        assert eng.undo()
        assert not eng.undo()

    def test_restart_rebuilds_fresh_identical_world(self):
        eng = from_scenario("small_office", 9)
        eng.attacker_act(ActionKind.DISCOVER)
        eng.step()
        eng.restart()
        fresh = from_scenario("small_office", 9)
        assert eng.state_hash() == fresh.state_hash()
        assert eng.tick == 0

    def test_restart_after_finish_clears_outcome(self):
        eng = from_mission("sentry", 3)
        eng.run_to_completion()
        assert eng.finished
        eng.restart()
        assert not eng.finished
        assert eng.outcome is None

    def test_replay_events_slice(self):
        eng = from_scenario("small_office", 5)
        eng.attacker_act(ActionKind.DISCOVER)
        eng.step()
        eng.attacker_act(ActionKind.INSPECT, "h1")
        eng.step()
        total = eng.log.last_seq
        assert eng.replay_events() == eng.log.to_list()
        assert eng.replay_events(end_seq=total - 1)[-1]["seq"] == total - 1
        assert eng.replay_events(start_seq=total)[0]["seq"] == total


class TestAlertDecayThroughEngine:
    def test_unattended_alert_ages_and_logs(self, monkeypatch):
        import nighthawk.simulation.engine as engine_mod

        monkeypatch.setattr(engine_mod, "ALERT_DECAY_TICKS", 1)
        eng = from_scenario("small_office", 5)
        eng.world.alerts.append(SimAlert(
            id="a1", tick=0, kind="detected.test", target_id="h1",
            confidence=InformationState.CONFIRMED, description="planted",
        ))
        eng.step()   # completed_tick 0 → age 0, no decay
        eng.step()   # completed_tick 1 → age 1 → decay to PROBABLE
        decays = [e for e in eng.log.all() if e.kind == "alert.decayed"]
        assert decays, "no decay events logged"
        assert eng.world.alerts[0].confidence is InformationState.PROBABLE