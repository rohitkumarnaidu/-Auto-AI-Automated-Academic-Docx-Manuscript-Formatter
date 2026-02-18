"""
Document Service — Supabase DB Layer.

All database operations for the `documents`, `document_results`, and
`processing_status` tables go through this service using the supabase-py client.

The old SQLAlchemy ORM imports are kept as comments for reference.
The SQLAlchemy ORM model (app/models/document.py) is still the canonical
schema definition and is used by Alembic migrations.
"""
from __future__ import annotations

import logging
from typing import Optional, List, Dict, Any

# ── Old ORM imports (kept for reference, replaced by supabase-py) ──────────────
# from sqlalchemy.orm import Session
# from app.models.document import Document as DocumentModel
# from app.models.document_result import DocumentResult as DocumentResultModel
# from app.models.processing_status import ProcessingStatus as ProcessingStatusModel

from app.db.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


class DocumentService:
    """
    Service layer for all document-related DB operations.
    Uses supabase-py for all reads and writes.
    """

    # ── Documents ──────────────────────────────────────────────────────────────

    @staticmethod
    def get_document(doc_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch a single document by ID.
        Optionally scope to a specific user_id for ownership checks.
        Returns None if not found or on error.
        """
        sb = get_supabase_client()
        if sb is None:
            logger.error("get_document: Supabase client not available.")
            return None
        try:
            query = sb.table("documents").select("*").eq("id", str(doc_id))
            if user_id:
                query = query.eq("user_id", str(user_id))
            result = query.maybe_single().execute()
            return result.data
        except Exception as exc:
            logger.error("get_document(%s) failed: %s", doc_id, exc)
            return None

    @staticmethod
    def list_documents(
        user_id: str,
        status: Optional[str] = None,
        template: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        List documents for a user with optional filters and pagination.
        Returns empty list on error.
        """
        sb = get_supabase_client()
        if sb is None:
            logger.error("list_documents: Supabase client not available.")
            return []
        try:
            query = (
                sb.table("documents")
                .select("*")
                .eq("user_id", str(user_id))
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
            )
            if status:
                query = query.eq("status", status.upper())
            if template:
                query = query.eq("template", template.upper())
            result = query.execute()
            return result.data or []
        except Exception as exc:
            logger.error("list_documents(user=%s) failed: %s", user_id, exc)
            return []

    @staticmethod
    def count_documents(
        user_id: str,
        status: Optional[str] = None,
        template: Optional[str] = None,
    ) -> int:
        """
        Count documents for a user with optional filters.
        Returns 0 on error.
        """
        sb = get_supabase_client()
        if sb is None:
            return 0
        try:
            query = (
                sb.table("documents")
                .select("id", count="exact")
                .eq("user_id", str(user_id))
            )
            if status:
                query = query.eq("status", status.upper())
            if template:
                query = query.eq("template", template.upper())
            result = query.execute()
            return result.count or 0
        except Exception as exc:
            logger.error("count_documents(user=%s) failed: %s", user_id, exc)
            return 0

    @staticmethod
    def create_document(
        doc_id: str,
        user_id: Optional[str],
        filename: str,
        template: Optional[str],
        original_file_path: Optional[str] = None,
        formatting_options: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Insert a new document row.
        Returns the inserted row dict or None on error.
        """
        sb = get_supabase_client()
        if sb is None:
            logger.error("create_document: Supabase client not available.")
            return None
        try:
            payload: Dict[str, Any] = {
                "id": str(doc_id),
                "filename": filename,
                "status": "RUNNING",
                "progress": 0,
            }
            if user_id:
                payload["user_id"] = str(user_id)
            if template:
                payload["template"] = template
            if original_file_path:
                payload["original_file_path"] = original_file_path
            if formatting_options:
                payload["formatting_options"] = formatting_options

            result = sb.table("documents").insert(payload).execute()
            return result.data[0] if result.data else None
        except Exception as exc:
            logger.error("create_document(%s) failed: %s", doc_id, exc)
            return None

    @staticmethod
    def update_document(doc_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update fields on a document row.
        Returns the updated row dict or None on error.
        """
        sb = get_supabase_client()
        if sb is None:
            logger.error("update_document: Supabase client not available.")
            return None
        try:
            result = (
                sb.table("documents")
                .update(updates)
                .eq("id", str(doc_id))
                .execute()
            )
            return result.data[0] if result.data else None
        except Exception as exc:
            logger.error("update_document(%s) failed: %s", doc_id, exc)
            return None

    @staticmethod
    def mark_document_failed(doc_id: str, error_message: str) -> None:
        """
        Convenience: mark a document as FAILED with an error message.
        Never raises — safe to call from background tasks and exception handlers.
        """
        sb = get_supabase_client()
        if sb is None:
            logger.error("mark_document_failed: Supabase client not available.")
            return
        try:
            sb.table("documents").update({
                "status": "FAILED",
                "error_message": error_message,
                "progress": 0,
            }).eq("id", str(doc_id)).execute()
        except Exception as exc:
            logger.error("mark_document_failed(%s) failed: %s", doc_id, exc)

    @staticmethod
    def mark_document_completed(
        doc_id: str,
        output_path: str,
        raw_text: Optional[str] = None,
    ) -> None:
        """
        Convenience: mark a document as COMPLETED with its output path.
        Never raises — safe to call from background tasks.
        """
        sb = get_supabase_client()
        if sb is None:
            logger.error("mark_document_completed: Supabase client not available.")
            return
        try:
            updates: Dict[str, Any] = {
                "status": "COMPLETED",
                "output_path": output_path,
                "progress": 100,
                "current_stage": "DONE",
            }
            if raw_text is not None:
                updates["raw_text"] = raw_text
            sb.table("documents").update(updates).eq("id", str(doc_id)).execute()
        except Exception as exc:
            logger.error("mark_document_completed(%s) failed: %s", doc_id, exc)

    # ── Document Results ───────────────────────────────────────────────────────

    @staticmethod
    def get_document_result(doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch the processing result for a document.
        Returns None if not found or on error.
        """
        sb = get_supabase_client()
        if sb is None:
            return None
        try:
            result = (
                sb.table("document_results")
                .select("*")
                .eq("document_id", str(doc_id))
                .maybe_single()
                .execute()
            )
            return result.data
        except Exception as exc:
            logger.error("get_document_result(%s) failed: %s", doc_id, exc)
            return None

    @staticmethod
    def upsert_document_result(
        doc_id: str,
        structured_data: Optional[Dict[str, Any]] = None,
        validation_results: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Insert or update the document_results row for a document.
        Never raises.
        """
        sb = get_supabase_client()
        if sb is None:
            logger.error("upsert_document_result: Supabase client not available.")
            return
        try:
            payload: Dict[str, Any] = {"document_id": str(doc_id)}
            if structured_data is not None:
                payload["structured_data"] = structured_data
            if validation_results is not None:
                payload["validation_results"] = validation_results
            sb.table("document_results").upsert(
                payload, on_conflict="document_id"
            ).execute()
        except Exception as exc:
            logger.error("upsert_document_result(%s) failed: %s", doc_id, exc)

    # ── Processing Status ──────────────────────────────────────────────────────

    @staticmethod
    def get_processing_statuses(doc_id: str) -> List[Dict[str, Any]]:
        """
        Fetch all processing phase statuses for a document.
        Returns empty list on error.
        """
        sb = get_supabase_client()
        if sb is None:
            return []
        try:
            result = (
                sb.table("processing_status")
                .select("*")
                .eq("document_id", str(doc_id))
                .execute()
            )
            return result.data or []
        except Exception as exc:
            logger.error("get_processing_statuses(%s) failed: %s", doc_id, exc)
            return []

    @staticmethod
    def upsert_processing_status(
        doc_id: str,
        phase: str,
        status: str,
        progress_percentage: Optional[int] = None,
        message: Optional[str] = None,
    ) -> None:
        """
        Insert or update a processing phase status row.
        Never raises.
        """
        sb = get_supabase_client()
        if sb is None:
            logger.error("upsert_processing_status: Supabase client not available.")
            return
        try:
            payload: Dict[str, Any] = {
                "document_id": str(doc_id),
                "phase": phase,
                "status": status,
            }
            if progress_percentage is not None:
                payload["progress_percentage"] = progress_percentage
            if message is not None:
                payload["message"] = message
            sb.table("processing_status").upsert(
                payload, on_conflict="document_id,phase"
            ).execute()
        except Exception as exc:
            logger.error(
                "upsert_processing_status(%s, %s) failed: %s", doc_id, phase, exc
            )
