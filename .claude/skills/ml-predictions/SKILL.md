# Skill: ML Predictions (Air Quality Forecasting)

## Purpose
Develop and maintain machine learning models for predicting air quality (PM2.5) at J+1, detecting anomalies in sensor data, and providing confidence scores for predictions.

## When to Use
- Training prediction models for air quality forecasting
- Implementing anomaly detection algorithms
- Feature engineering from pollution and weather data
- Evaluating model performance
- Making real-time predictions via API
- Updating or retraining models

## Objective
Predict PM2.5 concentration at J+1 with accuracy > 70% (R² > 0.7, MAPE < 30%)

## Architecture

```
backend/app/ml/
├── predictor.py           # PM2.5 prediction model
├── anomaly_detector.py    # Anomaly detection (Z-score, Isolation Forest)
├── trainer.py             # Model training pipeline
├── feature_engineering.py # Feature extraction and preparation
└── models/                # Saved model artifacts
    ├── pm25_model.pkl
    ├── scaler.pkl
    └── metadata.json
```

## Feature Engineering

### Input Features (X)

```python
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create features for PM2.5 prediction.

    Input: DataFrame with columns [timestamp, pm25, temperature, humidity, wind_speed, pressure]
    Output: DataFrame with engineered features
    """
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')

    # Historical pollution features (7-day rolling statistics)
    df['pm25_mean_7d'] = df['pm25'].rolling(window=7*24, min_periods=1).mean()
    df['pm25_std_7d'] = df['pm25'].rolling(window=7*24, min_periods=1).std()
    df['pm25_max_7d'] = df['pm25'].rolling(window=7*24, min_periods=1).max()
    df['pm25_min_7d'] = df['pm25'].rolling(window=7*24, min_periods=1).min()

    # Lag features (previous values)
    df['pm25_lag_24h'] = df['pm25'].shift(24)
    df['pm25_lag_48h'] = df['pm25'].shift(48)

    # Temporal features
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek  # 0=Monday, 6=Sunday
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    df['month'] = df['timestamp'].dt.month
    df['season'] = (df['month'] % 12 + 3) // 3  # 1=Winter, 2=Spring, 3=Summer, 4=Fall

    # Weather features (current values)
    # Already have: temperature, humidity, wind_speed, pressure

    # Weather interactions
    df['temp_humidity_interaction'] = df['temperature'] * df['humidity']
    df['wind_pressure_interaction'] = df['wind_speed'] * df['pressure']

    # Target variable (next day's PM2.5)
    df['pm25_next_day'] = df['pm25'].shift(-24)

    return df

# Feature list for training
FEATURE_COLUMNS = [
    'pm25_mean_7d',
    'pm25_std_7d',
    'pm25_lag_24h',
    'pm25_lag_48h',
    'temperature',
    'humidity',
    'wind_speed',
    'pressure',
    'hour',
    'day_of_week',
    'is_weekend',
    'season',
    'temp_humidity_interaction',
    'wind_pressure_interaction'
]

TARGET_COLUMN = 'pm25_next_day'
```

## Model Training Pipeline

### 1. Data Preparation

```python
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
import joblib

def prepare_training_data(df: pd.DataFrame):
    """
    Prepare data for time-series model training.

    Returns: X_train, X_test, y_train, y_test, scaler
    """
    # Engineer features
    df_features = engineer_features(df)

    # Remove rows with NaN (from rolling windows and shifts)
    df_clean = df_features.dropna()

    # Split features and target
    X = df_clean[FEATURE_COLUMNS]
    y = df_clean[TARGET_COLUMN]

    # Time-series split (80/20)
    split_idx = int(len(X) * 0.8)
    X_train = X[:split_idx]
    X_test = X[split_idx:]
    y_train = y[:split_idx]
    y_test = y[split_idx:]

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    return X_train_scaled, X_test_scaled, y_train, y_test, scaler
```

### 2. Model Training

```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np

class PM25Predictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.metadata = {}

    def train(self, X_train, y_train, X_test, y_test):
        """
        Train Random Forest model for PM2.5 prediction.
        """
        # Initialize model
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )

        # Train
        print("Training Random Forest model...")
        self.model.fit(X_train, y_train)

        # Evaluate
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)

        y_pred = self.model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100

        # Store metadata
        self.metadata = {
            'train_r2': train_score,
            'test_r2': test_score,
            'rmse': rmse,
            'mae': mae,
            'r2': r2,
            'mape': mape,
            'n_features': X_train.shape[1],
            'feature_importances': dict(zip(FEATURE_COLUMNS, self.model.feature_importances_))
        }

        print(f"Training R²: {train_score:.4f}")
        print(f"Test R²: {test_score:.4f}")
        print(f"RMSE: {rmse:.2f}")
        print(f"MAE: {mae:.2f}")
        print(f"MAPE: {mape:.2f}%")

        return self.metadata

    def predict(self, X, confidence=True):
        """
        Make prediction with optional confidence interval.
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        prediction = self.model.predict(X)

        if confidence and hasattr(self.model, 'estimators_'):
            # Calculate prediction interval using individual trees
            predictions = np.array([tree.predict(X) for tree in self.model.estimators_])
            lower_bound = np.percentile(predictions, 25, axis=0)
            upper_bound = np.percentile(predictions, 75, axis=0)
            std = np.std(predictions, axis=0)

            return {
                'prediction': prediction[0],
                'lower_bound': lower_bound[0],
                'upper_bound': upper_bound[0],
                'std': std[0],
                'confidence_score': 1 - (std[0] / prediction[0]) if prediction[0] > 0 else 0
            }

        return {'prediction': prediction[0]}

    def save(self, model_path='models/pm25_model.pkl', scaler_path='models/scaler.pkl'):
        """Save trained model and scaler."""
        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, scaler_path)
        print(f"Model saved to {model_path}")

    def load(self, model_path='models/pm25_model.pkl', scaler_path='models/scaler.pkl'):
        """Load pre-trained model and scaler."""
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        print(f"Model loaded from {model_path}")
```

### 3. Cross-Validation for Time Series

```python
from sklearn.model_selection import TimeSeriesSplit

def time_series_cv(X, y, n_splits=5):
    """
    Perform time-series cross-validation.
    """
    tscv = TimeSeriesSplit(n_splits=n_splits)
    scores = []

    for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
        X_train_cv, X_val_cv = X[train_idx], X[val_idx]
        y_train_cv, y_val_cv = y[train_idx], y[val_idx]

        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train_cv, y_train_cv)

        score = model.score(X_val_cv, y_val_cv)
        scores.append(score)
        print(f"Fold {fold+1}: R² = {score:.4f}")

    print(f"Mean CV R²: {np.mean(scores):.4f} (+/- {np.std(scores):.4f})")
    return scores
```

## Anomaly Detection

### Z-Score Method

```python
class ZScoreAnomalyDetector:
    """Detect anomalies using statistical Z-score method."""

    def __init__(self, threshold=3.0):
        self.threshold = threshold
        self.mean = None
        self.std = None

    def fit(self, data):
        """Fit detector on historical data."""
        self.mean = np.mean(data)
        self.std = np.std(data)

    def detect(self, value):
        """
        Detect if a value is anomalous.

        Returns: (is_anomaly, z_score)
        """
        if self.mean is None or self.std is None:
            raise ValueError("Detector not fitted. Call fit() first.")

        z_score = abs((value - self.mean) / self.std) if self.std > 0 else 0
        is_anomaly = z_score > self.threshold

        return is_anomaly, z_score

# Usage
detector = ZScoreAnomalyDetector(threshold=3.0)
detector.fit(historical_pm25_data)

is_anomaly, z_score = detector.detect(new_pm25_value)
if is_anomaly:
    print(f"Anomaly detected! Z-score: {z_score:.2f}")
```

### Isolation Forest Method

```python
from sklearn.ensemble import IsolationForest

class IsolationForestDetector:
    """Detect anomalies using Isolation Forest algorithm."""

    def __init__(self, contamination=0.1):
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )

    def fit(self, X):
        """Fit on historical multi-feature data."""
        self.model.fit(X)

    def detect(self, X):
        """
        Detect anomalies.

        Returns: -1 for anomaly, 1 for normal
        """
        prediction = self.model.predict(X)
        score = self.model.score_samples(X)

        return prediction[0], score[0]

# Usage with multiple features
detector = IsolationForestDetector(contamination=0.05)
detector.fit(historical_data[['pm25', 'temperature', 'humidity']])

prediction, score = detector.detect([[new_pm25, new_temp, new_humidity]])
if prediction == -1:
    print(f"Anomaly detected! Anomaly score: {score:.4f}")
```

## API Integration

### Prediction Endpoint

```python
# backend/app/api/v1/predictions.py
from fastapi import APIRouter, HTTPException, Depends
from app.ml.predictor import PM25Predictor
from app.models.prediction import PredictionRequest, PredictionResponse
import numpy as np

router = APIRouter(prefix="/api/v1/predictions", tags=["predictions"])

# Load model at startup
predictor = PM25Predictor()
predictor.load()

@router.post("/pm25", response_model=PredictionResponse)
async def predict_pm25(request: PredictionRequest):
    """
    Predict PM2.5 concentration for next day.

    Input features: pm25_mean_7d, temperature, humidity, wind_speed, etc.
    """
    try:
        # Prepare feature array
        features = np.array([[
            request.pm25_mean_7d,
            request.pm25_std_7d,
            request.pm25_lag_24h,
            request.pm25_lag_48h,
            request.temperature,
            request.humidity,
            request.wind_speed,
            request.pressure,
            request.hour,
            request.day_of_week,
            request.is_weekend,
            request.season,
            request.temperature * request.humidity,
            request.wind_speed * request.pressure
        ]])

        # Scale features
        features_scaled = predictor.scaler.transform(features)

        # Make prediction
        result = predictor.predict(features_scaled, confidence=True)

        return PredictionResponse(
            predicted_pm25=result['prediction'],
            confidence_score=result['confidence_score'],
            lower_bound=result['lower_bound'],
            upper_bound=result['upper_bound'],
            prediction_date=(datetime.utcnow() + timedelta(days=1)).date()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Model Evaluation Metrics

```python
from sklearn.metrics import mean_absolute_percentage_error

def evaluate_model(y_true, y_pred):
    """
    Calculate comprehensive evaluation metrics.
    """
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    mape = mean_absolute_percentage_error(y_true, y_pred) * 100

    metrics = {
        'RMSE': rmse,
        'MAE': mae,
        'R²': r2,
        'MAPE': mape,
        'n_samples': len(y_true)
    }

    print("Model Evaluation Metrics:")
    print(f"  RMSE: {rmse:.2f} μg/m³")
    print(f"  MAE: {mae:.2f} μg/m³")
    print(f"  R²: {r2:.4f}")
    print(f"  MAPE: {mape:.2f}%")

    return metrics

# Interpretation
# R² > 0.7: Good model fit
# MAPE < 30%: Acceptable prediction error
```

## Best Practices

### Data Requirements
- Minimum 6 months of historical data for training
- Hourly measurements preferred
- Handle missing values (forward fill or interpolation)
- Remove outliers before training (Z-score > 5)

### Feature Engineering
- Use rolling statistics (7-day, 30-day windows)
- Include lag features (24h, 48h)
- Add temporal features (hour, day of week, season)
- Create interaction terms for weather features

### Model Selection
- Start with baseline: Linear Regression
- Production model: Random Forest (best balance)
- Advanced: XGBoost or LSTM for time series

### Model Updates
- Retrain monthly with new data
- Monitor prediction drift
- A/B test new models before deployment
- Version models (v1.0, v1.1, etc.)

### Performance Optimization
- Cache model in memory (singleton pattern)
- Precompute rolling features daily
- Use model compression (quantization)
- Batch predictions when possible

## Common Tasks

### Training a New Model
```bash
# Run training script
python -m app.ml.trainer --data-path data/historical.csv --output models/pm25_v2.pkl
```

### Retraining with New Data
```python
# Fetch new data from database
new_data = supabase.table('air_quality_measurements').select('*').execute()
df_new = pd.DataFrame(new_data.data)

# Append to existing data
df_combined = pd.concat([df_old, df_new])

# Retrain
X_train, X_test, y_train, y_test, scaler = prepare_training_data(df_combined)
predictor = PM25Predictor()
predictor.train(X_train, y_train, X_test, y_test)
predictor.save('models/pm25_v2.pkl')
```

### Monitoring Predictions
```python
# Store predictions for monitoring
prediction_log = {
    'predicted_value': result['prediction'],
    'actual_value': None,  # Fill next day
    'confidence_score': result['confidence_score'],
    'prediction_date': target_date,
    'created_at': datetime.utcnow()
}

supabase.table('predictions').insert(prediction_log).execute()
```

## References
- Scikit-learn: https://scikit-learn.org/stable/
- Time Series Forecasting: https://otexts.com/fpp3/
- Random Forest: https://scikit-learn.org/stable/modules/ensemble.html#forest

## Trade-offs

**Random Forest vs. XGBoost:**
- RF: Easier to tune, less overfitting, faster training
- XGBoost: Higher accuracy, slower, more parameters

**Z-Score vs. Isolation Forest:**
- Z-Score: Simple, fast, works for univariate data
- Isolation Forest: Handles multivariate, detects complex anomalies

**Model Complexity:**
- More features ≠ better model (risk of overfitting)
- Balance accuracy vs. interpretability
- Simpler models easier to debug and maintain
