import { useQuery } from '@tanstack/react-query'
import { airQualityAPI } from '../services/api'

export const useCurrentAirQuality = (city: string) => {
  return useQuery({
    queryKey: ['airQuality', 'current', city],
    queryFn: () => airQualityAPI.getCurrent(city),
    refetchInterval: 5 * 60 * 1000,
  })
}

export const useAirQualityHistory = (city: string) => {
  return useQuery({
    queryKey: ['airQuality', 'history', city],
    queryFn: () => airQualityAPI.getHistory(city, 24),
  })
}
