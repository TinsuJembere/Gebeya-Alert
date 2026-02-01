"""
Market schemas.
"""
from pydantic import BaseModel, Field


class MarketCreate(BaseModel):
    """Schema for creating a market."""
    name: str = Field(..., min_length=1, max_length=100, description="Name of the market")
    region: str = Field(..., min_length=1, max_length=100, description="Region where the market is located")


class MarketResponse(BaseModel):
    """Schema for market response."""
    id: int
    name: str
    region: str
    
    class Config:
        from_attributes = True
















