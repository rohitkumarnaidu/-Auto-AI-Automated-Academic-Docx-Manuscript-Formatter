# -*- coding: utf-8 -*-
"""
Generator Router -- /generate endpoints for the Document Generator feature.

Routes:
  POST   /generate               -- Start generation job (202 Accepted)
  GET    /generate/status/{id}   -- Poll job status
  GET    /generate/download/{id} -- Download generated DOCX/PDF
"""
from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse

from app.pipeline.export.pdf_exporter import PDFExporter
from app.pipeline.generation.document_generator import get_generator
from app.routers.deprecation import DeprecatedRoute
from app.schemas.document import (
    GenerateRequest,
    GenerateResponse,
    GenerateStatusResponse,
    GenerationOptions,
)
from app.services.document_service import DocumentService
from app.services.enhancement_manager import enhancement_manager
from app.utils.dependencies import get_current_user

logger = logging.getLogger(__name__)

_LEGACY_SUCCESSORS = {
    "/generate": "/api/v1/generator/sessions",
    "/generate/status/{job_id}": "/api/v1/generator/sessions/{sessionId}",
    "/generate/download/{job_id}": "/api/v1/generator/sessions/{sessionId}/download",
    "/api/generate": "/api/v1/generator/sessions",
    "/api/generate/status/{job_id}": "/api/v1/generator/sessions/{sessionId}",
    "/api/generate/download/{job_id}": "/api/v1/generator/sessions/{sessionId}/download",
}


class LegacyGeneratorRoute(DeprecatedRoute):
    successor_map = _LEGACY_SUCCESSORS


router = APIRouter(prefix="/generate", tags=["generator"], route_class=LegacyGeneratorRoute)


def _assert_generation_owner(job_id: str, user_id: str) -> None:
    """
    Validate ownership when a DB-backed generation job record exists.
    In-memory-only jobs are tolerated for local/dev fallback mode.
    """
    generator = get_generator()
    session = generator.get_session(job_id)
    if session:
        owner = session.get("user_id")
        if owner and str(owner) != str(user_id):
            raise HTTPException(status_code=403, detail="Not authorized to access this generation job.")
        return

    record = DocumentService.get_document(job_id)
    if not record:
        return
    owner = record.get("user_id")
    if owner and str(owner) != str(user_id):
        raise HTTPException(status_code=403, detail="Not authorized to access this generation job.")


@router.post("", response_model=GenerateResponse, status_code=202)
async def start_generation(
    request: GenerateRequest,
    background_tasks: BackgroundTasks,
    user=Depends(get_current_user),
):
    """
    Start a new document generation job.
    Returns immediately with a job_id.
    Poll GET /generate/status/{job_id} for progress.
    """
    valid_types = {"academic_paper", "resume", "portfolio", "report", "thesis"}
    if request.doc_type not in valid_types:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid doc_type '{request.doc_type}'. Must be one of: {sorted(valid_types)}",
        )

    generator = get_generator()
    try:
        user_id = user.id if hasattr(user, "id") else str(user)
    except Exception:
        user_id = "anonymous"

    job_id = await generator.start_job(
        doc_type=request.doc_type,
        template=request.template,
        metadata=request.metadata,
        options=request.options.model_dump(),
        user_id=str(user_id),
    )

    dispatch_info = enhancement_manager.dispatch_generation_pipeline(
        background_tasks=background_tasks,
        run_pipeline=generator.run_pipeline,
        job_id=job_id,
    )
    logger.info("Generation dispatch mode for job %s: %s", job_id, dispatch_info.get("mode"))
    logger.info("Generation job %s queued for user %s", job_id, user_id)

    return GenerateResponse(
        job_id=job_id,
        status="pending",
        message=f"Generation job queued. Poll /generate/status/{job_id} for progress.",
    )


@router.get("/status/{job_id}", response_model=GenerateStatusResponse)
async def get_generation_status(
    job_id: str,
    user=Depends(get_current_user),
):
    """
    Poll the status of a generation job.
    """
    user_id = user.id if hasattr(user, "id") else str(user)
    _assert_generation_owner(job_id, str(user_id))

    generator = get_generator()
    try:
        status = generator.get_status(job_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Generation job '{job_id}' not found.")

    return GenerateStatusResponse(**status)


@router.get("/download/{job_id}")
async def download_generated(
    job_id: str,
    format: str = "docx",
    user=Depends(get_current_user),
):
    """
    Download the generated document in DOCX or PDF format.
    The document must be in 'done' status.
    """
    requested_format = (format or "").strip().lower()
    if requested_format not in {"docx", "pdf"}:
        raise HTTPException(status_code=400, detail="Unsupported format. Supported: docx, pdf")

    user_id = user.id if hasattr(user, "id") else str(user)
    _assert_generation_owner(job_id, str(user_id))

    generator = get_generator()
    try:
        status = generator.get_status(job_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Generation job '{job_id}' not found.")

    if status["status"] != "done":
        raise HTTPException(
            status_code=409,
            detail=f"Job is not yet complete. Current status: {status['status']} ({status['progress']}%)",
        )

    output_path = generator.get_download_path(job_id)
    if not output_path or not output_path.exists():
        raise HTTPException(status_code=404, detail="Generated file not found on server.")

    path_to_serve = output_path
    media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    filename = f"generated_{job_id[:8]}.docx"

    if requested_format == "pdf":
        pdf_path = output_path.with_suffix(".pdf")
        if not pdf_path.exists():
            try:
                exporter = PDFExporter()
                generated_pdf = exporter.convert_to_pdf(str(output_path), str(output_path.parent))
                if not generated_pdf:
                    raise HTTPException(status_code=500, detail="PDF conversion failed unexpectedly.")
                candidate = Path(generated_pdf)
                if not candidate.is_absolute():
                    candidate = output_path.parent / candidate
                if candidate.exists():
                    pdf_path = candidate
            except RuntimeError as exc:
                raise HTTPException(status_code=400, detail=f"PDF export unavailable: {exc}")
            except HTTPException:
                raise
            except Exception as exc:
                logger.error("Unexpected PDF export error for job %s: %s", job_id, exc)
                raise HTTPException(status_code=500, detail="An internal error occurred during PDF export.")

        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail="Generated PDF not found on server.")

        path_to_serve = pdf_path
        media_type = "application/pdf"
        filename = f"generated_{job_id[:8]}.pdf"

    return FileResponse(
        path=str(path_to_serve),
        media_type=media_type,
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
