import pytest
import threading
from datetime import datetime, timezone
import uuid
import json

from hashing import compute_entry_hash, verify_chain

def test_compute_entry_hash_ignores_hashes():
    record = {
        "log_id": "123",
        "case_id": "c1",
        "actor_user_id": "u1",
        "actor_role": "judge",
        "action_type": "manual_override",
        "action_payload": {"reason": "test"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "entry_hash": "should_be_ignored",
        "previous_hash": "also_ignored"
    }
    
    hash1 = compute_entry_hash(record, "prev123")
    
    # Change the ignored fields, hash should be the same
    record["entry_hash"] = "changed"
    record["previous_hash"] = "changed2"
    hash2 = compute_entry_hash(record, "prev123")
    
    assert hash1 == hash2

def test_verify_chain_valid():
    prev = "0" * 64
    entries = []
    for i in range(3):
        record = {
            "log_id": str(i),
            "case_id": "c1",
            "actor_user_id": "u1",
            "actor_role": "judge",
            "action_type": "manual_override",
            "action_payload": {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        h = compute_entry_hash(record, prev)
        record["entry_hash"] = h
        record["previous_hash"] = prev
        entries.append(record)
        prev = h
        
    assert verify_chain(entries) is True

def test_verify_chain_tampered():
    prev = "0" * 64
    entries = []
    for i in range(3):
        record = {
            "log_id": str(i),
            "case_id": "c1",
            "actor_user_id": "u1",
            "actor_role": "judge",
            "action_type": "manual_override",
            "action_payload": {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        h = compute_entry_hash(record, prev)
        record["entry_hash"] = h
        record["previous_hash"] = prev
        entries.append(record)
        prev = h
        
    # Tamper with the middle entry
    entries[1]["action_type"] = "alert_sent"
    assert verify_chain(entries) is False

import threading
from database import SessionLocal, init_db
from sqlalchemy import text
from models import AuditLog, User
from hashing import verify_chain
from fastapi.testclient import TestClient
from main import app
from auth import get_password_hash

client = TestClient(app)

def test_concurrent_audit_writes():
    init_db()
    db = SessionLocal()
    db.execute(text("TRUNCATE TABLE audit_logs;"))
    db.query(User).delete()
    
    u_id = uuid.uuid4()
    u = User(user_id=u_id, username='conc_user', password_hash=get_password_hash('pass'), role='admin')
    db.add(u)
    db.commit()
    
    res = client.post('/api/v1/auth/login', json={'username': 'conc_user', 'password': 'pass'})
    token = res.json()['data']['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    def make_request(i):
        payload = {
            'case_id': 'conc-case',
            'action_type': 'eligibility_check',
            'action_payload': {'thread': i}
        }
        res = client.post('/api/v1/audit/log', json=payload, headers=headers)
        assert res.status_code == 200
        assert res.json()['success'] is True
        
    threads = []
    for i in range(10):
        t = threading.Thread(target=make_request, args=(i,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    # Verify chain
    db_records = [
        {
            'log_id': str(r.log_id),
            'case_id': r.case_id,
            'actor_user_id': str(r.actor_user_id),
            'actor_role': r.actor_role,
            'action_type': r.action_type,
            'action_payload': r.action_payload,
            'timestamp': r.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z" if r.timestamp else None,
            'entry_hash': r.entry_hash,
            'previous_hash': r.previous_hash
        }
        for r in db.query(AuditLog).order_by(AuditLog.timestamp.asc()).all()
    ]
    
    assert len(db_records) == 10
    assert verify_chain(db_records) is True
    
    # Verify no two records share the same previous_hash
    prev_hashes = [r['previous_hash'] for r in db_records]
    assert len(set(prev_hashes)) == len(prev_hashes)
    db.close()