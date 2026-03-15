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
from app.middleware.request_id import get_request_id
from app.utils.logging_context import bind_request_context, get_request_id_context, log_extra
from app.utils.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/stream",
    tags=["Streaming"],
    dependencies=[Depends(bind_request_context)],
)
_pubsub = RedisPubSub()


async def event_generator(job_id: str, request: Request) -> AsyncGenerator[dict, None]:
    channel = f"job:{job_id}"
    request_id = get_request_id(request)
    try:
        from app.middleware.prometheus_metrics import MetricsManager
    except Exception:
        MetricsManager = None
    if MetricsManager:
        MetricsManager.sse_connection_open()
    connected_event = make_event(
        "connected",
        job_id=job_id,
        request_id=request_id,
        payload={"message": f"Connected to stream for job {job_id}"},
    )
    yield {"event": "connected", "data": json.dumps(connected_event)}
    try:
        async for event in _pubsub.subscribe(channel):
            if await request.is_disconnected():
                logger.info("Client disconnected from stream %s", job_id, extra=log_extra(job_id=job_id))
                break
            event_type = event.get("event_type") or "message"
            yield {"event": event_type, "data": json.dumps(event)}
    finally:
        if MetricsManager:
            MetricsManager.sse_connection_closed()


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
    request_id = data.get("request_id") or get_request_id_context()
    if request_id:
        data = {**data, "request_id": request_id}
    event = make_event(
        event_type,
        job_id=str(job_id),
        request_id=request_id,
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
