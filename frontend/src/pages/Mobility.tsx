import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { LayersControl } from 'react-leaflet'
import api from '../services/api'
import { LeafletMap } from '../components/Map/LeafletMap'
import { TransitStopsLayer } from '../components/Map/TransitStopsLayer'
import { VelibStationsLayer } from '../components/Map/VelibStationsLayer'

const { Overlay } = LayersControl

interface VelibStats {
  total_stations: number
  total_bikes_available: number
  total_docks_available: number
  average_availability_percent: number
}

interface TrafficDisruption {
  disruption_id: string
  line_id: string
  line_name: string
  severity: string
  message: string
  is_active: boolean
}

interface NextDeparture {
  line_name: string
  destination_name: string
  expected_arrival_time: string
  arrival_status: string
}

interface StopDepartures {
  stop_id: string
  stop_name: string
  departures: NextDeparture[]
}

interface SpatialAnalysis {
  status: string
  analysis_period_hours: number
  zones: {
    near_transit: {
      description: string
      avg_pm25: number
      measurements_count: number
      sensors_count: number
    }
    far_transit: {
      description: string
      avg_pm25: number
      measurements_count: number
      sensors_count: number
    }
  }
  comparison: {
    difference_pm25: number
    percent_increase: number
    is_significant: boolean
    interpretation: string
  }
  sensor_details: Array<{
    sensor_id: string
    latitude: number
    longitude: number
    distance_to_nearest_stop: number
    nearest_hub: string
    avg_pm25: number
    measurements_count: number
    zone: string
  }>
  insights: string[]
}

export const Mobility: React.FC = () => {
  const [searchStopId, setSearchStopId] = useState('')

  // Fetch Vélib stats
  const { data: velibStats, isLoading: velibLoading } = useQuery<VelibStats>({
    queryKey: ['velib-stats'],
    queryFn: async () => {
      const response = await api.get('/api/v1/mobility/velib/stats')
      return response.data
    },
    refetchInterval: 30000 // Refresh every 30s
  })

  // Fetch traffic disruptions
  const { data: disruptions, isLoading: disruptionsLoading } = useQuery<TrafficDisruption[]>({
    queryKey: ['traffic-disruptions'],
    queryFn: async () => {
      const response = await api.get('/api/v1/mobility/traffic-disruptions?active_only=true')
      return response.data
    },
    refetchInterval: 60000 // Refresh every 60s
  })

  // Fetch next departures for selected stop
  const { data: departures, isLoading: departuresLoading, error: departuresError} = useQuery<StopDepartures>({
    queryKey: ['next-departures', searchStopId],
    queryFn: async () => {
      const response = await api.get(`/api/v1/mobility/transit/next-departures/${searchStopId}?limit=10`)
      return response.data
    },
    enabled: !!searchStopId,
    retry: false
  })

  // Fetch spatial pollution analysis
  const { data: spatialAnalysis, isLoading: spatialLoading } = useQuery<SpatialAnalysis>({
    queryKey: ['spatial-pollution-analysis'],
    queryFn: async () => {
      const response = await api.get('/api/v1/mobility/spatial-pollution-analysis?hours_back=24')
      return response.data
    },
    refetchInterval: 300000, // Refresh every 5 minutes
    retry: false
  })

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critique':
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-300'
      case 'perturbee':
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-300'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300'
      default:
        return 'bg-blue-100 text-blue-800 border-blue-300'
    }
  }

  const getMinutesUntil = (arrivalTime: string) => {
    const now = new Date()
    const arrival = new Date(arrivalTime)
    const diff = Math.floor((arrival.getTime() - now.getTime()) / 60000)
    return Math.max(0, diff)
  }

  return (
    <div className="max-w-7xl mx-auto py-6 px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Mobilité en Temps Réel
        </h1>
        <p className="text-gray-600">
          Données de mobilité Île-de-France : Vélib, transports en commun, perturbations
        </p>
      </div>

      {/* Vélib Stats */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Vélib' Métropole</h2>
        {velibLoading ? (
          <div className="bg-white rounded-lg shadow p-6">
            <div className="animate-pulse">Chargement...</div>
          </div>
        ) : velibStats ? (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Stations totales</div>
              <div className="text-3xl font-bold text-blue-600">{velibStats.total_stations}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Vélos disponibles</div>
              <div className="text-3xl font-bold text-green-600">{velibStats.total_bikes_available}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Places libres</div>
              <div className="text-3xl font-bold text-purple-600">{velibStats.total_docks_available}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Disponibilité moyenne</div>
              <div className="text-3xl font-bold text-orange-600">{velibStats.average_availability_percent.toFixed(1)}%</div>
            </div>
          </div>
        ) : null}
      </div>

      {/* Traffic Disruptions */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Perturbations Trafic {disruptions && disruptions.length > 0 && `(${disruptions.length})`}
        </h2>
        {disruptionsLoading ? (
          <div className="bg-white rounded-lg shadow p-6">
            <div className="animate-pulse">Chargement des perturbations...</div>
          </div>
        ) : disruptions && disruptions.length > 0 ? (
          <div className="space-y-3">
            {disruptions.map((disruption) => (
              <div
                key={disruption.disruption_id}
                className={`rounded-lg border-2 p-4 ${getSeverityColor(disruption.severity)}`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="font-semibold text-lg">
                    {disruption.line_name || 'Ligne inconnue'}
                  </div>
                  <span className="px-2 py-1 rounded text-xs font-semibold uppercase">
                    {disruption.severity}
                  </span>
                </div>
                <p className="text-sm">{disruption.message}</p>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-green-50 border-2 border-green-200 rounded-lg p-6 text-center">
            <p className="text-green-800 font-semibold">Aucune perturbation en cours</p>
            <p className="text-sm text-green-600 mt-1">Le trafic est fluide sur l'ensemble du réseau</p>
          </div>
        )}
      </div>

      {/* Next Departures */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Carte des Arrêts & Prochains Passages</h2>

        {/* Interactive Map */}
        <div className="bg-white rounded-lg shadow overflow-hidden mb-4">
          <LeafletMap height="500px">
            <Overlay checked name="Arrêts Transport">
              <TransitStopsLayer onStopClick={(stopId) => setSearchStopId(stopId)} />
            </Overlay>
            <Overlay name="Stations Vélib">
              <VelibStationsLayer />
            </Overlay>
          </LeafletMap>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
          <p className="text-sm text-blue-800">
            💡 <strong>Astuce:</strong> Cliquez sur un arrêt sur la carte pour voir les prochains passages en temps réel
          </p>
        </div>

        {departuresLoading && (
          <div className="bg-white rounded-lg shadow p-6">
            <div className="animate-pulse">Chargement des prochains passages...</div>
          </div>
        )}

        {departuresError && (
          <div className="bg-yellow-50 border-2 border-yellow-300 rounded-lg p-6">
            <p className="text-yellow-800 font-semibold">Aucune donnée temps réel disponible</p>
            <p className="text-sm text-yellow-700 mt-1">
              Cet arrêt n'a pas de données temps réel actuellement ou l'ID est incorrect
            </p>
          </div>
        )}

        {departures && (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="bg-blue-600 text-white px-6 py-4">
              <h3 className="text-lg font-semibold">{departures.stop_name}</h3>
              <p className="text-sm text-blue-100">{departures.stop_id}</p>
            </div>

            {departures.departures.length === 0 ? (
              <div className="p-6 text-center text-gray-500">
                Aucun passage prévu dans les prochaines minutes
              </div>
            ) : (
              <div className="divide-y">
                {departures.departures.map((departure, index) => {
                  const minutes = getMinutesUntil(departure.expected_arrival_time)
                  return (
                    <div key={index} className="p-4 hover:bg-gray-50">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className="bg-blue-600 text-white px-3 py-1 rounded font-bold">
                            {departure.line_name}
                          </div>
                          <div>
                            <div className="font-semibold text-gray-900">
                              {departure.destination_name}
                            </div>
                            <div className="text-sm text-gray-500">
                              {new Date(departure.expected_arrival_time).toLocaleTimeString('fr-FR', {
                                hour: '2-digit',
                                minute: '2-digit'
                              })}
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className={`text-2xl font-bold ${minutes <= 2 ? 'text-red-600' : minutes <= 5 ? 'text-orange-600' : 'text-green-600'}`}>
                            {minutes === 0 ? 'À quai' : `${minutes} min`}
                          </div>
                          <div className="text-xs text-gray-500 uppercase">
                            {departure.arrival_status === 'onTime' ? 'À l\'heure' : departure.arrival_status}
                          </div>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Spatial Pollution Analysis */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Pollution à Proximité des Arrêts
        </h2>

        {spatialLoading ? (
          <div className="bg-white rounded-lg shadow p-6">
            <div className="animate-pulse">Analyse spatiale en cours...</div>
          </div>
        ) : spatialAnalysis ? (
          <>
            {/* Comparison Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              {/* Near Transit Card */}
              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-sm text-gray-600 mb-1">
                  🚇 {spatialAnalysis.zones.near_transit.description}
                </div>
                <div className="flex items-baseline gap-2 mb-2">
                  <div className="text-4xl font-bold text-red-600">
                    {spatialAnalysis.zones.near_transit.avg_pm25}
                  </div>
                  <div className="text-gray-600">μg/m³</div>
                </div>
                <div className="text-sm text-gray-500">
                  {spatialAnalysis.zones.near_transit.sensors_count} capteurs · {spatialAnalysis.zones.near_transit.measurements_count} mesures
                </div>
              </div>

              {/* Far Transit Card */}
              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-sm text-gray-600 mb-1">
                  🏠 {spatialAnalysis.zones.far_transit.description}
                </div>
                <div className="flex items-baseline gap-2 mb-2">
                  <div className="text-4xl font-bold text-green-600">
                    {spatialAnalysis.zones.far_transit.avg_pm25}
                  </div>
                  <div className="text-gray-600">μg/m³</div>
                </div>
                <div className="text-sm text-gray-500">
                  {spatialAnalysis.zones.far_transit.sensors_count} capteurs · {spatialAnalysis.zones.far_transit.measurements_count} mesures
                </div>
              </div>
            </div>

            {/* Comparison Result */}
            <div className={`rounded-lg border-2 p-6 mb-4 ${
              spatialAnalysis.comparison.is_significant
                ? 'bg-orange-50 border-orange-300'
                : 'bg-green-50 border-green-300'
            }`}>
              <div className="font-semibold text-lg mb-2">
                {spatialAnalysis.comparison.is_significant ? '⚠️ Différence Significative' : '✅ Pollution Homogène'}
              </div>
              <div className="text-sm">
                {spatialAnalysis.comparison.difference_pm25 > 0 ? (
                  <>
                    Pollution <strong>+{spatialAnalysis.comparison.difference_pm25} μg/m³</strong> plus élevée
                    près des arrêts ({spatialAnalysis.comparison.percent_increase > 0 ? '+' : ''}{spatialAnalysis.comparison.percent_increase}%)
                  </>
                ) : (
                  <>
                    Pollution <strong>{spatialAnalysis.comparison.difference_pm25} μg/m³</strong> plus faible
                    près des arrêts
                  </>
                )}
              </div>
            </div>

            {/* Insights */}
            {spatialAnalysis.insights && spatialAnalysis.insights.length > 0 && (
              <div className="bg-white rounded-lg shadow p-6 mb-4">
                <h3 className="font-semibold text-lg mb-3">Analyse Spatiale</h3>
                <ul className="space-y-2">
                  {spatialAnalysis.insights.map((insight, index) => (
                    <li key={index} className="flex items-start gap-2 text-sm">
                      <span className="text-blue-600 mt-1">→</span>
                      <span className="text-gray-800">{insight}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Sensor Details Table */}
            {spatialAnalysis.sensor_details && spatialAnalysis.sensor_details.length > 0 && (
              <div className="bg-white rounded-lg shadow overflow-hidden">
                <div className="bg-gray-50 px-6 py-3 border-b">
                  <h3 className="font-semibold">Détails par Capteur</h3>
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Capteur
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Arrêt le plus proche
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Distance
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          PM2.5 moyen
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Zone
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {spatialAnalysis.sensor_details.map((sensor) => (
                        <tr key={sensor.sensor_id}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {sensor.sensor_id}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {sensor.nearest_hub}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {sensor.distance_to_nearest_stop}m
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">
                            <span className={`font-semibold ${
                              sensor.avg_pm25 > 50 ? 'text-red-600' :
                              sensor.avg_pm25 > 25 ? 'text-orange-600' :
                              'text-green-600'
                            }`}>
                              {sensor.avg_pm25} μg/m³
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">
                            <span className={`px-2 py-1 rounded text-xs font-semibold ${
                              sensor.zone === 'near_transit' ? 'bg-red-100 text-red-800' :
                              sensor.zone === 'far_transit' ? 'bg-green-100 text-green-800' :
                              'bg-gray-100 text-gray-800'
                            }`}>
                              {sensor.zone === 'near_transit' ? 'Près transit' :
                               sensor.zone === 'far_transit' ? 'Loin transit' :
                               'Moyenne'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </>
        ) : null}
      </div>

      {/* Info Box */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <div className="flex items-start gap-4">
          <div className="text-3xl">ℹ️</div>
          <div>
            <h4 className="font-semibold text-blue-900 mb-2">
              Comment utiliser cette page ?
            </h4>
            <ul className="text-sm text-blue-800 space-y-2">
              <li>
                <strong>Vélib' :</strong> Stats en temps réel du réseau Vélib' Métropole (1000 stations)
              </li>
              <li>
                <strong>Perturbations :</strong> Alertes trafic sur les lignes RATP/SNCF en temps réel
              </li>
              <li>
                <strong>Prochains passages :</strong> Horaires temps réel aux arrêts (format SIRI Lite)
              </li>
              <li>
                <strong>Exemples d'ID d'arrêts :</strong> Recherchez dans le catalogue IDFM PRIM
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
