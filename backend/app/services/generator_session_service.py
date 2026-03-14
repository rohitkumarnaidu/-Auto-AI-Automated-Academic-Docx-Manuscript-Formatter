from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from app.db.supabase_client import get_supabase_client
from app.utils.logging_context import log_extra

logger = logging.getLogger(__name__)


class GeneratorSessionService:
    """Supabase-backed CRUD helpers for generator session artifacts."""

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

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
        logger.info(
            "Generator session created",
            extra=log_extra(session_id=session_id),
        )
        return session_id

    async def get_session(self, session_id: str) -> Optional[dict]:
        sb = get_supabase_client()
        if sb is None:
            logger.error("Generator session fetch failed: Supabase client unavailable.", extra=log_extra(session_id=session_id))
            raise RuntimeError("Supabase client unavailable.")
        result = (
            sb.table("generator_sessions")
            .select("*")
            .eq("id", str(session_id))
            .maybe_single()
            .execute()
        )
        return result.data if result else None

    async def update_session(self, session_id: str, **fields: Any) -> None:
        sb = get_supabase_client()
        if sb is None:
            logger.error("Generator session update failed: Supabase client unavailable.", extra=log_extra(session_id=session_id))
            raise RuntimeError("Supabase client unavailable.")
        payload = dict(fields)
        payload["updated_at"] = self._now_iso()
        sb.table("generator_sessions").update(payload).eq("id", str(session_id)).execute()
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
        logger.info("Generator message stored", extra=log_extra(session_id=session_id))

    async def get_messages(self, session_id: str, limit: int = 50) -> list[dict]:
        sb = get_supabase_client()
        if sb is None:
            logger.error("Generator messages fetch failed: Supabase client unavailable.", extra=log_extra(session_id=session_id))
            raise RuntimeError("Supabase client unavailable.")
        result = (
            sb.table("generator_messages")
            .select("*")
            .eq("session_id", str(session_id))
            .order("created_at", desc=False)
            .limit(int(limit or 50))
            .execute()
        )
        return result.data or []

    async def list_sessions(self, user_id: Optional[str], limit: int = 50) -> list[dict]:
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
        return result.data or []

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
        logger.info(
            "Generator document version saved",
            extra=log_extra(session_id=session_id),
        )
        return version_number

    async def get_latest_document(self, session_id: str) -> Optional[dict]:
        sb = get_supabase_client()
        if sb is None:
            logger.error("Generator document fetch failed: Supabase client unavailable.", extra=log_extra(session_id=session_id))
            raise RuntimeError("Supabase client unavailable.")
        result = (
            sb.table("generator_documents")
            .select("*")
            .eq("session_id", str(session_id))
            .order("version_number", desc=True)
            .limit(1)
            .maybe_single()
            .execute()
        )
        return result.data if result else None
