from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Any, Optional
from app.pipeline.agents.memory import AgentMemory

router = APIRouter(
    prefix="/feedback",
    tags=["feedback"],
    responses={404: {"description": "Not found"}},
)

# Instantiate memory (singleton-ish)
# In a real app, this might be a dependency injection
memory = AgentMemory()

class FeedbackRequest(BaseModel):
    document_id: str
    field: str
    original_value: Any
    corrected_value: Any
    comments: Optional[str] = None

@router.post("/", status_code=201)
async def submit_feedback(feedback: FeedbackRequest):
    """
    Submit user feedback/corrections for a document.
    This data is used to improve future processing models.
    """
    try:
        memory.remember_correction(
            document_id=feedback.document_id,
            field=feedback.field,
            original_value=feedback.original_value,
            corrected_value=feedback.corrected_value
        )
        return {"status": "success", "message": "Feedback recorded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary")
async def get_feedback_summary():
    """Get a summary of collected feedback."""
    try:
        summary = memory.get_memory_summary()
        return summary.get("corrections", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
