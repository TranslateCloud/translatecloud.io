from pydantic import BaseModel, EmailStr, UUID4
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    company: Optional[str] = None

class UserCreate(UserBase):
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    cognito_sub: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    company: Optional[str] = None

class UserResponse(UserBase):
    id: UUID4
    cognito_sub: str
    plan: str
    subscription_status: str
    monthly_word_count: int
    word_limit: int
    created_at: datetime
    
    class Config:
        from_attributes = True