import json
from fastapi import APIRouter
from logic import get_procedural_requirements, check_bond_waiver
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared_schemas'))
from audit_client import log_action
from config import TRUST_SERVICE_URL, engine
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from models import ProceduralRequirement, BondWaiverFlag

router = APIRouter()

SessionLocal = sessionmaker(bind=engine)


# CONFIRMED with Member 1 (2026-08-13) - actual schema:
#   case_offenses(case_id, offense_act, offense_section)
#   offenses(act, section, offense_category, is_compoundable, max_sentence_months)
# joined on case_offenses.offense_act = offenses.act
#      AND case_offenses.offense_section = offenses.section
# Where a case has multiple offenses, the one with the highest
# max_sentence_months governs (same rule eligibility-engine's
# binding_charge() uses - see docs/LEGAL_VALIDATION_QUESTIONS.md #1,
# not yet legally validated).
def resolve_offense_category(case_id: str) -> str | None:
    with engine.connect() as conn:
        row = conn.execute(
            text("""
                SELECT o.offense_category
                FROM case_offenses co
                JOIN offenses o
                  ON co.offense_act = o.act
                 AND co.offense_section = o.section
                WHERE co.case_id = :case_id
                ORDER BY o.max_sentence_months DESC
                LIMIT 1
            """),
            {"case_id": case_id},
        ).fetchone()
    return row[0] if row else None


def _save_procedural_requirement(offense_category: str, result: dict) -> None:
    db = SessionLocal()
    try:
        row = db.get(ProceduralRequirement, offense_category)
        if row is None:
            row = ProceduralRequirement(id=offense_category)
            db.add(row)
        row.offense_category = offense_category
        row.bond_type = result["bond_type"]
        row.estimated_fine_amount_inr = result["estimated_fine_amount_inr"]
        row.required_documents = ", ".join(result["required_documents"])
        row.procedural_steps = json.dumps(result["procedural_steps"])
        row.governing_sections = ", ".join(result["governing_sections"])
        db.commit()
    finally:
        db.close()


def _save_bond_waiver_flag(case_id: str, result: dict) -> None:
    db = SessionLocal()
    try:
        row = db.get(BondWaiverFlag, case_id)
        if row is None:
            row = BondWaiverFlag(case_id=case_id)
            db.add(row)
        row.is_flagged = result["is_flagged_for_waiver"]
        row.confidence = result["waiver_confidence"]
        row.reasoning = result["reasoning_summary"]
        db.commit()
    finally:
        db.close()


@router.post("/api/v1/procedural/requirements")
def procedural_requirements(payload: dict):
    case_id = payload["case_id"]
    offense_category = resolve_offense_category(case_id)

    if offense_category is None:
        result = {"code": "CASE_NOT_FOUND", "message": f"No case found for case_id '{case_id}'"}
        log_action(TRUST_SERVICE_URL, case_id, payload.get("actor_user_id", "system"),
                   payload.get("actor_role", "system"), "procedural_check_failed", result)
        return {"success": False, "data": None, "error": result}

    result = get_procedural_requirements(case_id, offense_category)
    _save_procedural_requirement(offense_category, result)
    log_action(TRUST_SERVICE_URL, case_id, payload.get("actor_user_id", "system"),
               payload.get("actor_role", "system"), "procedural_check", result)
    return {"success": True, "data": result, "error": None}


@router.post("/api/v1/bond-waiver/check")
def bond_waiver_check(payload: dict):
    case_id = payload["case_id"]
    hardship = payload.get("hardship_indicators", {})
    result = check_bond_waiver(case_id, hardship)
    _save_bond_waiver_flag(case_id, result)
    log_action(TRUST_SERVICE_URL, case_id, payload.get("actor_user_id", "system"),
               payload.get("actor_role", "system"), "bond_waiver_check", result)
    return {"success": True, "data": result, "error": None}
