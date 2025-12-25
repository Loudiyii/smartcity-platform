import React from 'react'
import type { Prediction } from '../../hooks/usePredictions'

interface PredictionCardProps {
  prediction: Prediction
}

const getColorClass = (color: string) => {
  const colorMap: Record<string, string> = {
    green: 'bg-green-100 border-green-500 text-green-800',
    yellow: 'bg-yellow-100 border-yellow-500 text-yellow-800',
    orange: 'bg-orange-100 border-orange-500 text-orange-800',
    red: 'bg-red-100 border-red-500 text-red-800',
    purple: 'bg-purple-100 border-purple-500 text-purple-800',
    maroon: 'bg-red-200 border-red-700 text-red-900'
  }
  return colorMap[color] || 'bg-gray-100 border-gray-500 text-gray-800'
}

export const PredictionCard: React.FC<PredictionCardProps> = ({ prediction }) => {
  const predictionDate = new Date(prediction.prediction_for)
  const confidence = Math.round(prediction.confidence * 100)

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-2xl font-bold text-gray-900">PM2.5 Prediction</h3>
          <p className="text-sm text-gray-600 mt-1">
            For {predictionDate.toLocaleDateString('fr-FR', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric'
            })}
          </p>
          <p className="text-xs text-gray-500">
            {predictionDate.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
          </p>
        </div>

        <div className={`px-4 py-2 rounded-lg border-2 ${getColorClass(prediction.aqi_level.color)}`}>
          <p className="text-sm font-semibold">{prediction.aqi_level.name}</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6 mb-6">
        <div className="text-center">
          <p className="text-5xl font-bold text-gray-900">{prediction.predicted_pm25.toFixed(1)}</p>
          <p className="text-sm text-gray-600 mt-2">ug/m³ PM2.5</p>
        </div>

        <div className="text-center">
          <div className="relative w-24 h-24 mx-auto">
            <svg className="w-24 h-24 transform -rotate-90">
              <circle
                cx="48"
                cy="48"
                r="40"
                stroke="#e5e7eb"
                strokeWidth="8"
                fill="none"
              />
              <circle
                cx="48"
                cy="48"
                r="40"
                stroke="#3b82f6"
                strokeWidth="8"
                fill="none"
                strokeDasharray={`${confidence * 2.51} 251`}
                strokeLinecap="round"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-2xl font-bold">{confidence}%</span>
            </div>
          </div>
          <p className="text-sm text-gray-600 mt-2">Confidence</p>
        </div>
      </div>

      <div className="mb-6">
        <p className="text-sm font-semibold text-gray-700 mb-2">Prediction Range</p>
        <div className="flex items-center justify-between bg-gray-50 rounded-lg p-4">
          <div>
            <p className="text-xs text-gray-600">Lower Bound</p>
            <p className="text-lg font-semibold text-gray-900">
              {prediction.prediction_range.lower.toFixed(1)}
            </p>
          </div>
          <div className="flex-1 mx-4">
            <div className="h-2 bg-gray-200 rounded-full relative">
              <div
                className="absolute h-2 bg-blue-500 rounded-full"
                style={{
                  left: '0%',
                  width: '100%'
                }}
              />
            </div>
          </div>
          <div className="text-right">
            <p className="text-xs text-gray-600">Upper Bound</p>
            <p className="text-lg font-semibold text-gray-900">
              {prediction.prediction_range.upper.toFixed(1)}
            </p>
          </div>
        </div>
      </div>

      <div className={`p-4 rounded-lg border-2 ${getColorClass(prediction.aqi_level.color)}`}>
        <p className="text-sm font-semibold mb-1">Health Advisory</p>
        <p className="text-sm">{prediction.aqi_level.description}</p>
      </div>

      <div className="mt-6 grid grid-cols-3 gap-4 pt-4 border-t border-gray-200">
        <div className="text-center">
          <p className="text-xs text-gray-600">R² Score</p>
          <p className="text-sm font-semibold text-gray-900">
            {prediction.model_metrics.r2.toFixed(3)}
          </p>
        </div>
        <div className="text-center">
          <p className="text-xs text-gray-600">MAPE</p>
          <p className="text-sm font-semibold text-gray-900">
            {prediction.model_metrics.mape.toFixed(1)}%
          </p>
        </div>
        <div className="text-center">
          <p className="text-xs text-gray-600">RMSE</p>
          <p className="text-sm font-semibold text-gray-900">
            {prediction.model_metrics.rmse.toFixed(1)}
          </p>
        </div>
      </div>
    </div>
  )
}
