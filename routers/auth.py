"""
Authentication router.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from datetime import timedelta
import traceback

from database import get_db
from schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from services.auth_service import AuthService
from utils.jwt import create_access_token
from utils.friendly_errors import get_friendly_message
from config import settings
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

# Add this endpoint to the auth router
@router.post("/login", response_model=TokenResponse)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    if settings.DEBUG:
        print(f"[LOGIN] Attempting login for phone: {form_data.username}")

    try:
        # In our case, the username field will contain the phone number
        user = AuthService.authenticate_user(
            db, 
            phone_number=form_data.username,
            password=form_data.password  # This would be the OTP in your case
        )
        if not user:
            if settings.DEBUG:
                print("[LOGIN] Authentication failed")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="The phone number or password you entered is incorrect. Please check and try again.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "phone": user.phone_number},
            expires_delta=access_token_expires
        )

        if settings.DEBUG:
            print("[LOGIN] Login successful")

        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException:
        raise
    except Exception as e:
        if settings.DEBUG:
            print(f"[LOGIN] Error: {e}")
            print(traceback.format_exc())
        friendly_message = get_friendly_message(str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=friendly_message
        )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    if settings.DEBUG:
        print(f"[REGISTER] Received request with phone: {user_data.phone_number}, language: {user_data.language}")

    try:
        if settings.DEBUG:
            print("[REGISTER] Starting user registration...")

        # Register user
        user = AuthService.register_user(db, user_data)

        if settings.DEBUG:
            print(f"[REGISTER] User created with ID: {user.id}")

        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "phone": user.phone_number},
            expires_delta=access_token_expires
        )

        if settings.DEBUG:
            print("[REGISTER] Access token created successfully")

        return TokenResponse(access_token=access_token)

    except HTTPException as he:
        if settings.DEBUG:
            print(f"[REGISTER] HTTPException: {he.status_code} - {he.detail}")
        raise

    except Exception as e:
        if settings.DEBUG:
            print(f"[REGISTER] Error: {e}")
            print(traceback.format_exc())
        friendly_message = get_friendly_message(str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=friendly_message
        )
