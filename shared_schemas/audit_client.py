"""
Shared audit-logging helper. Every service that performs a loggable
action (eligibility check, precedent search, procedural check, bond
waiver check, alert sent, override) imports this and calls log_action()
once, right before returning its response.

FIX: trust-access-layer's POST /api/v1/audit/log requires a valid Bearer
JWT (Depends(require_role(...))). This file previously sent NO
Authorization header at all, so every call from precedent-engine,
compliance-engine, and monitoring-engine was silently getting a 401,
caught by the try/except below, and printed as a console warning that
nobody was watching. The audit trail for those three services' actions
was simply never being written.

This now mints a short-lived internal service token (same HS256 /
JWT_SECRET the rest of the system already uses) so the call is actually
authenticated, matching the pattern eligibility-engine already used
locally in its own routes.py. Every existing caller of `log_action()`
needs zero changes - the fix is entirely inside this one function.
"""
import os
import time
import uuid
import requests
from datetime import datetime

try:
    import jwt
except ImportError:
    jwt = None  # if this prints, add `pyjwt` to that service's requirements.txt

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")

# Stable synthetic user_id so every internal/system-triggered audit entry
# from a given service is attributable to "that service", not a random
# uuid every call. trust-access-layer stores whatever role is embedded in
# THIS token as the actor_role (it ignores payload["actor_role"] for
# authenticated calls) - "admin" is in USER_ROLES, so this always passes
# the require_role() check on the audit endpoint.
_SERVICE_USER_ID = str(uuid.uuid5(uuid.NAMESPACE_DNS, "bail-reckoner-internal-service"))


def _internal_service_token() -> str | None:
    if jwt is None:
        return None
    payload = {
        "user_id": _SERVICE_USER_ID,
        "role": "admin",
        "exp": int(time.time()) + 300,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def log_action(trust_service_url: str, case_id: str, actor_user_id: str,
                actor_role: str, action_type: str, action_payload: dict) -> dict | None:
    """Best-effort audit log call. If the trust service is unreachable,
    this prints a warning and returns None rather than crashing the
    calling service - an unlogged action is bad, but a demo crashing
    because logging failed is worse. In production this should also
    write to a local retry queue, not just warn."""
    payload = {
        "case_id": case_id,
        "actor_user_id": actor_user_id,
        "actor_role": actor_role,
        "action_type": action_type,
        "action_payload": action_payload,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    headers = {}
    token = _internal_service_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        resp = requests.post(f"{trust_service_url}/api/v1/audit/log",
                              json=payload, headers=headers, timeout=3)
        if resp.status_code >= 400:
            print(f"[audit-log WARNING] trust service returned {resp.status_code}: {resp.text}")
        return resp.json()
    except Exception as e:
        print(f"[audit-log WARNING] failed to log action: {e}")
        return None