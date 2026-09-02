"""Append-only simulation event log with filters."""

from __future__ import annotations

from nighthawk.simulation.models import SimulationEvent


class EventLog:
    """Ordered, append-only log. Sequence numbers are 1-based and monotonic."""

    def __init__(self) -> None:
        self._events: list[SimulationEvent] = []
        self._seq = 0

    def append(
        self, tick: int, actor: str, kind: str, message: str,
        payload: dict | None = None,
    ) -> SimulationEvent:
        self._seq += 1
        event = SimulationEvent(
            seq=self._seq, tick=tick, actor=actor, kind=kind,
            message=message, payload=payload or {},
        )
        self._events.append(event)
        return event

    @property
    def last_seq(self) -> int:
        return self._seq

    def all(self) -> list[SimulationEvent]:
        return list(self._events)

    def since(self, seq: int) -> list[SimulationEvent]:
        """Events with sequence numbers strictly greater than `seq`."""
        return [e for e in self._events if e.seq > seq]

    def by_actor(self, actor: str) -> list[SimulationEvent]:
        return [e for e in self._events if e.actor == actor]

    def by_kind(self, kind: str) -> list[SimulationEvent]:
        return [e for e in self._events if e.kind == kind]

    def to_list(self) -> list[dict]:
        return [e.to_dict() for e in self._events]

    @classmethod
    def from_list(cls, events: list[dict]) -> "EventLog":
        """Rebuild a log from `to_list()` output, preserving sequence numbers."""
        log = cls()
        for e in events:
            log._events.append(
                SimulationEvent(
                    seq=int(e["seq"]),
                    tick=int(e["tick"]),
                    actor=e["actor"],
                    kind=e["kind"],
                    message=e["message"],
                    payload=dict(e.get("payload") or {}),
                )
            )
            log._seq = max(log._seq, int(e["seq"]))
        return log
