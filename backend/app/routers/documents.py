import os
import shutil
import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy import exc
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks, Query
from app.utils.dependencies import get_current_user, get_optional_user
from app.schemas.user import User
from app.db.session import SessionLocal
from app.models import Document, ProcessingStatus, DocumentResult
from app.pipeline.orchestrator import PipelineOrchestrator
from app.pipeline.export.pdf_exporter import PDFExporter

router = APIRouter(prefix="/api/documents", tags=["Documents"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

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
    db = SessionLocal()
    try:
        # Anonymous users get empty list
        if not current_user:
            return {
                "documents": [],
                "total": 0,
                "limit": limit,
                "offset": offset
            }
        
        # Build query
        query = db.query(Document).filter(Document.user_id == current_user.id)
        
        # Apply filters
        if status:
            query = query.filter(Document.status == status.upper())
        if template:
            query = query.filter(Document.template == template.upper())
        if start_date:
            query = query.filter(Document.created_at >= start_date)
        if end_date:
            query = query.filter(Document.created_at <= end_date)
        
        # Get total count before pagination
        total = query.count()
        
        # Apply pagination and ordering
        documents = query.order_by(Document.created_at.desc()).offset(offset).limit(limit).all()
        
        # Format response
        return {
            "documents": [
                {
                    "id": str(doc.id),
                    "filename": doc.filename,
                    "template": doc.template,
                    "status": doc.status,
                    "progress": doc.progress,
                    "current_stage": doc.current_stage,
                    "error_message": doc.error_message,
                    "created_at": doc.created_at.isoformat() if doc.created_at else None,
                    "updated_at": doc.updated_at.isoformat() if doc.updated_at else None
                }
                for doc in documents
            ],
            "total": total,
            "limit": limit,
            "offset": offset
        }
    finally:
        db.close()

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    template: str = "IEEE",
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Handle document upload and trigger async background processing.
    Note: This project intentionally avoids automated pipeline testing at this stage.
    """
    db = SessionLocal()
    try:
        # 1. Create Job Entry
        job_id = uuid.uuid4()
        
        # Save file to local storage
        file_ext = os.path.splitext(file.filename)[1]
        file_path = os.path.join(UPLOAD_DIR, f"{job_id}{file_ext}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create Document record with RUNNING status initially
        new_doc = Document(
            id=job_id,
            user_id=current_user.id if current_user else None,
            filename=file.filename,
            template=template,
            status="RUNNING",
            original_file_path=os.path.abspath(file_path)
        )
        db.add(new_doc)
        db.commit()
        
        # Offload logic to background
        orchestrator = PipelineOrchestrator()
        background_tasks.add_task(
            orchestrator.run_pipeline,
            input_path=os.path.abspath(file_path),
            job_id=job_id,
            template_name=template
        )
        
        return {
            "message": "Processing started",
            "job_id": str(job_id),
            "status": "RUNNING"
        }
    except exc.OperationalError as e:
        # Database is unreachable (DNS failure, connection timeout, etc.)
        db.rollback()
        print(f"Upload failed: Database unavailable. Error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Database temporarily unavailable. Please retry later."
        )
    except Exception as e:
        db.rollback()
        import traceback
        error_detail = {
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }
        print(f"Upload error: {error_detail}")  # Server-side logging
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    finally:
        db.close()

@router.get("/{job_id}/status")
async def get_status(
    job_id: str,
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get the detailed processing status of a document.
    """
    db = SessionLocal()
    try:
        doc = db.query(Document).filter_by(id=job_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document job not found")
        
        # Security: Scoping
        if doc.user_id is not None:
            if not current_user or doc.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not authorized to access this document")
        
        statuses = db.query(ProcessingStatus).filter_by(document_id=job_id).all()
        
        return {
            "job_id": job_id,
            "status": doc.status, # RUNNING, COMPLETED, FAILED
            "current_phase": doc.current_stage or "UPLOADED",
            "phase": doc.current_stage or "UPLOADED", # Alias for frontend compatibility
            "progress_percentage": doc.progress or 0,
            "message": doc.error_message or (doc.current_stage + "..." if doc.current_stage else "Processing..."),
            "updated_at": doc.updated_at or doc.created_at,
            "phases": [
                {
                    "phase": s.phase,
                    "status": s.status,
                    "message": getattr(s, "message", None),
                    "progress": s.progress_percentage,
                    "updated_at": s.updated_at
                } for s in statuses
            ]
        }
    except exc.OperationalError:
        # DB connection lost or server closed unexpectedly (common on reload)
        return {
            "job_id": job_id,
            "status": "UNSTABLE",
            "message": "Database connection interrupted. Retrying...",
            "progress_percentage": 0
        }
    except Exception as e:
        # Any other unexpected crash
        return {
            "job_id": job_id,
            "status": "ERROR",
            "message": f"Status check failed: {str(e)}",
            "progress_percentage": 0
        }
    finally:
        db.close()

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
    db = SessionLocal()
    try:
        doc = db.query(Document).filter_by(id=job_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
            
        # Security: Scoping
        if doc.user_id is not None:
            if not current_user or doc.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not authorized to edit this document")
        
        edited_data = data.get("edited_structured_data")
        if not edited_data:
            raise HTTPException(status_code=400, detail="Missing edited_structured_data")
        
        # Trigger edit flow in background
        orchestrator = PipelineOrchestrator()
        background_tasks.add_task(
            orchestrator.run_edit_flow,
            job_id=job_id,
            edited_structured_data=edited_data,
            template_name=doc.template
        )
        
        return {
            "message": "Edit received, re-formatting started",
            "job_id": job_id,
            "status": "RUNNING"
        }
    finally:
        db.close()

@router.get("/{job_id}/preview")
async def get_preview(
    job_id: str,
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get the structured preview data for a document.
    """
    db = SessionLocal()
    try:
        doc = db.query(Document).filter_by(id=job_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
            
        # Security: Scoping
        if doc.user_id is not None:
            if not current_user or doc.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not authorized to preview this document")
        
        result = db.query(DocumentResult).filter_by(document_id=job_id).first()
        if not result:
            raise HTTPException(status_code=404, detail="Processing results not found")
        
        return {
            "structured_data": result.structured_data,
            "validation_results": result.validation_results,
            "metadata": {
                "filename": doc.filename,
                "template": doc.template,
                "status": doc.status,
                "created_at": doc.created_at
            }
        }
    finally:
        db.close()

@router.get("/{job_id}/compare")
async def get_comparison_data(
    job_id: str,
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get data for side-by-side comparison with HTML diff.
    """
    import difflib
    import json
    
    db = SessionLocal()
    try:
        doc = db.query(Document).filter_by(id=job_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
            
        # Security: Scoping
        if doc.user_id is not None:
            if not current_user or doc.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not authorized to access comparison data")
        
        # Status gating: Only allow when processing is complete
        if doc.status != "COMPLETED":
            print(f"Compare endpoint called too early for job {job_id}. Status: {doc.status}")
            raise HTTPException(
                status_code=400,
                detail=f"Comparison data not available. Job status: {doc.status}. Wait for COMPLETED status."
            )
        
        result = db.query(DocumentResult).filter_by(document_id=job_id).first()
        if not result:
            print(f"DocumentResult missing for completed job {job_id}")
            raise HTTPException(status_code=404, detail="Processing results not found")
        
        # Generate HTML diff
        original_text = doc.raw_text or ""
        
        # Flatten structured data to text for comparison
        formatted_text = ""
        if result.structured_data and isinstance(result.structured_data, dict):
            blocks = result.structured_data.get("blocks", [])
            formatted_text = "\n\n".join([
                block.get("text", "") for block in blocks if isinstance(block, dict) and block.get("text")
            ])
        
        # Generate HTML diff using difflib
        original_lines = original_text.splitlines(keepends=True)
        formatted_lines = formatted_text.splitlines(keepends=True)
        
        html_diff = difflib.HtmlDiff(wrapcolumn=80).make_file(
            original_lines,
            formatted_lines,
            fromdesc="Original Document",
            todesc="Formatted Document",
            context=True,
            numlines=3
        )
        
        return {
            "html_diff": html_diff,
            "original": {
                "raw_text": doc.raw_text,
                "structured_data": None
            },
            "formatted": {
                "structured_data": result.structured_data
            }
        }
    finally:
        db.close()

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
    
    db = SessionLocal()
    try:
        doc = db.query(Document).filter_by(id=job_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document job not found")
            
        # Security: Scoping
        if doc.user_id is not None:
            if not current_user or doc.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not authorized to download this document")
        
        # Status gating: Check completion first
        if doc.status != "COMPLETED":
            print(f"Download endpoint called too early for job {job_id}. Status: {doc.status}")
            raise HTTPException(
                status_code=400,
                detail=f"Document not ready. Job status: {doc.status}. Wait for COMPLETED status."
            )
        
        # Check output_path exists
        if not doc.output_path:
            print(f"Output path missing for completed job {job_id}")
            raise HTTPException(
                status_code=500,
                detail="Processing completed but output file path not set. Contact support."
            )
        
        # Verify file actually exists on disk
        if not os.path.exists(doc.output_path):
            print(f"Output file missing on disk for job {job_id}: {doc.output_path}")
            raise HTTPException(
                status_code=404,
                detail="Output file not found on server. File may have been deleted."
            )
             
        # Format handling
        path_to_serve = doc.output_path
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = f"{os.path.splitext(doc.filename)[0]}_formatted.docx"
        
        if format.lower() == "pdf":
            pdf_path = doc.output_path.replace(".docx", ".pdf")
            if not os.path.exists(pdf_path):
                try:
                    # Trigger PDF generation
                    exporter = PDFExporter()
                    generated_path = exporter.convert_to_pdf(doc.output_path, os.path.dirname(doc.output_path))
                    if not generated_path:
                        # Fallback for unexpected None return (should be covered by RuntimeError now)
                        raise HTTPException(status_code=500, detail="PDF conversion failed unexpectedly.")
                    pdf_path = generated_path
                except RuntimeError as re:
                    print(f"PDF Export Error for job {job_id}: {str(re)}")
                    raise HTTPException(
                        status_code=400, 
                        detail=f"PDF export unavailable: {str(re)}"
                    )
                except Exception as e:
                    print(f"Unexpected PDF Error for job {job_id}: {str(e)}")
                    raise HTTPException(status_code=500, detail="An internal error occurred during PDF export.")
            
            path_to_serve = pdf_path
            media_type = "application/pdf"
            filename = f"{os.path.splitext(doc.filename)[0]}_formatted.pdf"
        elif format.lower() != "docx":
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}. Use 'docx' or 'pdf'.")

        return FileResponse(
            path=path_to_serve,
            media_type=media_type,
            filename=filename
        )
    finally:
        db.close()
