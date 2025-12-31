# Smart City Platform - Air Quality & Mobility Monitoring

A real-time platform for monitoring air quality and urban mobility in Paris. This project uses IoT sensors, external APIs, machine learning predictions, and interactive maps to track pollution levels and mobility data.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
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

This platform monitors air quality in Paris and predicts pollution levels. It combines:

- Real-time air quality monitoring from 5 IoT sensors
- 24-hour pollution predictions using machine learning
- Analysis of weather, traffic, and air quality correlations
- Alerts when pollution exceeds safe levels
- Interactive maps with heatmaps and mobility data
- Vélib stations, traffic disruptions, and transit info
- PDF report generation

Built during December 18-31, 2024 as a student project.

---

## Features

### Real-Time Monitoring
- 5 IoT sensors measuring PM2.5, PM10, and NO2
- Data collected every 15 minutes
- Live dashboard showing current pollution levels
- Historical data for trend analysis

### Machine Learning Predictions
- Random Forest model predicting PM2.5 for next 24 hours
- Auto-trains on startup if model doesn't exist
- Performance: R² > 0.7, MAPE < 30%
- Shows confidence scores for predictions
- Feature importance analysis

### Interactive Mapping
- Leaflet maps with pollution heatmaps
- IoT sensor locations with real-time readings
- 1000+ Vélib stations with bike availability
- Traffic disruptions from IDFM API
  - 577 active disruptions in real-time
  - Custom parser for IDFM datetime format
  - Filter by severity (info, medium, high, critical)
- Transit stops with departure times
- Spatial pollution analysis with kriging

### Analytics
- Pollution vs weather correlation charts
- Anomaly detection (Z-score and Isolation Forest)
  - Runs automatically every 30 minutes in production
  - Saves high/critical anomalies to alerts
  - Monitors unusual pollution spikes
- Pattern analysis (hourly, daily, weekly)
- Mobility impact on air quality
- Customizable time ranges

### Authentication
- Public pages (Dashboard, Map, Predictions, Mobility) - no login needed
- Protected pages (Analytics, Reports) - login required
- Supabase Auth for user management
- JWT tokens for API access
- Email/password registration with verification
- Password reset via email
- Session management with auto-refresh
- Row-level security on database
- Tested flow: registration, login, access control, logout

### Alerts
- Monitors PM2.5, PM10, NO2 thresholds
- Email notifications when limits exceeded
- Anomaly alerts for pollution spikes
- Sensor offline detection
- Severity levels (low, medium, high, critical)

### Reports
- PDF generation with charts and stats
- Customizable time periods (daily, weekly, monthly)
- Data export in multiple formats

---

## Technology Stack

### Backend
- Python 3.11+ - main language
- FastAPI 0.109.0 - REST API
- Uvicorn 0.27.0 - web server
- Supabase 2.10.0 - database & auth
- Scikit-learn 1.3.2 - ML models
- Pandas 2.1.4 - data processing
- NumPy 1.26.3 - calculations
- HTTPX 0.27.0 - HTTP requests
- Pydantic 2.5.3 - validation
- ReportLab 4.0.8 - PDF reports
- Matplotlib 3.8.2 - charts
- APScheduler 3.10.4 - scheduled tasks

### Frontend
- React 18.2.0 - UI framework
- TypeScript 5.3.3 - typed JavaScript
- Vite 5.0.8 - build tool
- TanStack Query 5.13.0 - data fetching
- Zustand 4.4.7 - state management
- React Router 6.30.2 - routing
- Leaflet 1.9.4 - maps
- Leaflet.heat 0.2.0 - heatmaps
- Chart.js 4.4.0 - charts
- Axios 1.6.2 - HTTP client
- Tailwind CSS 3.3.6 - styling
- Lucide React 0.294.0 - icons
- React Hook Form 7.48.2 - forms
- Zod 3.22.4 - validation

### Database
- PostgreSQL 17
- Supabase Cloud (managed PostgreSQL + Auth)

### Deployment
- Railway - backend hosting
- Vercel - frontend hosting
- Supabase Cloud - database
- IDFM APIs - mobility data

---

## Architecture

### How It Works

```
Frontend (React) → Backend (FastAPI) → Database (PostgreSQL)
     ↓                    ↓                      ↓
Dashboard/Map        API Routes           air_quality_meas
Analytics         Service Layer          predictions
Reports           ML Models              alerts
                  External APIs          weather_data
```

### Data Flow

1. IoT Sensors generate measurements every 15 minutes → POST to `/api/v1/air-quality/measurements`
2. ML Models auto-train on startup → predict next 24h pollution → store in database
3. IDFM APIs fetch mobility data on-demand → return to frontend
4. Frontend queries backend via REST API → displays in dashboard/maps/charts
5. Background worker monitors thresholds → sends email alerts

### Background Jobs (Production)

1. IoT Sensor Simulator (continuous)
   - 5 sensors generating PM2.5, PM10, NO2 data
   - 15-minute intervals
   - Auto-registers in sensor_metadata table

2. Anomaly Detection (every 30 minutes)
   - Z-score and Isolation Forest algorithms
   - Analyzes last 24 hours
   - Saves high/critical anomalies to alerts table

---

## Installation

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn
- Git
- Supabase account (free tier works)

### Backend Setup

1. Clone the repo
   ```bash
   git clone https://github.com/yourusername/smartcity.git
   cd smartcity/backend
   ```

2. Create virtual environment
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file in `backend/` directory:
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

5. Set up database
   - Go to https://supabase.com and create a project
   - Open Supabase SQL Editor
   - Copy contents from `backend/database/schema.sql`
   - Paste and execute to create tables
   - Go to Settings → API and copy your keys
   - Add keys to `.env` file

6. Run the backend
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
   ```

   API at: http://localhost:8080
   Docs at: http://localhost:8080/docs

### Frontend Setup

1. Navigate to frontend
   ```bash
   cd ../frontend
   ```

2. Install dependencies
   ```bash
   npm install
   ```

3. Create `.env` file in `frontend/` directory:
   ```env
   VITE_API_URL=http://localhost:8080
   ```

4. Run dev server
   ```bash
   npm run dev
   ```

   Frontend at: http://localhost:5173

---

## Usage

### Starting the App

Development mode:

1. Start backend (Terminal 1):
   ```bash
   cd backend
   source venv/bin/activate  # Windows: venv\Scripts\activate
   uvicorn app.main:app --reload --port 8080
   ```

2. Start frontend (Terminal 2):
   ```bash
   cd frontend
   npm run dev
   ```

3. Start IoT sensors (Terminal 3, optional):
   ```bash
   cd backend
   python app/simulators/iot_sensor.py
   ```

### Access Points

- Frontend: http://localhost:5173
- Backend: http://localhost:8080
- API Docs: http://localhost:8080/docs
- Health: http://localhost:8080/health

### How to Use

1. Dashboard - View current PM2.5, PM10, NO2 levels and trends
2. Map - Toggle pollution heatmap, sensors, Vélib stations, traffic, transit
3. Predictions - See 24-hour PM2.5 forecasts with confidence scores
4. Mobility - Check Vélib availability, traffic disruptions, transit times
5. Analytics - Analyze pollution-weather correlation and patterns (login required)
6. Reports - Generate PDF reports for custom date ranges (login required)

---

## IoT Sensors

### Sensor Locations

5 sensors placed across Paris:

- SENSOR_001 - Paris Centre (48.8566°N, 2.3522°E)
- SENSOR_002 - Paris Nord (48.8738°N, 2.2950°E)
- SENSOR_003 - Paris Sud (48.8414°N, 2.3209°E)
- SENSOR_004 - Paris Est (48.8467°N, 2.3775°E)
- SENSOR_005 - Paris Ouest (48.8656°N, 2.2879°E)

All measure: PM2.5, PM10, NO2

### Data Collection

- Measurement every 15 minutes
- 96 readings per sensor per day
- 480 total daily readings (5 sensors × 96)
- Sends via HTTP POST to `/api/v1/air-quality/measurements`

### Simulation

Sensors are simulated with realistic patterns:
- Daily cycles (peaks during rush hours 7-9am, 5-7pm)
- Random noise (±10%)
- Occasional spikes (5% chance, 1.5-2x multiplier)
- Gradual drift over time

Run simulator:
```bash
cd backend
python app/simulators/iot_sensor.py
```

Auto-registers sensors, sends data every 15 min, logs transmissions.

---

## API Documentation

### Base URLs

- Development: http://localhost:8080
- Production: https://smartcity-platform-production.up.railway.app

### Authentication

Some endpoints need JWT auth via Supabase:

```bash
# 1. Register new user
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe"  # optional
}

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}

# 2. Login
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "yourpassword"
}

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {...}
}

# 3. Forgot password (sends reset email)
POST /api/v1/auth/forgot-password
Content-Type: application/json

{
  "email": "user@example.com"
}

# 4. Reset password (with token from email)
POST /api/v1/auth/reset-password
Content-Type: application/json

{
  "token": "reset_token_from_email",
  "new_password": "newsecurepassword"
}

# 5. Logout
POST /api/v1/auth/logout
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

# 6. Use token in subsequent requests
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

#### Supabase Setup for Production

Before deploying, configure Supabase:

1. Go to https://supabase.com/dashboard
2. Select your project → Authentication → URL Configuration
3. Set Site URL: `https://frontend-gamma-three-19.vercel.app`
4. Add Redirect URLs:
   - `https://frontend-gamma-three-19.vercel.app/**`
   - `https://frontend-gamma-three-19.vercel.app/login`
   - `http://localhost:3000/**`
5. Enable email verification: Authentication → Providers → Email → Confirm email
6. Users must verify email before login works

### Main Endpoints

Air Quality:
- `GET /api/v1/air-quality/current?city=paris` - current readings
- `GET /api/v1/air-quality/history?city=paris&limit=100` - historical data
- `POST /api/v1/air-quality/measurements` - create measurement (sensors)

Predictions:
- `GET /api/v1/predictions/current?city=paris` - next 24h forecast
- `GET /api/v1/predictions/history?city=paris&days=7` - past predictions
- `POST /api/v1/predictions/train` - retrain model

Mobility:
- `GET /api/v1/mobility/velib?limit=50` - Vélib stations
- `GET /api/v1/mobility/traffic-disruptions?severity=high` - traffic issues
- `GET /api/v1/mobility/transit-stops?limit=50` - transit stops
- `GET /api/v1/mobility/next-departures?stop_id=STIF:StopPoint:Q:41322:` - departures

Analytics:
- `GET /api/v1/analytics/pollution-weather-correlation?city=paris&days=30`
- `GET /api/v1/analytics/temporal-analysis?city=paris&days=7`
- `GET /api/v1/analytics/statistics?city=paris&days=30`

Alerts:
- `GET /api/v1/alerts/active` - active alerts
- `POST /api/v1/alerts` - create alert
- `PATCH /api/v1/alerts/{id}/acknowledge` - acknowledge alert

Reports:
- `POST /api/v1/reports/generate` - generate PDF

Full docs: http://localhost:8080/docs

---

## Deployment

### Backend (Railway)

1. Create account at https://railway.app
2. Create new project: `railway init`
3. Add environment variables in Railway dashboard
4. Deploy: `railway up`
5. Get URL: https://smartcity-platform-production.up.railway.app

### Frontend (Vercel)

1. Install CLI: `npm install -g vercel`
2. Deploy: `cd frontend && vercel`
3. Add env var `VITE_API_URL` in Vercel dashboard
4. Get URL: https://frontend-gamma-three-19.vercel.app
5. Update Supabase redirect URLs (see Authentication section)

### Database (Supabase)

Already cloud-hosted. Just enable RLS policies and create indexes.

---

## Production URLs

Live app:
- Frontend: https://frontend-gamma-three-19.vercel.app
- Backend: https://smartcity-platform-production.up.railway.app
- API Docs: https://smartcity-platform-production.up.railway.app/docs
- Health: https://smartcity-platform-production.up.railway.app/health

Demo login:
- Email: demo@smartcity.com
- Password: Demo2024!

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

- API response: < 200ms
- Dashboard load: < 2 seconds
- Database queries: < 50ms
- ML predictions: < 500ms
- PDF generation: < 3 seconds

Optimizations:
- Database indexes on city, timestamp, source
- TanStack Query caching (5min stale time)
- React.lazy() code splitting
- Vercel Edge CDN
- Gzip/Brotli compression

---

## Security

- JWT tokens (HS256, 60min expiry)
- Row Level Security on database
- Pydantic input validation
- SQL injection prevention
- XSS protection
- HTTPS everywhere
- Environment variables for secrets

---

## Monitoring

- Health check: `/health`
- JSON logging
- Supabase dashboard for queries
- Email alerts for errors and threshold breaches
- Sensor offline detection

---

## Contributing

1. Fork the repo
2. Create feature branch: `git checkout -b feature/name`
3. Commit changes: `git commit -m "Add feature"`
4. Push: `git push origin feature/name`
5. Create Pull Request

Code standards:
- Backend: PEP 8, type hints, docstrings
- Frontend: TypeScript strict mode
- Write tests for new features

Run tests:
```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm test
```

---

## License

MIT License

---

## Credits

- Île-de-France Mobilités (IDFM) - mobility APIs
- Supabase - database and auth
- FastAPI and React communities
- ESIS-2 Team

---

**Built:** December 18-31, 2024
**Version:** 1.0.0
