#!/usr/bin/env python3
"""
Backfill Historical Data Script
Generates 60 days of realistic historical air quality and weather data for Paris
Uses pattern-based synthetic data generation to populate the database for ML training
"""

import os
import sys
from datetime import datetime, timedelta
import random
import numpy as np
from supabase import create_client
from dotenv import load_dotenv
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from backend/.env
env_path = Path(__file__).parent.parent / 'backend' / '.env'
load_dotenv(env_path)

# Configuration
DAYS_TO_BACKFILL = 60
CITIES = ['Paris', 'Lyon', 'Marseille']

# Realistic pollution patterns for Paris
# Based on seasonal and day-of-week variations
PM25_BASE = {
    'winter': 35,  # Higher in winter (heating)
    'spring': 25,
    'summer': 20,  # Lower in summer
    'fall': 30
}

# Environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')


def get_season(date):
    """Get season from date."""
    month = date.month
    if month in [12, 1, 2]:
        return 'winter'
    elif month in [3, 4, 5]:
        return 'spring'
    elif month in [6, 7, 8]:
        return 'summer'
    else:
        return 'fall'


def generate_pm25_value(timestamp, city):
    """Generate realistic PM2.5 value based on patterns."""
    season = get_season(timestamp)
    base = PM25_BASE[season]

    # Add day-of-week variation (weekdays higher due to traffic)
    if timestamp.weekday() < 5:  # Weekday
        base *= 1.15
    else:  # Weekend
        base *= 0.85

    # Add hourly variation (rush hours higher)
    hour = timestamp.hour
    if hour in [7, 8, 9, 17, 18, 19]:  # Rush hours
        base *= 1.3
    elif hour in [0, 1, 2, 3, 4, 5]:  # Night
        base *= 0.7

    # Add random variation (±30%)
    variation = random.uniform(-0.3, 0.3)
    value = base * (1 + variation)

    # City-specific adjustment
    if city == 'Lyon':
        value *= 0.9
    elif city == 'Marseille':
        value *= 0.85

    # Ensure positive and add noise
    return max(5, value + np.random.normal(0, 3))


def generate_weather_data(timestamp, city):
    """Generate realistic weather data."""
    season = get_season(timestamp)
    hour = timestamp.hour

    # Temperature (°C)
    temp_base = {
        'winter': 5,
        'spring': 15,
        'summer': 25,
        'fall': 12
    }[season]

    # Daily variation
    if 6 <= hour <= 18:  # Day
        temp = temp_base + (hour - 12) * 0.5 + random.uniform(-3, 3)
    else:  # Night
        temp = temp_base - 5 + random.uniform(-2, 2)

    # Humidity (%)
    humidity = int(65 + random.uniform(-15, 15))
    humidity = max(30, min(95, humidity))

    # Pressure (hPa)
    pressure = int(1013 + random.uniform(-20, 20))

    # Wind speed (km/h)
    wind_speed = max(0, random.uniform(5, 25))

    # Wind direction (degrees)
    wind_direction = random.randint(0, 359)

    return {
        'temperature': round(temp, 1),
        'humidity': humidity,
        'pressure': pressure,
        'wind_speed': round(wind_speed, 1),
        'wind_direction': wind_direction
    }


def generate_air_quality_data(timestamp, city):
    """Generate air quality measurement."""
    pm25 = generate_pm25_value(timestamp, city)

    # Correlate other pollutants with PM2.5
    pm10 = pm25 * random.uniform(1.3, 1.8)
    no2 = pm25 * random.uniform(0.4, 0.7)
    o3 = max(0, 50 - pm25 * 0.3 + random.uniform(-10, 10))  # Inverse correlation
    so2 = pm25 * random.uniform(0.1, 0.3)
    co = pm25 * random.uniform(0.3, 0.6)

    # Calculate AQI (simplified US EPA formula)
    aqi = int(pm25 * 3.5)  # Rough approximation

    return {
        'source': 'HISTORICAL_BACKFILL',
        'city': city,
        'aqi': aqi,
        'pm25': round(pm25, 1),
        'pm10': round(pm10, 1),
        'no2': round(no2, 1),
        'o3': round(o3, 1),
        'so2': round(so2, 1),
        'co': round(co, 1),
        'timestamp': timestamp.isoformat()
    }


def backfill_data():
    """Main backfill function."""
    print("="*70)
    print("Historical Data Backfill")
    print(f"Generating {DAYS_TO_BACKFILL} days of data")
    print("="*70)

    # Initialize Supabase
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("[ERROR] SUPABASE_URL and SUPABASE_KEY must be set")
        return

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("[OK] Connected to Supabase")

    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=DAYS_TO_BACKFILL)

    print(f"\nDate range: {start_date.date()} to {end_date.date()}")
    print(f"Cities: {', '.join(CITIES)}")

    total_records = 0
    errors = 0

    # Generate data for each city
    for city in CITIES:
        print(f"\nProcessing {city}...")
        city_records = 0

        # Generate hourly data
        current_time = start_date
        batch_air_quality = []
        batch_weather = []

        while current_time <= end_date:
            # Generate air quality data
            aq_data = generate_air_quality_data(current_time, city)
            batch_air_quality.append(aq_data)

            # Generate weather data
            weather = generate_weather_data(current_time, city)
            weather_data = {
                'city': city,
                'timestamp': current_time.isoformat(),
                **weather
            }
            batch_weather.append(weather_data)

            # Insert in batches of 100
            if len(batch_air_quality) >= 100:
                try:
                    # Insert air quality
                    supabase.table('air_quality_measurements').insert(batch_air_quality).execute()
                    # Insert weather
                    supabase.table('weather_data').insert(batch_weather).execute()

                    city_records += len(batch_air_quality)
                    total_records += len(batch_air_quality)

                    batch_air_quality = []
                    batch_weather = []

                    print(f"  [OK] Inserted {city_records} records for {city}", end='\r')

                except Exception as e:
                    print(f"\n  [ERROR] Error inserting batch: {e}")
                    errors += 1

            current_time += timedelta(hours=1)

        # Insert remaining records
        if batch_air_quality:
            try:
                supabase.table('air_quality_measurements').insert(batch_air_quality).execute()
                supabase.table('weather_data').insert(batch_weather).execute()
                city_records += len(batch_air_quality)
                total_records += len(batch_air_quality)
            except Exception as e:
                print(f"\n  [ERROR] Error inserting final batch: {e}")
                errors += 1

        print(f"  [OK] Completed {city}: {city_records} records")

    # Summary
    print("\n" + "="*70)
    print("Backfill Summary:")
    print(f"   Total records inserted: {total_records}")
    print(f"   Errors: {errors}")
    print(f"   Cities: {len(CITIES)}")
    print(f"   Days: {DAYS_TO_BACKFILL}")
    print(f"   Expected records per city: {DAYS_TO_BACKFILL * 24}")
    print("="*70)

    if errors > 0:
        print("\n[WARNING] Some errors occurred during backfill")
        return 1
    else:
        print("\n[OK] Backfill completed successfully!")
        print("Ready for ML model training")
        return 0


if __name__ == "__main__":
    sys.exit(backfill_data())
