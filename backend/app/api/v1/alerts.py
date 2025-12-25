"""
Alerts API Endpoints
Manages air quality alerts and notifications
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from supabase import Client

from app.config import get_supabase_client
from app.models.alert import AlertRecord, AlertResponse, SendAlertEmailRequest, EmailSentResponse
from app.services.alert_service import AlertService
from app.services.email_service import EmailService

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])


@router.post("/check-thresholds", response_model=Optional[AlertResponse])
async def check_thresholds(
    city: str = Query(..., description="City name"),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Check if PM2.5 exceeds threshold and create alert if needed.

    **Threshold:** PM2.5 > 50 μg/m³

    Creates an alert record in the database if:
    - Current PM2.5 > threshold
    - No alert created in the last hour

    **Returns:** Alert record with recommendations, or null if no alert
    """
    try:
        alert_service = AlertService(supabase)

        # Check thresholds
        alert = await alert_service.check_thresholds(city)

        if not alert:
            return None

        # Get recommendations
        pm25 = alert['data']['pm25']
        recommendations = alert_service.get_recommendations(pm25)

        return AlertResponse(
            alert=AlertRecord(**alert),
            recommendations=recommendations
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Threshold check failed: {str(e)}"
        )


@router.get("/active", response_model=List[AlertRecord])
async def get_active_alerts(
    city: Optional[str] = Query(None, description="City name (optional)"),
    limit: int = Query(50, ge=1, le=200, description="Maximum results"),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get active alerts.

    Returns all active alerts, optionally filtered by city.
    Active alerts are those marked as is_active=true in the database.
    """
    try:
        alert_service = AlertService(supabase)
        alerts = await alert_service.get_active_alerts(city, limit)

        return [AlertRecord(**alert) for alert in alerts]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch alerts: {str(e)}"
        )


@router.post("/send-email", response_model=EmailSentResponse)
async def send_alert_email(
    request: SendAlertEmailRequest,
    background_tasks: BackgroundTasks,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Send alert email to specified recipients.

    Sends an email notification about current air quality conditions
    with health recommendations.

    **Note:** SMTP must be configured in environment variables for this to work.
    """
    try:
        alert_service = AlertService(supabase)

        # Get current air quality
        aq_response = supabase.table('air_quality_measurements')\
            .select('*')\
            .eq('city', request.city)\
            .order('timestamp', desc=True)\
            .limit(1)\
            .execute()

        if not aq_response.data:
            raise HTTPException(
                status_code=404,
                detail=f"No air quality data found for {request.city}"
            )

        measurement = aq_response.data[0]
        pm25 = measurement['pm25']
        threshold = alert_service.pm25_threshold

        # Get recommendations
        recommendations = alert_service.get_recommendations(pm25)

        # Calculate severity
        severity = alert_service._calculate_threshold_severity(pm25)

        # Send email in background
        email_service = EmailService()

        def send_email_task():
            email_service.send_alert_email(
                to_emails=request.recipients,
                city=request.city,
                pm25=pm25,
                threshold=threshold,
                recommendations=recommendations,
                severity=severity
            )

        background_tasks.add_task(send_email_task)

        return EmailSentResponse(
            success=True,
            recipients_count=len(request.recipients),
            message=f"Email alert queued for {len(request.recipients)} recipient(s)"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send email: {str(e)}"
        )


@router.get("/recommendations")
async def get_recommendations(
    pm25: float = Query(..., ge=0, description="PM2.5 concentration"),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get health recommendations for a PM2.5 level.

    Returns a list of recommended actions based on air quality.
    """
    alert_service = AlertService(supabase)
    recommendations = alert_service.get_recommendations(pm25)

    return {
        'pm25': pm25,
        'recommendations': recommendations
    }


@router.post("/deactivate-old")
async def deactivate_old_alerts(
    hours: int = Query(24, ge=1, le=168, description="Hours threshold"),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Deactivate alerts older than specified hours.

    **Use case:** Cleanup task to deactivate stale alerts
    """
    try:
        alert_service = AlertService(supabase)
        count = await alert_service.deactivate_old_alerts(hours)

        return {
            'deactivated_count': count,
            'hours_threshold': hours
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to deactivate alerts: {str(e)}"
        )
