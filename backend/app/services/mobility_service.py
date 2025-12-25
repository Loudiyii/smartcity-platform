"""
Service for Île-de-France Mobilités (IDFM/PRIM) APIs
Fetches real-time mobility data: Vélib, traffic disruptions, transit stops
"""

import httpx
from typing import List, Optional, Dict
from app.config import get_settings
from app.models.mobility import TrafficDisruption, VelibStation, TransitStop

settings = get_settings()


class MobilityService:
    """Service for Île-de-France Mobilités (PRIM) APIs."""

    def __init__(self):
        self.base_url = settings.IDFM_BASE_URL
        self.api_key = settings.IDFM_API_KEY
        self.headers = {
            "apikey": self.api_key,
            "Accept": "application/json"
        }

    async def get_traffic_disruptions(
        self,
        severity: Optional[str] = None,
        active_only: bool = True
    ) -> List[TrafficDisruption]:
        """
        Fetch current traffic disruptions from IDFM general-message API.

        Args:
            severity: Filter by severity (low, medium, high, critical)
            active_only: Only return active disruptions

        Returns:
            List of traffic disruption objects
        """
        if not self.api_key:
            print("⚠️  IDFM_API_KEY not configured")
            return []

        url = f"{self.base_url}/general-message"

        params = {}
        if severity:
            params['severity'] = severity

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()

                disruptions = []

                # Parse SIRI response structure
                siri = data.get('Siri', {})
                service_delivery = siri.get('ServiceDelivery', {})
                message_delivery = service_delivery.get('GeneralMessageDelivery', [{}])[0]
                info_messages = message_delivery.get('InfoMessage', [])

                for item in info_messages:
                    disruption = self._parse_disruption(item)
                    if active_only and not disruption.is_active:
                        continue
                    disruptions.append(disruption)

                return disruptions

            except httpx.HTTPError as e:
                print(f"❌ Error fetching traffic disruptions: {e}")
                return []
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                return []

    async def get_velib_availability(
        self,
        station_id: Optional[str] = None,
        limit: int = 50
    ) -> List[VelibStation]:
        """
        Fetch Vélib station availability from IDFM bike-sharing API.

        Args:
            station_id: Specific station ID (optional)
            limit: Maximum number of stations to return

        Returns:
            List of Vélib station objects with availability
        """
        if not self.api_key:
            print("⚠️  IDFM_API_KEY not configured")
            return []

        # Note: Actual endpoint may vary based on IDFM documentation
        url = f"{self.base_url}/bike-sharing"

        params = {'limit': limit}
        if station_id:
            params['station_id'] = station_id

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()

                stations = []

                # Parse response (structure may vary)
                station_list = data.get('stations', [])

                for item in station_list[:limit]:
                    try:
                        station = VelibStation(
                            station_id=str(item.get('stationCode', item.get('station_id', ''))),
                            name=item.get('name', 'Unknown'),
                            num_bikes_available=item.get('nbBike', item.get('num_bikes_available', 0)),
                            num_docks_available=item.get('nbFreeDock', item.get('num_docks_available', 0)),
                            latitude=item.get('coordonnees_geo', {}).get('lat', item.get('lat', 0.0)),
                            longitude=item.get('coordonnees_geo', {}).get('lon', item.get('lon', 0.0)),
                            is_installed=item.get('is_installed', 1) == 1,
                            is_returning=item.get('is_returning', 1) == 1,
                            is_renting=item.get('is_renting', 1) == 1,
                            last_reported=item.get('dueDate')
                        )
                        stations.append(station)
                    except Exception as e:
                        print(f"⚠️  Error parsing station: {e}")
                        continue

                return stations

            except httpx.HTTPError as e:
                print(f"❌ Error fetching Vélib data: {e}")
                return []
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                return []

    async def get_transit_stops(
        self,
        limit: int = 50,
        zone_id: Optional[str] = None
    ) -> List[TransitStop]:
        """
        Fetch transit stop areas from IDFM stop-monitoring API.

        Args:
            limit: Maximum number of stops
            zone_id: Filter by zone (optional)

        Returns:
            List of transit stop objects
        """
        if not self.api_key:
            print("⚠️  IDFM_API_KEY not configured")
            return []

        url = f"{self.base_url}/stop-monitoring"

        params = {'limit': limit}
        if zone_id:
            params['zone_id'] = zone_id

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()

                stops = []

                # Parse response
                stop_list = data.get('stops', [])

                for item in stop_list[:limit]:
                    try:
                        stop = TransitStop(
                            stop_id=item['stop_id'],
                            stop_name=item['stop_name'],
                            stop_lat=item['stop_lat'],
                            stop_lon=item['stop_lon'],
                            zone_id=item.get('zone_id'),
                            location_type=item.get('location_type', 0)
                        )
                        stops.append(stop)
                    except Exception as e:
                        print(f"⚠️  Error parsing stop: {e}")
                        continue

                return stops

            except httpx.HTTPError as e:
                print(f"❌ Error fetching transit stops: {e}")
                return []
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                return []

    def _parse_disruption(self, item: Dict) -> TrafficDisruption:
        """Parse raw API disruption into structured model."""
        info_message = item.get('InfoMessage', {})
        content = info_message.get('Content', {})

        # Extract message text
        messages = content.get('Message', [{}])
        message_text = messages[0].get('MessageText', 'No details') if messages else 'No details'

        return TrafficDisruption(
            disruption_id=item.get('RecordedAtTime', ''),
            line_id=content.get('LineRef', ''),
            line_name=content.get('LineName', 'Unknown'),
            severity=content.get('Severity', 'unknown'),
            message=message_text,
            start_time=info_message.get('ValidUntilTime'),
            end_time=info_message.get('ValidUntilTime'),
            is_active=True
        )
