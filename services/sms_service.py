"""
SMS service for sending notifications via Twilio.
"""
import logging
from typing import Optional, Tuple
from twilio.rest import Client
from twilio.base.exceptions import TwilioException, TwilioRestException

from config import settings

logger = logging.getLogger(__name__)


class SMSService:
    """Service for sending SMS messages via Twilio."""
    
    def __init__(self):
        """Initialize Twilio client if credentials are configured."""
        self.client: Optional[Client] = None
        self.enabled = False
        
        if settings.SMS_ENABLED and all([
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN,
            settings.TWILIO_PHONE_NUMBER
        ]):
            try:
                self.client = Client(
                    settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN
                )
                self.enabled = True
                logger.info("Twilio SMS service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
                self.enabled = False
        else:
            logger.warning(
                "SMS service disabled: Missing Twilio credentials or SMS_ENABLED=False"
            )
    
    def format_message(self, message: str, max_length: int = 160) -> str:
        """
        Format message to be SMS-friendly (short and concise).
        
        Args:
            message: Original message
            max_length: Maximum message length (default 160 for single SMS)
            
        Returns:
            Formatted message (truncated if necessary)
        """
        # Remove extra whitespace and newlines
        formatted = " ".join(message.split())
        
        # Truncate if too long
        if len(formatted) > max_length:
            formatted = formatted[:max_length - 3] + "..."
        
        return formatted
    
    def send_sms(
        self,
        to_phone: str,
        message: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Send SMS message via Twilio.
        
        Args:
            to_phone: Recipient phone number (E.164 format, e.g., +251911234567)
            message: Message content (will be formatted for SMS)
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        if not self.enabled or not self.client:
            error_msg = "SMS service is not enabled or not configured"
            logger.warning(error_msg)
            return False, error_msg
        
        if not to_phone:
            error_msg = "Recipient phone number is required"
            logger.error(error_msg)
            return False, error_msg
        
        if not message:
            error_msg = "Message content is required"
            logger.error(error_msg)
            return False, error_msg
        
        # Format message for SMS (short and concise)
        formatted_message = self.format_message(message)
        
        try:
            # Send SMS via Twilio
            twilio_message = self.client.messages.create(
                body=formatted_message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=to_phone
            )
            
            logger.info(
                f"SMS sent successfully to {to_phone}. "
                f"Twilio SID: {twilio_message.sid}"
            )
            return True, None
            
        except TwilioRestException as e:
            error_msg = f"Twilio API error: {e.msg}"
            logger.error(f"Failed to send SMS to {to_phone}: {error_msg}")
            return False, error_msg
            
        except TwilioException as e:
            error_msg = f"Twilio error: {str(e)}"
            logger.error(f"Failed to send SMS to {to_phone}: {error_msg}")
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error sending SMS: {str(e)}"
            logger.error(f"Failed to send SMS to {to_phone}: {error_msg}")
            return False, error_msg
    
    def send_price_alert(
        self,
        to_phone: str,
        crop_name: str,
        market_name: str,
        current_price: float,
        target_price: float
    ) -> Tuple[bool, Optional[str]]:
        """
        Send price alert SMS in English with short format.
        
        Args:
            to_phone: Recipient phone number
            crop_name: Name of the crop
            market_name: Name of the market
            current_price: Current price in ETB
            target_price: Target price in ETB
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        # Create short, concise message in English
        message = (
            f"Price Alert: {crop_name} at {market_name} "
            f"is now {current_price:.2f} ETB. "
            f"Your target: {target_price:.2f} ETB"
        )
        
        return self.send_sms(to_phone, message)
    
    def send_generic_notification(
        self,
        to_phone: str,
        message: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Send generic notification SMS.
        
        Args:
            to_phone: Recipient phone number
            message: Message content
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        return self.send_sms(to_phone, message)


# Create singleton instance
sms_service = SMSService()

