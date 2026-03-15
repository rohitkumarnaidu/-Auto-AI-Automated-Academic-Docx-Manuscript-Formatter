from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query, Request

from app.routers import templates as legacy_templates
from app.schemas.user import User
from app.utils.dependencies import get_optional_user
from app.utils.logging_context import bind_request_context

from ._helpers import run_enveloped

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(bind_request_context)])


@router.get("")
async def list_builtin_templates(request: Request):
    async def operation():
        return await legacy_templates.list_builtin_templates()

    return await run_enveloped(
        request,
        operation,
        logger=logger,
        operation_name="template list",
    )


@router.get("/csl/search")
async def csl_search(
    request: Request,
    q: Optional[str] = Query(default=None, min_length=1),
    query: Optional[str] = Query(default=None, min_length=1),
):
    async def operation():
        return await legacy_templates.csl_search(q=q, query=query)

    return await run_enveloped(
        request,
        operation,
        code_map={422: "INVALID_TEMPLATE_QUERY"},
        logger=logger,
        operation_name="template csl search",
    )


@router.get("/csl/fetch")
async def csl_fetch(
    request: Request,
    slug: str = Query(..., min_length=1),
):
    async def operation():
        return await legacy_templates.csl_fetch(slug=slug)

    return await run_enveloped(
        request,
        operation,
        code_map={
            400: "INVALID_STYLE_SLUG",
            502: "STYLE_FETCH_FAILED",
        },
        logger=logger,
        operation_name="template csl fetch",
    )


@router.get("/csl/{styleId}")
async def csl_fetch_by_style_id(
    request: Request,
    styleId: str,
):
    async def operation():
        return await legacy_templates.csl_fetch_by_style_id(style_id=styleId)

    return await run_enveloped(
        request,
        operation,
        code_map={
            400: "INVALID_STYLE_SLUG",
            502: "STYLE_FETCH_FAILED",
        },
        logger=logger,
        operation_name="template style fetch",
    )


@router.get("/custom")
async def list_custom_templates(
    request: Request,
    current_user: Optional[User] = Depends(get_optional_user),
):
    async def operation():
        return await legacy_templates.list_custom_templates(current_user=current_user)

    return await run_enveloped(
        request,
        operation,
        code_map={
            401: "UNAUTHORIZED",
            500: "TEMPLATE_LIST_FAILED",
        },
        logger=logger,
        operation_name="custom template list",
    )


@router.post("/custom")
async def create_custom_template(
    request: Request,
    payload: Dict[str, Any],
    current_user: Optional[User] = Depends(get_optional_user),
):
    async def operation():
        return await legacy_templates.create_custom_template(
            request=request,
            payload=payload,
            current_user=current_user,
        )

    return await run_enveloped(
        request,
        operation,
        code_map={
            401: "UNAUTHORIZED",
            422: "INVALID_TEMPLATE_PAYLOAD",
            500: "TEMPLATE_CREATE_FAILED",
        },
        logger=logger,
        operation_name="custom template create",
    )


@router.put("/custom/{templateId}")
async def update_custom_template(
    request: Request,
    templateId: str,
    payload: Dict[str, Any],
    current_user: Optional[User] = Depends(get_optional_user),
):
    async def operation():
        return await legacy_templates.update_custom_template(
            request=request,
            template_id=templateId,
            payload=payload,
            current_user=current_user,
        )

    return await run_enveloped(
        request,
        operation,
        code_map={
            401: "UNAUTHORIZED",
            404: "TEMPLATE_NOT_FOUND",
            422: "INVALID_TEMPLATE_PAYLOAD",
            500: "TEMPLATE_UPDATE_FAILED",
        },
        logger=logger,
        operation_name="custom template update",
    )


@router.delete("/custom/{templateId}")
async def delete_custom_template(
    request: Request,
    templateId: str,
    current_user: Optional[User] = Depends(get_optional_user),
):
    async def operation():
        return await legacy_templates.delete_custom_template(
            template_id=templateId,
            current_user=current_user,
        )

    return await run_enveloped(
        request,
        operation,
        code_map={
            401: "UNAUTHORIZED",
            404: "TEMPLATE_NOT_FOUND",
            500: "TEMPLATE_DELETE_FAILED",
        },
        logger=logger,
        operation_name="custom template delete",
    )
