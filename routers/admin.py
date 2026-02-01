"""
Admin router.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func
from typing import List, Dict, Any

from database import get_db
from models.user import User
from models.alert import Alert
from models.crop import Crop
from models.market import Market
from models.price import Price
from schemas.user import UserResponse, UserCreate, UserUpdate
from schemas.crop import CropResponse
from schemas.market import MarketResponse
from dependencies import require_admin

router = APIRouter()

@router.get("/users", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """List all users (admin only)"""
    users = db.exec(select(User).offset(skip).limit(limit)).all()
    return users

@router.post("/users", response_model=UserResponse)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new user (admin only)"""
    # Check if user already exists
    existing_user = db.exec(select(User).where(User.phone_number == user_data.phone_number)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this phone number already exists"
        )
    
    # Create new user
    user = User(**user_data.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update a user (admin only)"""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    update_data = user_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/users/{user_id}/make-admin")
def make_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Grant admin privileges to a user (admin only)"""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_admin = True
    db.add(user)
    db.commit()
    return {"message": f"User {user.phone_number} is now an admin"}


@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get statistics for admin dashboard"""
    total_users = db.exec(select(func.count(User.id))).one()
    active_alerts = db.exec(select(func.count(Alert.id))).one()
    total_markets = db.exec(select(func.count(Market.id))).one()
    
    # Get latest price update time (simplified - just show if prices exist)
    latest_price = db.exec(select(Price).order_by(Price.price_date.desc()).limit(1)).first()
    recent_updates = "None"
    if latest_price:
        from datetime import datetime, date
        # Calculate days since latest price date
        if isinstance(latest_price.price_date, date):
            days_ago = (datetime.utcnow().date() - latest_price.price_date).days
            if days_ago == 0:
                recent_updates = "Today"
            elif days_ago == 1:
                recent_updates = "1 day"
            else:
                recent_updates = f"{days_ago} days"
    
    return {
        "total_users": total_users,
        "active_alerts": active_alerts,
        "total_markets": total_markets,
        "recent_updates": recent_updates
    }


@router.get("/markets", response_model=List[MarketResponse])
def list_markets(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """List all markets (admin only)"""
    from services.market_service import MarketService
    return MarketService.get_all_markets(db)


@router.get("/crops", response_model=List[CropResponse])
def list_crops(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """List all crops (admin only)"""
    from services.crop_service import CropService
    return CropService.get_all_crops(db)