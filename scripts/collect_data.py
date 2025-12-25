#!/usr/bin/env python3
"""
Data Collection Script - Standalone
Fetches air quality and weather data and saves to Supabase
Run via GitHub Actions cron or manually
"""

import os
import sys
import requests
from datetime import datetime
from supabase import create_client, Client
from typing import Optional

# Environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
AQICN_TOKEN = os.getenv('AQICN_API_TOKEN')
WEATHERAPI_KEY = os.getenv('WEATHERAPI_KEY')

# Configuration
CITIES = ['paris', 'lyon', 'marseille']  # Add more cities as needed
AQICN_BASE_URL = 'https://api.waqi.info/feed'


def get_supabase_client() -> Client:
    """Initialize Supabase client."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY environment variables")
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def fetch_aqicn_data(city: str) -> Optional[dict]:
    """Fetch air quality data from AQICN API."""
    try:
        url = f"{AQICN_BASE_URL}/{city}/?token={AQICN_TOKEN}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        if data.get('status') != 'ok':
            print(f"❌ AQICN API error for {city}: {data.get('data', 'Unknown error')}")
            return None

        aqi_data = data.get('data', {})
        iaqi = aqi_data.get('iaqi', {})

        return {
            'source': 'AQICN',
            'city': city.capitalize(),
            'aqi': aqi_data.get('aqi'),
            'pm25': iaqi.get('pm25', {}).get('v'),
            'pm10': iaqi.get('pm10', {}).get('v'),
            'no2': iaqi.get('no2', {}).get('v'),
            'o3': iaqi.get('o3', {}).get('v'),
            'so2': iaqi.get('so2', {}).get('v'),
            'co': iaqi.get('co', {}).get('v'),
            'timestamp': datetime.utcnow().isoformat()
        }

    except Exception as e:
        print(f"❌ Error fetching AQICN data for {city}: {e}")
        return None


def fetch_weather_data(city: str) -> Optional[dict]:
    """Fetch weather data from WeatherAPI."""
    try:
        url = f"http://api.weatherapi.com/v1/current.json?key={WEATHERAPI_KEY}&q={city}&aqi=no"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        current = data.get('current', {})

        return {
            'city': city.capitalize(),
            'temperature': current.get('temp_c'),
            'humidity': current.get('humidity'),
            'pressure': current.get('pressure_mb'),
            'wind_speed': current.get('wind_kph'),
            'wind_direction': current.get('wind_degree'),
            'timestamp': datetime.utcnow().isoformat()
        }

    except Exception as e:
        print(f"❌ Error fetching weather data for {city}: {e}")
        return None


def save_air_quality(client: Client, data: dict) -> bool:
    """Save air quality data to Supabase."""
    try:
        result = client.table('air_quality_measurements').insert(data).execute()
        if result.data:
            print(f"✅ Saved air quality data for {data['city']}: PM2.5={data.get('pm25')}, AQI={data.get('aqi')}")
            return True
        else:
            print(f"❌ Failed to save air quality data for {data['city']}")
            return False
    except Exception as e:
        print(f"❌ Error saving air quality data: {e}")
        return False


def save_weather(client: Client, data: dict) -> bool:
    """Save weather data to Supabase."""
    try:
        result = client.table('weather_data').insert(data).execute()
        if result.data:
            print(f"✅ Saved weather data for {data['city']}: {data['temperature']}°C, {data['humidity']}% humidity")
            return True
        else:
            print(f"❌ Failed to save weather data for {data['city']}")
            return False
    except Exception as e:
        print(f"❌ Error saving weather data: {e}")
        return False


def main():
    """Main collection workflow."""
    print("="*70)
    print(f"🌍 Smart City - Data Collection")
    print(f"📅 {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("="*70)

    # Initialize Supabase client
    try:
        supabase = get_supabase_client()
        print("✅ Supabase client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Supabase: {e}")
        sys.exit(1)

    # Collect data for each city
    success_count = 0
    error_count = 0

    for city in CITIES:
        print(f"\n📍 Processing {city.upper()}...")

        # Fetch and save air quality
        if AQICN_TOKEN:
            air_quality = fetch_aqicn_data(city)
            if air_quality:
                if save_air_quality(supabase, air_quality):
                    success_count += 1
                else:
                    error_count += 1
            else:
                error_count += 1
        else:
            print("⚠️  AQICN_TOKEN not set, skipping air quality")

        # Fetch and save weather
        if WEATHERAPI_KEY:
            weather = fetch_weather_data(city)
            if weather:
                if save_weather(supabase, weather):
                    success_count += 1
                else:
                    error_count += 1
            else:
                error_count += 1
        else:
            print("⚠️  WEATHERAPI_KEY not set, skipping weather")

    # Summary
    print("\n" + "="*70)
    print(f"📊 Collection Summary:")
    print(f"   ✅ Successful: {success_count}")
    print(f"   ❌ Errors: {error_count}")
    print(f"   🏙️  Cities processed: {len(CITIES)}")
    print("="*70)

    # Exit with appropriate code
    if error_count > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
