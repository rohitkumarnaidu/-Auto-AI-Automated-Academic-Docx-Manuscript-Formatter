import logging
import os
import uuid
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks, Query, Form
from app.utils.dependencies import get_current_user, get_optional_user
from app.schemas.user import User
from app.services.document_service import DocumentService
from app.pipeline.orchestrator import PipelineOrchestrator
from app.pipeline.export.pdf_exporter import PDFExporter
from app.config.settings import settings
from app.pipeline.safety.safe_execution import safe_async_function

# ── Old SQLAlchemy imports (kept for reference, replaced by DocumentService) ───
# from sqlalchemy import exc
# from app.db.session import SessionLocal
# from app.models import Document, ProcessingStatus, DocumentResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["Documents"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _require_db():
    """Raise HTTP 503 when the Supabase client is not configured."""
    from app.db.supabase_client import get_supabase_client
    if get_supabase_client() is None:
        raise HTTPException(
            status_code=503,
            detail="Database not configured. Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.",
        )


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.get("")
async def list_documents(
    status: Optional[str] = Query(None, description="Filter by status (RUNNING, COMPLETED, FAILED)"),
    template: Optional[str] = Query(None, description="Filter by template (IEEE, Springer, APA)"),
    start_date: Optional[datetime] = Query(None, description="Filter by created_at >= start_date"),
    end_date: Optional[datetime] = Query(None, description="Filter by created_at <= end_date"),
    limit: int = Query(50, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    List documents for the current user with optional filtering and pagination.
    Returns empty list for anonymous users.
    """
    _require_db()

    if not current_user:
        return {"documents": [], "total": 0, "limit": limit, "offset": offset}

    try:
        documents = DocumentService.list_documents(
            user_id=current_user.id,
            status=status,
            template=template,
            limit=limit,
            offset=offset,
        )
        total = DocumentService.count_documents(
            user_id=current_user.id,
            status=status,
            template=template,
        )

        return {
            "documents": [
                {
                    "id": str(doc.get("id")),
                    "filename": doc.get("filename"),
                    "template": doc.get("template"),
                    "status": doc.get("status"),
                    "progress": doc.get("progress", 0),
                    "current_stage": doc.get("current_stage"),
                    "error_message": doc.get("error_message"),
                    "created_at": doc.get("created_at"),
                    "updated_at": doc.get("updated_at"),
                }
                for doc in documents
            ],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        logger.error("Error listing documents: %s", e)
        return {"documents": [], "total": 0, "limit": limit, "offset": offset}


@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    template: str = Form(settings.DEFAULT_TEMPLATE),
    add_page_numbers: bool = Form(True),
    add_borders: bool = Form(False),
    add_cover_page: bool = Form(True),
    generate_toc: bool = Form(False),
    page_size: str = Form("Letter"),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Handle document upload and trigger async background processing.
    """
    _require_db()

    logger.debug("upload_document received template='%s' from request.", template)

    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
    ALLOWED_EXTENSIONS = {'.docx', '.pdf', '.tex', '.txt', '.html', '.htm', '.md', '.markdown', '.doc'}

    try:
        # ── File validation ────────────────────────────────────────────────────

        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type '{file_ext}'. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        safe_filename = os.path.basename(file.filename)
        if safe_filename != file.filename or '..' in file.filename:
            raise HTTPException(status_code=400, detail="Invalid filename. Path traversal detected.")

        file_content = await file.read()
        file_size = len(file_content)

        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large ({file_size / 1024 / 1024:.1f}MB). Maximum size is {MAX_FILE_SIZE / 1024 / 1024}MB"
            )

        if file_size == 0:
            raise HTTPException(status_code=400, detail="File is empty. Please upload a valid document.")

        # ── File storage ───────────────────────────────────────────────────────

        job_id = uuid.uuid4()
        file_path = os.path.abspath(os.path.join(UPLOAD_DIR, f"{job_id}{file_ext}"))
        upload_dir_abs = os.path.abspath(UPLOAD_DIR)

        if not file_path.startswith(upload_dir_abs):
            raise HTTPException(status_code=400, detail="Invalid file path detected")

        with open(file_path, "wb") as buffer:
            buffer.write(file_content)

        # ── DB insert via DocumentService ──────────────────────────────────────

        formatting_options = {
            "page_numbers": add_page_numbers,
            "borders": add_borders,
            "cover_page": add_cover_page,
            "toc": generate_toc,
            "page_size": page_size,
        }

        created = DocumentService.create_document(
            doc_id=str(job_id),
            user_id=str(current_user.id) if current_user else None,
            filename=safe_filename,
            template=template,
            original_file_path=file_path,
            formatting_options=formatting_options,
        )

        if created is None:
            raise HTTPException(status_code=503, detail="Database temporarily unavailable. Please retry later.")

        # ── Background pipeline ────────────────────────────────────────────────

        from app.utils.background_tasks import run_pipeline_with_timeout
        orchestrator = PipelineOrchestrator()
        background_tasks.add_task(
            run_pipeline_with_timeout,
            orchestrator=orchestrator,
            input_path=file_path,
            job_id=job_id,
            template_name=template,
            formatting_options=formatting_options,
        )

        return {"message": "Processing started", "job_id": str(job_id), "status": "RUNNING"}

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error("Upload error: %s\n%s", e, traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/{job_id}/status")
async def get_status(
    job_id: str,
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get the detailed processing status of a document.
    """
    try:
        doc = DocumentService.get_document(job_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document job not found")

        # Security: ownership check
        if doc.get("user_id") is not None:
            if not current_user or str(doc["user_id"]) != str(current_user.id):
                raise HTTPException(status_code=403, detail="Not authorized to access this document")

        statuses = DocumentService.get_processing_statuses(job_id)

        return {
            "job_id": job_id,
            "status": doc.get("status"),
            "current_phase": doc.get("current_stage") or "UPLOADED",
            "phase": doc.get("current_stage") or "UPLOADED",
            "progress_percentage": doc.get("progress") or 0,
            "message": doc.get("error_message") or (
                (doc.get("current_stage") + "...") if doc.get("current_stage") else "Processing..."
            ),
            "updated_at": doc.get("updated_at") or doc.get("created_at"),
            "phases": [
                {
                    "phase": s.get("phase"),
                    "status": s.get("status"),
                    "message": s.get("message"),
                    "progress": s.get("progress_percentage"),
                    "updated_at": s.get("updated_at"),
                }
                for s in statuses
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Status check failed for job %s: %s", job_id, e)
        return {
            "job_id": job_id,
            "status": "ERROR",
            "message": f"Status check failed: {str(e)}",
            "progress_percentage": 0,
        }


@router.post("/{job_id}/edit")
async def edit_document(
    job_id: str,
    data: dict,
    background_tasks: BackgroundTasks,
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Handle user edits and trigger non-destructive re-formatting.
    """
    try:
        doc = DocumentService.get_document(job_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if doc.get("user_id") is not None:
            if not current_user or str(doc["user_id"]) != str(current_user.id):
                raise HTTPException(status_code=403, detail="Not authorized to edit this document")

        edited_data = data.get("edited_structured_data")
        if not edited_data:
            raise HTTPException(status_code=400, detail="Missing edited_structured_data")

        orchestrator = PipelineOrchestrator()
        background_tasks.add_task(
            orchestrator.run_edit_flow,
            job_id=job_id,
            edited_structured_data=edited_data,
            template_name=doc.get("template"),
        )

        return {"message": "Edit received, re-formatting started", "job_id": job_id, "status": "RUNNING"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error editing document %s: %s", job_id, e)
        raise HTTPException(status_code=500, detail=f"Edit failed: {str(e)}")


@router.get("/{job_id}/preview")
async def get_preview(
    job_id: str,
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get the structured preview data for a document.
    """
    try:
        doc = DocumentService.get_document(job_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if doc.get("user_id") is not None:
            if not current_user or str(doc["user_id"]) != str(current_user.id):
                raise HTTPException(status_code=403, detail="Not authorized to preview this document")

        result = DocumentService.get_document_result(job_id)
        if not result:
            raise HTTPException(status_code=404, detail="Processing results not found")

        return {
            "structured_data": result.get("structured_data"),
            "validation_results": result.get("validation_results"),
            "metadata": {
                "filename": doc.get("filename"),
                "template": doc.get("template"),
                "status": doc.get("status"),
                "created_at": doc.get("created_at"),
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving preview for %s: %s", job_id, e)
        raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")


@router.get("/{job_id}/compare")
async def get_comparison_data(
    job_id: str,
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get data for side-by-side comparison with HTML diff.
    """
    import difflib

    try:
        doc = DocumentService.get_document(job_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if doc.get("user_id") is not None:
            if not current_user or str(doc["user_id"]) != str(current_user.id):
                raise HTTPException(status_code=403, detail="Not authorized to access comparison data")

        if doc.get("status") != "COMPLETED":
            logger.warning("Compare endpoint called too early for job %s. Status: %s", job_id, doc.get("status"))
            raise HTTPException(
                status_code=400,
                detail=f"Comparison data not available. Job status: {doc.get('status')}. Wait for COMPLETED status.",
            )

        result = DocumentService.get_document_result(job_id)
        if not result:
            logger.warning("DocumentResult missing for completed job %s", job_id)
            raise HTTPException(status_code=404, detail="Processing results not found")

        original_text = doc.get("raw_text") or ""
        formatted_text = ""
        structured_data = result.get("structured_data")
        if structured_data and isinstance(structured_data, dict):
            blocks = structured_data.get("blocks", [])
            formatted_text = "\n\n".join([
                block.get("text", "") for block in blocks
                if isinstance(block, dict) and block.get("text")
            ])

        html_diff = difflib.HtmlDiff(wrapcolumn=80).make_file(
            original_text.splitlines(keepends=True),
            formatted_text.splitlines(keepends=True),
            fromdesc="Original Document",
            todesc="Formatted Document",
            context=True,
            numlines=3,
        )

        return {
            "html_diff": html_diff,
            "original": {"raw_text": original_text, "structured_data": None},
            "formatted": {"structured_data": structured_data},
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error comparing documents for %s: %s", job_id, e)
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@router.get("/{job_id}/download")
async def download_document(
    job_id: str,
    format: str = "docx",
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Download the processed document in DOCX or PDF format.
    Returns actual binary file stream.
    """
    from fastapi.responses import FileResponse

    try:
        doc = DocumentService.get_document(job_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document job not found")

        if doc.get("user_id") is not None:
            if not current_user or str(doc["user_id"]) != str(current_user.id):
                raise HTTPException(status_code=403, detail="Not authorized to download this document")

        if doc.get("status") != "COMPLETED":
            logger.warning("Download endpoint called too early for job %s. Status: %s", job_id, doc.get("status"))
            raise HTTPException(
                status_code=400,
                detail=f"Document not ready. Job status: {doc.get('status')}. Wait for COMPLETED status.",
            )

        output_path = doc.get("output_path")
        if not output_path:
            logger.error("Output path missing for completed job %s", job_id)
            raise HTTPException(
                status_code=500,
                detail="Processing completed but output file path not set. Contact support.",
            )

        if not os.path.exists(output_path):
            logger.error("Output file missing on disk for job %s: %s", job_id, output_path)
            raise HTTPException(status_code=404, detail="Output file not found on server. File may have been deleted.")

        path_to_serve = output_path
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = f"{os.path.splitext(doc.get('filename', 'document'))[0]}_formatted.docx"

        if format.lower() == "pdf":
            pdf_path = output_path.replace(".docx", ".pdf")
            if not os.path.exists(pdf_path):
                try:
                    exporter = PDFExporter()
                    generated_path = exporter.convert_to_pdf(output_path, os.path.dirname(output_path))
                    if not generated_path:
                        raise HTTPException(status_code=500, detail="PDF conversion failed unexpectedly.")
                    pdf_path = generated_path
                except RuntimeError as re:
                    logger.error("PDF Export Error for job %s: %s", job_id, re)
                    raise HTTPException(status_code=400, detail=f"PDF export unavailable: {str(re)}")
                except HTTPException:
                    raise
                except Exception as e:
                    logger.error("Unexpected PDF Error for job %s: %s", job_id, e)
                    raise HTTPException(status_code=500, detail="An internal error occurred during PDF export.")

            path_to_serve = pdf_path
            media_type = "application/pdf"
            filename = f"{os.path.splitext(doc.get('filename', 'document'))[0]}_formatted.pdf"

        elif format.lower() != "docx":
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}. Use 'docx' or 'pdf'.")

        return FileResponse(path=path_to_serve, media_type=media_type, filename=filename)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error downloading document %s: %s", job_id, e)
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")
