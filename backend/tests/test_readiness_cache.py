from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from app.services import health_checks


@pytest.fixture(autouse=True)
def reset_readiness_cache():
    health_checks._reset_readiness_cache_for_tests()
    yield
    health_checks._reset_readiness_cache_for_tests()


def _configure_fast_readiness(monkeypatch, ttl_seconds: float) -> None:
    monkeypatch.setattr(health_checks.settings, "READINESS_CACHE_TTL_SECONDS", ttl_seconds, raising=False)
    monkeypatch.setattr(health_checks.settings, "GROBID_ENABLED", False, raising=False)
    monkeypatch.setattr(health_checks.settings, "USE_SCIBERT_CLASSIFICATION", False, raising=False)


@pytest.mark.asyncio
async def test_readiness_cache_hits_within_ttl(monkeypatch):
    _configure_fast_readiness(monkeypatch, ttl_seconds=5.0)

    with patch("app.db.supabase_client.check_supabase_health", return_value={"status": "healthy"}) as mock_sb:
        with patch(
            "app.services.llm_service.check_health",
            new=AsyncMock(return_value={"nvidia": "healthy"}),
        ) as mock_llm:
            first_payload, first_status = await health_checks.get_readiness_payload()
            second_payload, second_status = await health_checks.get_readiness_payload()

    assert first_status == second_status
    assert first_payload == second_payload
    assert mock_sb.call_count == 1
    assert mock_llm.await_count == 1


@pytest.mark.asyncio
async def test_readiness_cache_refreshes_after_ttl(monkeypatch):
    _configure_fast_readiness(monkeypatch, ttl_seconds=0.01)

    with patch("app.db.supabase_client.check_supabase_health", return_value={"status": "healthy"}) as mock_sb:
        with patch(
            "app.services.llm_service.check_health",
            new=AsyncMock(return_value={"nvidia": "healthy"}),
        ) as mock_llm:
            first_payload, _ = await health_checks.get_readiness_payload()
            await asyncio.sleep(0.02)
            second_payload, _ = await health_checks.get_readiness_payload()

    assert first_payload["timestamp"] != second_payload["timestamp"]
    assert mock_sb.call_count == 2
    assert mock_llm.await_count == 2


@pytest.mark.asyncio
async def test_readiness_force_refresh_bypasses_cache(monkeypatch):
    _configure_fast_readiness(monkeypatch, ttl_seconds=30.0)

    with patch("app.db.supabase_client.check_supabase_health", return_value={"status": "healthy"}) as mock_sb:
        with patch(
            "app.services.llm_service.check_health",
            new=AsyncMock(return_value={"nvidia": "healthy"}),
        ) as mock_llm:
            await health_checks.get_readiness_payload()
            await health_checks.get_readiness_payload(force_refresh=True)

    assert mock_sb.call_count == 2
    assert mock_llm.await_count == 2
