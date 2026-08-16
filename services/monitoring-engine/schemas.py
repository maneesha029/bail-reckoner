"""
Pydantic schemas for Monitoring & Outreach Engine API.

Defines request/response structures for all 3 endpoints.

Time Complexity: Schema validation is O(n) where n = fields in schema
Space Complexity: O(1) per schema instance
"""

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum
import re


class AlertStatusEnum(str, Enum):
    """Alert status options."""
    PENDING = "pending"
    NOTIFIED = "notified"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    FAILED = "failed"


# ============================================================================
# Endpoint 1: POST /api/v1/alerts/config — Save notification preferences
# ============================================================================

class AlertConfigRequest(BaseModel):
    """Request to save alert notification preferences."""
    
    user_id: str = Field(..., description="User ID from trust layer")
    email_enabled: bool = Field(default=True, description="Enable email notifications")
    email_address: Optional[str] = Field(default=None, description="Email address for notifications")
    sms_enabled: bool = Field(default=False, description="Enable SMS notifications")
    sms_number: Optional[str] = Field(default=None, description="Phone number for SMS")
    notify_immediately: bool = Field(default=True, description="Alert immediately or digest only")
    digest_enabled: bool = Field(default=False, description="Enable daily digest")
    digest_hour: int = Field(default=9, ge=0, le=23, description="Hour for daily digest (0-23)")
    
    @field_validator('email_address')
    @classmethod
    def validate_email(cls, v):
        """Validate email format if provided."""
        if v is None:
            return v
        # Simple email validation
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v
    
    @field_validator('sms_number')
    @classmethod
    def validate_phone(cls, v):
        """Validate phone number if provided."""
        if v is None:
            return v
        # Accept +91 or just 10 digits (Indian phone number)
        if not re.match(r'^(\+91|91)?[6-9]\d{9}$', v):
            raise ValueError('Invalid Indian phone number')
        return v
    
    @model_validator(mode='after')
    def validate_email_requirements(self):
        """If email enabled, email_address must be provided."""
        if self.email_enabled and not self.email_address:
            raise ValueError('email_address required when email_enabled=true')
        return self
    
    @model_validator(mode='after')
    def validate_sms_requirements(self):
        """If SMS enabled, sms_number must be provided."""
        if self.sms_enabled and not self.sms_number:
            raise ValueError('sms_number required when sms_enabled=true')
        return self


class AlertConfigResponse(BaseModel):
    """Response after saving alert config."""
    
    id: str = Field(..., description="Unique config ID")
    user_id: str = Field(..., description="User ID")
    email_enabled: bool
    email_address: Optional[str]
    sms_enabled: bool
    sms_number: Optional[str]
    notify_immediately: bool
    digest_enabled: bool
    digest_hour: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Endpoint 2: GET /api/v1/alerts/pending — List pending alerts
# ============================================================================

class AlertRecordResponse(BaseModel):
    """Single alert record in response."""
    
    id: str = Field(..., description="Alert ID")
    case_id: str = Field(..., description="Case ID")
    prisoner_id: str = Field(..., description="Prisoner ID")
    state: str = Field(..., description="State")
    district: str = Field(..., description="District")
    offense_category: str = Field(..., description="Offense category")
    max_sentence_months: int = Field(..., description="Max sentence in months")
    custody_start_date: datetime = Field(..., description="When prisoner entered custody")
    eligibility_reason: str = Field(..., description="Why case is eligible (e.g., served_50_percent)")
    date_became_eligible: datetime = Field(..., description="When case became eligible")
    status: AlertStatusEnum = Field(..., description="Alert status")
    last_notified_at: Optional[datetime] = Field(None, description="Last notification timestamp")
    created_at: datetime = Field(..., description="Alert creation timestamp")
    
    model_config = ConfigDict(from_attributes=True)


class PendingAlertsResponse(BaseModel):
    """Response to GET /api/v1/alerts/pending."""
    
    count: int = Field(..., description="Number of pending alerts")
    pending_alerts: List[AlertRecordResponse] = Field(..., description="List of pending alerts")
    filters_applied: Dict[str, Any] = Field(default={}, description="Filters used in query")


# ============================================================================
# Endpoint 3: GET /api/v1/alerts/scan — Internal scan trigger
# ============================================================================

class ScanResultResponse(BaseModel):
    """Response to GET /api/v1/alerts/scan (internal endpoint)."""
    
    total_cases_scanned: int = Field(..., description="Total undertrial cases checked")
    newly_eligible_found: int = Field(..., description="Cases newly found eligible")
    newly_flagged: int = Field(..., description="New alert records created")
    skipped_already_flagged: int = Field(..., description="Cases already flagged")
    errors: List[str] = Field(default=[], description="Any errors during scan")
    scan_timestamp: datetime = Field(..., description="When scan ran")
    scan_duration_seconds: float = Field(..., description="How long scan took")


# ============================================================================
# Standard Response Envelope (used by all endpoints)
# ============================================================================

class StandardResponse(BaseModel):
    """
    Standard response envelope for all API responses.
    
    All endpoints return this format:
    {
        "success": true/false,
        "data": <response_data>,
        "error": null or error message
    }
    """
    
    success: bool = Field(..., description="Whether request succeeded")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Response data")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Response timestamp")


# ============================================================================
# Error Response
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = False
    data: None = None
    error: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))