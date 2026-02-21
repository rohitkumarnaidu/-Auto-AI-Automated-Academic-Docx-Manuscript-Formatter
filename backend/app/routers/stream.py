"""
Streaming Response Router
Provides Server-Sent Events (SSE) for real-time agent feedback.
"""

import asyncio
import json
import logging
import time
from typing import AsyncGenerator, Dict
from fastapi import APIRouter, Request, HTTPException, Depends
from sse_starlette.sse import EventSourceResponse
from app.utils.dependencies import get_current_user

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/stream", tags=["Streaming"])

# Global event queue for simple broadcasting (per job_id)
# In production, use Redis or a proper message queue
job_event_queues: Dict[str, asyncio.Queue] = {}
_queue_timestamps: Dict[str, float] = {}  # Track creation time for TTL cleanup
_QUEUE_TTL_SECONDS = 3600  # 1 hour


def _cleanup_stale_queues():
    """Remove queues older than TTL to prevent memory leaks."""
    now = time.time()
    stale_ids = [
        jid for jid, ts in _queue_timestamps.items()
        if now - ts > _QUEUE_TTL_SECONDS
    ]
    for jid in stale_ids:
        job_event_queues.pop(jid, None)
        _queue_timestamps.pop(jid, None)
    if stale_ids:
        logger.info("Cleaned up %d stale event queues", len(stale_ids))


async def event_generator(job_id: str, request: Request) -> AsyncGenerator[dict, None]:
    """
    Generate SSE events for a specific job.
    """
    # Clean up stale queues on each new subscription
    _cleanup_stale_queues()

    if job_id not in job_event_queues:
        job_event_queues[job_id] = asyncio.Queue()
        _queue_timestamps[job_id] = time.time()
        
    queue = job_event_queues[job_id]
    
    try:
        # collaborative yield to let other tasks run
        yield {
            "event": "connected",
            "data": json.dumps({"message": f"Connected to stream for job {job_id}"})
        }
        
        while True:
            # Check if client disconnected
            if await request.is_disconnected():
                logger.info(f"Client disconnected from stream {job_id}")
                break
                
            try:
                # Wait for next event with timeout to allow disconnect check
                event = await asyncio.wait_for(queue.get(), timeout=1.0)
                yield event
                queue.task_done()
            except asyncio.TimeoutError:
                # Send keepalive comment
                yield {"comment": "keepalive"}
                
    except asyncio.CancelledError:
        logger.info(f"Stream cancelled for job {job_id}")
    finally:
        # Clean up completed job queues
        if job_id in job_event_queues:
            job_event_queues.pop(job_id, None)
            _queue_timestamps.pop(job_id, None)

@router.get("/{job_id}")
async def stream_job_events(
    job_id: str,
    request: Request,
    current_user=Depends(get_current_user)
):
    """
    Stream real-time events for a specific job.
    Requires authentication.
    """
    return EventSourceResponse(event_generator(job_id, request))

def emit_event(job_id: str, event_type: str, data: dict):
    """
    Emit an event to the job's stream.
    """
    if job_id in job_event_queues:
        queue = job_event_queues[job_id]
        asyncio.create_task(queue.put({
            "event": event_type,
            "data": json.dumps(data)
        }))
    else:
        # Queue might not be created if no client is listening yet
        pass
