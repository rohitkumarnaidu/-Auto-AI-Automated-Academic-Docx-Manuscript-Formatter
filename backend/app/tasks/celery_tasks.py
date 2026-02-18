import os
import logging
from celery import Celery
from app.pipeline.orchestrator_v2 import create_orchestrator
from app.db.session import SessionLocal
from app.models import PipelineDocument
import time

logger = logging.getLogger(__name__)

# Configure Celery
celery_app = Celery(
    "manuscript_tasks",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
)

@celery_app.task(name="process_document_async")
def process_document_task(document_id: str, use_agent: bool = True):
    """
    Asynchronously process a document using the Agent Orchestrator.
    """
    logger.info("Starting async processing for document: %s", document_id)

    # Guard: SessionLocal may be None if DB is unconfigured
    try:
        db = SessionLocal()
        if db is None:
            logger.error("process_document_task: Database session unavailable (DB not configured).")
            return False
    except Exception as exc:
        logger.error("process_document_task: Failed to create DB session: %s", exc)
        return False

    doc = None
    try:
        # Retrieve document from DB
        doc = db.query(PipelineDocument).filter(
            PipelineDocument.document_id == document_id
        ).first()
        if not doc:
            logger.error("process_document_task: Document %s not found in database.", document_id)
            return False

        # Update status to RUNNING
        doc.status = "RUNNING"
        doc.progress_percentage = 10
        doc.message = "Initializing agent orchestration..."
        db.commit()

        # Initialize Orchestrator
        orchestrator = create_orchestrator(use_agent=use_agent)

        # Start processing
        start_time = time.time()
        orchestrator.process(doc)
        processing_time = time.time() - start_time

        # Update completion status
        doc.status = "COMPLETED"
        doc.progress_percentage = 100
        doc.message = f"Processing complete in {processing_time:.1f}s"
        db.commit()

        logger.info("Document %s processed successfully in %.1fs", document_id, processing_time)
        return True

    except Exception as exc:
        logger.error("Async processing failed for %s: %s", document_id, exc, exc_info=True)
        try:
            db.rollback()
            if doc is not None:
                doc.status = "FAILED"
                if hasattr(doc, "error_message"):
                    doc.error_message = str(exc)
                db.commit()
        except Exception as commit_exc:
            logger.error("process_document_task: Failed to update FAILED status: %s", commit_exc)
        return False
    finally:
        try:
            db.close()
        except Exception:
            pass
