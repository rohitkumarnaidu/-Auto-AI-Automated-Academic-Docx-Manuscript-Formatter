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
import os
import time
import hmac
import hashlib
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

# ── Old ORM imports (kept for reference, replaced by supabase-py) ──────────────
# from sqlalchemy.orm import Session
# from app.models.document import Document as DocumentModel
# from app.models.document_result import DocumentResult as DocumentResultModel
# from app.models.processing_status import ProcessingStatus as ProcessingStatusModel

from app.db.supabase_client import get_supabase_client
from app.utils.logging_context import log_extra

logger = logging.getLogger(__name__)


class DocumentService:
    """
    Service layer for all document-related DB operations.
    Uses supabase-py for all reads and writes.
    """
    _supports_file_hash: Optional[bool] = None
    _file_hash_warning_logged: bool = False
    _supports_output_hash: Optional[bool] = None
    _output_hash_warning_logged: bool = False

    @staticmethod
    def generate_signed_download_url(
        *,
        file_url: str,
        file_path: str,
        secret: str,
        expires_in_seconds: int = 3600,
    ) -> Dict[str, Any]:
        if not secret:
            raise ValueError("SIGNED_URL_SECRET is required")
        expires = int(time.time()) + int(expires_in_seconds)
        signature = hmac.new(
            secret.encode("utf-8"),
            f"{file_path}{expires}".encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        parsed = urlparse(file_url)
        query = dict(parse_qsl(parsed.query))
        query.update({"token": signature, "expires": str(expires)})
        signed_url = urlunparse(parsed._replace(query=urlencode(query)))
        return {"url": signed_url, "expires": expires}

    @staticmethod
    def verify_signed_download(
        *,
        file_path: str,
        token: str,
        expires: int,
        secret: str,
    ) -> bool:
        if not secret or not token or not expires:
            return False
        try:
            expires_int = int(expires)
        except (TypeError, ValueError):
            return False
        if expires_int < int(time.time()):
            return False
        expected = hmac.new(
            secret.encode("utf-8"),
            f"{file_path}{expires_int}".encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, token)

    # ── Documents ──────────────────────────────────────────────────────────────

    @staticmethod
    def get_document(doc_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch a single document by ID.
        Optionally scope to a specific user_id for ownership checks.
        Returns None if not found or on error.
        """
        sb = get_supabase_client()
        doc_id = str(doc_id)
        if user_id: user_id = str(user_id)
        if sb is None:
            logger.error("get_document: Supabase client not available.", extra=log_extra(job_id=doc_id))
            return None
        try:
            query = sb.table("documents").select("*").eq("id", str(doc_id))
            if user_id:
                query = query.eq("user_id", str(user_id))
            result = query.maybe_single().execute()
            return result.data
        except Exception as exc:
            logger.error("get_document(%s) failed: %s", doc_id, exc, extra=log_extra(job_id=doc_id))
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
        user_id = str(user_id)
        if sb is None:
            logger.error("list_documents: Supabase client not available.", extra=log_extra())
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
            logger.error("list_documents(user=%s) failed: %s", user_id, exc, extra=log_extra())
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
            logger.error("count_documents(user=%s) failed: %s", user_id, exc, extra=log_extra())
            return 0

    @staticmethod
    def count_uploads_today(user_id: str) -> int:
        """
        Count uploads created by this user during the current UTC day.
        Returns 0 on error.
        """
        sb = get_supabase_client()
        if sb is None:
            return 0
        try:
            day_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            result = (
                sb.table("documents")
                .select("id", count="exact")
                .eq("user_id", str(user_id))
                .gte("created_at", day_start.isoformat())
                .lt("created_at", day_end.isoformat())
                .execute()
            )
            return int(result.count or 0)
        except Exception as exc:
            logger.error("count_uploads_today(user=%s) failed: %s", user_id, exc, extra=log_extra())
            return 0

    @staticmethod
    def create_document(
        doc_id: str,
        user_id: Optional[str],
        filename: str,
        template: Optional[str],
        original_file_path: Optional[str] = None,
        formatting_options: Optional[Dict[str, Any]] = None,
        file_hash: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Insert a new document row.
        Returns the inserted row dict or None on error.
        """
        sb = get_supabase_client()
        doc_id = str(doc_id)
        if user_id: user_id = str(user_id)
        if sb is None:
            logger.error("create_document: Supabase client not available.", extra=log_extra(job_id=doc_id))
            return None
        try:
            payload: Dict[str, Any] = {
                "id": str(doc_id),
                "filename": filename,
                "status": "PROCESSING",
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
            include_file_hash = (
                bool(file_hash)
                and DocumentService._supports_file_hash is not False
            )
            if include_file_hash:
                payload["file_hash"] = file_hash

            result = sb.table("documents").insert(payload).execute()
            if include_file_hash:
                DocumentService._supports_file_hash = True
            return result.data[0] if result.data else None
        except Exception as exc:
            # Backward-compat: some deployments don't yet have `documents.file_hash`.
            # Retry once without the optional field instead of failing upload.
            err = str(exc)
            missing_file_hash = (
                "file_hash" in err
                and ("schema cache" in err or "column" in err or "PGRST204" in err)
            )
            if missing_file_hash and "file_hash" in payload:
                try:
                    retry_payload = dict(payload)
                    retry_payload.pop("file_hash", None)
                    DocumentService._supports_file_hash = False
                    if not DocumentService._file_hash_warning_logged:
                        logger.warning(
                            "documents.file_hash not found in Supabase schema; "
                            "upload will continue without file hashing until migration is applied.",
                            extra=log_extra(job_id=doc_id),
                        )
                        DocumentService._file_hash_warning_logged = True
                    retry_result = sb.table("documents").insert(retry_payload).execute()
                    return retry_result.data[0] if retry_result.data else None
                except Exception as retry_exc:
                    logger.error(
                        "create_document(%s) retry without file_hash failed: %s",
                        doc_id,
                        retry_exc,
                        extra=log_extra(job_id=doc_id),
                    )
                    return None
            logger.error("create_document(%s) failed: %s", doc_id, exc, extra=log_extra(job_id=doc_id))
            return None

    @staticmethod
    def update_document(doc_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update fields on a document row.
        Returns the updated row dict or None on error.
        """
        sb = get_supabase_client()
        doc_id = str(doc_id)
        if sb is None:
            logger.error("update_document: Supabase client not available.", extra=log_extra(job_id=doc_id))
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
            logger.error("update_document(%s) failed: %s", doc_id, exc, extra=log_extra(job_id=doc_id))
            return None

    @staticmethod
    def delete_document(document_id: str, user_id: Optional[str] = None) -> bool:
        """
        Delete a document and associated DB artifacts/files.
        Returns True on success, raises on failure.
        """
        sb = get_supabase_client()
        doc_id = str(document_id)
        owner_id = str(user_id) if user_id else None

        if sb is None:
            raise RuntimeError("Supabase client not available")

        doc = DocumentService.get_document(doc_id, owner_id)
        if not doc:
            raise ValueError("Document not found or not owned by user")

        # Best-effort local file cleanup
        for key in ("output_path", "original_file_path"):
            candidate = doc.get(key)
            if candidate and os.path.isfile(candidate):
                try:
                    os.remove(candidate)
                except OSError as exc:
                    logger.warning(
                        "Failed to remove file %s for document %s: %s",
                        candidate,
                        doc_id,
                        exc,
                        extra=log_extra(job_id=doc_id),
                    )

        try:
            sb.table("processing_status").delete().eq("document_id", doc_id).execute()
            sb.table("document_results").delete().eq("document_id", doc_id).execute()
            sb.table("document_versions").delete().eq("document_id", doc_id).execute()
        except Exception as exc:
            logger.warning("Auxiliary cleanup failed for document %s: %s", doc_id, exc, extra=log_extra(job_id=doc_id))

        try:
            query = sb.table("documents").delete().eq("id", doc_id)
            if owner_id:
                query = query.eq("user_id", owner_id)
            result = query.execute()
            if result.data is not None and len(result.data) == 0:
                raise ValueError("Document delete affected 0 rows")
            return True
        except Exception as exc:
            logger.error("delete_document(%s, user=%s) failed: %s", doc_id, owner_id, exc, extra=log_extra(job_id=doc_id))
            raise

    @staticmethod
    def update_output_hash(doc_id: str, output_hash: str) -> bool:
        """
        Persist SHA256 for generated output artifacts.
        Returns True when persisted, False otherwise.
        """
        if not output_hash:
            return False
        if DocumentService._supports_output_hash is False:
            return False

        sb = get_supabase_client()
        if sb is None:
            return False
        try:
            sb.table("documents").update({"output_hash": output_hash}).eq("id", str(doc_id)).execute()
            DocumentService._supports_output_hash = True
            return True
        except Exception as exc:
            err = str(exc)
            missing_output_hash = (
                "output_hash" in err
                and ("schema cache" in err or "column" in err or "PGRST204" in err)
            )
            if missing_output_hash:
                DocumentService._supports_output_hash = False
                if not DocumentService._output_hash_warning_logged:
                    logger.warning(
                        "documents.output_hash not found in Supabase schema; "
                        "download integrity checks will be best-effort until migration is applied.",
                        extra=log_extra(job_id=doc_id),
                    )
                    DocumentService._output_hash_warning_logged = True
                return False
            logger.error("update_output_hash(%s) failed: %s", doc_id, exc, extra=log_extra(job_id=doc_id))
            return False

    @staticmethod
    def mark_document_failed(doc_id: str, error_message: str) -> None:
        """
        Convenience: mark a document as FAILED with an error message.
        Never raises — safe to call from background tasks and exception handlers.
        """
        sb = get_supabase_client()
        doc_id = str(doc_id)
        if sb is None:
            logger.error("mark_document_failed: Supabase client not available.", extra=log_extra(job_id=doc_id))
            return
        try:
            sb.table("documents").update({
                "status": "FAILED",
                "error_message": error_message,
                "progress": 0,
            }).eq("id", str(doc_id)).execute()
        except Exception as exc:
            logger.error("mark_document_failed(%s) failed: %s", doc_id, exc, extra=log_extra(job_id=doc_id))

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
        doc_id = str(doc_id)
        if sb is None:
            logger.error("mark_document_completed: Supabase client not available.", extra=log_extra(job_id=doc_id))
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
            logger.error("mark_document_completed(%s) failed: %s", doc_id, exc, extra=log_extra(job_id=doc_id))

    # ── Document Results ───────────────────────────────────────────────────────

    @staticmethod
    def get_document_result(doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch the processing result for a document.
        Returns None if not found or on error.
        """
        sb = get_supabase_client()
        doc_id = str(doc_id)
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
            logger.error("get_document_result(%s) failed: %s", doc_id, exc, extra=log_extra(job_id=doc_id))
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
        doc_id = str(doc_id)
        if sb is None:
            logger.error("upsert_document_result: Supabase client not available.", extra=log_extra(job_id=doc_id))
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
            logger.error("upsert_document_result(%s) failed: %s", doc_id, exc, extra=log_extra(job_id=doc_id))

    # ── Processing Status ──────────────────────────────────────────────────────

    @staticmethod
    def get_processing_statuses(doc_id: str) -> List[Dict[str, Any]]:
        """
        Fetch all processing phase statuses for a document.
        Returns empty list on error.
        """
        sb = get_supabase_client()
        doc_id = str(doc_id)
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
            logger.error("get_processing_statuses(%s) failed: %s", doc_id, exc, extra=log_extra(job_id=doc_id))
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
        doc_id = str(doc_id)
        if sb is None:
            logger.error("upsert_processing_status: Supabase client not available.", extra=log_extra(job_id=doc_id))
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
                "upsert_processing_status(%s, %s) failed: %s",
                doc_id,
                phase,
                exc,
                extra=log_extra(job_id=doc_id),
            )
