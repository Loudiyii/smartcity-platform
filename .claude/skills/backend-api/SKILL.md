# Skill: Backend API (FastAPI)

## Purpose
Develop and maintain FastAPI backend services for the Smart City platform, including REST API routes, Pydantic models, Supabase integration, and authentication.

## When to Use
- Creating new API endpoints
- Modifying existing routes in `backend/app/api/v1/`
- Working with Pydantic models for validation
- Integrating with Supabase database
- Implementing authentication/authorization
- Adding business logic in services layer

## Architecture Overview

```
backend/app/
├── main.py                    # FastAPI app entry point
├── config.py                  # Environment variables & settings
├── dependencies.py            # Dependency injection
│
├── api/v1/                    # API routes (v1)
│   ├── air_quality.py
│   ├── weather.py
│   ├── sensors.py
│   ├── predictions.py
│   ├── auth.py
│   └── reports.py
│
├── services/                  # Business logic layer
│   ├── supabase_service.py
│   ├── air_quality_service.py
│   ├── weather_service.py
│   └── alert_service.py
│
├── models/                    # Pydantic models
│   ├── air_quality.py
│   ├── sensor.py
│   └── prediction.py
│
├── ml/                        # Machine Learning
│   ├── predictor.py
│   └── anomaly_detector.py
│
└── utils/
    ├── logger.py
    └── validators.py
```

## Core Patterns

### 1. FastAPI Route Definition

```python
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
from app.models.air_quality import AirQualityResponse, AirQualityCreate
from app.services.air_quality_service import AirQualityService
from app.dependencies import get_air_quality_service

router = APIRouter(prefix="/api/v1/air-quality", tags=["air-quality"])

@router.get("/current", response_model=AirQualityResponse)
async def get_current_air_quality(
    city: str = Query(..., description="City name"),
    service: AirQualityService = Depends(get_air_quality_service)
):
    """
    Get current air quality data for a specific city.

    - **city**: City name (e.g., 'paris')
    - Returns: Current AQI and pollutant levels
    """
    try:
        data = await service.get_current_data(city)
        if not data:
            raise HTTPException(status_code=404, detail=f"No data found for {city}")
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=List[AirQualityResponse])
async def get_air_quality_history(
    city: str = Query(...),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(100, le=1000),
    service: AirQualityService = Depends(get_air_quality_service)
):
    """Get historical air quality data with optional date filtering."""
    return await service.get_history(city, start_date, end_date, limit)

@router.post("/measurements", response_model=AirQualityResponse, status_code=201)
async def create_measurement(
    measurement: AirQualityCreate,
    service: AirQualityService = Depends(get_air_quality_service)
):
    """Create a new air quality measurement (authenticated only)."""
    return await service.create_measurement(measurement)
```

### 2. Pydantic Models

```python
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class LocationModel(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    name: Optional[str] = None

class AirQualityBase(BaseModel):
    source: str = Field(..., max_length=50, description="'api' or 'sensor_xxx'")
    city: Optional[str] = Field(None, max_length=100)
    location: Optional[LocationModel] = None

    # Pollutants
    aqi: Optional[int] = Field(None, ge=0, le=500)
    pm25: Optional[float] = Field(None, ge=0)
    pm10: Optional[float] = Field(None, ge=0)
    no2: Optional[float] = Field(None, ge=0)
    o3: Optional[float] = Field(None, ge=0)
    so2: Optional[float] = Field(None, ge=0)

    @validator('pm25', 'pm10', 'no2')
    def validate_pollutant(cls, v):
        if v is not None and v < 0:
            raise ValueError('Pollutant values must be positive')
        return v

class AirQualityCreate(AirQualityBase):
    timestamp: Optional[datetime] = None

class AirQualityResponse(AirQualityBase):
    id: int
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True
```

### 3. Service Layer Pattern

```python
from supabase import Client
from typing import List, Optional
from datetime import datetime, timedelta
from app.models.air_quality import AirQualityCreate, AirQualityResponse

class AirQualityService:
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.table_name = "air_quality_measurements"

    async def get_current_data(self, city: str) -> Optional[AirQualityResponse]:
        """Get most recent air quality data for a city."""
        result = self.supabase.table(self.table_name) \
            .select("*") \
            .eq("city", city) \
            .order("timestamp", desc=True) \
            .limit(1) \
            .execute()

        if result.data:
            return AirQualityResponse(**result.data[0])
        return None

    async def get_history(
        self,
        city: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AirQualityResponse]:
        """Get historical data with optional date filtering."""
        query = self.supabase.table(self.table_name) \
            .select("*") \
            .eq("city", city)

        if start_date:
            query = query.gte("timestamp", start_date.isoformat())
        if end_date:
            query = query.lte("timestamp", end_date.isoformat())

        result = query.order("timestamp", desc=True).limit(limit).execute()

        return [AirQualityResponse(**item) for item in result.data]

    async def create_measurement(self, measurement: AirQualityCreate) -> AirQualityResponse:
        """Insert new measurement into database."""
        data = measurement.model_dump(exclude_none=True)

        result = self.supabase.table(self.table_name) \
            .insert(data) \
            .execute()

        return AirQualityResponse(**result.data[0])

    async def get_average_pm25(self, hours: int = 24) -> float:
        """Calculate average PM2.5 over last N hours."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        result = self.supabase.rpc(
            'get_average_pm25',
            {'hours': hours}
        ).execute()

        return result.data if result.data else 0.0
```

### 4. Supabase Client Configuration

```python
# app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str

    # External APIs
    OPENWEATHER_API_KEY: str
    AQICN_API_TOKEN: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Environment
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

# app/dependencies.py
from supabase import create_client, Client
from app.config import get_settings

def get_supabase_client() -> Client:
    settings = get_settings()
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def get_air_quality_service():
    supabase = get_supabase_client()
    from app.services.air_quality_service import AirQualityService
    return AirQualityService(supabase)
```

### 5. Authentication with JWT

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.dependencies import get_supabase_client

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Verify JWT token and return current user."""
    supabase = get_supabase_client()

    try:
        user = supabase.auth.get_user(credentials.credentials)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

# Usage in protected routes
@router.post("/admin/settings")
async def update_settings(
    settings: dict,
    current_user = Depends(get_current_user)
):
    """Protected route - requires authentication."""
    # Only authenticated users can access
    pass
```

### 6. Error Handling

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": exc.body
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all for unhandled exceptions."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

### 7. CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://smartcity.example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 8. Main Application Setup

```python
# app/main.py
from fastapi import FastAPI
from app.api.v1 import air_quality, weather, sensors, predictions, auth
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Smart City API",
    description="Air quality and mobility monitoring platform",
    version="1.0.0"
)

# Include routers
app.include_router(air_quality.router)
app.include_router(weather.router)
app.include_router(sensors.router)
app.include_router(predictions.router)
app.include_router(auth.router)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }

@app.get("/")
async def root():
    return {"message": "Smart City API v1.0.0"}
```

## Best Practices

### Code Organization
- Keep routes thin - delegate logic to services
- Use Pydantic models for all request/response validation
- Implement dependency injection for services
- Separate concerns: routes → services → database

### Database Queries
- Use Supabase RPC for complex queries
- Leverage PostgreSQL functions defined in database
- Always apply filters before ordering and limiting
- Use select("*") or specify columns explicitly

### Error Handling
- Always catch exceptions in route handlers
- Return appropriate HTTP status codes
- Provide meaningful error messages
- Log errors with context

### Performance
- Use `async def` for all route handlers
- Implement caching for external API calls
- Use database indexes for frequently queried fields
- Limit response sizes with pagination

### Security
- Never commit `.env` file
- Use environment variables for secrets
- Validate all user inputs with Pydantic
- Apply rate limiting on public endpoints
- Enable CORS only for trusted origins

## Common Tasks

### Adding a New Endpoint
1. Define Pydantic models in `app/models/`
2. Create service methods in `app/services/`
3. Add route in `app/api/v1/`
4. Register router in `app/main.py`
5. Test with `/docs` interactive API

### Querying Supabase
```python
# Simple select
result = supabase.table('table_name').select('*').execute()

# With filters
result = supabase.table('table_name') \
    .select('*') \
    .eq('column', 'value') \
    .gte('timestamp', date) \
    .order('created_at', desc=True) \
    .limit(10) \
    .execute()

# Insert
result = supabase.table('table_name').insert(data).execute()

# Update
result = supabase.table('table_name') \
    .update({'status': 'active'}) \
    .eq('id', record_id) \
    .execute()
```

### Calling External APIs
```python
import httpx

async def fetch_external_api(url: str, params: dict):
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, timeout=10.0)
        response.raise_for_status()
        return response.json()
```

## Testing

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_current_air_quality():
    response = client.get("/api/v1/air-quality/current?city=paris")
    assert response.status_code == 200
    assert "aqi" in response.json()

def test_create_measurement():
    data = {
        "source": "sensor_001",
        "city": "paris",
        "pm25": 25.5
    }
    response = client.post("/api/v1/air-quality/measurements", json=data)
    assert response.status_code == 201
```

## References
- FastAPI Documentation: https://fastapi.tiangolo.com/
- Supabase Python Client: https://supabase.com/docs/reference/python
- Pydantic: https://docs.pydantic.dev/

## Trade-offs and Considerations

**Pros:**
- Fast development with FastAPI auto-documentation
- Type safety with Pydantic models
- Supabase handles auth and RLS automatically
- Async support for high performance

**Cons:**
- Supabase client is not fully async (use sync in async context)
- Need to manage connection pooling manually
- External API rate limits require caching strategy

**When to use services vs. routes:**
- Routes: HTTP handling, validation, response formatting
- Services: Business logic, database operations, external API calls
