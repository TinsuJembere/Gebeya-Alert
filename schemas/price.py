"""
Price schemas.
"""
from datetime import date
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


class PriceCreate(BaseModel):
    """Schema for creating a price."""
    crop_id: int = Field(..., description="ID of the crop")
    market_id: int = Field(..., description="ID of the market")
    price: Decimal = Field(..., gt=0, description="Price in ETB (Ethiopian Birr)")
    price_date: date = Field(..., description="Date of the price record")
    source: Optional[str] = Field(default="manual", description="Source of the price data")
    confidence_score: Optional[float] = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")


class PriceResponse(BaseModel):
    """Schema for price response."""
    id: int
    crop_id: int
    market_id: int
    price: Decimal
    price_date: date
    source: Optional[str] = None
    confidence_score: Optional[float] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class PriceResponseWithDetails(BaseModel):
    """Schema for price response with crop and market details."""
    id: int
    crop_id: int
    market_id: int
    price: Decimal
    price_date: date
    source: Optional[str] = None
    confidence_score: Optional[float] = None
    crop_name: Optional[str] = None
    market_name: Optional[str] = None
    market_region: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class PricePrediction(BaseModel):
    """Schema for price prediction response."""
    crop_id: int
    market_id: int
    predicted_price: float
    predicted_date: date
    confidence: float = Field(ge=0.0, le=1.0, description="Prediction confidence (0.0-1.0)")
    trend: str = Field(..., description="Price trend: 'rising', 'falling', or 'stable'")
    trend_percentage: float = Field(..., description="Percentage change in trend")
    recommendation: str = Field(..., description="Human-readable recommendation")


class BestTimeToSell(BaseModel):
    """Schema for best time to sell recommendation."""
    crop_id: int
    market_id: int
    crop_name: str
    market_name: str
    current_price: float
    recommended_price: float
    recommendation: str = Field(..., description="Human-readable advice")
    confidence: float = Field(ge=0.0, le=1.0, description="Recommendation confidence")
    reasoning: Optional[str] = None





