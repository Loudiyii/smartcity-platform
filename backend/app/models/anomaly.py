"""Pydantic models for anomaly detection."""

from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class AnomalyRecord(BaseModel):
    """Single anomaly detection record."""
    city: str = Field(..., description="City name")
    timestamp: datetime = Field(..., description="When anomaly occurred")
    pm25: float = Field(..., ge=0, description="PM2.5 value")
    detection_method: str = Field(..., description="Detection method (z_score, isolation_forest)")
    severity: str = Field(..., description="Severity level (low, medium, high, critical)")
    detected_at: datetime = Field(..., description="When anomaly was detected")
    z_score: Optional[float] = Field(None, description="Z-score (if z_score method)")
    anomaly_score: Optional[float] = Field(None, description="Anomaly score (if isolation_forest)")
    expected_pm25: Optional[float] = Field(None, description="Expected PM2.5 value")


class AnomalyDetectionResponse(BaseModel):
    """Response for anomaly detection."""
    city: str = Field(..., description="City name")
    total_anomalies: int = Field(..., ge=0, description="Total anomalies detected")
    zscore_count: int = Field(..., ge=0, description="Anomalies from Z-score method")
    isolation_forest_count: int = Field(..., ge=0, description="Anomalies from Isolation Forest")
    anomalies: List[Dict[str, Any]] = Field(..., description="List of anomaly records")
    lookback_days: int = Field(..., description="Days analyzed")
    detected_at: datetime = Field(..., description="Detection timestamp")


class AnomalyAlert(BaseModel):
    """Anomaly alert record."""
    id: int = Field(..., description="Alert ID")
    city: str = Field(..., description="City name")
    alert_type: str = Field(..., description="Alert type")
    severity: str = Field(..., description="Severity level")
    message: str = Field(..., description="Alert message")
    data: Dict[str, Any] = Field(..., description="Anomaly data")
    is_active: bool = Field(..., description="Is alert active")
    created_at: datetime = Field(..., description="Creation timestamp")
