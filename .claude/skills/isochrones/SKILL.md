# Skill: Isochrones Analysis

## Purpose
Calculate and visualize accessibility zones (isochrones) showing areas reachable within specific time limits using various transport modes.

## When to Use
- Calculating reachable areas from a point
- Analyzing public transport coverage
- Comparing multimodal accessibility
- Visualizing service areas on maps

## Concept

**Isochrone:** Area reachable from a point within a time limit
**Use Cases:**
- "Show areas within 15 min by public transport"
- "Calculate 30-min walking radius"
- "Compare bike vs transit coverage"

## API Integration

### OpenRouteService

```python
# backend/app/services/isochrone_service.py
import httpx
from typing import List, Dict

class IsochroneService:
    """Calculate isochrones using OpenRouteService."""

    def __init__(self):
        self.base_url = "https://api.openrouteservice.org/v2/isochrones"
        self.api_key = settings.ORS_API_KEY

    async def calculate_isochrone(
        self,
        lat: float,
        lon: float,
        time_minutes: int = 15,
        mode: str = "driving-car",
        intervals: List[int] = None
    ) -> Dict:
        """
        Calculate isochrone polygon.

        Args:
            lat, lon: Origin coordinates
            time_minutes: Time limit in minutes
            mode: Transport mode (driving-car, foot-walking, cycling-regular)
            intervals: Multiple time intervals [5, 10, 15]

        Returns:
            GeoJSON FeatureCollection with isochrone polygons
        """
        if intervals is None:
            intervals = [time_minutes * 60]
        else:
            intervals = [t * 60 for t in intervals]

        body = {
            "locations": [[lon, lat]],
            "range": intervals,
            "range_type": "time"
        }

        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/{mode}",
                json=body,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
```

## Frontend Visualization

### Leaflet Integration

```typescript
// frontend/src/components/Map/IsochroneLayer.tsx
import { GeoJSON } from 'react-leaflet';

export const IsochroneLayer: React.FC<{lat: number, lon: number}> = ({ lat, lon }) => {
  const { data } = useQuery({
    queryKey: ['isochrone', lat, lon],
    queryFn: () => fetch(`/api/v1/isochrones/calculate`, {
      method: 'POST',
      body: JSON.stringify({ latitude: lat, longitude: lon, time_minutes: 15 })
    }).then(r => r.json())
  });

  if (!data) return null;

  return (
    <GeoJSON
      data={data}
      style={{ color: '#3388ff', weight: 2, fillOpacity: 0.2 }}
    />
  );
};
```

## Caching Strategy

```python
# Cache isochrones for frequently requested locations
def get_cache_key(lat: float, lon: float, time: int, mode: str) -> str:
    lat_rounded = round(lat, 3)
    lon_rounded = round(lon, 3)
    return f"iso_{lat_rounded}_{lon_rounded}_{time}_{mode}"

async def get_cached_isochrone(lat, lon, time, mode):
    cache_key = get_cache_key(lat, lon, time, mode)

    # Check database cache
    result = supabase.table('isochrones').select('geojson') \
        .eq('cache_key', cache_key).limit(1).execute()

    if result.data:
        return result.data[0]['geojson']

    # Calculate and cache
    geojson = await service.calculate_isochrone(lat, lon, time, mode)
    supabase.table('isochrones').insert({
        'cache_key': cache_key,
        'geojson': geojson
    }).execute()

    return geojson
```

## Best Practices

- Cache calculated isochrones (valid for weeks)
- Round coordinates to 3 decimals for cache hits
- Use appropriate mode for use case
- Make polygons semi-transparent
- Add legend explaining colors

## References
- OpenRouteService: https://openrouteservice.org/
- GeoJSON Spec: https://geojson.org/

## Trade-offs

**API Choice:**
- OpenRouteService: Free, 2000 req/day
- Mapbox: Better accuracy, paid
- Self-hosted: Full control, infrastructure cost

**Caching:**
- Cache everything: Fast, stale data
- Calculate on-demand: Fresh, slower
- Hybrid: Cache common locations
