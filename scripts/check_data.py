#!/usr/bin/env python3
"""Check data in Supabase."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
env_path = Path(__file__).parent.parent / 'backend' / '.env'
load_dotenv(env_path)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Check air quality data
print("Checking air_quality_measurements...")
for city in ['Paris', 'Lyon', 'Marseille']:
    response = supabase.table('air_quality_measurements')\
        .select('*', count='exact')\
        .eq('city', city)\
        .limit(1)\
        .execute()

    count = response.count if hasattr(response, 'count') else len(response.data)
    print(f"  {city}: {count} records")

# Try to get all Paris records
print("\nFetching all Paris records...")
response = supabase.table('air_quality_measurements')\
    .select('*')\
    .eq('city', 'Paris')\
    .order('timestamp')\
    .execute()

print(f"Got {len(response.data)} records")
if len(response.data) > 0:
    print(f"First record: {response.data[0]['timestamp']}")
    print(f"Last record: {response.data[-1]['timestamp']}")
