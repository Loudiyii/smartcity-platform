# Smart City Platform - Air Quality & Mobility Monitoring

A comprehensive real-time platform for monitoring air quality and urban mobility in metropolitan areas. The platform integrates IoT sensors, external APIs, machine learning predictions, and interactive visualizations to provide actionable environmental insights for city officials, environmental managers, and concerned citizens.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [IoT Sensors](#iot-sensors)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Production URLs](#production-urls)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The Smart City Platform is an enterprise-grade environmental monitoring system designed to:

- **Monitor** air quality in real-time across multiple locations
- **Predict** pollution levels 24 hours in advance using machine learning
- **Analyze** correlations between weather, traffic, and air quality
- **Alert** stakeholders when pollution thresholds are exceeded
- **Visualize** data through interactive maps and charts
- **Integrate** mobility data (Vélib stations, traffic disruptions, transit stops)
- **Generate** comprehensive PDF reports for decision-makers

**Primary User Persona:** Environmental managers like Marie Dubois who need to monitor air quality, predict trends, and make data-driven decisions about pollution control measures.

---

## Key Features

### Real-Time Monitoring
- **5 IoT sensors** continuously measuring PM2.5, PM10, and NO2 levels
- **15-minute data intervals** for high-resolution time-series analysis
- **Live dashboard** with KPI cards showing current conditions
- **Historical data** tracking for trend analysis

### Machine Learning Predictions
- **Random Forest model** for J+1 (24-hour) PM2.5 forecasting
- **Auto-training on startup** if models don't exist
- **Performance metrics:** R² > 0.7, MAPE < 30%
- **Confidence scores** for each prediction
- **Feature importance** analysis to understand drivers

### Interactive Mapping
- **Multi-layer Leaflet maps** with pollution heatmaps
- **IoT sensor locations** with real-time readings
- **Vélib station availability** (1000+ stations)
- **Traffic disruptions** from IDFM API
- **Transit stops** with real-time departure information
- **Spatial pollution analysis** using kriging interpolation

### Advanced Analytics
- **Pollution-weather correlation** charts
- **Anomaly detection** using Z-score methodology
- **Temporal pattern analysis** (hourly, daily, weekly trends)
- **Mobility impact analysis** on air quality
- **Statistical dashboards** with customizable time ranges

### Alert System
- **Threshold monitoring** for PM2.5, PM10, NO2
- **Email notifications** when limits are exceeded
- **Anomaly alerts** for unusual pollution spikes
- **Sensor offline detection**
- **Severity classification** (low, medium, high, critical)

### Reporting
- **PDF report generation** with charts and statistics
- **Executive summaries** for decision-makers
- **Customizable time periods** (daily, weekly, monthly)
- **Data export** in multiple formats

---

## Technology Stack

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11+ | Programming language |
| **FastAPI** | 0.109.0 | REST API framework |
| **Uvicorn** | 0.27.0 | ASGI web server |
| **Supabase** | 2.10.0 | PostgreSQL database & auth |
| **Scikit-learn** | 1.3.2 | Machine learning models |
| **Pandas** | 2.1.4 | Data manipulation |
| **NumPy** | 1.26.3 | Numerical computing |
| **HTTPX** | 0.27.0 | Async HTTP client |
| **Pydantic** | 2.5.3 | Data validation |
| **ReportLab** | 4.0.8 | PDF generation |
| **Matplotlib** | 3.8.2 | Chart generation |
| **APScheduler** | 3.10.4 | Task scheduling |

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 18.2.0 | UI framework |
| **TypeScript** | 5.3.3 | Type-safe JavaScript |
| **Vite** | 5.0.8 | Build tool & dev server |
| **TanStack Query** | 5.13.0 | Server state management |
| **Zustand** | 4.4.7 | Global state management |
| **React Router** | 6.30.2 | Client-side routing |
| **Leaflet** | 1.9.4 | Interactive maps |
| **Leaflet.heat** | 0.2.0 | Heatmap visualization |
| **Chart.js** | 4.4.0 | Data charts |
| **Axios** | 1.6.2 | HTTP client |
| **Tailwind CSS** | 3.3.6 | Utility-first CSS |
| **Lucide React** | 0.294.0 | Icon library |
| **React Hook Form** | 7.48.2 | Form handling |
| **Zod** | 3.22.4 | Schema validation |

### Database

| Technology | Version | Purpose |
|------------|---------|---------|
| **PostgreSQL** | 17 | Primary database |
| **Supabase** | Cloud | Managed PostgreSQL + Auth |

### Infrastructure

| Service | Purpose |
|---------|---------|
| **Railway** | Backend deployment |
| **Vercel** | Frontend deployment |
| **Supabase Cloud** | Database hosting |
| **IDFM APIs** | Mobility data (Vélib, traffic, transit) |

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          FRONTEND (React)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Dashboard   │  │  Interactive │  │  Analytics   │          │
│  │   + KPIs     │  │     Map      │  │  + Reports   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│           │                 │                  │                 │
│           └─────────────────┼──────────────────┘                 │
│                             │                                    │
│                    TanStack Query + Axios                        │
└─────────────────────────────┼──────────────────────────────────┘
                              │ HTTPS
                              │
┌─────────────────────────────┼──────────────────────────────────┐
│                    BACKEND (FastAPI)                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    API Routes (v1)                        │  │
│  │  /air-quality  /predictions  /mobility  /analytics       │  │
│  └────────┬─────────────┬────────────┬──────────────────────┘  │
│           │             │            │                          │
│  ┌────────▼─────┐  ┌────▼────┐  ┌───▼──────┐  ┌────────────┐  │
│  │   Service    │  │   ML    │  │ External │  │    IoT     │  │
│  │    Layer     │  │ Models  │  │   APIs   │  │  Sensors   │  │
│  └────────┬─────┘  └────┬────┘  └───┬──────┘  └──────┬─────┘  │
│           │             │            │                │         │
│           └─────────────┴────────────┴────────────────┘         │
│                              │                                  │
└──────────────────────────────┼──────────────────────────────────┘
                               │
┌──────────────────────────────┼──────────────────────────────────┐
│                    DATABASE (PostgreSQL)                         │
│  ┌───────────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ air_quality_meas  │  │ predictions  │  │ sensor_metadata │  │
│  ├───────────────────┤  ├──────────────┤  ├─────────────────┤  │
│  │ weather_data      │  │ alerts       │  │ ...             │  │
│  └───────────────────┘  └──────────────┘  └─────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **IoT Sensors** → Generate measurements every 15 minutes → POST to `/api/v1/air-quality/measurements`
2. **ML Models** → Auto-train on startup → Predict J+1 pollution → Store in `predictions` table
3. **External APIs** (IDFM) → Fetch mobility data on-demand → Return to frontend
4. **Frontend** → Query backend via REST API → Display in dashboard/maps/charts
5. **Alerts** → Background worker monitors thresholds → Send email notifications

---

## Installation

### Prerequisites

- **Python** 3.11 or higher
- **Node.js** 18 or higher
- **npm** or **yarn**
- **Git**
- **Supabase account** (free tier)

### Backend Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/smartcity.git
   cd smartcity/backend
   ```

2. **Create Python virtual environment**
   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file in the `backend/` directory:
   ```env
   # Supabase Configuration
   SUPABASE_URL=https://vnznhsbjqxufvhasotid.supabase.co
   SUPABASE_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_KEY=your_supabase_service_key

   # External APIs
   WEATHERAPI_KEY=your_weatherapi_key
   AQICN_API_TOKEN=your_aqicn_token
   IDFM_API_KEY=your_idfm_api_key

   # Security
   SECRET_KEY=your_secret_key_here_min_32_chars
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60

   # Application
   ENVIRONMENT=development
   PORT=8080
   DEBUG=true

   # CORS
   ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

   # SMTP (for email alerts)
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   ALERT_RECIPIENTS=manager@example.com,admin@example.com
   ```

5. **Set up database**

   Run the database schema script in Supabase SQL Editor:
   ```bash
   # Copy contents of backend/database/schema.sql
   # Paste into Supabase SQL Editor
   # Execute to create all tables
   ```

6. **Run the backend server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
   ```

   The API will be available at: `http://localhost:8080`

   API documentation (Swagger UI): `http://localhost:8080/docs`

### Frontend Installation

1. **Navigate to frontend directory**
   ```bash
   cd ../frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment variables**

   Create a `.env` file in the `frontend/` directory:
   ```env
   VITE_API_URL=http://localhost:8080
   ```

4. **Run the development server**
   ```bash
   npm run dev
   ```

   The frontend will be available at: `http://localhost:5173`

### Database Setup (Supabase)

1. **Create a Supabase project** at https://supabase.com

2. **Run database migrations**
   ```bash
   # In Supabase SQL Editor, execute:
   # - backend/database/schema.sql (creates all tables)
   ```

3. **Enable Row Level Security (RLS)**
   ```sql
   -- Run these commands in Supabase SQL Editor
   ALTER TABLE air_quality_measurements ENABLE ROW LEVEL SECURITY;
   ALTER TABLE weather_data ENABLE ROW LEVEL SECURITY;
   ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;
   ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
   ALTER TABLE sensor_metadata ENABLE ROW LEVEL SECURITY;

   -- Create policies (example for public read access)
   CREATE POLICY "Public read access" ON air_quality_measurements
   FOR SELECT USING (true);
   ```

4. **Get your API keys**
   - Go to Settings → API in your Supabase dashboard
   - Copy the `anon` key and `service_role` key
   - Add them to your backend `.env` file

---

## Usage

### Starting the Application

#### Development Mode

1. **Start backend** (Terminal 1):
   ```bash
   cd backend
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   uvicorn app.main:app --reload --port 8080
   ```

2. **Start frontend** (Terminal 2):
   ```bash
   cd frontend
   npm run dev
   ```

3. **Start IoT sensors** (Terminal 3, optional):
   ```bash
   cd backend
   python app/simulators/iot_sensor.py
   ```

#### Production Mode

See [Deployment](#deployment) section below.

### Accessing the Application

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8080
- **API Documentation:** http://localhost:8080/docs
- **Health Check:** http://localhost:8080/health

### User Workflows

#### 1. Viewing Current Air Quality

1. Navigate to the **Dashboard** page (home)
2. View real-time KPI cards for PM2.5, PM10, NO2
3. Check the air quality trend chart
4. View recent anomalies widget

#### 2. Exploring Interactive Maps

1. Navigate to **Carte Interactive** (Map page)
2. Toggle layers:
   - Pollution heatmap
   - IoT sensor locations
   - Vélib stations
   - Traffic disruptions
   - Transit stops
3. Click markers for detailed information
4. Zoom/pan to explore different areas

#### 3. Viewing Predictions

1. Navigate to **Prédictions** page
2. See J+1 (24-hour) PM2.5 forecast
3. View confidence scores
4. Compare predicted vs. historical values
5. Analyze prediction accuracy metrics

#### 4. Mobility Data

1. Navigate to **Mobilité** page
2. View Vélib station availability
3. Check traffic disruptions by severity
4. See real-time transit departures
5. Analyze mobility patterns

#### 5. Advanced Analytics

1. Navigate to **Analyses** page
2. View pollution-weather correlations
3. Analyze temporal patterns
4. Examine statistical distributions
5. Customize time ranges

#### 6. Generating Reports

1. Navigate to **Rapports** page
2. Select date range
3. Choose report type (summary, detailed)
4. Click "Generate PDF Report"
5. Download the generated PDF

---

## IoT Sensors

### Sensor Network

The platform includes **5 IoT air quality sensors** strategically placed across Paris:

| Sensor ID | Location | Coordinates | Pollutants Measured |
|-----------|----------|-------------|---------------------|
| SENSOR_001 | Paris Centre | 48.8566°N, 2.3522°E | PM2.5, PM10, NO2 |
| SENSOR_002 | Paris Nord | 48.8738°N, 2.2950°E | PM2.5, PM10, NO2 |
| SENSOR_003 | Paris Sud | 48.8414°N, 2.3209°E | PM2.5, PM10, NO2 |
| SENSOR_004 | Paris Est | 48.8467°N, 2.3775°E | PM2.5, PM10, NO2 |
| SENSOR_005 | Paris Ouest | 48.8656°N, 2.2879°E | PM2.5, PM10, NO2 |

### Data Collection

- **Measurement Interval:** 15 minutes (900 seconds)
- **Data Points per Day:** 96 measurements per sensor
- **Total Daily Readings:** 480 measurements (5 sensors × 96)
- **Data Transmission:** HTTP POST to `/api/v1/air-quality/measurements`

### Sensor Simulation

The IoT sensors are simulated with realistic behavior:

```python
# Realistic PM2.5 generation with:
# - Daily cycles (higher during rush hours 7-9am, 5-7pm)
# - Random noise (±10%)
# - Occasional spikes (5% probability, 1.5-2x multiplier)
# - Gradual drift (baseline changes over time)
```

**Starting the simulator:**
```bash
cd backend
python app/simulators/iot_sensor.py
```

The simulator automatically:
- Registers sensors in the `sensor_metadata` table
- Sends measurements every 15 minutes
- Logs successful transmissions
- Handles API errors gracefully

---

## API Documentation

### Base URL

- **Development:** `http://localhost:8080`
- **Production:** `https://smartcity-platform-production.up.railway.app`

### Authentication

Most endpoints require JWT authentication:

```bash
# 1. Login
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "yourpassword"
}

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}

# 2. Use token in subsequent requests
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Core Endpoints

#### Air Quality

```bash
# Get current air quality
GET /api/v1/air-quality/current?city=paris

# Get historical data
GET /api/v1/air-quality/history?city=paris&limit=100

# Create measurement (IoT sensors)
POST /api/v1/air-quality/measurements
Content-Type: application/json

{
  "source": "SENSOR_001",
  "city": "paris",
  "pm25": 25.5,
  "pm10": 38.2,
  "no2": 18.7,
  "timestamp": "2025-12-30T10:30:00Z"
}
```

#### Predictions

```bash
# Get J+1 prediction
GET /api/v1/predictions/current?city=paris

# Get prediction history
GET /api/v1/predictions/history?city=paris&days=7

# Manually trigger training
POST /api/v1/predictions/train
{
  "city": "paris",
  "days": 60
}
```

#### Mobility

```bash
# Get Vélib station availability
GET /api/v1/mobility/velib?limit=50

# Get traffic disruptions
GET /api/v1/mobility/traffic-disruptions?severity=high&active_only=true

# Get transit stops
GET /api/v1/mobility/transit-stops?limit=50

# Get next departures
GET /api/v1/mobility/next-departures?stop_id=STIF:StopPoint:Q:41322:
```

#### Analytics

```bash
# Get pollution-weather correlation
GET /api/v1/analytics/pollution-weather-correlation?city=paris&days=30

# Get temporal analysis
GET /api/v1/analytics/temporal-analysis?city=paris&days=7

# Get statistics
GET /api/v1/analytics/statistics?city=paris&days=30
```

#### Alerts

```bash
# Get active alerts
GET /api/v1/alerts/active

# Create alert
POST /api/v1/alerts
{
  "alert_type": "threshold_exceeded",
  "severity": "high",
  "city": "paris",
  "pollutant": "PM2.5",
  "value": 55.2,
  "threshold": 50.0,
  "message": "PM2.5 exceeded WHO guideline"
}

# Acknowledge alert
PATCH /api/v1/alerts/{alert_id}/acknowledge
```

#### Reports

```bash
# Generate PDF report
POST /api/v1/reports/generate
{
  "city": "paris",
  "start_date": "2025-12-01",
  "end_date": "2025-12-30",
  "report_type": "summary"
}

# Response: PDF file download
```

### Response Formats

All responses follow this structure:

**Success (200 OK):**
```json
{
  "id": 12345,
  "city": "paris",
  "pm25": 25.5,
  "pm10": 38.2,
  "timestamp": "2025-12-30T10:30:00Z"
}
```

**Error (4xx/5xx):**
```json
{
  "detail": "City not found"
}
```

### Rate Limiting

- **Public endpoints:** 100 requests/minute
- **Authenticated endpoints:** 1000 requests/minute
- **ML training endpoints:** 10 requests/hour

---

## Deployment

### Backend Deployment (Railway)

1. **Create Railway account** at https://railway.app

2. **Create new project**
   ```bash
   railway init
   ```

3. **Add environment variables** in Railway dashboard:
   ```
   SUPABASE_URL=https://vnznhsbjqxufvhasotid.supabase.co
   SUPABASE_KEY=your_key
   SUPABASE_SERVICE_KEY=your_service_key
   SECRET_KEY=your_secret_key
   ENVIRONMENT=production
   PORT=8080
   ALLOWED_ORIGINS=https://frontend-gamma-three-19.vercel.app
   IDFM_API_KEY=your_idfm_key
   ```

4. **Deploy**
   ```bash
   railway up
   ```

5. **Get deployment URL**
   ```
   https://smartcity-platform-production.up.railway.app
   ```

### Frontend Deployment (Vercel)

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy**
   ```bash
   cd frontend
   vercel
   ```

3. **Configure environment variables** in Vercel dashboard:
   ```
   VITE_API_URL=https://smartcity-platform-production.up.railway.app
   ```

4. **Production URL**
   ```
   https://frontend-gamma-three-19.vercel.app
   ```

### Database (Supabase)

Supabase is already cloud-hosted, no deployment needed. Just ensure:

- RLS policies are enabled
- Indexes are created
- Backups are configured

---

## Production URLs

### Live Application

- **Frontend:** https://frontend-gamma-three-19.vercel.app
- **Backend API:** https://smartcity-platform-production.up.railway.app
- **API Docs:** https://smartcity-platform-production.up.railway.app/docs
- **Health Check:** https://smartcity-platform-production.up.railway.app/health

### Demo Credentials

```
Email: demo@smartcity.com
Password: Demo2025!
```

---

## Project Structure

```
smartcity/
├── backend/                      # FastAPI backend
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── config.py            # Configuration management
│   │   ├── dependencies.py      # Dependency injection
│   │   ├── api/
│   │   │   └── v1/              # API version 1 routes
│   │   │       ├── air_quality.py
│   │   │       ├── predictions.py
│   │   │       ├── mobility.py
│   │   │       ├── analytics.py
│   │   │       ├── alerts.py
│   │   │       └── reports.py
│   │   ├── services/            # Business logic layer
│   │   │   ├── supabase_service.py
│   │   │   ├── mobility_service.py
│   │   │   ├── alert_service.py
│   │   │   └── pdf_service.py
│   │   ├── ml/                  # Machine learning
│   │   │   ├── trainer.py       # Model training
│   │   │   ├── predictor.py     # Predictions
│   │   │   ├── feature_engineering.py
│   │   │   └── anomaly_detector.py
│   │   ├── models/              # Pydantic models
│   │   │   ├── air_quality.py
│   │   │   ├── prediction.py
│   │   │   ├── mobility.py
│   │   │   └── alert.py
│   │   ├── simulators/          # IoT simulation
│   │   │   └── iot_sensor.py
│   │   └── utils/               # Utilities
│   ├── database/
│   │   └── schema.sql           # Database schema
│   ├── requirements.txt         # Python dependencies
│   └── .env                     # Environment variables
│
├── frontend/                    # React frontend
│   ├── src/
│   │   ├── pages/               # Page components
│   │   │   ├── Dashboard.tsx
│   │   │   ├── DashboardMap.tsx
│   │   │   ├── Predictions.tsx
│   │   │   ├── Mobility.tsx
│   │   │   ├── Analytics.tsx
│   │   │   └── Reports.tsx
│   │   ├── components/          # Reusable components
│   │   │   ├── Dashboard/       # Dashboard-specific
│   │   │   ├── Map/             # Map layers
│   │   │   ├── Charts/          # Chart components
│   │   │   └── Predictions/     # Prediction cards
│   │   ├── services/            # API services
│   │   │   └── api.ts
│   │   ├── hooks/               # Custom React hooks
│   │   │   ├── useAirQuality.ts
│   │   │   ├── usePredictions.ts
│   │   │   ├── useMobility.ts
│   │   │   └── useAnalytics.ts
│   │   ├── stores/              # Zustand state stores
│   │   ├── types/               # TypeScript types
│   │   ├── App.tsx              # Main app component
│   │   └── main.tsx             # Entry point
│   ├── package.json             # Node dependencies
│   ├── vite.config.ts           # Vite configuration
│   └── .env                     # Environment variables
│
├── docs/                        # Documentation
│   ├── TECHNICAL.md             # Technical documentation
│   ├── ARCHITECTURE_SEPARATION.md
│   └── TESTING.md
│
└── README.md                    # This file
```

---

## Performance

### Benchmarks

- **API Response Time:** < 200ms (95th percentile)
- **Dashboard Load:** < 2 seconds
- **Database Queries:** < 50ms average
- **ML Predictions:** < 500ms
- **PDF Generation:** < 3 seconds

### Optimization Strategies

- **Database:** Indexed on `city`, `timestamp`, `source` columns
- **Caching:** TanStack Query with 5-minute stale time
- **Lazy Loading:** Code splitting with React.lazy()
- **CDN:** Static assets served via Vercel Edge Network
- **Compression:** Gzip/Brotli enabled

---

## Security

### Authentication
- JWT tokens with HS256 algorithm
- Token expiration: 60 minutes
- Refresh token support

### Data Protection
- Row Level Security (RLS) enabled on all tables
- Input validation with Pydantic
- SQL injection prevention
- XSS protection via React's automatic escaping

### HTTPS
- All production traffic encrypted
- Certificate management via Railway/Vercel

### API Keys
- Never committed to version control
- Stored in environment variables
- Rotated regularly

---

## Monitoring

### Application Monitoring
- Health check endpoint: `/health`
- Logging with structured JSON format
- Error tracking

### Database Monitoring
- Supabase dashboard for query performance
- Connection pool monitoring

### Alerts
- Email notifications for critical errors
- Threshold breach alerts
- Sensor offline detection

---

## Contributing

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make changes and commit**
   ```bash
   git commit -m "Add: feature description"
   ```
4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Create Pull Request**

### Code Standards

- **Backend:** Follow PEP 8, use type hints, write docstrings
- **Frontend:** Use TypeScript strict mode, follow React best practices
- **Testing:** Write tests for new features
- **Documentation:** Update README and technical docs

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

---

## License

MIT License - see LICENSE file for details

---

## Support

For issues, questions, or contributions:

- **GitHub Issues:** https://github.com/yourusername/smartcity/issues
- **Documentation:** See `docs/` folder
- **Email:** support@smartcity.com

---

## Acknowledgments

- **Île-de-France Mobilités (IDFM)** for mobility APIs
- **Supabase** for database and authentication
- **FastAPI** and **React** communities
- **ESIS-2 Team** for development

---

**Last Updated:** 2025-12-30
**Version:** 1.0.0
**Status:** Production
