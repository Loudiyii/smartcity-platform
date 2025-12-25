"""Pydantic models for alerts and notifications."""

from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, EmailStr


class AlertRecord(BaseModel):
    """Alert database record."""
    id: Optional[int] = Field(None, description="Alert ID")
    city: str = Field(..., description="City name")
    alert_type: str = Field(..., description="Alert type")
    severity: str = Field(..., description="Severity level")
    message: str = Field(..., description="Alert message")
    data: Dict[str, Any] = Field(..., description="Alert data")
    is_active: bool = Field(True, description="Is alert active")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")


class AlertResponse(BaseModel):
    """Alert API response."""
    alert: AlertRecord
    recommendations: List[str] = Field(..., description="Health recommendations")


class SendAlertEmailRequest(BaseModel):
    """Request to send alert email."""
    city: str = Field(..., description="City name")
    recipients: List[EmailStr] = Field(..., min_items=1, description="Email recipients")


class EmailSentResponse(BaseModel):
    """Email send response."""
    success: bool = Field(..., description="Whether email was sent")
    recipients_count: int = Field(..., description="Number of recipients")
    message: str = Field(..., description="Status message")
