import React from 'react'
import { CircleMarker, Popup } from 'react-leaflet'
import { useTransitStops } from '../../hooks/useMobility'

interface TransitStopsLayerProps {
  onStopClick?: (stopId: string) => void
}

export const TransitStopsLayer: React.FC<TransitStopsLayerProps> = ({ onStopClick }) => {
  const { data: stops, isLoading } = useTransitStops(100)

  if (isLoading || !stops) {
    return null
  }

  return (
    <>
      {stops.map((stop) => {
        const lat = stop.stop_lat
        const lon = stop.stop_lon

        if (!lat || !lon) return null

        const isStation = stop.location_type === 1

        return (
          <CircleMarker
            key={stop.stop_id}
            center={[lat, lon]}
            radius={isStation ? 10 : 6}
            pathOptions={{
              fillColor: '#3b82f6', // blue-500
              color: '#fff',
              weight: 2,
              opacity: 1,
              fillOpacity: isStation ? 0.8 : 0.6
            }}
          >
            <Popup>
              <div className="p-2">
                <h3 className="font-bold text-sm mb-1">{stop.stop_name}</h3>
                <p className="text-xs text-gray-600">
                  {isStation ? '🚉 Station' : '🚏 Arrêt'}
                </p>
                {stop.zone_id && (
                  <p className="text-xs text-gray-500 mt-1">
                    Zone: {stop.zone_id}
                  </p>
                )}
                <p className="text-xs text-gray-400 mt-2">
                  ID: {stop.stop_id}
                </p>
                {onStopClick && (
                  <button
                    onClick={() => onStopClick(stop.stop_id)}
                    className="mt-3 w-full px-3 py-1.5 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 font-medium"
                  >
                    Voir horaires temps réel →
                  </button>
                )}
              </div>
            </Popup>
          </CircleMarker>
        )
      })}
    </>
  )
}
