"""
Crop service for business logic.
"""
from sqlmodel import Session, select
from typing import List
from fastapi import HTTPException, status

from models.crop import Crop
from schemas.crop import CropCreate


class CropService:
    """Service for crop operations."""
    
    @staticmethod
    def get_all_crops(db: Session) -> List[Crop]:
        """
        Get all crops.
        
        Args:
            db: Database session
            
        Returns:
            List of all crops
        """
        statement = select(Crop).order_by(Crop.name)
        return list(db.exec(statement).all())
    
    @staticmethod
    def get_crop_by_id(db: Session, crop_id: int) -> Crop:
        """
        Get crop by ID.
        
        Args:
            db: Database session
            crop_id: Crop ID
            
        Returns:
            Crop object
            
        Raises:
            HTTPException: If crop not found
        """
        crop = db.get(Crop, crop_id)
        if not crop:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Crop not found"
            )
        return crop
    
    @staticmethod
    def create_crop(db: Session, crop_data: CropCreate) -> Crop:
        """
        Create a new crop.
        
        Args:
            db: Database session
            crop_data: Crop creation data
            
        Returns:
            Created crop
            
        Raises:
            HTTPException: If crop name already exists
        """
        # Check if crop with same name already exists
        statement = select(Crop).where(Crop.name == crop_data.name)
        existing_crop = db.exec(statement).first()
        if existing_crop:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Crop with this name already exists"
            )
        
        # Create new crop
        new_crop = Crop(
            name=crop_data.name,
            crop_type=crop_data.crop_type
        )
        db.add(new_crop)
        db.commit()
        db.refresh(new_crop)
        
        return new_crop
















