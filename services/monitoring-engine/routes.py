from fastapi import APIRouter
from scheduler import scan_all_cases
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared_schemas'))
from audit_client import log_action
from config import TRUST_SERVICE_URL

router = APIRouter()
PENDING_ALERTS = []


@router.post("/api/v1/alerts/config")
def alerts_config(payload: dict):
    return {"success": True, "data": payload, "error": None}


@router.get("/api/v1/alerts/pending")
def alerts_pending():
    return {"success": True, "data": PENDING_ALERTS, "error": None}


@router.get("/api/v1/alerts/scan")
def trigger_scan():
    # In production this is called by a Celery beat schedule, not a user.
    demo_case_ids = ["case-001", "case-002"]
    new_alerts = scan_all_cases(demo_case_ids, "legalaid@example.org")
    PENDING_ALERTS.extend(new_alerts)
    for alert in new_alerts:
        log_action(TRUST_SERVICE_URL, alert["case_id"], "system", "system",
                   "alert_sent", alert)
    return {"success": True, "data": {"new_alerts": len(new_alerts)}, "error": None}
