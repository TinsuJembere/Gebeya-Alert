"""
NotificationLog model for GebeyaAlert.
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, ForeignKey, Column, String, Text
from sqlalchemy import Index

from .base import BaseModel

if TYPE_CHECKING:
    from .user import User


class NotificationLog(BaseModel, table=True):
    """NotificationLog model for tracking sent notifications."""
    
    __tablename__ = "notification_logs"
    
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    message: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Notification message content"
    )
    sent_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="Timestamp when the notification was sent"
    )
    
    # Relationships
    user: "User" = Relationship(back_populates="notification_logs")
    
    # Indexes
    __table_args__ = (
        Index("idx_notification_log_user_id", "user_id"),
        Index("idx_notification_log_sent_at", "sent_at"),
        Index("idx_notification_log_user_sent_at", "user_id", "sent_at"),
    )
















