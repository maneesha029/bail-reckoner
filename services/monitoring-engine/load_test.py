# Create: bail-reckoner/services/monitoring-engine/load_test.py

import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import config
from models import Alert, AlertStatus
from datetime import datetime, timezone

def load_test_1000_cases():
    """Load test with 1000 cases in database."""
    engine = create_engine(config.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    print("Creating 1000 test alerts...")
    start = time.time()
    
    # Create 1000 alerts
    for i in range(1000):
        alert = Alert(
            case_id=f"case-{i:05d}",
            prisoner_id=f"PRIS-{i:05d}",
            state="Test State",
            district=f"District-{i % 10}",
            offense_category="theft",
            max_sentence_months=36,
            custody_start_date=datetime(2024, 6, 15, tzinfo=timezone.utc),
            eligibility_reason="served_50_percent",
            status=AlertStatus.PENDING.value,
            created_by="system"
        )
        db.add(alert)
        
        if i % 100 == 0:
            db.commit()
    
    db.commit()
    elapsed = time.time() - start
    
    print(f"✓ Created 1000 alerts in {elapsed:.2f}s")
    
    # Test query performance
    print("Testing query performance...")
    start = time.time()
    
    pending_alerts = db.query(Alert).filter(
        Alert.status == AlertStatus.PENDING.value
    ).limit(50).all()
    
    elapsed = time.time() - start
    print(f"✓ Queried 50 alerts in {elapsed:.4f}s")
    
    # Test filtered query
    start = time.time()
    
    filtered_alerts = db.query(Alert).filter(
        Alert.status == AlertStatus.PENDING.value,
        Alert.state == "Test State"
    ).limit(50).all()
    
    elapsed = time.time() - start
    print(f"✓ Filtered query in {elapsed:.4f}s")
    
    db.close()

if __name__ == "__main__":
    load_test_1000_cases()