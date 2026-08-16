"""
SQLAlchemy ORM models for Monitoring & Outreach Engine.

Member 5 owns:
  - alerts: Alert records created when cases become eligible
  - alert_configs: User notification preferences

Time Complexity: Model definitions are O(1) — no computation
Space Complexity: O(1) per instance — fixed schema
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Index, String, Integer, Boolean, DateTime, Text, Enum
from sqlalchemy.orm import declarative_base  # ← This is the fix
from sqlalchemy.dialects.postgresql import JSON, UUID
import uuid
import enum

Base = declarative_base()

def get_utc_now():
    """Get current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


class AlertStatus(str, enum.Enum):
    """Status of an alert record."""
    PENDING = "pending"           # Created, not yet notified
    NOTIFIED = "notified"         # Notification sent
    ACKNOWLEDGED = "acknowledged" # User has seen it
    RESOLVED = "resolved"         # Action taken
    FAILED = "failed"             # Notification failed


class AlertConfig(Base):
    """
    User notification preferences.
    
    Stores how each user wants to be notified about eligible cases.
    """
    __tablename__ = "alert_configs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User identifier (from Member 4's trust layer)
    user_id = Column(String(255), nullable=False, unique=True, index=True)
    
    # Notification preferences
    email_enabled = Column(Boolean, default=True)
    email_address = Column(String(255), nullable=True)
    
    sms_enabled = Column(Boolean, default=False)
    sms_number = Column(String(20), nullable=True)
    
    # Notification frequency
    notify_immediately = Column(Boolean, default=True)  # Alert as soon as eligible
    digest_enabled = Column(Boolean, default=False)     # Daily digest
    digest_hour = Column(Integer, default=9)            # Hour for daily digest (0-23)
    
    # Metadata
    created_at = Column(DateTime, default=get_utc_now, nullable=False)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)
    
    def __repr__(self):
        return f"<AlertConfig user_id={self.user_id} email={self.email_enabled}>"


class Alert(Base):
    """
    Alert record for eligible cases.
    
    Created when a case becomes eligible_now.
    One alert per case (no duplicates).
    """
    __tablename__ = "alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Case reference (foreign key to Member 1's cases table)
    case_id = Column(String(255), nullable=False, unique=True, index=True)
    
    # Prisoner reference (for convenience)
    prisoner_id = Column(String(255), nullable=False, index=True)
    
    # State & District (for filtering)
    state = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=False, index=True)
    
    # Eligibility details
    offense_category = Column(String(100), nullable=False)
    max_sentence_months = Column(Integer, nullable=False)
    custody_start_date = Column(DateTime, nullable=False)
    
    # Eligibility criterion met
    eligibility_reason = Column(String(255), nullable=False)  # e.g., "served_50_percent"
    date_became_eligible = Column(DateTime, default=get_utc_now, nullable=False)
    
    # Alert status
    status = Column(String(50), default=AlertStatus.PENDING.value, nullable=False, index=True)
    
    # Notification tracking
    notified_users = Column(JSON, default=list)  # List of user_ids notified
    last_notified_at = Column(DateTime, nullable=True)
    notification_attempts = Column(Integer, default=0)
    last_notification_error = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=get_utc_now, nullable=False, index=True)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)
    
    # Audit logging
    created_by = Column(String(255), default="system", nullable=False)  # "system" or user_id

    __table_args__ = (
        Index('idx_case_id', 'case_id'),
        Index('idx_status', 'status'),
        Index('idx_state_district', 'state', 'district'),
        Index('idx_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Alert case_id={self.case_id} status={self.status}>"
    
    def mark_notified(self, user_id: str):
        """
        Mark alert as notified to a specific user.
        
        Time Complexity: O(n) where n = number of already-notified users
        Space Complexity: O(1) — modifying existing list
        """
        if user_id not in self.notified_users:
            self.notified_users.append(user_id)
        self.last_notified_at = get_utc_now()
        self.status = AlertStatus.NOTIFIED.value