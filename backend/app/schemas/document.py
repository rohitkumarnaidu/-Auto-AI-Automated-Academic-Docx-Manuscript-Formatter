from pydantic import BaseModel, ConfigDict, Field
from typing import List, Literal, Optional
from datetime import datetime

ExportFormat = Literal["docx", "json", "markdown", "pdf", "jats", "xml"]

class DocumentBase(BaseModel):
    filename: str
    template: str
    status: str
    export_formats: List[ExportFormat] = Field(
        default_factory=lambda: ["docx", "json", "markdown"],
        description="Requested output formats for the document pipeline.",
    )

class Document(DocumentBase):
    id: str
    user_id: str
    output_path: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
