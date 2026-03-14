from __future__ import annotations

from datetime import datetime, timezone

from app.config.settings import settings


async def get_readiness_payload() -> tuple[dict, int]:
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

    if settings.USE_SCIBERT_CLASSIFICATION:
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

    payload = {
        "ready": is_ready,
        "checks": checks,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return payload, 200 if is_ready else 503
