from __future__ import annotations

import logging
from typing import Any, Optional, Dict

from app.db.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


class AuditLogService:
    async def log(
        self,
        user_id: Optional[str],
        action: str,
        resource_type: str,
        resource_id: Optional[str],
        ip_address: Optional[str],
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        sb = get_supabase_client()
        if sb is None:
            logger.warning("Audit log skipped: Supabase client unavailable.")
            return
        payload = {
            "user_id": str(user_id) if user_id else None,
            "action": action,
            "resource_type": resource_type,
            "resource_id": str(resource_id) if resource_id else None,
            "ip_address": ip_address,
            "details": details or {},
        }
        try:
            sb.table("audit_log").insert(payload).execute()
        except Exception as exc:
            logger.warning("Audit log insert failed: %s", exc)


audit_log_service = AuditLogService()
