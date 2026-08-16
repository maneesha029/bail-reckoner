from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class AuditLog(Base):
    __tablename__ = "audit_logs"
    log_id = Column(String, primary_key=True)
    case_id = Column(String)
    actor_user_id = Column(String)
    actor_role = Column(String)
    action_type = Column(String)
    action_payload = Column(String)  # JSON-serialized
    timestamp = Column(DateTime)
    entry_hash = Column(String)
    previous_hash = Column(String)


class User(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True)
    username = Column(String, unique=True)
    password_hash = Column(String)
    role = Column(String)
