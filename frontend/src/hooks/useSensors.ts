/**
 * TanStack Query hooks for IoT sensors
 */

import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'

export interface SensorMetadata {
  sensor_id: string
  name: string
  location: {
    lat: number
    lon: number
    name?: string
  }
  status: string
  last_reading_at: string | null
}

export function useSensors() {
  return useQuery<SensorMetadata[]>({
    queryKey: ['sensors'],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE_URL}/api/v1/sensors/`)
      // API returns {status, count, sensors: [...]} - extract the sensors array
      return response.data.sensors || []
    },
    staleTime: 300000, // 5 minutes - sensor locations don't change often
  })
}
