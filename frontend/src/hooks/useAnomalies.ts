import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface AnomalyDetectionResponse {
  city: string
  total_anomalies: number
  zscore_count: number
  isolation_forest_count: number
  anomalies: any[]
  lookback_days: number
  detected_at: string
}

interface AnomalyStats {
  city: string
  days_analyzed: number
  total_anomalies: number
  severity_distribution: {
    low: number
    medium: number
    high: number
    critical: number
  }
  method_distribution: {
    z_score: number
    isolation_forest: number
  }
  detected_at: string
}

export function useDetectAnomalies(city: string, lookbackDays: number = 7) {
  return useQuery<AnomalyDetectionResponse>({
    queryKey: ['anomalies-detect', city, lookbackDays],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE_URL}/api/v1/anomalies/detect`, {
        params: { city, lookback_days: lookbackDays }
      })
      return response.data
    },
    staleTime: 300000, // 5 minutes
    refetchInterval: 300000 // Auto-refresh every 5 minutes
  })
}

export function useRecentAnomalies(city?: string, hours: number = 24, limit: number = 50) {
  return useQuery<any[]>({
    queryKey: ['anomalies-recent', city, hours, limit],
    queryFn: async () => {
      const params: any = { hours, limit }
      if (city) params.city = city

      const response = await axios.get(`${API_BASE_URL}/api/v1/anomalies/recent`, { params })
      return response.data
    },
    staleTime: 60000, // 1 minute
    refetchInterval: 60000
  })
}

export function useAnomalyStats(city: string, days: number = 7) {
  return useQuery<AnomalyStats>({
    queryKey: ['anomaly-stats', city, days],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE_URL}/api/v1/anomalies/stats`, {
        params: { city, days }
      })
      return response.data
    },
    staleTime: 300000
  })
}

export function useDetectAndAlert() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ city, lookback_days }: { city: string; lookback_days?: number }) => {
      const response = await axios.post(`${API_BASE_URL}/api/v1/anomalies/detect-and-alert`, null, {
        params: { city, lookback_days: lookback_days || 1 }
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['anomalies-recent'] })
      queryClient.invalidateQueries({ queryKey: ['anomalies-detect'] })
    }
  })
}
