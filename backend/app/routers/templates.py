from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query

from app.db.supabase_client import get_supabase_client
from app.pipeline.services.csl_fetcher import search_styles, fetch_style
from app.schemas.user import User
from app.utils.dependencies import get_optional_user

logger = logging.getLogger(__name__)

templates_router = APIRouter()


def _require_db():
    sb = get_supabase_client()
    if sb is None:
        raise HTTPException(
            status_code=503,
            detail="Database not configured. Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.",
        )
    return sb


def _require_user(current_user: Optional[User]) -> User:
    if current_user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return current_user


def _extract_template_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise HTTPException(status_code=422, detail="Invalid template payload")

    candidate = payload.get("template")
    if isinstance(candidate, dict):
        template_data = candidate
    else:
        template_data = payload

    if not isinstance(template_data, dict):
        raise HTTPException(status_code=422, detail="Invalid template payload")

    name = str(template_data.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=422, detail="Template name is required")

    config = template_data.get("config")
    if config is None:
        config = template_data.get("settings")
    if config is None:
        config = payload.get("config")
    if config is None:
        config = {}
    if not isinstance(config, dict):
        raise HTTPException(status_code=422, detail="Template config must be an object")

    description = template_data.get("description", payload.get("description", ""))
    if description is None:
        description = ""
    description = str(description)

    template_id = str(template_data.get("id") or payload.get("id") or uuid4())

    now_iso = datetime.now(timezone.utc).isoformat()
    created_at = (
        template_data.get("created_at")
        or template_data.get("createdAt")
        or payload.get("created_at")
        or payload.get("createdAt")
        or now_iso
    )
    updated_at = now_iso

    return {
        "id": template_id,
        "name": name,
        "description": description,
        "config": config,
        "created_at": str(created_at),
        "updated_at": updated_at,
    }


@templates_router.get("/")
async def list_builtin_templates():
    """List all built-in templates (public)."""
    templates_dir = Path(__file__).resolve().parents[1] / "templates"
    descriptions = {
        "ieee": "IEEE manuscript style",
        "springer": "Springer journal style",
        "apa": "APA style",
        "nature": "Nature style",
        "vancouver": "Vancouver citation style",
    }

    items = []
    if templates_dir.exists():
        for entry in sorted(templates_dir.iterdir()):
            if entry.is_dir() and not entry.name.startswith("__"):
                template_id = entry.name
                items.append(
                    {
                        "id": template_id,
                        "name": template_id.upper() if template_id != "none" else "None",
                        "description": descriptions.get(template_id, f"{template_id.title()} template"),
                        "source": "built_in",
                    }
                )

    return {"templates": items}


@templates_router.get("/csl/search")
async def csl_search(query: str = Query(..., min_length=1)):
    """Search CSL styles by keyword."""
    results = await search_styles(query)
    return {"query": query, "results": results}


@templates_router.get("/csl/fetch")
async def csl_fetch(slug: str = Query(..., min_length=1)):
    """Fetch CSL XML by style slug."""
    try:
        style = await fetch_style(slug)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error("Failed to fetch CSL style '%s': %s", slug, exc)
        raise HTTPException(status_code=502, detail=f"Failed to fetch CSL style '{slug}'")
    return style


@templates_router.get("/custom")
async def list_custom_templates(current_user: Optional[User] = Depends(get_optional_user)):
    """List authenticated user's custom templates."""
    user = _require_user(current_user)
    sb = _require_db()
    try:
        result = (
            sb.table("custom_templates")
            .select("*")
            .eq("user_id", str(user.id))
            .order("updated_at", desc=True)
            .execute()
        )
        return {"templates": result.data or []}
    except Exception as exc:
        logger.error("Failed to list custom templates: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to list custom templates")


@templates_router.post("/custom")
async def create_custom_template(
    payload: Dict[str, Any],
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Create a custom template for the authenticated user."""
    user = _require_user(current_user)
    sb = _require_db()
    record = _extract_template_payload(payload)
    record["user_id"] = str(user.id)

    try:
        result = sb.table("custom_templates").insert(record).execute()
        created = result.data[0] if result.data else record
        return {"template": created}
    except Exception as exc:
        logger.error("Failed to create custom template: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to create custom template")


@templates_router.put("/custom/{template_id}")
async def update_custom_template(
    template_id: str,
    payload: Dict[str, Any],
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Update an authenticated user's custom template."""
    user = _require_user(current_user)
    sb = _require_db()
    parsed = _extract_template_payload(payload)

    updates = {
        "name": parsed["name"],
        "description": parsed["description"],
        "config": parsed["config"],
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        result = (
            sb.table("custom_templates")
            .update(updates)
            .eq("id", template_id)
            .eq("user_id", str(user.id))
            .execute()
        )
        if not result.data:
            raise HTTPException(status_code=404, detail="Template not found")
        return {"template": result.data[0]}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to update custom template %s: %s", template_id, exc)
        raise HTTPException(status_code=500, detail="Failed to update custom template")


@templates_router.delete("/custom/{template_id}")
async def delete_custom_template(
    template_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Delete an authenticated user's custom template."""
    user = _require_user(current_user)
    sb = _require_db()

    try:
        existing = (
            sb.table("custom_templates")
            .select("id")
            .eq("id", template_id)
            .eq("user_id", str(user.id))
            .maybe_single()
            .execute()
        )
        if not existing.data:
            raise HTTPException(status_code=404, detail="Template not found")

        sb.table("custom_templates").delete().eq("id", template_id).eq("user_id", str(user.id)).execute()
        return {"status": "deleted", "id": template_id}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to delete custom template %s: %s", template_id, exc)
        raise HTTPException(status_code=500, detail="Failed to delete custom template")
