# Data Collection Scripts

## Overview

Automated scripts to collect air quality and weather data from external APIs and save to Supabase.

## Scripts

### `collect_data.py`

Standalone Python script that:
- Fetches air quality data from AQICN API
- Fetches weather data from WeatherAPI
- Saves all data to Supabase PostgreSQL
- Runs independently (no backend needed)

**Supported cities:** Paris, Lyon, Marseille (configurable)

**Data collected:**
- **Air Quality:** PM2.5, PM10, NO2, O3, SO2, CO, AQI
- **Weather:** Temperature, humidity, pressure, wind speed/direction

## GitHub Actions Automation

The script runs automatically via GitHub Actions:

**Schedule:** Every hour (cron: `0 * * * *`)

**Workflow file:** `.github/workflows/collect-data.yml`

### How it works:

1. GitHub Actions triggers at the top of every hour
2. Spins up an Ubuntu container
3. Installs Python 3.11 + dependencies
4. Runs `collect_data.py` with secrets from GitHub
5. Script fetches data from APIs
6. Script saves data to Supabase
7. Logs success/failure
8. Creates GitHub issue if failure

## Setup Instructions

### 1. Configure GitHub Secrets

Go to: `https://github.com/YOUR_USERNAME/smartcity-platform/settings/secrets/actions`

Add the following secrets:

| Secret Name | Value | How to Get |
|-------------|-------|------------|
| `SUPABASE_URL` | `https://vnznhsbjqxufvhasotid.supabase.co` | Supabase Dashboard → Settings → API |
| `SUPABASE_KEY` | Your anon/public key | Supabase Dashboard → Settings → API |
| `AQICN_API_TOKEN` | Your AQICN token | https://aqicn.org/data-platform/token/ |
| `WEATHERAPI_KEY` | Your WeatherAPI key | https://www.weatherapi.com/signup.aspx |

### 2. Enable GitHub Actions

1. Go to repository Settings → Actions → General
2. Under "Actions permissions", select "Allow all actions and reusable workflows"
3. Save

### 3. Test the Workflow

**Option A: Wait for next hourly run**
- Check at `:00` of next hour
- View logs in Actions tab

**Option B: Trigger manually**
1. Go to Actions tab
2. Click "Collect Air Quality & Weather Data"
3. Click "Run workflow" → "Run workflow"
4. Watch the live logs

## Local Testing

Test the script locally before deployment:

```bash
# Install dependencies
cd scripts
pip install -r requirements.txt

# Set environment variables (Linux/macOS)
export SUPABASE_URL="https://vnznhsbjqxufvhasotid.supabase.co"
export SUPABASE_KEY="your_key_here"
export AQICN_API_TOKEN="your_token_here"
export WEATHERAPI_KEY="your_key_here"

# Or Windows PowerShell
$env:SUPABASE_URL="https://vnznhsbjqxufvhasotid.supabase.co"
$env:SUPABASE_KEY="your_key_here"
# ... etc

# Run the script
python collect_data.py
```

Expected output:
```
======================================================================
🌍 Smart City - Data Collection
📅 2024-12-25 19:00:00 UTC
======================================================================
✅ Supabase client initialized

📍 Processing PARIS...
✅ Saved air quality data for Paris: PM2.5=45.0, AQI=120
✅ Saved weather data for Paris: 12.5°C, 75% humidity

📍 Processing LYON...
✅ Saved air quality data for Lyon: PM2.5=38.0, AQI=105
✅ Saved weather data for Lyon: 10.2°C, 80% humidity

======================================================================
📊 Collection Summary:
   ✅ Successful: 6
   ❌ Errors: 0
   🏙️  Cities processed: 3
======================================================================
```

## Monitoring

### View Logs

1. Go to GitHub Actions tab
2. Click on latest "Collect Air Quality & Weather Data" run
3. Expand "Collect and save data" step

### Check Data in Supabase

```sql
-- Check latest data
SELECT
  source,
  city,
  pm25,
  aqi,
  timestamp
FROM air_quality_measurements
WHERE source = 'AQICN'
ORDER BY timestamp DESC
LIMIT 10;

-- Check collection frequency
SELECT
  DATE_TRUNC('hour', timestamp) as hour,
  COUNT(*) as measurements
FROM air_quality_measurements
WHERE source = 'AQICN'
GROUP BY hour
ORDER BY hour DESC
LIMIT 24;
```

### Failure Notifications

If data collection fails:
- GitHub Actions creates an issue automatically
- Issue labeled: `automated`, `data-collection`, `bug`
- Issue contains link to failed run

## Customization

### Change Collection Frequency

Edit `.github/workflows/collect-data.yml`:

```yaml
schedule:
  - cron: '0 * * * *'     # Every hour (current)
  - cron: '*/30 * * * *'  # Every 30 minutes
  - cron: '0 */3 * * *'   # Every 3 hours
  - cron: '0 0 * * *'     # Once per day at midnight
```

**Note:** GitHub Actions has a minimum interval of 5 minutes.

### Add More Cities

Edit `scripts/collect_data.py`:

```python
CITIES = ['paris', 'lyon', 'marseille', 'toulouse', 'nice']
```

### Change Data Sources

Modify functions in `collect_data.py`:
- `fetch_aqicn_data()` - Air quality source
- `fetch_weather_data()` - Weather source

## Cost & Limits

### GitHub Actions (Free Tier)
- **2000 minutes/month** for private repos
- **Unlimited** for public repos
- Each run takes ~30-60 seconds
- **Monthly usage:** ~720 minutes (hourly runs)
- **Well within free tier** ✅

### API Limits
- **AQICN:** 1000 requests/day (free tier)
- **WeatherAPI:** 1 million calls/month (free tier)
- **Current usage:** 72 requests/day (well within limits) ✅

## Troubleshooting

### "Repository secret not found"
- Ensure secrets are added in GitHub Settings → Secrets → Actions
- Secret names must match exactly (case-sensitive)

### "Import error: No module named 'supabase'"
- Check `scripts/requirements.txt` is present
- Verify workflow runs `pip install -r scripts/requirements.txt`

### "Failed to save data"
- Check Supabase is online
- Verify `SUPABASE_KEY` has write permissions
- Check Row Level Security (RLS) policies allow inserts

### "API rate limit exceeded"
- Reduce collection frequency
- Add fewer cities
- Upgrade API plan

## Architecture

```
┌─────────────────────────────────────────┐
│   GitHub Actions (Runs every hour)     │
│                                         │
│  1. Checkout code                       │
│  2. Install Python + dependencies       │
│  3. Run collect_data.py                 │
│                                         │
│     ┌─────────────────────┐             │
│     │  collect_data.py    │             │
│     │  ├─ fetch AQICN     │────┐        │
│     │  ├─ fetch Weather   │────┤        │
│     │  └─ save Supabase   │────┘        │
│     └─────────────────────┘             │
└─────────────────────────────────────────┘
                  │
                  ↓
         ┌────────────────┐      ┌──────────────┐
         │  AQICN API     │      │ WeatherAPI   │
         │  (Air Quality) │      │ (Météo)      │
         └────────────────┘      └──────────────┘
                  │                     │
                  └──────────┬──────────┘
                             ↓
                    ┌─────────────────┐
                    │    Supabase     │
                    │  (PostgreSQL)   │
                    │                 │
                    │  • air_quality  │
                    │  • weather_data │
                    └─────────────────┘
```

## Benefits

✅ **No server required** - Runs on GitHub's infrastructure
✅ **100% serverless** - No backend needed
✅ **Free** - Within GitHub Actions free tier
✅ **Reliable** - GitHub's uptime > 99.9%
✅ **Automated** - Set and forget
✅ **Logged** - Full audit trail
✅ **Notifications** - Auto-creates issues on failure
✅ **Scalable** - Easy to add cities/data sources

---

**Last Updated:** 2024-12-25
**Status:** ✅ Active
**Next Run:** Check GitHub Actions tab
