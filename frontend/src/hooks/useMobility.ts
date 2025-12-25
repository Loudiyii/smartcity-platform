/**
 * TanStack Query hooks for IDFM mobility data
 * Vélib stations, traffic disruptions, transit stops
 */

import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Types
export interface VelibStation {
  station_id: string
  name: string
  num_bikes_available: number
  num_docks_available: number
  latitude: number
  longitude: number
  is_installed: boolean
  is_returning: boolean
  is_renting: boolean
  last_reported: string | null
  capacity: number
  availability_percent: number
}

export interface TrafficDisruption {
  disruption_id: string
  line_id: string | null
  line_name: string | null
  severity: string
  message: string
  start_time: string | null
  end_time: string | null
  is_active: boolean
  created_at: string
}

export interface TransitStop {
  stop_id: string
  stop_name: string
  stop_lat: number
  stop_lon: number
  zone_id: string | null
  location_type: number
}

export interface VelibStats {
  total_stations: number
  total_bikes_available: number
  total_docks_available: number
  average_availability_percent: number
}

// Hooks
export function useVelibStations(limit: number = 50) {
  return useQuery<VelibStation[]>({
    queryKey: ['velib-stations', limit],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE_URL}/api/v1/mobility/velib/stations`, {
        params: { limit }
      })
      return response.data
    },
    staleTime: 60000, // 1 minute
    refetchInterval: 60000 // Refetch every minute
  })
}

export function useVelibStats() {
  return useQuery<VelibStats>({
    queryKey: ['velib-stats'],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE_URL}/api/v1/mobility/velib/stats`)
      return response.data
    },
    staleTime: 60000,
    refetchInterval: 60000
  })
}

export function useTrafficDisruptions(severity?: string) {
  return useQuery<TrafficDisruption[]>({
    queryKey: ['traffic-disruptions', severity],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE_URL}/api/v1/mobility/traffic-disruptions`, {
        params: { severity, active_only: true }
      })
      return response.data
    },
    staleTime: 120000, // 2 minutes
    refetchInterval: 120000
  })
}

export function useTransitStops(limit: number = 50) {
  return useQuery<TransitStop[]>({
    queryKey: ['transit-stops', limit],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE_URL}/api/v1/mobility/transit/stops`, {
        params: { limit }
      })
      return response.data
    },
    staleTime: 300000, // 5 minutes (stops don't change often)
    refetchInterval: false // No auto-refetch for static data
  })
}
