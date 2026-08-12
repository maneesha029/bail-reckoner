from fastapi import APIRouter
from datetime import datetime
import uuid
from auth import create_token
from hashing import compute_entry_hash

router = APIRouter()

# TODO: replace with real DB-backed user store and audit log persistence
MOCK_USERS = {"judge1": {"password": "demo", "role": "judge", "user_id": "u1"}}
AUDIT_CHAIN = []  # in-memory placeholder; real impl uses audit_logs table


@router.post("/api/v1/auth/login")
def login(payload: dict):
    user = MOCK_USERS.get(payload.get("username"))
    if not user or user["password"] != payload.get("password"):
        return {"success": False, "data": None,
                "error": {"code": "AUTH_FAILED", "message": "Invalid credentials"}}
    token = create_token(user["user_id"], user["role"])
    return {"success": True, "data": {"access_token": token, "role": user["role"],
             "user_id": user["user_id"]}, "error": None}


@router.post("/api/v1/audit/log")
def audit_log(payload: dict):
    previous_hash = AUDIT_CHAIN[-1]["entry_hash"] if AUDIT_CHAIN else "0" * 64
    entry_hash = compute_entry_hash(payload, previous_hash)
    entry = {"log_id": str(uuid.uuid4()), "payload": payload,
              "entry_hash": entry_hash, "previous_hash": previous_hash,
              "timestamp": datetime.utcnow().isoformat() + "Z"}
    AUDIT_CHAIN.append(entry)
    return {"success": True, "data": {"log_id": entry["log_id"],
             "entry_hash": entry_hash, "previous_hash": previous_hash}, "error": None}


@router.get("/api/v1/audit/logs/{case_id}")
def get_audit_logs(case_id: str):
    matching = [e for e in AUDIT_CHAIN if e["payload"].get("case_id") == case_id]
    return {"success": True, "data": matching, "error": None}
