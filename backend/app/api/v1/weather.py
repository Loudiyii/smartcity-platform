"""Weather API routes"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.models.weather import WeatherCreate, WeatherResponse
from app.dependencies import get_supabase_client
from app.services.supabase_service import SupabaseService

router = APIRouter(prefix="/api/v1/weather", tags=["weather"])


@router.post("/", response_model=WeatherResponse, status_code=201)
async def create_weather_data(weather: WeatherCreate):
    """Create new weather data entry."""
    supabase = get_supabase_client()
    service = SupabaseService(supabase)

    data = weather.model_dump(exclude_none=True)
    result = await service.insert_weather(data)

    if not result:
        raise HTTPException(status_code=500, detail="Failed to create weather data")

    return result
