import pytest
import time
from fastapi.testclient import TestClient
import jwt

from main import app
from auth import create_token, decode_token, role_can
from config import JWT_SECRET
from fastapi import HTTPException

client = TestClient(app)

def test_jwt_creation_and_decoding():
    token = create_token("user-123", "judge")
    decoded = decode_token(token)
    assert decoded["user_id"] == "user-123"
    assert decoded["role"] == "judge"
    assert "exp" in decoded

def test_jwt_expired():
    # create a token that is already expired
    payload = {"user_id": "user-123", "role": "judge", "exp": int(time.time()) - 100}
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    with pytest.raises(HTTPException) as exc_info:
        decode_token(token)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail["error"]["code"] == "TOKEN_EXPIRED"

def test_jwt_invalid_signature():
    token = jwt.encode({"user_id": "u1"}, "wrong-secret", algorithm="HS256")
    with pytest.raises(HTTPException) as exc_info:
        decode_token(token)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail["error"]["code"] == "INVALID_TOKEN"

def test_role_permissions():
    assert role_can("judge", "override") is True
    assert role_can("jail_officer", "override") is False
    assert role_can("admin", "read_audit") is True
    assert role_can("legal_aid", "read_procedural") is True
    assert role_can("legal_aid", "override") is False
