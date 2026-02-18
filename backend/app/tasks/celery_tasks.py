import os
import logging
import time
from celery import Celery
from app.pipeline.orchestrator_v2 import create_orchestrator

# ── Old ORM imports (kept for reference, replaced by DocumentService) ──────────
# from app.db.session import SessionLocal
# from app.models import PipelineDocument

from app.services.document_service import DocumentService

logger = logging.getLogger(__name__)

# Configure Celery
celery_app = Celery(
    "manuscript_tasks",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
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
        # ── Mark as RUNNING ────────────────────────────────────────────────────
        DocumentService.update_document(document_id, {
            "status": "RUNNING",
            "progress": 10,
            "current_stage": "Initializing agent orchestration...",
        })

        # ── Run pipeline ───────────────────────────────────────────────────────
        orchestrator = create_orchestrator(use_agent=use_agent)
        start_time = time.time()
        orchestrator.process(doc_row)
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
