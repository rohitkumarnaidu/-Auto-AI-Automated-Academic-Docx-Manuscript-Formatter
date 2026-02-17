"""
Streaming Response Router
Provides Server-Sent Events (SSE) for real-time agent feedback.
"""

import asyncio
import json
import logging
from typing import AsyncGenerator
from fastapi import APIRouter, Request, HTTPException
from sse_starlette.sse import EventSourceResponse

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/stream", tags=["Streaming"])

# Global event queue for simple broadcasting (per job_id)
# In production, use Redis or a proper message queue
job_event_queues = {}

async def event_generator(job_id: str, request: Request) -> AsyncGenerator[dict, None]:
    """
    Generate SSE events for a specific job.
    """
    if job_id not in job_event_queues:
        job_event_queues[job_id] = asyncio.Queue()
        
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
        # Cleanup if needed (optional, depends on architecture)
        pass

@router.get("/{job_id}")
async def stream_job_events(job_id: str, request: Request):
    """
    Stream real-time events for a specific job.
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
