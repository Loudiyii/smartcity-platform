"""Pydantic models for IoT sensors"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SensorMetadata(BaseModel):
    """Sensor metadata model."""
    sensor_id: str
    name: str
    location: dict
    status: str = "active"
    last_reading_at: Optional[datetime] = None


class SensorReading(BaseModel):
    """Sensor reading model."""
    sensor_id: str
    pm25: float
    pm10: float
    temperature: float
    humidity: int
    timestamp: Optional[datetime] = None
