from fastapi import APIRouter
from datetime import datetime
from logic import search_precedent

router = APIRouter()


@router.post("/api/v1/precedent/search")
def precedent_search(payload: dict):
    case_id = payload["case_id"]
    ctx = payload.get("query_context", {})
    results = search_precedent(ctx.get("offense_category", "general"),
                                ctx.get("discretion_factors", []))
    return {"success": True, "data": {
        "case_id": case_id, "results": results,
        "disclaimer": ("This output surfaces relevant law and precedent only. "
                        "It does not constitute a bail recommendation. Final "
                        "determination rests with the presiding judicial authority."),
        "retrieved_at": datetime.utcnow().isoformat() + "Z",
    }, "error": None}
