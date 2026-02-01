"""
Crop model for GebeyaAlert.
"""
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column, String
from sqlalchemy import Index

from .base import BaseModel

if TYPE_CHECKING:
    from .price import Price
    from .alert import Alert


class Crop(BaseModel, table=True):
    """Crop model representing agricultural crops."""
    
    __tablename__ = "crops"
    
    name: str = Field(
        sa_column=Column(String(100), unique=True, nullable=False, index=True),
        description="Name of the crop"
    )
    crop_type: str = Field(
        default="Grain",
        sa_column=Column(String(50), nullable=False),
        description="Type of crop (e.g., Grain, Vegetable, Fruit, Legume)"
    )
    
    # Relationships
    prices: List["Price"] = Relationship(back_populates="crop")
    alerts: List["Alert"] = Relationship(back_populates="crop")
    
    # Indexes
    __table_args__ = (
        Index("idx_crop_name", "name"),
    )
















