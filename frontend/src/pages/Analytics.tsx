import React, { useState } from 'react'
import { useCorrelationData, useCorrelationStats } from '../hooks/useAnalytics'
import { CorrelationChart } from '../components/Charts/CorrelationChart'

const CITIES = ['Paris', 'Lyon', 'Marseille']
const POLLUTANTS = [
  { key: 'pm25', label: 'PM2.5' },
  { key: 'pm10', label: 'PM10' },
  { key: 'no2', label: 'NO2' },
  { key: 'o3', label: 'O3' }
]
const WEATHER_VARS = [
  { key: 'temperature', label: 'Température', unit: '°C' },
  { key: 'humidity', label: 'Humidité', unit: '%' },
  { key: 'wind_speed', label: 'Vitesse du Vent', unit: 'km/h' },
  { key: 'pressure', label: 'Pression', unit: 'hPa' }
]

export const Analytics: React.FC = () => {
  const [selectedCity, setSelectedCity] = useState('Paris')
  const [days, setDays] = useState(7)
  const [selectedPollutant, setSelectedPollutant] = useState('pm25')
  const [selectedWeather, setSelectedWeather] = useState('temperature')

  const { data: correlationData, isLoading } = useCorrelationData(selectedCity, days)
  const { data: stats } = useCorrelationStats(selectedCity, days)

  const pollutantInfo = POLLUTANTS.find(p => p.key === selectedPollutant)
  const weatherInfo = WEATHER_VARS.find(w => w.key === selectedWeather)

  // Get correlation coefficient
  const getCorrelation = () => {
    if (!stats) return null
    const pollutantKey = `${selectedPollutant}_vs_weather` as keyof typeof stats.correlations
    return stats.correlations[pollutantKey]?.[selectedWeather] || null
  }

  const correlation = getCorrelation()

  return (
    <div className="max-w-7xl mx-auto py-6 px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Analyse de Corrélation
        </h1>
        <p className="text-gray-600">
          Corrélations entre pollution et conditions météorologiques
        </p>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* City Selector */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Ville
            </label>
            <select
              value={selectedCity}
              onChange={(e) => setSelectedCity(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {CITIES.map(city => (
                <option key={city} value={city}>{city}</option>
              ))}
            </select>
          </div>

          {/* Days Selector */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Période
            </label>
            <select
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={7}>7 jours</option>
              <option value={14}>14 jours</option>
              <option value={30}>30 jours</option>
            </select>
          </div>

          {/* Pollutant Selector */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Polluant
            </label>
            <select
              value={selectedPollutant}
              onChange={(e) => setSelectedPollutant(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {POLLUTANTS.map(p => (
                <option key={p.key} value={p.key}>{p.label}</option>
              ))}
            </select>
          </div>

          {/* Weather Variable Selector */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Variable Météo
            </label>
            <select
              value={selectedWeather}
              onChange={(e) => setSelectedWeather(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {WEATHER_VARS.map(w => (
                <option key={w.key} value={w.key}>{w.label}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Correlation Coefficient */}
        {correlation !== null && (
          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">
                Coefficient de corrélation de Pearson:
              </span>
              <span className={`text-2xl font-bold ${
                Math.abs(correlation) > 0.7 ? 'text-red-600' :
                Math.abs(correlation) > 0.4 ? 'text-orange-600' :
                'text-blue-600'
              }`}>
                {correlation.toFixed(3)}
              </span>
            </div>
            <p className="text-xs text-gray-600 mt-2">
              {Math.abs(correlation) > 0.7 && "Corrélation forte"}
              {Math.abs(correlation) > 0.4 && Math.abs(correlation) <= 0.7 && "Corrélation modérée"}
              {Math.abs(correlation) <= 0.4 && "Corrélation faible"}
              {correlation > 0 ? " positive" : " négative"}
            </p>
          </div>
        )}
      </div>

      {/* Chart */}
      {isLoading && (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-gray-600">Chargement des données...</p>
        </div>
      )}

      {!isLoading && correlationData && pollutantInfo && weatherInfo && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">
            {pollutantInfo.label} vs {weatherInfo.label}
          </h3>
          <CorrelationChart
            timestamps={correlationData.timestamps}
            pollutionData={correlationData.pollution[selectedPollutant as keyof typeof correlationData.pollution] as number[]}
            pollutionLabel={pollutantInfo.label}
            weatherData={correlationData.weather[selectedWeather as keyof typeof correlationData.weather]}
            weatherLabel={weatherInfo.label}
            weatherUnit={weatherInfo.unit}
          />
          <p className="text-sm text-gray-500 mt-4 text-center">
            {correlationData.data_points} points de données sur {days} jours
          </p>
        </div>
      )}

      {/* Info */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h4 className="font-semibold text-blue-900 mb-3">
          Interprétation du coefficient de corrélation
        </h4>
        <ul className="text-sm text-blue-800 space-y-2">
          <li><strong>+1.0:</strong> Corrélation positive parfaite (les deux augmentent ensemble)</li>
          <li><strong>0.0:</strong> Aucune corrélation linéaire</li>
          <li><strong>-1.0:</strong> Corrélation négative parfaite (l'un augmente, l'autre diminue)</li>
          <li className="mt-3"><strong>Seuils:</strong> |r| > 0.7 = forte, 0.4-0.7 = modérée, &lt; 0.4 = faible</li>
        </ul>
      </div>
    </div>
  )
}
