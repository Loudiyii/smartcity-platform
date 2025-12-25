# Skill: IoT Simulation (Virtual Sensors)

## Purpose
Simulate IoT air quality sensors to generate realistic time-series data for testing and development without requiring physical hardware.

## When to Use
- Testing data ingestion pipelines
- Developing real-time monitoring features
- Demonstrating the platform without physical sensors
- Load testing the backend API
- Generating training data for ML models

## Overview

Simulate 3 virtual IoT sensors that:
- Measure PM2.5, PM10, temperature, and humidity
- Send data every 15 minutes
- POST data to backend API
- Generate realistic values with variations
- Simulate occasional anomalies

## Simulator Architecture

```
backend/app/simulators/
├── iot_sensor.py          # Main sensor simulator
├── sensor_config.json     # Sensor configurations
└── run_simulation.py      # Entry point script
```

## Core Implementation

### 1. Sensor Simulator Class

```python
# backend/app/simulators/iot_sensor.py
import random
import time
import requests
from datetime import datetime
from typing import Dict
import numpy as np

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
        self.base_temp = 20.0
        self.base_humidity = 60.0

    def generate_pm25(self) -> float:
        """
        Generate realistic PM2.5 value with:
        - Daily cycle (lower at night, higher during rush hours)
        - Random variation
        - Occasional spikes
        """
        hour = datetime.now().hour

        # Daily pattern (rush hours effect)
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            rush_hour_factor = 1.3
        elif 22 <= hour or hour <= 6:
            night_factor = 0.7
        else:
            rush_hour_factor = 1.0
            night_factor = 1.0

        daily_factor = rush_hour_factor if 7 <= hour <= 19 else night_factor

        # Random variation (±20%)
        noise = random.gauss(0, 0.1)

        # Occasional spike (5% chance)
        spike = random.uniform(1.5, 2.0) if random.random() < 0.05 else 1.0

        pm25 = self.base_pm25 * daily_factor * (1 + noise) * spike

        # Ensure non-negative and add slight drift
        self.base_pm25 += random.gauss(0, 0.5)
        self.base_pm25 = max(5, min(100, self.base_pm25))

        return max(0, round(pm25, 2))

    def generate_pm10(self, pm25: float) -> float:
        """PM10 is typically 1.2-2x PM2.5."""
        ratio = random.uniform(1.2, 2.0)
        pm10 = pm25 * ratio
        return round(pm10, 2)

    def generate_temperature(self) -> float:
        """Generate realistic temperature (°C) with daily cycle."""
        hour = datetime.now().hour

        # Daily temperature variation
        if 6 <= hour <= 14:
            temp_variation = random.uniform(2, 5)  # Warmer during day
        else:
            temp_variation = random.uniform(-3, 0)  # Cooler at night

        temp = self.base_temp + temp_variation + random.gauss(0, 1)
        return round(temp, 1)

    def generate_humidity(self) -> int:
        """Generate realistic humidity (%)."""
        humidity = self.base_humidity + random.gauss(0, 10)
        humidity = max(30, min(95, humidity))  # Clamp to realistic range
        return int(humidity)

    def generate_measurement(self) -> Dict:
        """Generate a complete sensor measurement."""
        pm25 = self.generate_pm25()
        pm10 = self.generate_pm10(pm25)
        temperature = self.generate_temperature()
        humidity = self.generate_humidity()

        return {
            "source": self.sensor_id,
            "location": self.location,
            "pm25": pm25,
            "pm10": pm10,
            "no2": round(random.uniform(10, 40), 2),  # Simplified
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
            print(f"[{self.sensor_id}] Sent: PM2.5={measurement['pm25']}, PM10={measurement['pm10']}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"[{self.sensor_id}] Error sending data: {e}")
            return False

    def run(self, interval_seconds: int = 900):
        """
        Run sensor in continuous mode.

        Args:
            interval_seconds: Time between measurements (default: 900 = 15 minutes)
        """
        print(f"[{self.sensor_id}] Starting sensor at {self.location}")

        while True:
            measurement = self.generate_measurement()
            self.send_measurement(measurement)
            time.sleep(interval_seconds)
```

### 2. Multi-Sensor Simulation

```python
# backend/app/simulators/run_simulation.py
import json
import threading
from iot_sensor import IoTSensor

# Sensor configurations
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
        location=config["location"],
        api_url="http://localhost:8000/api/v1/air-quality/measurements"
    )
    sensor.run(interval_seconds=interval)

def main():
    """Start all sensors in parallel threads."""
    print("Starting IoT sensor simulation...")
    print(f"Number of sensors: {len(SENSORS)}")
    print("Measurement interval: 15 minutes")

    threads = []
    for sensor_config in SENSORS:
        thread = threading.Thread(
            target=run_sensor,
            args=(sensor_config, 900),  # 15 minutes
            daemon=True
        )
        thread.start()
        threads.append(thread)

    print("All sensors started. Press Ctrl+C to stop.")

    # Keep main thread alive
    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print("\nStopping simulation...")

if __name__ == "__main__":
    main()
```

### 3. Advanced Features

#### Seasonal Variations

```python
def get_seasonal_factor() -> float:
    """Adjust base pollution levels by season."""
    month = datetime.now().month

    # Winter: higher pollution (heating)
    if month in [12, 1, 2]:
        return 1.3
    # Spring/Fall: moderate
    elif month in [3, 4, 5, 9, 10, 11]:
        return 1.0
    # Summer: lower pollution
    else:
        return 0.8
```

#### Weather-Correlated Data

```python
def correlate_with_weather(pm25: float, wind_speed: float, humidity: int) -> float:
    """
    Adjust PM2.5 based on weather conditions.

    - High wind disperses pollutants (lower PM2.5)
    - High humidity can trap pollutants (higher PM2.5)
    """
    wind_factor = 1.0 - (wind_speed / 20.0)  # 0-20 m/s wind
    humidity_factor = 1.0 + ((humidity - 50) / 200.0)  # 50% baseline

    adjusted_pm25 = pm25 * wind_factor * humidity_factor
    return max(0, adjusted_pm25)
```

#### Anomaly Injection

```python
def inject_anomaly(self, probability: float = 0.01) -> bool:
    """
    Randomly inject sensor malfunction or extreme event.

    Returns True if anomaly injected.
    """
    if random.random() < probability:
        anomaly_type = random.choice(['spike', 'dropout', 'stuck'])

        if anomaly_type == 'spike':
            self.base_pm25 *= random.uniform(3, 5)  # Extreme spike
        elif anomaly_type == 'dropout':
            return False  # Skip sending measurement
        elif anomaly_type == 'stuck':
            self.base_pm25 = self.base_pm25  # Stuck value (no variation)

        print(f"[{self.sensor_id}] Anomaly injected: {anomaly_type}")
        return True

    return False
```

### 4. Batch Historical Data Generation

```python
# Generate historical data for ML training
def generate_historical_data(
    sensor_id: str,
    start_date: datetime,
    end_date: datetime,
    interval_minutes: int = 60
) -> list:
    """
    Generate historical sensor data for a date range.

    Useful for creating training datasets for ML models.
    """
    sensor = IoTSensor(sensor_id, {"lat": 48.856, "lon": 2.352, "name": "Paris"})
    measurements = []

    current = start_date
    while current <= end_date:
        measurement = sensor.generate_measurement()
        measurement['timestamp'] = current.isoformat()
        measurements.append(measurement)

        current += timedelta(minutes=interval_minutes)

    return measurements

# Usage
from datetime import datetime, timedelta

historical = generate_historical_data(
    sensor_id="sensor_001",
    start_date=datetime(2024, 6, 1),
    end_date=datetime(2024, 12, 1),
    interval_minutes=60
)

# Save to CSV
import pandas as pd
df = pd.DataFrame(historical)
df.to_csv('historical_sensor_data.csv', index=False)
```

## Running the Simulation

### Development Mode (Fast Testing)

```bash
# Run with 1-minute intervals for testing
python backend/app/simulators/run_simulation.py --interval 60
```

### Production Mode (Realistic)

```bash
# Run with 15-minute intervals
python backend/app/simulators/run_simulation.py --interval 900
```

### Docker Compose Integration

```yaml
# docker-compose.yml
services:
  iot-simulator:
    build: ./backend
    command: python app/simulators/run_simulation.py
    environment:
      - API_URL=http://backend:8000/api/v1/air-quality/measurements
    depends_on:
      - backend
```

## MQTT Alternative (Advanced)

For more realistic IoT simulation, use MQTT protocol:

```python
import paho.mqtt.client as mqtt
import json

class MQTTSensor(IoTSensor):
    """Sensor that publishes to MQTT broker."""

    def __init__(self, sensor_id: str, location: dict, mqtt_broker: str = "localhost"):
        super().__init__(sensor_id, location)
        self.client = mqtt.Client()
        self.client.connect(mqtt_broker, 1883, 60)

    def send_measurement(self, measurement: dict) -> bool:
        topic = f"smartcity/sensors/{self.sensor_id}/measurements"
        payload = json.dumps(measurement)

        result = self.client.publish(topic, payload, qos=1)
        return result.rc == mqtt.MQTT_ERR_SUCCESS
```

## Best Practices

### Realistic Data Generation
- Use statistical distributions (Gaussian, Poisson)
- Implement daily and seasonal patterns
- Correlate with weather conditions
- Add occasional anomalies (5-10% of data)

### Performance
- Use threading for multiple sensors
- Batch insertions for historical data
- Implement retry logic with exponential backoff
- Monitor memory usage for long-running simulations

### Testing
- Start with fast intervals (1 min) during development
- Use realistic intervals (15 min) for demos
- Validate data ranges before sending
- Log all errors and retry attempts

### Configuration
- Externalize sensor configs to JSON
- Make API URL configurable
- Support different intervals per sensor
- Allow enabling/disabling specific sensors

## Common Tasks

### Adding a New Sensor
```python
# Add to SENSORS list
SENSORS.append({
    "sensor_id": "sensor_004",
    "location": {"lat": 48.8, "lon": 2.4, "name": "Paris Est"}
})
```

### Simulating Sensor Failure
```python
def simulate_failure(duration_seconds: int):
    """Stop sending data for specified duration."""
    print(f"Sensor offline for {duration_seconds}s")
    time.sleep(duration_seconds)
    print("Sensor back online")
```

### Monitoring Sensor Health
```python
def check_sensor_health(self) -> dict:
    """Return sensor health metrics."""
    return {
        "sensor_id": self.sensor_id,
        "last_measurement": datetime.utcnow().isoformat(),
        "measurements_sent": self.sent_count,
        "errors": self.error_count,
        "uptime_hours": (datetime.utcnow() - self.start_time).total_seconds() / 3600
    }
```

## References
- IoT Simulation Patterns: https://aws.amazon.com/blogs/iot/
- MQTT Protocol: https://mqtt.org/
- Paho MQTT Python: https://www.eclipse.org/paho/

## Trade-offs

**HTTP POST vs. MQTT:**
- HTTP: Simpler, stateless, easier to debug
- MQTT: More realistic, better for scale, requires broker

**Realism vs. Simplicity:**
- High realism: Complex models, weather correlation
- Simplicity: Random values, easier to implement

**Intervals:**
- Short (1 min): Fast testing, high data volume
- Long (15 min): Realistic, less storage
