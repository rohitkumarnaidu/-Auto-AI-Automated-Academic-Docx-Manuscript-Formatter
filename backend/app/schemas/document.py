
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class DocumentBase(BaseModel):
    filename: str
    template: str
    status: str

class Document(DocumentBase):
    id: str
    user_id: str
    output_path: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
