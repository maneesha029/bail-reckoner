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


# NOTE (2026-08-13, corrected): the earlier version of this function
# queried a `case_offenses` junction table, which does not exist in the
# real schema and caused psycopg2.errors.UndefinedTable in Docker.
#
# Confirmed with Member 1: the actual shared schema has only `cases`
# and `offenses` (a standalone offense-definition catalog: act, section,
# offense_category, is_compoundable, max_sentence_months). Neither table
# has a column linking a specific case_id to a specific offense - there
# is currently no key to join on. This is unchanged from spec section 6,
# which calls this "your single highest-risk integration point - talk
# to [Member 1] directly before finalizing."
#
# Until Member 1 exposes a real case->offense link (e.g. a case_id
# column on `offenses`, or a join table they own), this function only
# confirms the case exists in `cases` and returns the safe default
# offense_category ("general"), matching the original scaffold's
# fallback behavior instead of guessing at a table that isn't there.
def resolve_offense_category(case_id: str) -> str | None:
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT case_id FROM cases WHERE case_id = :case_id"),
            {"case_id": case_id},
        ).fetchone()
    if row is None:
        return None
    return "general"


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
