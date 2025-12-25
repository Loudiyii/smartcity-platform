# Documentation Technique - Smart City Platform

## Architecture Globale

### Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────┐
│                      UTILISATEURS                            │
│  (Responsables Env, Élus, Citoyens)                         │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              FRONTEND (React + TypeScript)                   │
│  • Dashboard temps réel (Air + Mobilité)                    │
│  • Cartes interactives (React Leaflet - 5 couches)         │
│  • Graphiques (Chart.js via react-chartjs-2)               │
│  • State management (TanStack Query + Zustand)              │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTPS/REST API
                        ▼
┌─────────────────────────────────────────────────────────────┐
│               BACKEND (FastAPI)                              │
│  ┌──────────────┬──────────────┬────────────────┐          │
│  │ API Routes   │  Services    │  ML Engine     │          │
│  │ (v1)         │              │  (Predictions) │          │
│  └──────────────┴──────────────┴────────────────┘          │
└───────┬────────────────┬──────────────────┬─────────────────┘
        │                │                  │
        ▼                ▼                  ▼
┌──────────────┐ ┌──────────────┐ ┌─────────────────┐
│   SUPABASE   │ │ APIs Externes│ │ Capteurs IoT    │
│  (PostgreSQL)│ │ • AQICN      │ │ (Simulés)       │
│  • Data      │ │ • OpenWeather│ │ • 3 Capteurs    │
│  • Auth      │ │              │ │ • Toutes 15min  │
│  • Storage   │ │              │ │                 │
└──────────────┘ └──────────────┘ └─────────────────┘
```

## Stack Technique Détaillée

### Backend - FastAPI

**Version:** Python 3.11+

**Dépendances principales:**
```python
fastapi==0.104.1              # Framework API REST
uvicorn[standard]==0.24.0     # Serveur ASGI
supabase==2.3.0               # Client Supabase
python-dotenv==1.0.0          # Variables d'environnement
httpx==0.25.2                 # Client HTTP async
pydantic==2.5.0               # Validation données
python-jose[cryptography]     # JWT tokens
scikit-learn==1.3.2           # ML/Prédictions
pandas==2.1.4                 # Analyse de données
numpy==1.26.2                 # Calculs numériques
```

**Architecture modulaire:**
```
backend/app/
├── main.py                    # Point d'entrée
├── config.py                  # Configuration centralisée
├── dependencies.py            # Injection de dépendances
│
├── api/v1/                    # Routes API
│   ├── air_quality.py
│   ├── weather.py
│   ├── sensors.py
│   ├── predictions.py
│   ├── auth.py
│   └── reports.py
│
├── services/                  # Logique métier
│   ├── supabase_service.py   # Client Supabase
│   ├── air_quality_service.py
│   ├── weather_service.py
│   └── alert_service.py
│
├── models/                    # Modèles Pydantic
│   ├── air_quality.py
│   ├── sensor.py
│   └── prediction.py
│
├── ml/                        # Machine Learning
│   ├── predictor.py          # Modèle de prédiction
│   ├── anomaly_detector.py   # Détection anomalies
│   └── trainer.py            # Entraînement modèles
│
├── simulators/                # IoT Simulation
│   └── iot_sensor.py
│
└── utils/
    ├── logger.py
    └── validators.py
```

### Base de Données - Supabase (PostgreSQL 17)

**Configuration du projet:**
- **Project ID:** vnznhsbjqxufvhasotid
- **Région:** eu-central-2 (Francfort)
- **Version PostgreSQL:** 17.6.1
- **Status:** ACTIVE_HEALTHY

#### Schéma de Base de Données

##### Table: `air_quality_measurements`
```sql
CREATE TABLE air_quality_measurements (
  id BIGSERIAL PRIMARY KEY,
  source VARCHAR(50) NOT NULL,           -- 'api' ou 'sensor_xxx'
  city VARCHAR(100),
  location JSONB,                        -- {lat, lon, name}

  -- Polluants
  aqi INTEGER,
  pm25 REAL,
  pm10 REAL,
  no2 REAL,
  o3 REAL,
  so2 REAL,

  -- Métadonnées
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW(),

  -- Index pour performances
  CONSTRAINT check_pm25_positive CHECK (pm25 >= 0),
  CONSTRAINT check_timestamp_valid CHECK (timestamp <= NOW())
);

-- Index pour requêtes time-series
CREATE INDEX idx_timestamp_source ON air_quality_measurements(timestamp DESC, source);
CREATE INDEX idx_city_timestamp ON air_quality_measurements(city, timestamp DESC);
CREATE INDEX idx_source ON air_quality_measurements(source);

-- Enable Row Level Security (RLS)
ALTER TABLE air_quality_measurements ENABLE ROW LEVEL SECURITY;

-- Policy: lecture publique, écriture authentifiée
CREATE POLICY "Public read access"
ON air_quality_measurements FOR SELECT
USING (true);

CREATE POLICY "Authenticated write access"
ON air_quality_measurements FOR INSERT
TO authenticated
WITH CHECK (true);
```

##### Table: `weather_data`
```sql
CREATE TABLE weather_data (
  id BIGSERIAL PRIMARY KEY,
  city VARCHAR(100) NOT NULL,

  -- Données météo
  temperature REAL NOT NULL,
  humidity INTEGER CHECK (humidity BETWEEN 0 AND 100),
  pressure INTEGER,
  wind_speed REAL CHECK (wind_speed >= 0),
  wind_direction INTEGER CHECK (wind_direction BETWEEN 0 AND 360),

  -- Métadonnées
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_weather_city_timestamp ON weather_data(city, timestamp DESC);

ALTER TABLE weather_data ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read weather"
ON weather_data FOR SELECT
USING (true);
```

##### Table: `predictions`
```sql
CREATE TABLE predictions (
  id BIGSERIAL PRIMARY KEY,
  pollutant VARCHAR(20) NOT NULL,        -- 'pm25', 'pm10', etc.
  predicted_value REAL NOT NULL,
  confidence_score REAL CHECK (confidence_score BETWEEN 0 AND 1),

  -- Date de prédiction
  prediction_for_date DATE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),

  -- Modèle utilisé
  model_version VARCHAR(50),
  model_accuracy REAL,

  CONSTRAINT unique_prediction_per_day UNIQUE (pollutant, prediction_for_date)
);

CREATE INDEX idx_predictions_date ON predictions(prediction_for_date DESC);
```

##### Table: `sensor_metadata`
```sql
CREATE TABLE sensor_metadata (
  sensor_id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(100),
  location JSONB NOT NULL,               -- {lat, lon, address}
  status VARCHAR(20) DEFAULT 'active',   -- 'active', 'maintenance', 'offline'
  last_reading_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Spatial index pour recherches géographiques
CREATE INDEX idx_sensor_location ON sensor_metadata USING GIN (location);
```

##### Table: `alerts`
```sql
CREATE TABLE alerts (
  id BIGSERIAL PRIMARY KEY,
  alert_type VARCHAR(50) NOT NULL,       -- 'threshold_exceeded', 'anomaly_detected'
  severity VARCHAR(20) NOT NULL,         -- 'low', 'medium', 'high', 'critical'
  pollutant VARCHAR(20),
  value REAL,
  threshold REAL,

  message TEXT,
  sent_at TIMESTAMPTZ,
  acknowledged BOOLEAN DEFAULT FALSE,
  acknowledged_at TIMESTAMPTZ,

  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_alerts_created ON alerts(created_at DESC);
CREATE INDEX idx_alerts_acknowledged ON alerts(acknowledged, created_at);
```

#### Fonctions SQL Utilitaires

```sql
-- Fonction: Obtenir la moyenne des mesures sur N heures
CREATE OR REPLACE FUNCTION get_average_pm25(hours INTEGER DEFAULT 24)
RETURNS REAL AS $$
BEGIN
  RETURN (
    SELECT AVG(pm25)
    FROM air_quality_measurements
    WHERE timestamp >= NOW() - INTERVAL '1 hour' * hours
      AND pm25 IS NOT NULL
  );
END;
$$ LANGUAGE plpgsql;

-- Fonction: Détecter anomalies (écart > 3 sigma)
CREATE OR REPLACE FUNCTION detect_anomalies(threshold REAL DEFAULT 3.0)
RETURNS TABLE(id BIGINT, pm25 REAL, z_score REAL) AS $$
BEGIN
  RETURN QUERY
  WITH stats AS (
    SELECT
      AVG(pm25) as mean,
      STDDEV(pm25) as stddev
    FROM air_quality_measurements
    WHERE timestamp >= NOW() - INTERVAL '7 days'
  )
  SELECT
    m.id,
    m.pm25,
    ABS((m.pm25 - s.mean) / NULLIF(s.stddev, 0)) as z_score
  FROM air_quality_measurements m, stats s
  WHERE ABS((m.pm25 - s.mean) / NULLIF(s.stddev, 0)) > threshold
    AND m.timestamp >= NOW() - INTERVAL '24 hours'
  ORDER BY z_score DESC;
END;
$$ LANGUAGE plpgsql;
```

### Frontend

**Technologies:**
- **Framework:** React 18 + TypeScript 5
- **Build Tool:** Vite 5
- **Routing:** React Router v6
- **State Management:** Zustand (global state) + TanStack Query (server state)
- **Styling:** Tailwind CSS 3
- **Graphiques:** Chart.js 4.4 (via react-chartjs-2)
- **Cartes:** Leaflet.js 1.9 (via react-leaflet)
- **HTTP Client:** Axios + TanStack Query
- **Forms:** React Hook Form + Zod validation
- **UI Components:** Headless UI + custom components

**Architecture Frontend:**
```
frontend/
├── public/
├── src/
│   ├── main.tsx                 # Point d'entrée
│   ├── App.tsx                  # Root component
│   ├── router.tsx               # React Router config
│   │
│   ├── pages/                   # Pages principales
│   │   ├── Home.tsx
│   │   ├── Dashboard.tsx
│   │   ├── DashboardMap.tsx
│   │   ├── Predictions.tsx
│   │   ├── Admin.tsx
│   │   └── Reports.tsx
│   │
│   ├── components/              # Composants réutilisables
│   │   ├── Dashboard/
│   │   │   ├── KPICard.tsx
│   │   │   ├── AirQualityChart.tsx
│   │   │   ├── VelibChart.tsx
│   │   │   └── TransportDelaysChart.tsx
│   │   ├── Map/
│   │   │   ├── LeafletMap.tsx
│   │   │   ├── IoTSensorsLayer.tsx
│   │   │   ├── VelibStationsLayer.tsx
│   │   │   ├── TransitStopsLayer.tsx
│   │   │   ├── IsochronesLayer.tsx
│   │   │   └── DisruptionsLayer.tsx
│   │   ├── Charts/
│   │   │   ├── LineChart.tsx
│   │   │   ├── BarChart.tsx
│   │   │   └── ScatterPlot.tsx
│   │   └── UI/
│   │       ├── Button.tsx
│   │       ├── Card.tsx
│   │       └── LoadingSpinner.tsx
│   │
│   ├── services/                # API clients
│   │   ├── api.ts              # Axios config
│   │   ├── airQualityService.ts
│   │   ├── mobilityService.ts
│   │   ├── weatherService.ts
│   │   └── authService.ts
│   │
│   ├── hooks/                   # Custom hooks
│   │   ├── useAirQuality.ts
│   │   ├── useVelibStats.ts
│   │   ├── useTransportData.ts
│   │   └── useAuth.ts
│   │
│   ├── stores/                  # Zustand stores
│   │   ├── authStore.ts
│   │   └── mapStore.ts
│   │
│   ├── types/                   # TypeScript types
│   │   ├── airQuality.ts
│   │   ├── mobility.ts
│   │   └── api.ts
│   │
│   └── utils/
│       ├── formatters.ts
│       └── validators.ts
│
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

**Routes principales:**
```
/                       → Landing page
/dashboard              → Dashboard temps réel (Air + Mobilité)
/dashboard/map          → Carte interactive (5 couches)
/dashboard/predictions  → Prédictions IA (Air + Transport)
/admin                  → Interface admin (protégé)
/reports                → Rapports PDF (Air, Mobilité, Combiné)
```

**Dépendances principales:**
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "@tanstack/react-query": "^5.13.0",
    "zustand": "^4.4.7",
    "axios": "^1.6.2",
    "react-leaflet": "^4.2.1",
    "leaflet": "^1.9.4",
    "react-chartjs-2": "^5.2.0",
    "chart.js": "^4.4.0",
    "react-hook-form": "^7.48.2",
    "zod": "^3.22.4"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/leaflet": "^1.9.8",
    "typescript": "^5.3.3",
    "vite": "^5.0.8",
    "tailwindcss": "^3.3.6",
    "@vitejs/plugin-react": "^4.2.1"
  }
}
```

### APIs Externes

#### AQICN (Air Quality Index China)
```
Base URL: https://api.waqi.info
Endpoint: /feed/{city}/
Params: ?token={AQICN_API_TOKEN}

Response:
{
  "status": "ok",
  "data": {
    "aqi": 42,
    "iaqi": {
      "pm25": {"v": 29},
      "pm10": {"v": 35},
      "no2": {"v": 15}
    }
  }
}
```

#### OpenWeatherMap
```
Base URL: https://api.openweathermap.org/data/2.5
Endpoint: /weather
Params: ?q={city}&appid={API_KEY}&units=metric

Response:
{
  "main": {
    "temp": 15.3,
    "humidity": 72,
    "pressure": 1013
  },
  "wind": {
    "speed": 3.2,
    "deg": 180
  }
}
```

## Machine Learning - Modèle Prédictif

### Objectif
Prédire la concentration de PM2.5 à J+1 avec une précision > 70%

### Architecture du modèle

```python
# Features (variables d'entrée)
X = [
    'pm25_mean_7d',           # Moyenne PM2.5 7 derniers jours
    'pm25_std_7d',            # Écart-type PM2.5
    'temperature',            # Température actuelle
    'humidity',               # Humidité
    'wind_speed',             # Vitesse du vent
    'pressure',               # Pression atmosphérique
    'day_of_week',            # Jour de la semaine (0-6)
    'is_weekend',             # Booléen weekend
    'season'                  # Saison (0-3)
]

# Target (variable à prédire)
y = 'pm25_next_day'
```

### Algorithmes testés
1. **Baseline:** Régression linéaire multiple
2. **Production:** Random Forest Regressor (meilleure performance)
3. **Avancé:** XGBoost (si temps disponible)

### Métriques d'évaluation
```python
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

RMSE = sqrt(mean_squared_error(y_true, y_pred))
MAE = mean_absolute_error(y_true, y_pred)
R² = r2_score(y_true, y_pred)
MAPE = mean_absolute_percentage_error(y_true, y_pred)

# Objectif: MAPE < 30%, R² > 0.7
```

### Pipeline d'entraînement
```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit

# 1. Collecte données historiques (minimum 6 mois)
# 2. Feature engineering
# 3. Train/test split temporel (80/20)
# 4. Cross-validation time-series
# 5. Hyperparameter tuning (GridSearchCV)
# 6. Sauvegarde modèle (joblib)
```

## Sécurité

### Authentification - Supabase Auth

**Flow JWT:**
```
1. User → POST /auth/login {email, password}
2. Backend → Supabase Auth verify credentials
3. Supabase → JWT token (expires in 1h)
4. Backend → Return {access_token, refresh_token}
5. User → Include header: Authorization: Bearer {token}
```

**Protection des routes:**
```python
from fastapi import Depends, HTTPException
from supabase import create_client

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        user = supabase.auth.get_user(token)
        return user
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/admin/settings")
async def update_settings(user = Depends(get_current_user)):
    # Route protégée
    pass
```

### Row Level Security (RLS)

Supabase applique automatiquement les politiques RLS sur toutes les requêtes:

```sql
-- Exemple: Seuls les admins peuvent supprimer des mesures
CREATE POLICY "Admin delete only"
ON air_quality_measurements FOR DELETE
TO authenticated
USING (auth.jwt() ->> 'role' = 'admin');
```

### Variables d'environnement sensibles

```bash
# backend/.env (NE JAMAIS COMMITER)
SUPABASE_URL=https://vnznhsbjqxufvhasotid.supabase.co
SUPABASE_KEY=eyJhbGciOiJ... (anon key)
SUPABASE_SERVICE_KEY=eyJhbGciOiJ... (service role key - CRITIQUE)

OPENWEATHER_API_KEY=xxx
AQICN_API_TOKEN=xxx

SECRET_KEY=your-256-bit-secret
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/v1/air-quality/current")
@limiter.limit("60/minute")  # Max 60 requêtes/minute
async def get_current_air_quality():
    pass
```

## Performance & Optimisation

### Caching

**Strategy:** Cache in-memory pour données API externes (TTL: 5 minutes)

```python
from functools import lru_cache
import time

@lru_cache(maxsize=128)
def get_cached_air_quality(city: str, timestamp_bucket: int):
    # timestamp_bucket = timestamp // 300 (5 min buckets)
    return fetch_air_quality_from_api(city)
```

### Index de base de données

Tous les index sont définis dans le schéma SQL ci-dessus. Requêtes optimisées:
- Time-series: Index sur `(timestamp DESC, source)`
- Filtres géographiques: GIN index sur JSONB location
- Recherche par capteur: Index sur `source`

### Métriques de performance attendues

- **Temps de réponse API:** < 200ms (95e percentile)
- **Chargement dashboard:** < 2 secondes
- **Requêtes DB:** < 50ms
- **Prédiction ML:** < 500ms

## Déploiement

### Docker Compose (Développement)

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --reload
```

### Production (Cloud)

**Options recommandées:**
1. **Vercel** (frontend + API routes)
2. **Railway** (backend FastAPI)
3. **Fly.io** (alternative)

**Configuration Supabase:**
- Enable SSL connections
- Set up database backups (daily)
- Configure CORS origins
- Enable RLS on all tables

## Monitoring & Logs

### Structured Logging

```python
import logging
import json

logger = logging.getLogger("smartcity")

logger.info(json.dumps({
    "event": "air_quality_fetched",
    "city": "paris",
    "pm25": 42.5,
    "timestamp": "2025-12-18T10:30:00Z"
}))
```

### Health Check Endpoint

```python
@app.get("/health")
async def health_check():
    try:
        # Test Supabase connection
        supabase.table('air_quality_measurements').select('id').limit(1).execute()
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }, 503
```

## Tests

### Tests unitaires

```bash
# backend/tests/test_services.py
pytest backend/tests/ -v

# Coverage
pytest --cov=app --cov-report=html
```

### Tests d'intégration

```python
# Test Supabase connection
def test_supabase_insert():
    data = {
        "source": "test",
        "city": "paris",
        "pm25": 25.0
    }
    result = supabase.table('air_quality_measurements').insert(data).execute()
    assert result.data[0]['pm25'] == 25.0
```

## Références Techniques

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Supabase Python Client](https://supabase.com/docs/reference/python)
- [Chart.js](https://www.chartjs.org/docs/)
- [Scikit-learn](https://scikit-learn.org/stable/)

---

**Version:** 1.0.0
**Dernière mise à jour:** 18 décembre 2025
**Maintenu par:** Équipe Smart City ESIS-2
