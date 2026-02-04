"""
Notification service for generating SMS content with AI insights.
"""
import logging
from typing import Optional, Tuple
from decimal import Decimal

from services.sms_providers.base import SMSProvider
from services.prediction_service import PredictionService
from sqlmodel import Session

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for generating and sending notifications with rich content."""
    
    def __init__(self, sms_provider: SMSProvider):
        """
        Initialize notification service with SMS provider.
        
        Args:
            sms_provider: SMS provider instance (ConsoleSMSProvider or TwilioSMSProvider)
        """
        self.sms_provider = sms_provider
    
    def generate_price_alert_message(
        self,
        crop_name: str,
        market_name: str,
        current_price: float,
        target_price: float,
        confidence_score: Optional[float] = None,
        source: Optional[str] = None,
        price_change_7d: Optional[float] = None
    ) -> str:
        """
        Generate SMS message for price alert with additional context.
        
        Args:
            crop_name: Name of the crop
            market_name: Name of the market
            current_price: Current price in ETB
            target_price: Target price in ETB
            confidence_score: Confidence score (0.0-1.0) for price data
            source: Source of price data (manual, api, sms, market_officer)
            price_change_7d: 7-day price change in ETB
            
        Returns:
            Formatted SMS message
        """
        # Base message
        message = (
            f"🎯 Price Alert!\n"
            f"{crop_name} at {market_name}\n"
            f"Current: {current_price:.2f} ETB\n"
            f"Target: {target_price:.2f} ETB\n"
        )
        
        # Add price change if available
        if price_change_7d is not None:
            if price_change_7d > 0:
                message += f"📈 +{price_change_7d:.2f} ETB (7d)\n"
            elif price_change_7d < 0:
                message += f"📉 {price_change_7d:.2f} ETB (7d)\n"
            else:
                message += f"➡️ Stable (7d)\n"
        
        # Add confidence score if available
        if confidence_score is not None:
            confidence_pct = int(confidence_score * 100)
            if confidence_pct >= 80:
                message += f"✅ Confidence: {confidence_pct}%\n"
            elif confidence_pct >= 60:
                message += f"⚠️ Confidence: {confidence_pct}%\n"
            else:
                message += f"❓ Confidence: {confidence_pct}%\n"
        
        # Add source if available and not manual
        if source and source != 'manual':
            source_labels = {
                'api': '🌐 API',
                'sms': '📱 SMS',
                'market_officer': '👤 Officer'
            }
            message += f"Source: {source_labels.get(source, source)}\n"
        
        message += "\nGebeyaAlert"
        
        return message
    
    def generate_best_time_to_sell_message(
        self,
        crop_name: str,
        market_name: str,
        current_price: float,
        recommended_price: float,
        recommendation: str,
        confidence: float,
        reasoning: Optional[str] = None
    ) -> str:
        """
        Generate SMS message for best time to sell recommendation.
        
        Args:
            crop_name: Name of the crop
            market_name: Name of the market
            current_price: Current price in ETB
            recommended_price: Recommended price in ETB
            recommendation: Human-readable recommendation
            confidence: Confidence score (0.0-1.0)
            reasoning: Optional reasoning explanation
            
        Returns:
            Formatted SMS message
        """
        price_diff = recommended_price - current_price
        price_diff_pct = (price_diff / current_price) * 100 if current_price > 0 else 0
        confidence_pct = int(confidence * 100)
        
        message = (
            f"💡 Best Time to Sell\n"
            f"{crop_name} at {market_name}\n\n"
            f"Current: {current_price:.2f} ETB\n"
        )
        
        if price_diff != 0:
            if price_diff > 0:
                message += f"Recommended: {recommended_price:.2f} ETB\n"
                message += f"(+{price_diff_pct:.1f}% higher)\n\n"
            else:
                message += f"Recommended: {recommended_price:.2f} ETB\n"
                message += f"({price_diff_pct:.1f}% lower)\n\n"
        
        message += f"Advice: {recommendation}\n"
        
        if reasoning:
            message += f"\nWhy: {reasoning}\n"
        
        message += f"\nConfidence: {confidence_pct}%\n"
        message += "\nGebeyaAlert"
        
        return message
    
    def generate_price_update_message(
        self,
        crop_name: str,
        market_name: str,
        price: float,
        confidence_score: Optional[float] = None,
        source: Optional[str] = None,
        price_change_7d: Optional[float] = None
    ) -> str:
        """
        Generate SMS message for general price update.
        
        Args:
            crop_name: Name of the crop
            market_name: Name of the market
            price: Current price in ETB
            confidence_score: Confidence score (0.0-1.0)
            source: Source of price data
            price_change_7d: 7-day price change
            
        Returns:
            Formatted SMS message
        """
        message = (
            f"📊 Price Update\n"
            f"{crop_name} at {market_name}\n"
            f"Price: {price:.2f} ETB\n"
        )
        
        if price_change_7d is not None:
            if price_change_7d > 0:
                message += f"📈 +{price_change_7d:.2f} ETB (7d)\n"
            elif price_change_7d < 0:
                message += f"📉 {price_change_7d:.2f} ETB (7d)\n"
            else:
                message += f"➡️ Stable (7d)\n"
        
        if confidence_score is not None:
            confidence_pct = int(confidence_score * 100)
            message += f"Confidence: {confidence_pct}%\n"
        
        if source and source != 'manual':
            source_labels = {
                'api': '🌐 API',
                'sms': '📱 SMS',
                'market_officer': '👤 Officer'
            }
            message += f"Source: {source_labels.get(source, source)}\n"
        
        message += "\nGebeyaAlert"
        
        return message
    
    def send_price_alert(
        self,
        to_phone: str,
        crop_name: str,
        market_name: str,
        current_price: float,
        target_price: float,
        confidence_score: Optional[float] = None,
        source: Optional[str] = None,
        price_change_7d: Optional[float] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Send price alert SMS with rich content.
        
        Args:
            to_phone: Recipient phone number
            crop_name: Name of the crop
            market_name: Name of the market
            current_price: Current price in ETB
            target_price: Target price in ETB
            confidence_score: Confidence score for price data
            source: Source of price data
            price_change_7d: 7-day price change
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        message = self.generate_price_alert_message(
            crop_name=crop_name,
            market_name=market_name,
            current_price=current_price,
            target_price=target_price,
            confidence_score=confidence_score,
            source=source,
            price_change_7d=price_change_7d
        )
        
        return self.sms_provider.send_sms(to_phone, message)
    
    def send_best_time_to_sell(
        self,
        db: Session,
        to_phone: str,
        crop_id: int,
        market_id: int,
        crop_name: str,
        market_name: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Send best time to sell recommendation SMS.
        
        Args:
            db: Database session
            to_phone: Recipient phone number
            crop_id: Crop ID
            market_id: Market ID
            crop_name: Name of the crop
            market_name: Name of the market
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            # Get recommendation from prediction service
            recommendation = PredictionService.get_best_time_to_sell(
                db, crop_id, market_id
            )
            
            message = self.generate_best_time_to_sell_message(
                crop_name=crop_name,
                market_name=market_name,
                current_price=float(recommendation.current_price),
                recommended_price=float(recommendation.recommended_price),
                recommendation=recommendation.recommendation,
                confidence=recommendation.confidence,
                reasoning=recommendation.reasoning
            )
            
            return self.sms_provider.send_sms(to_phone, message)
            
        except Exception as e:
            error_msg = f"Failed to generate best time to sell message: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
    
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
        return self.sms_provider.send_sms(to_phone, message)
