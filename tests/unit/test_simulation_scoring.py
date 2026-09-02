"""Scoring math: objective points, stealth, efficiency, letter grades."""

import pytest

from nighthawk.simulation import (
    InformationState,
    ObjectiveKind,
    SimAlert,
    generate_world,
)
from nighthawk.simulation.scoring import (
    efficiency_points,
    letter_grade,
    objective_points,
    score,
    stealth_points,
)


@pytest.fixture()
def world():
    return generate_world("small_office", 42)


def _alert(confidence, alert_id="a1"):
    return SimAlert(
        id=alert_id, tick=0, kind="detected.test", target_id="h1",
        confidence=confidence, description="test alert",
    )


class TestStealthPoints:
    def test_fresh_world_full_stealth(self, world):
        assert stealth_points(world) == 300

    def test_confirmed_alert_costs_100(self, world):
        world.alerts.append(_alert(InformationState.CONFIRMED))
        assert stealth_points(world) == 200

    def test_probable_alert_costs_25(self, world):
        world.alerts.append(_alert(InformationState.PROBABLE))
        assert stealth_points(world) == 275

    def test_floors_at_zero(self, world):
        for i in range(5):
            world.alerts.append(_alert(InformationState.CONFIRMED, f"a{i}"))
        assert stealth_points(world) == 0


class TestObjectivePoints:
    def test_fresh_world_scores_only_undetected_bonus(self, world):
        # REMAIN_UNDETECTED pays out immediately on a clean run (300 pts);
        # every other objective requires actual progress.
        undetected = sum(
            1 for o in world.objectives if o.kind is ObjectiveKind.REMAIN_UNDETECTED
        )
        assert objective_points(world) == 300 * undetected

    def test_discovery_scores_per_host(self, world):
        before = objective_points(world)
        discover = next(
            o for o in world.objectives if o.kind is ObjectiveKind.DISCOVER_HOSTS
        )
        for host in world.hosts[: discover.required_count]:
            host.visibility = InformationState.OBSERVED
        gained = objective_points(world) - before
        assert gained == 100 * discover.required_count

    def test_discovery_caps_at_required(self, world):
        discover = next(
            o for o in world.objectives if o.kind is ObjectiveKind.DISCOVER_HOSTS
        )
        for host in world.hosts:  # reveal everything
            host.visibility = InformationState.OBSERVED
        points = objective_points(world)
        assert points < 100 * len(world.hosts) + 100  # capped contribution

    def test_evidence_scores_per_item(self, world):
        world.collected_evidence.append(
            {"id": "e1", "host_id": "h1", "vuln_id": "v1", "tick": 0}
        )
        evidence_obj = next(
            o for o in world.objectives if o.kind is ObjectiveKind.COLLECT_EVIDENCE
        )
        assert objective_points(world) >= 200 * min(1, evidence_obj.required_count)

    def test_undetected_bonus_only_without_confirmed_alerts(self, world):
        world.alerts.append(_alert(InformationState.CONFIRMED))
        points_with_alert = objective_points(world)
        world.alerts.clear()
        assert objective_points(world) > points_with_alert


class TestEfficiencyPoints:
    def test_no_actions_zero(self, world):
        assert efficiency_points(world, 5) == 0

    def test_one_action_per_tick_max(self, world):
        world.action_log.append({"kind": "discover"})  # 1 action
        assert efficiency_points(world, 1) == 150

    def test_slow_runs_score_zero(self, world):
        for i in range(2):
            world.action_log.append({"kind": "x"})
        assert efficiency_points(world, 6) == 0  # 3.0 ticks per action

    def test_midpoint_scores_half(self, world):
        world.action_log.append({"kind": "x"})  # 1 action over 2 ticks
        assert efficiency_points(world, 2) == 75


class TestLetterGrade:
    @pytest.mark.parametrize(
        ("total", "grade"),
        [(2000, "S"), (1600, "A"), (1200, "B"), (800, "C"), (400, "D"), (399, "F")],
    )
    def test_boundaries(self, total, grade):
        assert letter_grade(total) == grade


class TestScoreCard:
    def test_components_sum_to_total(self, world):
        world.alerts.append(_alert(InformationState.PROBABLE))
        world.collected_evidence.append(
            {"id": "e1", "host_id": "h1", "vuln_id": "v1", "tick": 0}
        )
        card = score(world, ticks_used=4)
        assert card["total"] == (
            card["objective_points"] + card["stealth_points"]
            + card["efficiency_points"]
        )
        assert card["grade"] == letter_grade(card["total"])

    def test_same_world_same_score(self, world):
        assert score(world, 3) == score(world, 3)
