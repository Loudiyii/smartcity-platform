"""
IoT Sensor Simulator Worker - Production
Runs continuously on Railway to generate sensor data
"""

import time
import threading
from datetime import datetime
from app.simulators.iot_sensor import IoTSensor
from app.config import get_supabase_client

# Production API URL
API_URL = "https://smartcity-platform-production.up.railway.app/api/v1/air-quality/measurements"

# 5 sensors across Paris
SENSORS = [
    {
        "sensor_id": "SENSOR_001",
        "location": {"lat": 48.8566, "lon": 2.3522, "name": "Paris Centre"}
    },
    {
        "sensor_id": "SENSOR_002",
        "location": {"lat": 48.8738, "lon": 2.2950, "name": "Paris Nord"}
    },
    {
        "sensor_id": "SENSOR_003",
        "location": {"lat": 48.8414, "lon": 2.3209, "name": "Paris Sud"}
    },
    {
        "sensor_id": "SENSOR_004",
        "location": {"lat": 48.8467, "lon": 2.3775, "name": "Paris Est"}
    },
    {
        "sensor_id": "SENSOR_005",
        "location": {"lat": 48.8656, "lon": 2.2879, "name": "Paris Ouest"}
    }
]


def init_sensor_metadata():
    """Initialize sensor metadata in Supabase on first run."""
    print("🔧 Initializing sensor metadata...")
    supabase = get_supabase_client()

    for sensor in SENSORS:
        try:
            # Check if exists
            existing = supabase.table('sensor_metadata')\
                .select('sensor_id')\
                .eq('sensor_id', sensor['sensor_id'])\
                .execute()

            if existing.data:
                print(f"   ✓ {sensor['sensor_id']}: Already registered")
                continue

            # Insert metadata
            supabase.table('sensor_metadata').insert({
                'sensor_id': sensor['sensor_id'],
                'name': f"{sensor['location']['name']} Air Quality Monitor",
                'latitude': sensor['location']['lat'],
                'longitude': sensor['location']['lon'],
                'location_description': sensor['location']['name'],
                'sensor_type': 'air_quality',
                'status': 'active',
                'installed_at': datetime.utcnow().isoformat()
            }).execute()

            print(f"   ✅ {sensor['sensor_id']}: Registered")

        except Exception as e:
            print(f"   ⚠️ {sensor['sensor_id']}: {e}")


def run_sensor(config: dict, interval: int = 900):
    """Run a single sensor continuously."""
    sensor = IoTSensor(
        sensor_id=config["sensor_id"],
        location=config["location"],
        api_url=API_URL
    )
    sensor.run(interval_seconds=interval)


def main():
    """Main worker process."""
    print("=" * 70)
    print("🌐 Smart City - IoT Sensor Worker (Railway)")
    print("=" * 70)
    print(f"📊 Sensors: {len(SENSORS)}")
    print(f"⏱️  Interval: 15 minutes (900s)")
    print(f"🎯 API: {API_URL}")
    print("=" * 70)
    print()

    # Step 1: Initialize metadata
    init_sensor_metadata()
    print()

    # Step 2: Start sensors
    print("🚀 Starting sensors...")
    threads = []
    for sensor_config in SENSORS:
        thread = threading.Thread(
            target=run_sensor,
            args=(sensor_config, 900),
            daemon=True
        )
        thread.start()
        threads.append(thread)
        time.sleep(2)

    print()
    print("✨ All sensors running!")
    print("📡 Worker will run continuously...")
    print()

    # Keep worker alive
    try:
        while True:
            time.sleep(3600)  # Check every hour
    except KeyboardInterrupt:
        print("\n🛑 Worker stopped")


if __name__ == "__main__":
    main()
