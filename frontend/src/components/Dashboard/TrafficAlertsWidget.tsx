import React from 'react'
import { useTrafficDisruptions } from '../../hooks/useMobility'

export const TrafficAlertsWidget: React.FC = () => {
  const { data: disruptions, isLoading, isError } = useTrafficDisruptions()

  if (isLoading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Alertes Trafic</h3>
        <div className="text-center text-gray-500">Chargement...</div>
      </div>
    )
  }

  if (isError) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Alertes Trafic</h3>
        <div className="text-center text-gray-500">
          Données non disponibles
          <p className="text-sm mt-2">Vérifiez IDFM_API_KEY</p>
        </div>
      </div>
    )
  }

  const activeDisruptions = disruptions || []

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'bg-red-100 border-red-500 text-red-800'
      case 'high':
        return 'bg-orange-100 border-orange-500 text-orange-800'
      case 'medium':
        return 'bg-yellow-100 border-yellow-500 text-yellow-800'
      default:
        return 'bg-blue-100 border-blue-500 text-blue-800'
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
      case 'high':
        return '🚨'
      case 'medium':
        return '⚠️'
      default:
        return 'ℹ️'
    }
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">Alertes Trafic</h3>
        <span className="bg-gray-100 text-gray-700 text-xs font-semibold px-2 py-1 rounded-full">
          {activeDisruptions.length} active{activeDisruptions.length !== 1 ? 's' : ''}
        </span>
      </div>

      {activeDisruptions.length === 0 ? (
        <div className="text-center py-8">
          <div className="text-4xl mb-2">✅</div>
          <p className="text-gray-600">Aucune perturbation signalée</p>
          <p className="text-sm text-gray-400 mt-1">Trafic fluide sur le réseau</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {activeDisruptions.slice(0, 5).map((disruption, index) => (
            <div
              key={`${disruption.disruption_id}-${index}`}
              className={`border-l-4 p-3 rounded-r ${getSeverityColor(disruption.severity)}`}
            >
              <div className="flex items-start">
                <span className="text-xl mr-2">{getSeverityIcon(disruption.severity)}</span>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-semibold text-sm">
                      {disruption.line_name || 'Réseau'}</span>
                    <span className="text-xs opacity-75 capitalize">
                      {disruption.severity}
                    </span>
                  </div>
                  <p className="text-sm opacity-90 line-clamp-2">
                    {disruption.message}
                  </p>
                </div>
              </div>
            </div>
          ))}

          {activeDisruptions.length > 5 && (
            <div className="text-center pt-2">
              <span className="text-sm text-gray-500">
                + {activeDisruptions.length - 5} autre{activeDisruptions.length - 5 !== 1 ? 's' : ''} perturbation{activeDisruptions.length - 5 !== 1 ? 's' : ''}
              </span>
            </div>
          )}
        </div>
      )}

      {/* Status Indicator */}
      <div className="mt-4 pt-3 border-t border-gray-200">
        <div className="flex items-center">
          <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
          <span className="text-xs text-gray-500">Mis à jour il y a 2 min</span>
        </div>
      </div>
    </div>
  )
}
