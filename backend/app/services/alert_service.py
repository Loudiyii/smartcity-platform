"""
Alert Service for Air Quality Monitoring
Creates and manages alerts based on threshold exceedances
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from supabase import Client


class AlertService:
    """Manages air quality alerts and threshold monitoring."""

    def __init__(self, supabase_client: Client):
        """
        Initialize alert service.

        Args:
            supabase_client: Supabase client for database access
        """
        self.supabase = supabase_client
        self.pm25_threshold = 50.0  # μg/m³

    async def check_thresholds(self, city: str) -> Optional[Dict[str, Any]]:
        """
        Check if current PM2.5 exceeds threshold.

        Args:
            city: City name

        Returns:
            Alert data if threshold exceeded, None otherwise
        """
        # Get latest measurement
        response = self.supabase.table('air_quality_measurements')\
            .select('*')\
            .eq('city', city)\
            .order('timestamp', desc=True)\
            .limit(1)\
            .execute()

        if not response.data:
            return None

        measurement = response.data[0]
        pm25 = measurement['pm25']

        if pm25 > self.pm25_threshold:
            # Check if alert already exists for recent time
            recent_alert = await self._get_recent_alert(city, hours=1)

            if not recent_alert:
                # Create new alert
                alert_data = {
                    'city': city,
                    'alert_type': 'threshold_exceeded',
                    'severity': self._calculate_threshold_severity(pm25),
                    'message': f"PM2.5 level exceeds threshold: {pm25:.1f} μg/m³ (threshold: {self.pm25_threshold})",
                    'data': {
                        'pm25': pm25,
                        'threshold': self.pm25_threshold,
                        'timestamp': measurement['timestamp'],
                        'aqi': measurement['aqi']
                    },
                    'is_active': True
                }

                # Insert alert
                result = self.supabase.table('alerts').insert(alert_data).execute()

                return result.data[0] if result.data else alert_data

        return None

    async def _get_recent_alert(
        self,
        city: str,
        hours: int = 1,
        alert_type: str = 'threshold_exceeded'
    ) -> Optional[Dict[str, Any]]:
        """
        Check if a recent alert exists.

        Args:
            city: City name
            hours: Hours to look back
            alert_type: Type of alert

        Returns:
            Recent alert if found, None otherwise
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        response = self.supabase.table('alerts')\
            .select('*')\
            .eq('city', city)\
            .eq('alert_type', alert_type)\
            .eq('is_active', True)\
            .gte('created_at', cutoff.isoformat())\
            .order('created_at', desc=True)\
            .limit(1)\
            .execute()

        return response.data[0] if response.data else None

    def _calculate_threshold_severity(self, pm25: float) -> str:
        """
        Calculate severity based on PM2.5 level.

        Args:
            pm25: PM2.5 concentration

        Returns:
            Severity level
        """
        if pm25 < 55:
            return 'medium'  # Unhealthy for sensitive groups
        elif pm25 < 150:
            return 'high'  # Unhealthy
        elif pm25 < 250:
            return 'critical'  # Very unhealthy
        else:
            return 'critical'  # Hazardous

    def get_recommendations(self, pm25: float) -> List[str]:
        """
        Get health recommendations based on PM2.5 level.

        Args:
            pm25: PM2.5 concentration

        Returns:
            List of recommendation strings
        """
        if pm25 <= 12:
            return [
                "Qualité de l'air excellente",
                "Conditions idéales pour les activités en plein air"
            ]
        elif pm25 <= 35.4:
            return [
                "Qualité de l'air acceptable",
                "Les personnes sensibles peuvent limiter les efforts prolongés"
            ]
        elif pm25 <= 55.4:
            return [
                "Évitez l'activité physique prolongée en extérieur",
                "Les groupes sensibles doivent limiter leur exposition",
                "Fermez les fenêtres",
                "Utilisez un purificateur d'air si disponible"
            ]
        elif pm25 <= 150.4:
            return [
                "Évitez toute activité physique en extérieur",
                "Restez à l'intérieur autant que possible",
                "Fermez les fenêtres et portes",
                "Utilisez un purificateur d'air",
                "Portez un masque FFP2/N95 si vous devez sortir",
                "Privilégiez les transports en commun couverts"
            ]
        else:
            return [
                "ALERTE SANTÉ: Restez à l'intérieur",
                "N'ouvrez pas les fenêtres",
                "Évitez tout effort physique",
                "Portez un masque FFP2/N95 si vous devez sortir",
                "Consultez un médecin en cas de symptômes",
                "Suivez les instructions des autorités locales"
            ]

    async def get_active_alerts(
        self,
        city: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get active alerts.

        Args:
            city: City name (optional)
            limit: Maximum results

        Returns:
            List of active alerts
        """
        query = self.supabase.table('alerts')\
            .select('*')\
            .eq('is_active', True)\
            .order('created_at', desc=True)\
            .limit(limit)

        if city:
            query = query.eq('city', city)

        response = query.execute()

        return response.data

    async def deactivate_old_alerts(self, hours: int = 24) -> int:
        """
        Deactivate alerts older than specified hours.

        Args:
            hours: Hours threshold

        Returns:
            Number of alerts deactivated
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        response = self.supabase.table('alerts')\
            .update({'is_active': False})\
            .eq('is_active', True)\
            .lt('created_at', cutoff.isoformat())\
            .execute()

        return len(response.data) if response.data else 0
