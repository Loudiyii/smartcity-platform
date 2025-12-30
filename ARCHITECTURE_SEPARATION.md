# Architecture & Separation of Concerns

Comprehensive guide to the architectural patterns, layer separation, and code organization principles used in the Smart City Platform.

## Table of Contents

- [Architectural Overview](#architectural-overview)
- [Layer Architecture](#layer-architecture)
- [Backend Architecture](#backend-architecture)
- [Frontend Architecture](#frontend-architecture)
- [Dependency Injection](#dependency-injection)
- [State Management](#state-management)
- [API Design Principles](#api-design-principles)
- [Code Organization](#code-organization)
- [Design Patterns](#design-patterns)
- [Data Flow](#data-flow)

---

## Architectural Overview

### Three-Tier Architecture

The Smart City Platform follows a classic **three-tier architecture** with clear separation between presentation, business logic, and data access layers.

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION TIER                         │
│                                                              │
│  React Components (Pages, UI Components)                    │
│  ├─ User Interface                                          │
│  ├─ User Input Handling                                     │
│  └─ Display Logic                                           │
│                                                              │
│  Responsibilities:                                          │
│  - Render UI components                                     │
│  - Handle user interactions                                 │
│  - Display data from business tier                          │
│  - NO business logic                                        │
│  - NO direct API calls (use hooks)                          │
│                                                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                    Custom Hooks
                    (useAirQuality, usePredictions)
                         │
┌────────────────────────▼────────────────────────────────────┐
│                     BUSINESS TIER                            │
│                                                              │
│  FastAPI Routes → Services → ML Models                      │
│  ├─ Business Rules                                          │
│  ├─ Data Processing                                         │
│  ├─ ML Predictions                                          │
│  └─ External API Integration                                │
│                                                              │
│  Responsibilities:                                          │
│  - Process business logic                                   │
│  - Validate data                                            │
│  - Coordinate between layers                                │
│  - NO database queries (delegate to data tier)              │
│  - NO UI concerns                                           │
│                                                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                   Service Layer
                         │
┌────────────────────────▼────────────────────────────────────┐
│                      DATA TIER                               │
│                                                              │
│  Supabase PostgreSQL + ORM Layer                            │
│  ├─ Data Persistence                                        │
│  ├─ Query Execution                                         │
│  └─ Data Retrieval                                          │
│                                                              │
│  Responsibilities:                                          │
│  - Store and retrieve data                                  │
│  - Execute database queries                                 │
│  - Manage transactions                                      │
│  - NO business logic                                        │
│  - NO presentation logic                                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Key Principles

1. **Separation of Concerns:** Each layer has a single, well-defined responsibility
2. **Loose Coupling:** Layers interact through well-defined interfaces
3. **High Cohesion:** Related functionality is grouped together
4. **Dependency Inversion:** High-level modules don't depend on low-level modules
5. **Single Responsibility:** Each class/module does one thing well

---

## Layer Architecture

### Presentation Layer (Frontend)

**Location:** `frontend/src/`

**Responsibilities:**
- Display data to users
- Capture user input
- Navigate between views
- Client-side validation

**Does NOT:**
- Contain business logic
- Make direct database calls
- Perform complex calculations
- Handle authentication logic

**Example Structure:**
```typescript
// ✅ GOOD: Presentation layer
export const Dashboard: React.FC = () => {
  // Use custom hook for data fetching
  const { data: airQuality, isLoading } = useAirQuality('paris');

  if (isLoading) return <Spinner />;

  return (
    <div>
      <h1>Air Quality Dashboard</h1>
      <KPICard title="PM2.5" value={airQuality.pm25} />
    </div>
  );
};

// ❌ BAD: Business logic in presentation
export const Dashboard: React.FC = () => {
  const [data, setData] = useState(null);

  useEffect(() => {
    // Direct API call - should be in hook
    fetch('/api/v1/air-quality/current?city=paris')
      .then(res => res.json())
      .then(setData);
  }, []);

  // Complex calculation - should be in backend
  const aqi = calculateAQI(data.pm25, data.pm10);

  return <div>AQI: {aqi}</div>;
};
```

### Business Logic Layer (Backend Services)

**Location:** `backend/app/services/`

**Responsibilities:**
- Implement business rules
- Coordinate data access
- Process and transform data
- Validate business constraints

**Does NOT:**
- Directly access database (uses Supabase service)
- Render UI
- Handle HTTP requests (done by routes)

**Example Structure:**
```python
# ✅ GOOD: Business logic layer
class AirQualityService:
    """Business logic for air quality operations."""

    def __init__(self, supabase_service: SupabaseService):
        self.db = supabase_service

    async def get_current_with_forecast(self, city: str) -> Dict:
        """
        Get current air quality with J+1 forecast.

        Business rule: Include prediction only if confidence > 0.7
        """
        # Delegate data access to data layer
        current = await self.db.get_current_air_quality(city)
        prediction = await self.db.get_latest_prediction(city)

        # Business logic: Filter by confidence
        if prediction and prediction['confidence_score'] > 0.7:
            current['forecast'] = prediction

        return current

# ❌ BAD: Direct database access
class AirQualityService:
    async def get_current_with_forecast(self, city: str):
        # Direct SQL query - should be in data layer
        result = supabase.table('air_quality_measurements') \
            .select('*') \
            .eq('city', city) \
            .execute()
        return result.data
```

### Data Access Layer (Database Service)

**Location:** `backend/app/services/supabase_service.py`

**Responsibilities:**
- Execute database queries
- Handle CRUD operations
- Manage transactions
- Abstract database details

**Does NOT:**
- Contain business logic
- Validate business rules
- Transform data for presentation

**Example Structure:**
```python
# ✅ GOOD: Data access layer
class SupabaseService:
    """Data access layer for Supabase operations."""

    def __init__(self, client: Client):
        self.client = client

    async def get_current_air_quality(self, city: str) -> Optional[Dict]:
        """
        Fetch most recent air quality measurement for city.

        Pure data access - no business logic.
        """
        result = self.client.table('air_quality_measurements') \
            .select('*') \
            .eq('city', city) \
            .order('timestamp', desc=True) \
            .limit(1) \
            .execute()

        return result.data[0] if result.data else None

    async def insert_air_quality(self, data: Dict) -> Dict:
        """Insert new air quality measurement."""
        result = self.client.table('air_quality_measurements') \
            .insert(data) \
            .execute()

        return result.data[0]

# ❌ BAD: Business logic in data layer
class SupabaseService:
    async def get_current_air_quality(self, city: str):
        result = self.client.table('air_quality_measurements') \
            .select('*') \
            .eq('city', city) \
            .order('timestamp', desc=True) \
            .limit(1) \
            .execute()

        data = result.data[0]

        # Business logic - should be in service layer
        if data['pm25'] > 50:
            self.send_alert(city, data['pm25'])

        return data
```

---

## Backend Architecture

### Directory Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration management
│   ├── dependencies.py            # Dependency injection
│   │
│   ├── api/                       # API LAYER (Routes)
│   │   └── v1/                    # API version 1
│   │       ├── air_quality.py     # Air quality routes
│   │       ├── predictions.py     # ML prediction routes
│   │       ├── mobility.py        # Mobility data routes
│   │       ├── analytics.py       # Analytics routes
│   │       ├── alerts.py          # Alert routes
│   │       └── reports.py         # Report generation routes
│   │
│   ├── services/                  # BUSINESS LOGIC LAYER
│   │   ├── supabase_service.py    # Data access service
│   │   ├── mobility_service.py    # Mobility business logic
│   │   ├── alert_service.py       # Alert business logic
│   │   ├── pdf_service.py         # PDF generation logic
│   │   └── spatial_pollution_service.py
│   │
│   ├── ml/                        # MACHINE LEARNING LAYER
│   │   ├── trainer.py             # Model training
│   │   ├── predictor.py           # Prediction logic
│   │   ├── feature_engineering.py # Feature extraction
│   │   └── anomaly_detector.py    # Anomaly detection
│   │
│   ├── models/                    # DATA MODELS (Pydantic)
│   │   ├── air_quality.py         # Air quality models
│   │   ├── prediction.py          # Prediction models
│   │   ├── mobility.py            # Mobility models
│   │   ├── alert.py               # Alert models
│   │   └── sensor.py              # Sensor models
│   │
│   ├── simulators/                # IOT SIMULATION
│   │   └── iot_sensor.py          # Sensor simulation
│   │
│   └── utils/                     # UTILITIES
│       └── helpers.py             # Helper functions
```

### Request Flow (Backend)

```
1. HTTP Request
   │
   ▼
2. FastAPI Route (api/v1/air_quality.py)
   │
   ├─ Parse request parameters
   ├─ Validate input (Pydantic)
   └─ Inject dependencies
   │
   ▼
3. Service Layer (services/air_quality_service.py)
   │
   ├─ Apply business rules
   ├─ Coordinate data access
   └─ Process/transform data
   │
   ▼
4. Data Access Layer (services/supabase_service.py)
   │
   ├─ Execute database query
   ├─ Handle errors
   └─ Return raw data
   │
   ▼
5. Business Logic (Service)
   │
   ├─ Transform data
   ├─ Apply calculations
   └─ Return processed data
   │
   ▼
6. API Route
   │
   ├─ Serialize to JSON (Pydantic)
   └─ Return HTTP response
   │
   ▼
7. HTTP Response
```

### Example: Complete Request Flow

**Route Layer:**
```python
# app/api/v1/air_quality.py
@router.get("/current", response_model=AirQualityResponse)
async def get_current_air_quality(
    city: str = Query(...),
    service: AirQualityService = Depends(get_air_quality_service)
):
    """
    Route layer: Handle HTTP request, validate input, return response.

    Responsibilities:
    - Parse query parameters
    - Validate input (Pydantic)
    - Inject dependencies
    - Return HTTP response
    """
    data = await service.get_current_with_forecast(city)

    if not data:
        raise HTTPException(status_code=404, detail="No data found")

    return data  # Pydantic serialization
```

**Service Layer:**
```python
# app/services/air_quality_service.py
class AirQualityService:
    """
    Service layer: Business logic for air quality.

    Responsibilities:
    - Implement business rules
    - Coordinate data access
    - Process/transform data
    """

    def __init__(self, supabase_service: SupabaseService):
        self.db = supabase_service

    async def get_current_with_forecast(self, city: str) -> Dict:
        """Get current air quality with forecast if available."""
        # Fetch from data layer
        current = await self.db.get_current_air_quality(city)

        if not current:
            return None

        # Business rule: Add forecast if confidence > 0.7
        prediction = await self.db.get_latest_prediction(city)

        if prediction and prediction['confidence_score'] > 0.7:
            current['forecast'] = {
                'pm25': prediction['predicted_value'],
                'confidence': prediction['confidence_score'],
                'prediction_for': prediction['prediction_for']
            }

        # Business rule: Calculate AQI if not present
        if not current.get('aqi'):
            current['aqi'] = self._calculate_aqi(current['pm25'], current['pm10'])

        return current

    def _calculate_aqi(self, pm25: float, pm10: float) -> int:
        """Business logic: Calculate AQI from pollutant values."""
        # AQI calculation logic
        return int((pm25 / 12) * 50)
```

**Data Access Layer:**
```python
# app/services/supabase_service.py
class SupabaseService:
    """
    Data access layer: Database operations.

    Responsibilities:
    - Execute queries
    - Handle CRUD operations
    - Abstract database details
    """

    def __init__(self, client: Client):
        self.client = client

    async def get_current_air_quality(self, city: str) -> Optional[Dict]:
        """Fetch most recent air quality measurement."""
        result = self.client.table('air_quality_measurements') \
            .select('*') \
            .eq('city', city) \
            .order('timestamp', desc=True) \
            .limit(1) \
            .execute()

        return result.data[0] if result.data else None

    async def get_latest_prediction(self, city: str) -> Optional[Dict]:
        """Fetch most recent prediction."""
        result = self.client.table('predictions') \
            .select('*') \
            .eq('city', city) \
            .order('created_at', desc=True) \
            .limit(1) \
            .execute()

        return result.data[0] if result.data else None
```

---

## Frontend Architecture

### Directory Structure

```
frontend/src/
├── pages/                         # PAGE COMPONENTS (Routes)
│   ├── Dashboard.tsx              # Dashboard page
│   ├── DashboardMap.tsx           # Interactive map page
│   ├── Predictions.tsx            # Predictions page
│   ├── Mobility.tsx               # Mobility page
│   ├── Analytics.tsx              # Analytics page
│   └── Reports.tsx                # Reports page
│
├── components/                    # REUSABLE COMPONENTS
│   ├── Dashboard/
│   │   ├── KPICard.tsx            # KPI display card
│   │   ├── AirQualityChart.tsx    # Line chart
│   │   ├── VelibCard.tsx          # Vélib widget
│   │   └── AnomalyWidget.tsx      # Anomaly display
│   ├── Map/
│   │   ├── LeafletMap.tsx         # Base map component
│   │   ├── PollutionHeatmapLayer.tsx
│   │   ├── IoTSensorsLayer.tsx
│   │   ├── VelibStationsLayer.tsx
│   │   └── TrafficDisruptionsLayer.tsx
│   ├── Charts/
│   │   └── CorrelationChart.tsx   # Correlation chart
│   └── Predictions/
│       └── PredictionCard.tsx     # Prediction display
│
├── services/                      # API CLIENT LAYER
│   └── api.ts                     # Axios API client
│
├── hooks/                         # CUSTOM HOOKS (Business Logic)
│   ├── useAirQuality.ts           # Air quality data hook
│   ├── usePredictions.ts          # Predictions hook
│   ├── useMobility.ts             # Mobility data hook
│   ├── useAnalytics.ts            # Analytics hook
│   ├── useAnomalies.ts            # Anomalies hook
│   └── useAuth.ts                 # Authentication hook
│
├── stores/                        # STATE MANAGEMENT
│   └── authStore.ts               # Zustand auth store
│
├── types/                         # TYPESCRIPT TYPES
│   └── index.ts                   # Type definitions
│
├── App.tsx                        # Main app component
└── main.tsx                       # Entry point
```

### Component Hierarchy

```
App.tsx
├── Router
│   ├── Dashboard (Page)
│   │   ├── KPICard (Component)
│   │   ├── AirQualityChart (Component)
│   │   ├── VelibCard (Component)
│   │   └── AnomalyWidget (Component)
│   │
│   ├── DashboardMap (Page)
│   │   └── LeafletMap (Component)
│   │       ├── PollutionHeatmapLayer
│   │       ├── IoTSensorsLayer
│   │       ├── VelibStationsLayer
│   │       └── TrafficDisruptionsLayer
│   │
│   ├── Predictions (Page)
│   │   └── PredictionCard (Component)
│   │
│   └── Analytics (Page)
│       └── CorrelationChart (Component)
```

### Data Flow (Frontend)

```
1. User Action (e.g., page load, button click)
   │
   ▼
2. Page Component (Dashboard.tsx)
   │
   ├─ Use custom hook
   └─ const { data } = useAirQuality('paris')
   │
   ▼
3. Custom Hook (useAirQuality.ts)
   │
   ├─ TanStack Query
   └─ useQuery({ queryKey: ['airQuality'], queryFn: fetchAirQuality })
   │
   ▼
4. API Service (api.ts)
   │
   ├─ Axios HTTP client
   └─ axios.get('/api/v1/air-quality/current?city=paris')
   │
   ▼
5. Backend API (FastAPI)
   │
   ├─ Process request
   └─ Return JSON response
   │
   ▼
6. API Service
   │
   └─ Return data to hook
   │
   ▼
7. Custom Hook
   │
   ├─ TanStack Query caching
   └─ Return data to component
   │
   ▼
8. Page Component
   │
   ├─ Render UI with data
   └─ Pass data to child components
   │
   ▼
9. UI Update
```

### Example: Complete Frontend Flow

**Page Component:**
```typescript
// pages/Dashboard.tsx
export const Dashboard: React.FC = () => {
  // Hook handles data fetching
  const { data: airQuality, isLoading, error } = useAirQuality('paris');
  const { data: predictions } = usePredictions('paris');

  if (isLoading) return <Spinner />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <div className="container">
      <h1>Air Quality Dashboard</h1>

      {/* Pass data to presentational components */}
      <div className="grid grid-cols-3 gap-4">
        <KPICard
          title="PM2.5"
          value={airQuality.pm25}
          unit="μg/m³"
          severity={getSeverity(airQuality.pm25)}
        />
        <KPICard
          title="PM10"
          value={airQuality.pm10}
          unit="μg/m³"
          severity={getSeverity(airQuality.pm10)}
        />
      </div>

      {predictions && (
        <PredictionCard prediction={predictions} />
      )}
    </div>
  );
};
```

**Custom Hook:**
```typescript
// hooks/useAirQuality.ts
export const useAirQuality = (city: string) => {
  return useQuery({
    queryKey: ['airQuality', city],
    queryFn: () => api.getAirQuality(city),
    staleTime: 5 * 60 * 1000,  // 5 minutes
    retry: 3,
    onError: (error) => {
      console.error('Failed to fetch air quality:', error);
    }
  });
};
```

**API Service:**
```typescript
// services/api.ts
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

export const api = {
  getAirQuality: async (city: string): Promise<AirQuality> => {
    const response = await apiClient.get(`/api/v1/air-quality/current`, {
      params: { city }
    });
    return response.data;
  },

  getPredictions: async (city: string): Promise<Prediction> => {
    const response = await apiClient.get(`/api/v1/predictions/current`, {
      params: { city }
    });
    return response.data;
  }
};
```

**Presentational Component:**
```typescript
// components/Dashboard/KPICard.tsx
interface KPICardProps {
  title: string;
  value: number;
  unit: string;
  severity: 'good' | 'moderate' | 'poor';
}

export const KPICard: React.FC<KPICardProps> = ({ title, value, unit, severity }) => {
  const severityColors = {
    good: 'bg-green-100 text-green-800',
    moderate: 'bg-yellow-100 text-yellow-800',
    poor: 'bg-red-100 text-red-800'
  };

  return (
    <div className={`rounded-lg p-6 ${severityColors[severity]}`}>
      <h3 className="text-sm font-medium">{title}</h3>
      <p className="text-3xl font-bold mt-2">
        {value.toFixed(1)} <span className="text-lg">{unit}</span>
      </p>
      <span className="text-xs uppercase">{severity}</span>
    </div>
  );
};
```

---

## Dependency Injection

### Backend Dependency Injection (FastAPI)

FastAPI uses dependency injection via `Depends()` to provide services to routes.

**Configuration:**
```python
# app/dependencies.py
from functools import lru_cache
from app.config import get_settings, get_supabase_client
from app.services.supabase_service import SupabaseService

@lru_cache()
def get_supabase_service() -> SupabaseService:
    """
    Get Supabase service instance (singleton).

    Benefits:
    - Single instance across application
    - Automatic cleanup
    - Testable (can mock)
    """
    client = get_supabase_client()
    return SupabaseService(client)
```

**Usage in Routes:**
```python
# app/api/v1/air_quality.py
@router.get("/current")
async def get_current_air_quality(
    city: str = Query(...),
    service: SupabaseService = Depends(get_supabase_service)
):
    """
    Dependency injection:
    - 'service' is automatically provided by FastAPI
    - No manual instantiation needed
    - Easy to mock in tests
    """
    data = await service.get_current_air_quality(city)
    return data
```

**Benefits:**
1. **Testability:** Easy to mock dependencies in tests
2. **Flexibility:** Swap implementations without changing routes
3. **Reusability:** Single instance shared across requests
4. **Separation:** Routes don't know how services are created

### Frontend Dependency Injection (React Context)

**Context Provider:**
```typescript
// contexts/ApiContext.tsx
const ApiContext = createContext<ApiClient | null>(null);

export const ApiProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const apiClient = useMemo(() => createApiClient(), []);

  return (
    <ApiContext.Provider value={apiClient}>
      {children}
    </ApiContext.Provider>
  );
};

export const useApi = () => {
  const context = useContext(ApiContext);
  if (!context) throw new Error('useApi must be used within ApiProvider');
  return context;
};
```

**Usage:**
```typescript
// App.tsx
function App() {
  return (
    <ApiProvider>
      <Dashboard />
    </ApiProvider>
  );
}

// Dashboard.tsx
function Dashboard() {
  const api = useApi();  // Injected dependency
  // Use api...
}
```

---

## State Management

### Backend State Management

**Configuration State (Singleton):**
```python
# app/config.py
@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings instance.

    Benefits:
    - Single source of truth
    - Loaded once at startup
    - Environment-specific
    """
    return Settings()
```

**Request State (Dependency Injection):**
```python
# Each request gets fresh service instance
service = Depends(get_supabase_service)
```

**Application State (In-Memory):**
```python
# Trained ML models stored in memory
class PM25ModelTrainer:
    def __init__(self):
        self.model: Optional[RandomForestRegressor] = None
        self.metrics: Optional[Dict] = None
```

### Frontend State Management

**1. Server State (TanStack Query):**

For data from the backend API.

```typescript
// Automatic caching, refetching, and background updates
const { data, isLoading, error } = useQuery({
  queryKey: ['airQuality', city],
  queryFn: () => api.getAirQuality(city),
  staleTime: 5 * 60 * 1000,  // Cache for 5 minutes
  refetchInterval: 60 * 1000  // Refetch every minute
});
```

**Benefits:**
- Automatic caching
- Background refetching
- Deduplication
- Optimistic updates

**2. Global State (Zustand):**

For client-side application state.

```typescript
// stores/authStore.ts
export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,

  login: (user, token) => set({ user, token }),
  logout: () => set({ user: null, token: null })
}));

// Usage
const { user, login } = useAuthStore();
```

**Benefits:**
- Simple API
- No boilerplate
- TypeScript support
- Devtools integration

**3. Local State (useState):**

For component-specific state.

```typescript
const [isOpen, setIsOpen] = useState(false);
const [selectedLayer, setSelectedLayer] = useState('pollution');
```

### State Decision Tree

```
Is this data from the server?
├─ YES → Use TanStack Query (server state)
│
└─ NO → Is it shared across components?
    ├─ YES → Use Zustand (global state)
    │
    └─ NO → Use useState (local state)
```

---

## API Design Principles

### RESTful Design

**Resource-based URLs:**
```
✅ GOOD:
GET    /api/v1/air-quality/current
GET    /api/v1/predictions/history
POST   /api/v1/alerts

❌ BAD:
GET    /api/v1/getCurrentAirQuality
GET    /api/v1/getPredictionHistory
POST   /api/v1/createAlert
```

**HTTP Methods:**
- `GET`: Retrieve resources
- `POST`: Create resources
- `PATCH`: Partial update
- `DELETE`: Remove resources

**Status Codes:**
- `200 OK`: Successful GET
- `201 Created`: Successful POST
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Missing/invalid auth
- `404 Not Found`: Resource doesn't exist
- `500 Internal Server Error`: Server error

### API Versioning

```
/api/v1/air-quality/current  ← Version in URL
```

**Benefits:**
- Backward compatibility
- Clear migration path
- Multiple versions can coexist

### Request/Response Format

**Request (with Pydantic validation):**
```python
class AirQualityCreate(BaseModel):
    source: str
    city: str
    pm25: Optional[float] = Field(None, ge=0)
    timestamp: datetime

@router.post("/measurements")
async def create_measurement(measurement: AirQualityCreate):
    # Pydantic automatically validates
    # - source is string
    # - pm25 is >= 0 if provided
    # - timestamp is valid datetime
    pass
```

**Response (consistent format):**
```json
{
  "id": 12345,
  "source": "SENSOR_001",
  "city": "paris",
  "pm25": 25.5,
  "timestamp": "2025-12-30T10:30:00Z",
  "created_at": "2025-12-30T10:30:05Z"
}
```

**Error Response:**
```json
{
  "detail": "City not found"
}
```

### Pagination

```python
@router.get("/history")
async def get_history(
    city: str = Query(...),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0)
):
    # Return paginated results
    pass
```

### Filtering

```python
@router.get("/traffic-disruptions")
async def get_disruptions(
    severity: Optional[str] = Query(None),
    active_only: bool = Query(True)
):
    # Filter by query parameters
    pass
```

---

## Code Organization

### Single Responsibility Principle

Each module/class has one clear purpose:

```python
# ✅ GOOD: Each file has single responsibility
# app/services/supabase_service.py - Database operations
# app/services/alert_service.py - Alert logic
# app/services/pdf_service.py - PDF generation

# ❌ BAD: Kitchen sink service
# app/services/everything_service.py
#   - Database operations
#   - Alert logic
#   - PDF generation
#   - Email sending
#   - ML predictions
```

### DRY (Don't Repeat Yourself)

**Shared utilities:**
```python
# app/utils/helpers.py
def calculate_aqi(pm25: float, pm10: float) -> int:
    """Reusable AQI calculation."""
    return int((pm25 / 12) * 50)

# Use everywhere instead of duplicating
from app.utils.helpers import calculate_aqi
```

### Configuration Over Code

```python
# ✅ GOOD: Configuration-driven
ALERT_THRESHOLDS = {
    'pm25': 50.0,
    'pm10': 100.0,
    'no2': 40.0
}

def check_threshold(pollutant: str, value: float) -> bool:
    return value > ALERT_THRESHOLDS.get(pollutant, float('inf'))

# ❌ BAD: Hardcoded values
def check_threshold(pollutant: str, value: float) -> bool:
    if pollutant == 'pm25' and value > 50.0:
        return True
    elif pollutant == 'pm10' and value > 100.0:
        return True
    # ...
```

---

## Design Patterns

### Repository Pattern (Backend)

**Problem:** Direct database access throughout codebase

**Solution:** Centralize data access in repository classes

```python
# SupabaseService acts as repository
class SupabaseService:
    def get_current_air_quality(self, city: str):
        # Encapsulate database query
        pass

    def insert_air_quality(self, data: Dict):
        # Encapsulate insert logic
        pass
```

### Service Pattern (Backend)

**Problem:** Business logic scattered in routes

**Solution:** Centralize business logic in service classes

```python
class AirQualityService:
    def __init__(self, db: SupabaseService):
        self.db = db

    async def get_with_forecast(self, city: str):
        # Business logic here
        current = await self.db.get_current_air_quality(city)
        # ... process and return
```

### Custom Hooks Pattern (Frontend)

**Problem:** API logic duplicated across components

**Solution:** Encapsulate API calls in custom hooks

```typescript
// Reusable hook
export const useAirQuality = (city: string) => {
  return useQuery({
    queryKey: ['airQuality', city],
    queryFn: () => api.getAirQuality(city)
  });
};

// Use in multiple components
const Dashboard = () => {
  const { data } = useAirQuality('paris');
};
```

### Factory Pattern (ML Models)

**Problem:** Complex model instantiation

**Solution:** Factory method for model creation

```python
class ModelFactory:
    @staticmethod
    def create_pm25_model(city: str) -> PM25Predictor:
        """Create configured PM2.5 predictor."""
        trainer = PM25ModelTrainer(supabase)
        trainer.load_model(city)
        return PM25Predictor(trainer.model)
```

---

## Data Flow

### Complete End-to-End Flow

```
┌────────────────────────────────────────────────────────────────┐
│ 1. USER ACTION                                                  │
│    User clicks "View Dashboard"                                │
└────────────┬───────────────────────────────────────────────────┘
             │
┌────────────▼───────────────────────────────────────────────────┐
│ 2. REACT COMPONENT (Dashboard.tsx)                             │
│    const { data } = useAirQuality('paris')                     │
└────────────┬───────────────────────────────────────────────────┘
             │
┌────────────▼───────────────────────────────────────────────────┐
│ 3. CUSTOM HOOK (useAirQuality.ts)                              │
│    useQuery({ queryFn: api.getAirQuality })                    │
└────────────┬───────────────────────────────────────────────────┘
             │
┌────────────▼───────────────────────────────────────────────────┐
│ 4. API SERVICE (api.ts)                                        │
│    axios.get('/api/v1/air-quality/current?city=paris')         │
└────────────┬───────────────────────────────────────────────────┘
             │ HTTP Request
┌────────────▼───────────────────────────────────────────────────┐
│ 5. FASTAPI ROUTE (air_quality.py)                              │
│    @router.get("/current")                                     │
│    async def get_current_air_quality(service: Depends(...))    │
└────────────┬───────────────────────────────────────────────────┘
             │
┌────────────▼───────────────────────────────────────────────────┐
│ 6. SERVICE LAYER (air_quality_service.py)                      │
│    async def get_current_with_forecast(city):                  │
│      - Apply business logic                                    │
│      - Coordinate data access                                  │
└────────────┬───────────────────────────────────────────────────┘
             │
┌────────────▼───────────────────────────────────────────────────┐
│ 7. DATA ACCESS LAYER (supabase_service.py)                     │
│    supabase.table('air_quality_measurements')                  │
│      .select('*')                                              │
│      .eq('city', 'paris')                                      │
│      .execute()                                                │
└────────────┬───────────────────────────────────────────────────┘
             │
┌────────────▼───────────────────────────────────────────────────┐
│ 8. DATABASE (PostgreSQL)                                       │
│    Execute query, return rows                                  │
└────────────┬───────────────────────────────────────────────────┘
             │
             │ (Response flows back up the stack)
             │
┌────────────▼───────────────────────────────────────────────────┐
│ 9. UI UPDATE                                                   │
│    Dashboard re-renders with new data                          │
└────────────────────────────────────────────────────────────────┘
```

---

**Document Version:** 1.0.0
**Last Updated:** 2025-12-30
**Maintained By:** ESIS-2 Architecture Team
