"""
Pydantic models for IDFM mobility data
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TrafficDisruption(BaseModel):
    """Traffic disruption/incident information from IDFM."""
    disruption_id: str
    line_id: Optional[str] = None
    line_name: Optional[str] = None
    severity: str = Field(..., description="low, medium, high, critical")
    message: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class VelibStation(BaseModel):
    """Vélib bike-sharing station data."""
    station_id: str
    name: str
    num_bikes_available: int = Field(ge=0)
    num_docks_available: int = Field(ge=0)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    is_installed: bool = True
    is_returning: bool = True
    is_renting: bool = True
    last_reported: Optional[datetime] = None

    @property
    def capacity(self) -> int:
        """Total capacity of the station."""
        return self.num_bikes_available + self.num_docks_available

    @property
    def availability_percent(self) -> float:
        """Percentage of bikes available."""
        if self.capacity == 0:
            return 0.0
        return (self.num_bikes_available / self.capacity) * 100


class TransitStop(BaseModel):
    """Transit stop/station information."""
    stop_id: str
    stop_name: str
    stop_lat: float = Field(ge=-90, le=90)
    stop_lon: float = Field(ge=-180, le=180)
    zone_id: Optional[str] = None
    location_type: int = 0  # 0=stop, 1=station


class VelibStatsResponse(BaseModel):
    """Aggregated Vélib statistics."""
    total_stations: int
    total_bikes_available: int
    total_docks_available: int
    average_availability_percent: float
