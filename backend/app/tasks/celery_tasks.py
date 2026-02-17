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
    logger.info(f"Starting async processing for document: {document_id}")
    db = SessionLocal()
    try:
        # Retrieve document from DB
        doc = db.query(PipelineDocument).filter(PipelineDocument.document_id == document_id).first()
        if not doc:
            logger.error(f"Document {document_id} not found in database.")
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
        processed_doc = orchestrator.process(doc)
        processing_time = time.time() - start_time
        
        # Update completion status
        doc.status = "COMPLETED"
        doc.progress_percentage = 100
        doc.message = f"Processing complete in {processing_time:.1f}s"
        db.commit()
        
        logger.info(f"Document {document_id} processed successfully in {processing_time:.1f}s")
        return True

    except Exception as e:
        logger.error(f"Async processing failed for {document_id}: {e}", exc_info=True)
        # Update document status to FAILED
        if 'doc' in locals() and doc:
            doc.status = "FAILED"
            doc.error_message = str(e)
            db.commit()
        return False
    finally:
        db.close()
