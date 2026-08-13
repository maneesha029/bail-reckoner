import sys
from sqlalchemy import text
from database import SessionLocal, init_db
from models import AuditLog
from hashing import compute_entry_hash, verify_chain
from datetime import datetime, timezone
import uuid

def run_demonstration():
    print("--- Trust & Access Layer Tamper Demonstration ---")
    init_db()
    db = SessionLocal()
    
    # Cleanup for demo
    db.query(AuditLog).delete()
    db.commit()
    
    try:
        print("\n1. Inserting valid audit records...")
        prev = "0" * 64
        entries = []
        for i in range(3):
            record = {
                "log_id": str(uuid.uuid4()),
                "case_id": "c-demo",
                "actor_user_id": str(uuid.uuid4()),
                "actor_role": "admin",
                "action_type": "eligibility_check",
                "action_payload": {"step": i},
                "timestamp": datetime.now(timezone.utc).replace(tzinfo=None).strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"
            }
            h = compute_entry_hash(record, prev)
            
            al = AuditLog(
                **record,
                entry_hash=h,
                previous_hash=prev
            )
            db.add(al)
            db.commit()
            
            record["entry_hash"] = h
            record["previous_hash"] = prev
            entries.append(record)
            prev = h
            
        print("Records inserted.")
        
        # Verify chain from DB
        db_records = [
            {
                "log_id": str(r.log_id),
                "case_id": r.case_id,
                "actor_user_id": str(r.actor_user_id),
                "actor_role": r.actor_role,
                "action_type": r.action_type,
                "action_payload": r.action_payload,
                "timestamp": r.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z" if r.timestamp else None,
                "entry_hash": r.entry_hash,
                "previous_hash": r.previous_hash
            }
            for r in db.query(AuditLog).order_by(AuditLog.timestamp.asc()).all()
        ]
        
        is_valid = verify_chain(db_records)
        print("Chain valid before tampering:", is_valid)
        
        target_log_id = db_records[1]["log_id"]
        
        print("\n2. Attempting normal UPDATE (should be blocked by append-only protection)...")
        try:
            db.execute(text("UPDATE audit_logs SET action_type = 'TAMPERED' WHERE log_id = :id"), {"id": target_log_id})
            db.commit()
            print("WARNING: UPDATE succeeded! Trigger missing?")
        except Exception as e:
            db.rollback()
            print(f"UPDATE correctly blocked. Reason: {e}")
            
        print("\n3. Dropping trigger temporarily to demonstrate detection...")
        db.execute(text("DROP TRIGGER IF EXISTS audit_log_append_only ON audit_logs;"))
        db.commit()
        
        print("Tampering with record...")
        db.execute(text("UPDATE audit_logs SET action_type = 'TAMPERED' WHERE log_id = :id"), {"id": target_log_id})
        db.commit()
        
        print("Re-creating trigger...")
        db.execute(text("""
            CREATE TRIGGER audit_log_append_only
            BEFORE UPDATE OR DELETE ON audit_logs
            FOR EACH ROW EXECUTE FUNCTION prevent_audit_log_modification();
        """))
        db.commit()
        
        # Verify chain again
        db_records_after = [
            {
                "log_id": str(r.log_id),
                "case_id": r.case_id,
                "actor_user_id": str(r.actor_user_id),
                "actor_role": r.actor_role,
                "action_type": r.action_type,
                "action_payload": r.action_payload,
                "timestamp": r.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z" if r.timestamp else None,
                "entry_hash": r.entry_hash,
                "previous_hash": r.previous_hash
            }
            for r in db.query(AuditLog).order_by(AuditLog.timestamp.asc()).all()
        ]
        
        is_valid_after = verify_chain(db_records_after)
        print("Chain valid after tampering: ", is_valid_after)
        
        if is_valid and not is_valid_after:
            print("Tamper detection confirmed working.")
        else:
            print("Tamper detection FAILED")
            
    finally:
        db.close()

if __name__ == "__main__":
    run_demonstration()
