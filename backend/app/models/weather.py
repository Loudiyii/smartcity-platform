"""Pydantic models for weather data"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class WeatherBase(BaseModel):
    """Base weather model."""
    city: str
    temperature: float
    humidity: int = Field(..., ge=0, le=100)
    pressure: int = Field(..., gt=0)
    wind_speed: float = Field(..., ge=0)
    wind_direction: Optional[int] = Field(None, ge=0, le=360)


class WeatherCreate(WeatherBase):
    """Create weather data."""
    timestamp: Optional[datetime] = None


class WeatherResponse(WeatherBase):
    """Weather response model."""
    id: int
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True
