import pytest
from fastapi.testclient import TestClient
from main import app
from database import init_db, SessionLocal
from sqlalchemy import text
from models import User, AuditLog
from auth import get_password_hash
import uuid

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_db():
    init_db()
    db = SessionLocal()
    # Clean up
    db.execute(text("TRUNCATE TABLE audit_logs;"))
    db.query(User).delete()
    
    # Add a user
    user_id = uuid.uuid4()
    u = User(
        user_id=user_id,
        username="test_admin",
        password_hash=get_password_hash("password123"),
        role="admin"
    )
    db.add(u)
    db.commit()
    db.close()
    
    yield {"user_id": str(user_id)}
    
    db = SessionLocal()
    db.execute(text("TRUNCATE TABLE audit_logs;"))
    db.query(User).delete()
    db.commit()
    db.close()


def test_login_success(setup_db):
    response = client.post("/api/v1/auth/login", json={
        "username": "test_admin",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["role"] == "admin"

def test_login_invalid_password(setup_db):
    response = client.post("/api/v1/auth/login", json={
        "username": "test_admin",
        "password": "wrong"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "AUTH_FAILED"

def test_audit_log_flow(setup_db):
    # Get token
    response = client.post("/api/v1/auth/login", json={
        "username": "test_admin",
        "password": "password123"
    })
    token = response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create an audit log
    payload = {
        "case_id": "case-999",
        "actor_user_id": setup_db["user_id"],
        "actor_role": "admin",
        "action_type": "eligibility_check",
        "action_payload": {"notes": "test"}
    }
    log_res = client.post("/api/v1/audit/log", json=payload, headers=headers)
    assert log_res.status_code == 200
    log_data = log_res.json()
    assert log_data["success"] is True
    
    # Get audit logs
    get_res = client.get("/api/v1/audit/logs/case-999", headers=headers)
    assert get_res.status_code == 200
    get_data = get_res.json()
    assert get_data["success"] is True
    assert len(get_data["data"]) == 1
    assert get_data["data"][0]["action_type"] == "eligibility_check"

def test_audit_log_requires_auth():
    payload = {
        "case_id": "case-999",
        "actor_user_id": "u1",
        "actor_role": "admin",
        "action_type": "eligibility_check",
        "action_payload": {}
    }
    res = client.post("/api/v1/audit/log", json=payload)
    # unauthorized
    assert res.status_code == 401

def test_rate_limiting():
    # Attempt many logins quickly
    for _ in range(5):
        client.post("/api/v1/auth/login", json={"username": "test_admin", "password": "wrong"})
    
    # 6th should fail with 429
    res = client.post("/api/v1/auth/login", json={"username": "test_admin", "password": "wrong"})
    assert res.status_code == 429
