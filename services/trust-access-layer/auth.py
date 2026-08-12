import jwt
import time
from config import JWT_SECRET

ROLE_PERMISSIONS = {
    "judge": ["read_case", "read_precedent", "override"],
    "legal_aid": ["read_case", "read_precedent", "read_procedural", "read_bond_waiver"],
    "jail_officer": ["read_eligibility", "read_alerts"],
    "admin": ["read_case", "read_precedent", "read_procedural", "read_bond_waiver",
              "read_eligibility", "read_alerts", "override", "read_audit"],
}


def create_token(user_id: str, role: str) -> str:
    payload = {"user_id": user_id, "role": role, "exp": time.time() + 86400}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])


def role_can(role: str, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, [])
