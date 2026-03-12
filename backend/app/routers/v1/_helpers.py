from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Any, Mapping, Optional

from fastapi import HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from starlette.responses import Response

from app.middleware.request_id import get_request_id
from app.schemas.api_envelope import error_response, success_response

DEFAULT_ERROR_CODES = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    409: "CONFLICT",
    413: "PAYLOAD_TOO_LARGE",
    422: "VALIDATION_ERROR",
    429: "RATE_LIMITED",
    500: "INTERNAL_SERVER_ERROR",
    501: "NOT_IMPLEMENTED",
    502: "BAD_GATEWAY",
    503: "SERVICE_UNAVAILABLE",
}


def build_success_response(
    request: Request,
    data: Any,
    *,
    status_code: int = 200,
) -> JSONResponse:
    payload = success_response(jsonable_encoder(data), get_request_id(request))
    return JSONResponse(
        status_code=status_code,
        content=payload.model_dump(mode="json", exclude_none=True),
    )


def build_error_response(
    request: Request,
    *,
    status_code: int,
    code: str,
    message: str,
    details: Optional[Mapping[str, Any]] = None,
) -> JSONResponse:
    payload = error_response(
        code=code,
        message=message,
        request_id=get_request_id(request),
        details=jsonable_encoder(details) if details is not None else None,
    )
    return JSONResponse(
        status_code=status_code,
        content=payload.model_dump(mode="json", exclude_none=True),
    )


def http_exception_to_response(
    request: Request,
    exc: HTTPException,
    *,
    code_map: Optional[Mapping[int, str]] = None,
) -> JSONResponse:
    detail = exc.detail
    if isinstance(detail, str):
        message = detail
        details = None
    else:
        message = "Request failed"
        details = {"detail": jsonable_encoder(detail)}

    code = (code_map or {}).get(exc.status_code) or DEFAULT_ERROR_CODES.get(
        exc.status_code,
        "API_ERROR",
    )
    return build_error_response(
        request,
        status_code=exc.status_code,
        code=code,
        message=message,
        details=details,
    )


async def run_enveloped(
    request: Request,
    operation: Callable[[], Awaitable[Any]],
    *,
    success_status_code: int = 200,
    code_map: Optional[Mapping[int, str]] = None,
    logger: Optional[logging.Logger] = None,
    operation_name: str = "request",
):
    try:
        result = await operation()
    except HTTPException as exc:
        return http_exception_to_response(request, exc, code_map=code_map)
    except Exception:
        if logger is not None:
            logger.exception("Unhandled error while processing %s", operation_name)
        return build_error_response(
            request,
            status_code=500,
            code="INTERNAL_SERVER_ERROR",
            message="Internal server error",
        )

    if isinstance(result, Response):
        return result

    return build_success_response(
        request,
        result,
        status_code=success_status_code,
    )
