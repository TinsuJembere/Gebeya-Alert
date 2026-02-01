"""
Crop schemas.
"""
from pydantic import BaseModel, Field


class CropCreate(BaseModel):
    """Schema for creating a crop."""
    name: str = Field(..., min_length=1, max_length=100, description="Name of the crop")
    crop_type: str = Field(default="Grain", max_length=50, description="Type of crop (e.g., Grain, Vegetable, Fruit, Legume)")


class CropResponse(BaseModel):
    """Schema for crop response."""
    id: int
    name: str
    crop_type: str
    
    class Config:
        from_attributes = True
















