#!/usr/bin/env python3
"""
Train PM2.5 Prediction Model
Trains Random Forest model on historical data
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Add backend directory to path
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.insert(0, backend_path)

# Load environment variables
env_path = Path(__file__).parent.parent / 'backend' / '.env'
load_dotenv(env_path)

from app.ml.trainer import PM25ModelTrainer

# Configuration
CITIES = ['Paris', 'Lyon', 'Marseille']
TRAINING_DAYS = 60  # Use all backfilled data

# Environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')


async def train_models():
    """Train models for all cities."""
    print("="*70)
    print("PM2.5 Prediction Model Training")
    print("="*70)

    # Initialize Supabase
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("[ERROR] SUPABASE_URL and SUPABASE_KEY must be set")
        return 1

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("[OK] Connected to Supabase\n")

    results = {}

    # Train model for each city
    for city in CITIES:
        print(f"\n{'='*70}")
        print(f"Training model for {city}")
        print(f"{'='*70}\n")

        try:
            trainer = PM25ModelTrainer(supabase)

            # Train
            result = await trainer.train(
                city=city,
                days=TRAINING_DAYS,
                n_estimators=100,
                max_depth=20,
                random_state=42
            )

            # Save model
            model_path = trainer.save_model(city)

            results[city] = {
                'success': True,
                'metrics': result['metrics'],
                'model_path': model_path
            }

        except Exception as e:
            print(f"\n[ERROR] Failed to train model for {city}: {e}")
            results[city] = {
                'success': False,
                'error': str(e)
            }

    # Summary
    print("\n" + "="*70)
    print("TRAINING SUMMARY")
    print("="*70)

    for city, result in results.items():
        if result['success']:
            metrics = result['metrics']
            print(f"\n{city}:")
            print(f"  Status: SUCCESS")
            print(f"  R2 Score: {metrics['r2']:.4f}")
            print(f"  MAE: {metrics['mae']:.2f} ug/m3")
            print(f"  MAPE: {metrics['mape']:.2f}%")
            print(f"  Model: {result['model_path']}")
        else:
            print(f"\n{city}:")
            print(f"  Status: FAILED")
            print(f"  Error: {result['error']}")

    print("\n" + "="*70)

    # Check if all succeeded
    all_success = all(r['success'] for r in results.values())

    if all_success:
        print("\n[OK] All models trained successfully!")
        print("Ready to make predictions via /api/v1/predictions/pm25")
        return 0
    else:
        print("\n[WARNING] Some models failed to train")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(train_models())
    sys.exit(exit_code)
