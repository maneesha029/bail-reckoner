from sqlalchemy import Column, String, DateTime, Index
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import JSONB, UUID

Base = declarative_base()


class AuditLog(Base):
    __tablename__ = "audit_logs"
    log_id = Column(UUID(as_uuid=True), primary_key=True)
    case_id = Column(String, nullable=False)
    actor_user_id = Column(UUID(as_uuid=True), nullable=False)
    actor_role = Column(String, nullable=False)
    action_type = Column(String, nullable=False)
    action_payload = Column(JSONB, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    entry_hash = Column(String, nullable=False)
    previous_hash = Column(String, nullable=False)

    __table_args__ = (
        Index("ix_audit_logs_case_id", "case_id"),
        Index("ix_audit_logs_timestamp", "timestamp"),
        Index("ix_audit_logs_actor_user_id", "actor_user_id"),
    )


class User(Base):
    __tablename__ = "users"
    user_id = Column(UUID(as_uuid=True), primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)
