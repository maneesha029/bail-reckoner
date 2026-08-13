from datetime import datetime, timezone
import time
import uuid
import jwt
import requests

from fastapi import APIRouter, Header, HTTPException
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, selectinload

from config import DATABASE_URL, TRUST_SERVICE_URL, TRUST_SERVICE_TOKEN, JWT_SECRET
from logic import determine_eligibility
from models import Base, CaseRecord
from schemas import EligibilityCheckRequest, EligibilityOverrideRequest

router = APIRouter()
engine_kwargs = {"pool_pre_ping": True}
if DATABASE_URL.startswith("postgresql"):
    engine_kwargs["connect_args"] = {"connect_timeout": 3}
engine = create_engine(DATABASE_URL, **engine_kwargs)


def initialize_database():
    try:
        Base.metadata.create_all(engine)
    except Exception as exc:
        # The container may start before Postgres is ready; requests will
        # report the database error, while the process remains healthy.
        print(f"[database WARNING] initialization failed: {exc}")

# Results and overrides are intentionally kept separately: an override never
# replaces the deterministic computed result.
LAST_RESULTS: dict[str, dict] = {}
OVERRIDES: dict[str, list[dict]] = {}

def log_action(
    case_id: str,
    actor_user_id: str,
    actor_role: str,
    action_type: str,
    action_payload: dict,
    authorization: str | None = None,
):
    payload = {
        "case_id": case_id,
        "actor_user_id": actor_user_id,
        "actor_role": actor_role,
        "action_type": action_type,
        "action_payload": action_payload,
        "timestamp": datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
    }

    token = authorization or (
        f"Bearer {TRUST_SERVICE_TOKEN}"
        if TRUST_SERVICE_TOKEN
        else None
    )

    headers = {"Authorization": token} if token else {}

    try:
        response = requests.post(
            f"{TRUST_SERVICE_URL}/api/v1/audit/log",
            json=payload,
            headers=headers,
            timeout=3,
        )

        if response.status_code >= 400:
            print(
                f"[audit-log WARNING] trust service returned "
                f"{response.status_code}: {response.text}"
            )
    except Exception as exc:
        print(f"[audit-log WARNING] failed to log action: {exc}")

def internal_audit_token() -> str:
    return jwt.encode(
        {
            "user_id": str(uuid.uuid5(uuid.NAMESPACE_DNS, "eligibility-engine")),
            "role": "admin",
            "exp": int(time.time()) + 300,
        },
        JWT_SECRET,
        algorithm="HS256",
    )

def envelope(data=None, error=None):
    return {"success": error is None, "data": data, "error": error}


def find_case(case_id: str):
    with Session(engine) as session:
        return session.scalar(
            select(CaseRecord)
            .options(selectinload(CaseRecord.offense_records))
            .where(CaseRecord.case_id == case_id)
        )


@router.post("/api/v1/eligibility/check")
def check_eligibility(payload: EligibilityCheckRequest):
    case = find_case(payload.case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    charges = [
        {
            "act": offense.act,
            "section": offense.section,
            "offense_category": offense.offense_category,
            "is_compoundable": offense.is_compoundable,
            "max_sentence_months": offense.max_sentence_months,
        }
        for offense in case.offense_records
    ]
    result = determine_eligibility(
        case.case_id,
        case.custody_start_date.date().isoformat(),
        bool(case.is_first_time_offender),
        charges,
    )
    LAST_RESULTS[payload.case_id] = result
    log_action(
    payload.case_id,
    "service-eligibility-engine",
    "admin",
    "eligibility_check",
    result,
    f'Bearer {internal_audit_token()}',
)
    return envelope(result)


@router.get("/api/v1/eligibility/{case_id}")
def get_eligibility(case_id: str):
    result = LAST_RESULTS.get(case_id)
    if result is None:
        raise HTTPException(status_code=404, detail="No computed eligibility result")
    return envelope(result)


@router.post("/api/v1/eligibility/override")
def override_eligibility(
    payload: EligibilityOverrideRequest,
    x_actor_role: str | None = Header(default=None),
    authorization: str | None = Header(default=None),):
    if x_actor_role not in {"legal_aid", "judge"}:
        raise HTTPException(status_code=403, detail="Only legal_aid or judge may override")
    if payload.case_id not in LAST_RESULTS:
        raise HTTPException(status_code=404, detail="No computed eligibility result")
    override = {
        "case_id": payload.case_id,
        "actor_user_id": payload.actor_user_id,
        "actor_role": x_actor_role,
        "reason": payload.reason,
        "reviewed_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
    }
    OVERRIDES.setdefault(payload.case_id, []).append(override)
    log_action(
    payload.case_id,
    payload.actor_user_id,
    x_actor_role,
    "manual_override",
    override,
    authorization,
)
    return envelope({"computed_result": LAST_RESULTS[payload.case_id],
                     "override": override})

