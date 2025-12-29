"""
Script to initialize sensor metadata in Supabase
Run this once to register the 3 IoT sensors with their GPS locations
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import get_supabase_client
from datetime import datetime


SENSORS = [
    {
        "sensor_id": "SENSOR_001",
        "name": "Paris Centre - Air Quality Monitor",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "location_description": "Paris Centre, near Notre-Dame",
        "sensor_type": "air_quality",
        "status": "active"
    },
    {
        "sensor_id": "SENSOR_002",
        "name": "Paris Nord - Air Quality Monitor",
        "latitude": 48.8738,
        "longitude": 2.2950,
        "location_description": "Paris Nord, near Gare du Nord",
        "sensor_type": "air_quality",
        "status": "active"
    },
    {
        "sensor_id": "SENSOR_003",
        "name": "Paris Sud - Air Quality Monitor",
        "latitude": 48.8414,
        "longitude": 2.3209,
        "location_description": "Paris Sud, near Place d'Italie",
        "sensor_type": "air_quality",
        "status": "active"
    },
    {
        "sensor_id": "SENSOR_004",
        "name": "Paris Est - Air Quality Monitor",
        "latitude": 48.8467,
        "longitude": 2.3775,
        "location_description": "Paris Est, near Gare de Lyon",
        "sensor_type": "air_quality",
        "status": "active"
    },
    {
        "sensor_id": "SENSOR_005",
        "name": "Paris Ouest - Air Quality Monitor",
        "latitude": 48.8656,
        "longitude": 2.2879,
        "location_description": "Paris Ouest, near Arc de Triomphe",
        "sensor_type": "air_quality",
        "status": "active"
    }
]


def init_sensor_metadata():
    """Insert sensor metadata into Supabase."""
    supabase = get_supabase_client()

    print("=" * 70)
    print("🌐 Smart City - Sensor Metadata Initialization")
    print("=" * 70)
    print(f"📊 Registering {len(SENSORS)} sensors in Supabase...")
    print()

    success_count = 0
    error_count = 0

    for sensor in SENSORS:
        try:
            # Check if sensor already exists
            existing = supabase.table('sensor_metadata')\
                .select('sensor_id')\
                .eq('sensor_id', sensor['sensor_id'])\
                .execute()

            if existing.data:
                print(f"⚠️  {sensor['sensor_id']}: Already exists, skipping...")
                continue

            # Insert sensor metadata
            result = supabase.table('sensor_metadata').insert({
                'sensor_id': sensor['sensor_id'],
                'name': sensor['name'],
                'latitude': sensor['latitude'],
                'longitude': sensor['longitude'],
                'location_description': sensor['location_description'],
                'sensor_type': sensor['sensor_type'],
                'status': sensor['status'],
                'installed_at': datetime.utcnow().isoformat()
            }).execute()

            print(f"✅ {sensor['sensor_id']}: Registered at ({sensor['latitude']}, {sensor['longitude']})")
            success_count += 1

        except Exception as e:
            print(f"❌ {sensor['sensor_id']}: Error - {e}")
            error_count += 1

    print()
    print("=" * 70)
    print(f"✨ Registration complete!")
    print(f"   ✅ Success: {success_count}")
    print(f"   ⚠️  Skipped: {len(SENSORS) - success_count - error_count}")
    print(f"   ❌ Errors: {error_count}")
    print("=" * 70)

    if success_count > 0:
        print()
        print("📝 Next steps:")
        print("   1. Run the IoT simulator: python -m app.simulators.iot_sensor")
        print("   2. Wait 24 hours for data accumulation")
        print("   3. Test the spatial analysis endpoint")
        print()


if __name__ == "__main__":
    try:
        init_sensor_metadata()
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
