"""
Feature Engineering for Air Quality Prediction
Extracts and transforms time-series data into ML-ready features
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from supabase import Client


class FeatureEngineer:
    """Handles feature extraction and transformation for ML models."""

    def __init__(self, supabase_client: Client):
        """
        Initialize feature engineer.

        Args:
            supabase_client: Supabase client for database access
        """
        self.supabase = supabase_client

    async def fetch_training_data(
        self,
        city: str,
        days: int = 60,
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Fetch historical data from Supabase for training.

        Args:
            city: City name
            days: Number of days of historical data
            end_date: End date for data fetch (defaults to now)

        Returns:
            DataFrame with air quality and weather data
        """
        if end_date is None:
            end_date = datetime.utcnow()

        start_date = end_date - timedelta(days=days)

        # Fetch air quality measurements
        # Note: Supabase has a 1000 record default limit, so we need to fetch in batches
        all_aq_data = []
        offset = 0
        batch_size = 1000

        while True:
            aq_response = self.supabase.table('air_quality_measurements')\
                .select('*')\
                .eq('city', city)\
                .gte('timestamp', start_date.isoformat())\
                .lte('timestamp', end_date.isoformat())\
                .order('timestamp')\
                .range(offset, offset + batch_size - 1)\
                .execute()

            if not aq_response.data:
                break

            all_aq_data.extend(aq_response.data)

            if len(aq_response.data) < batch_size:
                break

            offset += batch_size

        # Fetch weather data in batches
        all_weather_data = []
        offset = 0

        while True:
            weather_response = self.supabase.table('weather_data')\
                .select('*')\
                .eq('city', city)\
                .gte('timestamp', start_date.isoformat())\
                .lte('timestamp', end_date.isoformat())\
                .order('timestamp')\
                .range(offset, offset + batch_size - 1)\
                .execute()

            if not weather_response.data:
                break

            all_weather_data.extend(weather_response.data)

            if len(weather_response.data) < batch_size:
                break

            offset += batch_size

        # Convert to DataFrames
        aq_df = pd.DataFrame(all_aq_data)
        weather_df = pd.DataFrame(all_weather_data)

        if aq_df.empty or weather_df.empty:
            raise ValueError(f"Insufficient data for {city}. Need at least {days} days.")

        # Convert timestamps
        aq_df['timestamp'] = pd.to_datetime(aq_df['timestamp'])
        weather_df['timestamp'] = pd.to_datetime(weather_df['timestamp'])

        # Merge on timestamp
        df = pd.merge(
            aq_df,
            weather_df,
            on=['timestamp', 'city'],
            how='inner',
            suffixes=('_aq', '_weather')
        )

        return df

    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract features from raw time-series data.

        Features created:
        - Temporal: hour, day_of_week, is_weekend, season
        - Rolling statistics: 7-day mean/std for PM2.5
        - Weather: temperature, humidity, wind_speed, pressure
        - Lag features: PM2.5 from 1h, 6h, 12h, 24h ago

        Args:
            df: Raw DataFrame with air quality and weather data

        Returns:
            DataFrame with engineered features
        """
        df = df.copy()
        df = df.sort_values('timestamp').reset_index(drop=True)

        print(f"[Feature Eng] Initial rows: {len(df)}")

        # Temporal features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        df['month'] = df['timestamp'].dt.month

        # Season (Northern hemisphere)
        def get_season(month):
            if month in [12, 1, 2]:
                return 0  # winter
            elif month in [3, 4, 5]:
                return 1  # spring
            elif month in [6, 7, 8]:
                return 2  # summer
            else:
                return 3  # fall

        df['season'] = df['month'].apply(get_season)

        # Rolling statistics (7-day window)
        df['pm25_mean_7d'] = df['pm25'].rolling(window=7*24, min_periods=24).mean()
        df['pm25_std_7d'] = df['pm25'].rolling(window=7*24, min_periods=24).std()
        df['pm25_min_7d'] = df['pm25'].rolling(window=7*24, min_periods=24).min()
        df['pm25_max_7d'] = df['pm25'].rolling(window=7*24, min_periods=24).max()

        # Lag features
        df['pm25_lag_1h'] = df['pm25'].shift(1)
        df['pm25_lag_6h'] = df['pm25'].shift(6)
        df['pm25_lag_12h'] = df['pm25'].shift(12)
        df['pm25_lag_24h'] = df['pm25'].shift(24)

        # Weather features (already in df)
        # - temperature, humidity, wind_speed, pressure

        # Rate of change
        df['pm25_change_1h'] = df['pm25'] - df['pm25_lag_1h']
        df['pm25_change_24h'] = df['pm25'] - df['pm25_lag_24h']

        # Drop rows with NaN values ONLY in feature/target columns we care about
        # Don't drop based on nullable columns like location, visibility, description
        required_cols = [
            'pm25', 'pm10', 'no2', 'o3',  # Pollutants
            'temperature', 'humidity', 'wind_speed', 'pressure',  # Weather
            'pm25_mean_7d', 'pm25_std_7d', 'pm25_min_7d', 'pm25_max_7d',  # Rolling stats
            'pm25_lag_1h', 'pm25_lag_6h', 'pm25_lag_12h', 'pm25_lag_24h',  # Lags
            'pm25_change_1h', 'pm25_change_24h'  # Changes
        ]

        print(f"[Feature Eng] Before dropna: {len(df)} rows")
        df = df.dropna(subset=required_cols)
        print(f"[Feature Eng] After dropna: {len(df)} rows")

        return df

    def prepare_training_data(
        self,
        df: pd.DataFrame,
        target_column: str = 'pm25',
        forecast_hours: int = 24
    ) -> tuple[pd.DataFrame, pd.Series]:
        """
        Prepare features (X) and target (y) for training.

        For J+1 prediction, we shift the target by forecast_hours to the future.

        Args:
            df: DataFrame with engineered features
            target_column: Name of target variable
            forecast_hours: Hours ahead to forecast (24 for J+1)

        Returns:
            X: Feature matrix, y: Target vector
        """
        df = df.copy()

        print(f"[Prepare Training] Input rows: {len(df)}")
        print(f"[Prepare Training] Columns: {list(df.columns)}")

        # Create target variable (shifted to future)
        df['target'] = df[target_column].shift(-forecast_hours)

        print(f"[Prepare Training] After target shift: {len(df)} rows, NaN in target: {df['target'].isna().sum()}")

        # Drop rows with NaN target ONLY (not other columns!)
        df = df.dropna(subset=['target'])

        print(f"[Prepare Training] After dropna: {len(df)} rows")

        # Define feature columns
        feature_cols = [
            # Temporal
            'hour', 'day_of_week', 'is_weekend', 'season',
            # Rolling stats
            'pm25_mean_7d', 'pm25_std_7d', 'pm25_min_7d', 'pm25_max_7d',
            # Lag features
            'pm25_lag_1h', 'pm25_lag_6h', 'pm25_lag_12h', 'pm25_lag_24h',
            # Rate of change
            'pm25_change_1h', 'pm25_change_24h',
            # Weather
            'temperature', 'humidity', 'wind_speed', 'pressure',
            # Other pollutants (optional - can improve prediction)
            'pm10', 'no2', 'o3'
        ]

        # Filter to only existing columns
        feature_cols = [col for col in feature_cols if col in df.columns]

        X = df[feature_cols]
        y = df['target']

        return X, y

    async def prepare_prediction_features(
        self,
        city: str,
        prediction_time: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Prepare features for making a prediction at a specific time.

        Args:
            city: City name
            prediction_time: Time to make prediction for (defaults to now)

        Returns:
            Single-row DataFrame with features for prediction
        """
        if prediction_time is None:
            prediction_time = datetime.utcnow()

        # Fetch last 7 days of data for rolling features
        df = await self.fetch_training_data(city, days=7, end_date=prediction_time)

        # Extract features
        df = self.extract_features(df)

        # Return only the latest row (most recent data)
        return df.tail(1)
