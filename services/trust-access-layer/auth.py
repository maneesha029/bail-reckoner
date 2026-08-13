import jwt
import time
from fastapi import Request, HTTPException, Depends
from passlib.context import CryptContext
from config import JWT_SECRET

ROLE_PERMISSIONS = {
    "judge": ["read_case", "read_precedent", "override"],
    "legal_aid": ["read_case", "read_precedent", "read_procedural", "read_bond_waiver"],
    "jail_officer": ["read_eligibility", "read_alerts"],
    "admin": ["read_case", "read_precedent", "read_procedural", "read_bond_waiver",
              "read_eligibility", "read_alerts", "override", "read_audit"],
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_token(user_id: str, role: str) -> str:
    payload = {"user_id": str(user_id), "role": role, "exp": int(time.time()) + 86400}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail={"success": False, "data": None, "error": {"code": "TOKEN_EXPIRED", "message": "Token has expired"}})
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail={"success": False, "data": None, "error": {"code": "INVALID_TOKEN", "message": "Invalid token"}})

def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail={"success": False, "data": None, "error": {"code": "UNAUTHORIZED", "message": "Missing or invalid Authorization header"}})
    
    token = auth_header.split(" ")[1]
    return decode_token(token)

def role_can(role: str, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, [])

def require_role(allowed_roles: list[str]):
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail={"success": False, "data": None, "error": {"code": "FORBIDDEN", "message": "Insufficient permissions"}}
            )
        return current_user
    return role_checker
