"""
SMS service factory - creates appropriate SMS provider based on configuration.
This file maintains backward compatibility with the old SMSService interface.
"""
import logging
from typing import Optional, Tuple

from config import settings
from services.sms_providers.console import ConsoleSMSProvider
from services.sms_providers.twilio import TwilioSMSProvider
from services.notification_service import NotificationService

logger = logging.getLogger(__name__)

# Global SMS provider instance
_sms_provider: Optional[ConsoleSMSProvider | TwilioSMSProvider] = None
_notification_service: Optional[NotificationService] = None


def get_sms_provider():
    """
    Get the configured SMS provider based on SMS_PROVIDER setting.
    
    Returns:
        SMS provider instance (ConsoleSMSProvider or TwilioSMSProvider)
    """
    global _sms_provider
    
    if _sms_provider is not None:
        return _sms_provider
    
    provider_type = getattr(settings, 'SMS_PROVIDER', 'console').lower()
    
    if provider_type == 'twilio':
        _sms_provider = TwilioSMSProvider()
        logger.info("Using Twilio SMS provider")
    else:
        _sms_provider = ConsoleSMSProvider()
        logger.info("Using Console SMS provider (demo mode)")
    
    return _sms_provider


def get_notification_service() -> NotificationService:
    """
    Get the notification service instance.
    
    Returns:
        NotificationService instance
    """
    global _notification_service
    
    if _notification_service is None:
        provider = get_sms_provider()
        _notification_service = NotificationService(provider)
    
    return _notification_service


# Backward compatibility: Old SMSService class
class SMSService:
    """Legacy SMS service for backward compatibility."""
    
    def __init__(self):
        """Initialize with current provider."""
        self.provider = get_sms_provider()
        self.enabled = self.provider.is_enabled()
    
    def format_message(self, message: str, max_length: int = 160) -> str:
        """Format message for SMS (legacy method)."""
        formatted = " ".join(message.split())
        if len(formatted) > max_length:
            formatted = formatted[:max_length - 3] + "..."
        return formatted
    
    def send_sms(
        self,
        to_phone: str,
        message: str
    ) -> Tuple[bool, Optional[str]]:
        """Send SMS (legacy method)."""
        return self.provider.send_sms(to_phone, message)
    
    def send_price_alert(
        self,
        to_phone: str,
        crop_name: str,
        market_name: str,
        current_price: float,
        target_price: float
    ) -> Tuple[bool, Optional[str]]:
        """Send price alert (legacy method)."""
        notification_service = get_notification_service()
        return notification_service.send_price_alert(
            to_phone=to_phone,
            crop_name=crop_name,
            market_name=market_name,
            current_price=current_price,
            target_price=target_price
        )
    
    def send_generic_notification(
        self,
        to_phone: str,
        message: str
    ) -> Tuple[bool, Optional[str]]:
        """Send generic notification (legacy method)."""
        return self.provider.send_sms(to_phone, message)


# Create singleton instance for backward compatibility
sms_service = SMSService()
