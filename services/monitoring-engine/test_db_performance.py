"""
Database performance testing for Phase 3 optimization
"""

import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import config
from models import Alert, AlertStatus, AlertConfig

def test_database_performance():
    """Test database query performance."""
    engine = create_engine(config.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    print("\n" + "="*80)
    print("DATABASE PERFORMANCE TESTING (Phase 3)")
    print("="*80 + "\n")
    
    # Test 1: Simple SELECT (50 rows)
    print("Test 1: Simple SELECT (50 rows)")
    start = time.time()
    alerts = db.query(Alert).filter(
        Alert.status == AlertStatus.PENDING.value
    ).limit(50).all()
    elapsed = time.time() - start
    
    print(f"  ✓ Time: {elapsed*1000:.2f}ms")
    print(f"  ✓ Records: {len(alerts)}")
    assert elapsed < 0.1, f"Query too slow: {elapsed*1000:.2f}ms (target: <100ms)"
    print("  ✅ PASS\n")
    
    # Test 2: Filtered SELECT (state)
    print("Test 2: Filtered SELECT by state (Maharashtra)")
    start = time.time()
    alerts = db.query(Alert).filter(
        Alert.status == AlertStatus.PENDING.value,
        Alert.state == "Maharashtra"
    ).limit(50).all()
    elapsed = time.time() - start
    
    print(f"  ✓ Time: {elapsed*1000:.2f}ms")
    print(f"  ✓ Records: {len(alerts)}")
    assert elapsed < 0.1, f"Query too slow: {elapsed*1000:.2f}ms (target: <100ms)"
    print("  ✅ PASS\n")
    
    # Test 3: Filtered SELECT (state + district)
    print("Test 3: Filtered SELECT by state + district")
    start = time.time()
    alerts = db.query(Alert).filter(
        Alert.status == AlertStatus.PENDING.value,
        Alert.state == "Maharashtra",
        Alert.district == "Mumbai"
    ).limit(50).all()
    elapsed = time.time() - start
    
    print(f"  ✓ Time: {elapsed*1000:.2f}ms")
    print(f"  ✓ Records: {len(alerts)}")
    assert elapsed < 0.1, f"Query too slow: {elapsed*1000:.2f}ms (target: <100ms)"
    print("  ✅ PASS\n")
    
    # Test 4: COUNT query
    print("Test 4: COUNT query (pending alerts)")
    start = time.time()
    count = db.query(Alert).filter(
        Alert.status == AlertStatus.PENDING.value
    ).count()
    elapsed = time.time() - start
    
    print(f"  ✓ Time: {elapsed*1000:.2f}ms")
    print(f"  ✓ Count: {count}")
    assert elapsed < 0.1, f"Query too slow: {elapsed*1000:.2f}ms (target: <100ms)"
    print("  ✅ PASS\n")
    
    # Test 5: JOIN query (alerts + configs)
    print("Test 5: JOIN query (alerts + alert_configs)")
    start = time.time()
    results = db.query(Alert, AlertConfig).outerjoin(
        AlertConfig, Alert.id == AlertConfig.id
    ).limit(50).all()
    elapsed = time.time() - start
    
    print(f"  ✓ Time: {elapsed*1000:.2f}ms")
    print(f"  ✓ Records: {len(results)}")
    assert elapsed < 0.2, f"Query too slow: {elapsed*1000:.2f}ms (target: <200ms)"
    print("  ✅ PASS\n")
    
    # Test 6: Pagination performance
    print("Test 6: Pagination (offset + limit)")
    offsets = [0, 50, 100, 150]
    for offset in offsets:
        start = time.time()
        alerts = db.query(Alert).filter(
            Alert.status == AlertStatus.PENDING.value
        ).offset(offset).limit(50).all()
        elapsed = time.time() - start
        
        print(f"  ✓ Offset {offset}: {elapsed*1000:.2f}ms")
        assert elapsed < 0.1, f"Pagination too slow at offset {offset}"
    print("  ✅ PASS\n")
    
    db.close()
    
    print("="*80)
    print("✅ ALL DATABASE PERFORMANCE TESTS PASSED")
    print("="*80)
    print("\nPerformance Summary:")
    print("  • Simple SELECT: <100ms ✓")
    print("  • Filtered SELECT: <100ms ✓")
    print("  • COUNT query: <100ms ✓")
    print("  • JOIN query: <200ms ✓")
    print("  • Pagination: <100ms per page ✓")

if __name__ == "__main__":
    try:
        test_database_performance()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nMake sure PostgreSQL is running and database is initialized:")
        print("  python3 seed_test_data.py")
        exit(1)