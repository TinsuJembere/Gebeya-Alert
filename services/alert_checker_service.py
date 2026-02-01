"""
Service for checking price alerts and sending notifications.
"""
import logging
from datetime import datetime, date
from sqlmodel import Session, select
from typing import List, Optional
from decimal import Decimal

from models.alert import Alert
from models.price import Price
from models.notification_log import NotificationLog
from models.crop import Crop
from models.market import Market
from models.user import User
from services.sms_service import sms_service

logger = logging.getLogger(__name__)


class AlertCheckerService:
    """Service for checking and processing price alerts."""
    
    @staticmethod
    def get_latest_price(
        db: Session,
        crop_id: int,
        market_id: int
    ) -> Optional[Price]:
        """
        Get the latest price for a crop at a market.
        
        Args:
            db: Database session
            crop_id: Crop ID
            market_id: Market ID
            
        Returns:
            Latest Price object or None if no price found
        """
        statement = (
            select(Price)
            .where(
                Price.crop_id == crop_id,
                Price.market_id == market_id
            )
            .order_by(Price.price_date.desc())
            .limit(1)
        )
        
        return db.exec(statement).first()
    
    @staticmethod
    def should_send_alert(alert: Alert, latest_price: Price) -> bool:
        """
        Check if alert should be sent based on price and last_sent_at.
        
        Args:
            alert: Alert object
            latest_price: Latest price for the alert's crop/market
            
        Returns:
            True if alert should be sent, False otherwise
        """
        # Check if price meets or exceeds target
        if latest_price.price < alert.target_price:
            return False
        
        # Check if alert was already sent today
        if alert.last_sent_at:
            last_sent_date = alert.last_sent_at.date()
            today = date.today()
            if last_sent_date == today:
                return False
        
        return True
    
    @staticmethod
    def send_alert_notification(
        db: Session,
        alert: Alert,
        latest_price: Price
    ) -> bool:
        """
        Send SMS notification for an alert and update records.
        
        Args:
            db: Database session
            alert: Alert object
            latest_price: Latest price that triggered the alert
            
        Returns:
            True if notification sent successfully, False otherwise
        """
        try:
            # Get related objects for message
            crop = db.get(Crop, alert.crop_id)
            market = db.get(Market, alert.market_id)
            user = db.get(User, alert.user_id)
            
            if not crop or not market or not user:
                logger.error(
                    f"Missing related objects for alert {alert.id}: "
                    f"crop={crop is not None}, market={market is not None}, user={user is not None}"
                )
                return False
            
            # Send SMS
            success, error = sms_service.send_price_alert(
                to_phone=user.phone_number,
                crop_name=crop.name,
                market_name=market.name,
                current_price=float(latest_price.price),
                target_price=float(alert.target_price)
            )
            
            if not success:
                logger.error(
                    f"Failed to send SMS for alert {alert.id}: {error}"
                )
                return False
            
            # Update alert's last_sent_at
            alert.last_sent_at = datetime.utcnow()
            db.add(alert)
            
            # Log notification
            notification_log = NotificationLog(
                user_id=user.id,
                message=(
                    f"Price Alert: {crop.name} at {market.name} "
                    f"is now {latest_price.price:.2f} ETB. "
                    f"Your target: {alert.target_price:.2f} ETB"
                )
            )
            db.add(notification_log)
            
            db.commit()
            
            logger.info(
                f"Alert {alert.id} processed successfully. "
                f"SMS sent to {user.phone_number}"
            )
            
            return True
            
        except Exception as e:
            logger.error(
                f"Error processing alert {alert.id}: {str(e)}",
                exc_info=True
            )
            db.rollback()
            return False
    
    @staticmethod
    def check_all_alerts(db: Session) -> dict:
        """
        Check all active alerts and send notifications where appropriate.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with processing statistics
        """
        stats = {
            "total_alerts": 0,
            "checked": 0,
            "sent": 0,
            "skipped": 0,
            "errors": 0
        }
        
        try:
            # Get all active alerts
            statement = select(Alert)
            alerts = list(db.exec(statement).all())
            stats["total_alerts"] = len(alerts)
            
            logger.info(f"Checking {len(alerts)} alerts...")
            
            for alert in alerts:
                try:
                    stats["checked"] += 1
                    
                    # Get latest price
                    latest_price = AlertCheckerService.get_latest_price(
                        db,
                        alert.crop_id,
                        alert.market_id
                    )
                    
                    if not latest_price:
                        logger.debug(
                            f"Alert {alert.id}: No price data found for "
                            f"crop {alert.crop_id} at market {alert.market_id}"
                        )
                        stats["skipped"] += 1
                        continue
                    
                    # Check if alert should be sent
                    if not AlertCheckerService.should_send_alert(alert, latest_price):
                        logger.debug(
                            f"Alert {alert.id}: Conditions not met "
                            f"(price: {latest_price.price}, target: {alert.target_price}, "
                            f"last_sent: {alert.last_sent_at})"
                        )
                        stats["skipped"] += 1
                        continue
                    
                    # Send notification
                    if AlertCheckerService.send_alert_notification(
                        db,
                        alert,
                        latest_price
                    ):
                        stats["sent"] += 1
                    else:
                        stats["errors"] += 1
                        
                except Exception as e:
                    logger.error(
                        f"Error processing alert {alert.id}: {str(e)}",
                        exc_info=True
                    )
                    stats["errors"] += 1
            
            logger.info(
                f"Alert check completed: {stats['sent']} sent, "
                f"{stats['skipped']} skipped, {stats['errors']} errors"
            )
            
        except Exception as e:
            logger.error(f"Error in check_all_alerts: {str(e)}", exc_info=True)
            stats["errors"] += 1
        
        return stats

