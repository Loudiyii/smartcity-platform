"""
Smart City Platform - Main FastAPI Application
Phase 1 MVP - Sprint 1
Updated: 2025-12-28 23:45
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import threading
import time

print("[MAIN] Importing routers...")
from app.api.v1 import air_quality, weather, sensors, auth, mobility
print("[MAIN] Core routers imported (air_quality, weather, sensors, auth, mobility)")

from app.api.v1 import predictions, anomalies, alerts, analytics, reports, mobility_impact
print("[MAIN] Phase 2 routers imported (predictions, anomalies, alerts, analytics, reports, mobility_impact)")

from app.config import get_settings, get_supabase_client

settings = get_settings()
print(f"[MAIN] Settings loaded, environment: {settings.ENVIRONMENT}")


def init_sensor_metadata():
    """Initialize sensor metadata in Supabase."""
    from datetime import datetime

    SENSORS = [
        {"sensor_id": "SENSOR_001", "name": "Paris Centre", "lat": 48.8566, "lon": 2.3522},
        {"sensor_id": "SENSOR_002", "name": "Paris Nord", "lat": 48.8738, "lon": 2.2950},
        {"sensor_id": "SENSOR_003", "name": "Paris Sud", "lat": 48.8414, "lon": 2.3209},
        {"sensor_id": "SENSOR_004", "name": "Paris Est", "lat": 48.8467, "lon": 2.3775},
        {"sensor_id": "SENSOR_005", "name": "Paris Ouest", "lat": 48.8656, "lon": 2.2879}
    ]

    try:
        supabase = get_supabase_client()
        for s in SENSORS:
            try:
                existing = supabase.table('sensor_metadata').select('sensor_id').eq('sensor_id', s['sensor_id']).execute()
                if not existing.data:
                    supabase.table('sensor_metadata').insert({
                        'sensor_id': s['sensor_id'],
                        'name': f"{s['name']} Air Quality Monitor",
                        'latitude': s['lat'],
                        'longitude': s['lon'],
                        'location_description': s['name'],
                        'sensor_type': 'air_quality',
                        'status': 'active',
                        'installed_at': datetime.utcnow().isoformat()
                    }).execute()
                    print(f"[IOT] Registered sensor: {s['sensor_id']}")
            except:
                pass
    except Exception as e:
        print(f"[IOT] Sensor metadata init failed: {e}")


def run_iot_worker():
    """Background worker to simulate IoT sensors."""
    from app.simulators.iot_sensor import IoTSensor

    print("[IOT] Starting IoT sensor worker...")

    # Initialize metadata first
    init_sensor_metadata()

    SENSORS = [
        {"sensor_id": "SENSOR_001", "location": {"lat": 48.8566, "lon": 2.3522, "name": "Paris Centre"}},
        {"sensor_id": "SENSOR_002", "location": {"lat": 48.8738, "lon": 2.2950, "name": "Paris Nord"}},
        {"sensor_id": "SENSOR_003", "location": {"lat": 48.8414, "lon": 2.3209, "name": "Paris Sud"}},
        {"sensor_id": "SENSOR_004", "location": {"lat": 48.8467, "lon": 2.3775, "name": "Paris Est"}},
        {"sensor_id": "SENSOR_005", "location": {"lat": 48.8656, "lon": 2.2879, "name": "Paris Ouest"}}
    ]

    def run_sensor(config):
        api_url = f"http://localhost:{settings.PORT or 8080}/api/v1/air-quality/measurements"
        sensor = IoTSensor(sensor_id=config["sensor_id"], location=config["location"], api_url=api_url)
        sensor.run(interval_seconds=900)  # 15 minutes

    for sensor_config in SENSORS:
        thread = threading.Thread(target=run_sensor, args=(sensor_config,), daemon=True)
        thread.start()
        time.sleep(1)

    print("[IOT] All 5 sensors started (15min interval)")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for startup and shutdown."""
    # Startup
    print("Smart City API starting...")
    print(f"Environment: {settings.ENVIRONMENT}")

    # Start IoT worker in production
    if settings.ENVIRONMENT == "production":
        worker_thread = threading.Thread(target=run_iot_worker, daemon=True)
        worker_thread.start()
        print("[IOT] Worker thread started")

    yield

    # Shutdown
    print("Smart City API shutting down...")


app = FastAPI(
    title="Smart City API",
    description="Air quality and mobility monitoring platform - Phase 1 MVP",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(air_quality.router)
app.include_router(weather.router)
app.include_router(sensors.router)
app.include_router(auth.router)
app.include_router(mobility.router)
print(f"[MAIN] Mobility router routes: {[route.path for route in mobility.router.routes]}")
app.include_router(predictions.router)
app.include_router(anomalies.router)
app.include_router(alerts.router)
app.include_router(analytics.router)
app.include_router(reports.router)
app.include_router(mobility_impact.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Smart City API",
        "version": "1.0.0",
        "status": "running",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "database": "connected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
