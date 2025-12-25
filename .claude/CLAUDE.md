# Smart City Platform - Context Engineering

## Project Overview

Real-time air quality and mobility monitoring platform for metropolitan areas. The platform collects data from multiple sources (APIs, IoT sensors), analyzes it with ML models, and presents actionable insights through an interactive dashboard.

**Target Users:**
- Environmental managers (Marie Dubois - persona principal)
- City officials making policy decisions
- Citizens concerned about air quality

## Architecture

### Technology Stack

**Backend:**
- FastAPI (Python 3.11+) - REST API framework
- Supabase (PostgreSQL 17) - Database and authentication
- Scikit-learn - ML predictions
- Uvicorn - ASGI server

**Frontend:**
- React 18 + TypeScript 5
- Vite - Build tool
- TanStack Query - Server state management
- Zustand - Global state management
- Tailwind CSS - Styling
- Chart.js - Data visualization
- Leaflet.js - Interactive maps

**External APIs:**
- AQICN - Air quality data
- OpenWeatherMap - Weather data

### Key Components

1. **Data Collection:**
   - AQICN API (hourly air quality)
   - OpenWeatherMap API (weather conditions)
   - 3 IoT sensors (simulated, 15-min intervals)

2. **Data Storage:**
   - air_quality_measurements table (time-series)
   - weather_data table
   - predictions table
   - sensor_metadata table
   - alerts table

3. **ML Pipeline:**
   - PM2.5 prediction (J+1 forecast)
   - Anomaly detection (Z-score method)
   - Feature engineering (7-day rolling stats, temporal features)

4. **Dashboard:**
   - Real-time KPI cards
   - Interactive charts (Chart.js)
   - Multi-layer map (Leaflet)
   - Prediction display
   - Alert system

## Project Structure

```
smartcity/
├── .claude/                    # Claude Code configuration
│   ├── skills/                 # Specialized skills
│   │   ├── backend-api/
│   │   ├── ml-predictions/
│   │   ├── frontend-dashboard/
│   │   ├── database-schema/
│   │   ├── iot-simulation/
│   │   └── external-apis/
│   ├── commands/               # Slash commands
│   └── CLAUDE.md              # This file
│
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/v1/
│   │   ├── services/
│   │   ├── models/
│   │   ├── ml/
│   │   ├── simulators/
│   │   └── utils/
│   ├── requirements.txt
│   └── .env
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── services/
│   │   ├── hooks/
│   │   ├── stores/
│   │   └── types/
│   ├── package.json
│   └── vite.config.ts
│
├── docs/                       # Documentation
│   ├── TECHNICAL.md
│   └── fonctionnel.md
│
└── README.md
```

## Key Paths

**Backend:**
- API routes: `backend/app/api/v1/`
- Services: `backend/app/services/`
- ML models: `backend/app/ml/`
- Pydantic models: `backend/app/models/`

**Frontend:**
- Pages: `frontend/src/pages/`
- Components: `frontend/src/components/`
- API services: `frontend/src/services/`
- Custom hooks: `frontend/src/hooks/`

**Documentation:**
- Technical: `docs/TECHNICAL.md`
- Functional: `docs/fonctionnel.md`

## Coding Standards

### Backend (Python)

- Use async/await for all route handlers
- Pydantic models for request/response validation
- Service layer pattern (routes → services → database)
- Type hints on all functions
- Dependency injection via FastAPI Depends
- Error handling with HTTPException

**Example:**
```python
@router.get("/air-quality/current", response_model=AirQualityResponse)
async def get_current_air_quality(
    city: str = Query(...),
    service: AirQualityService = Depends(get_air_quality_service)
):
    data = await service.get_current_data(city)
    if not data:
        raise HTTPException(status_code=404, detail="No data found")
    return data
```

### Frontend (TypeScript/React)

- Functional components with hooks
- TypeScript strict mode
- Props typed with interfaces
- TanStack Query for API calls
- Tailwind CSS for styling
- Responsive design (mobile-first)

**Example:**
```typescript
interface KPICardProps {
  title: string;
  value: number;
  unit: string;
  severity: 'good' | 'moderate' | 'poor';
}

export const KPICard: React.FC<KPICardProps> = ({ title, value, unit, severity }) => {
  return (
    <div className={`rounded-lg p-6 ${severityColors[severity]}`}>
      <h3>{title}</h3>
      <p className="text-3xl">{value.toFixed(1)} {unit}</p>
    </div>
  );
};
```

### Database (SQL)

- Row Level Security (RLS) enabled on all tables
- Indexes on frequently queried columns
- CHECK constraints for validation
- JSONB for flexible location data
- Time-series optimizations

## Skills Available

Activate skills based on your task context:

| Skill | When to Use |
|-------|-------------|
| **backend-api** | Creating/modifying FastAPI routes, Pydantic models, services |
| **ml-predictions** | Training models, making predictions, anomaly detection |
| **frontend-dashboard** | Building React components, charts, maps, UI |
| **database-schema** | Writing SQL queries, creating tables, RLS policies |
| **iot-simulation** | Simulating sensors, generating test data |
| **external-apis** | Integrating AQICN, OpenWeatherMap, API calls |
| **mobility-data** | IDFM/PRIM APIs, Vélib, traffic disruptions, transit data |
| **realtime-transport** | GTFS-RT, real-time departures, delays, WebSocket patterns |
| **isochrones** | Accessibility zones, OpenRouteService, GeoJSON, map visualization |

## Slash Commands

Quick actions for common tasks:

- `/add-api-route` - Create new FastAPI endpoint
- `/create-component` - Generate React component
- `/run-ml-training` - Train/retrain prediction model
- `/test-sensors` - Test IoT sensor simulation

## Workflows Available

Step-by-step guides for implementing complete features:

| Workflow | Description | Priority |
|----------|-------------|----------|
| **dashboard-setup** | Basic dashboard with KPIs and charts | High |
| **authentication-setup** | JWT auth with Supabase | High |
| **ml-pipeline-setup** | PM2.5 predictions pipeline | High |
| **advanced-features** | Interactive map, correlations, export | Medium |
| **alerts-implementation** | Email notifications system | Medium |
| **anomaly-detection-setup** | Z-score + Isolation Forest | Medium |
| **pdf-reports-implementation** | PDF generation with charts | Low |
| **final-touches** | Optimization, monitoring, tests | Low |

**Index:** See `.claude/workflows/INDEX.md` for complete navigation

## Environment Variables

Required environment variables (`.env` files):

**Backend:**
```bash
SUPABASE_URL=https://vnznhsbjqxufvhasotid.supabase.co
SUPABASE_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key
OPENWEATHER_API_KEY=your_api_key
AQICN_API_TOKEN=your_token
SECRET_KEY=your_secret_key
```

**Frontend:**
```bash
VITE_API_URL=http://localhost:8000
```

## Current Sprint: Sprint 2

**Focus:**
- Advanced dashboard features
- ML prediction integration
- Alert system
- Multi-layer interactive map

**User Stories in Progress:**
- US-009: J+1 air quality prediction
- US-012: Interactive map with pollution zones
- US-013: Pollution-weather correlation charts
- US-015: Email alerts for threshold exceedance

## Performance Targets

- API response time: < 200ms (95th percentile)
- Dashboard load time: < 2 seconds
- Database queries: < 50ms
- ML prediction: < 500ms
- Model accuracy: R² > 0.7, MAPE < 30%

## Security Requirements

- JWT authentication for protected routes
- RLS policies on all Supabase tables
- Input validation with Pydantic
- Rate limiting on public endpoints
- CORS configured for trusted origins
- No API keys in version control

## Database Schema

**Main Tables:**
- `air_quality_measurements` - Time-series pollution data
- `weather_data` - Meteorological data
- `predictions` - ML model predictions
- `sensor_metadata` - IoT sensor registry
- `alerts` - System alerts

**Key Indexes:**
- `idx_timestamp_source` - Fast time-series queries
- `idx_city_timestamp` - City-specific data retrieval
- `idx_location` - GIN index for JSONB location queries

## Testing

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

## Deployment

**Development:**
```bash
# Backend
cd backend && uvicorn app.main:app --reload

# Frontend
cd frontend && npm run dev

# Sensors (optional)
python backend/app/simulators/run_simulation.py --interval 60
```

**Production:**
- Backend: Railway, Fly.io, or Vercel
- Frontend: Vercel or Netlify
- Database: Supabase (managed PostgreSQL)

## References

**Documentation:**
- Technical specs: `docs/TECHNICAL.md`
- Functional requirements: `docs/fonctionnel.md`

**External:**
- FastAPI: https://fastapi.tiangolo.com/
- React: https://react.dev
- Supabase: https://supabase.com/docs
- Scikit-learn: https://scikit-learn.org/

## Project Constraints

- **Budget:** €0 (free tiers only)
- **Timeline:** 1 month (3 sprints)
- **Team:** 5-7 people
- **Data:** Minimum 6 months historical for ML training
- **Compliance:** RGPD (no personal data storage)

## Success Criteria

**Sprint 1 (MVP):**
- ✅ API collecting data hourly
- ✅ 7+ days historical data in database
- ✅ Dashboard with 3+ KPI cards
- ✅ Basic authentication

**Sprint 2 (Advanced):**
- 🔄 ML prediction with 70%+ accuracy
- 🔄 Interactive map with multiple layers
- 🔄 Alert system with email notifications
- 🔄 Pollution-weather correlation analysis

**Sprint 3 (Production):**
- ⬜ Performance optimized (< 2s load time)
- ⬜ Mobile responsive interface
- ⬜ Monitoring and logging
- ⬜ PDF report generation

---

**Last Updated:** 2025-12-24
**Version:** 1.0.0
**Maintained By:** ESIS-2 Team
