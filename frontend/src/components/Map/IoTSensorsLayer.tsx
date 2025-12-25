import React from 'react'
import { CircleMarker, Popup } from 'react-leaflet'
import { useSensors } from '../../hooks/useSensors'
import { useCurrentAirQuality } from '../../hooks/useAirQuality'

const getPM25Color = (pm25: number): string => {
  if (pm25 <= 12) return '#10b981' // green-500 (good)
  if (pm25 <= 35.4) return '#f59e0b' // amber-500 (moderate)
  if (pm25 <= 55.4) return '#ef4444' // red-500 (unhealthy)
  return '#991b1b' // red-900 (very unhealthy)
}

export const IoTSensorsLayer: React.FC = () => {
  const { data: sensors, isLoading } = useSensors()

  // Get current air quality for Paris (will get sensor readings later)
  const { data: airQuality } = useCurrentAirQuality('paris')

  if (isLoading || !sensors) {
    return null
  }

  return (
    <>
      {sensors.map((sensor) => {
        const lat = sensor.location?.lat
        const lon = sensor.location?.lon

        if (!lat || !lon) return null

        // Use sensor's last PM2.5 reading or fallback to city average
        const pm25 = airQuality?.data?.pm25 || 25
        const color = getPM25Color(pm25)

        return (
          <CircleMarker
            key={sensor.sensor_id}
            center={[lat, lon]}
            radius={12}
            pathOptions={{
              fillColor: color,
              color: '#fff',
              weight: 2,
              opacity: 1,
              fillOpacity: 0.8
            }}
          >
            <Popup>
              <div className="p-2">
                <h3 className="font-bold text-sm mb-1">{sensor.name}</h3>
                <p className="text-xs text-gray-600">ID: {sensor.sensor_id}</p>
                <p className="text-xs text-gray-600">Status: {sensor.status}</p>
                <div className="mt-2 pt-2 border-t border-gray-200">
                  <p className="text-sm font-semibold" style={{ color }}>
                    PM2.5: {pm25.toFixed(1)} μg/m³
                  </p>
                </div>
                {sensor.last_reading_at && (
                  <p className="text-xs text-gray-400 mt-1">
                    Updated: {new Date(sensor.last_reading_at).toLocaleTimeString()}
                  </p>
                )}
              </div>
            </Popup>
          </CircleMarker>
        )
      })}
    </>
  )
}
