from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Alert(Base):
    __tablename__ = "alerts"
    alert_id = Column(String, primary_key=True)
    case_id = Column(String)
    triggered_at = Column(DateTime)
    reason = Column(String)
    is_acknowledged = Column(Boolean, default=False)


class AlertConfigRow(Base):
    __tablename__ = "alert_configs"
    recipient_user_id = Column(String, primary_key=True)
    notify_via = Column(String)
    scan_frequency = Column(String)
