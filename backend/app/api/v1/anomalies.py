"""
Anomaly Detection API Endpoints
Handles anomaly detection and retrieval
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client

from app.config import get_supabase_client
from app.models.anomaly import AnomalyDetectionResponse, AnomalyAlert
from app.ml.anomaly_detector import AnomalyDetector

router = APIRouter(prefix="/api/v1/anomalies", tags=["anomalies"])


@router.get("/detect", response_model=AnomalyDetectionResponse)
async def detect_anomalies(
    city: str = Query(..., description="City name"),
    lookback_days: int = Query(7, ge=1, le=30, description="Days of data to analyze"),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Detect anomalies using Z-score and Isolation Forest methods.

    Analyzes recent air quality measurements to identify abnormal readings.
    Anomalies are detected using:
    - **Z-score**: Statistical outliers (>3 standard deviations)
    - **Isolation Forest**: Machine learning-based multivariate anomaly detection

    **Returns:**
    - List of detected anomalies with severity levels
    - Count by detection method
    - Anomaly details (timestamp, values, scores)
    """
    try:
        detector = AnomalyDetector(supabase)
        result = await detector.detect_all_anomalies(city, lookback_days)

        return AnomalyDetectionResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Anomaly detection failed: {str(e)}"
        )


@router.post("/detect-and-alert")
async def detect_and_create_alerts(
    city: str = Query(..., description="City name"),
    lookback_days: int = Query(1, ge=1, le=7, description="Days to analyze"),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Detect anomalies and automatically create alerts.

    This endpoint:
    1. Detects anomalies using both methods
    2. Saves high/critical severity anomalies to alerts table
    3. Returns summary of created alerts

    **Use case:** Scheduled task to run every 15 minutes for real-time monitoring
    """
    try:
        detector = AnomalyDetector(supabase)
        result = await detector.detect_all_anomalies(city, lookback_days)

        # Save high/critical anomalies as alerts
        alerts_created = 0
        for anomaly in result['anomalies']:
            if anomaly['severity'] in ['high', 'critical']:
                await detector.save_anomaly_to_alerts(anomaly)
                alerts_created += 1

        return {
            'city': city,
            'anomalies_detected': result['total_anomalies'],
            'alerts_created': alerts_created,
            'lookback_days': lookback_days
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Anomaly detection and alert creation failed: {str(e)}"
        )


@router.get("/recent", response_model=List[dict])
async def get_recent_anomalies(
    city: Optional[str] = Query(None, description="City name (optional)"),
    hours: int = Query(24, ge=1, le=168, description="Hours to look back"),
    limit: int = Query(50, ge=1, le=200, description="Maximum results"),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get recent anomaly alerts from the alerts table.

    **Parameters:**
    - **city**: Filter by city (optional, omit for all cities)
    - **hours**: Time window in hours (default 24)
    - **limit**: Maximum number of results (default 50)

    **Returns:** List of anomaly alerts sorted by most recent first
    """
    try:
        detector = AnomalyDetector(supabase)
        anomalies = await detector.get_recent_anomalies(city, hours, limit)

        return anomalies

    except Exception as e:
        import traceback
        print(f"[ERROR] Failed to fetch recent anomalies: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch recent anomalies: {str(e)}"
        )


@router.get("/stats")
async def get_anomaly_statistics(
    city: str = Query(..., description="City name"),
    days: int = Query(7, ge=1, le=30, description="Days to analyze"),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get anomaly statistics for a city.

    **Returns:**
    - Total anomalies detected
    - Anomaly rate (% of measurements that are anomalous)
    - Severity distribution
    - Detection method breakdown
    """
    try:
        detector = AnomalyDetector(supabase)
        result = await detector.detect_all_anomalies(city, days)

        # Calculate statistics
        anomalies = result['anomalies']
        total = result['total_anomalies']

        # Severity distribution
        severity_dist = {
            'low': 0,
            'medium': 0,
            'high': 0,
            'critical': 0
        }

        for anomaly in anomalies:
            severity_dist[anomaly['severity']] += 1

        # Detection method distribution
        method_dist = {
            'z_score': result['zscore_count'],
            'isolation_forest': result['isolation_forest_count']
        }

        return {
            'city': city,
            'days_analyzed': days,
            'total_anomalies': total,
            'severity_distribution': severity_dist,
            'method_distribution': method_dist,
            'detected_at': result['detected_at']
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate statistics: {str(e)}"
        )
