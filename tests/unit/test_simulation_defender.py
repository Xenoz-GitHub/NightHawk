"""Defender actions: investigation escalation, containment, monitoring."""

import pytest

from nighthawk.simulation import (
    ActionKind,
    InformationState,
    InvalidActionError,
    SimAlert,
    from_scenario,
)


def make_engine(seed: int = 42):
    return from_scenario("small_office", seed)


def _plant_alert(eng, confidence=InformationState.PROBABLE, alert_id="a1"):
    alert = SimAlert(
        id=alert_id, tick=0, kind="detected.discover", target_id="h1",
        confidence=confidence, description="planted",
    )
    eng.world.alerts.append(alert)
    return alert


class TestInvestigate:
    def test_escalates_probable_to_confirmed(self):
        eng = make_engine()
        alert = _plant_alert(eng)
        eng.defender_act(ActionKind.INVESTIGATE, alert.id)
        assert alert.confidence is InformationState.CONFIRMED
        assert alert.status == "confirmed"

    def test_escalates_unknown_stepwise(self):
        eng = make_engine()
        alert = _plant_alert(eng, InformationState.UNKNOWN)
        eng.defender_act(ActionKind.INVESTIGATE, alert.id)
        assert alert.confidence is InformationState.OBSERVED

    def test_unknown_alert_rejected(self):
        eng = make_engine()
        with pytest.raises(InvalidActionError, match="Unknown alert"):
            eng.defender_act(ActionKind.INVESTIGATE, "nope")

    def test_already_confirmed_rejected(self):
        eng = make_engine()
        alert = _plant_alert(eng, InformationState.CONFIRMED)
        with pytest.raises(Exception, match="already confirmed"):
            eng.defender_act(ActionKind.INVESTIGATE, alert.id)


class TestContain:
    def test_severs_links_and_evicts_attacker(self):
        eng = make_engine()
        info = eng.attacker_act(ActionKind.DISCOVER)
        eng.end_turn()
        host = info["changed"][0]
        hobj = next(h for h in eng.world.hosts if h.id == host)
        eng.attacker_act(ActionKind.MOVE_TO, host)
        eng.end_turn()
        assert eng.world.attacker_position == host
        hobj.compromised = True  # simulate an established foothold

        result = eng.defender_act(ActionKind.CONTAIN, host)
        assert any(str(c).endswith(":evicted") for c in result["changed"])
        assert eng.world.attacker_position is None
        assert not hobj.compromised
        assert not any(
            link.traversable
            for link in eng.world.links
            if host in (link.from_id, link.to_id)
        )

    def test_unknown_host_rejected(self):
        eng = make_engine()
        with pytest.raises(Exception, match="Unknown host"):
            eng.defender_act(ActionKind.CONTAIN, "ghost")


class TestMonitor:
    def test_boost_applies_once_then_clears(self):
        eng = make_engine()
        eng.defender_act(ActionKind.MONITOR)
        assert eng._monitor_boost == pytest.approx(0.15)
        eng.end_turn()
        assert eng._monitor_boost == 0.0

    def test_monitor_with_target_rejected(self):
        eng = make_engine()
        with pytest.raises(Exception, match="no target"):
            eng.defender_act(ActionKind.MONITOR, "h1")
