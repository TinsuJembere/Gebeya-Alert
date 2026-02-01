"""
Market service for business logic.
"""
from sqlmodel import Session, select
from typing import List
from fastapi import HTTPException, status

from models.market import Market
from schemas.market import MarketCreate


class MarketService:
    """Service for market operations."""
    
    @staticmethod
    def get_all_markets(db: Session) -> List[Market]:
        """
        Get all markets.
        
        Args:
            db: Database session
            
        Returns:
            List of all markets
        """
        statement = select(Market).order_by(Market.name, Market.region)
        return list(db.exec(statement).all())
    
    @staticmethod
    def get_market_by_id(db: Session, market_id: int) -> Market:
        """
        Get market by ID.
        
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
                detail="Market not found"
            )
        return market
    
    @staticmethod
    def create_market(db: Session, market_data: MarketCreate) -> Market:
        """
        Create a new market.
        
        Args:
            db: Database session
            market_data: Market creation data
            
        Returns:
            Created market
            
        Raises:
            HTTPException: If market with same name and region already exists
        """
        # Check if market with same name and region already exists
        statement = select(Market).where(
            Market.name == market_data.name,
            Market.region == market_data.region
        )
        existing_market = db.exec(statement).first()
        if existing_market:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Market with this name and region already exists"
            )
        
        # Create new market
        new_market = Market(
            name=market_data.name,
            region=market_data.region
        )
        db.add(new_market)
        db.commit()
        db.refresh(new_market)
        
        return new_market
















