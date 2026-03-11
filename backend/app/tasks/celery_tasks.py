# RESERVED: Celery task definitions for future distributed processing.
# Not currently wired into the FastAPI runtime — kept for planned Redis/Celery migration.
import logging
import time
import asyncio
from celery import Celery
from app.pipeline.orchestrator import PipelineOrchestrator
from app.config.settings import settings

# ── Old ORM imports (kept for reference, replaced by DocumentService) ──────────
# from app.db.session import SessionLocal
# from app.models import PipelineDocument

from app.services.document_service import DocumentService

logger = logging.getLogger(__name__)

# Configure Celery
celery_app = Celery(
    "manuscript_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)


@celery_app.task(name="process_document_async")
def process_document_task(document_id: str, use_agent: bool = True):
    """
    Asynchronously process a document using the Agent Orchestrator.

    Uses DocumentService (supabase-py) for all DB reads and writes.
    Old ORM equivalent used SessionLocal() + db.query(PipelineDocument).
    """
    logger.info("Starting async processing for document: %s", document_id)

    # ── Fetch document via supabase-py ─────────────────────────────────────────
    doc_row = DocumentService.get_document(document_id)
    if doc_row is None:
        logger.error(
            "process_document_task: Document %s not found or DB unavailable.", document_id
        )
        return False

    try:
        # ── Mark as PROCESSING ────────────────────────────────────────────────────
        DocumentService.update_document(document_id, {
            "status": "PROCESSING",
            "progress": 10,
            "current_stage": "Initializing agent orchestration...",
        })

        # ── Run pipeline ───────────────────────────────────────────────────────
        orchestrator = PipelineOrchestrator()
        start_time = time.time()
        orchestrator.run_pipeline(input_path=doc_row["original_file_path"], job_id=document_id)
        processing_time = time.time() - start_time

        # ── Mark as COMPLETED ──────────────────────────────────────────────────
        DocumentService.update_document(document_id, {
            "status": "COMPLETED",
            "progress": 100,
            "current_stage": f"Processing complete in {processing_time:.1f}s",
        })

        logger.info("Document %s processed successfully in %.1fs", document_id, processing_time)
        return True

    except Exception as exc:
        logger.error("Async processing failed for %s: %s", document_id, exc, exc_info=True)
        # Mark as FAILED — never raises
        DocumentService.mark_document_failed(document_id, str(exc))
        return False


@celery_app.task(name="process_generation_async")
def process_generation_task(job_id: str):
    """
    Run generate-from-scratch jobs through Celery when enabled.
    """
    logger.info("Starting async generation for job: %s", job_id)
    try:
        from app.pipeline.generation.document_generator import get_generator

        generator = get_generator()
        asyncio.run(generator.run_pipeline(str(job_id)))
        logger.info("Generation job %s completed successfully via Celery", job_id)
        return True
    except Exception as exc:
        logger.error("Generation task failed for %s: %s", job_id, exc, exc_info=True)
        DocumentService.mark_document_failed(str(job_id), str(exc))
        return False


@celery_app.task(name="process_edit_document_async")
def process_edit_document_task(job_id: str, edited_structured_data: dict, template_name: str = "IEEE"):
    """
    Run edit/reformat flow through Celery when enabled.
    """
    logger.info("Starting async edit flow for job: %s", job_id)
    try:
        orchestrator = PipelineOrchestrator()
        result = orchestrator.run_edit_flow(
            job_id=str(job_id),
            edited_structured_data=edited_structured_data or {},
            template_name=template_name or "IEEE",
        )
        ok = isinstance(result, dict) and result.get("status") == "success"
        if ok:
            logger.info("Edit job %s completed successfully via Celery", job_id)
        else:
            logger.warning("Edit job %s finished with non-success result: %s", job_id, result)
        return ok
    except Exception as exc:
        logger.error("Edit task failed for %s: %s", job_id, exc, exc_info=True)
        DocumentService.mark_document_failed(str(job_id), f"Edit flow failed: {exc}")
        return False
