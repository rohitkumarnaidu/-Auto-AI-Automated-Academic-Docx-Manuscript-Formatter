"""
Streaming Response Router
Provides Server-Sent Events (SSE) for real-time agent feedback.
"""

import os
import redis as sync_redis
import redis.asyncio as aioredis
import asyncio
import json
import logging
from typing import AsyncGenerator
from fastapi import APIRouter, Request, Depends
from sse_starlette.sse import EventSourceResponse
from app.utils.dependencies import get_current_user

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/stream", tags=["Streaming"])

# Phase 5: Redis Pub/Sub for SSE
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
async_redis = aioredis.from_url(REDIS_URL)
sync_redis_client = sync_redis.from_url(REDIS_URL)

async def event_generator(job_id: str, request: Request) -> AsyncGenerator[dict, None]:
    """
    Generate SSE events for a specific job using Redis Pub/Sub.
    """
    pubsub = async_redis.pubsub()
    await pubsub.subscribe(f"job:{job_id}")
    
    try:
        # Initial connection event
        yield {
            "event": "connected",
            "data": json.dumps({"message": f"Connected to stream for job {job_id}"})
        }
        
        async for message in pubsub.listen():
            if await request.is_disconnected():
                logger.info(f"Client disconnected from stream {job_id}")
                break
            
            if message["type"] == "message":
                try:
                    event_data = json.loads(message["data"])
                    yield event_data
                except Exception as e:
                    logger.error(f"Error parsing Redis message: {e}")
            
            # Note: sse-starlette handles keepalive automatically if configured, 
            # or we can rely on pubsub.listen() blocking until a message arrives.
                
    except asyncio.CancelledError:
        logger.info(f"Stream cancelled for job {job_id}")
    finally:
        await pubsub.unsubscribe(f"job:{job_id}")
        await pubsub.close()

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
    Emit an event to the job's stream via Redis Pub/Sub.
    Sync-friendly for use in pipeline threads.
    """
    try:
        sync_redis_client.publish(
            f"job:{job_id}", 
            json.dumps({"event": event_type, "data": data})
        )
    except Exception as e:
        logger.error(f"Failed to publish Redis event: {e}")
