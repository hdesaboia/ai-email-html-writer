from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# Shared properties
class EmailTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    html_content: str = Field(..., min_length=1)
    is_public: bool = Field(default=False)
    figma_url: Optional[str] = None
    figma_file_key: Optional[str] = None
    figma_node_id: Optional[str] = None


# Properties to receive on template creation
class EmailTemplateCreate(EmailTemplateBase):
    pass


# Properties to receive on template update
class EmailTemplateUpdate(EmailTemplateBase):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    html_content: Optional[str] = Field(None, min_length=1)


# Properties shared by models stored in DB
class EmailTemplateInDBBase(EmailTemplateBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Properties to return to client
class EmailTemplate(EmailTemplateInDBBase):
    pass


# Properties stored in DB
class EmailTemplateInDB(EmailTemplateInDBBase):
    pass 