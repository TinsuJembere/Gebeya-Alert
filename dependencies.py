"""
FastAPI dependencies for authentication and database access.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from database import get_db
from utils.jwt import verify_token
from config import settings
from models.user import User

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login",
    auto_error=False
)


def get_current_user_id(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[int]:
    """
    Dependency to get current authenticated user ID from JWT token.
    
    Returns:
        User ID if token is valid, None otherwise
    """
    if not token:
        return None
    
    payload = verify_token(token)
    if payload is None:
        return None
    
    user_id_str = payload.get("sub")
    if user_id_str is None:
        return None
    
    try:
        return int(user_id_str)
    except (ValueError, TypeError):
        return None


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency to get current authenticated user from JWT token.
    
    Returns:
        User object if token is valid, None otherwise
    """
    user_id = get_current_user_id(token, db)
    if user_id is None:
        return None
    
    statement = select(User).where(User.id == user_id)
    user = db.exec(statement).first()
    return user


def require_auth(
    current_user_id: Optional[int] = Depends(get_current_user_id)
) -> int:
    """
    Dependency that requires authentication.
    Raises 401 if user is not authenticated.
    
    Returns:
        Authenticated user ID
    """
    if current_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user_id


def require_user(
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    """
    Dependency that requires authentication and returns User object.
    Raises 401 if user is not authenticated.
    
    Returns:
        Authenticated User object
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


def require_admin(
    current_user: User = Depends(require_user)
) -> User:
    """
    Dependency that requires admin privileges.
    Raises 403 if user is not an admin.
    
    Returns:
        Authenticated admin User object
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

