"""WebSocket event streaming per campaign.

Clients receive every normalized event (lifecycle, discovery, findings)
emitted by services for the subscribed campaign. A heartbeat comment keeps
intermediaries from closing idle connections; a gap in `seq` values tells
the client to refetch state after a reconnect.
"""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from nighthawk.api.deps import get_event_hub
from nighthawk.events import EventHub

router = APIRouter(tags=["events"])

HEARTBEAT_SECONDS = 2.0


@router.websocket("/ws/campaigns/{campaign_id}")
async def campaign_events(websocket: WebSocket, campaign_id: str) -> None:
    hub: EventHub = get_event_hub()
    await websocket.accept()
    queue = hub.subscribe(campaign_id)
    try:
        while True:
            try:
                event = await asyncio.wait_for(
                    queue.get(), timeout=HEARTBEAT_SECONDS
                )
                await websocket.send_json(event.to_ws_dict())
            except asyncio.TimeoutError:
                # heartbeat — also surfaces dead connections
                await websocket.send_text("#hb")
    except WebSocketDisconnect:
        pass
    finally:
        hub.unsubscribe(campaign_id, queue)
