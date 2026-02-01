# schemas/user.py
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator

class UserBase(BaseModel):
    phone_number: str
    language: str = "en"
    is_admin: bool = False

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    phone_number: Optional[str] = None
    language: Optional[str] = None
    is_admin: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8)

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True