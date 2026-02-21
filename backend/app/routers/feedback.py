from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Any, Optional
from app.pipeline.agents.memory import AgentMemory
from app.utils.dependencies import get_current_user
from app.db.supabase_client import get_supabase_client
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/feedback",
    tags=["feedback"],
    responses={404: {"description": "Not found"}},
)

# Instantiate memory (singleton-ish)
memory = AgentMemory()

class FeedbackRequest(BaseModel):
    document_id: str
    field: str
    original_value: Any
    corrected_value: Any
    comments: Optional[str] = None

@router.post("/", status_code=201)
async def submit_feedback(
    feedback: FeedbackRequest,
    current_user=Depends(get_current_user)
):
    """
    Submit user feedback/corrections for a document.
    This data is used to improve future processing models.
    Requires authentication.
    """
    try:
        # Store in-memory for fast access
        memory.remember_correction(
            document_id=feedback.document_id,
            field=feedback.field,
            original_value=feedback.original_value,
            corrected_value=feedback.corrected_value
        )

        # Also persist to Supabase for durability
        try:
            sb = get_supabase_client()
            if sb:
                sb.table("feedback").insert({
                    "document_id": feedback.document_id,
                    "user_id": str(current_user.id),
                    "field": feedback.field,
                    "original_value": str(feedback.original_value),
                    "corrected_value": str(feedback.corrected_value),
                    "comments": feedback.comments,
                }).execute()
        except Exception as db_err:
            # Don't fail the request if DB persistence fails — in-memory is enough
            logger.warning("Failed to persist feedback to Supabase: %s", db_err)

        return {"status": "success", "message": "Feedback recorded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary")
async def get_feedback_summary(current_user=Depends(get_current_user)):
    """Get a summary of collected feedback. Requires authentication."""
    try:
        summary = memory.get_memory_summary()
        return summary.get("corrections", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
