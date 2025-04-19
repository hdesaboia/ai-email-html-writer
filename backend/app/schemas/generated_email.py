from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


# Shared properties
class GeneratedEmailBase(BaseModel):
    html_content: str = Field(..., min_length=1)
    template_id: int
    data: Dict[str, Any]


# Properties to receive on email generation
class GeneratedEmailCreate(GeneratedEmailBase):
    pass


# Properties shared by models stored in DB
class GeneratedEmailInDBBase(GeneratedEmailBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        orm_mode = True


# Properties to return to client
class GeneratedEmail(GeneratedEmailInDBBase):
    pass


# Properties stored in DB
class GeneratedEmailInDB(GeneratedEmailInDBBase):
    pass 