"""
Prices router.
"""
from datetime import date as date_type
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from database import get_db
from schemas.price import PriceCreate, PriceResponse, PricePrediction, BestTimeToSell
from services.price_service import PriceService
from services.prediction_service import PredictionService
from dependencies import require_admin
from models.user import User

router = APIRouter()


@router.get("", response_model=List[PriceResponse])
async def get_prices(
    crop_id: Optional[int] = Query(None, description="Filter by crop ID"),
    market_id: Optional[int] = Query(None, description="Filter by market ID"),
    date: Optional[date_type] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Get prices with optional filters.
    Public endpoint - no authentication required.
    
    Query parameters:
    - crop_id: Filter by crop ID
    - market_id: Filter by market ID
    - date: Filter by date (YYYY-MM-DD format)
    
    Examples:
    - GET /prices - Get all prices
    - GET /prices?crop_id=1 - Get prices for crop ID 1
    - GET /prices?market_id=2 - Get prices for market ID 2
    - GET /prices?crop_id=1&market_id=2 - Get prices for crop 1 at market 2
    - GET /prices?date=2024-01-15 - Get prices for specific date
    """
    prices = PriceService.get_prices(
        db,
        crop_id=crop_id,
        market_id=market_id,
        price_date=date
    )
    return prices


@router.get("/latest", response_model=List[Dict[str, Any]])
async def get_latest_prices(
    limit: int = Query(10, ge=1, le=100, description="Maximum number of prices to return"),
    db: Session = Depends(get_db)
):
    """
    Get latest prices with crop and market details, including trend calculation.
    Public endpoint - no authentication required.
    
    Returns the most recent price for each crop-market combination,
    with trend calculated based on price 7 days ago.
    """
    prices = PriceService.get_latest_prices_with_details(db, limit=limit)
    return prices


@router.post("", response_model=PriceResponse, status_code=status.HTTP_201_CREATED)
async def create_price(
    price_data: PriceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create a new price entry.
    Admin only endpoint.
    
    Requirements:
    - One price per crop per market per day
    - Price must be positive
    - Price is stored in ETB (Ethiopian Birr)
    
    Returns:
        Created price entry
    """
    price = PriceService.create_price(db, price_data)
    return price


@router.get("/predictions/{crop_id}/{market_id}", response_model=PricePrediction)
async def get_price_prediction(
    crop_id: int,
    market_id: int,
    days_ahead: int = Query(7, ge=1, le=30, description="Number of days to predict ahead"),
    db: Session = Depends(get_db)
):
    """
    Get price prediction for a crop-market combination.
    Public endpoint - no authentication required.
    
    Uses moving averages and simple regression to predict future prices.
    
    Args:
        crop_id: Crop ID
        market_id: Market ID
        days_ahead: Number of days to predict ahead (1-30)
    
    Returns:
        PricePrediction with predicted price, trend, and recommendation
    """
    prediction = PredictionService.predict_price(db, crop_id, market_id, days_ahead=days_ahead)
    return prediction


@router.get("/best-time-to-sell/{crop_id}/{market_id}", response_model=BestTimeToSell)
async def get_best_time_to_sell(
    crop_id: int,
    market_id: int,
    db: Session = Depends(get_db)
):
    """
    Get recommendation for best time to sell a crop.
    Public endpoint - no authentication required.
    
    Analyzes historical prices and trends to provide actionable advice.
    
    Args:
        crop_id: Crop ID
        market_id: Market ID
    
    Returns:
        BestTimeToSell with recommendation and reasoning
    """
    recommendation = PredictionService.get_best_time_to_sell(db, crop_id, market_id)
    return recommendation

