"""
User service for business logic.
"""
from sqlmodel import Session, select
from typing import Optional
from fastapi import HTTPException, status

from models.user import User
from schemas.user import UserUpdate
from utils.phone import normalize_phone_number


class UserService:
    """Service for user operations."""
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        """
        Get user by ID.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            User object
            
        Raises:
            HTTPException: If user not found
        """
        user = db.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User:
        """
        Update user information.
        
        Args:
            db: Database session
            user_id: User ID
            user_data: User update data
            
        Returns:
            Updated user object
            
        Raises:
            HTTPException: If user not found or phone number already exists
        """
        user = UserService.get_user_by_id(db, user_id)
        
        # Update phone number if provided
        if user_data.phone_number is not None:
            normalized_phone = normalize_phone_number(user_data.phone_number)
            
            # Check if phone number is already taken by another user
            if normalized_phone != user.phone_number:
                statement = select(User).where(User.phone_number == normalized_phone)
                existing_user = db.exec(statement).first()
                if existing_user:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Phone number already registered"
                    )
                user.phone_number = normalized_phone
        
        # Update language if provided
        if user_data.language is not None:
            user.language = user_data.language
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
















