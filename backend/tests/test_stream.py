from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.user import User
from app.utils.dependencies import get_current_user


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def authenticated_user():
    user = User(id="user-123", email="user@example.com", role="authenticated")
    app.dependency_overrides[get_current_user] = lambda: user
    yield user
    app.dependency_overrides.pop(get_current_user, None)


def test_sse_stream_connection(client, authenticated_user):
    async def fake_event_generator(job_id, request):
        yield {"event": "connected", "data": '{"message":"ok"}'}

    with patch("app.routers.stream.event_generator", fake_event_generator):
        response = client.get("/api/stream/job-123")

    assert response.status_code == 200
    assert "text/event-stream" in response.headers.get("content-type", "")
    assert "event: connected" in response.text


def test_emit_event_redis_fallback_behavior():
    from app.routers import stream as stream_router

    original_client = stream_router.sync_redis_client
    original_unavailable = stream_router._redis_publish_unavailable
    original_retry_after = stream_router._redis_publish_retry_after

    failing_client = MagicMock()
    failing_client.publish.side_effect = RuntimeError("redis down")

    try:
        stream_router.sync_redis_client = failing_client
        stream_router._redis_publish_unavailable = False
        stream_router._redis_publish_retry_after = 0.0

        stream_router.emit_event("job-1", "STATUS", {"ok": True})
        assert stream_router._redis_publish_unavailable is True
        assert failing_client.publish.call_count == 1

        # Second call should be skipped during retry window.
        stream_router.emit_event("job-1", "STATUS", {"ok": True})
        assert failing_client.publish.call_count == 1
    finally:
        stream_router.sync_redis_client = original_client
        stream_router._redis_publish_unavailable = original_unavailable
        stream_router._redis_publish_retry_after = original_retry_after
