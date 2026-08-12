import requests
from datetime import datetime
from config import ELIGIBILITY_SERVICE_URL
from notify import send_email_alert

ALREADY_FLAGGED = set()  # in-memory placeholder; real impl uses DB


def scan_all_cases(case_ids: list[str], recipient_email: str) -> list[dict]:
    """Runs Member 1's eligibility check across every under-trial case;
    creates an alert for any newly-eligible case not already flagged."""
    new_alerts = []
    for case_id in case_ids:
        try:
            resp = requests.post(f"{ELIGIBILITY_SERVICE_URL}/api/v1/eligibility/check",
                                  json={"case_id": case_id}, timeout=5)
            result = resp.json()["data"]
        except Exception as e:
            continue
        if result["eligibility_status"] in ("eligible_now", "eligible_first_time_offender_rule"):
            if case_id not in ALREADY_FLAGGED:
                ALREADY_FLAGGED.add(case_id)
                alert = {"case_id": case_id,
                          "triggered_at": datetime.utcnow().isoformat() + "Z",
                          "reason": f"eligibility_status changed to {result['eligibility_status']}",
                          "is_acknowledged": False}
                new_alerts.append(alert)
                send_email_alert(recipient_email, case_id, alert["reason"])
    return new_alerts
