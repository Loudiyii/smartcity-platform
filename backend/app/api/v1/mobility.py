"""
Mobility API routes for IDFM data
Vélib, traffic disruptions, transit stops
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from app.services.mobility_service import MobilityService
from app.models.mobility import (
    TrafficDisruption,
    VelibStation,
    TransitStop,
    VelibStatsResponse,
    StopDepartures
)

router = APIRouter(prefix="/api/v1/mobility", tags=["mobility"])


def get_mobility_service():
    """Dependency to get MobilityService instance."""
    return MobilityService()


@router.get("/traffic-disruptions", response_model=List[TrafficDisruption])
async def get_traffic_disruptions(
    severity: Optional[str] = Query(None, regex="^(low|medium|high|critical)$"),
    active_only: bool = True,
    service: MobilityService = Depends(get_mobility_service)
):
    """
    Get current traffic disruptions from IDFM.

    **Parameters:**
    - severity: Filter by severity (low, medium, high, critical)
    - active_only: Only return active disruptions (default: true)

    **Returns:** List of traffic disruptions
    """
    disruptions = await service.get_traffic_disruptions(severity, active_only)
    return disruptions


@router.get("/velib/stations", response_model=List[VelibStation])
async def get_velib_stations(
    station_id: Optional[str] = None,
    limit: int = Query(50, le=200, description="Maximum number of stations"),
    service: MobilityService = Depends(get_mobility_service)
):
    """
    Get Vélib station availability in real-time.

    **Parameters:**
    - station_id: Specific station ID (optional)
    - limit: Maximum number of stations to return (default: 50, max: 200)

    **Returns:** List of Vélib stations with availability data
    """
    stations = await service.get_velib_availability(station_id, limit)
    return stations


@router.get("/transit/stops", response_model=List[TransitStop])
async def get_transit_stops(
    limit: int = Query(50, le=200, description="Maximum number of stops"),
    zone_id: Optional[str] = None,
    service: MobilityService = Depends(get_mobility_service)
):
    """
    Get transit stop areas for mapping.

    **Parameters:**
    - limit: Maximum number of stops (default: 50, max: 200)
    - zone_id: Filter by zone (optional)

    **Returns:** List of transit stops
    """
    stops = await service.get_transit_stops(limit, zone_id)
    return stops


@router.get("/transit/next-departures/{stop_id}", response_model=StopDepartures)
async def get_next_departures(
    stop_id: str,
    limit: int = Query(10, le=50, description="Maximum number of departures"),
    service: MobilityService = Depends(get_mobility_service)
):
    """
    Get next departures/arrivals at a specific transit stop in real-time.

    **Parameters:**
    - stop_id: IDFM stop monitoring reference (e.g., "STIF:StopPoint:Q:41322:")
    - limit: Maximum number of departures to return (default: 10, max: 50)

    **Returns:** Real-time departures with estimated arrival times

    **Example:**
    ```
    /api/v1/mobility/transit/next-departures/STIF:StopPoint:Q:41322:?limit=5
    ```
    """
    departures = await service.get_next_departures(stop_id, limit)

    if not departures:
        raise HTTPException(
            status_code=404,
            detail=f"No real-time data available for stop {stop_id}. Either the stop doesn't exist or real-time data is not yet available for this stop."
        )

    return departures


@router.get("/velib/stats", response_model=VelibStatsResponse)
async def get_velib_stats(
    service: MobilityService = Depends(get_mobility_service)
):
    """
    Get aggregated Vélib statistics for Paris.

    **Returns:** Aggregated stats (total stations, bikes available, average availability)
    """
    stations = await service.get_velib_availability(limit=1000)

    total_stations = len(stations)
    total_bikes = sum(s.num_bikes_available for s in stations)
    total_docks = sum(s.num_docks_available for s in stations)
    avg_availability = (
        sum(s.availability_percent for s in stations) / total_stations
        if total_stations > 0 else 0
    )

    return VelibStatsResponse(
        total_stations=total_stations,
        total_bikes_available=total_bikes,
        total_docks_available=total_docks,
        average_availability_percent=round(avg_availability, 2)
    )
