import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface AQILevel {
  name: string
  color: string
  description: string
}

interface PredictionRange {
  lower: number
  upper: number
}

interface ModelMetrics {
  r2: number
  mape: number
  rmse: number
}

export interface Prediction {
  city: string
  predicted_pm25: number
  confidence: number
  prediction_range: PredictionRange
  aqi_level: AQILevel
  prediction_for: string
  predicted_at: string
  model_metrics: ModelMetrics
}

interface TrainingRequest {
  city: string
  days?: number
  n_estimators?: number
  max_depth?: number
}

interface TrainingResponse {
  status: string
  metrics: Record<string, number>
  city: string
  trained_at: string
  message: string
}

export function usePM25Prediction(city: string) {
  return useQuery<Prediction>({
    queryKey: ['pm25-prediction', city],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE_URL}/api/v1/predictions/pm25`, {
        params: { city }
      })
      return response.data
    },
    staleTime: 3600000, // 1 hour
    retry: 1
  })
}

export function useTrainModel() {
  const queryClient = useQueryClient()

  return useMutation<TrainingResponse, Error, TrainingRequest>({
    mutationFn: async (request) => {
      const response = await axios.post(`${API_BASE_URL}/api/v1/predictions/train`, request)
      return response.data
    },
    onSuccess: (data) => {
      // Invalidate predictions for this city
      queryClient.invalidateQueries({ queryKey: ['pm25-prediction', data.city] })
    }
  })
}

export function usePredictionHistory(city: string, limit: number = 10) {
  return useQuery<any[]>({
    queryKey: ['prediction-history', city, limit],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE_URL}/api/v1/predictions/history`, {
        params: { city, limit }
      })
      return response.data
    },
    staleTime: 300000 // 5 minutes
  })
}
