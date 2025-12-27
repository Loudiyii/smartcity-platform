import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'

interface CorrelationData {
  city: string
  days: number
  data_points: number
  timestamps: string[]
  pollution: {
    pm25: number[]
    pm10: number[]
    no2: number[]
    o3: number[]
    aqi: number[]
  }
  weather: {
    temperature: number[]
    humidity: number[]
    pressure: number[]
    wind_speed: number[]
  }
}

interface CorrelationStats {
  city: string
  days_analyzed: number
  data_points: number
  correlations: {
    pm25_vs_weather: Record<string, number>
    pm10_vs_weather: Record<string, number>
    no2_vs_weather: Record<string, number>
  }
}

export function useCorrelationData(city: string, days: number = 7) {
  return useQuery<CorrelationData>({
    queryKey: ['correlation-data', city, days],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE_URL}/api/v1/analytics/correlation`, {
        params: { city, days }
      })
      return response.data
    },
    staleTime: 300000 // 5 minutes
  })
}

export function useCorrelationStats(city: string, days: number = 7) {
  return useQuery<CorrelationStats>({
    queryKey: ['correlation-stats', city, days],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE_URL}/api/v1/analytics/correlation/stats`, {
        params: { city, days }
      })
      return response.data
    },
    staleTime: 300000
  })
}
