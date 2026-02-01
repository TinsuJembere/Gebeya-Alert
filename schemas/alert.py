"""
Alert schemas.
"""
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


class AlertCreate(BaseModel):
    """Schema for creating an alert."""
    crop_id: int = Field(..., description="ID of the crop to monitor")
    market_id: int = Field(..., description="ID of the market to monitor")
    target_price: Decimal = Field(..., gt=0, description="Target price in ETB (alert triggers when price reaches this)")


class AlertResponse(BaseModel):
    """Schema for alert response."""
    id: int
    user_id: int
    crop_id: int
    market_id: int
    target_price: Decimal
    last_sent_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AlertResponseWithDetails(BaseModel):
    """Schema for alert response with crop and market details."""
    id: int
    user_id: int
    crop_id: int
    market_id: int
    target_price: Decimal
    last_sent_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    crop_name: Optional[str] = None
    market_name: Optional[str] = None
    market_region: Optional[str] = None
    
    class Config:
        from_attributes = True
















