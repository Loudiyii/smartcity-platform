"""Pydantic models for ML predictions."""

from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class PredictionRange(BaseModel):
    """Prediction confidence range."""
    lower: float = Field(..., description="Lower bound of prediction (μg/m³)")
    upper: float = Field(..., description="Upper bound of prediction (μg/m³)")


class AQILevel(BaseModel):
    """Air Quality Index level information."""
    name: str = Field(..., description="Level name (Good, Moderate, etc.)")
    color: str = Field(..., description="Color code for UI")
    description: str = Field(..., description="Health implications")


class ModelMetrics(BaseModel):
    """Model performance metrics."""
    r2: float = Field(..., ge=0, le=1, description="R² score")
    mape: float = Field(..., ge=0, description="Mean Absolute Percentage Error (%)")
    rmse: float = Field(..., ge=0, description="Root Mean Squared Error")


class PredictionResponse(BaseModel):
    """PM2.5 prediction response."""
    city: str = Field(..., description="City name")
    predicted_pm25: float = Field(..., ge=0, description="Predicted PM2.5 (μg/m³)")
    confidence: float = Field(..., ge=0, le=1, description="Prediction confidence (0-1)")
    prediction_range: PredictionRange = Field(..., description="Confidence interval")
    aqi_level: AQILevel = Field(..., description="Predicted AQI level")
    prediction_for: datetime = Field(..., description="Timestamp prediction is for")
    predicted_at: datetime = Field(..., description="When prediction was made")
    model_metrics: ModelMetrics = Field(..., description="Model performance metrics")


class TrainingRequest(BaseModel):
    """Request to train a model."""
    city: str = Field(..., description="City to train model for")
    days: int = Field(60, ge=30, le=365, description="Days of historical data to use")
    n_estimators: int = Field(100, ge=10, le=500, description="Number of trees")
    max_depth: Optional[int] = Field(20, ge=5, le=50, description="Max tree depth")


class TrainingResponse(BaseModel):
    """Training result response."""
    status: str = Field(..., description="Training status (success, warning, error)")
    metrics: Dict[str, float] = Field(..., description="Model performance metrics")
    city: str = Field(..., description="City name")
    trained_at: datetime = Field(..., description="Training timestamp")
    message: str = Field(..., description="Human-readable status message")


class FeatureImportance(BaseModel):
    """Feature importance from trained model."""
    feature: str = Field(..., description="Feature name")
    importance: float = Field(..., ge=0, le=1, description="Importance score")


class FeatureImportanceResponse(BaseModel):
    """Feature importance response."""
    city: str = Field(..., description="City name")
    features: list[FeatureImportance] = Field(..., description="Top features")
