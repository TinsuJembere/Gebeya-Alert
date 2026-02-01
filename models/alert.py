"""
Alert model for GebeyaAlert.
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, ForeignKey, Column, Numeric
from sqlalchemy import Index

from .base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from .user import User
    from .crop import Crop
    from .market import Market


class Alert(BaseModel, TimestampMixin, table=True):
    """Alert model representing user price alerts."""
    
    __tablename__ = "alerts"
    
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    crop_id: int = Field(foreign_key="crops.id", nullable=False, index=True)
    market_id: int = Field(foreign_key="markets.id", nullable=False, index=True)
    target_price: float = Field(
        sa_column=Column(Numeric(10, 2), nullable=False),
        description="Target price threshold for the alert"
    )
    last_sent_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the alert was last sent"
    )
    
    # Relationships
    user: "User" = Relationship(back_populates="alerts")
    crop: "Crop" = Relationship(back_populates="alerts")
    market: "Market" = Relationship(back_populates="alerts")
    
    # Indexes
    __table_args__ = (
        Index("idx_alert_user_id", "user_id"),
        Index("idx_alert_crop_id", "crop_id"),
        Index("idx_alert_market_id", "market_id"),
        Index("idx_alert_user_crop_market", "user_id", "crop_id", "market_id"),
    )
















