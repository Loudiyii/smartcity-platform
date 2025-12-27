"""
Simple script to train ML models for all cities
"""
import asyncio
import sys
from pathlib import Path

# Add app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.ml.trainer import PM25ModelTrainer
from app.config import get_supabase_client

async def train_all_models():
    """Train models for all cities."""
    cities = ['Paris', 'Lyon', 'Marseille']
    supabase = get_supabase_client()

    for city in cities:
        print(f"\n{'='*60}")
        print(f"Training model for {city}")
        print('='*60)

        try:
            trainer = PM25ModelTrainer(supabase)

            # Train model
            result = await trainer.train(
                city=city,
                days=60,
                n_estimators=100,
                max_depth=20
            )

            # Save model
            model_path = trainer.save_model(city)

            print(f"\n[SUCCESS] {city} model training complete!")
            print(f"   Model saved to: {model_path}")
            print(f"   R2 Score: {result['metrics']['r2']:.4f}")
            print(f"   MAPE: {result['metrics']['mape']:.2f}%")
            print(f"   RMSE: {result['metrics']['rmse']:.2f}")
            print(f"   Training samples: {result['metrics']['training_samples']}")

        except Exception as e:
            print(f"\n[ERROR] Error training {city} model: {e}")
            continue

    print(f"\n{'='*60}")
    print("Training complete for all cities!")
    print('='*60)

if __name__ == "__main__":
    asyncio.run(train_all_models())
