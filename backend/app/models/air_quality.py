"""Pydantic models for air quality data"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LocationModel(BaseModel):
    """Geographic location."""
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    name: Optional[str] = None


class AirQualityBase(BaseModel):
    """Base air quality model."""
    source: str = Field(..., max_length=50)
    city: Optional[str] = Field(None, max_length=100)
    location: Optional[LocationModel] = None

    # Pollutants
    aqi: Optional[int] = Field(None, ge=0, le=500)
    pm25: Optional[float] = Field(None, ge=0)
    pm10: Optional[float] = Field(None, ge=0)
    no2: Optional[float] = Field(None, ge=0)
    o3: Optional[float] = Field(None, ge=0)
    so2: Optional[float] = Field(None, ge=0)


class AirQualityCreate(AirQualityBase):
    """Create air quality measurement."""
    timestamp: Optional[datetime] = None


class AirQualityResponse(AirQualityBase):
    """Air quality response model."""
    id: int
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True
