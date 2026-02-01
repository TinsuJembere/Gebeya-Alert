"""
Crops router.
"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from database import get_db
from schemas.crop import CropCreate, CropResponse
from services.crop_service import CropService
from dependencies import require_admin
from models.user import User

router = APIRouter()


@router.get("", response_model=List[CropResponse])
async def get_crops(
    db: Session = Depends(get_db)
):
    """
    Get all crops.
    Public endpoint - no authentication required.
    """
    crops = CropService.get_all_crops(db)
    return crops


@router.post("", response_model=CropResponse, status_code=status.HTTP_201_CREATED)
async def create_crop(
    crop_data: CropCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create a new crop.
    Admin only endpoint.
    """
    crop = CropService.create_crop(db, crop_data)
    return crop

