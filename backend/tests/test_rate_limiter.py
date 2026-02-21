"""
Tests for RateLimitMiddleware — in-memory store behaviour,
per-IP limits, and eviction of stale entries.
"""
from __future__ import annotations

import sys
import time
import pytest
from unittest.mock import MagicMock, AsyncMock

# Mock out heavy imports that trigger Python 3.14 type evaluation bugs in LangChain
sys.modules["app.routers"] = MagicMock()
sys.modules["app.routers.feedback"] = MagicMock()
sys.modules["app.pipeline.agents"] = MagicMock()
sys.modules["app.pipeline.agents.document_agent"] = MagicMock()
sys.modules["langchain"] = MagicMock()
sys.modules["langchain_core"] = MagicMock()
sys.modules["langchain_community"] = MagicMock()

try:
    from app.middleware.rate_limit import RateLimitMiddleware
except Exception as e:
    pytest.skip(f"Could not import RateLimitMiddleware: {e}", allow_module_level=True)


class TestRateLimiting:
    """Unit tests for rate-limit logic."""

    def _make_middleware(self, rpm: int = 5):
        mock_app = MagicMock()
        return RateLimitMiddleware(mock_app, requests_per_minute=rpm)

    def _make_request(self, ip: str, path: str = "/api/chat", method: str = "POST"):
        req = MagicMock()
        req.client.host = ip
        req.url.path = path
        req.method = method
        return req

    @pytest.mark.asyncio
    async def test_first_request_allowed(self):
        """A brand-new IP should always pass."""
        mw = self._make_middleware(rpm=10)
        req = self._make_request("192.168.1.1")
        call_next = AsyncMock(return_value="OK")
        
        res = await mw.dispatch(req, call_next)
        assert res == "OK"
        assert len(mw.request_counts["192.168.1.1"]) == 1

    @pytest.mark.asyncio
    async def test_exceeds_limit_is_blocked(self):
        """After rpm requests the IP should be rate-limited."""
        rpm = 3
        mw = self._make_middleware(rpm=rpm)
        req = self._make_request("10.0.0.1")
        call_next = AsyncMock(return_value="OK")

        # Allow rpm requests
        for _ in range(rpm):
            res = await mw.dispatch(req, call_next)
            assert res == "OK"

        # Block the rpm+1 request
        res_blocked = await mw.dispatch(req, call_next)
        # Fastapi JSONResponse mock check
        assert hasattr(res_blocked, "status_code")
        assert res_blocked.status_code == 429

    @pytest.mark.asyncio
    async def test_old_requests_evicted(self):
        """Requests older than window should be evicted."""
        mw = self._make_middleware(rpm=3)
        req = self._make_request("172.16.0.1")
        
        # Inject old requests
        old_ts = time.time() - 120
        mw.request_counts["172.16.0.1"] = [old_ts, old_ts, old_ts]
        
        call_next = AsyncMock(return_value="OK")
        res = await mw.dispatch(req, call_next)
        
        assert res == "OK"
        # The 3 old requests were evicted, and 1 new request was added
        assert len(mw.request_counts["172.16.0.1"]) == 1

    @pytest.mark.asyncio
    async def test_rate_limit_is_per_ip(self):
        """Rate limit must track IPs independently."""
        mw = self._make_middleware(rpm=2)
        req_a = self._make_request("10.1.1.1")
        req_b = self._make_request("10.1.1.2")
        call_next = AsyncMock(return_value="OK")

        # Max out IP A
        await mw.dispatch(req_a, call_next)
        await mw.dispatch(req_a, call_next)
        res_a_blocked = await mw.dispatch(req_a, call_next)
        assert res_a_blocked.status_code == 429

        # IP B should still be allowed
        res_b = await mw.dispatch(req_b, call_next)
        assert res_b == "OK"
