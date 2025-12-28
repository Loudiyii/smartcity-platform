"""
Service for Île-de-France Mobilités (IDFM/PRIM) APIs
Fetches real-time mobility data: Vélib, traffic disruptions, transit stops
"""

import httpx
from typing import List, Optional, Dict
from datetime import datetime
from app.config import get_settings
from app.models.mobility import TrafficDisruption, VelibStation, TransitStop, StopDepartures, NextDeparture

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
        Fetch current traffic disruptions from IDFM disruptions_bulk API.

        Args:
            severity: Filter by severity (low, medium, high, critical)
            active_only: Only return active disruptions

        Returns:
            List of traffic disruption objects
        """
        if not self.api_key:
            print("[WARNING] IDFM_API_KEY not configured")
            return []

        url = f"{self.base_url}/disruptions_bulk/disruptions/v2"

        async with httpx.AsyncClient(verify=False) as client:
            try:
                response = await client.get(
                    url,
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()

                disruptions = []

                # Parse disruptions array
                disruptions_list = data.get('disruptions', [])
                print(f"[DEBUG] Fetched {len(disruptions_list)} disruptions from IDFM API")

                for item in disruptions_list:
                    try:
                        # Extract severity (v2 API returns string, not object)
                        item_severity = item.get('severity', 'unknown').lower()

                        # Filter by severity if provided
                        if severity and item_severity != severity.lower():
                            continue

                        # Check if active (v2 API uses applicationPeriods to determine active status)
                        application_periods = item.get('applicationPeriods', [])
                        is_active = len(application_periods) > 0
                        if active_only and not is_active:
                            continue

                        # Get affected lines from impactedSections
                        impacted_sections = item.get('impactedSections', [])
                        line_id = None
                        line_name = None
                        if impacted_sections:
                            first_section = impacted_sections[0]
                            line_id = first_section.get('lineId', '')
                            # Extract line name from the from/to section names
                            from_name = first_section.get('from', {}).get('name', '')
                            to_name = first_section.get('to', {}).get('name', '')
                            line_name = f"{from_name} → {to_name}" if from_name and to_name else 'Unknown'

                        # Get message text (v2 API returns message as string)
                        message_text = item.get('message', '') or item.get('shortMessage', 'No details')
                        # Strip HTML tags from message
                        import re
                        message_text = re.sub('<[^<]+?>', '', message_text)

                        # Get timeframe
                        start_time = None
                        end_time = None
                        if application_periods:
                            start_time = application_periods[0].get('begin')
                            end_time = application_periods[-1].get('end')  # Use last period end

                        disruption = TrafficDisruption(
                            disruption_id=item.get('id', ''),
                            line_id=line_id,
                            line_name=line_name,
                            severity=item_severity,
                            message=message_text,
                            start_time=start_time,
                            end_time=end_time,
                            is_active=is_active
                        )
                        disruptions.append(disruption)

                    except Exception as e:
                        print(f"[WARNING] Error parsing disruption: {e}")
                        continue

                print(f"[DEBUG] Returning {len(disruptions)} disruptions after filtering")
                return disruptions

            except httpx.HTTPError as e:
                print(f"[ERROR] Error fetching traffic disruptions: {e}")
                print(f"   Response status: {e.response.status_code if hasattr(e, 'response') else 'N/A'}")
                return []
            except Exception as e:
                print(f"[ERROR] Unexpected error: {e}")
                return []

    async def get_velib_availability(
        self,
        station_id: Optional[str] = None,
        limit: int = 50
    ) -> List[VelibStation]:
        """
        Fetch Vélib station availability from IDFM GBFS API.

        Args:
            station_id: Specific station ID (optional)
            limit: Maximum number of stations to return

        Returns:
            List of Vélib station objects with availability
        """
        if not self.api_key:
            print("[WARNING] IDFM_API_KEY not configured")
            return []

        # GBFS endpoints
        status_url = f"{self.base_url}/velib/station_status.json"
        info_url = f"{self.base_url}/velib/station_information.json"

        async with httpx.AsyncClient(verify=False) as client:
            try:
                # Fetch station status (availability)
                status_response = await client.get(
                    status_url,
                    headers=self.headers,
                    timeout=10.0
                )
                status_response.raise_for_status()
                status_data = status_response.json()

                # Fetch station information (location, name)
                info_response = await client.get(
                    info_url,
                    headers=self.headers,
                    timeout=10.0
                )
                info_response.raise_for_status()
                info_data = info_response.json()

                # Parse GBFS format
                stations_status = status_data.get('data', {}).get('stations', [])
                stations_info = info_data.get('data', {}).get('stations', [])

                # Create lookup dict for info
                info_dict = {s['station_id']: s for s in stations_info}

                stations = []

                for status in stations_status[:limit]:
                    try:
                        station_id_val = str(status.get('station_id', ''))

                        # Filter by station_id if provided
                        if station_id and station_id_val != station_id:
                            continue

                        info = info_dict.get(station_id_val, {})

                        station = VelibStation(
                            station_id=station_id_val,
                            name=info.get('name', 'Unknown'),
                            num_bikes_available=status.get('num_bikes_available', 0),
                            num_docks_available=status.get('num_docks_available', 0),
                            latitude=info.get('lat', 0.0),
                            longitude=info.get('lon', 0.0),
                            is_installed=status.get('is_installed', 1) == 1,
                            is_returning=status.get('is_returning', 1) == 1,
                            is_renting=status.get('is_renting', 1) == 1,
                            last_reported=status.get('last_reported')
                        )
                        stations.append(station)
                    except Exception as e:
                        print(f"[WARNING] Error parsing station: {e}")
                        continue

                return stations

            except httpx.HTTPError as e:
                print(f"[ERROR] Error fetching Velib data: {e}")
                print(f"   Response status: {e.response.status_code if hasattr(e, 'response') else 'N/A'}")
                print(f"   Response text: {e.response.text[:200] if hasattr(e, 'response') else 'N/A'}")
                return []
            except Exception as e:
                print(f"[ERROR] Unexpected error: {e}")
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
            print("[WARNING] IDFM_API_KEY not configured")
            return []

        url = f"{self.base_url}/stop-monitoring"

        params = {'limit': limit}
        if zone_id:
            params['zone_id'] = zone_id

        async with httpx.AsyncClient(verify=False) as client:  # Disable SSL verification for Windows compatibility
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
                        print(f"[WARNING] Error parsing stop: {e}")
                        continue

                return stops

            except httpx.HTTPError as e:
                print(f"[ERROR] Error fetching transit stops: {e}")
                print(f"   Response status: {e.response.status_code if hasattr(e, 'response') else 'N/A'}")
                return []
            except Exception as e:
                print(f"[ERROR] Unexpected error: {e}")
                return []

    async def get_next_departures(
        self,
        stop_id: str,
        limit: int = 10
    ) -> Optional[StopDepartures]:
        """
        Fetch next departures/arrivals at a specific transit stop.

        Args:
            stop_id: IDFM stop monitoring reference (e.g., "STIF:StopPoint:Q:41322:")
            limit: Maximum number of departures to return

        Returns:
            StopDepartures object with next departures, or None if error
        """
        if not self.api_key:
            print("[WARNING] IDFM_API_KEY not configured")
            return None

        # IDFM stop-monitoring endpoint
        url = f"{self.base_url}/stop-monitoring"

        params = {
            'MonitoringRef': stop_id
        }

        async with httpx.AsyncClient(verify=False) as client:
            try:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()

                # Parse SIRI Lite response
                siri = data.get('Siri', {})
                service_delivery = siri.get('ServiceDelivery', {})
                stop_monitoring_deliveries = service_delivery.get('StopMonitoringDelivery', [])

                if not stop_monitoring_deliveries:
                    print(f"[WARNING] No monitoring data for stop {stop_id}")
                    return None

                delivery = stop_monitoring_deliveries[0]
                monitored_stop_visits = delivery.get('MonitoredStopVisit', [])

                departures = []
                stop_name = "Unknown"

                for visit in monitored_stop_visits[:limit]:
                    try:
                        monitored_vehicle_journey = visit.get('MonitoredVehicleJourney', {})

                        # Extract stop name
                        if not stop_name or stop_name == "Unknown":
                            monitored_call = monitored_vehicle_journey.get('MonitoredCall', {})
                            stop_name = monitored_call.get('StopPointName', [{}])[0].get('value', 'Unknown')

                        # Extract line info
                        line_ref = monitored_vehicle_journey.get('LineRef', {}).get('value', '')
                        published_line_name = monitored_vehicle_journey.get('PublishedLineName', [{}])[0].get('value', 'Unknown')

                        # Extract destination
                        destination_ref = monitored_vehicle_journey.get('DestinationRef', {}).get('value', '')
                        destination_name = monitored_vehicle_journey.get('DestinationName', [{}])[0].get('value', 'Unknown')

                        # Extract expected arrival time
                        monitored_call = monitored_vehicle_journey.get('MonitoredCall', {})
                        expected_arrival = monitored_call.get('ExpectedArrivalTime')
                        expected_departure = monitored_call.get('ExpectedDepartureTime')

                        arrival_time_str = expected_arrival or expected_departure
                        if not arrival_time_str:
                            continue

                        # Parse ISO 8601 datetime
                        arrival_time = datetime.fromisoformat(arrival_time_str.replace('Z', '+00:00'))

                        # Extract arrival status
                        arrival_status = monitored_call.get('ArrivalStatus', 'onTime')

                        # Vehicle reference
                        vehicle_ref = monitored_vehicle_journey.get('VehicleRef', {}).get('value')

                        departure = NextDeparture(
                            line_id=line_ref,
                            line_name=published_line_name,
                            destination_name=destination_name,
                            expected_arrival_time=arrival_time,
                            arrival_status=arrival_status,
                            vehicle_ref=vehicle_ref
                        )
                        departures.append(departure)

                    except Exception as e:
                        print(f"[WARNING] Error parsing departure: {e}")
                        continue

                return StopDepartures(
                    stop_id=stop_id,
                    stop_name=stop_name,
                    departures=departures
                )

            except httpx.HTTPError as e:
                print(f"[ERROR] Error fetching next departures: {e}")
                print(f"   Response status: {e.response.status_code if hasattr(e, 'response') else 'N/A'}")
                return None
            except Exception as e:
                print(f"[ERROR] Unexpected error: {e}")
                return None

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
