"""
Market model for GebeyaAlert.
"""
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column, String
from sqlalchemy import Index

from .base import BaseModel

if TYPE_CHECKING:
    from .price import Price
    from .alert import Alert


class Market(BaseModel, table=True):
    """Market model representing market locations."""
    
    __tablename__ = "markets"
    
    name: str = Field(
        sa_column=Column(String(100), nullable=False, index=True),
        description="Name of the market"
    )
    region: str = Field(
        sa_column=Column(String(100), nullable=False, index=True),
        description="Region where the market is located"
    )
    
    # Relationships
    prices: List["Price"] = Relationship(back_populates="market")
    alerts: List["Alert"] = Relationship(back_populates="market")
    
    # Indexes
    __table_args__ = (
        Index("idx_market_name", "name"),
        Index("idx_market_region", "region"),
        Index("idx_market_name_region", "name", "region"),
    )
















