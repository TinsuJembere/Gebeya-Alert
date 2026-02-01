"""
Alerts router.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from database import get_db
from schemas.alert import AlertCreate, AlertResponse
from services.alert_service import AlertService
from dependencies import require_user
from models.user import User

router = APIRouter()


@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_data: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """
    Create a new price alert.
    Requires authentication.
    
    Requirements:
    - One alert per user per crop per market (prevents duplicates)
    - Target price must be positive
    - Price is in ETB (Ethiopian Birr)
    
    Returns:
        Created alert
    """
    alert = AlertService.create_alert(db, current_user.id, alert_data)
    return alert


@router.get("", response_model=List[Dict[str, Any]])
async def get_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """
    Get all alerts for the current user with details (crop/market names and current prices).
    Requires authentication.
    
    Returns:
        List of user's alerts with crop name, market name, and current price
    """
    alerts = AlertService.get_user_alerts_with_details(db, current_user.id)
    return alerts


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """
    Delete an alert.
    Requires authentication and ownership of the alert.
    
    Args:
        alert_id: ID of the alert to delete
        
    Returns:
        204 No Content on success
        
    Raises:
        403: If user doesn't own the alert
        404: If alert not found
    """
    AlertService.delete_alert(db, alert_id, current_user.id)
    return None
















