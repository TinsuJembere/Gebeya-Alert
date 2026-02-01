"""
Price service for business logic.
"""
import logging
from datetime import date, timedelta
from sqlmodel import Session, select
from typing import List, Optional
from fastapi import HTTPException, status
from decimal import Decimal

from models.price import Price
from models.crop import Crop
from models.market import Market
from models.alert import Alert
from models.user import User
from models.notification_log import NotificationLog
from schemas.price import PriceCreate
from services.sms_service import sms_service

logger = logging.getLogger(__name__)


class PriceService:
    """Service for price operations."""
    
    @staticmethod
    def get_prices(
        db: Session,
        crop_id: Optional[int] = None,
        market_id: Optional[int] = None,
        price_date: Optional[date] = None,
        limit: Optional[int] = None
    ) -> List[Price]:
        """
        Get prices with optional filters.
        Optimized with limit support for large datasets.
        
        Args:
            db: Database session
            crop_id: Optional crop ID filter
            market_id: Optional market ID filter
            price_date: Optional date filter
            limit: Optional limit on number of results
            
        Returns:
            List of prices matching the filters
        """
        statement = select(Price)
        
        # Apply filters
        if crop_id is not None:
            statement = statement.where(Price.crop_id == crop_id)
        
        if market_id is not None:
            statement = statement.where(Price.market_id == market_id)
        
        if price_date is not None:
            statement = statement.where(Price.price_date == price_date)
        
        # Order by date (newest first), then by crop and market
        statement = statement.order_by(Price.price_date.desc(), Price.crop_id, Price.market_id)
        
        # Apply limit if specified
        if limit is not None:
            statement = statement.limit(limit)
        
        return list(db.exec(statement).all())
    
    @staticmethod
    def get_price_by_id(db: Session, price_id: int) -> Price:
        """
        Get price by ID.
        
        Args:
            db: Database session
            price_id: Price ID
            
        Returns:
            Price object
            
        Raises:
            HTTPException: If price not found
        """
        price = db.get(Price, price_id)
        if not price:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Price not found"
            )
        return price
    
    @staticmethod
    def check_duplicate_price(
        db: Session,
        crop_id: int,
        market_id: int,
        price_date: date
    ) -> Optional[Price]:
        """
        Check if a price already exists for the given crop, market, and date.
        
        Args:
            db: Database session
            crop_id: Crop ID
            market_id: Market ID
            price_date: Date of the price
            
        Returns:
            Existing price if found, None otherwise
        """
        statement = select(Price).where(
            Price.crop_id == crop_id,
            Price.market_id == market_id,
            Price.price_date == price_date
        )
        return db.exec(statement).first()
    
    @staticmethod
    def validate_crop_exists(db: Session, crop_id: int) -> Crop:
        """
        Validate that crop exists.
        
        Args:
            db: Database session
            crop_id: Crop ID
            
        Returns:
            Crop object
            
        Raises:
            HTTPException: If crop not found
        """
        crop = db.get(Crop, crop_id)
        if not crop:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Crop with ID {crop_id} not found"
            )
        return crop
    
    @staticmethod
    def validate_market_exists(db: Session, market_id: int) -> Market:
        """
        Validate that market exists.
        
        Args:
            db: Database session
            market_id: Market ID
            
        Returns:
            Market object
            
        Raises:
            HTTPException: If market not found
        """
        market = db.get(Market, market_id)
        if not market:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Market with ID {market_id} not found"
            )
        return market
    
    @staticmethod
    def create_price(db: Session, price_data: PriceCreate) -> Price:
        """
        Create a new price.
        Enforces one price per crop per market per day.
        
        Args:
            db: Database session
            price_data: Price creation data
            
        Returns:
            Created price
            
        Raises:
            HTTPException: If duplicate price exists or related entities not found
        """
        # Validate crop exists
        PriceService.validate_crop_exists(db, price_data.crop_id)
        
        # Validate market exists
        PriceService.validate_market_exists(db, price_data.market_id)
        
        # Check for duplicate (one price per crop per market per day)
        existing_price = PriceService.check_duplicate_price(
            db,
            price_data.crop_id,
            price_data.market_id,
            price_data.price_date
        )
        
        if existing_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Price already exists for this crop, market, and date. "
                       f"Use PUT/PATCH to update existing price (ID: {existing_price.id})"
            )
        
        # Create new price
        new_price = Price(
            crop_id=price_data.crop_id,
            market_id=price_data.market_id,
            price=price_data.price,
            price_date=price_data.price_date,
            source=price_data.source or "manual",
            confidence_score=price_data.confidence_score or 1.0
        )
        db.add(new_price)
        db.commit()
        db.refresh(new_price)
        
        # Notify users about price change if significant (async, don't block)
        try:
            PriceService._notify_price_change(db, new_price)
        except Exception as e:
            # Log error but don't fail price creation
            logger.error(f"Error in price change notification: {str(e)}", exc_info=True)
        
        return new_price
    
    @staticmethod
    def get_latest_prices_with_details(db: Session, limit: int = 10) -> List[dict]:
        """
        Get latest prices with crop and market details, including trend calculation.
        Optimized for large datasets using efficient queries.
        
        Args:
            db: Database session
            limit: Maximum number of prices to return
            
        Returns:
            List of dictionaries with price, crop, market, and trend information
        """
        # Get latest prices ordered by date, then group by crop-market
        # This approach works with both SQLite and PostgreSQL
        statement = (
            select(Price)
            .order_by(Price.price_date.desc())
            .limit(limit * 3)  # Get extra to account for duplicates
        )
        all_prices = db.exec(statement).all()
        
        # Group by crop-market and get latest for each
        seen = {}
        latest_prices = []
        
        for price in all_prices:
            key = (price.crop_id, price.market_id)
            if key not in seen:
                seen[key] = True
                
                # Get crop and market details
                crop = db.get(Crop, price.crop_id)
                market = db.get(Market, price.market_id)
                
                if not crop or not market:
                    continue
                
                # Get previous price for trend calculation (7 days ago)
                prev_date = price.price_date - timedelta(days=7)
                prev_statement = (
                    select(Price)
                    .where(
                        Price.crop_id == price.crop_id,
                        Price.market_id == price.market_id,
                        Price.price_date <= prev_date
                    )
                    .order_by(Price.price_date.desc())
                    .limit(1)
                )
                prev_price_obj = db.exec(prev_statement).first()
                
                # Calculate trend
                change = 0
                if prev_price_obj:
                    current_price = float(price.price)
                    previous_price = float(prev_price_obj.price)
                    change = current_price - previous_price
                
                # Safely get crop_type (handle existing crops without crop_type column)
                try:
                    crop_type = crop.crop_type if hasattr(crop, 'crop_type') else 'Grain'
                except (AttributeError, KeyError):
                    crop_type = 'Grain'
                
                # Safely get source and confidence_score (handle old database without these columns)
                try:
                    source = price.source if hasattr(price, 'source') and price.source else "manual"
                except (AttributeError, KeyError):
                    source = "manual"
                
                try:
                    confidence_score = float(price.confidence_score) if hasattr(price, 'confidence_score') and price.confidence_score else 1.0
                except (AttributeError, KeyError):
                    confidence_score = 1.0
                
                # Safely get timestamps
                try:
                    updated_at = price.updated_at.isoformat() if hasattr(price, 'updated_at') and price.updated_at else None
                except (AttributeError, KeyError):
                    updated_at = None
                
                if not updated_at:
                    try:
                        updated_at = price.created_at.isoformat() if hasattr(price, 'created_at') and price.created_at else None
                    except (AttributeError, KeyError):
                        updated_at = None
                
                latest_prices.append({
                    "id": price.id,
                    "crop_id": price.crop_id,
                    "market_id": price.market_id,
                    "crop_name": crop.name,
                    "crop_type": crop_type,
                    "market_name": market.name,
                    "market_region": market.region,
                    "price": float(price.price),
                    "price_date": price.price_date.isoformat(),
                    "price_change_7d": change,
                    "source": source,
                    "confidence_score": confidence_score,
                    "updated_at": updated_at
                })
                
                if len(latest_prices) >= limit:
                    break
        
        return latest_prices
    
    @staticmethod
    def _notify_price_change(db: Session, new_price: Price) -> None:
        """
        Notify users about price changes for crops they have alerts on.
        
        Args:
            db: Database session
            new_price: Newly created price record
        """
        try:
            # Get all active alerts for this crop-market combination
            alert_statement = (
                select(Alert)
                .where(
                    Alert.crop_id == new_price.crop_id,
                    Alert.market_id == new_price.market_id
                )
            )
            alerts = db.exec(alert_statement).all()
            
            if not alerts:
                return
            
            # Get crop and market details
            crop = db.get(Crop, new_price.crop_id)
            market = db.get(Market, new_price.market_id)
            
            if not crop or not market:
                return
            
            # Get previous price (from yesterday or latest)
            prev_date = new_price.price_date - timedelta(days=1)
            prev_statement = (
                select(Price)
                .where(
                    Price.crop_id == new_price.crop_id,
                    Price.market_id == new_price.market_id,
                    Price.price_date < new_price.price_date
                )
                .order_by(Price.price_date.desc())
                .limit(1)
            )
            prev_price = db.exec(prev_statement).first()
            
            # Calculate price change percentage
            price_change_pct = 0
            if prev_price:
                prev_price_float = float(prev_price.price)
                new_price_float = float(new_price.price)
                if prev_price_float > 0:
                    price_change_pct = ((new_price_float - prev_price_float) / prev_price_float) * 100
            
            # Only notify if price changed by more than 5%
            if abs(price_change_pct) < 5:
                return
            
            # Send notifications to users with alerts
            for alert in alerts:
                user = db.get(User, alert.user_id)
                if not user:
                    continue
                
                # Create price change notification message
                direction = "increased" if price_change_pct > 0 else "decreased"
                message = (
                    f"Price Update: {crop.name} at {market.name} "
                    f"has {direction} to {new_price.price:.2f} ETB. "
                    f"Change: {abs(price_change_pct):.1f}%"
                )
                
                # Send SMS
                success, error = sms_service.send_generic_notification(
                    to_phone=user.phone_number,
                    message=message
                )
                
                if success:
                    # Log notification
                    notification_log = NotificationLog(
                        user_id=user.id,
                        message=message
                    )
                    db.add(notification_log)
                    logger.info(
                        f"Price change notification sent to user {user.id} "
                        f"for {crop.name} at {market.name}"
                    )
                else:
                    logger.error(
                        f"Failed to send price change notification to user {user.id}: {error}"
                    )
            
            db.commit()
            
        except Exception as e:
            logger.error(
                f"Error notifying users about price change: {str(e)}",
                exc_info=True
            )
            db.rollback()





