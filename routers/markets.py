"""
Markets router.
"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from database import get_db
from schemas.market import MarketCreate, MarketResponse
from services.market_service import MarketService
from dependencies import require_admin
from models.user import User

router = APIRouter()


@router.get("", response_model=List[MarketResponse])
async def get_markets(
    db: Session = Depends(get_db)
):
    """
    Get all markets.
    Public endpoint - no authentication required.
    """
    markets = MarketService.get_all_markets(db)
    return markets


@router.post("", response_model=MarketResponse, status_code=status.HTTP_201_CREATED)
async def create_market(
    market_data: MarketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create a new market.
    Admin only endpoint.
    """
    market = MarketService.create_market(db, market_data)
    return market

