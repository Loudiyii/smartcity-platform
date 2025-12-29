"""Air Quality API routes"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models.air_quality import AirQualityCreate, AirQualityResponse
from app.dependencies import get_supabase_client
from app.services.supabase_service import SupabaseService

router = APIRouter(prefix="/api/v1/air-quality", tags=["air-quality"])


@router.get("/current", response_model=AirQualityResponse)
async def get_current_air_quality(city: str = Query(..., description="City name")):
    """Get current air quality data for a city."""
    supabase = get_supabase_client()
    service = SupabaseService(supabase)

    # Normalize city name to Title Case for consistent DB queries
    city_normalized = city.capitalize()

    data = await service.get_current_air_quality(city_normalized)
    if not data:
        raise HTTPException(status_code=404, detail=f"No data found for {city}")

    return data


@router.get("/history", response_model=List[AirQualityResponse])
async def get_air_quality_history(
    city: str = Query(...),
    limit: int = Query(100, le=1000)
):
    """Get historical air quality data."""
    supabase = get_supabase_client()
    service = SupabaseService(supabase)

    # Normalize city name to Title Case for consistent DB queries
    city_normalized = city.capitalize()

    return await service.get_air_quality_history(city_normalized, limit)


@router.post("/measurements", response_model=AirQualityResponse, status_code=201)
async def create_measurement(measurement: AirQualityCreate):
    """Create a new air quality measurement."""
    supabase = get_supabase_client()
    service = SupabaseService(supabase)

    # Use mode='json' to serialize datetime objects to ISO strings
    data = measurement.model_dump(exclude_none=True, mode='json')
    result = await service.insert_air_quality(data)

    if not result:
        raise HTTPException(status_code=500, detail="Failed to create measurement")

    return result
