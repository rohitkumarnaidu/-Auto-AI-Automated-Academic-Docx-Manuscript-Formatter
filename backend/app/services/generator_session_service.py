from __future__ import annotations

import asyncio
import copy
import logging
import uuid
from datetime import datetime, timezone
from time import monotonic
from typing import Any, Optional

from app.config.settings import settings
from app.db.supabase_client import get_supabase_client
from app.utils.logging_context import log_extra

logger = logging.getLogger(__name__)

_CACHE_MISS = object()


class GeneratorSessionService:
    """Supabase-backed CRUD helpers for generator session artifacts."""

    def __init__(self) -> None:
        self._cache_lock = asyncio.Lock()
        self._session_cache: dict[str, tuple[float, Any]] = {}
        self._messages_cache: dict[str, tuple[float, Any]] = {}
        self._session_list_cache: dict[str, tuple[float, Any]] = {}
        self._latest_document_cache: dict[str, tuple[float, Any]] = {}

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _session_ttl_seconds() -> float:
        raw_ttl = getattr(settings, "GENERATOR_SESSION_CACHE_TTL_SECONDS", 2)
        try:
            ttl = float(raw_ttl)
        except (TypeError, ValueError):
            ttl = 2.0
        return max(0.0, ttl)

    @staticmethod
    def _messages_ttl_seconds() -> float:
        raw_ttl = getattr(settings, "GENERATOR_MESSAGES_CACHE_TTL_SECONDS", 1)
        try:
            ttl = float(raw_ttl)
        except (TypeError, ValueError):
            ttl = 1.0
        return max(0.0, ttl)

    @staticmethod
    def _session_list_ttl_seconds() -> float:
        raw_ttl = getattr(settings, "GENERATOR_SESSION_LIST_CACHE_TTL_SECONDS", 3)
        try:
            ttl = float(raw_ttl)
        except (TypeError, ValueError):
            ttl = 3.0
        return max(0.0, ttl)

    @staticmethod
    def _latest_document_ttl_seconds() -> float:
        raw_ttl = getattr(settings, "GENERATOR_DOCUMENT_CACHE_TTL_SECONDS", 2)
        try:
            ttl = float(raw_ttl)
        except (TypeError, ValueError):
            ttl = 2.0
        return max(0.0, ttl)

    @staticmethod
    def _clone(value: Any) -> Any:
        return copy.deepcopy(value)

    async def _get_cached(
        self,
        cache: dict[str, tuple[float, Any]],
        key: str,
        ttl_seconds: float,
    ) -> Any:
        if ttl_seconds <= 0:
            return _CACHE_MISS
        now = monotonic()
        async with self._cache_lock:
            cached = cache.get(key)
            if not cached:
                return _CACHE_MISS
            expiry, value = cached
            if now >= expiry:
                cache.pop(key, None)
                return _CACHE_MISS
            return self._clone(value)

    async def _set_cached(
        self,
        cache: dict[str, tuple[float, Any]],
        key: str,
        value: Any,
        ttl_seconds: float,
    ) -> None:
        async with self._cache_lock:
            if ttl_seconds <= 0:
                cache.pop(key, None)
                return
            cache[key] = (monotonic() + ttl_seconds, self._clone(value))

    async def _invalidate_session_caches(self, session_id: str) -> None:
        sid = str(session_id)
        async with self._cache_lock:
            self._session_cache.pop(sid, None)
            self._latest_document_cache.pop(sid, None)
            message_keys = [key for key in self._messages_cache if key.startswith(f"{sid}|")]
            for key in message_keys:
                self._messages_cache.pop(key, None)

    async def _invalidate_session_lists(self) -> None:
        async with self._cache_lock:
            self._session_list_cache.clear()

    async def reset_cache_for_tests(self) -> None:
        async with self._cache_lock:
            self._session_cache.clear()
            self._messages_cache.clear()
            self._session_list_cache.clear()
            self._latest_document_cache.clear()

    async def create_session(self, user_id: Optional[str], session_type: str, config: dict) -> str:
        session_id = str(uuid.uuid4())
        sb = get_supabase_client()
        if sb is None:
            logger.error("Generator session create failed: Supabase client unavailable.", extra=log_extra())
            raise RuntimeError("Supabase client unavailable.")

        payload = {
            "id": session_id,
            "user_id": str(user_id) if user_id else None,
            "session_type": session_type or "multi_doc",
            "status": "pending",
            "progress": 0,
            "config_json": config or {},
            "outline_json": None,
            "created_at": self._now_iso(),
            "updated_at": self._now_iso(),
        }
        sb.table("generator_sessions").insert(payload).execute()
        await self._set_cached(
            self._session_cache,
            session_id,
            payload,
            self._session_ttl_seconds(),
        )
        await self._invalidate_session_lists()
        logger.info(
            "Generator session created",
            extra=log_extra(session_id=session_id),
        )
        return session_id

    async def get_session(self, session_id: str) -> Optional[dict]:
        sid = str(session_id)
        cached = await self._get_cached(
            self._session_cache,
            sid,
            self._session_ttl_seconds(),
        )
        if cached is not _CACHE_MISS:
            return cached

        sb = get_supabase_client()
        if sb is None:
            logger.error("Generator session fetch failed: Supabase client unavailable.", extra=log_extra(session_id=session_id))
            raise RuntimeError("Supabase client unavailable.")
        result = (
            sb.table("generator_sessions")
            .select("*")
            .eq("id", sid)
            .maybe_single()
            .execute()
        )
        payload = result.data if result else None
        await self._set_cached(
            self._session_cache,
            sid,
            payload,
            self._session_ttl_seconds(),
        )
        return payload

    async def update_session(self, session_id: str, **fields: Any) -> None:
        sb = get_supabase_client()
        if sb is None:
            logger.error("Generator session update failed: Supabase client unavailable.", extra=log_extra(session_id=session_id))
            raise RuntimeError("Supabase client unavailable.")
        payload = dict(fields)
        payload["updated_at"] = self._now_iso()
        sb.table("generator_sessions").update(payload).eq("id", str(session_id)).execute()
        await self._invalidate_session_caches(str(session_id))
        await self._invalidate_session_lists()
        logger.info("Generator session updated", extra=log_extra(session_id=session_id))

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        token_count: int = 0,
    ) -> None:
        sb = get_supabase_client()
        if sb is None:
            logger.error("Generator message create failed: Supabase client unavailable.", extra=log_extra(session_id=session_id))
            raise RuntimeError("Supabase client unavailable.")
        payload = {
            "session_id": str(session_id),
            "role": role,
            "content": content,
            "token_count": int(token_count or 0),
            "created_at": self._now_iso(),
        }
        sb.table("generator_messages").insert(payload).execute()
        await self._invalidate_session_caches(str(session_id))
        logger.info("Generator message stored", extra=log_extra(session_id=session_id))

    async def get_messages(self, session_id: str, limit: int = 50) -> list[dict]:
        sid = str(session_id)
        cache_key = f"{sid}|{int(limit or 50)}"
        cached = await self._get_cached(
            self._messages_cache,
            cache_key,
            self._messages_ttl_seconds(),
        )
        if cached is not _CACHE_MISS:
            return cached

        sb = get_supabase_client()
        if sb is None:
            logger.error("Generator messages fetch failed: Supabase client unavailable.", extra=log_extra(session_id=session_id))
            raise RuntimeError("Supabase client unavailable.")
        result = (
            sb.table("generator_messages")
            .select("*")
            .eq("session_id", sid)
            .order("created_at", desc=False)
            .limit(int(limit or 50))
            .execute()
        )
        payload = result.data or []
        await self._set_cached(
            self._messages_cache,
            cache_key,
            payload,
            self._messages_ttl_seconds(),
        )
        return payload

    async def list_sessions(self, user_id: Optional[str], limit: int = 50) -> list[dict]:
        uid = str(user_id) if user_id else "__all__"
        cache_key = f"{uid}|{int(limit or 50)}"
        cached = await self._get_cached(
            self._session_list_cache,
            cache_key,
            self._session_list_ttl_seconds(),
        )
        if cached is not _CACHE_MISS:
            return cached

        sb = get_supabase_client()
        if sb is None:
            logger.error("Generator sessions list failed: Supabase client unavailable.", extra=log_extra())
            raise RuntimeError("Supabase client unavailable.")
        query = sb.table("generator_sessions").select("*")
        if user_id:
            query = query.eq("user_id", str(user_id))
        result = (
            query.order("updated_at", desc=True)
            .limit(int(limit or 50))
            .execute()
        )
        payload = result.data or []
        await self._set_cached(
            self._session_list_cache,
            cache_key,
            payload,
            self._session_list_ttl_seconds(),
        )
        return payload

    async def save_document_version(
        self,
        session_id: str,
        content_json: dict,
        docx_path: str,
        version: Optional[int] = None,
    ) -> int:
        sb = get_supabase_client()
        if sb is None:
            logger.error("Generator document save failed: Supabase client unavailable.", extra=log_extra(session_id=session_id))
            raise RuntimeError("Supabase client unavailable.")

        version_number = int(version or 0)
        if version_number <= 0:
            latest = (
                sb.table("generator_documents")
                .select("version_number")
                .eq("session_id", str(session_id))
                .order("version_number", desc=True)
                .limit(1)
                .execute()
            )
            if latest.data:
                try:
                    version_number = int(latest.data[0].get("version_number") or 0) + 1
                except (TypeError, ValueError):
                    version_number = 1
            else:
                version_number = 1

        payload = {
            "session_id": str(session_id),
            "content_json": content_json or {},
            "docx_path": str(docx_path) if docx_path else None,
            "version_number": version_number,
        }
        sb.table("generator_documents").insert(payload).execute()
        await self._invalidate_session_caches(str(session_id))
        await self._invalidate_session_lists()
        logger.info(
            "Generator document version saved",
            extra=log_extra(session_id=session_id),
        )
        return version_number

    async def get_latest_document(self, session_id: str) -> Optional[dict]:
        sid = str(session_id)
        cached = await self._get_cached(
            self._latest_document_cache,
            sid,
            self._latest_document_ttl_seconds(),
        )
        if cached is not _CACHE_MISS:
            return cached

        sb = get_supabase_client()
        if sb is None:
            logger.error("Generator document fetch failed: Supabase client unavailable.", extra=log_extra(session_id=session_id))
            raise RuntimeError("Supabase client unavailable.")
        result = (
            sb.table("generator_documents")
            .select("*")
            .eq("session_id", sid)
            .order("version_number", desc=True)
            .limit(1)
            .maybe_single()
            .execute()
        )
        payload = result.data if result else None
        await self._set_cached(
            self._latest_document_cache,
            sid,
            payload,
            self._latest_document_ttl_seconds(),
        )
        return payload
