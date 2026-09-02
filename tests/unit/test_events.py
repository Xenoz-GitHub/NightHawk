"""EventHub fan-out and Event wire-format tests."""

import uuid
from datetime import datetime, timezone

from nighthawk.events import Event, EventHub, EventType


def _event(seq: int, campaign_id: uuid.UUID | None = None) -> Event:
    return Event(
        type=EventType.CAMPAIGN_CREATED,
        campaign_id=campaign_id or uuid.uuid4(),
        seq=seq,
        message="test",
        payload={"k": "v"},
    )


class TestEventHub:
    def test_publish_fans_out_to_all_subscribers(self):
        hub = EventHub()
        q1 = hub.subscribe("c1")
        q2 = hub.subscribe("c1")
        event = _event(1)
        hub.publish("c1", event)
        assert q1.get_nowait() is event
        assert q2.get_nowait() is event

    def test_unsubscribe_stops_delivery(self):
        hub = EventHub()
        queue = hub.subscribe("c1")
        hub.unsubscribe("c1", queue)
        hub.publish("c1", _event(1))  # must not raise
        assert queue.empty()

    def test_campaigns_are_isolated(self):
        hub = EventHub()
        qa = hub.subscribe("a")
        qb = hub.subscribe("b")
        hub.publish("a", _event(1))
        assert not qa.empty()
        assert qb.empty()

    def test_unsubscribe_unknown_queue_is_noop(self):
        hub = EventHub()
        hub.unsubscribe("c1", __import__("queue").Queue())  # no raise


class TestEvent:
    def test_to_ws_dict_shape(self):
        data = _event(7).to_ws_dict()
        assert data["seq"] == 7
        assert data["type"] == "campaign.created"
        assert data["message"] == "test"
        assert data["payload"] == {"k": "v"}
        assert "timestamp" in data
        assert "campaign_id" in data
