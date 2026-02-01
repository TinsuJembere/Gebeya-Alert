"""
Base schema classes for Pydantic models.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel as PydanticBaseModel, ConfigDict


class BaseSchema(PydanticBaseModel):
    """Base schema with common configuration."""
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
    )


class TimestampSchema(BaseSchema):
    """Schema with timestamp fields."""
    created_at: datetime
    updated_at: Optional[datetime] = None


class BaseResponseSchema(BaseSchema):
    """Base response schema with common fields."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
















