import { useState } from 'react'
import { Line } from 'react-chartjs-2'
import { useCombinedMobilityImpact } from '../hooks/useMobilityImpact'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

export default function MobilityImpact() {
  const [selectedCity, setSelectedCity] = useState('Paris')
  const [days, setDays] = useState(7)

  const { data, isLoading, error } = useCombinedMobilityImpact(selectedCity, days)

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-lg">Analyse en cours...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6 bg-red-50 rounded-lg">
        <h3 className="text-red-800 font-semibold mb-2">Erreur de chargement</h3>
        <p className="text-red-600">Impossible de charger l'analyse de corrélation</p>
      </div>
    )
  }

  if (!data) {
    return <div>Aucune donnée disponible</div>
  }

  const trafficAnalysis = data.traffic_analysis
  const velibAnalysis = data.velib_analysis

  // Traffic-Pollution Chart Data
  const trafficChartData = {
    labels: trafficAnalysis?.time_series?.timestamps || [],
    datasets: [
      {
        label: 'PM2.5 (μg/m³)',
        data: trafficAnalysis?.time_series?.pm25 || [],
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        yAxisID: 'y1',
        tension: 0.4
      },
      {
        label: 'Perturbations Trafic',
        data: trafficAnalysis?.time_series?.traffic_disruptions || [],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        yAxisID: 'y2',
        tension: 0.4
      }
    ]
  }

  // Vélib-Pollution Chart Data
  const velibChartData = {
    labels: velibAnalysis?.time_series?.timestamps || [],
    datasets: [
      {
        label: 'PM2.5 (μg/m³)',
        data: velibAnalysis?.time_series?.pm25 || [],
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        yAxisID: 'y1',
        tension: 0.4
      },
      {
        label: 'Vélos disponibles',
        data: velibAnalysis?.time_series?.velib_available || [],
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        yAxisID: 'y2',
        tension: 0.4
      }
    ]
  }

  const dualAxisOptions: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top' as const,
      },
    },
    scales: {
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        title: {
          display: true,
          text: 'PM2.5 (μg/m³)'
        },
        grid: {
          drawOnChartArea: true,
        },
      },
      y2: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        title: {
          display: true,
          text: 'Métrique Mobilité'
        },
        grid: {
          drawOnChartArea: false,
        },
      },
    },
  }

  const getCorrelationColor = (value: number): string => {
    const abs = Math.abs(value)
    if (abs > 0.7) return 'text-red-600 bg-red-50'
    if (abs > 0.4) return 'text-orange-600 bg-orange-50'
    if (abs > 0.2) return 'text-yellow-600 bg-yellow-50'
    return 'text-gray-600 bg-gray-50'
  }

  const getPriorityColor = (priority: string): string => {
    if (priority === 'HIGH') return 'bg-red-100 text-red-800 border-red-300'
    if (priority === 'MEDIUM') return 'bg-orange-100 text-orange-800 border-orange-300'
    return 'bg-blue-100 text-blue-800 border-blue-300'
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Impact Mobilité sur Pollution</h1>
        <p className="text-gray-600">
          Analyse de corrélation entre la mobilité urbaine et la qualité de l'air
        </p>
      </div>

      {/* City and Period Selector */}
      <div className="bg-white rounded-lg shadow p-4 mb-6 flex gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Ville</label>
          <select
            value={selectedCity}
            onChange={(e) => setSelectedCity(e.target.value)}
            className="border rounded px-3 py-2"
          >
            <option value="Paris">Paris</option>
            <option value="Lyon">Lyon</option>
            <option value="Marseille">Marseille</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Période</label>
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="border rounded px-3 py-2"
          >
            <option value={7}>7 jours</option>
            <option value={14}>14 jours</option>
            <option value={30}>30 jours</option>
          </select>
        </div>
      </div>

      {/* Correlation Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* Traffic Correlation Card */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Trafic ↔ Pollution</h2>
          <div className={`rounded-lg p-4 mb-4 ${getCorrelationColor(trafficAnalysis?.correlation?.value || 0)}`}>
            <div className="text-3xl font-bold mb-1">
              r = {trafficAnalysis?.correlation?.value?.toFixed(3)}
            </div>
            <div className="text-sm">
              Corrélation {trafficAnalysis?.correlation?.strength} ({trafficAnalysis?.correlation?.direction})
            </div>
          </div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">PM2.5 moyen:</span>
              <span className="font-semibold">{trafficAnalysis?.statistics?.pm25_mean?.toFixed(1)} μg/m³</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Perturbations/h:</span>
              <span className="font-semibold">{trafficAnalysis?.statistics?.traffic_mean?.toFixed(1)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Points de données:</span>
              <span className="font-semibold">{trafficAnalysis?.data_points}</span>
            </div>
          </div>
        </div>

        {/* Vélib Correlation Card */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Vélib ↔ Pollution</h2>
          <div className={`rounded-lg p-4 mb-4 ${getCorrelationColor(velibAnalysis?.correlation?.value || 0)}`}>
            <div className="text-3xl font-bold mb-1">
              r = {velibAnalysis?.correlation?.value?.toFixed(3)}
            </div>
            <div className="text-sm">
              Corrélation {velibAnalysis?.correlation?.strength} ({velibAnalysis?.correlation?.direction})
            </div>
          </div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">PM2.5 moyen:</span>
              <span className="font-semibold">{velibAnalysis?.statistics?.pm25_mean?.toFixed(1)} μg/m³</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Vélos dispo (moy):</span>
              <span className="font-semibold">{velibAnalysis?.statistics?.velib_avg_available?.toFixed(0)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Points de données:</span>
              <span className="font-semibold">{velibAnalysis?.data_points}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Traffic-Pollution Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Trafic vs PM2.5</h3>
          <div className="h-80">
            <Line data={trafficChartData} options={dualAxisOptions} />
          </div>
        </div>

        {/* Vélib-Pollution Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Vélib vs PM2.5</h3>
          <div className="h-80">
            <Line data={velibChartData} options={dualAxisOptions} />
          </div>
        </div>
      </div>

      {/* Overall Insights */}
      {data.overall_insights && data.overall_insights.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold mb-3 text-blue-900">Insights Globaux</h3>
          <ul className="space-y-2">
            {data.overall_insights.map((insight, index) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-blue-600 mt-1">•</span>
                <span className="text-blue-900">{insight}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Traffic Insights */}
      {trafficAnalysis?.insights && trafficAnalysis.insights.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h3 className="text-lg font-semibold mb-3">Analyse Trafic</h3>
          <ul className="space-y-2">
            {trafficAnalysis.insights.map((insight, index) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-gray-600 mt-1">→</span>
                <span className="text-gray-800">{insight}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Vélib Insights */}
      {velibAnalysis?.insights && velibAnalysis.insights.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h3 className="text-lg font-semibold mb-3">Analyse Vélib</h3>
          <ul className="space-y-2">
            {velibAnalysis.insights.map((insight, index) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-gray-600 mt-1">→</span>
                <span className="text-gray-800">{insight}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Policy Recommendations */}
      {data.recommendations && data.recommendations.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Recommandations Politiques</h3>
          <div className="space-y-4">
            {data.recommendations.map((rec, index) => (
              <div
                key={index}
                className={`border rounded-lg p-4 ${getPriorityColor(rec.priority)}`}
              >
                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-semibold text-lg">{rec.action}</h4>
                  <span className="px-2 py-1 text-xs font-semibold rounded">
                    {rec.priority}
                  </span>
                </div>
                <p className="text-sm mb-2">{rec.description}</p>
                <div className="text-sm font-medium">
                  Impact attendu: {rec.expected_impact}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
