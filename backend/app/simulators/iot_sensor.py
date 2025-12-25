"""
IoT Sensor Simulator - Phase 1 MVP
Simulates 3 air quality sensors sending data every 15 minutes
"""

import random
import time
import requests
from datetime import datetime
from typing import Dict
import asyncio


class IoTSensor:
    """Simulates an air quality IoT sensor."""

    def __init__(
        self,
        sensor_id: str,
        location: Dict[str, float],
        api_url: str = "http://localhost:8000/api/v1/air-quality/measurements"
    ):
        self.sensor_id = sensor_id
        self.location = location
        self.api_url = api_url

        # Base values for realistic variations
        self.base_pm25 = random.uniform(15, 35)
        self.base_pm10 = self.base_pm25 * 1.5
        self.sent_count = 0
        self.error_count = 0

    def generate_pm25(self) -> float:
        """Generate realistic PM2.5 value with daily cycle."""
        hour = datetime.now().hour

        # Rush hour effect
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            factor = 1.3
        elif 22 <= hour or hour <= 6:
            factor = 0.7
        else:
            factor = 1.0

        # Random variation
        noise = random.gauss(0, 0.1)

        # Occasional spike (5% chance)
        spike = random.uniform(1.5, 2.0) if random.random() < 0.05 else 1.0

        pm25 = self.base_pm25 * factor * (1 + noise) * spike

        # Drift
        self.base_pm25 += random.gauss(0, 0.5)
        self.base_pm25 = max(5, min(100, self.base_pm25))

        return max(0, round(pm25, 2))

    def generate_pm10(self, pm25: float) -> float:
        """PM10 is typically 1.2-2x PM2.5."""
        ratio = random.uniform(1.2, 2.0)
        return round(pm25 * ratio, 2)

    def generate_measurement(self) -> Dict:
        """Generate a complete sensor measurement."""
        pm25 = self.generate_pm25()
        pm10 = self.generate_pm10(pm25)

        return {
            "source": self.sensor_id,
            "city": "paris",
            "location": self.location,
            "pm25": pm25,
            "pm10": pm10,
            "no2": round(random.uniform(10, 40), 2),
            "timestamp": datetime.utcnow().isoformat()
        }

    def send_measurement(self, measurement: Dict) -> bool:
        """Send measurement to backend API."""
        try:
            response = requests.post(
                self.api_url,
                json=measurement,
                timeout=10
            )
            response.raise_for_status()
            self.sent_count += 1
            print(f"✅ [{self.sensor_id}] PM2.5={measurement['pm25']}, PM10={measurement['pm10']} | Total sent: {self.sent_count}")
            return True
        except requests.exceptions.RequestException as e:
            self.error_count += 1
            print(f"❌ [{self.sensor_id}] Error: {e}")
            return False

    def run(self, interval_seconds: int = 900):
        """
        Run sensor in continuous mode.

        Args:
            interval_seconds: Time between measurements (default: 900 = 15 min)
        """
        print(f"🚀 [{self.sensor_id}] Starting sensor at {self.location}")
        print(f"📍 Sending data every {interval_seconds}s")

        while True:
            measurement = self.generate_measurement()
            self.send_measurement(measurement)
            time.sleep(interval_seconds)


# ============================================================================
# Multi-Sensor Runner
# ============================================================================

SENSORS = [
    {
        "sensor_id": "sensor_001",
        "location": {"lat": 48.8566, "lon": 2.3522, "name": "Paris Centre"}
    },
    {
        "sensor_id": "sensor_002",
        "location": {"lat": 48.8738, "lon": 2.2950, "name": "Paris Nord"}
    },
    {
        "sensor_id": "sensor_003",
        "location": {"lat": 48.8414, "lon": 2.3209, "name": "Paris Sud"}
    }
]


def run_sensor(config: dict, interval: int = 900):
    """Run a single sensor in a thread."""
    sensor = IoTSensor(
        sensor_id=config["sensor_id"],
        location=config["location"]
    )
    sensor.run(interval_seconds=interval)


def main():
    """Start all sensors in parallel."""
    import threading

    print("=" * 70)
    print("🌐 Smart City - IoT Sensor Simulator")
    print("=" * 70)
    print(f"📊 Number of sensors: {len(SENSORS)}")
    print(f"⏱️  Measurement interval: 15 minutes (900s)")
    print(f"🎯 Backend API: http://localhost:8000/api/v1/air-quality/measurements")
    print("=" * 70)

    threads = []
    for sensor_config in SENSORS:
        thread = threading.Thread(
            target=run_sensor,
            args=(sensor_config, 60),  # 60s for testing, change to 900 for production
            daemon=True
        )
        thread.start()
        threads.append(thread)

    print("\n✨ All sensors started. Press Ctrl+C to stop.\n")

    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping simulation...")
        print("👋 Goodbye!")


if __name__ == "__main__":
    main()
