from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks, Depends, Request

from app.routers import generator as legacy_generator
from app.schemas.document import GenerateRequest
from app.utils.dependencies import get_current_user

from ._helpers import build_error_response, run_enveloped

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/sessions", status_code=202)
async def start_generation(
    request: Request,
    payload: GenerateRequest,
    background_tasks: BackgroundTasks,
    user=Depends(get_current_user),
):
    async def operation():
        return await legacy_generator.start_generation(
            request=payload,
            background_tasks=background_tasks,
            user=user,
        )

    return await run_enveloped(
        request,
        operation,
        success_status_code=202,
        code_map={422: "INVALID_GENERATION_REQUEST"},
        logger=logger,
        operation_name="generation session create",
    )


@router.get("/sessions/{sessionId}")
async def get_generation_status(
    request: Request,
    sessionId: str,
    user=Depends(get_current_user),
):
    async def operation():
        return await legacy_generator.get_generation_status(job_id=sessionId, user=user)

    return await run_enveloped(
        request,
        operation,
        code_map={
            403: "GENERATION_ACCESS_DENIED",
            404: "SESSION_NOT_FOUND",
        },
        logger=logger,
        operation_name="generation session status",
    )


@router.get("/sessions/{sessionId}/download")
async def download_generated(
    request: Request,
    sessionId: str,
    format: str = "docx",
    user=Depends(get_current_user),
):
    async def operation():
        return await legacy_generator.download_generated(
            job_id=sessionId,
            format=format,
            user=user,
        )

    return await run_enveloped(
        request,
        operation,
        code_map={
            400: "INVALID_EXPORT_FORMAT",
            403: "GENERATION_ACCESS_DENIED",
            404: "SESSION_NOT_FOUND",
            409: "SESSION_NOT_READY",
        },
        logger=logger,
        operation_name="generation session download",
    )


@router.get("/sessions/{sessionId}/events")
async def generation_events(
    request: Request,
    sessionId: str,
    user=Depends(get_current_user),
):
    return build_error_response(
        request,
        status_code=501,
        code="EVENT_STREAM_NOT_IMPLEMENTED",
        message="Generation event streaming will be added in Module 3.",
        details={"session_id": sessionId},
    )


@router.post("/sessions/{sessionId}/messages")
async def generation_messages(
    request: Request,
    sessionId: str,
    payload: Dict[str, Any],
    user=Depends(get_current_user),
):
    return build_error_response(
        request,
        status_code=501,
        code="SESSION_MESSAGES_NOT_IMPLEMENTED",
        message="Session messaging will be added in Module 4.",
        details={"session_id": sessionId, "payload": payload},
    )


@router.post("/sessions/{sessionId}/outline/approve")
async def approve_outline(
    request: Request,
    sessionId: str,
    payload: Dict[str, Any],
    user=Depends(get_current_user),
):
    return build_error_response(
        request,
        status_code=501,
        code="OUTLINE_APPROVAL_NOT_IMPLEMENTED",
        message="Outline approval will be added in Module 5.",
        details={"session_id": sessionId, "payload": payload},
    )
