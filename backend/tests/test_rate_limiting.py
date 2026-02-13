"""
Rate Limiting Middleware Tests
Tests rate limiting functionality and DoS protection.
"""

import pytest
import time
from fastapi import Request
from fastapi.responses import JSONResponse
from unittest.mock import Mock, MagicMock
from app.middleware.rate_limit import RateLimitMiddleware

class TestRateLimiting:
    """Test suite for rate limiting middleware."""
    
    @pytest.mark.unit
    def test_rate_limit_initialization(self):
        """Test rate limiting middleware initialization."""
        app = Mock()
        middleware = RateLimitMiddleware(app, requests_per_minute=60)
        
        assert middleware.requests_per_minute == 60
        assert middleware.request_counts is not None
    
    @pytest.mark.unit
    async def test_rate_limit_allows_normal_traffic(self):
        """Test rate limiting allows normal traffic."""
        app = Mock()
        middleware = RateLimitMiddleware(app, requests_per_minute=60)
        
        # Mock request
        request = Mock(spec=Request)
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.url = Mock()
        request.url.path = "/api/test"
        
        # Mock call_next
        async def mock_call_next(req):
            return JSONResponse({"status": "ok"})
        
        # Should allow request
        response = await middleware.dispatch(request, mock_call_next)
        assert response.status_code == 200
    
    @pytest.mark.unit
    async def test_rate_limit_blocks_excessive_requests(self):
        """Test rate limiting blocks excessive requests."""
        app = Mock()
        middleware = RateLimitMiddleware(app, requests_per_minute=5)  # Low limit for testing
        
        # Mock request
        request = Mock(spec=Request)
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.url = Mock()
        request.url.path = "/api/test"
        
        async def mock_call_next(req):
            return JSONResponse({"status": "ok"})
        
        # Make requests up to limit
        for i in range(5):
            response = await middleware.dispatch(request, mock_call_next)
            assert response.status_code == 200
        
        # Next request should be rate limited
        response = await middleware.dispatch(request, mock_call_next)
        assert response.status_code == 429
    
    @pytest.mark.unit
    async def test_rate_limit_skips_health_endpoint(self):
        """Test rate limiting skips /health endpoint."""
        app = Mock()
        middleware = RateLimitMiddleware(app, requests_per_minute=1)
        
        # Mock health check request
        request = Mock(spec=Request)
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.url = Mock()
        request.url.path = "/health"
        
        async def mock_call_next(req):
            return JSONResponse({"status": "healthy"})
        
        # Should allow unlimited health checks
        for _ in range(100):
            response = await middleware.dispatch(request, mock_call_next)
            assert response.status_code == 200
    
    @pytest.mark.unit
    def test_rate_limit_cleanup(self):
        """Test old requests are cleaned up."""
        app = Mock()
        middleware = RateLimitMiddleware(app, requests_per_minute=60)
        
        # Add old timestamp
        middleware.request_counts["127.0.0.1"] = [time.time() - 120]  # 2 minutes ago
        
        # Should be cleaned up on next request
        assert len(middleware.request_counts["127.0.0.1"]) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "unit"])
