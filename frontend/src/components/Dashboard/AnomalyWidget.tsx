import React from 'react'
import { useRecentAnomalies } from '../../hooks/useAnomalies'

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
      return '🚨'
    case 'high':
      return '⚠️'
    case 'medium':
      return '⚡'
    default:
      return 'ℹ️'
  }
}

export const AnomalyWidget: React.FC = () => {
  const { data: anomalies, isLoading } = useRecentAnomalies(undefined, 24, 5)

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Anomalies détectées</h3>
        <p className="text-gray-500">Chargement...</p>
      </div>
    )
  }

  if (!anomalies || anomalies.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Anomalies détectées</h3>
        <div className="text-center py-8">
          <span className="text-6xl">✅</span>
          <p className="text-gray-600 mt-4">Aucune anomalie détectée</p>
          <p className="text-sm text-gray-500 mt-2">Dernières 24 heures</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Anomalies détectées</h3>
        <span className="bg-red-100 text-red-800 text-xs font-semibold px-3 py-1 rounded-full">
          {anomalies.length} active{anomalies.length > 1 ? 's' : ''}
        </span>
      </div>

      <div className="space-y-3">
        {anomalies.slice(0, 5).map((anomaly, index) => {
          const anomalyData = anomaly.data || {}
          const detectionMethod = anomalyData.detection_method || 'unknown'
          const pm25 = anomalyData.pm25 || 0

          return (
            <div
              key={`${anomaly.id}-${index}`}
              className={`border-2 rounded-lg p-3 ${getSeverityColor(anomaly.severity)}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-2">
                  <span className="text-xl">{getSeverityIcon(anomaly.severity)}</span>
                  <div>
                    <p className="font-semibold text-sm">{anomaly.city}</p>
                    <p className="text-xs opacity-90">{anomaly.message}</p>
                    <div className="flex items-center gap-3 mt-1">
                      <span className="text-xs">
                        PM2.5: <strong>{pm25.toFixed(1)}</strong> μg/m³
                      </span>
                      <span className="text-xs opacity-75">
                        {detectionMethod === 'z_score' ? 'Z-score' : 'Isolation Forest'}
                      </span>
                    </div>
                  </div>
                </div>
                <span className={`text-xs px-2 py-1 rounded font-semibold ${getSeverityColor(anomaly.severity)}`}>
                  {anomaly.severity}
                </span>
              </div>

              <div className="mt-2 pt-2 border-t border-current opacity-50">
                <p className="text-xs">
                  Détecté: {new Date(anomaly.created_at).toLocaleString('fr-FR')}
                </p>
              </div>
            </div>
          )
        })}
      </div>

      {anomalies.length > 5 && (
        <p className="text-xs text-gray-500 text-center mt-4">
          +{anomalies.length - 5} anomalies supplémentaires
        </p>
      )}
    </div>
  )
}
