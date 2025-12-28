"""
Smart City Platform - Main FastAPI Application
Phase 1 MVP - Sprint 1
Updated: 2025-12-28
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

print("[MAIN] Importing routers...")
from app.api.v1 import air_quality, weather, sensors, auth, mobility
print("[MAIN] Core routers imported (air_quality, weather, sensors, auth, mobility)")

from app.api.v1 import predictions, anomalies, alerts, analytics, reports, mobility_impact
print("[MAIN] Phase 2 routers imported (predictions, anomalies, alerts, analytics, reports, mobility_impact)")

from app.config import get_settings

settings = get_settings()
print(f"[MAIN] Settings loaded, environment: {settings.ENVIRONMENT}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for startup and shutdown."""
    # Startup
    print("Smart City API starting...")
    print(f"Environment: {settings.ENVIRONMENT}")

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
