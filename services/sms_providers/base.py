"""
Base SMS provider interface.
"""
from abc import ABC, abstractmethod
from typing import Tuple, Optional


class SMSProvider(ABC):
    """Abstract base class for SMS providers."""
    
    @abstractmethod
    def send_sms(
        self,
        to_phone: str,
        message: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Send SMS message.
        
        Args:
            to_phone: Recipient phone number
            message: Message content
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        pass
    
    @abstractmethod
    def is_enabled(self) -> bool:
        """
        Check if the provider is enabled and ready to send messages.
        
        Returns:
            True if enabled, False otherwise
        """
        pass
