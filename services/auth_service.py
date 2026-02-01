"""
Authentication service for business logic.
"""
from sqlmodel import Session, select
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
import traceback

from models.user import User
from schemas.auth import RegisterRequest
from config import settings
from utils.password import hash_password, verify_password
from utils.password import hash_password, verify_password


class AuthService:
    """Service for authentication operations."""

    @staticmethod
    def get_user_by_phone(db: Session, phone_number: str) -> Optional[User]:
        """
        Get user by phone number.
        """
        statement = select(User).where(User.phone_number == phone_number)
        return db.exec(statement).first()

    @staticmethod
    def register_user(db: Session, user_data: RegisterRequest) -> User:
        """
        Register a new user.
        """
        try:
            # Check if user already exists
            existing_user = AuthService.get_user_by_phone(db, user_data.phone_number)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Phone number already registered"
                )

            # Create new user with hashed password
            new_user = User(
                phone_number=user_data.phone_number,
                language=user_data.language,
                hashed_password=hash_password(user_data.password)
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            return new_user

        except HTTPException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            if settings.DEBUG:
                print(f"Database error in register_user: {e}")
                print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred during registration"
            )
        except Exception as e:
            db.rollback()
            if settings.DEBUG:
                print(f"Unexpected error in register_user: {e}")
                print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Registration failed: {str(e)}"
            )

    @staticmethod
    def login_user(db: Session, phone_number: str) -> User:
        """
        Login user by phone number.
        Auto-registers user if doesn't exist.
        """
        try:
            # Try to get existing user
            user = AuthService.get_user_by_phone(db, phone_number)

            if not user:
                # Auto-register if user doesn't exist
                user = User(
                    phone_number=phone_number,
                    language="en"
                )
                db.add(user)
                db.commit()
                db.refresh(user)

            return user

        except SQLAlchemyError as e:
            db.rollback()
            if settings.DEBUG:
                print(f"Database error in login_user: {e}")
                print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred during login"
            )
        except Exception as e:
            db.rollback()
            if settings.DEBUG:
                print(f"Unexpected error in login_user: {e}")
                print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Login failed: {str(e)}"
            )

    @staticmethod
    def authenticate_user(db: Session, phone_number: str, password: str) -> Optional[User]:
        """
        Authenticate a user with phone number and password.
        
        Args:
            db: Database session
            phone_number: User's phone number
            password: Plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        if settings.DEBUG:
            print(f"[AUTH] Authenticating user: {phone_number}")

        # Check if user exists
        user = AuthService.get_user_by_phone(db, phone_number)
        if not user:
            if settings.DEBUG:
                print(f"[AUTH] User not found: {phone_number}")
            return None

        # Verify password if user has a password set
        if user.hashed_password:
            if not verify_password(password, user.hashed_password):
                if settings.DEBUG:
                    print(f"[AUTH] Password verification failed for user: {phone_number}")
                return None
        else:
            # If no password is set, allow login (for backward compatibility with OTP-only users)
            if settings.DEBUG:
                print(f"[AUTH] User has no password set, allowing login: {user.id}")

        if settings.DEBUG:
            print(f"[AUTH] User authenticated: {user.id}")

        return user
