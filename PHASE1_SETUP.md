# Phase 1 MVP - Setup Guide

Complete setup instructions for running the Smart City Phase 1 MVP (Sprint 1).

## Prerequisites

- **Python 3.11+** installed
- **Node.js 18+** and npm installed
- **Supabase account** (free tier)
- **API Keys:**
  - OpenWeatherMap API key (free tier)
  - AQICN API token (free tier)

---

## Part 1: Database Setup (Supabase)

### 1.1 Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Create a new project
3. Choose a database password (save it securely)
4. Wait for the project to be ready (~2 minutes)

### 1.2 Get Your Credentials

1. In your Supabase project dashboard, go to **Settings** → **API**
2. Copy these values:
   - **Project URL** (e.g., `https://vnznhsbjqxufvhasotid.supabase.co`)
   - **anon/public key**
   - **service_role key** (keep this secret!)

### 1.3 Run Database Schema

1. In Supabase dashboard, go to **SQL Editor**
2. Click **New Query**
3. Copy the entire content of `backend/database/schema.sql`
4. Paste it into the SQL editor
5. Click **Run** (or press Ctrl+Enter)
6. Verify success: You should see 5 new tables in the **Database** → **Tables** section

---

## Part 2: Backend Setup

### 2.1 Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2.2 Configure Environment Variables

1. Copy the example file:
```bash
cp .env.example .env
```

2. Edit `.env` and fill in your actual values:
```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key_here
SUPABASE_SERVICE_KEY=your_service_role_key_here

# External APIs
OPENWEATHER_API_KEY=your_openweather_api_key
AQICN_API_TOKEN=your_aqicn_token

# Security
SECRET_KEY=your_super_secret_key_min_32_chars_generate_with_openssl

# Environment
ENVIRONMENT=development
DEBUG=True

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

**Get API Keys:**
- **OpenWeatherMap:** https://openweathermap.org/api
- **AQICN:** https://aqicn.org/data-platform/token/

**Generate SECRET_KEY:**
```bash
openssl rand -hex 32
```

### 2.3 Test Backend

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Test the API:
- Open http://localhost:8000/docs
- You should see the Swagger UI with all endpoints
- Try the `/health` endpoint (should return `{"status": "ok"}`)

---

## Part 3: Frontend Setup

### 3.1 Install Dependencies

```bash
cd frontend
npm install
```

### 3.2 Configure Environment Variables

1. Copy the example file:
```bash
cp .env.example .env
```

2. Edit `.env`:
```bash
VITE_API_URL=http://localhost:8000
```

### 3.3 Start Development Server

```bash
npm run dev
```

Expected output:
```
  VITE v5.0.11  ready in 543 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

Open http://localhost:5173 in your browser.

---

## Part 4: IoT Sensor Simulation (Optional)

The IoT sensors simulate realistic air quality data and send it to your backend.

### 4.1 Start Sensors

In a new terminal:
```bash
cd backend
python -m app.simulators.iot_sensor
```

Expected output:
```
======================================================================
🌐 Smart City - IoT Sensor Simulator
======================================================================
📊 Number of sensors: 3
⏱️  Measurement interval: 15 minutes (900s)
🎯 Backend API: http://localhost:8000/api/v1/air-quality/measurements
======================================================================

🚀 [sensor_001] Starting sensor at {'lat': 48.8566, 'lon': 2.3522, 'name': 'Paris Centre'}
🚀 [sensor_002] Starting sensor at {'lat': 48.8738, 'lon': 2.2950, 'name': 'Paris Nord'}
🚀 [sensor_003] Starting sensor at {'lat': 48.8414, 'lon': 2.3209, 'name': 'Paris Sud'}

✨ All sensors started. Press Ctrl+C to stop.

✅ [sensor_001] PM2.5=25.3, PM10=38.2 | Total sent: 1
✅ [sensor_002] PM2.5=18.7, PM10=29.4 | Total sent: 1
✅ [sensor_003] PM2.5=31.2, PM10=47.8 | Total sent: 1
```

**Note:** By default, sensors send data every 60 seconds for testing. To change to production mode (15 minutes):
- Edit `backend/app/simulators/iot_sensor.py` line 157
- Change `args=(sensor_config, 60)` to `args=(sensor_config, 900)`

---

## Part 5: Verify Everything Works

### 5.1 Check Data Flow

1. **Backend Running:** http://localhost:8000/docs
2. **Frontend Running:** http://localhost:5173
3. **Sensors Running:** Should see console output with ✅ checkmarks

### 5.2 Test Dashboard

Open http://localhost:5173 and verify:
- ✅ Dashboard loads without errors
- ✅ 3 KPI cards display (PM2.5, PM10, NO2)
- ✅ Chart shows air quality trends
- ✅ Data refreshes automatically

### 5.3 Check Database

In Supabase dashboard:
1. Go to **Database** → **Tables** → **air_quality_measurements**
2. Click **View Data**
3. You should see rows from your sensors (source: `sensor_001`, `sensor_002`, `sensor_003`)

---

## Part 6: Development Workflow

### Start All Services

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 - Sensors (optional):**
```bash
cd backend
python -m app.simulators.iot_sensor
```

### Stop Services

- Press `Ctrl+C` in each terminal to stop services

---

## Troubleshooting

### Backend Issues

**Error: "Module not found"**
```bash
# Make sure you're in the backend directory
cd backend
pip install -r requirements.txt
```

**Error: "Supabase connection failed"**
- Check your `.env` file has correct `SUPABASE_URL` and `SUPABASE_KEY`
- Verify your Supabase project is running (check dashboard)
- Test connection: `curl https://your-project.supabase.co`

**Error: "Invalid API key"**
- Verify your OpenWeatherMap and AQICN API keys are active
- Check rate limits (free tiers have limits)

### Frontend Issues

**Error: "Failed to fetch"**
- Check backend is running on http://localhost:8000
- Verify `VITE_API_URL` in frontend `.env` is correct
- Check browser console for CORS errors

**Blank screen or loading forever**
- Open browser DevTools (F12)
- Check Console tab for JavaScript errors
- Check Network tab to see if API calls are failing

### Sensor Issues

**Error: "Connection refused"**
- Backend must be running first
- Check `api_url` in `iot_sensor.py` matches your backend URL

**No data in database**
- Check sensor console for ✅ success messages
- If you see ❌ errors, check backend logs
- Verify RLS policies in Supabase allow inserts

---

## Architecture Overview

```
┌─────────────────┐
│   Frontend      │
│  React + Vite   │──┐
│  localhost:5173 │  │
└─────────────────┘  │
                     │ HTTP
┌─────────────────┐  │
│  IoT Sensors    │  │
│  (3 simulators) │──┤
└─────────────────┘  │
                     ↓
              ┌─────────────┐
              │   Backend   │
              │   FastAPI   │
              │ localhost:  │
              │    8000     │
              └──────┬──────┘
                     │
                     ↓
              ┌─────────────┐
              │  Supabase   │
              │ PostgreSQL  │
              └─────────────┘
```

---

## Next Steps

Once Phase 1 is running:

1. **Let sensors collect data** for a few hours/days
2. **Verify dashboard displays real-time updates**
3. **Test authentication** (login/logout)
4. **Move to Phase 2:** ML predictions, advanced features

---

## Support

**Documentation:**
- Technical specs: `docs/TECHNICAL.md`
- Functional requirements: `docs/fonctionnel.md`

**External APIs:**
- FastAPI docs: https://fastapi.tiangolo.com
- Supabase docs: https://supabase.com/docs
- TanStack Query: https://tanstack.com/query/latest

**Issues?**
- Check Supabase logs: Dashboard → Logs
- Check browser console (F12)
- Check backend terminal for errors

---

**Phase 1 MVP Checklist:**
- ✅ Database schema deployed
- ✅ Backend API running
- ✅ Frontend dashboard displaying
- ✅ 3 IoT sensors sending data
- ✅ Authentication configured
- ✅ Real-time data updates working

**Congratulations! Your Smart City Phase 1 MVP is live! 🎉**
