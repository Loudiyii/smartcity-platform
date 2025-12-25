"""
PM2.5 Prediction Service
Makes J+1 forecasts using trained Random Forest model
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import pandas as pd
from supabase import Client

from app.ml.trainer import PM25ModelTrainer
from app.ml.feature_engineering import FeatureEngineer


class PM25Predictor:
    """Makes PM2.5 predictions using trained model."""

    def __init__(self, supabase_client: Client):
        """
        Initialize predictor.

        Args:
            supabase_client: Supabase client
        """
        self.supabase = supabase_client
        self.trainer = PM25ModelTrainer(supabase_client)
        self.feature_engineer = FeatureEngineer(supabase_client)

    async def predict_j_plus_1(self, city: str) -> Dict[str, Any]:
        """
        Predict PM2.5 concentration for J+1 (24 hours ahead).

        Args:
            city: City name

        Returns:
            Dictionary with prediction and metadata
        """
        # Load trained model
        try:
            model_metadata = self.trainer.load_model(city)
        except FileNotFoundError:
            raise ValueError(
                f"No trained model found for {city}. "
                f"Train a model first using the /predictions/train endpoint."
            )

        # Prepare features for current time
        current_time = datetime.utcnow()
        features_df = await self.feature_engineer.prepare_prediction_features(
            city, prediction_time=current_time
        )

        # Ensure features match training columns
        missing_cols = set(self.trainer.feature_columns) - set(features_df.columns)
        if missing_cols:
            raise ValueError(f"Missing features for prediction: {missing_cols}")

        # Reorder columns to match training
        X = features_df[self.trainer.feature_columns]

        # Make prediction
        predicted_pm25 = self.trainer.model.predict(X)[0]

        # Calculate confidence based on model metrics
        # Confidence = 1 - (MAPE / 100)
        confidence = max(0, 1 - (self.trainer.metrics['mape'] / 100))

        # Get prediction range (±1 std dev)
        # Using RMSE as approximation of std dev
        rmse = self.trainer.metrics['rmse']
        prediction_lower = max(0, predicted_pm25 - rmse)
        prediction_upper = predicted_pm25 + rmse

        # Determine air quality level
        aqi_level = self._get_aqi_level(predicted_pm25)

        # Prediction time (24h from now)
        prediction_for = current_time + timedelta(hours=24)

        result = {
            'city': city,
            'predicted_pm25': round(float(predicted_pm25), 2),
            'confidence': round(float(confidence), 2),
            'prediction_range': {
                'lower': round(float(prediction_lower), 2),
                'upper': round(float(prediction_upper), 2)
            },
            'aqi_level': aqi_level,
            'prediction_for': prediction_for.isoformat(),
            'predicted_at': current_time.isoformat(),
            'model_metrics': {
                'r2': self.trainer.metrics['r2'],
                'mape': self.trainer.metrics['mape'],
                'rmse': self.trainer.metrics['rmse']
            }
        }

        # Save prediction to database
        await self._save_prediction(result)

        return result

    async def _save_prediction(self, prediction: Dict[str, Any]) -> None:
        """
        Save prediction to database.

        Args:
            prediction: Prediction result dictionary
        """
        prediction_record = {
            'city': prediction['city'],
            'prediction_for': prediction['prediction_for'],
            'predicted_pm25': prediction['predicted_pm25'],
            'confidence': prediction['confidence'],
            'prediction_range_lower': prediction['prediction_range']['lower'],
            'prediction_range_upper': prediction['prediction_range']['upper'],
            'model_r2': prediction['model_metrics']['r2'],
            'model_mape': prediction['model_metrics']['mape'],
            'created_at': prediction['predicted_at']
        }

        self.supabase.table('predictions').insert(prediction_record).execute()

    @staticmethod
    def _get_aqi_level(pm25: float) -> Dict[str, Any]:
        """
        Determine AQI level from PM2.5 concentration.

        Args:
            pm25: PM2.5 value in μg/m³

        Returns:
            Dictionary with level info
        """
        if pm25 <= 12:
            return {
                'name': 'Good',
                'color': 'green',
                'description': 'Air quality is satisfactory'
            }
        elif pm25 <= 35.4:
            return {
                'name': 'Moderate',
                'color': 'yellow',
                'description': 'Air quality is acceptable'
            }
        elif pm25 <= 55.4:
            return {
                'name': 'Unhealthy for Sensitive Groups',
                'color': 'orange',
                'description': 'Sensitive groups may experience health effects'
            }
        elif pm25 <= 150.4:
            return {
                'name': 'Unhealthy',
                'color': 'red',
                'description': 'Everyone may begin to experience health effects'
            }
        elif pm25 <= 250.4:
            return {
                'name': 'Very Unhealthy',
                'color': 'purple',
                'description': 'Health alert: everyone may experience serious effects'
            }
        else:
            return {
                'name': 'Hazardous',
                'color': 'maroon',
                'description': 'Health warnings of emergency conditions'
            }

    async def get_recent_predictions(
        self,
        city: str,
        limit: int = 10
    ) -> list[Dict[str, Any]]:
        """
        Get recent predictions for a city.

        Args:
            city: City name
            limit: Number of predictions to return

        Returns:
            List of prediction records
        """
        response = self.supabase.table('predictions')\
            .select('*')\
            .eq('city', city)\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()

        return response.data
