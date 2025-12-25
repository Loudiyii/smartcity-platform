# Skill: External APIs Integration

## Purpose
Integrate with third-party APIs for real-time air quality data (AQICN) and weather information (OpenWeatherMap) to complement IoT sensor data.

## When to Use
- Fetching real-time air quality data from public sources
- Retrieving weather data for correlation analysis
- Implementing data fallback mechanisms
- Enriching local sensor data with regional context

## API Overview

### 1. AQICN (Air Quality Index China - World Air Quality Index)
- **Purpose:** Global air quality data
- **Coverage:** 12,000+ stations worldwide
- **Data:** AQI, PM2.5, PM10, NO2, O3, SO2
- **Update Frequency:** Hourly
- **Cost:** Free tier available

### 2. OpenWeatherMap
- **Purpose:** Weather conditions and forecasts
- **Coverage:** Global
- **Data:** Temperature, humidity, pressure, wind
- **Update Frequency:** Every 10 minutes
- **Cost:** Free tier (60 calls/min)

## API Configuration

### Environment Variables

```bash
# .env
AQICN_API_TOKEN=your_aqicn_token_here
OPENWEATHER_API_KEY=your_openweather_key_here
```

### Getting API Keys

**AQICN:**
1. Visit https://aqicn.org/api/
2. Request free token (instant)
3. No credit card required

**OpenWeatherMap:**
1. Visit https://openweathermap.org/api
2. Sign up for free account
3. Get API key from dashboard

## Implementation

### 1. AQICN Service

```python
# backend/app/services/aqicn_service.py
import httpx
from typing import Optional, Dict
from app.config import get_settings

settings = get_settings()

class AQICNService:
    """Service for fetching air quality data from AQICN API."""

    BASE_URL = "https://api.waqi.info"

    def __init__(self):
        self.api_token = settings.AQICN_API_TOKEN

    async def get_city_data(self, city: str) -> Optional[Dict]:
        """
        Fetch current air quality data for a city.

        Args:
            city: City name (e.g., 'paris', 'london', 'beijing')

        Returns:
            Dict with air quality data or None if error
        """
        url = f"{self.BASE_URL}/feed/{city}/"
        params = {"token": self.api_token}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()

                if data.get("status") != "ok":
                    print(f"AQICN API error: {data}")
                    return None

                return self._parse_response(data["data"])

            except httpx.HTTPError as e:
                print(f"Error fetching AQICN data: {e}")
                return None

    def _parse_response(self, data: Dict) -> Dict:
        """
        Parse AQICN response into standard format.

        AQICN Response Structure:
        {
          "aqi": 42,
          "iaqi": {
            "pm25": {"v": 29},
            "pm10": {"v": 35},
            "no2": {"v": 15},
            "o3": {"v": 22}
          },
          "city": {"name": "Paris"},
          "time": {"iso": "2024-12-24T10:00:00Z"}
        }
        """
        iaqi = data.get("iaqi", {})

        return {
            "source": "api",
            "city": data.get("city", {}).get("name", "unknown"),
            "location": self._extract_location(data),
            "aqi": data.get("aqi"),
            "pm25": iaqi.get("pm25", {}).get("v"),
            "pm10": iaqi.get("pm10", {}).get("v"),
            "no2": iaqi.get("no2", {}).get("v"),
            "o3": iaqi.get("o3", {}).get("v"),
            "so2": iaqi.get("so2", {}).get("v"),
            "timestamp": data.get("time", {}).get("iso")
        }

    def _extract_location(self, data: Dict) -> Dict:
        """Extract location coordinates from response."""
        city_data = data.get("city", {})
        geo = city_data.get("geo", [])

        if len(geo) >= 2:
            return {
                "lat": geo[0],
                "lon": geo[1],
                "name": city_data.get("name")
            }
        return {}

    async def get_station_data(self, station_id: int) -> Optional[Dict]:
        """
        Fetch data from specific monitoring station.

        Args:
            station_id: AQICN station ID

        Returns:
            Air quality data dict
        """
        url = f"{self.BASE_URL}/feed/@{station_id}/"
        params = {"token": self.api_token}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "ok":
                return self._parse_response(data["data"])
            return None

    async def search_stations(self, keyword: str) -> list:
        """
        Search for monitoring stations by keyword.

        Args:
            keyword: Search term (city name, location)

        Returns:
            List of station results
        """
        url = f"{self.BASE_URL}/search/"
        params = {"token": self.api_token, "keyword": keyword}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "ok":
                return data.get("data", [])
            return []
```

### 2. OpenWeatherMap Service

```python
# backend/app/services/openweather_service.py
import httpx
from typing import Optional, Dict
from app.config import get_settings

settings = get_settings()

class OpenWeatherService:
    """Service for fetching weather data from OpenWeatherMap API."""

    BASE_URL = "https://api.openweathermap.org/data/2.5"

    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY

    async def get_current_weather(self, city: str) -> Optional[Dict]:
        """
        Fetch current weather data for a city.

        Args:
            city: City name (e.g., 'Paris,FR')

        Returns:
            Weather data dict
        """
        url = f"{self.BASE_URL}/weather"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"  # Celsius, m/s
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()

                return self._parse_response(data)

            except httpx.HTTPError as e:
                print(f"Error fetching weather data: {e}")
                return None

    def _parse_response(self, data: Dict) -> Dict:
        """
        Parse OpenWeatherMap response.

        Response Structure:
        {
          "main": {
            "temp": 15.3,
            "humidity": 72,
            "pressure": 1013
          },
          "wind": {
            "speed": 3.2,
            "deg": 180
          },
          "name": "Paris"
        }
        """
        main = data.get("main", {})
        wind = data.get("wind", {})

        return {
            "city": data.get("name"),
            "temperature": main.get("temp"),
            "humidity": main.get("humidity"),
            "pressure": main.get("pressure"),
            "wind_speed": wind.get("speed"),
            "wind_direction": wind.get("deg"),
            "timestamp": None  # Will be set by backend
        }

    async def get_weather_by_coords(self, lat: float, lon: float) -> Optional[Dict]:
        """Fetch weather data by geographic coordinates."""
        url = f"{self.BASE_URL}/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            return self._parse_response(response.json())

    async def get_forecast(self, city: str, days: int = 5) -> Optional[list]:
        """
        Fetch weather forecast.

        Args:
            city: City name
            days: Number of days (max 5 for free tier)

        Returns:
            List of forecast data points (3-hour intervals)
        """
        url = f"{self.BASE_URL}/forecast"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric",
            "cnt": days * 8  # 8 data points per day (3h intervals)
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()

            forecasts = []
            for item in data.get("list", []):
                forecasts.append({
                    "timestamp": item.get("dt_txt"),
                    "temperature": item["main"]["temp"],
                    "humidity": item["main"]["humidity"],
                    "wind_speed": item["wind"]["speed"],
                    "description": item["weather"][0]["description"]
                })

            return forecasts
```

### 3. API Route Integration

```python
# backend/app/api/v1/external_data.py
from fastapi import APIRouter, HTTPException, Depends
from app.services.aqicn_service import AQICNService
from app.services.openweather_service import OpenWeatherService
from app.services.supabase_service import SupabaseService

router = APIRouter(prefix="/api/v1/external", tags=["external-data"])

@router.get("/air-quality/{city}")
async def fetch_air_quality(
    city: str,
    save_to_db: bool = True
):
    """
    Fetch air quality data from AQICN and optionally save to database.
    """
    aqicn_service = AQICNService()
    data = await aqicn_service.get_city_data(city)

    if not data:
        raise HTTPException(status_code=404, detail=f"No data found for {city}")

    if save_to_db:
        # Save to database
        supabase = SupabaseService()
        await supabase.insert_air_quality(data)

    return data

@router.get("/weather/{city}")
async def fetch_weather(
    city: str,
    save_to_db: bool = True
):
    """
    Fetch weather data from OpenWeatherMap.
    """
    weather_service = OpenWeatherService()
    data = await weather_service.get_current_weather(city)

    if not data:
        raise HTTPException(status_code=404, detail=f"No weather data for {city}")

    if save_to_db:
        supabase = SupabaseService()
        await supabase.insert_weather(data)

    return data
```

### 4. Scheduled Data Collection

```python
# backend/app/schedulers/data_collector.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.aqicn_service import AQICNService
from app.services.openweather_service import OpenWeatherService
from app.services.supabase_service import SupabaseService

scheduler = AsyncIOScheduler()

CITIES = ["paris", "lyon", "marseille"]

async def collect_air_quality_data():
    """Collect air quality data for all cities."""
    aqicn = AQICNService()
    supabase = SupabaseService()

    for city in CITIES:
        try:
            data = await aqicn.get_city_data(city)
            if data:
                await supabase.insert_air_quality(data)
                print(f"Collected air quality data for {city}")
        except Exception as e:
            print(f"Error collecting data for {city}: {e}")

async def collect_weather_data():
    """Collect weather data for all cities."""
    weather = OpenWeatherService()
    supabase = SupabaseService()

    for city in CITIES:
        try:
            data = await weather.get_current_weather(city)
            if data:
                await supabase.insert_weather(data)
                print(f"Collected weather data for {city}")
        except Exception as e:
            print(f"Error collecting weather for {city}: {e}")

# Schedule jobs
scheduler.add_job(collect_air_quality_data, 'interval', hours=1)  # Every hour
scheduler.add_job(collect_weather_data, 'interval', hours=1)

def start_scheduler():
    """Start the background scheduler."""
    scheduler.start()
    print("Data collection scheduler started")
```

## Caching Strategy

```python
# backend/app/utils/cache.py
from functools import lru_cache
import time

def cached_with_ttl(ttl_seconds: int):
    """
    Decorator for caching with time-to-live.

    Args:
        ttl_seconds: Cache expiration time in seconds
    """
    def decorator(func):
        cache = {}

        async def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            now = time.time()

            if key in cache:
                result, timestamp = cache[key]
                if now - timestamp < ttl_seconds:
                    return result

            result = await func(*args, **kwargs)
            cache[key] = (result, now)
            return result

        return wrapper
    return decorator

# Usage
@cached_with_ttl(300)  # Cache for 5 minutes
async def get_cached_air_quality(city: str):
    aqicn = AQICNService()
    return await aqicn.get_city_data(city)
```

## Error Handling & Retry Logic

```python
# backend/app/utils/retry.py
import asyncio
from typing import Callable

async def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0
):
    """
    Retry function with exponential backoff.

    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries (doubles each time)
    """
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise

            delay = base_delay * (2 ** attempt)
            print(f"Retry {attempt + 1}/{max_retries} after {delay}s: {e}")
            await asyncio.sleep(delay)
```

## Best Practices

### API Usage
- Respect rate limits (60 calls/min for OpenWeather free tier)
- Cache responses to minimize API calls
- Implement exponential backoff for retries
- Monitor API quota usage

### Data Validation
- Validate API responses before saving
- Handle missing or null values
- Check data freshness (timestamp)
- Log invalid responses for debugging

### Error Handling
- Graceful degradation (use cached data if API fails)
- Fallback to alternative data sources
- Alert on repeated API failures
- Log all errors with context

### Security
- Never commit API keys to version control
- Use environment variables for credentials
- Rotate API keys periodically
- Monitor for unusual API usage

## Common Tasks

### Testing API Connections
```python
async def test_apis():
    aqicn = AQICNService()
    weather = OpenWeatherService()

    air_data = await aqicn.get_city_data("paris")
    weather_data = await weather.get_current_weather("Paris,FR")

    print(f"AQICN: {air_data}")
    print(f"Weather: {weather_data}")
```

### Monitoring API Health
```python
async def check_api_health():
    """Check if external APIs are responding."""
    health = {}

    try:
        aqicn = AQICNService()
        await aqicn.get_city_data("paris")
        health["aqicn"] = "healthy"
    except:
        health["aqicn"] = "unhealthy"

    try:
        weather = OpenWeatherService()
        await weather.get_current_weather("Paris")
        health["openweather"] = "healthy"
    except:
        health["openweather"] = "unhealthy"

    return health
```

## References
- AQICN API Docs: https://aqicn.org/json-api/doc/
- OpenWeatherMap API: https://openweathermap.org/api
- HTTPX Async: https://www.python-httpx.org/

## Trade-offs

**Real-time vs. Cached:**
- Real-time: Always fresh, higher API costs
- Cached: Lower costs, slightly stale data

**Single vs. Multiple Sources:**
- Single: Simpler, single point of failure
- Multiple: Redundancy, data validation

**Polling vs. Webhooks:**
- Polling: Simpler, predictable costs
- Webhooks: Real-time, fewer calls (not supported by these APIs)
