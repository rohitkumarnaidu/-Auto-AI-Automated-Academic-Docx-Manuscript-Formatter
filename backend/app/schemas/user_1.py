
from pydantic import BaseModel, ConfigDict
from typing import Optional

class UserBase(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    institution: Optional[str] = None
    role: str = "authenticated"

class User(UserBase):
    id: str

    model_config = ConfigDict(from_attributes=True)
