import React from 'react'
import { Marker, Popup } from 'react-leaflet'
import { useTrafficDisruptions } from '../../hooks/useMobility'
import L from 'leaflet'

// Custom icon for traffic disruptions
const getDisruptionIcon = (severity: string) => {
  const color = severity === 'critical' || severity === 'high' ? 'red' :
                severity === 'medium' ? 'orange' : 'blue'

  return L.divIcon({
    className: 'custom-div-icon',
    html: `
      <div style="
        background-color: ${color};
        width: 24px;
        height: 24px;
        border-radius: 50%;
        border: 2px solid white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
      ">
        ⚠️
      </div>
    `,
    iconSize: [24, 24],
    iconAnchor: [12, 12]
  })
}

const getSeverityColor = (severity: string) => {
  switch (severity.toLowerCase()) {
    case 'critical':
      return 'text-red-600 bg-red-100'
    case 'high':
      return 'text-orange-600 bg-orange-100'
    case 'medium':
      return 'text-yellow-600 bg-yellow-100'
    default:
      return 'text-blue-600 bg-blue-100'
  }
}

export const TrafficDisruptionsLayer: React.FC = () => {
  const { data: disruptions, isLoading } = useTrafficDisruptions()

  if (isLoading || !disruptions || disruptions.length === 0) {
    return null
  }

  // For now, place disruptions at Paris center (would need geo data from API)
  const parisCenter: [number, number] = [48.8566, 2.3522]

  return (
    <>
      {disruptions.slice(0, 10).map((disruption, index) => {
        // Spread disruptions around Paris center
        const offsetLat = (Math.random() - 0.5) * 0.1
        const offsetLon = (Math.random() - 0.5) * 0.1
        const position: [number, number] = [
          parisCenter[0] + offsetLat,
          parisCenter[1] + offsetLon
        ]

        return (
          <Marker
            key={`${disruption.disruption_id}-${index}`}
            position={position}
            icon={getDisruptionIcon(disruption.severity)}
          >
            <Popup maxWidth={300}>
              <div className="p-2">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-bold text-sm">{disruption.line_name || 'Réseau'}</h3>
                  <span className={`text-xs px-2 py-1 rounded-full font-semibold ${getSeverityColor(disruption.severity)}`}>
                    {disruption.severity}
                  </span>
                </div>

                <p className="text-sm text-gray-700 mb-2">
                  {disruption.message}
                </p>

                {disruption.line_id && (
                  <p className="text-xs text-gray-500">
                    Ligne: {disruption.line_id}
                  </p>
                )}

                <div className="mt-2 pt-2 border-t border-gray-200">
                  <p className="text-xs text-gray-400">
                    Signalé: {new Date(disruption.created_at).toLocaleString('fr-FR')}
                  </p>
                </div>
              </div>
            </Popup>
          </Marker>
        )
      })}
    </>
  )
}
