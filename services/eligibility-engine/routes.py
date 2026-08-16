from fastapi import APIRouter
from logic import determine_eligibility

router = APIRouter()

# TODO: replace this in-memory placeholder with a real DB lookup by case_id
MOCK_CASES = {}


@router.post("/api/v1/eligibility/check")
def check_eligibility(payload: dict):
    case_id = payload["case_id"]
    case = MOCK_CASES.get(case_id, {
        "custody_start_date": "2025-06-01", "is_first_time_offender": False,
        "charges": [{"max_sentence_months": 24}],
    })
    result = determine_eligibility(case_id, case["custody_start_date"],
                                    case["is_first_time_offender"], case["charges"])
    return {"success": True, "data": result, "error": None}


@router.get("/api/v1/eligibility/{case_id}")
def get_eligibility(case_id: str):
    return check_eligibility({"case_id": case_id})


@router.post("/api/v1/eligibility/override")
def override_eligibility(payload: dict):
    return {"success": True, "data": {"case_id": payload.get("case_id"),
            "overridden": True, "reason": payload.get("reason")}, "error": None}
