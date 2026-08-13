from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timezone
import uuid

from auth import create_token, verify_password, get_current_user, require_role
from hashing import compute_entry_hash
from database import get_db
from models import User, AuditLog
USER_ROLES = ["judge", "legal_aid", "jail_officer", "admin"]

# For rate limiting, we import limiter from main (we will define it there and pass it)
# To avoid circular import, we can use request.app.state.limiter if we want, or just define it in a deps module.
# Let's import limiter from a new dependencies or just instantiate a limiter here if slowapi allows, 
# but slowapi standard is in main.py. We can import it from slowapi directly or set it up in main.py.
# Actually, slowapi requires a Limiter object.
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

router = APIRouter()

@router.post("/api/v1/auth/login")
@limiter.limit("5/minute")
def login(request: Request, payload: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.get("username")).first()
    if not user or not verify_password(payload.get("password", ""), user.password_hash):
        return {"success": False, "data": None,
                "error": {"code": "AUTH_FAILED", "message": "Invalid credentials"}}
    token = create_token(str(user.user_id), user.role)
    return {"success": True, "data": {"access_token": token, "role": user.role,
             "user_id": str(user.user_id)}, "error": None}


@router.post("/api/v1/audit/log")
def audit_log(payload: dict, db: Session = Depends(get_db), current_user: dict = Depends(require_role(USER_ROLES))):
    # This endpoint is internal but we enforce authentication so we know the actor is authorized.
    # Alternatively, the spec says Members 1, 2, 3, 5 call this. They could use an admin token or their own service tokens.
    # The requirement: "Do not silently trust actor_role from an unauthenticated request." 
    # Here, we validate they have a valid token with a valid role.
    
    # We must use a transaction and advisory lock to prevent concurrent insert race conditions breaking the chain
    # We use a hardcoded lock ID for the audit chain, e.g., 12345
    LOCK_ID = 123456789
    
    try:
        # Acquire advisory lock for this transaction
        db.execute(text("SELECT pg_advisory_xact_lock(:lock_id)"), {"lock_id": LOCK_ID})
        
        # Fetch latest entry
        latest = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).first()
        previous_hash = latest.entry_hash if latest else "0" * 64
        
        # Prepare record
        log_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).replace(tzinfo=None).strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"
        
        action_type = payload.get("action_type")
        valid_actions = ["eligibility_check", "precedent_search", "procedural_check", "bond_waiver_check", "alert_sent", "manual_override"]
        if action_type not in valid_actions:
            return {"success": False, "data": None, "error": {"code": "INVALID_ACTION", "message": "Invalid action_type"}}
        
        record_dict = {
            "log_id": log_id,
            "case_id": payload.get("case_id"),
            "actor_user_id": str(current_user["user_id"]),
            "actor_role": current_user["role"],
            "action_type": action_type,
            "action_payload": payload.get("action_payload"),
            "timestamp": timestamp
        }
        
        # Compute hash
        entry_hash = compute_entry_hash(record_dict, previous_hash)
        
        # Insert
        entry = AuditLog(
            **record_dict,
            entry_hash=entry_hash,
            previous_hash=previous_hash
        )
        db.add(entry)
        db.commit()
        
        return {"success": True, "data": {"log_id": log_id,
                 "entry_hash": entry_hash, "previous_hash": previous_hash}, "error": None}
    except Exception as e:
        db.rollback()
        # In a real app we'd log `e`
        return {"success": False, "data": None, "error": {"code": "INTERNAL_ERROR", "message": str(e)}}


@router.get("/api/v1/audit/logs/{case_id}")
def get_audit_logs(case_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    logs = db.query(AuditLog).filter(AuditLog.case_id == case_id).order_by(AuditLog.timestamp.asc()).all()
    # Serialize correctly
    data = []
    for log in logs:
        data.append({
            "log_id": str(log.log_id),
            "case_id": log.case_id,
            "actor_user_id": str(log.actor_user_id),
            "actor_role": log.actor_role,
            "action_type": log.action_type,
            "action_payload": log.action_payload,
            "timestamp": log.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z" if log.timestamp else None,
            "entry_hash": log.entry_hash,
            "previous_hash": log.previous_hash
        })
    return {"success": True, "data": data, "error": None}
