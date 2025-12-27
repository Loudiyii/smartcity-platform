import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'

interface CorrelationData {
  value: number
  strength: string
  direction: string
  interpretation?: string
}

interface TimeSeriesData {
  timestamps: string[]
  pm25: number[]
  traffic_disruptions?: number[]
  velib_available?: number[]
  velib_usage?: number[]
}

interface Statistics {
  pm25_mean: number
  pm25_max?: number
  pm25_min?: number
  traffic_mean?: number
  traffic_max?: number
  traffic_min?: number
  velib_avg_available?: number
  velib_avg_usage?: number
}

interface TrafficPollutionResponse {
  status: string
  city: string
  period_days: number
  data_points: number
  correlation: CorrelationData
  time_series: TimeSeriesData
  statistics: Statistics
  insights: string[]
  analyzed_at: string
}

interface VelibPollutionResponse {
  status: string
  city: string
  period_days: number
  data_points: number
  correlation: CorrelationData
  time_series: TimeSeriesData
  statistics: Statistics
  insights: string[]
  analyzed_at: string
}

interface PolicyRecommendation {
  priority: string
  action: string
  description: string
  expected_impact: string
}

interface CombinedImpactResponse {
  city: string
  period_days: number
  traffic_analysis: TrafficPollutionResponse
  velib_analysis: VelibPollutionResponse
  overall_insights: string[]
  recommendations: PolicyRecommendation[]
  analyzed_at: string
}

export function useTrafficPollutionCorrelation(city: string, days: number = 7) {
  return useQuery<TrafficPollutionResponse>({
    queryKey: ['mobility-impact', 'traffic-pollution', city, days],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE_URL}/api/v1/mobility-impact/traffic-pollution`, {
        params: { city, days }
      })
      return response.data
    },
    staleTime: 300000, // 5 minutes
    enabled: !!city
  })
}

export function useVelibPollutionCorrelation(city: string = 'Paris', days: number = 7) {
  return useQuery<VelibPollutionResponse>({
    queryKey: ['mobility-impact', 'velib-pollution', city, days],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE_URL}/api/v1/mobility-impact/velib-pollution`, {
        params: { city, days }
      })
      return response.data
    },
    staleTime: 300000,
    enabled: !!city
  })
}

export function useCombinedMobilityImpact(city: string, days: number = 7) {
  return useQuery<CombinedImpactResponse>({
    queryKey: ['mobility-impact', 'combined', city, days],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE_URL}/api/v1/mobility-impact/combined`, {
        params: { city, days }
      })
      return response.data
    },
    staleTime: 300000,
    enabled: !!city
  })
}
