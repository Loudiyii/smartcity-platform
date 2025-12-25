# Skill: Realtime Transport (IDFM GTFS-RT)

## Purpose
Fetch and process real-time public transport data from IDFM APIs including departures, delays, disruptions, and live vehicle positions using GTFS-RT format.

## When to Use
- Getting next departures at a stop
- Monitoring transport delays
- Tracking real-time vehicle positions
- Displaying live transport information
- Calculating estimated arrival times

## GTFS-RT Overview

**Format:** Protocol Buffers (protobuf)
**Update Frequency:** 10-30 seconds
**Feeds:**
- Trip Updates (delays, cancellations)
- Service Alerts (disruptions)
- Vehicle Positions (GPS tracking)

## Service Implementation

```python
# backend/app/services/realtime_transport_service.py
import httpx
from typing import List, Optional
from datetime import datetime, timedelta
from app.models.transport import Departure, Delay, TransportAlert

class RealtimeTransportService:
    """Real-time transport data from IDFM."""

    def __init__(self):
        self.base_url = "https://prim.iledefrance-mobilites.fr/marketplace"
        self.api_key = settings.idfm_api_key

    async def get_next_departures(
        self,
        stop_id: str,
        limit: int = 10,
        time_window_minutes: int = 60
    ) -> List[Departure]:
        """
        Get next departures from a stop.

        Args:
            stop_id: Stop monitoring ref
            limit: Max number of departures
            time_window_minutes: Look ahead window

        Returns:
            List of upcoming departures with real-time info
        """
        url = f"{self.base_url}/stop-monitoring"

        params = {
            'MonitoringRef': stop_id,
            'MaximumStopVisits': limit
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers={'apikey': self.api_key},
                params=params,
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()

            departures = []
            for visit in data.get('Siri', {}).get('ServiceDelivery', {}).get('StopMonitoringDelivery', [{}])[0].get('MonitoredStopVisit', []):
                departure = self._parse_departure(visit)

                # Filter by time window
                if departure.expected_departure_time:
                    time_until = (departure.expected_departure_time - datetime.utcnow()).total_seconds() / 60
                    if 0 <= time_until <= time_window_minutes:
                        departures.append(departure)

            return sorted(departures, key=lambda d: d.expected_departure_time or datetime.max)[:limit]

    def _parse_departure(self, visit: dict) -> Departure:
        """Parse SIRI MonitoredStopVisit to Departure model."""
        journey = visit.get('MonitoredVehicleJourney', {})

        aimed_time = journey.get('MonitoredCall', {}).get('AimedDepartureTime')
        expected_time = journey.get('MonitoredCall', {}).get('ExpectedDepartureTime')

        return Departure(
            stop_id=visit.get('MonitoringRef'),
            line_id=journey.get('LineRef'),
            line_name=journey.get('PublishedLineName'),
            direction=journey.get('DestinationName'),
            aimed_departure_time=datetime.fromisoformat(aimed_time) if aimed_time else None,
            expected_departure_time=datetime.fromisoformat(expected_time) if expected_time else None,
            delay_seconds=self._calculate_delay(aimed_time, expected_time),
            vehicle_id=journey.get('VehicleRef')
        )

    def _calculate_delay(self, aimed: str, expected: str) -> Optional[int]:
        """Calculate delay in seconds."""
        if not aimed or not expected:
            return None
        aimed_dt = datetime.fromisoformat(aimed)
        expected_dt = datetime.fromisoformat(expected)
        return int((expected_dt - aimed_dt).total_seconds())
```

## Pydantic Models

```python
# backend/app/models/transport.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Departure(BaseModel):
    """Real-time departure information."""
    stop_id: str
    line_id: str
    line_name: str
    direction: str
    aimed_departure_time: Optional[datetime]
    expected_departure_time: Optional[datetime]
    delay_seconds: Optional[int] = 0
    vehicle_id: Optional[str] = None

    @property
    def minutes_until_departure(self) -> Optional[int]:
        if not self.expected_departure_time:
            return None
        delta = self.expected_departure_time - datetime.utcnow()
        return max(0, int(delta.total_seconds() / 60))

    @property
    def is_delayed(self) -> bool:
        return self.delay_seconds and self.delay_seconds > 60
```

## API Routes

```python
# backend/app/api/v1/realtime_transport.py
from fastapi import APIRouter, Query
from typing import List

router = APIRouter(prefix="/api/v1/realtime-transport", tags=["realtime-transport"])

@router.get("/departures/{stop_id}", response_model=List[Departure])
async def get_stop_departures(
    stop_id: str,
    limit: int = Query(10, le=50),
    time_window: int = Query(60, le=120)
):
    """Get next departures from a stop with real-time updates."""
    service = RealtimeTransportService()
    return await service.get_next_departures(stop_id, limit, time_window)
```

## Polling vs WebSocket

### Polling Pattern (Simple)
```python
import asyncio

async def poll_departures(stop_id: str):
    service = RealtimeTransportService()
    while True:
        departures = await service.get_next_departures(stop_id)
        # Update UI or database
        await asyncio.sleep(30)
```

### WebSocket Pattern (Advanced)
```python
from fastapi import WebSocket

@app.websocket("/ws/departures/{stop_id}")
async def websocket_departures(websocket: WebSocket, stop_id: str):
    await websocket.accept()
    try:
        while True:
            departures = await service.get_next_departures(stop_id)
            await websocket.send_json([d.model_dump() for d in departures])
            await asyncio.sleep(15)
    except:
        await websocket.close()
```

## Best Practices
- Poll every 15-30 seconds for departures
- Cache line metadata (names, routes)
- Handle missing real-time data gracefully
- Display both scheduled and real-time times

## References
- GTFS-RT Spec: https://gtfs.org/realtime/
- IDFM API: https://prim.iledefrance-mobilites.fr/

## Trade-offs
**Polling vs WebSocket:**
- Polling: Simpler, stateless, good for < 50 clients
- WebSocket: Real-time, complex, better for dashboards
