"""
Background Task Utilities with Timeout Support
Prevents infinite loops and resource exhaustion in background tasks.
"""

import asyncio
import logging
from typing import Callable, Any
from functools import wraps
from app.db.session import SessionLocal
from app.models import Document

logger = logging.getLogger(__name__)

def with_timeout(timeout_seconds: int = 300):
    """
    Decorator to add timeout to background tasks.
    
    Args:
        timeout_seconds: Maximum execution time (default: 5 minutes)
    
    Usage:
        @with_timeout(timeout_seconds=300)
        def my_background_task(arg1, arg2):
            # Task code here
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=timeout_seconds
                )
            except asyncio.TimeoutError:
                logger.error(f"Task {func.__name__} timed out after {timeout_seconds} seconds")
                # Extract job_id if available
                job_id = kwargs.get('job_id') or (args[1] if len(args) > 1 else None)
                if job_id:
                    _mark_job_as_failed(job_id, f"Processing timeout ({timeout_seconds}s exceeded)")
                raise
            except Exception as e:
                logger.error(f"Task {func.__name__} failed: {e}", exc_info=True)
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For synchronous functions, run in executor with timeout
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            async def run_with_timeout():
                try:
                    return await asyncio.wait_for(
                        loop.run_in_executor(None, func, *args, **kwargs),
                        timeout=timeout_seconds
                    )
                except asyncio.TimeoutError:
                    logger.error(f"Task {func.__name__} timed out after {timeout_seconds} seconds")
                    # Extract job_id if available
                    job_id = kwargs.get('job_id') or (args[1] if len(args) > 1 else None)
                    if job_id:
                        _mark_job_as_failed(job_id, f"Processing timeout ({timeout_seconds}s exceeded)")
                    raise
            
            return loop.run_until_complete(run_with_timeout())
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def _mark_job_as_failed(job_id: str, error_message: str):
    """
    Mark a job as failed in the database.
    
    Args:
        job_id: Job ID to mark as failed
        error_message: Error message to store
    """
    try:
        with SessionLocal() as db:
            doc = db.query(Document).filter_by(id=job_id).first()
            if doc:
                doc.status = "FAILED"
                doc.error_message = error_message
                doc.progress = 0
                db.commit()
                logger.info(f"Marked job {job_id} as FAILED: {error_message}")
    except Exception as e:
        logger.error(f"Failed to mark job {job_id} as failed: {e}", exc_info=True)

async def run_pipeline_with_timeout(orchestrator, input_path: str, job_id: str, template_name: str):
    """
    Run pipeline with timeout protection.
    
    Args:
        orchestrator: PipelineOrchestrator instance
        input_path: Path to input file
        job_id: Job ID
        template_name: Template name
    """
    try:
        await asyncio.wait_for(
            asyncio.to_thread(
                orchestrator.run_pipeline,
                input_path=input_path,
                job_id=job_id,
                template_name=template_name
            ),
            timeout=300.0  # 5 minutes max
        )
        logger.info(f"Pipeline completed successfully for job {job_id}")
    except asyncio.TimeoutError:
        logger.error(f"Pipeline timeout for job {job_id}")
        _mark_job_as_failed(job_id, "Processing timeout (5 minutes exceeded)")
    except Exception as e:
        logger.error(f"Pipeline failed for job {job_id}: {e}", exc_info=True)
        _mark_job_as_failed(job_id, f"Processing failed: {str(e)}")
