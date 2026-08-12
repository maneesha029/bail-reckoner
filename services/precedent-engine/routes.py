from fastapi import APIRouter
from datetime import datetime
from logic import search_precedent
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared_schemas'))
from audit_client import log_action
from config import TRUST_SERVICE_URL

router = APIRouter()


@router.post("/api/v1/precedent/search")
def precedent_search(payload: dict):
    case_id = payload["case_id"]
    ctx = payload.get("query_context", {})
    results = search_precedent(ctx.get("offense_category", "general"),
                                ctx.get("discretion_factors", []))
    log_action(TRUST_SERVICE_URL, case_id, payload.get("actor_user_id", "system"),
               payload.get("actor_role", "system"), "precedent_search", {"results_count": len(results)})
    return {"success": True, "data": {
        "case_id": case_id, "results": results,
        "disclaimer": ("This output surfaces relevant law and precedent only. "
                        "It does not constitute a bail recommendation. Final "
                        "determination rests with the presiding judicial authority."),
        "retrieved_at": datetime.utcnow().isoformat() + "Z",
    }, "error": None}
