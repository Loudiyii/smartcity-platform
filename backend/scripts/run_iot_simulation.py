"""
IoT Sensor Simulator - Production Ready
Sends sensor data to Railway production API
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.simulators.iot_sensor import IoTSensor
import threading
import time


# Production API URL (Railway)
API_URL = "https://smartcity-platform-production.up.railway.app/api/v1/air-quality/measurements"

# Sensor configurations - matching sensor_metadata
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


def run_sensor(config: dict, interval: int = 900):
    """Run a single sensor in a thread."""
    sensor = IoTSensor(
        sensor_id=config["sensor_id"],
        location=config["location"],
        api_url=API_URL
    )
    sensor.run(interval_seconds=interval)


def main():
    """Start all sensors in parallel."""
    print("=" * 70)
    print("🌐 Smart City - IoT Sensor Simulator (Production)")
    print("=" * 70)
    print(f"📊 Number of sensors: {len(SENSORS)}")
    print(f"⏱️  Measurement interval: 15 minutes (900s)")
    print(f"🎯 Backend API: {API_URL}")
    print("=" * 70)
    print()

    # Ask for confirmation
    response = input("⚠️  This will send data to PRODUCTION. Continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("❌ Aborted by user")
        return

    print()
    print("🚀 Starting sensors...")
    print()

    threads = []
    for sensor_config in SENSORS:
        thread = threading.Thread(
            target=run_sensor,
            args=(sensor_config, 900),  # 900s = 15 minutes
            daemon=True
        )
        thread.start()
        threads.append(thread)
        time.sleep(1)  # Stagger sensor starts

    print()
    print("✨ All sensors started. Press Ctrl+C to stop.")
    print("📊 Sensors will send data every 15 minutes")
    print()

    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping simulation...")
        print("👋 Goodbye!")


if __name__ == "__main__":
    main()
