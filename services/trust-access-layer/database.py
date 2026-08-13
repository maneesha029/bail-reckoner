from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
from models import Base
import logging

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Create append-only protection trigger
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE OR REPLACE FUNCTION prevent_audit_log_modification()
            RETURNS trigger AS $$
            BEGIN
                RAISE EXCEPTION 'Audit logs are append-only. UPDATE and DELETE are prohibited.';
            END;
            $$ LANGUAGE plpgsql;
        """))
        
        # Check if trigger already exists to avoid errors on multiple init_db calls
        res = conn.execute(text("""
            SELECT tgname FROM pg_trigger WHERE tgname = 'audit_log_append_only'
        """)).fetchone()
        
        if not res:
            conn.execute(text("""
                CREATE TRIGGER audit_log_append_only
                BEFORE UPDATE OR DELETE ON audit_logs
                FOR EACH ROW EXECUTE FUNCTION prevent_audit_log_modification();
            """))
