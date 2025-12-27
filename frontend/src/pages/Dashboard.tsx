import React from 'react'
import { useCurrentAirQuality, useAirQualityHistory } from '../hooks/useAirQuality'
import { KPICard } from '../components/Dashboard/KPICard'
import { AirQualityChart } from '../components/Dashboard/AirQualityChart'
import { VelibCard } from '../components/Dashboard/VelibCard'
import { TrafficAlertsWidget } from '../components/Dashboard/TrafficAlertsWidget'
import { AnomalyWidget } from '../components/Dashboard/AnomalyWidget'

const getSeverity = (pm25: number) => {
  if (pm25 <= 12) return 'good'
  if (pm25 <= 35.4) return 'moderate'
  if (pm25 <= 55.4) return 'poor'
  return 'unhealthy'
}

export const Dashboard: React.FC = () => {
  const { data: current, isLoading: loadingCurrent } = useCurrentAirQuality('paris')
  const { data: history, isLoading: loadingHistory } = useAirQualityHistory('paris')

  if (loadingCurrent) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg">Loading...</div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto py-6 px-4">
      <h1 className="text-3xl font-bold mb-8">Smart City Dashboard</h1>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <KPICard
          title="PM2.5"
          value={current?.pm25 || 0}
          unit="μg/m³"
          severity={getSeverity(current?.pm25 || 0)}
        />
        <KPICard
          title="PM10"
          value={current?.pm10 || 0}
          unit="μg/m³"
          severity={current?.pm10 > 50 ? 'poor' : 'good'}
        />
        <KPICard
          title="NO2"
          value={current?.no2 || 0}
          unit="μg/m³"
          severity={current?.no2 > 40 ? 'moderate' : 'good'}
        />
      </div>

      {/* Air Quality Chart */}
      {!loadingHistory && history?.measurements && (
        <div className="bg-white p-6 rounded-lg shadow mb-8">
          <AirQualityChart data={history.measurements} />
        </div>
      )}

      {/* IDFM Mobility Data - Phase 2 */}
      <div className="mt-8">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">Mobilité Temps Réel (IDFM)</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <VelibCard />
          <TrafficAlertsWidget />
        </div>
      </div>

      {/* Anomaly Detection - Phase 2 Epic 3 */}
      <div className="mt-8">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">Détection d'Anomalies</h2>
        <AnomalyWidget />
      </div>
    </div>
  )
}
