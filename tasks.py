"""
Celery tasks for background processing.
"""
import logging
from sqlmodel import Session

from celery_app import celery_app
from database import engine
from services.alert_checker_service import AlertCheckerService

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.check_price_alerts")
def check_price_alerts():
    """
    Celery task to check all price alerts and send notifications.
    Runs daily via celery-beat scheduler.
    """
    logger.info("Starting price alert check task...")
    
    try:
        with Session(engine) as db:
            stats = AlertCheckerService.check_all_alerts(db)
            logger.info(f"Price alert check completed: {stats}")
            return stats
    except Exception as e:
        logger.error(f"Error in check_price_alerts task: {str(e)}", exc_info=True)
        raise
















