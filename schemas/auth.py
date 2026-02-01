"""
Authentication schemas.
"""
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from utils.phone import normalize_phone_number


class RegisterRequest(BaseModel):
    """Request schema for user registration."""
    phone_number: str = Field(..., description="Phone number in any format")
    password: str = Field(..., min_length=1, description="User password")
    language: str = Field(default="en", description="User's preferred language")
    
    @field_validator('phone_number')
    @classmethod
    def normalize_phone(cls, v: str) -> str:
        """Normalize phone number to +251 format."""
        return normalize_phone_number(v)
    
    @field_validator('language')
    @classmethod
    def validate_language(cls, v: str) -> str:
        """Validate language code."""
        if len(v) > 10:
            raise ValueError("Language code must be 10 characters or less")
        return v


class LoginRequest(BaseModel):
    """Request schema for user login."""
    phone_number: str = Field(..., description="Phone number in any format")
    otp: str = Optional
    @field_validator('phone_number')
    @classmethod
    def normalize_phone(cls, v: str) -> str:
        """Normalize phone number to +251 format."""
        return normalize_phone_number(v)


class TokenResponse(BaseModel):
    """Response schema for authentication tokens."""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Response schema for user information."""
    id: int
    phone_number: str
    language: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    phone_number: Optional[str] = None



