"""
Mobility Impact Analysis API
Analyze correlation between urban mobility and air pollution
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any
from supabase import Client

from app.config import get_supabase_client
from app.services.mobility_impact_service import MobilityImpactService

router = APIRouter(prefix="/api/v1/mobility-impact", tags=["mobility-impact"])


def get_mobility_impact_service(supabase: Client = Depends(get_supabase_client)):
    """Dependency to get MobilityImpactService instance."""
    return MobilityImpactService(supabase)


@router.get("/traffic-pollution", response_model=Dict[str, Any])
async def analyze_traffic_pollution(
    city: str = Query(..., description="City name (Paris, Lyon, Marseille)"),
    days: int = Query(7, ge=1, le=30, description="Number of days to analyze"),
    service: MobilityImpactService = Depends(get_mobility_impact_service)
):
    """
    Analyze correlation between traffic disruptions and PM2.5 pollution.

    **Use Case:**
    Determine if traffic congestion directly impacts air quality.
    Helps policy makers decide on traffic restriction measures.

    **Returns:**
    - Correlation coefficient (r)
    - Time-series data for visualization
    - Automated insights and recommendations

    **Example:**
    - Strong positive correlation (r > 0.7): Traffic significantly increases pollution
    - Weak correlation (r < 0.3): Other factors more influential
    """
    try:
        result = await service.analyze_traffic_pollution_correlation(city, days)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Traffic-pollution analysis failed: {str(e)}"
        )


@router.get("/velib-pollution", response_model=Dict[str, Any])
async def analyze_velib_pollution(
    city: str = Query("Paris", description="City name"),
    days: int = Query(7, ge=1, le=30, description="Number of days to analyze"),
    service: MobilityImpactService = Depends(get_mobility_impact_service)
):
    """
    Analyze correlation between Vélib bike usage and pollution levels.

    **Hypothesis:** More bike usage → Less car usage → Less pollution
    **Expected:** Negative correlation (inverse relationship)

    **Use Case:**
    Evaluate effectiveness of bike-sharing programs in reducing pollution.
    Justify budget allocation for Vélib expansion.

    **Returns:**
    - Correlation coefficient (negative = bikes reduce pollution)
    - Vélib usage vs PM2.5 time-series
    - ROI estimation for Vélib expansion
    """
    try:
        result = await service.analyze_velib_pollution_correlation(city, days)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Vélib-pollution analysis failed: {str(e)}"
        )


@router.get("/combined", response_model=Dict[str, Any])
async def get_combined_mobility_impact(
    city: str = Query(..., description="City name (Paris, Lyon, Marseille)"),
    days: int = Query(7, ge=1, le=30, description="Number of days to analyze"),
    service: MobilityImpactService = Depends(get_mobility_impact_service)
):
    """
    Get comprehensive mobility impact analysis.

    **Combines:**
    - Traffic disruptions vs Pollution
    - Vélib usage vs Pollution
    - Overall mobility impact score (0-100)
    - Policy recommendations

    **Use Case:**
    Executive summary for city officials showing complete picture of
    how urban mobility affects air quality.

    **Returns:**
    - All correlation analyses
    - Prioritized policy recommendations
    - Impact score (higher = mobility strongly affects pollution)
    """
    try:
        result = await service.get_combined_mobility_impact(city, days)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Combined mobility impact analysis failed: {str(e)}"
        )
