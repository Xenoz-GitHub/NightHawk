"""Defender AI depth: presets, detection curves, alert decay, autopilot."""

import random

import pytest

from nighthawk.simulation import (
    ActionKind,
    DefenderSkill,
    InformationState,
    SimAlert,
    choose_defender_action,
    decay_alerts,
    defender_turn,
    from_scenario,
    generate_world,
)
from nighthawk.simulation.actions import DETECTION_CURVES, detection_curve
from nighthawk.simulation.defender import ALERT_DECAY_TICKS, SKILL_PRESETS


def _alert(confidence, alert_id="a1", tick=0):
    return SimAlert(
        id=alert_id, tick=tick, kind="detected.test", target_id="h1",
        confidence=confidence, description="planted",
    )


class TestSkillPresets:
    def test_all_six_presets_present(self):
        assert set(SKILL_PRESETS) == set(DefenderSkill)

    def test_difficulty_curve_is_monotonic(self):
        multipliers = [SKILL_PRESETS[s].detection_multiplier for s in DefenderSkill]
        assert multipliers == sorted(multipliers)
        assert len(set(multipliers)) == len(multipliers)

    def test_higher_tiers_respond_to_probable(self):
        assert SKILL_PRESETS[DefenderSkill.NIGHTHAWK].respond_if_probable
        assert not SKILL_PRESETS[DefenderSkill.RECRUIT].respond_if_probable


class TestDetectionCurves:
    def test_curve_lookup(self):
        assert detection_curve("edr", ActionKind.COLLECT_EVIDENCE) == pytest.approx(0.55)
        assert detection_curve("backups", ActionKind.DISCOVER) == 0.0

    def test_all_values_in_unit_interval(self):
        for control, mapping in DETECTION_CURVES.items():
            for action, prob in mapping.items():
                assert 0.0 <= prob <= 1.0, (control, action)

    def test_controls_only_detect_actions_with_a_curve(self):
        world = generate_world("saas_company", 3)
        for control in world.controls:
            for action in control.detects:
                assert detection_curve(control.kind, action) > 0.0

    def test_key_actions_are_detectable(self):
        detected = {
            (control, action)
            for control, mapping in DETECTION_CURVES.items()
            for action, prob in mapping.items()
            if prob > 0.0
        }
        for action in (ActionKind.DISCOVER, ActionKind.ENUMERATE,
                       ActionKind.FINGERPRINT, ActionKind.ANALYZE,
                       ActionKind.COLLECT_EVIDENCE, ActionKind.MOVE_TO):
            assert any(c == action for _, c in detected), action


class TestDecay:
    def test_confirmed_drops_to_probable_after_period(self):
        world = generate_world("small_office", 1)
        alert = _alert(InformationState.CONFIRMED, tick=0)
        world.alerts.append(alert)
        changes = decay_alerts(world, current_tick=ALERT_DECAY_TICKS)
        assert alert.confidence is InformationState.PROBABLE
        assert changes[0]["new"] == "probable"
        assert not changes[0]["closed"]

    def test_observed_alert_closes_after_period(self):
        world = generate_world("small_office", 1)
        world.alerts.append(_alert(InformationState.OBSERVED, tick=0))
        changes = decay_alerts(world, current_tick=ALERT_DECAY_TICKS)
        assert changes[0]["closed"] is True
        assert world.alerts == []

    def test_fresh_alerts_untouched(self):
        world = generate_world("small_office", 1)
        world.alerts.append(_alert(InformationState.PROBABLE, tick=0))
        decay_alerts(world, current_tick=1)
        assert world.alerts[0].confidence is InformationState.PROBABLE

    def test_decay_is_deterministic(self):
        a = generate_world("small_office", 1)
        b = generate_world("small_office", 1)
        a.alerts.append(_alert(InformationState.CONFIRMED, tick=0))
        b.alerts.append(_alert(InformationState.CONFIRMED, tick=0))
        assert decay_alerts(a, 5) == decay_alerts(b, 5)
class TestChooseDefenderAction:
    def test_contains_compromised_host(self):
        eng = from_scenario("small_office", 4)
        eng.world.hosts[0].compromised = True
        rng = random.Random(0)
        assert choose_defender_action(eng.world, DefenderSkill.OPERATOR, rng) \
            is ActionKind.CONTAIN

    def test_passes_on_silent_world(self):
        eng = from_scenario("small_office", 4)
        assert choose_defender_action(
            eng.world, DefenderSkill.OPERATOR, random.Random(0)) is None

    def test_operator_investigates_probable_alert(self):
        eng = from_scenario("small_office", 4)
        eng.world.alerts.append(_alert(InformationState.PROBABLE))
        assert choose_defender_action(
            eng.world, DefenderSkill.OPERATOR, random.Random(0)) \
            is ActionKind.INVESTIGATE

    def test_recruit_only_reacts_to_confirmed(self):
        eng = from_scenario("small_office", 4)
        eng.world.alerts.append(_alert(InformationState.PROBABLE))
        assert choose_defender_action(
            eng.world, DefenderSkill.RECRUIT, random.Random(0)) \
            is ActionKind.MONITOR

    def test_respects_response_latency(self):
        eng = from_scenario("small_office", 4)
        eng.world.alerts.append(_alert(InformationState.CONFIRMED, tick=0))
        # latency 2 ⇒ at tick 0 the confirmed alert is not yet investigated
        assert choose_defender_action(
            eng.world, DefenderSkill.RECRUIT, random.Random(0)) \
            is ActionKind.MONITOR


class TestDefenderTurn:
    def test_investigates_and_escalates_through_engine(self):
        eng = from_scenario("small_office", 4)
        eng.world.alerts.append(_alert(InformationState.PROBABLE))
        info = defender_turn(eng, DefenderSkill.OPERATOR, random.Random(0))
        assert info is not None
        assert info["kind"] == "investigate"
        assert eng.world.alerts[0].confidence is InformationState.CONFIRMED

    def test_containment_evicts_attacker(self):
        eng = from_scenario("small_office", 4)
        target = eng.world.hosts[0].id
        eng.world.hosts[0].compromised = True
        eng.world.attacker_position = target
        info = defender_turn(eng, DefenderSkill.OPERATOR, random.Random(0))
        assert info is not None
        assert info["kind"] == "contain"
        assert eng.world.attacker_position is None

    def test_returns_none_when_no_work(self):
        eng = from_scenario("small_office", 4)
        assert defender_turn(eng, DefenderSkill.OPERATOR, random.Random(0)) is None

    def test_illegal_choice_is_swallowed(self):
        eng = from_scenario("small_office", 4)
        eng.finished = True
        assert defender_turn(eng, DefenderSkill.OPERATOR, random.Random(0)) is None

    def test_autopilot_is_reproducible(self):
        def run(seed):
            eng = from_scenario("small_office", 4)
            eng.world.alerts.append(_alert(InformationState.PROBABLE))
            out = []
            for _ in range(3):
                out.append(defender_turn(eng, DefenderSkill.NIGHTHAWK,
                                         random.Random(seed)))
                eng.step()
            return [o and o["kind"] for o in out]
        assert run(7) == run(7)