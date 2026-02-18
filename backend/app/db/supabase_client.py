"""
Supabase Client — Server-Side DB Layer.

Provides a singleton supabase-py client using the SERVICE ROLE KEY for
all server-side database operations. This bypasses Row Level Security (RLS)
which is correct for backend operations that have already verified auth via JWT.

Design decisions:
- Uses SUPABASE_SERVICE_ROLE_KEY (not anon key) — server-side writes need it.
- Falls back gracefully: if credentials are missing, client is None and
  get_supabase_db() raises HTTP 503 instead of crashing the server.
- The SQLAlchemy session (session.py) is kept alongside this for schema
  reference and any future Alembic migrations.

Usage (FastAPI dependency):
    @router.get("/example")
    async def example(sb: Client = Depends(get_supabase_db)):
        result = sb.table("documents").select("*").execute()
        return result.data

Usage (direct, e.g. in background tasks):
    from app.db.supabase_client import get_supabase_client
    sb = get_supabase_client()
    if sb:
        sb.table("documents").update({"status": "FAILED"}).eq("id", job_id).execute()
"""

import logging
from typing import Optional

from app.config.settings import settings

logger = logging.getLogger(__name__)

# ── Singleton client ────────────────────────────────────────────────────────────

_supabase_client = None


def _init_client():
    """
    Initialise the supabase-py client once at module load.
    Returns None (instead of raising) if credentials are missing.
    """
    global _supabase_client

    url = settings.SUPABASE_URL
    key = settings.SUPABASE_SERVICE_ROLE_KEY

    if not url or not key:
        logger.warning(
            "⚠️  SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set. "
            "DB-dependent endpoints will return 503 until credentials are configured."
        )
        return None

    try:
        from supabase import create_client, Client
        _supabase_client = create_client(url, key)
        logger.info("✅ Supabase DB client (service role) initialised successfully.")
        return _supabase_client
    except Exception as exc:
        logger.error("❌ Failed to initialise Supabase DB client: %s", exc)
        return None


# Initialise at import time (lazy-safe — won't crash if deps missing)
_supabase_client = _init_client()


def get_supabase_client():
    """
    Return the singleton Supabase client.
    Returns None if not configured — callers must check.
    """
    return _supabase_client


# ── FastAPI dependency ──────────────────────────────────────────────────────────

def get_supabase_db():
    """
    FastAPI dependency that returns the Supabase client.
    Raises HTTP 503 if the client is not configured.

    Usage:
        @router.get("/endpoint")
        async def endpoint(sb = Depends(get_supabase_db)):
            ...
    """
    from fastapi import HTTPException, status

    if _supabase_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Database is not configured. "
                "Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY."
            ),
        )
    return _supabase_client


# ── Health check helper ─────────────────────────────────────────────────────────

def check_supabase_health() -> dict:
    """
    Returns a dict describing the current Supabase DB connectivity status.
    Used by the /health endpoint.
    """
    if _supabase_client is None:
        return {
            "status": "unconfigured",
            "detail": "SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set",
        }

    try:
        # Lightweight ping: select 1 row from profiles (limit 1)
        result = _supabase_client.table("profiles").select("id").limit(1).execute()
        return {"status": "healthy"}
    except Exception as exc:
        return {"status": "unhealthy", "detail": str(exc)}
