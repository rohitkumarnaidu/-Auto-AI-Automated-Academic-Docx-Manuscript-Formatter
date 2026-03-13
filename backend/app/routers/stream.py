"""
Streaming Response Router
Provides Server-Sent Events (SSE) for real-time agent feedback.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, Request
from sse_starlette.sse import EventSourceResponse

from app.realtime.events import make_event
from app.realtime.pubsub import RedisPubSub
from app.utils.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/stream", tags=["Streaming"])
_pubsub = RedisPubSub()


async def event_generator(job_id: str, request: Request) -> AsyncGenerator[dict, None]:
    channel = f"job:{job_id}"
    connected_event = make_event(
        "connected",
        job_id=job_id,
        payload={"message": f"Connected to stream for job {job_id}"},
    )
    yield {"event": "connected", "data": json.dumps(connected_event)}
    async for event in _pubsub.subscribe(channel):
        if await request.is_disconnected():
            logger.info("Client disconnected from stream %s", job_id)
            break
        event_type = event.get("event_type") or "message"
        yield {"event": event_type, "data": json.dumps(event)}


@router.get("/{job_id}")
async def stream_job_events(
    job_id: str,
    request: Request,
    current_user=Depends(get_current_user),
):
    """
    Stream real-time events for a specific job.
    Requires authentication.
    """
    return EventSourceResponse(event_generator(job_id, request))


def emit_event(job_id: str, event_type: str, data: dict) -> None:
    """
    Emit an event to the job's stream via Redis Pub/Sub.
    Sync-friendly for use in pipeline threads.
    """
    event = make_event(
        event_type,
        job_id=str(job_id),
        stage=data.get("phase") or data.get("stage"),
        progress=data.get("progress"),
        payload=data,
    )
    channel = f"job:{job_id}"
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_pubsub.publish(channel, event))
    except RuntimeError:
        asyncio.run(_pubsub.publish(channel, event))
