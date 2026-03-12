from __future__ import annotations

import logging

from fastapi import APIRouter, Request

from app.services.health_checks import get_readiness_payload

from ._helpers import build_error_response, build_success_response

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/live")
async def live(request: Request):
    return build_success_response(request, {"status": "alive"})


@router.get("/ready")
async def ready(request: Request):
    try:
        payload, status_code = await get_readiness_payload()
    except Exception:
        logger.exception("Failed to build readiness payload")
        return build_error_response(
            request,
            status_code=500,
            code="READINESS_CHECK_FAILED",
            message="Failed to evaluate readiness state",
        )

    return build_success_response(request, payload, status_code=status_code)
