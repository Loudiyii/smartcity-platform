import React from 'react'
import { CircleMarker, Popup } from 'react-leaflet'
import { useVelibStations } from '../../hooks/useMobility'

const getAvailabilityColor = (percent: number): string => {
  if (percent >= 60) return '#10b981' // green-500 (good availability)
  if (percent >= 30) return '#f59e0b' // amber-500 (moderate)
  return '#ef4444' // red-500 (low availability)
}

export const VelibStationsLayer: React.FC = () => {
  const { data: stations, isLoading } = useVelibStations(100) // Get 100 stations

  if (isLoading || !stations) {
    return null
  }

  return (
    <>
      {stations.map((station) => {
        const color = getAvailabilityColor(station.availability_percent)
        const lat = station.latitude
        const lon = station.longitude

        if (!lat || !lon) return null

        return (
          <CircleMarker
            key={station.station_id}
            center={[lat, lon]}
            radius={8}
            pathOptions={{
              fillColor: color,
              color: '#fff',
              weight: 2,
              opacity: 1,
              fillOpacity: 0.7
            }}
          >
            <Popup>
              <div className="p-2 min-w-[200px]">
                <h3 className="font-bold text-sm mb-2">{station.name}</h3>

                <div className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Vélos:</span>
                    <span className="font-semibold text-blue-600">
                      {station.num_bikes_available}
                    </span>
                  </div>

                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Places:</span>
                    <span className="font-semibold text-gray-700">
                      {station.num_docks_available}
                    </span>
                  </div>

                  <div className="flex justify-between text-sm pt-1 border-t border-gray-200">
                    <span className="text-gray-600">Disponibilité:</span>
                    <span className="font-semibold" style={{ color }}>
                      {station.availability_percent.toFixed(0)}%
                    </span>
                  </div>
                </div>

                <div className="mt-2 pt-2 border-t border-gray-200">
                  <div className="flex gap-2 text-xs">
                    {station.is_renting && (
                      <span className="bg-green-100 text-green-700 px-2 py-0.5 rounded">
                        En service
                      </span>
                    )}
                    {!station.is_installed && (
                      <span className="bg-red-100 text-red-700 px-2 py-0.5 rounded">
                        Hors service
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </Popup>
          </CircleMarker>
        )
      })}
    </>
  )
}
