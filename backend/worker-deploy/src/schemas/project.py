from pydantic import BaseModel, UUID4, HttpUrl
from typing import Optional
from datetime import datetime

class ProjectBase(BaseModel):
    name: str
    url: Optional[HttpUrl] = None
    source_lang: str
    target_lang: str

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[HttpUrl] = None
    status: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: UUID4
    user_id: UUID4
    status: str
    total_words: int
    translated_words: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True