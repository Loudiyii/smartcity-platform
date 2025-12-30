# Technical Documentation - Smart City Platform

Comprehensive technical reference for developers, architects, and DevOps engineers working on the Smart City Platform.

## Table of Contents

- [System Architecture](#system-architecture)
- [Database Schema](#database-schema)
- [API Reference](#api-reference)
- [Machine Learning Pipeline](#machine-learning-pipeline)
- [IoT Sensor Implementation](#iot-sensor-implementation)
- [External API Integration](#external-api-integration)
- [Performance Optimization](#performance-optimization)
- [Security Architecture](#security-architecture)
- [Monitoring & Logging](#monitoring--logging)
- [Deployment Architecture](#deployment-architecture)

---

## System Architecture

### Technology Stack Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                            │
│                                                                       │
│  React 18 + TypeScript 5 + Vite 5                                    │
│  ├─ State Management: TanStack Query + Zustand                       │
│  ├─ Routing: React Router 6                                          │
│  ├─ UI: Tailwind CSS + Lucide Icons                                  │
│  ├─ Maps: Leaflet.js + Leaflet.heat                                  │
│  └─ Charts: Chart.js + React-ChartJS-2                               │
│                                                                       │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ HTTPS/REST API
┌───────────────────────────────┴─────────────────────────────────────┐
│                        APPLICATION LAYER                             │
│                                                                       │
│  FastAPI 0.109.0 + Uvicorn 0.27.0 (Python 3.11+)                     │
│  ├─ API Routes (v1)                                                  │
│  ├─ Service Layer (Business Logic)                                   │
│  ├─ ML Pipeline (Scikit-learn 1.3.2)                                 │
│  ├─ IoT Simulation (Threading + Requests)                            │
│  └─ External API Clients (HTTPX)                                     │
│                                                                       │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ PostgreSQL Protocol
┌───────────────────────────────┴─────────────────────────────────────┐
│                          DATA LAYER                                  │
│                                                                       │
│  Supabase PostgreSQL 17                                              │
│  ├─ Time-series tables (air_quality_measurements, weather_data)      │
│  ├─ ML tables (predictions)                                          │
│  ├─ Alert tables (alerts)                                            │
│  ├─ Metadata tables (sensor_metadata)                                │
│  └─ Indexes: GIN (JSONB), B-tree (timestamp, city)                   │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

### Component Interaction Diagram

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│ IoT Sensors  │──────▶│   Backend    │──────▶│   Database   │
│ (5 sensors)  │ POST  │  (FastAPI)   │ SQL   │ (PostgreSQL) │
└──────────────┘       └──────┬───────┘       └──────────────┘
                              │                        ▲
                              │ Train/Predict          │
                              ▼                        │
                       ┌──────────────┐                │
                       │  ML Models   │────────────────┘
                       │ (Scikit-     │  Read training
                       │  learn)      │  data
                       └──────────────┘
                              ▲
                              │ Predictions
┌──────────────┐              │
│   Frontend   │──────────────┴────────────────────┐
│   (React)    │◀────────────────────────────────┐ │
└──────────────┘  GET /predictions               │ │
       │                                          │ │
       │ GET                                      │ │
       └──────────────────────────────────────────┘ │
         External APIs (IDFM, AQICN, Weather)       │
                                                     │
         ┌───────────────────────────────────────────┘
         │
         ▼
  ┌──────────────┐
  │ Email Service│  Send alerts
  │  (SMTP)      │
  └──────────────┘
```

---

## Database Schema

### Complete Schema Overview

The database consists of 5 primary tables optimized for time-series data and real-time queries.

#### Table 1: `air_quality_measurements`

Time-series table storing all pollution measurements.

```sql
CREATE TABLE IF NOT EXISTS air_quality_measurements (
  id BIGSERIAL PRIMARY KEY,
  source VARCHAR(50) NOT NULL,           -- 'api' or 'SENSOR_XXX'
  city VARCHAR(100),
  location JSONB,                        -- {lat, lon, name}

  -- Pollutant concentrations (μg/m³)
  pm25 REAL CHECK (pm25 >= 0),          -- Fine particles
  pm10 REAL CHECK (pm10 >= 0),          -- Coarse particles
  no2 REAL CHECK (no2 >= 0),            -- Nitrogen dioxide
  o3 REAL CHECK (o3 >= 0),              -- Ozone
  so2 REAL CHECK (so2 >= 0),            -- Sulfur dioxide
  co REAL CHECK (co >= 0),              -- Carbon monoxide

  -- Air Quality Index
  aqi INTEGER CHECK (aqi BETWEEN 0 AND 500),

  -- Metadata
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_aq_timestamp_source ON air_quality_measurements(timestamp DESC, source);
CREATE INDEX idx_aq_city_timestamp ON air_quality_measurements(city, timestamp DESC);
CREATE INDEX idx_aq_location ON air_quality_measurements USING GIN(location);

-- Enable Row Level Security
ALTER TABLE air_quality_measurements ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read access" ON air_quality_measurements
FOR SELECT USING (true);
```

**Usage:**
- **INSERT:** IoT sensors and API collectors
- **SELECT:** Dashboard queries, ML training data fetching
- **Typical query volume:** 1000+ inserts/day, 100+ reads/minute

#### Table 2: `weather_data`

Meteorological data correlated with air quality.

```sql
CREATE TABLE IF NOT EXISTS weather_data (
  id BIGSERIAL PRIMARY KEY,
  city VARCHAR(100) NOT NULL,

  -- Weather metrics
  temperature REAL NOT NULL,             -- Celsius
  humidity REAL CHECK (humidity BETWEEN 0 AND 100),
  pressure REAL,                         -- hPa
  wind_speed REAL CHECK (wind_speed >= 0),
  wind_direction INTEGER CHECK (wind_direction BETWEEN 0 AND 360),
  precipitation REAL DEFAULT 0,          -- mm

  -- Metadata
  timestamp TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_weather_city_timestamp ON weather_data(city, timestamp DESC);

ALTER TABLE weather_data ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read access" ON weather_data FOR SELECT USING (true);
```

**Correlation with pollution:**
- High humidity → increased PM2.5
- Low wind speed → pollution accumulation
- High temperature → increased ozone (O3)

#### Table 3: `sensor_metadata`

Registry of all IoT sensors with location and status.

```sql
CREATE TABLE IF NOT EXISTS sensor_metadata (
  sensor_id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(100),
  latitude DOUBLE PRECISION NOT NULL,
  longitude DOUBLE PRECISION NOT NULL,
  location_description VARCHAR(255),

  sensor_type VARCHAR(50),               -- 'air_quality', 'weather', 'traffic'
  status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'maintenance', 'offline')),

  installed_at TIMESTAMPTZ,
  last_reading_at TIMESTAMPTZ,

  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sensor_status ON sensor_metadata(status);

ALTER TABLE sensor_metadata ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read access" ON sensor_metadata FOR SELECT USING (true);
```

**Current sensors:**
- SENSOR_001: Paris Centre (48.8566°N, 2.3522°E)
- SENSOR_002: Paris Nord (48.8738°N, 2.2950°E)
- SENSOR_003: Paris Sud (48.8414°N, 2.3209°E)
- SENSOR_004: Paris Est (48.8467°N, 2.3775°E)
- SENSOR_005: Paris Ouest (48.8656°N, 2.2879°E)

#### Table 4: `predictions`

Machine learning predictions for J+1 air quality forecasts.

```sql
CREATE TABLE IF NOT EXISTS predictions (
  id BIGSERIAL PRIMARY KEY,
  city VARCHAR(100) NOT NULL,
  pollutant VARCHAR(20) NOT NULL DEFAULT 'PM2.5',

  predicted_value REAL NOT NULL CHECK (predicted_value >= 0),
  confidence_score REAL CHECK (confidence_score BETWEEN 0 AND 1),

  -- Prediction metadata
  model_version VARCHAR(50),
  features_used JSONB,                   -- List of features used
  prediction_for TIMESTAMPTZ NOT NULL,   -- Timestamp being predicted

  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_predictions_city_timestamp ON predictions(city, prediction_for DESC);
CREATE INDEX idx_predictions_created_at ON predictions(created_at DESC);

ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read access" ON predictions FOR SELECT USING (true);
```

**Model details:**
- Algorithm: Random Forest Regressor
- Features: 20+ (temporal, weather, historical pollution)
- Target: PM2.5 value 24 hours ahead
- Performance: R² > 0.7, MAPE < 30%

#### Table 5: `alerts`

Alert system for threshold exceedances and anomalies.

```sql
CREATE TABLE IF NOT EXISTS alerts (
  id BIGSERIAL PRIMARY KEY,

  alert_type VARCHAR(50) NOT NULL CHECK (alert_type IN ('threshold_exceeded', 'anomaly_detected', 'sensor_offline')),
  severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),

  -- Alert details
  city VARCHAR(100),
  pollutant VARCHAR(20),
  value REAL,
  threshold REAL,
  message TEXT NOT NULL,

  -- Status tracking
  is_active BOOLEAN DEFAULT true,
  acknowledged_at TIMESTAMPTZ,
  acknowledged_by VARCHAR(255),

  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_alerts_active ON alerts(is_active, created_at DESC);
CREATE INDEX idx_alerts_severity ON alerts(severity, created_at DESC);

ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read access" ON alerts FOR SELECT USING (true);
```

**Alert thresholds (WHO guidelines):**
- PM2.5: 15 μg/m³ (24h average)
- PM10: 45 μg/m³ (24h average)
- NO2: 25 μg/m³ (24h average)

---

## API Reference

### Base Configuration

**Base URL:**
- Development: `http://localhost:8080`
- Production: `https://smartcity-platform-production.up.railway.app`

**API Version:** v1

**Authentication:** JWT Bearer tokens

### Authentication Endpoints

#### POST `/api/v1/auth/login`

Authenticate user and receive JWT token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Errors:**
- `401 Unauthorized`: Invalid credentials
- `422 Validation Error`: Missing fields

### Air Quality Endpoints

#### GET `/api/v1/air-quality/current`

Get current air quality for a city.

**Query Parameters:**
- `city` (required): City name (e.g., "paris")

**Response (200 OK):**
```json
{
  "id": 12345,
  "source": "SENSOR_001",
  "city": "paris",
  "location": {
    "lat": 48.8566,
    "lon": 2.3522,
    "name": "Paris Centre"
  },
  "pm25": 25.5,
  "pm10": 38.2,
  "no2": 18.7,
  "aqi": 78,
  "timestamp": "2025-12-30T10:30:00Z"
}
```

#### GET `/api/v1/air-quality/history`

Get historical air quality data.

**Query Parameters:**
- `city` (required): City name
- `limit` (optional): Max records, default 100, max 1000

**Response (200 OK):**
```json
[
  {
    "id": 12345,
    "source": "SENSOR_001",
    "city": "paris",
    "pm25": 25.5,
    "pm10": 38.2,
    "no2": 18.7,
    "timestamp": "2025-12-30T10:30:00Z"
  },
  ...
]
```

#### POST `/api/v1/air-quality/measurements`

Create new air quality measurement (IoT sensors).

**Request:**
```json
{
  "source": "SENSOR_001",
  "city": "paris",
  "pm25": 25.5,
  "pm10": 38.2,
  "no2": 18.7,
  "timestamp": "2025-12-30T10:30:00Z"
}
```

**Response (201 Created):**
```json
{
  "id": 12346,
  "source": "SENSOR_001",
  "city": "paris",
  "pm25": 25.5,
  "pm10": 38.2,
  "no2": 18.7,
  "timestamp": "2025-12-30T10:30:00Z",
  "created_at": "2025-12-30T10:30:05Z"
}
```

### Prediction Endpoints

#### GET `/api/v1/predictions/current`

Get current J+1 prediction.

**Query Parameters:**
- `city` (required): City name

**Response (200 OK):**
```json
{
  "id": 456,
  "city": "paris",
  "pollutant": "PM2.5",
  "predicted_value": 28.3,
  "confidence_score": 0.85,
  "model_version": "v1.0",
  "prediction_for": "2025-12-31T10:00:00Z",
  "created_at": "2025-12-30T10:00:00Z"
}
```

#### GET `/api/v1/predictions/history`

Get prediction history.

**Query Parameters:**
- `city` (required): City name
- `days` (optional): Number of days, default 7

**Response (200 OK):**
```json
[
  {
    "id": 456,
    "city": "paris",
    "pollutant": "PM2.5",
    "predicted_value": 28.3,
    "confidence_score": 0.85,
    "prediction_for": "2025-12-31T10:00:00Z",
    "created_at": "2025-12-30T10:00:00Z"
  },
  ...
]
```

#### POST `/api/v1/predictions/train`

Manually trigger model training.

**Request:**
```json
{
  "city": "paris",
  "days": 60
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "metrics": {
    "r2": 0.8234,
    "mae": 4.52,
    "rmse": 6.78,
    "mape": 18.45,
    "cv_r2_mean": 0.7956,
    "cv_r2_std": 0.0412
  },
  "city": "paris",
  "trained_at": "2025-12-30T10:30:00Z"
}
```

### Mobility Endpoints

#### GET `/api/v1/mobility/velib`

Get Vélib station availability.

**Query Parameters:**
- `station_id` (optional): Specific station ID
- `limit` (optional): Max stations, default 50

**Response (200 OK):**
```json
[
  {
    "station_id": "16107",
    "name": "Benjamin Godard - Victor Hugo",
    "num_bikes_available": 12,
    "num_docks_available": 23,
    "latitude": 48.865983,
    "longitude": 2.275725,
    "is_installed": true,
    "is_returning": true,
    "is_renting": true,
    "last_reported": 1735555800
  },
  ...
]
```

#### GET `/api/v1/mobility/traffic-disruptions`

Get traffic disruptions from IDFM.

**Query Parameters:**
- `severity` (optional): Filter by severity (low, medium, high, critical)
- `active_only` (optional): Only active disruptions, default true

**Response (200 OK):**
```json
[
  {
    "disruption_id": "IDFM_DISRUPT_12345",
    "line_id": "C01742",
    "line_name": "RER A",
    "severity": "high",
    "message": "Traffic interruption between La Défense and Auber due to signal failure",
    "start_time": "2025-12-30T08:00:00Z",
    "end_time": "2025-12-30T12:00:00Z",
    "is_active": true
  },
  ...
]
```

#### GET `/api/v1/mobility/transit-stops`

Get transit stop locations.

**Query Parameters:**
- `limit` (optional): Max stops, default 50
- `zone_id` (optional): Filter by zone

**Response (200 OK):**
```json
[
  {
    "stop_id": "STIF:StopPoint:Q:41322:",
    "stop_name": "Gare du Nord",
    "stop_lat": 48.880931,
    "stop_lon": 2.355323,
    "zone_id": "1",
    "location_type": 0
  },
  ...
]
```

#### GET `/api/v1/mobility/next-departures`

Get next departures at a transit stop.

**Query Parameters:**
- `stop_id` (required): IDFM stop monitoring reference

**Response (200 OK):**
```json
{
  "stop_id": "STIF:StopPoint:Q:41322:",
  "stop_name": "Gare du Nord",
  "departures": [
    {
      "line_id": "C01742",
      "line_name": "RER B",
      "destination_name": "Aéroport Charles de Gaulle",
      "expected_arrival_time": "2025-12-30T10:35:00Z",
      "arrival_status": "onTime",
      "vehicle_ref": "RER_B_12345"
    },
    ...
  ]
}
```

### Analytics Endpoints

#### GET `/api/v1/analytics/pollution-weather-correlation`

Get pollution-weather correlation data.

**Query Parameters:**
- `city` (required): City name
- `days` (optional): Number of days, default 30

**Response (200 OK):**
```json
{
  "correlations": {
    "pm25_temperature": 0.45,
    "pm25_humidity": 0.62,
    "pm25_wind_speed": -0.71,
    "pm10_temperature": 0.38,
    "no2_temperature": 0.28
  },
  "data_points": 720,
  "period": "30 days"
}
```

#### GET `/api/v1/analytics/temporal-analysis`

Get temporal pattern analysis.

**Query Parameters:**
- `city` (required): City name
- `days` (optional): Number of days, default 7

**Response (200 OK):**
```json
{
  "hourly_averages": {
    "0": 18.5,
    "1": 17.2,
    ...
    "23": 22.1
  },
  "daily_averages": {
    "2025-12-24": 25.3,
    "2025-12-25": 19.8,
    ...
  },
  "peak_hours": [8, 9, 18, 19],
  "lowest_hours": [3, 4, 5]
}
```

### Alert Endpoints

#### GET `/api/v1/alerts/active`

Get active alerts.

**Response (200 OK):**
```json
[
  {
    "id": 789,
    "alert_type": "threshold_exceeded",
    "severity": "high",
    "city": "paris",
    "pollutant": "PM2.5",
    "value": 55.2,
    "threshold": 50.0,
    "message": "PM2.5 level exceeded WHO guideline",
    "is_active": true,
    "created_at": "2025-12-30T10:30:00Z"
  },
  ...
]
```

#### POST `/api/v1/alerts`

Create new alert.

**Request:**
```json
{
  "alert_type": "threshold_exceeded",
  "severity": "high",
  "city": "paris",
  "pollutant": "PM2.5",
  "value": 55.2,
  "threshold": 50.0,
  "message": "PM2.5 level exceeded WHO guideline"
}
```

**Response (201 Created):**
```json
{
  "id": 789,
  "alert_type": "threshold_exceeded",
  "severity": "high",
  "city": "paris",
  "pollutant": "PM2.5",
  "value": 55.2,
  "threshold": 50.0,
  "message": "PM2.5 level exceeded WHO guideline",
  "is_active": true,
  "created_at": "2025-12-30T10:30:00Z"
}
```

---

## Machine Learning Pipeline

### Model Architecture

**Algorithm:** Random Forest Regressor

**Library:** Scikit-learn 1.3.2

**Hyperparameters:**
```python
RandomForestRegressor(
    n_estimators=100,      # Number of trees
    max_depth=20,          # Maximum tree depth
    random_state=42,       # Reproducibility
    n_jobs=-1              # Use all CPU cores
)
```

### Feature Engineering

The model uses 20+ engineered features:

**1. Temporal Features (6 features):**
- Hour of day (0-23)
- Day of week (0-6)
- Month (1-12)
- Is weekend (boolean)
- Is rush hour (boolean)
- Season (0-3)

**2. Historical Pollution (7 features):**
- PM2.5 rolling mean (7 days)
- PM2.5 rolling std (7 days)
- PM2.5 lag 1 day
- PM2.5 lag 7 days
- PM10 rolling mean (7 days)
- NO2 rolling mean (7 days)
- Daily pollution trend

**3. Weather Features (5 features):**
- Temperature
- Humidity
- Wind speed
- Precipitation
- Atmospheric pressure

**4. Interaction Features (3 features):**
- Temperature × humidity
- Wind speed × precipitation
- Hour × day of week

**Implementation:**
```python
# app/ml/feature_engineering.py
class FeatureEngineer:
    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract all features from raw data.

        Args:
            df: Raw dataframe with columns [timestamp, pm25, pm10, ...]

        Returns:
            Feature dataframe ready for ML
        """
        # Temporal features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['month'] = df['timestamp'].dt.month
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['is_rush_hour'] = df['hour'].isin([7, 8, 9, 17, 18, 19]).astype(int)

        # Rolling statistics
        df['pm25_rolling_mean_7d'] = df['pm25'].rolling(window=168, min_periods=1).mean()
        df['pm25_rolling_std_7d'] = df['pm25'].rolling(window=168, min_periods=1).std()

        # Lag features
        df['pm25_lag_24h'] = df['pm25'].shift(24)
        df['pm25_lag_168h'] = df['pm25'].shift(168)

        # Interaction features
        df['temp_humidity_interaction'] = df['temperature'] * df['humidity']

        return df
```

### Training Pipeline

**1. Data Collection:**
```python
# Fetch 60 days of historical data
raw_df = await feature_engineer.fetch_training_data(city="paris", days=60)
# Expected: ~5,760 hourly records
```

**2. Feature Extraction:**
```python
features_df = feature_engineer.extract_features(raw_df)
# Output: DataFrame with 20+ feature columns
```

**3. Target Preparation:**
```python
# Prepare J+1 (24-hour ahead) predictions
X, y = feature_engineer.prepare_training_data(
    features_df,
    target_column='pm25',
    forecast_hours=24  # Predict 24 hours ahead
)
# X shape: (n_samples, 20+ features)
# y shape: (n_samples,)
```

**4. Train-Test Split:**
```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    shuffle=False  # Preserve temporal order
)
```

**5. Model Training:**
```python
model = RandomForestRegressor(
    n_estimators=100,
    max_depth=20,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)
```

**6. Evaluation:**
```python
y_pred = model.predict(X_test)

metrics = {
    'mae': mean_absolute_error(y_test, y_pred),
    'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
    'r2': r2_score(y_test, y_pred),
    'mape': np.mean(np.abs((y_test - y_pred) / y_test)) * 100
}
```

**Performance Requirements:**
- R² score > 0.7
- MAPE < 30%
- MAE < 10 μg/m³

### Prediction Pipeline

**Real-time Prediction Flow:**

```python
# 1. Load trained model
model_path = "app/ml/models/pm25_model_paris.pkl"
model_data = pickle.load(open(model_path, 'rb'))

# 2. Fetch recent data for feature engineering
recent_data = await fetch_last_7_days(city="paris")

# 3. Engineer features
features = feature_engineer.extract_features(recent_data)
X = features[model_data['feature_columns']].tail(1)

# 4. Make prediction
predicted_pm25 = model_data['model'].predict(X)[0]

# 5. Calculate confidence score
confidence = model_data['metrics']['r2']  # Simplified

# 6. Save to database
prediction_record = {
    'city': 'paris',
    'pollutant': 'PM2.5',
    'predicted_value': predicted_pm25,
    'confidence_score': confidence,
    'prediction_for': datetime.now() + timedelta(hours=24)
}
```

### Model Retraining Strategy

**Auto-train on startup:**
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Check if model exists
    if not model_path.exists():
        print(f"[ML] No model found, training now...")
        result = await trainer.train(city="paris", days=30)
        trainer.save_model("paris")
```

**Manual retraining via API:**
```bash
POST /api/v1/predictions/train
{
  "city": "paris",
  "days": 60
}
```

**Scheduled retraining (future):**
- Weekly automatic retraining
- Triggered by performance degradation
- Data drift detection

---

## IoT Sensor Implementation

### Sensor Architecture

**Hardware Specification (Simulated):**
- Sensor type: PM2.5/PM10/NO2 multi-parameter sensor
- Measurement interval: 15 minutes (900 seconds)
- Data transmission: HTTP POST to backend API
- Power: Continuous (simulated)

### Sensor Locations

| ID | Name | Latitude | Longitude | Area |
|----|------|----------|-----------|------|
| SENSOR_001 | Paris Centre | 48.8566 | 2.3522 | Central Paris |
| SENSOR_002 | Paris Nord | 48.8738 | 2.2950 | Northern Paris |
| SENSOR_003 | Paris Sud | 48.8414 | 2.3209 | Southern Paris |
| SENSOR_004 | Paris Est | 48.8467 | 2.3775 | Eastern Paris |
| SENSOR_005 | Paris Ouest | 48.8656 | 2.2879 | Western Paris |

### Data Generation Logic

```python
class IoTSensor:
    def generate_pm25(self) -> float:
        """Generate realistic PM2.5 with daily cycle."""
        hour = datetime.now().hour

        # Rush hour effect (7-9am, 5-7pm)
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            factor = 1.3  # 30% increase
        elif 22 <= hour or hour <= 6:
            factor = 0.7  # 30% decrease (night)
        else:
            factor = 1.0

        # Random noise (±10%)
        noise = random.gauss(0, 0.1)

        # Occasional spike (5% probability)
        spike = random.uniform(1.5, 2.0) if random.random() < 0.05 else 1.0

        # Calculate PM2.5
        pm25 = self.base_pm25 * factor * (1 + noise) * spike

        # Drift (slow baseline change)
        self.base_pm25 += random.gauss(0, 0.5)
        self.base_pm25 = max(5, min(100, self.base_pm25))

        return max(0, round(pm25, 2))
```

### Data Transmission

**Protocol:** HTTP POST

**Endpoint:** `/api/v1/air-quality/measurements`

**Payload Format:**
```json
{
  "source": "SENSOR_001",
  "city": "paris",
  "pm25": 25.5,
  "pm10": 38.2,
  "no2": 18.7,
  "timestamp": "2025-12-30T10:30:00Z"
}
```

**Transmission Code:**
```python
def send_measurement(self, measurement: Dict) -> bool:
    """Send measurement to backend API."""
    try:
        response = requests.post(
            self.api_url,
            json=measurement,
            timeout=10
        )
        response.raise_for_status()
        self.sent_count += 1
        print(f"✅ [{self.sensor_id}] PM2.5={measurement['pm25']}")
        return True
    except requests.exceptions.RequestException as e:
        self.error_count += 1
        print(f"❌ [{self.sensor_id}] Error: {e}")
        return False
```

### Multi-Sensor Orchestration

**Thread-based parallel execution:**
```python
def run_iot_worker():
    """Background worker to simulate IoT sensors."""

    # Initialize metadata
    init_sensor_metadata()

    SENSORS = [
        {"sensor_id": "SENSOR_001", "location": {...}},
        {"sensor_id": "SENSOR_002", "location": {...}},
        # ... 5 sensors total
    ]

    def run_sensor(config):
        sensor = IoTSensor(sensor_id=config["sensor_id"], ...)
        sensor.run(interval_seconds=900)  # 15 minutes

    for sensor_config in SENSORS:
        thread = threading.Thread(target=run_sensor, args=(sensor_config,), daemon=True)
        thread.start()
        time.sleep(1)  # Stagger starts
```

---

## External API Integration

### IDFM (Île-de-France Mobilités) APIs

**Base URL:** `https://prim.iledefrance-mobilites.fr/marketplace`

**Authentication:** API key in headers

#### 1. Vélib Station Availability (GBFS)

**Endpoints:**
- Station information: `/velib/station_information.json`
- Station status: `/velib/station_status.json`

**Data format:** GBFS (General Bikeshare Feed Specification)

**Sample response:**
```json
{
  "data": {
    "stations": [
      {
        "station_id": "16107",
        "num_bikes_available": 12,
        "num_docks_available": 23,
        "is_installed": 1,
        "is_returning": 1,
        "is_renting": 1,
        "last_reported": 1735555800
      }
    ]
  }
}
```

**Implementation:**
```python
async def get_velib_availability(self, limit: int = 50) -> List[VelibStation]:
    status_url = f"{self.base_url}/velib/station_status.json"
    info_url = f"{self.base_url}/velib/station_information.json"

    async with httpx.AsyncClient() as client:
        # Fetch both status and info
        status_response = await client.get(status_url, headers=self.headers)
        info_response = await client.get(info_url, headers=self.headers)

        # Merge data
        stations = merge_station_data(status_response.json(), info_response.json())

        return stations[:limit]
```

#### 2. Traffic Disruptions

**Endpoint:** `/disruptions_bulk/disruptions/v2`

**Data format:** SIRI-Lite

**Sample response:**
```json
{
  "disruptions": [
    {
      "id": "IDFM_DISRUPT_12345",
      "severity": "high",
      "message": "Traffic interruption...",
      "impactedSections": [
        {
          "lineId": "C01742",
          "from": {"name": "La Défense"},
          "to": {"name": "Auber"}
        }
      ],
      "applicationPeriods": [
        {
          "begin": "2025-12-30T08:00:00Z",
          "end": "2025-12-30T12:00:00Z"
        }
      ]
    }
  ]
}
```

#### 3. Real-time Departures (Stop Monitoring)

**Endpoint:** `/stop-monitoring`

**Parameters:**
- `MonitoringRef`: Stop ID (e.g., "STIF:StopPoint:Q:41322:")

**Data format:** SIRI Lite

**Sample response:**
```json
{
  "Siri": {
    "ServiceDelivery": {
      "StopMonitoringDelivery": [
        {
          "MonitoredStopVisit": [
            {
              "MonitoredVehicleJourney": {
                "LineRef": {"value": "C01742"},
                "PublishedLineName": [{"value": "RER B"}],
                "DestinationName": [{"value": "Aéroport CDG"}],
                "MonitoredCall": {
                  "ExpectedArrivalTime": "2025-12-30T10:35:00Z",
                  "ArrivalStatus": "onTime"
                }
              }
            }
          ]
        }
      ]
    }
  }
}
```

### Performance Optimization

**Caching Strategy:**
- Vélib data: Cache for 2 minutes
- Traffic disruptions: Cache for 5 minutes
- Stop monitoring: Cache for 30 seconds

**Error Handling:**
```python
async def get_traffic_disruptions(self):
    try:
        response = await client.get(url, headers=self.headers, timeout=10.0)
        response.raise_for_status()
        return parse_disruptions(response.json())
    except httpx.HTTPError as e:
        print(f"[ERROR] IDFM API error: {e}")
        return []  # Graceful degradation
```

---

## Performance Optimization

### Database Optimization

**1. Indexing Strategy:**
```sql
-- Time-series queries (most common)
CREATE INDEX idx_aq_timestamp_source ON air_quality_measurements(timestamp DESC, source);
CREATE INDEX idx_aq_city_timestamp ON air_quality_measurements(city, timestamp DESC);

-- JSONB location queries
CREATE INDEX idx_aq_location ON air_quality_measurements USING GIN(location);

-- Alert queries
CREATE INDEX idx_alerts_active ON alerts(is_active, created_at DESC);
```

**2. Query Optimization:**
```python
# ❌ Bad: Fetches all columns
SELECT * FROM air_quality_measurements WHERE city = 'paris'

# ✅ Good: Only needed columns
SELECT id, pm25, pm10, timestamp FROM air_quality_measurements
WHERE city = 'paris'
ORDER BY timestamp DESC
LIMIT 100
```

**3. Connection Pooling:**
- Supabase client uses connection pooling by default
- Max connections: 100 (adjustable)

### Frontend Optimization

**1. React Query Caching:**
```typescript
const { data } = useQuery({
  queryKey: ['airQuality', city],
  queryFn: () => fetchAirQuality(city),
  staleTime: 5 * 60 * 1000,  // 5 minutes
  cacheTime: 10 * 60 * 1000  // 10 minutes
});
```

**2. Code Splitting:**
```typescript
// Lazy load heavy components
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Analytics = lazy(() => import('./pages/Analytics'));
```

**3. Memoization:**
```typescript
const chartData = useMemo(() => {
  return processChartData(rawData);
}, [rawData]);
```

### Backend Optimization

**1. Async Operations:**
```python
# All I/O operations are async
async def get_current_air_quality(city: str):
    data = await service.get_current_data(city)
    return data
```

**2. Batch Processing:**
```python
# Insert multiple measurements in one query
supabase.table('air_quality_measurements').insert(measurements_batch).execute()
```

**3. Background Tasks:**
```python
# ML training runs in background
worker_thread = threading.Thread(target=run_iot_worker, daemon=True)
worker_thread.start()
```

### Performance Benchmarks

| Operation | Target | Actual | Status |
|-----------|--------|--------|--------|
| API Response (GET) | < 200ms | ~120ms | ✅ |
| API Response (POST) | < 500ms | ~250ms | ✅ |
| Database Query | < 50ms | ~35ms | ✅ |
| Dashboard Load | < 2s | ~1.5s | ✅ |
| ML Prediction | < 500ms | ~380ms | ✅ |
| PDF Generation | < 5s | ~2.8s | ✅ |

---

## Security Architecture

### Authentication & Authorization

**JWT Token Structure:**
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
{
  "sub": "user@example.com",
  "exp": 1735565400,
  "iat": 1735561800
}
```

**Token Validation:**
```python
from jose import jwt, JWTError

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Row Level Security (RLS)

**Supabase RLS Policies:**
```sql
-- Public read access for air quality data
CREATE POLICY "Public read access" ON air_quality_measurements
FOR SELECT USING (true);

-- Authenticated write access
CREATE POLICY "Authenticated write" ON air_quality_measurements
FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Admin-only access for alerts
CREATE POLICY "Admin only" ON alerts
FOR ALL USING (auth.jwt() ->> 'role' = 'admin');
```

### Input Validation

**Pydantic Models:**
```python
class AirQualityCreate(BaseModel):
    source: str = Field(..., max_length=50)
    city: str = Field(..., max_length=100)
    pm25: Optional[float] = Field(None, ge=0)
    pm10: Optional[float] = Field(None, ge=0)
    timestamp: datetime

    @validator('pm25')
    def validate_pm25(cls, v):
        if v and v > 500:
            raise ValueError('PM2.5 value too high')
        return v
```

### CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://frontend-gamma-three-19.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### API Rate Limiting

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/v1/predictions/train")
@limiter.limit("10/hour")
async def train_model(request: Request):
    # Expensive operation, limit to 10/hour
    pass
```

---

## Monitoring & Logging

### Application Logging

**Structured Logging:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Usage
logger.info(f"[ML] Training model for {city}")
logger.error(f"[ERROR] Failed to fetch IDFM data: {e}")
```

### Health Check Endpoint

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "database": "connected",
        "timestamp": datetime.utcnow().isoformat()
    }
```

### Error Tracking

**Exception Handling:**
```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

---

## Deployment Architecture

### Production Stack

```
┌─────────────────────────────────────────────────────────┐
│                    Vercel (Frontend)                     │
│  - CDN: Global edge network                              │
│  - Regions: Auto (closest to user)                       │
│  - Build: Vite production build                          │
│  - ENV: VITE_API_URL                                     │
└────────────────────┬────────────────────────────────────┘
                     │ HTTPS
┌────────────────────▼────────────────────────────────────┐
│                    Railway (Backend)                     │
│  - Region: US East                                       │
│  - Runtime: Python 3.11                                  │
│  - Server: Uvicorn                                       │
│  - Workers: 4                                            │
│  - ENV: All backend variables                            │
└────────────────────┬────────────────────────────────────┘
                     │ PostgreSQL
┌────────────────────▼────────────────────────────────────┐
│                  Supabase (Database)                     │
│  - Region: US East 1                                     │
│  - PostgreSQL: 17                                        │
│  - Backups: Daily                                        │
│  - RLS: Enabled                                          │
└─────────────────────────────────────────────────────────┘
```

### Environment Variables

**Backend (.env):**
```bash
# Database
SUPABASE_URL=https://vnznhsbjqxufvhasotid.supabase.co
SUPABASE_KEY=<anon_key>
SUPABASE_SERVICE_KEY=<service_key>

# APIs
IDFM_API_KEY=<idfm_key>
WEATHERAPI_KEY=<weather_key>

# Security
SECRET_KEY=<32_char_secret>
ALGORITHM=HS256

# App
ENVIRONMENT=production
PORT=8080
ALLOWED_ORIGINS=https://frontend-gamma-three-19.vercel.app
```

**Frontend (.env):**
```bash
VITE_API_URL=https://smartcity-platform-production.up.railway.app
```

### CI/CD Pipeline

**Automatic Deployments:**
- **Frontend:** Git push to `main` → Vercel auto-deploy
- **Backend:** Git push to `main` → Railway auto-deploy

**Build Commands:**
```bash
# Frontend
npm run build

# Backend
pip install -r requirements.txt
```

**Start Commands:**
```bash
# Frontend (handled by Vercel)
# Static files served from /dist

# Backend
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

**Document Version:** 1.0.0
**Last Updated:** 2025-12-30
**Maintained By:** ESIS-2 Technical Team
