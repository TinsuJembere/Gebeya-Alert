"""
Celery configuration for background tasks.
"""
from celery import Celery
from celery.schedules import crontab
import os

from config import settings

# Create Celery app
celery_app = Celery(
    "gebeyaalert",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Schedule periodic tasks
celery_app.conf.beat_schedule = {
    "check-price-alerts-daily": {
        "task": "tasks.check_price_alerts",
        "schedule": crontab(hour=9, minute=0),  # Run daily at 9:00 AM UTC
    },
}

# Import tasks
from tasks import check_price_alerts  # noqa: F401, E402
















