import time
import jwt
from fastapi.testclient import TestClient
from main import app
from config import JWT_SECRET

client = TestClient(app)


def make_token(role="judge", exp_delta=3600):
    payload = {"user_id": "u1", "role": role, "exp": time.time() + exp_delta}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def test_request_without_token_is_rejected():
    resp = client.get("/api/v1/eligibility/check")
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "MISSING_TOKEN"


def test_request_with_invalid_token_is_rejected():
    resp = client.get("/api/v1/eligibility/check", headers={"Authorization": "Bearer garbage"})
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "INVALID_TOKEN"


def test_request_with_expired_token_is_rejected():
    token = make_token(exp_delta=-10)
    resp = client.get("/api/v1/eligibility/check", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "TOKEN_EXPIRED"


def test_login_route_does_not_require_a_token():
    resp = client.post("/api/v1/auth/login", json={"username": "x", "password": "y"})
    assert resp.status_code == 200
    assert resp.json()["error"]["code"] != "MISSING_TOKEN"


def test_valid_token_is_accepted_and_passed_through():
    token = make_token()
    resp = client.get("/api/v1/eligibility/check", headers={"Authorization": f"Bearer {token}"})
    # Auth passes -> gateway tries to reach a service that isn't running
    # in this test, so we expect SERVICE_UNAVAILABLE, not a 401.
    assert resp.status_code == 200
    assert resp.json()["error"]["code"] == "SERVICE_UNAVAILABLE"