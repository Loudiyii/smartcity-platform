"""Sensors API routes"""

from fastapi import APIRouter
from typing import List
from app.models.sensor import SensorMetadata
from app.dependencies import get_supabase_client
from app.services.supabase_service import SupabaseService

router = APIRouter(prefix="/api/v1/sensors", tags=["sensors"])


@router.get("/", response_model=List[SensorMetadata])
async def get_sensors():
    """Get all sensor metadata."""
    supabase = get_supabase_client()
    service = SupabaseService(supabase)

    return await service.get_sensor_metadata()
