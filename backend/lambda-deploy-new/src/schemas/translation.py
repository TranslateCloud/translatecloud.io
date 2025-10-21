from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime

class TranslationBase(BaseModel):
    source_text: str
    source_lang: str
    target_lang: str

class TranslationCreate(TranslationBase):
    project_id: UUID4

class TranslationResponse(TranslationBase):
    id: UUID4
    project_id: UUID4
    translated_text: Optional[str] = None
    word_count: Optional[int] = None
    engine: str
    status: str
    created_at: datetime
    translated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True