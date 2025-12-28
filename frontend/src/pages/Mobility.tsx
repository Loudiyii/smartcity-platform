import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../services/api'

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

export const Mobility: React.FC = () => {
  const [stopId, setStopId] = useState('')
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
  const { data: departures, isLoading: departuresLoading, error: departuresError } = useQuery<StopDepartures>({
    queryKey: ['next-departures', searchStopId],
    queryFn: async () => {
      const response = await api.get(`/api/v1/mobility/transit/next-departures/${searchStopId}?limit=10`)
      return response.data
    },
    enabled: !!searchStopId,
    retry: false
  })

  const handleSearch = () => {
    setSearchStopId(stopId)
  }

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
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Prochains Passages</h2>

        <div className="bg-white rounded-lg shadow p-6 mb-4">
          <div className="flex gap-3">
            <input
              type="text"
              value={stopId}
              onChange={(e) => setStopId(e.target.value)}
              placeholder="ID d'arrêt (ex: STIF:StopPoint:Q:41322:)"
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <button
              onClick={handleSearch}
              disabled={!stopId}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Rechercher
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Les données temps réel ne sont disponibles que pour certains arrêts du réseau IDFM
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
