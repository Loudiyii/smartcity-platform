import React from 'react'
import { useVelibStats } from '../../hooks/useMobility'

export const VelibCard: React.FC = () => {
  const { data: stats, isLoading, isError } = useVelibStats()

  if (isLoading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Vélib Paris</h3>
        <div className="text-center text-gray-500">Chargement...</div>
      </div>
    )
  }

  if (isError || !stats) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Vélib Paris</h3>
        <div className="text-center text-gray-500">
          Données non disponibles
          <p className="text-sm mt-2">Vérifiez IDFM_API_KEY</p>
        </div>
      </div>
    )
  }

  const getAvailabilityColor = (percent: number) => {
    if (percent >= 60) return 'text-green-600'
    if (percent >= 30) return 'text-orange-600'
    return 'text-red-600'
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">Vélib Paris</h3>
        <span className="text-sm text-gray-500">Temps réel</span>
      </div>

      <div className="space-y-3">
        {/* Total Bikes Available */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Vélos disponibles</span>
          <span className="text-2xl font-bold text-blue-600">
            {stats.total_bikes_available.toLocaleString()}
          </span>
        </div>

        {/* Total Stations */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Stations actives</span>
          <span className="text-lg font-semibold text-gray-800">
            {stats.total_stations.toLocaleString()}
          </span>
        </div>

        {/* Average Availability */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Disponibilité moyenne</span>
          <span className={`text-lg font-semibold ${getAvailabilityColor(stats.average_availability_percent)}`}>
            {stats.average_availability_percent.toFixed(1)}%
          </span>
        </div>

        {/* Total Docks */}
        <div className="flex items-center justify-between pt-2 border-t border-gray-200">
          <span className="text-xs text-gray-500">Places libres</span>
          <span className="text-sm text-gray-700">
            {stats.total_docks_available.toLocaleString()}
          </span>
        </div>
      </div>

      {/* Status Indicator */}
      <div className="mt-4 pt-3 border-t border-gray-200">
        <div className="flex items-center">
          <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
          <span className="text-xs text-gray-500">Mis à jour il y a 1 min</span>
        </div>
      </div>
    </div>
  )
}
