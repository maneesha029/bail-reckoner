# bail-reckoner/services/monitoring-engine/seed_test_data.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
from config import config
from models import AlertConfig, Alert, AlertStatus

def seed_test_data():
    """Seed test data into database."""
    engine = create_engine(config.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # ✅ ALWAYS clear existing data first (idempotent seeding)
        print("Clearing old data...")
        db.query(Alert).delete()
        db.query(AlertConfig).delete()
        db.commit()
        print("✓ Cleared old data")
        
        # Create test users
        users = [
            AlertConfig(
                user_id="user-001",
                email_enabled=True,
                email_address="user1@example.com",
                sms_enabled=False,
                sms_number=None,
                notify_immediately=True,
                digest_enabled=False,
                digest_hour=9
            ),
            AlertConfig(
                user_id="user-002",
                email_enabled=False,
                email_address=None,
                sms_enabled=True,
                sms_number="+919876543210",
                notify_immediately=False,
                digest_enabled=True,
                digest_hour=9
            )
        ]
        
        for user in users:
            db.add(user)
        
        # Create test alerts
        alerts = [
            Alert(
                case_id="case-001",
                prisoner_id="PRIS-2026-00001",
                state="Maharashtra",
                district="Mumbai",
                offense_category="crimes_against_women",
                max_sentence_months=36,
                custody_start_date=datetime(2024, 6, 15, tzinfo=timezone.utc),
                eligibility_reason="served_50_percent",
                date_became_eligible=datetime.now(timezone.utc),
                status=AlertStatus.PENDING.value,
                created_by="system"
            ),
            Alert(
                case_id="case-002",
                prisoner_id="PRIS-2026-00002",
                state="Karnataka",
                district="Bengaluru",
                offense_category="economic_offences",
                max_sentence_months=84,
                custody_start_date=datetime(2023, 12, 1, tzinfo=timezone.utc),
                eligibility_reason="served_50_percent",
                date_became_eligible=datetime.now(timezone.utc),
                status=AlertStatus.PENDING.value,
                created_by="system"
            )
        ]
        
        for alert in alerts:
            db.add(alert)
        
        db.commit()
        print(f"✓ Seeded {len(users)} users and {len(alerts)} alerts")
        print(f"\nTest data ready:")
        print(f"  Users: user-001, user-002")
        print(f"  Cases: case-001, case-002")
    
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    
    finally:
        db.close()

if __name__ == "__main__":
    seed_test_data()