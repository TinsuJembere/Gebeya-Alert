"""
Twilio SMS provider for production SMS sending.
"""
import logging
from typing import Tuple, Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioException, TwilioRestException

from config import settings
from services.sms_providers.base import SMSProvider

logger = logging.getLogger(__name__)


class TwilioSMSProvider(SMSProvider):
    """SMS provider using Twilio API."""
    
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
                logger.info("Twilio SMS provider initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
                self.enabled = False
        else:
            logger.warning(
                "Twilio SMS provider disabled: Missing credentials or SMS_ENABLED=False"
            )
    
    def is_enabled(self) -> bool:
        """Check if Twilio is enabled and configured."""
        return self.enabled
    
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
            error_msg = "Twilio SMS provider is not enabled or not configured"
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
