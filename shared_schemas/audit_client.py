"""
Shared audit-logging helper. Every service that performs a loggable
action (eligibility check, precedent search, procedural check, bond
waiver check, alert sent, override) imports this and calls log_action()
once, right before returning its response.
"""
import requests
from datetime import datetime


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
    try:
        resp = requests.post(f"{trust_service_url}/api/v1/audit/log",
                              json=payload, timeout=3)
        return resp.json()
    except Exception as e:
        print(f"[audit-log WARNING] failed to log action: {e}")
        return None
