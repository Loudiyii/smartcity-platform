# Skill: Mobility Data (IDFM/PRIM APIs)

## Purpose
Integrate with Île-de-France Mobilités (IDFM/PRIM) APIs to collect real-time mobility data including traffic disruptions, Vélib availability, and transit information for correlation with air quality data.

## When to Use
- Fetching traffic disruptions and incidents
- Retrieving Vélib station availability
- Getting transit stop information
- Integrating IDFM/PRIM API endpoints
- Caching mobility data

## API Overview

### IDFM/PRIM Platform
- **Provider:** Île-de-France Mobilités
- **Coverage:** Paris metropolitan area
- **APIs:** Traffic, Vélib, Transit, Disruptions
- **Authentication:** API key (header)
- **Format:** JSON REST API
- **Rate Limits:** Varies by endpoint

## Configuration

### Environment Variables

```bash
# .env
IDFM_API_KEY=your_prim_api_key_here
IDFM_BASE_URL=https://prim.iledefrance-mobilites.fr/marketplace
```

### Settings Configuration

```python
# backend/app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # IDFM Configuration
    idfm_api_key: str
    idfm_base_url: str = "https://prim.iledefrance-mobilites.fr/marketplace"

    class Config:
        env_file = ".env"
```

## Service Implementation

### 1. Mobility Service Class

```python
# backend/app/services/mobility_service.py
import httpx
from typing import List, Optional, Dict
from app.config import get_settings
from app.models.mobility import TrafficDisruption, VelibStation, TransitStop

settings = get_settings()

class MobilityService:
    """Service for Île-de-France Mobilités (PRIM) APIs."""

    def __init__(self):
        self.base_url = settings.idfm_base_url
        self.api_key = settings.idfm_api_key
        self.headers = {
            "apikey": self.api_key,
            "Accept": "application/json"
        }

    async def get_traffic_disruptions(
        self,
        severity: Optional[str] = None,
        active_only: bool = True
    ) -> List[TrafficDisruption]:
        """
        Fetch current traffic disruptions.

        Args:
            severity: Filter by severity (low, medium, high)
            active_only: Only return active disruptions

        Returns:
            List of traffic disruption objects
        """
        url = f"{self.base_url}/general-message"

        params = {}
        if severity:
            params['severity'] = severity

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()

                disruptions = []
                for item in data.get('Siri', {}).get('ServiceDelivery', {}).get('GeneralMessageDelivery', [{}])[0].get('InfoMessage', []):
                    disruption = self._parse_disruption(item)
                    if active_only and not disruption.is_active:
                        continue
                    disruptions.append(disruption)

                return disruptions

            except httpx.HTTPError as e:
                print(f"Error fetching traffic disruptions: {e}")
                return []

    async def get_velib_availability(
        self,
        station_id: Optional[str] = None,
        limit: int = 50
    ) -> List[VelibStation]:
        """
        Fetch Vélib station availability.

        Args:
            station_id: Specific station ID (optional)
            limit: Maximum number of stations to return

        Returns:
            List of Vélib station objects with availability
        """
        # Note: Actual endpoint may vary, adjust based on IDFM docs
        url = f"{self.base_url}/bike-sharing"

        params = {'limit': limit}
        if station_id:
            params['station_id'] = station_id

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()

                stations = []
                for item in data.get('stations', []):
                    station = VelibStation(
                        station_id=item['stationCode'],
                        name=item['name'],
                        num_bikes_available=item.get('nbBike', 0),
                        num_docks_available=item.get('nbFreeDock', 0),
                        latitude=item['coordonnees_geo']['lat'],
                        longitude=item['coordonnees_geo']['lon'],
                        is_installed=item.get('is_installed', 1) == 1,
                        is_returning=item.get('is_returning', 1) == 1,
                        is_renting=item.get('is_renting', 1) == 1,
                        last_reported=item.get('dueDate')
                    )
                    stations.append(station)

                return stations

            except httpx.HTTPError as e:
                print(f"Error fetching Vélib data: {e}")
                return []

    async def get_transit_stops(
        self,
        limit: int = 50,
        zone_id: Optional[str] = None
    ) -> List[TransitStop]:
        """
        Fetch transit stop areas for mapping.

        Args:
            limit: Maximum number of stops
            zone_id: Filter by zone (optional)

        Returns:
            List of transit stop objects
        """
        url = f"{self.base_url}/stop-monitoring"

        params = {'limit': limit}
        if zone_id:
            params['zone_id'] = zone_id

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()

                stops = []
                for item in data.get('stops', []):
                    stop = TransitStop(
                        stop_id=item['stop_id'],
                        stop_name=item['stop_name'],
                        stop_lat=item['stop_lat'],
                        stop_lon=item['stop_lon'],
                        zone_id=item.get('zone_id'),
                        location_type=item.get('location_type', 0)
                    )
                    stops.append(stop)

                return stops

            except httpx.HTTPError as e:
                print(f"Error fetching transit stops: {e}")
                return []

    def _parse_disruption(self, item: Dict) -> TrafficDisruption:
        """Parse raw API disruption into structured model."""
        info_message = item.get('InfoMessage', {})
        content = info_message.get('Content', {})

        return TrafficDisruption(
            disruption_id=item.get('RecordedAtTime', ''),
            line_id=content.get('LineRef', ''),
            line_name=content.get('LineName', ''),
            severity=content.get('Severity', 'unknown'),
            message=content.get('Message', [{}])[0].get('MessageText', ''),
            start_time=info_message.get('ValidUntilTime'),
            end_time=info_message.get('ValidUntilTime'),
            is_active=True
        )
```

## Pydantic Models

### 1. Traffic Disruption Model

```python
# backend/app/models/mobility.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TrafficDisruption(BaseModel):
    """Traffic disruption/incident information."""
    disruption_id: str
    line_id: Optional[str] = None
    line_name: Optional[str] = None
    severity: str = Field(..., description="low, medium, high, critical")
    message: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 2. Vélib Station Model

```python
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
        return self.num_bikes_available + self.num_docks_available

    @property
    def availability_percent(self) -> float:
        if self.capacity == 0:
            return 0.0
        return (self.num_bikes_available / self.capacity) * 100
```

### 3. Transit Stop Model

```python
class TransitStop(BaseModel):
    """Transit stop/station information."""
    stop_id: str
    stop_name: str
    stop_lat: float = Field(ge=-90, le=90)
    stop_lon: float = Field(ge=-180, le=180)
    zone_id: Optional[str] = None
    location_type: int = 0  # 0=stop, 1=station
```

## API Routes

### Mobility Endpoints

```python
# backend/app/api/v1/mobility.py
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from app.services.mobility_service import MobilityService
from app.models.mobility import TrafficDisruption, VelibStation, TransitStop

router = APIRouter(prefix="/api/v1/mobility", tags=["mobility"])

def get_mobility_service():
    return MobilityService()

@router.get("/traffic-disruptions", response_model=List[TrafficDisruption])
async def get_traffic_disruptions(
    severity: Optional[str] = Query(None, regex="^(low|medium|high|critical)$"),
    active_only: bool = True,
    service: MobilityService = Depends(get_mobility_service)
):
    """Get current traffic disruptions."""
    disruptions = await service.get_traffic_disruptions(severity, active_only)
    return disruptions

@router.get("/velib/stations", response_model=List[VelibStation])
async def get_velib_stations(
    station_id: Optional[str] = None,
    limit: int = Query(50, le=200),
    service: MobilityService = Depends(get_mobility_service)
):
    """Get Vélib station availability."""
    stations = await service.get_velib_availability(station_id, limit)
    return stations

@router.get("/transit/stops", response_model=List[TransitStop])
async def get_transit_stops(
    limit: int = Query(50, le=200),
    zone_id: Optional[str] = None,
    service: MobilityService = Depends(get_mobility_service)
):
    """Get transit stop areas for mapping."""
    stops = await service.get_transit_stops(limit, zone_id)
    return stops

@router.get("/velib/stats")
async def get_velib_stats(
    service: MobilityService = Depends(get_mobility_service)
):
    """Get aggregated Vélib statistics."""
    stations = await service.get_velib_availability(limit=1000)

    total_stations = len(stations)
    total_bikes = sum(s.num_bikes_available for s in stations)
    total_docks = sum(s.num_docks_available for s in stations)
    avg_availability = sum(s.availability_percent for s in stations) / total_stations if total_stations > 0 else 0

    return {
        "total_stations": total_stations,
        "total_bikes_available": total_bikes,
        "total_docks_available": total_docks,
        "average_availability_percent": round(avg_availability, 2)
    }
```

## Caching Strategy

### Redis Cache Pattern

```python
from functools import lru_cache
import time
from typing import Optional

class CachedMobilityService(MobilityService):
    """Mobility service with caching."""

    def __init__(self):
        super().__init__()
        self._cache = {}
        self._cache_ttl = 60  # 60 seconds

    async def get_traffic_disruptions_cached(self, **kwargs):
        cache_key = f"disruptions_{kwargs}"

        if cache_key in self._cache:
            data, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                return data

        data = await self.get_traffic_disruptions(**kwargs)
        self._cache[cache_key] = (data, time.time())
        return data
```

## Error Handling & Retry

### Retry with Exponential Backoff

```python
import asyncio

async def fetch_with_retry(
    func,
    max_retries: int = 3,
    base_delay: float = 1.0
):
    """Retry API call with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return await func()
        except httpx.HTTPError as e:
            if attempt == max_retries - 1:
                raise

            delay = base_delay * (2 ** attempt)
            print(f"Retry {attempt + 1}/{max_retries} after {delay}s: {e}")
            await asyncio.sleep(delay)
```

## Best Practices

### API Usage
- Cache responses (60s TTL for real-time data)
- Respect rate limits
- Use pagination for large datasets
- Implement retry logic with backoff

### Data Validation
- Validate all API responses with Pydantic
- Handle missing/null values gracefully
- Check data freshness timestamps
- Log invalid responses

### Performance
- Use async HTTP client (httpx)
- Batch requests when possible
- Limit response sizes
- Monitor API quota usage

## Common Tasks

### Fetching Active Disruptions

```python
service = MobilityService()
disruptions = await service.get_traffic_disruptions(
    severity="high",
    active_only=True
)
```

### Monitoring Vélib Station

```python
# Get specific station
station = await service.get_velib_availability(station_id="16107")

# Check availability
if station[0].num_bikes_available < 3:
    print("Low bike availability!")
```

### Saving to Database

```python
from app.services.supabase_service import SupabaseService

supabase = SupabaseService()

# Save disruptions
for disruption in disruptions:
    await supabase.insert_traffic_disruption(disruption.model_dump())
```

## References
- IDFM API Docs: https://prim.iledefrance-mobilites.fr/
- HTTPX Async: https://www.python-httpx.org/
- Pydantic: https://docs.pydantic.dev/

## Trade-offs

**Real-time vs. Cached:**
- Real-time: Always current, higher API costs
- Cached: Lower costs, slight staleness (acceptable for 60s)

**Pagination:**
- Small limits: More requests, fresh data
- Large limits: Fewer requests, slower responses

**Error Handling:**
- Strict: Fail fast, easier debugging
- Graceful: Better UX, may hide issues
