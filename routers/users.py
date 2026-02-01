"""
Users router.
"""
from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from database import get_db
from schemas.user import UserResponse, UserUpdate
from services.user_service import UserService
from dependencies import require_user
from models.user import User

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(require_user),
    db: Session = Depends(get_db)
):
    """
    Get current user information.
    Requires authentication.
    """
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_db)
):
    """
    Update current user information.
    Requires authentication.
    
    Can update:
    - Phone number
    - Language preference
    """
    updated_user = UserService.update_user(db, current_user.id, user_data)
    return updated_user
















