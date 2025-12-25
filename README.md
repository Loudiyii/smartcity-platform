# Smart City Platform

> Real-time air quality and mobility monitoring platform for metropolitan areas

## 🚀 Quick Start

**New to the project?** Follow our complete setup guide: **[PHASE1_SETUP.md](PHASE1_SETUP.md)**

This guide walks you through:
- Database setup (Supabase)
- Backend configuration (FastAPI)
- Frontend installation (React)
- Running IoT sensors
- Verifying everything works

---

## Overview

The Smart City Platform collects, analyzes, and visualizes air quality data from multiple sources (APIs, IoT sensors) to help city officials and citizens make informed decisions about environmental health.

### Key Features

- 📊 **Real-time Dashboard** - Live air quality monitoring with interactive visualizations
- 🤖 **AI Predictions** - Next-day PM2.5 forecasting with >70% accuracy
- 🗺️ **Interactive Maps** - Multi-layer Leaflet maps showing pollution zones and sensors
- 🔔 **Smart Alerts** - Automated notifications for pollution threshold exceedances
- 📱 **Responsive Design** - Mobile-friendly interface for on-the-go access

## Technology Stack

### Backend
- **FastAPI** (Python 3.11+) - High-performance REST API
- **Supabase** (PostgreSQL 17) - Database and authentication
- **Scikit-learn** - Machine learning for predictions
- **Uvicorn** - ASGI server

### Frontend
- **React 18** + **TypeScript 5** - Modern UI framework
- **Vite** - Lightning-fast build tool
- **TanStack Query** - Server state management
- **Chart.js** - Data visualization
- **Leaflet.js** - Interactive maps
- **Tailwind CSS** - Utility-first styling

### Data Sources
- **AQICN API** - Global air quality data
- **OpenWeatherMap** - Weather conditions
- **IoT Sensors** - Simulated local sensors (3 units)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      USERS                                   │
│  (Environmental Managers, Officials, Citizens)               │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              FRONTEND (React + TypeScript)                   │
│  • Dashboard  • Charts  • Maps  • Predictions               │
└───────────────────────┬─────────────────────────────────────┘
                        │ REST API
                        ▼
┌─────────────────────────────────────────────────────────────┐
│               BACKEND (FastAPI)                              │
│  • API Routes  • Services  • ML Engine                      │
└───────┬────────────────┬──────────────────┬─────────────────┘
        │                │                  │
        ▼                ▼                  ▼
┌──────────────┐ ┌──────────────┐ ┌─────────────────┐
│   SUPABASE   │ │ APIs Externes│ │ IoT Sensors     │
│  PostgreSQL  │ │ • AQICN      │ │ (Simulated)     │
│              │ │ • OpenWeather│ │                 │
└──────────────┘ └──────────────┘ └─────────────────┘
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Supabase account (free tier)
- API keys for AQICN and OpenWeatherMap

### Installation

#### 1. Clone the repository

```bash
git clone https://github.com/your-org/smartcity.git
cd smartcity
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your API keys and Supabase credentials
```

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env
# Edit .env with API URL
```

### Configuration

Create `.env` files in both backend and frontend directories:

**backend/.env:**
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key
OPENWEATHER_API_KEY=your_api_key
AQICN_API_TOKEN=your_token
SECRET_KEY=your_secret_key
```

**frontend/.env:**
```bash
VITE_API_URL=http://localhost:8000
```

### Running the Application

#### Start Backend

```bash
cd backend
uvicorn app.main:app --reload
```

API will be available at: http://localhost:8000
Interactive docs: http://localhost:8000/docs

#### Start Frontend

```bash
cd frontend
npm run dev
```

Frontend will be available at: http://localhost:5173

#### Start IoT Sensors (Optional)

```bash
cd backend
python app/simulators/run_simulation.py --interval 60
```

## Project Structure

```
smartcity/
├── .claude/                    # Claude Code skills & commands
│   ├── skills/                 # Context engineering skills
│   └── commands/               # Quick action commands
│
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # Application entry point
│   │   ├── config.py          # Configuration management
│   │   ├── api/v1/            # API route handlers
│   │   ├── services/          # Business logic layer
│   │   ├── models/            # Pydantic models
│   │   ├── ml/                # Machine learning models
│   │   ├── simulators/        # IoT sensor simulation
│   │   └── utils/             # Utilities
│   └── requirements.txt
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── pages/             # Page components
│   │   ├── components/        # Reusable components
│   │   ├── services/          # API clients
│   │   ├── hooks/             # Custom React hooks
│   │   ├── stores/            # Zustand stores
│   │   └── types/             # TypeScript types
│   └── package.json
│
└── docs/                       # Documentation
    ├── TECHNICAL.md           # Technical specifications
    └── fonctionnel.md         # Functional requirements
```

## API Documentation

Once the backend is running, visit:
- **Interactive API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Key Endpoints

```
GET  /api/v1/air-quality/current?city=paris
GET  /api/v1/air-quality/history?city=paris&limit=100
POST /api/v1/air-quality/measurements
GET  /api/v1/predictions/pm25
GET  /api/v1/weather/{city}
GET  /health
```

## Machine Learning

### PM2.5 Prediction Model

The platform uses a Random Forest Regressor to predict next-day PM2.5 concentrations.

**Features:**
- 7-day rolling statistics (mean, std, max, min)
- Lag features (24h, 48h)
- Weather conditions (temperature, humidity, wind)
- Temporal features (hour, day of week, season)

**Performance Targets:**
- R² > 0.7
- MAPE < 30%
- RMSE minimized

**Training:**
```bash
cd backend
python -m app.ml.trainer --data-path data/historical.csv
```

## Development

### Running Tests

**Backend:**
```bash
pytest backend/tests/ -v
pytest --cov=app --cov-report=html
```

**Frontend:**
```bash
npm test
npm run test:coverage
```

### Code Quality

**Backend:**
```bash
# Linting
flake8 backend/app
black backend/app

# Type checking
mypy backend/app
```

**Frontend:**
```bash
# Linting
npm run lint
npm run type-check
```

## Deployment

### Backend (Railway / Fly.io)

```bash
# Build Docker image
docker build -t smartcity-backend ./backend

# Deploy to Railway
railway up
```

### Frontend (Vercel)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel --prod
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **AQICN** for air quality data
- **OpenWeatherMap** for weather data
- **Supabase** for database and auth
- **ESIS-2** team for project development

## Contact

**Project Lead:** Joel BANKA
**Team:** ESIS-2 / CPDIA-2
**Year:** 2025

---

**Status:** 🚧 In Development (Sprint 2)
**Last Updated:** 2025-12-24
