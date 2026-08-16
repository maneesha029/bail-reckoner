from fastapi import APIRouter
from logic import get_procedural_requirements, check_bond_waiver

router = APIRouter()


@router.post("/api/v1/procedural/requirements")
def procedural_requirements(payload: dict):
    case_id = payload["case_id"]
    result = get_procedural_requirements(case_id, "general")
    return {"success": True, "data": result, "error": None}


@router.post("/api/v1/bond-waiver/check")
def bond_waiver_check(payload: dict):
    case_id = payload["case_id"]
    hardship = payload.get("hardship_indicators", {})
    result = check_bond_waiver(case_id, hardship)
    return {"success": True, "data": result, "error": None}
