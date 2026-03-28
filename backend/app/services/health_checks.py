from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from time import monotonic
from typing import Any

from app.config.settings import settings
from app.services.scibert_gate import get_scibert_gate_state, should_enable_scibert


_readiness_cache_lock: asyncio.Lock | None = None
_readiness_cache_payload: dict[str, Any] | None = None
_readiness_cache_status_code: int = 503
_readiness_cache_expiry: float = 0.0

_health_cache_lock: asyncio.Lock | None = None
_health_cache_payload: dict[str, Any] | None = None
_health_cache_status_code: int = 503
_health_cache_expiry: float = 0.0


def _get_readiness_cache_lock() -> asyncio.Lock:
    global _readiness_cache_lock
    if _readiness_cache_lock is None:
        _readiness_cache_lock = asyncio.Lock()
    return _readiness_cache_lock


def _get_health_cache_lock() -> asyncio.Lock:
    global _health_cache_lock
    if _health_cache_lock is None:
        _health_cache_lock = asyncio.Lock()
    return _health_cache_lock


def _readiness_ttl_seconds() -> float:
    raw_ttl = getattr(settings, "READINESS_CACHE_TTL_SECONDS", 15)
    try:
        ttl = float(raw_ttl)
    except (TypeError, ValueError):
        ttl = 15.0
    return max(0.0, ttl)


def _health_ttl_seconds() -> float:
    raw_ttl = getattr(settings, "HEALTH_CACHE_TTL_SECONDS", 15)
    try:
        ttl = float(raw_ttl)
    except (TypeError, ValueError):
        ttl = 15.0
    return max(0.0, ttl)


def _clone_payload(payload: dict[str, Any]) -> dict[str, Any]:
    cloned = dict(payload)
    checks = cloned.get("checks")
    if isinstance(checks, dict):
        cloned["checks"] = dict(checks)
    return cloned


def invalidate_readiness_cache() -> None:
    global _readiness_cache_payload, _readiness_cache_status_code, _readiness_cache_expiry
    _readiness_cache_payload = None
    _readiness_cache_status_code = 503
    _readiness_cache_expiry = 0.0


def invalidate_health_cache() -> None:
    global _health_cache_payload, _health_cache_status_code, _health_cache_expiry
    _health_cache_payload = None
    _health_cache_status_code = 503
    _health_cache_expiry = 0.0


def _reset_readiness_cache_for_tests() -> None:
    """Test helper to clear cached readiness state across test cases."""
    global _readiness_cache_lock, _health_cache_lock
    invalidate_readiness_cache()
    invalidate_health_cache()
    _readiness_cache_lock = None
    _health_cache_lock = None


async def _build_health_payload() -> tuple[dict, int]:
    import httpx

    from app.db.supabase_client import check_supabase_health
    from app.services.model_store import model_store

    health_status = {
        "status": "healthy",
        "version": "1.0.0",
        "components": {},
    }

    try:
        sb_health = check_supabase_health()
        health_status["components"]["supabase_db"] = sb_health.get("status", "unknown")
        if sb_health.get("status") != "healthy":
            health_status["status"] = "degraded"
    except Exception as exc:
        health_status["components"]["supabase_db"] = f"unhealthy: {str(exc)}"
        health_status["status"] = "degraded"

    try:
        async with httpx.AsyncClient(timeout=2) as client:
            response = await client.get(f"{settings.OLLAMA_URL}/api/tags")
            if response.status_code == 200:
                health_status["components"]["ollama"] = "healthy"
            else:
                health_status["components"]["ollama"] = "unhealthy"
                health_status["status"] = "degraded"
    except (httpx.RequestError, Exception):
        health_status["components"]["ollama"] = "unavailable (fallback active)"
        health_status["status"] = "degraded"

    try:
        if model_store.get_model("scibert_model") is not None:
            health_status["components"]["ai_models"] = "loaded"
        else:
            health_status["components"]["ai_models"] = "not_loaded"
    except Exception:
        health_status["components"]["ai_models"] = "error"

    status_code = 200 if health_status["status"] == "healthy" else 503
    return health_status, status_code


async def _build_readiness_payload() -> tuple[dict, int]:
    import httpx

    from app.db.supabase_client import check_supabase_health
    from app.services.model_store import model_store

    checks = {}
    is_ready = True

    try:
        sb_health = check_supabase_health()
        checks["database"] = sb_health.get("status", "unknown")
        if sb_health.get("status") == "healthy":
            pass
        elif sb_health.get("status") == "unconfigured":
            # Allow local/dev to run without Supabase configured.
            if not settings.DEBUG:
                is_ready = False
        else:
            is_ready = False
    except Exception as exc:
        checks["database"] = f"unhealthy: {str(exc)}"
        is_ready = False

    if settings.GROBID_ENABLED:
        try:
            async with httpx.AsyncClient(timeout=2) as client:
                response = await client.get(f"{settings.GROBID_URL}/api/isalive")
                checks["grobid"] = "ready" if response.status_code == 200 else "unavailable"
                if response.status_code != 200:
                    is_ready = False
        except (httpx.RequestError, Exception):
            checks["grobid"] = "unavailable"
            is_ready = False
    else:
        checks["grobid"] = "disabled"

    try:
        from app.services.llm_service import check_health as llm_check_health

        checks["llm_status"] = await llm_check_health()
    except Exception:
        checks["llm_status"] = "unknown"

    if should_enable_scibert():
        try:
            if model_store.get_model("scibert_model") is not None:
                checks["ai_models"] = "loaded"
            else:
                checks["ai_models"] = "not_loaded"
                is_ready = False
        except Exception:
            checks["ai_models"] = "error"
            is_ready = False
    else:
        checks["ai_models"] = "disabled"
        checks["scibert_gate"] = get_scibert_gate_state()

    payload = {
        "ready": is_ready,
        "checks": checks,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return payload, 200 if is_ready else 503


async def get_readiness_payload(*, force_refresh: bool = False) -> tuple[dict, int]:
    global _readiness_cache_payload, _readiness_cache_status_code, _readiness_cache_expiry

    ttl_seconds = _readiness_ttl_seconds()
    now = monotonic()
    if (
        not force_refresh
        and ttl_seconds > 0
        and _readiness_cache_payload is not None
        and now < _readiness_cache_expiry
    ):
        return _clone_payload(_readiness_cache_payload), _readiness_cache_status_code

    async with _get_readiness_cache_lock():
        now = monotonic()
        if (
            not force_refresh
            and ttl_seconds > 0
            and _readiness_cache_payload is not None
            and now < _readiness_cache_expiry
        ):
            return _clone_payload(_readiness_cache_payload), _readiness_cache_status_code

        payload, status_code = await _build_readiness_payload()
        if ttl_seconds > 0:
            _readiness_cache_payload = payload
            _readiness_cache_status_code = status_code
            _readiness_cache_expiry = now + ttl_seconds
        else:
            invalidate_readiness_cache()

        return _clone_payload(payload), status_code


async def get_health_payload(*, force_refresh: bool = False) -> tuple[dict, int]:
    global _health_cache_payload, _health_cache_status_code, _health_cache_expiry

    ttl_seconds = _health_ttl_seconds()
    now = monotonic()
    if (
        not force_refresh
        and ttl_seconds > 0
        and _health_cache_payload is not None
        and now < _health_cache_expiry
    ):
        return _clone_payload(_health_cache_payload), _health_cache_status_code

    async with _get_health_cache_lock():
        now = monotonic()
        if (
            not force_refresh
            and ttl_seconds > 0
            and _health_cache_payload is not None
            and now < _health_cache_expiry
        ):
            return _clone_payload(_health_cache_payload), _health_cache_status_code

        payload, status_code = await _build_health_payload()
        if ttl_seconds > 0:
            _health_cache_payload = payload
            _health_cache_status_code = status_code
            _health_cache_expiry = now + ttl_seconds
        else:
            invalidate_health_cache()

        return _clone_payload(payload), status_code
