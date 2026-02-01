"""
Base model class for all database models.
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class TimestampMixin(SQLModel):
    """Mixin class for timestamp fields."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


class BaseModel(SQLModel):
    """Base model class with common fields."""
    id: Optional[int] = Field(default=None, primary_key=True)
















