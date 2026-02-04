"""
Console SMS provider for demo/testing - logs SMS messages to terminal.
"""
import logging
from typing import Tuple, Optional
from datetime import datetime

from services.sms_providers.base import SMSProvider

logger = logging.getLogger(__name__)


class ConsoleSMSProvider(SMSProvider):
    """SMS provider that logs messages to console instead of sending real SMS."""
    
    def __init__(self):
        """Initialize console SMS provider."""
        self.enabled = True
        logger.info("Console SMS provider initialized (messages will be logged to terminal)")
    
    def is_enabled(self) -> bool:
        """Console provider is always enabled."""
        return True
    
    def send_sms(
        self,
        to_phone: str,
        message: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Log SMS message to console instead of sending.
        
        Args:
            to_phone: Recipient phone number
            message: Message content
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        if not to_phone:
            error_msg = "Recipient phone number is required"
            logger.error(error_msg)
            return False, error_msg
        
        if not message:
            error_msg = "Message content is required"
            logger.error(error_msg)
            return False, error_msg
        
        # Format message for console output
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Print to console with clear formatting
        print("\n" + "=" * 80)
        print(f"📱 SMS MESSAGE (Console Mode) - {timestamp}")
        print("=" * 80)
        print(f"To: {to_phone}")
        print(f"Message ({len(message)} chars):")
        print("-" * 80)
        print(message)
        print("-" * 80)
        print("=" * 80 + "\n")
        
        # Also log to logger
        logger.info(
            f"[CONSOLE SMS] To: {to_phone} | Message: {message[:100]}..."
        )
        
        return True, None
