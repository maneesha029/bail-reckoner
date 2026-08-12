from fastapi import APIRouter
from logic import get_procedural_requirements, check_bond_waiver
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared_schemas'))
from audit_client import log_action
from config import TRUST_SERVICE_URL

router = APIRouter()


@router.post("/api/v1/procedural/requirements")
def procedural_requirements(payload: dict):
    case_id = payload["case_id"]
    result = get_procedural_requirements(case_id, "general")
    log_action(TRUST_SERVICE_URL, case_id, payload.get("actor_user_id", "system"),
               payload.get("actor_role", "system"), "procedural_check", result)
    return {"success": True, "data": result, "error": None}


@router.post("/api/v1/bond-waiver/check")
def bond_waiver_check(payload: dict):
    case_id = payload["case_id"]
    hardship = payload.get("hardship_indicators", {})
    result = check_bond_waiver(case_id, hardship)
    log_action(TRUST_SERVICE_URL, case_id, payload.get("actor_user_id", "system"),
               payload.get("actor_role", "system"), "bond_waiver_check", result)
    return {"success": True, "data": result, "error": None}
