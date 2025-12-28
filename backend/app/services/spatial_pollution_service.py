"""
Service for spatial analysis of pollution around transit stops
Analyzes if pollution is higher near bus/metro stops
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from supabase import Client
import math


class SpatialPollutionService:
    """Analyze pollution levels around transit infrastructure."""

    def __init__(self, supabase: Client):
        self.supabase = supabase

    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates using Haversine formula.

        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates

        Returns:
            Distance in meters
        """
        R = 6371000  # Earth radius in meters

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi/2)**2 + \
            math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        return R * c

    async def analyze_pollution_near_stops(
        self,
        hours_back: int = 24
    ) -> Dict[str, Any]:
        """
        Analyze if pollution is higher near transit stops.

        Compares PM2.5 levels of sensors:
        - Near stops (<200m): Urban transit zones
        - Far from stops (>500m): Residential/background zones

        Args:
            hours_back: Number of hours of data to analyze

        Returns:
            Spatial analysis with insights
        """
        # Get IoT sensors with location
        sensors_response = self.supabase.table('sensor_metadata')\
            .select('*')\
            .execute()

        sensors = sensors_response.data

        if not sensors or len(sensors) == 0:
            return {
                'status': 'error',
                'message': 'Aucun capteur IoT trouvé avec localisation'
            }

        # Get recent pollution measurements from sensors
        # Get sensor IDs from sensor_metadata
        sensor_ids = [s['sensor_id'] for s in sensors]

        start_time = datetime.utcnow() - timedelta(hours=hours_back)

        measurements_response = self.supabase.table('air_quality_measurements')\
            .select('*')\
            .in_('source', sensor_ids)\
            .gte('timestamp', start_time.isoformat())\
            .execute()

        measurements = measurements_response.data

        if not measurements or len(measurements) < 5:
            return {
                'status': 'insufficient_data',
                'message': f'Pas assez de mesures de capteurs (besoin de 5+, trouvé {len(measurements) if measurements else 0})'
            }

        # For this demo, we'll use known Paris transit coordinates
        # In production, this would fetch from IDFM transit stops API
        major_transit_hubs = [
            {'name': 'Gare du Nord', 'lat': 48.8809, 'lon': 2.3553},
            {'name': 'Châtelet-Les Halles', 'lat': 48.8620, 'lon': 2.3470},
            {'name': 'Gare de Lyon', 'lat': 48.8447, 'lon': 2.3743},
            {'name': 'Montparnasse', 'lat': 48.8420, 'lon': 2.3219},
            {'name': 'Saint-Lazare', 'lat': 48.8756, 'lon': 2.3250},
            {'name': 'République', 'lat': 48.8673, 'lon': 2.3636},
            {'name': 'Nation', 'lat': 48.8483, 'lon': 2.3965},
        ]

        # Calculate pollution by proximity to transit
        near_stop_readings = []  # <200m from transit
        far_stop_readings = []   # >500m from transit
        sensor_analysis = []

        # Group measurements by sensor
        sensor_measurements = {}
        for m in measurements:
            sensor_id = m.get('source', 'unknown')  # Use 'source' field from air_quality_measurements
            if sensor_id not in sensor_measurements:
                sensor_measurements[sensor_id] = []
            sensor_measurements[sensor_id].append(m)

        # Analyze each sensor
        for sensor in sensors:
            sensor_id = sensor['sensor_id']
            location = sensor.get('location', {})

            if not location or 'latitude' not in location:
                continue

            sensor_lat = location['latitude']
            sensor_lon = location['longitude']

            # Find nearest transit hub
            min_distance = float('inf')
            nearest_hub = None

            for hub in major_transit_hubs:
                dist = self.calculate_distance(
                    sensor_lat, sensor_lon,
                    hub['lat'], hub['lon']
                )
                if dist < min_distance:
                    min_distance = dist
                    nearest_hub = hub['name']

            # Get sensor measurements
            if sensor_id in sensor_measurements:
                sensor_pm25_values = [
                    m['pm25'] for m in sensor_measurements[sensor_id]
                    if m.get('pm25') is not None
                ]

                if sensor_pm25_values:
                    avg_pm25 = sum(sensor_pm25_values) / len(sensor_pm25_values)

                    sensor_analysis.append({
                        'sensor_id': sensor_id,
                        'latitude': sensor_lat,
                        'longitude': sensor_lon,
                        'distance_to_nearest_stop': round(min_distance, 0),
                        'nearest_hub': nearest_hub,
                        'avg_pm25': round(avg_pm25, 1),
                        'measurements_count': len(sensor_pm25_values),
                        'zone': 'near_transit' if min_distance < 200 else 'far_transit' if min_distance > 500 else 'medium'
                    })

                    # Categorize readings
                    if min_distance < 200:
                        near_stop_readings.extend(sensor_pm25_values)
                    elif min_distance > 500:
                        far_stop_readings.extend(sensor_pm25_values)

        # Calculate statistics
        if not near_stop_readings or not far_stop_readings:
            return {
                'status': 'insufficient_data',
                'message': 'Pas assez de capteurs dans les deux zones (près/loin des arrêts)',
                'sensors_analyzed': len(sensor_analysis),
                'sensor_details': sensor_analysis
            }

        avg_near = sum(near_stop_readings) / len(near_stop_readings)
        avg_far = sum(far_stop_readings) / len(far_stop_readings)

        difference = avg_near - avg_far
        percent_increase = (difference / avg_far) * 100 if avg_far > 0 else 0

        # Generate insights
        insights = self._generate_spatial_insights(
            avg_near, avg_far, difference, percent_increase,
            len(near_stop_readings), len(far_stop_readings)
        )

        return {
            'status': 'success',
            'analysis_period_hours': hours_back,
            'zones': {
                'near_transit': {
                    'description': 'Capteurs à <200m des arrêts majeurs',
                    'avg_pm25': round(avg_near, 1),
                    'measurements_count': len(near_stop_readings),
                    'sensors_count': len([s for s in sensor_analysis if s['zone'] == 'near_transit'])
                },
                'far_transit': {
                    'description': 'Capteurs à >500m des arrêts majeurs',
                    'avg_pm25': round(avg_far, 1),
                    'measurements_count': len(far_stop_readings),
                    'sensors_count': len([s for s in sensor_analysis if s['zone'] == 'far_transit'])
                }
            },
            'comparison': {
                'difference_pm25': round(difference, 1),
                'percent_increase': round(percent_increase, 1),
                'is_significant': abs(difference) > 5,  # >5 μg/m³ is considered significant
                'interpretation': 'pollution_higher_near_stops' if difference > 5 else
                                 'pollution_lower_near_stops' if difference < -5 else
                                 'no_significant_difference'
            },
            'sensor_details': sensor_analysis,
            'transit_hubs_analyzed': major_transit_hubs,
            'insights': insights,
            'analyzed_at': datetime.utcnow().isoformat()
        }

    @staticmethod
    def _generate_spatial_insights(
        avg_near: float,
        avg_far: float,
        difference: float,
        percent_increase: float,
        near_count: int,
        far_count: int
    ) -> List[str]:
        """Generate insights from spatial analysis."""
        insights = []

        if difference > 10:
            insights.append(
                f"[ALERT SPATIAL] Pollution significativement plus élevée près des arrêts: "
                f"+{difference:.1f} μg/m³ ({percent_increase:.0f}% plus élevé). "
                f"Les zones de transit sont des hotspots de pollution."
            )
            insights.append(
                f"Recommandation: Installer des filtres à air dans les stations de transport, "
                f"végétaliser les abords des arrêts pour absorber les particules."
            )
        elif difference > 5:
            insights.append(
                f"Pollution modérément plus élevée près des arrêts (+{difference:.1f} μg/m³, {percent_increase:.0f}%). "
                f"Impact mesurable du trafic de transit."
            )
        elif difference < -5:
            insights.append(
                f"Résultat inattendu: Pollution plus faible près des arrêts ({difference:.1f} μg/m³). "
                f"Possibles facteurs: zones piétonnes, espaces verts, circulation réduite."
            )
        else:
            insights.append(
                f"Pas de différence significative entre zones de transit et zones résidentielles "
                f"(différence: {difference:.1f} μg/m³). "
                f"La pollution est homogène dans la zone analysée."
            )

        insights.append(
            f"Analyse basée sur {near_count} mesures près des arrêts vs {far_count} mesures en zone résidentielle."
        )

        if avg_near > 50:
            insights.append(
                f"[SANTÉ] PM2.5 moyen près des arrêts ({avg_near:.1f} μg/m³) dépasse les recommandations OMS (25 μg/m³). "
                f"Risque sanitaire pour les usagers quotidiens des transports."
            )

        return insights
