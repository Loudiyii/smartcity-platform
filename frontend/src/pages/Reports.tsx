import React, { useState } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'
const CITIES = ['Paris', 'Lyon', 'Marseille']

export const Reports: React.FC = () => {
  const [selectedCity, setSelectedCity] = useState('Paris')
  const [startDate, setStartDate] = useState(() => {
    const date = new Date()
    date.setDate(date.getDate() - 7)
    return date.toISOString().split('T')[0]
  })
  const [endDate, setEndDate] = useState(() => {
    return new Date().toISOString().split('T')[0]
  })
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleGenerateReport = async () => {
    setError(null)
    setIsGenerating(true)

    try {
      // Validate date range
      const start = new Date(startDate)
      const end = new Date(endDate)

      if (start > end) {
        throw new Error("La date de début doit être antérieure à la date de fin")
      }

      const daysDiff = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24))
      if (daysDiff > 90) {
        throw new Error("La période ne peut pas dépasser 90 jours")
      }

      // Build URL
      const url = `${API_BASE_URL}/api/v1/reports/pdf?city=${encodeURIComponent(selectedCity)}&start_date=${startDate}&end_date=${endDate}`

      // Trigger download
      const response = await fetch(url)

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Erreur de génération' }))
        throw new Error(errorData.detail || 'Erreur de génération du rapport')
      }

      // Get PDF blob
      const blob = await response.blob()

      // Create download link
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = `rapport_${selectedCity.toLowerCase()}_${startDate}_to_${endDate}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)

    } catch (err: any) {
      setError(err.message || 'Erreur lors de la génération du rapport')
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto py-6 px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Rapports PDF
        </h1>
        <p className="text-gray-600">
          Générez des rapports PDF personnalisés avec graphiques et statistiques
        </p>
      </div>

      {/* Report Form */}
      <div className="bg-white rounded-lg shadow p-8 mb-6">
        <h2 className="text-xl font-semibold mb-6 text-gray-800">
          Configuration du rapport
        </h2>

        <div className="space-y-6">
          {/* City Selector */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Ville
            </label>
            <div className="grid grid-cols-3 gap-4">
              {CITIES.map((city) => (
                <button
                  key={city}
                  onClick={() => setSelectedCity(city)}
                  className={`px-4 py-3 rounded-lg font-semibold transition-colors ${
                    selectedCity === city
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {city}
                </button>
              ))}
            </div>
          </div>

          {/* Date Range */}
          <div className="grid grid-cols-2 gap-6">
            <div>
              <label htmlFor="start-date" className="block text-sm font-medium text-gray-700 mb-2">
                Date de début
              </label>
              <input
                id="start-date"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label htmlFor="end-date" className="block text-sm font-medium text-gray-700 mb-2">
                Date de fin
              </label>
              <input
                id="end-date"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                max={new Date().toISOString().split('T')[0]}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border-2 border-red-500 rounded-lg p-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {/* Generate Button */}
          <button
            onClick={handleGenerateReport}
            disabled={isGenerating}
            className="w-full py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isGenerating ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Génération en cours...
              </span>
            ) : (
              'Générer le rapport PDF'
            )}
          </button>
        </div>
      </div>

      {/* Info Card */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <div className="flex items-start gap-4">
          <span className="text-3xl">📄</span>
          <div>
            <h3 className="font-semibold text-blue-900 mb-2">
              Contenu du rapport
            </h3>
            <ul className="text-sm text-blue-800 space-y-2">
              <li>• Tableau de statistiques (moyennes, min, max pour PM2.5, PM10, NO2)</li>
              <li>• Graphique d'évolution PM2.5 sur la période sélectionnée</li>
              <li>• Graphiques des conditions météorologiques (température, humidité)</li>
              <li>• En-tête avec ville et période analysée</li>
              <li>• Horodatage de génération</li>
            </ul>
            <p className="text-xs text-blue-700 mt-4">
              <strong>Limite:</strong> Maximum 90 jours par rapport
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
