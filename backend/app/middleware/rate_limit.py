"""
Rate Limiting Middleware for FastAPI
Prevents DoS attacks by limiting requests per IP address.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict
from typing import Dict, Tuple

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware.
    
    Default: 60 requests per minute per IP address.
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts: Dict[str, list] = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Skip rate limiting for health check
        if request.url.path == "/health":
            return await call_next(request)
        
        current_time = time.time()
        
        # Clean up old requests (older than 1 minute)
        self.request_counts[client_ip] = [
            req_time for req_time in self.request_counts[client_ip]
            if current_time - req_time < 60
        ]
        
        # Check rate limit
        if len(self.request_counts[client_ip]) >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {self.requests_per_minute} requests per minute allowed",
                    "retry_after": 60
                }
            )
        
        # Record this request
        self.request_counts[client_ip].append(current_time)
        
        # Process request
        response = await call_next(request)
        return response
