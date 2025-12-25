"""
Model Training for PM2.5 Prediction
Trains Random Forest Regressor for J+1 air quality forecasting
"""

import os
import pickle
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from supabase import Client

from app.ml.feature_engineering import FeatureEngineer


class PM25ModelTrainer:
    """Trains and evaluates Random Forest model for PM2.5 prediction."""

    def __init__(
        self,
        supabase_client: Client,
        model_dir: str = "app/ml/models"
    ):
        """
        Initialize trainer.

        Args:
            supabase_client: Supabase client
            model_dir: Directory to save trained models
        """
        self.supabase = supabase_client
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.feature_engineer = FeatureEngineer(supabase_client)
        self.model: Optional[RandomForestRegressor] = None
        self.feature_columns: Optional[list] = None
        self.metrics: Optional[Dict[str, float]] = None

    async def train(
        self,
        city: str,
        days: int = 60,
        n_estimators: int = 100,
        max_depth: int = 20,
        random_state: int = 42,
        test_size: float = 0.2
    ) -> Dict[str, Any]:
        """
        Train Random Forest model on historical data.

        Args:
            city: City to train model for
            days: Days of historical data to use
            n_estimators: Number of trees in forest
            max_depth: Maximum depth of trees
            random_state: Random seed for reproducibility
            test_size: Fraction of data for testing

        Returns:
            Dictionary with training metrics and status
        """
        print(f"[Training] Fetching {days} days of data for {city}...")

        # Fetch and prepare data
        raw_df = await self.feature_engineer.fetch_training_data(city, days=days)

        print(f"[Training] Extracted {len(raw_df)} raw records")

        # Engineer features
        print("[Training] Engineering features...")
        features_df = self.feature_engineer.extract_features(raw_df)

        # Prepare training data (J+1 = 24h forecast)
        X, y = self.feature_engineer.prepare_training_data(
            features_df,
            target_column='pm25',
            forecast_hours=24
        )

        print(f"[Training] Prepared {len(X)} training samples with {len(X.columns)} features")

        # Store feature columns for later use
        self.feature_columns = X.columns.tolist()

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=random_state,
            shuffle=False  # Keep temporal order
        )

        print(f"[Training] Training set: {len(X_train)}, Test set: {len(X_test)}")

        # Train Random Forest
        print("[Training] Training Random Forest model...")
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=-1,  # Use all CPU cores
            verbose=0
        )

        self.model.fit(X_train, y_train)

        # Evaluate on test set
        print("[Training] Evaluating model...")
        y_pred = self.model.predict(X_test)

        # Calculate metrics
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100

        # Cross-validation score
        cv_scores = cross_val_score(
            self.model, X_train, y_train,
            cv=5,
            scoring='r2',
            n_jobs=-1
        )

        self.metrics = {
            'mae': float(mae),
            'rmse': float(rmse),
            'r2': float(r2),
            'mape': float(mape),
            'cv_r2_mean': float(cv_scores.mean()),
            'cv_r2_std': float(cv_scores.std()),
            'n_samples': len(X),
            'n_features': len(self.feature_columns),
            'test_samples': len(X_test)
        }

        print("\n" + "="*60)
        print("MODEL EVALUATION RESULTS")
        print("="*60)
        print(f"R2 Score:              {r2:.4f}")
        print(f"MAE:                   {mae:.2f} ug/m3")
        print(f"RMSE:                  {rmse:.2f} ug/m3")
        print(f"MAPE:                  {mape:.2f}%")
        print(f"Cross-Val R2 (mean):   {cv_scores.mean():.4f} +/- {cv_scores.std():.4f}")
        print("="*60)

        # Check if model meets requirements
        if r2 >= 0.7 and mape <= 30:
            print("[OK] Model meets performance requirements (R2 > 0.7, MAPE < 30%)")
            status = "success"
        else:
            print("[WARNING] Model does not meet performance requirements")
            status = "warning"

        return {
            'status': status,
            'metrics': self.metrics,
            'city': city,
            'trained_at': datetime.utcnow().isoformat()
        }

    def save_model(self, city: str) -> str:
        """
        Save trained model to disk.

        Args:
            city: City name (used in filename)

        Returns:
            Path to saved model file
        """
        if self.model is None:
            raise ValueError("No model trained yet. Call train() first.")

        model_path = self.model_dir / f"pm25_model_{city.lower()}.pkl"

        model_data = {
            'model': self.model,
            'feature_columns': self.feature_columns,
            'metrics': self.metrics,
            'trained_at': datetime.utcnow().isoformat(),
            'city': city
        }

        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)

        print(f"[OK] Model saved to {model_path}")

        return str(model_path)

    def load_model(self, city: str) -> Dict[str, Any]:
        """
        Load trained model from disk.

        Args:
            city: City name

        Returns:
            Model metadata
        """
        model_path = self.model_dir / f"pm25_model_{city.lower()}.pkl"

        if not model_path.exists():
            raise FileNotFoundError(f"No trained model found for {city} at {model_path}")

        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)

        self.model = model_data['model']
        self.feature_columns = model_data['feature_columns']
        self.metrics = model_data['metrics']

        print(f"[OK] Model loaded from {model_path}")
        print(f"     Trained at: {model_data['trained_at']}")
        print(f"     R² score: {self.metrics['r2']:.4f}")

        return {
            'trained_at': model_data['trained_at'],
            'metrics': self.metrics,
            'city': city
        }

    def get_feature_importance(self, top_n: int = 10) -> pd.DataFrame:
        """
        Get feature importance from trained model.

        Args:
            top_n: Number of top features to return

        Returns:
            DataFrame with feature names and importance scores
        """
        if self.model is None or self.feature_columns is None:
            raise ValueError("No model trained yet")

        importance_df = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)

        return importance_df.head(top_n)
