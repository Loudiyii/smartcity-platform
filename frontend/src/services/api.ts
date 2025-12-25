import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
})

export const airQualityAPI = {
  getCurrent: async (city: string) => {
    const { data } = await api.get(`/api/v1/air-quality/current`, { params: { city } })
    return data
  },
  getHistory: async (city: string, limit = 24) => {
    const { data } = await api.get(`/api/v1/air-quality/history`, { params: { city, limit } })
    return data
  }
}

export default api
