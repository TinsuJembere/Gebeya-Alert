"""
Alert service for business logic.
"""
from sqlmodel import Session, select
from typing import List, Optional
from fastapi import HTTPException, status
from decimal import Decimal

from models.alert import Alert
from models.user import User
from models.crop import Crop
from models.market import Market
from schemas.alert import AlertCreate


class AlertService:
    """Service for alert operations."""
    
    @staticmethod
    def get_user_alerts(db: Session, user_id: int) -> List[Alert]:
        """
        Get all alerts for a specific user.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of user's alerts
        """
        statement = select(Alert).where(
            Alert.user_id == user_id
        ).order_by(Alert.created_at.desc())
        
        return list(db.exec(statement).all())
    
    @staticmethod
    def get_alert_by_id(db: Session, alert_id: int) -> Alert:
        """
        Get alert by ID.
        
        Args:
            db: Database session
            alert_id: Alert ID
            
        Returns:
            Alert object
            
        Raises:
            HTTPException: If alert not found
        """
        alert = db.get(Alert, alert_id)
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        return alert
    
    @staticmethod
    def check_duplicate_alert(
        db: Session,
        user_id: int,
        crop_id: int,
        market_id: int
    ) -> Optional[Alert]:
        """
        Check if an alert already exists for the given user, crop, and market.
        Prevents duplicate alerts.
        
        Args:
            db: Database session
            user_id: User ID
            crop_id: Crop ID
            market_id: Market ID
            
        Returns:
            Existing alert if found, None otherwise
        """
        statement = select(Alert).where(
            Alert.user_id == user_id,
            Alert.crop_id == crop_id,
            Alert.market_id == market_id
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
    def verify_alert_ownership(db: Session, alert_id: int, user_id: int) -> Alert:
        """
        Verify that the alert belongs to the user.
        
        Args:
            db: Database session
            alert_id: Alert ID
            user_id: User ID
            
        Returns:
            Alert object if ownership verified
            
        Raises:
            HTTPException: If alert not found or doesn't belong to user
        """
        alert = AlertService.get_alert_by_id(db, alert_id)
        
        if alert.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this alert"
            )
        
        return alert
    
    @staticmethod
    def create_alert(db: Session, user_id: int, alert_data: AlertCreate) -> Alert:
        """
        Create a new alert for a user.
        Prevents duplicate alerts (same user, crop, market).
        
        Args:
            db: Database session
            user_id: User ID (owner of the alert)
            alert_data: Alert creation data
            
        Returns:
            Created alert
            
        Raises:
            HTTPException: If duplicate alert exists or related entities not found
        """
        # Validate crop exists
        AlertService.validate_crop_exists(db, alert_data.crop_id)
        
        # Validate market exists
        AlertService.validate_market_exists(db, alert_data.market_id)
        
        # Check for duplicate alert (prevent same user, crop, market combination)
        existing_alert = AlertService.check_duplicate_alert(
            db,
            user_id,
            alert_data.crop_id,
            alert_data.market_id
        )
        
        if existing_alert:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Alert already exists for this crop and market. "
                       f"Use DELETE to remove existing alert (ID: {existing_alert.id}) or update target price"
            )
        
        # Create new alert
        new_alert = Alert(
            user_id=user_id,
            crop_id=alert_data.crop_id,
            market_id=alert_data.market_id,
            target_price=alert_data.target_price
        )
        db.add(new_alert)
        db.commit()
        db.refresh(new_alert)
        
        return new_alert
    
    @staticmethod
    def delete_alert(db: Session, alert_id: int, user_id: int) -> None:
        """
        Delete an alert.
        Verifies ownership before deletion.
        
        Args:
            db: Database session
            alert_id: Alert ID
            user_id: User ID (must own the alert)
            
        Raises:
            HTTPException: If alert not found or user doesn't own it
        """
        # Verify ownership
        alert = AlertService.verify_alert_ownership(db, alert_id, user_id)
        
        # Delete the alert
        db.delete(alert)
        db.commit()
    
    @staticmethod
    def get_user_alerts_with_details(db: Session, user_id: int) -> List[dict]:
        """
        Get all alerts for a user with crop/market details and current prices.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of dictionaries with alert details including crop name, market name, and current price
        """
        from models.price import Price
        from datetime import date
        
        alerts = AlertService.get_user_alerts(db, user_id)
        alerts_with_details = []
        
        for alert in alerts:
            # Get crop and market details
            crop = db.get(Crop, alert.crop_id)
            market = db.get(Market, alert.market_id)
            
            if not crop or not market:
                continue
            
            # Get latest price for this crop-market combination
            price_statement = (
                select(Price)
                .where(
                    Price.crop_id == alert.crop_id,
                    Price.market_id == alert.market_id
                )
                .order_by(Price.price_date.desc())
                .limit(1)
            )
            latest_price_obj = db.exec(price_statement).first()
            
            current_price = None
            if latest_price_obj:
                current_price = float(latest_price_obj.price)
            
            # Determine if alert is met (current price >= target price)
            is_met = current_price is not None and current_price >= float(alert.target_price)
            
            alerts_with_details.append({
                "id": alert.id,
                "user_id": alert.user_id,
                "crop_id": alert.crop_id,
                "market_id": alert.market_id,
                "crop": crop.name,
                "market": market.name,
                "market_region": market.region,
                "target_price": float(alert.target_price),
                "current_price": current_price,
                "is_met": is_met,
                "last_sent_at": alert.last_sent_at.isoformat() if alert.last_sent_at else None,
                "created_at": alert.created_at.isoformat(),
                "updated_at": alert.updated_at.isoformat() if alert.updated_at else None,
            })
        
        return alerts_with_details
















