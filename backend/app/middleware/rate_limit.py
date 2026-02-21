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
    Upload endpoint: 5 uploads per minute per IP address.
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts: Dict[str, list] = defaultdict(list)
        # Separate tracking for upload endpoint (stricter limit)
        self.upload_counts: Dict[str, list] = defaultdict(list)
        self.uploads_per_minute = 5
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Skip rate limiting for health check
        if request.url.path == "/health":
            return await call_next(request)
        
        current_time = time.time()
        
        # Check if this is an upload request (stricter limit)
        is_upload = request.url.path == "/api/documents/upload" and request.method == "POST"
        
        # BUG 3 FIX: Use only IP address as the key to prevent JWT-rotation bypass
        client_id = client_ip

        if is_upload:
            # BUG 2 FIX: Removed self.uploads_per_minute = 10 line that overwrote init value
            
            # Clean up old upload requests (older than 1 minute)
            if client_id in self.upload_counts:
                self.upload_counts[client_id] = [
                    req_time for req_time in self.upload_counts[client_id]
                    if current_time - req_time < 60
                ]
                # BUG 1 FIX: Delete empty lists to prevent memory leak
                if not self.upload_counts[client_id]:
                    del self.upload_counts[client_id]
            
            # Check upload rate limit
            if client_id in self.upload_counts and len(self.upload_counts[client_id]) >= self.uploads_per_minute:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Upload rate limit exceeded",
                        "message": f"Maximum {self.uploads_per_minute} uploads per minute allowed. Please wait before uploading again.",
                        "retry_after": 60
                    }
                )
            
            # Record this upload
            self.upload_counts[client_id].append(current_time)
        
        # Clean up old requests (older than 1 minute)
        if client_ip in self.request_counts:
            self.request_counts[client_ip] = [
                req_time for req_time in self.request_counts[client_ip]
                if current_time - req_time < 60
            ]
            # BUG 1 FIX: Delete empty lists to prevent memory leak
            if not self.request_counts[client_ip]:
                del self.request_counts[client_ip]
        
        # Check general rate limit (60 per minute)
        if client_ip in self.request_counts and len(self.request_counts[client_ip]) >= self.requests_per_minute:
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
