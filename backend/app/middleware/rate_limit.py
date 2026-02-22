import os
import redis.asyncio as aioredis
import time
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# Initialize Redis client for shared rate limiting
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis = aioredis.from_url(REDIS_URL, decode_responses=True)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Redis-based rate limiting middleware.
    
    Default: 60 requests per minute per IP address.
    Upload endpoint: 5 uploads per minute per IP address.
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.uploads_per_minute = 5
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Skip rate limiting for health check
        if request.url.path == "/health":
            return await call_next(request)
        
        # Check if this is an upload request (stricter limit)
        is_upload = request.url.path == "/api/documents/upload" and request.method == "POST"
        
        # Determine limits and keys
        # We use current minute bucket for simple windowing
        current_window = int(time.time() / 60)
        
        if is_upload:
            limit = self.uploads_per_minute
            key = f"ratelimit:upload:{client_ip}:{current_window}"
            error_msg = f"Maximum {limit} uploads per minute allowed."
        else:
            limit = self.requests_per_minute
            key = f"ratelimit:general:{client_ip}:{current_window}"
            error_msg = f"Maximum {limit} requests per minute allowed."

        try:
            # Phase 5: Redis-based Rate Limiting
            count = await redis.incr(key)
            if count == 1:
                # Set TTL to 61 seconds (slightly over the window)
                await redis.expire(key, 61)
            
            if count > limit:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "message": error_msg,
                        "retry_after": 60
                    }
                )
        except Exception as e:
            # Fallback: if Redis is down, we allow the request but log it
            # In a strict production system, you might want to block instead
            print(f"⚠️ Rate limit Redis error: {e}")
        
        # Process request
        response = await call_next(request)
        return response
