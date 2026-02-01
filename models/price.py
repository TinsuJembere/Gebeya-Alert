"""
Price model for GebeyaAlert.
"""
from datetime import date
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, ForeignKey, Column, Date, Numeric, String
from sqlalchemy import Index

from .base import BaseModel

if TYPE_CHECKING:
    from .crop import Crop
    from .market import Market


class Price(BaseModel, table=True):
    """Price model representing crop prices at markets."""
    
    __tablename__ = "prices"
    
    crop_id: int = Field(foreign_key="crops.id", nullable=False, index=True)
    market_id: int = Field(foreign_key="markets.id", nullable=False, index=True)
    price: float = Field(
        sa_column=Column(Numeric(10, 2), nullable=False),
        description="Price of the crop at the market"
    )
    price_date: date = Field(
        sa_column=Column(name="date", type_=Date, nullable=False, index=True),
        description="Date of the price record"
    )
    source: Optional[str] = Field(
        default="manual",
        sa_column=Column(String(50), nullable=True),
        description="Source of the price data (e.g., 'manual', 'api', 'sms', 'market_officer')"
    )
    confidence_score: Optional[float] = Field(
        default=1.0,
        sa_column=Column(Numeric(3, 2), nullable=True),
        description="Confidence score from 0.0 to 1.0 indicating data reliability"
    )
    
    # Relationships
    crop: "Crop" = Relationship(back_populates="prices")
    market: "Market" = Relationship(back_populates="prices")
    
    # Indexes
    __table_args__ = (
        Index("idx_price_crop_id", "crop_id"),
        Index("idx_price_market_id", "market_id"),
        Index("idx_price_date", "date"),
        Index("idx_price_crop_market_date", "crop_id", "market_id", "date"),
    )





