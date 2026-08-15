import json
from fastapi import APIRouter
from logic import get_procedural_requirements, check_bond_waiver
from discretion import compute_discretion_indicators
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared_schemas'))
from audit_client import log_action
from config import TRUST_SERVICE_URL, engine
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from models import ProceduralRequirement, BondWaiverFlag, DiscretionAssessment

router = APIRouter()

SessionLocal = sessionmaker(bind=engine)


# Resolve the offense category for a case through the shared
# case_offenses junction table.
#
# If a case has multiple linked offenses, use the offense with the
# highest maximum sentence as the governing offense.
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


def _save_discretion_assessment(case_id: str, result: dict) -> None:
    db = SessionLocal()
    try:
        row = db.get(DiscretionAssessment, case_id)
        if row is None:
            row = DiscretionAssessment(case_id=case_id)
            db.add(row)
        row.flight_risk_band = result["flight_risk"]["band"]
        row.flight_risk_score = result["flight_risk"]["score"]
        row.witness_influence_band = result["witness_influence_risk"]["band"]
        row.witness_influence_score = result["witness_influence_risk"]["score"]
        row.factors_present = ", ".join(
            result["flight_risk"]["factors_present"]
            + result["witness_influence_risk"]["factors_present"]
        )
        db.commit()
    finally:
        db.close()


@router.post("/api/v1/discretion/assess")
def discretion_assess(payload: dict):
    """
    Rule-based flight-risk / witness-influence indicators for the judge's
    consideration (CrPC/BNSS discretion factors). Advisory only - see
    discretion.py's docstring and the disclaimer returned in every response.
    """
    case_id = payload["case_id"]
    indicators = payload.get("indicators", {})
    result = compute_discretion_indicators(case_id, indicators)
    _save_discretion_assessment(case_id, result)
    log_action(TRUST_SERVICE_URL, case_id, payload.get("actor_user_id", "system"),
               payload.get("actor_role", "system"), "discretion_assessment", result)
    return {"success": True, "data": result, "error": None}
