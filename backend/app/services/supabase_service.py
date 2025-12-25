"""Supabase service for database operations"""

from supabase import Client
from typing import List, Optional, Dict
from datetime import datetime


class SupabaseService:
    """Service for Supabase database operations."""

    def __init__(self, client: Client):
        self.client = client

    async def insert_air_quality(self, data: dict) -> dict:
        """Insert air quality measurement."""
        result = self.client.table('air_quality_measurements').insert(data).execute()
        return result.data[0] if result.data else None

    async def get_current_air_quality(self, city: str) -> Optional[dict]:
        """Get most recent air quality data for a city."""
        result = self.client.table('air_quality_measurements') \
            .select('*') \
            .eq('city', city) \
            .order('timestamp', desc=True) \
            .limit(1) \
            .execute()
        return result.data[0] if result.data else None

    async def get_air_quality_history(
        self,
        city: str,
        limit: int = 100
    ) -> List[dict]:
        """Get historical air quality data."""
        result = self.client.table('air_quality_measurements') \
            .select('*') \
            .eq('city', city) \
            .order('timestamp', desc=True) \
            .limit(limit) \
            .execute()
        return result.data

    async def insert_weather(self, data: dict) -> dict:
        """Insert weather data."""
        result = self.client.table('weather_data').insert(data).execute()
        return result.data[0] if result.data else None

    async def get_sensor_metadata(self) -> List[dict]:
        """Get all sensor metadata."""
        result = self.client.table('sensor_metadata').select('*').execute()
        return result.data
