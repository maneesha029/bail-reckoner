"""HTTP routes for precedent search and case summarization."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

# FIX: docker-compose mounts shared_schemas/audit_client.py as a single
# flat file at /app/audit_client.py (see the `volumes:` entry for this
# service) - there is no `shared_schemas` PACKAGE inside this container,
# only that one file sitting next to routes.py. The old
# `from shared_schemas.audit_client import log_action` therefore always
# failed with ModuleNotFoundError, and the fallback
# `parents[2]` path-walk assumed a directory depth that only exists on
# your local machine, not inside the container - so it crashed with
# IndexError instead, and this whole service never started.
# compliance-engine and monitoring-engine already do it this simpler way -
# this brings precedent-engine in line with them.
from audit_client import log_action

from config import TRUST_SERVICE_URL
from logic import search_precedent, summarize_case
from schemas import (
    CaseSummaryRequest,
    PrecedentSearchRequest,
    envelope,
    model_dump,
)

router = APIRouter()


def _audit(case_id: str, actor_user_id: str, actor_role: str, action_type: str, payload: dict) -> None:
    log_action(TRUST_SERVICE_URL, case_id, actor_user_id, actor_role, action_type, payload)


@router.post("/api/v1/precedent/search")
def precedent_search(payload: PrecedentSearchRequest):
    try:
        results = search_precedent(
            payload.query_context.offense_category,
            payload.query_context.discretion_factors,
        )
        _audit(payload.case_id, "system", "system", "precedent_search", {"results_count": len(results)})
        data = {
            "case_id": payload.case_id,
            "results": results,
            "disclaimer": (
                "This output surfaces relevant law and precedent only. It does not constitute "
                "a bail recommendation. Final determination rests with the presiding judicial authority."
            ),
            "retrieved_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        }
        return envelope(data)
    except Exception as exc:
        return envelope(error={"code": "PRECEDENT_SEARCH_ERROR", "message": "Precedent search is unavailable."})


@router.post("/api/v1/precedent/summarize")
def precedent_summarize(payload: CaseSummaryRequest):
    try:
        result = summarize_case(payload)
        data = model_dump(result)
        _audit(payload.case_id, "system", "system", "precedent_summarize", {"cited_sections": data["cited_sections"]})
        return envelope(data)
    except ValueError:
        return envelope(error={"code": "SUMMARY_VALIDATION_ERROR", "message": "The supplied case could not be validated."})
    except RuntimeError:
        return envelope(error={"code": "SUMMARY_UNAVAILABLE", "message": "A neutral case summary could not be generated."})
    except Exception:
        return envelope(error={"code": "SUMMARY_ERROR", "message": "Case summarization is unavailable."})