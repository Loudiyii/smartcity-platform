# Skill: Frontend Dashboard (React + TypeScript)

## Purpose
Develop and maintain the React frontend for the Smart City dashboard, including real-time data visualization, interactive maps, charts, and responsive UI components.

## When to Use
- Creating new React components
- Working with Chart.js for data visualization
- Implementing Leaflet maps with multiple layers
- Managing state with Zustand or TanStack Query
- Styling with Tailwind CSS
- Fetching data from backend API

## Tech Stack

```
Frontend Stack:
├── React 18 + TypeScript 5
├── Vite 5 (build tool)
├── TanStack Query (server state)
├── Zustand (global state)
├── React Router v6 (routing)
├── Tailwind CSS 3 (styling)
├── Chart.js 4 (charts via react-chartjs-2)
├── Leaflet.js (maps via react-leaflet)
└── Axios (HTTP client)
```

## Architecture

```
frontend/src/
├── main.tsx                 # App entry point
├── App.tsx                  # Root component
├── router.tsx               # Route configuration
│
├── pages/                   # Page components
│   ├── Home.tsx
│   ├── Dashboard.tsx
│   ├── DashboardMap.tsx
│   ├── Predictions.tsx
│   ├── Admin.tsx
│   └── Reports.tsx
│
├── components/              # Reusable components
│   ├── Dashboard/
│   │   ├── KPICard.tsx
│   │   ├── AirQualityChart.tsx
│   │   └── PollutantFilter.tsx
│   ├── Map/
│   │   ├── LeafletMap.tsx
│   │   ├── IoTSensorsLayer.tsx
│   │   └── HeatmapLayer.tsx
│   ├── Charts/
│   │   ├── LineChart.tsx
│   │   ├── BarChart.tsx
│   │   └── GaugeChart.tsx
│   └── UI/
│       ├── Button.tsx
│       ├── Card.tsx
│       └── LoadingSpinner.tsx
│
├── services/                # API clients
│   ├── api.ts
│   ├── airQualityService.ts
│   └── weatherService.ts
│
├── hooks/                   # Custom hooks
│   ├── useAirQuality.ts
│   ├── useWeather.ts
│   └── useRealtime.ts
│
├── stores/                  # Zustand stores
│   ├── authStore.ts
│   └── mapStore.ts
│
├── types/                   # TypeScript types
│   ├── airQuality.ts
│   ├── weather.ts
│   └── api.ts
│
└── utils/
    ├── formatters.ts
    └── constants.ts
```

## Core Patterns

### 1. React Component Structure

```typescript
// components/Dashboard/KPICard.tsx
import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface KPICardProps {
  title: string;
  value: number;
  unit: string;
  trend?: 'up' | 'down';
  trendValue?: number;
  severity?: 'good' | 'moderate' | 'poor' | 'unhealthy';
}

export const KPICard: React.FC<KPICardProps> = ({
  title,
  value,
  unit,
  trend,
  trendValue,
  severity = 'good'
}) => {
  const severityColors = {
    good: 'bg-green-100 border-green-500',
    moderate: 'bg-yellow-100 border-yellow-500',
    poor: 'bg-orange-100 border-orange-500',
    unhealthy: 'bg-red-100 border-red-500'
  };

  return (
    <div className={`rounded-lg border-l-4 p-6 ${severityColors[severity]}`}>
      <h3 className="text-sm font-medium text-gray-600">{title}</h3>
      <div className="mt-2 flex items-baseline">
        <p className="text-3xl font-semibold text-gray-900">
          {value.toFixed(1)}
        </p>
        <span className="ml-2 text-sm text-gray-500">{unit}</span>
      </div>
      {trend && trendValue !== undefined && (
        <div className="mt-2 flex items-center text-sm">
          {trend === 'up' ? (
            <TrendingUp className="h-4 w-4 text-red-500" />
          ) : (
            <TrendingDown className="h-4 w-4 text-green-500" />
          )}
          <span className={trend === 'up' ? 'text-red-500' : 'text-green-500'}>
            {Math.abs(trendValue)}% vs yesterday
          </span>
        </div>
      )}
    </div>
  );
};
```

### 2. Data Fetching with TanStack Query

```typescript
// hooks/useAirQuality.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { airQualityService } from '../services/airQualityService';
import type { AirQualityData } from '../types/airQuality';

export const useCurrentAirQuality = (city: string) => {
  return useQuery({
    queryKey: ['airQuality', 'current', city],
    queryFn: () => airQualityService.getCurrent(city),
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
    staleTime: 2 * 60 * 1000, // Data fresh for 2 minutes
  });
};

export const useAirQualityHistory = (
  city: string,
  startDate?: Date,
  endDate?: Date
) => {
  return useQuery({
    queryKey: ['airQuality', 'history', city, startDate, endDate],
    queryFn: () => airQualityService.getHistory(city, startDate, endDate),
    enabled: !!city,
  });
};

export const useCreateMeasurement = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: airQualityService.createMeasurement,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['airQuality'] });
    },
  });
};
```

### 3. API Service Layer

```typescript
// services/airQualityService.ts
import axios from './api';
import type { AirQualityData, AirQualityCreate } from '../types/airQuality';

export const airQualityService = {
  async getCurrent(city: string): Promise<AirQualityData> {
    const { data } = await axios.get(`/api/v1/air-quality/current`, {
      params: { city }
    });
    return data;
  },

  async getHistory(
    city: string,
    startDate?: Date,
    endDate?: Date,
    limit = 100
  ): Promise<AirQualityData[]> {
    const { data } = await axios.get(`/api/v1/air-quality/history`, {
      params: {
        city,
        start_date: startDate?.toISOString(),
        end_date: endDate?.toISOString(),
        limit
      }
    });
    return data;
  },

  async createMeasurement(measurement: AirQualityCreate): Promise<AirQualityData> {
    const { data } = await axios.post(`/api/v1/air-quality/measurements`, measurement);
    return data;
  }
};

// services/api.ts - Axios configuration
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Request interceptor for auth
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

### 4. Chart.js Integration

```typescript
// components/Charts/AirQualityChart.tsx
import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import type { AirQualityData } from '../../types/airQuality';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface AirQualityChartProps {
  data: AirQualityData[];
  pollutant: 'pm25' | 'pm10' | 'no2' | 'o3';
}

export const AirQualityChart: React.FC<AirQualityChartProps> = ({ data, pollutant }) => {
  const chartData = {
    labels: data.map(d => new Date(d.timestamp).toLocaleTimeString()),
    datasets: [
      {
        label: pollutant.toUpperCase(),
        data: data.map(d => d[pollutant]),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        fill: true,
        tension: 0.4,
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: `${pollutant.toUpperCase()} Levels (Last 24h)`,
      },
      tooltip: {
        callbacks: {
          label: (context: any) => `${context.parsed.y.toFixed(1)} μg/m³`
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Concentration (μg/m³)'
        }
      }
    }
  };

  return (
    <div className="h-80">
      <Line data={chartData} options={options} />
    </div>
  );
};
```

### 5. Leaflet Map with Layers

```typescript
// components/Map/LeafletMap.tsx
import React, { useState } from 'react';
import { MapContainer, TileLayer, LayersControl } from 'react-leaflet';
import { IoTSensorsLayer } from './IoTSensorsLayer';
import { HeatmapLayer } from './HeatmapLayer';
import 'leaflet/dist/leaflet.css';

const { BaseLayer, Overlay } = LayersControl;

export const LeafletMap: React.FC = () => {
  const [center] = useState<[number, number]>([48.8566, 2.3522]); // Paris
  const [zoom] = useState(12);

  return (
    <MapContainer
      center={center}
      zoom={zoom}
      style={{ height: '600px', width: '100%' }}
      className="rounded-lg shadow-lg"
    >
      <LayersControl position="topright">
        <BaseLayer checked name="OpenStreetMap">
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
        </BaseLayer>
        <BaseLayer name="Satellite">
          <TileLayer
            attribution='&copy; Esri'
            url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
          />
        </BaseLayer>

        <Overlay checked name="IoT Sensors">
          <IoTSensorsLayer />
        </Overlay>
        <Overlay name="Air Quality Heatmap">
          <HeatmapLayer />
        </Overlay>
      </LayersControl>
    </MapContainer>
  );
};

// components/Map/IoTSensorsLayer.tsx
import React from 'react';
import { Marker, Popup } from 'react-leaflet';
import { Icon } from 'leaflet';
import { useSensors } from '../../hooks/useSensors';

const sensorIcon = new Icon({
  iconUrl: '/sensor-icon.png',
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32]
});

export const IoTSensorsLayer: React.FC = () => {
  const { data: sensors, isLoading } = useSensors();

  if (isLoading || !sensors) return null;

  return (
    <>
      {sensors.map((sensor) => (
        <Marker
          key={sensor.sensor_id}
          position={[sensor.location.lat, sensor.location.lon]}
          icon={sensorIcon}
        >
          <Popup>
            <div className="p-2">
              <h3 className="font-bold">{sensor.name}</h3>
              <p className="text-sm">Status: {sensor.status}</p>
              <p className="text-sm">Last reading: {new Date(sensor.last_reading_at).toLocaleString()}</p>
            </div>
          </Popup>
        </Marker>
      ))}
    </>
  );
};
```

### 6. Zustand State Management

```typescript
// stores/authStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  role: string;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  setUser: (user: User, token: string) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      isAuthenticated: false,

      login: async (email: string, password: string) => {
        const response = await fetch('/api/v1/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });
        const data = await response.json();
        set({
          user: data.user,
          accessToken: data.access_token,
          isAuthenticated: true
        });
        localStorage.setItem('access_token', data.access_token);
      },

      logout: () => {
        set({ user: null, accessToken: null, isAuthenticated: false });
        localStorage.removeItem('access_token');
      },

      setUser: (user: User, token: string) => {
        set({ user, accessToken: token, isAuthenticated: true });
      }
    }),
    { name: 'auth-storage' }
  )
);
```

### 7. TypeScript Types

```typescript
// types/airQuality.ts
export interface AirQualityData {
  id: number;
  source: string;
  city: string;
  location?: {
    lat: number;
    lon: number;
    name?: string;
  };
  aqi?: number;
  pm25?: number;
  pm10?: number;
  no2?: number;
  o3?: number;
  so2?: number;
  timestamp: string;
  created_at: string;
}

export interface AirQualityCreate {
  source: string;
  city?: string;
  location?: {
    lat: number;
    lon: number;
    name?: string;
  };
  pm25?: number;
  pm10?: number;
  no2?: number;
  timestamp?: string;
}

export type Pollutant = 'pm25' | 'pm10' | 'no2' | 'o3' | 'so2';

export type AirQualitySeverity = 'good' | 'moderate' | 'poor' | 'unhealthy' | 'dangerous';
```

### 8. React Router Configuration

```typescript
// router.tsx
import { createBrowserRouter } from 'react-router-dom';
import { Home } from './pages/Home';
import { Dashboard } from './pages/Dashboard';
import { DashboardMap } from './pages/DashboardMap';
import { Predictions } from './pages/Predictions';
import { Admin } from './pages/Admin';
import { ProtectedRoute } from './components/ProtectedRoute';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Home />
  },
  {
    path: '/dashboard',
    element: <Dashboard />
  },
  {
    path: '/dashboard/map',
    element: <DashboardMap />
  },
  {
    path: '/dashboard/predictions',
    element: <Predictions />
  },
  {
    path: '/admin',
    element: (
      <ProtectedRoute>
        <Admin />
      </ProtectedRoute>
    )
  }
]);

// main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { RouterProvider } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { router } from './router';
import './index.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000,
    }
  }
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </React.StrictMode>
);
```

## Best Practices

### Component Design
- Keep components small and focused (< 200 lines)
- Use functional components with hooks
- Extract reusable logic into custom hooks
- Props should be typed with TypeScript interfaces

### State Management
- Use TanStack Query for server state (API data)
- Use Zustand for global client state (auth, UI preferences)
- Keep component state local when possible
- Avoid prop drilling with context or stores

### Performance
- Memoize expensive computations with `useMemo`
- Memoize callbacks with `useCallback`
- Use React.lazy for code splitting
- Optimize re-renders with React.memo

### Styling
- Use Tailwind utility classes
- Create reusable component variants
- Mobile-first responsive design
- Consistent spacing and colors

### Error Handling
- Show loading states during data fetching
- Display user-friendly error messages
- Implement error boundaries for crash recovery
- Retry failed requests automatically

## Common Tasks

### Adding a New Page
1. Create component in `src/pages/`
2. Add route in `router.tsx`
3. Create navigation link in header

### Creating a Chart
1. Register Chart.js components
2. Prepare data in correct format
3. Configure options (responsive, tooltips)
4. Wrap in container with fixed height

### Fetching Real-time Data
```typescript
useQuery({
  queryKey: ['realtime', 'sensors'],
  queryFn: fetchSensors,
  refetchInterval: 15000, // 15 seconds
});
```

## References
- React Docs: https://react.dev
- TanStack Query: https://tanstack.com/query/latest
- Chart.js: https://www.chartjs.org/
- Leaflet: https://leafletjs.com/
- Tailwind CSS: https://tailwindcss.com/

## Trade-offs

**TanStack Query vs. Redux:**
- TanStack Query: Better for server state, less boilerplate
- Redux: Better for complex client state, more verbose

**Chart.js vs. D3.js:**
- Chart.js: Easier to use, good for standard charts
- D3.js: More flexible, steeper learning curve

**Tailwind vs. CSS Modules:**
- Tailwind: Faster development, utility-first
- CSS Modules: Better for complex custom designs
