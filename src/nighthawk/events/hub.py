"""In-process event hub for fan-out to WebSocket subscribers.

The hub is intentionally simple: an in-memory pub/sub keyed by campaign id.
Single-process deployments (the current architecture) share one hub; the
sequence numbers carried by events let multi-process deployments add a
transport later without changing the client contract.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any

from nighthawk.events.models import Event
from nighthawk.logging.setup import get_logger

logger = get_logger("events")


class EventHub:
    """Async pub/sub hub. Each subscriber gets an unbounded queue."""

    def __init__(self, max_queue: int = 1000) -> None:
        self._subscribers: dict[str, set[asyncio.Queue[Event]]] = defaultdict(set)
        self._max_queue = max_queue

    def subscribe(self, campaign_id: str) -> asyncio.Queue[Event]:
        """Subscribe to all events for a campaign."""
        queue: asyncio.Queue[Event] = asyncio.Queue(maxsize=self._max_queue)
        self._subscribers[campaign_id].add(queue)
        return queue

    def unsubscribe(self, campaign_id: str, queue: asyncio.Queue[Event]) -> None:
        """Remove a subscription; drops the campaign bucket when empty."""
        queues = self._subscribers.get(campaign_id)
        if queues is not None:
            queues.discard(queue)
            if not queues:
                self._subscribers.pop(campaign_id, None)

    def publish(self, campaign_id: str, event: Event) -> None:
        """Fan an event out to all current subscribers (non-blocking).

        Slow subscribers whose queue is full get the event dropped and a
        warning logged — a UI lagging behind must never block a scan.
        """
        for queue in list(self._subscribers.get(campaign_id, ())):
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                logger.warning(
                    "event_queue_overflow", campaign=campaign_id, event_type=event.type.value
                )

    def subscriber_count(self, campaign_id: str) -> int:
        """Number of live subscribers for a campaign (used by tests/ops)."""
        return len(self._subscribers.get(campaign_id, ()))


HUB = EventHub()
"""Process-wide hub instance shared by services and the WS endpoint."""