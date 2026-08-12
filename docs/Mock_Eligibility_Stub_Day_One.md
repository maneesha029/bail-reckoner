# Day-One Mock Stub — Eligibility Engine
### Unblocks Members 2, 3, 5, 6 Before Member 1's Real Service Exists

---

## WHY THIS EXISTS

Member 1's real eligibility logic depends on a legally-validated offense database — which takes time to get right and time to get reviewed by a real legal contact. Everyone else shouldn't sit idle waiting for that. This stub returns **structurally correct, hardcoded responses** matching the exact schema — so Members 2, 3, 5, 6 can build and test their own services against a real, running endpoint from hour one. Member 1 replaces this with the real logic later, behind the same route — nobody else's code changes when that swap happens.

---

## RUN THIS ON DAY ONE (Anyone Can Start It, Takes 5 Minutes)

```python
# eligibility-engine/mock_main.py
# TEMPORARY STUB — run this until Member 1's real service is ready.
# Same route, same response shape, same port as the real service.

from fastapi import FastAPI
from datetime import datetime, timedelta

app = FastAPI()

@app.post("/api/v1/eligibility/check")
def check_eligibility(payload: dict):
    case_id = payload.get("case_id", "mock-case-id")
    return {
        "success": True,
        "data": {
            "case_id": case_id,
            "eligibility_status": "eligible_now",
            "days_served": 412,
            "days_required": 365,
            "threshold_rule_applied": "half_term",
            "eligible_since_date": (datetime.utcnow() - timedelta(days=47)).date().isoformat(),
            "computed_at": datetime.utcnow().isoformat() + "Z"
        },
        "error": None
    }

@app.get("/api/v1/eligibility/{case_id}")
def get_eligibility(case_id: str):
    return check_eligibility({"case_id": case_id})
```

**Run it:**
```bash
pip install fastapi uvicorn
uvicorn mock_main:app --port 8001
```

Point `ELIGIBILITY_SERVICE_URL=http://localhost:8001` in everyone's `.env` — this is the exact same URL the real service will eventually use.

---

## THE RULE FOR USING THIS

1. **Nobody builds their real logic assuming the mock's specific values (412 days, "eligible_now") are meaningful** — they're placeholder. Test your own logic's *behavior* (does my service correctly handle whatever eligibility_status it receives), not the specific mock numbers.
2. **Member 1 owns swapping this out.** Once the real service is ready and legally reviewed, Member 1 deploys it on the same route/port, and this file gets deleted. No other member's code should need to change.
3. **This does not replace Member 1's own honest test** (two different real cases, different results) — the mock is for unblocking *other people's* development, not for validating Member 1's actual logic.

---

## SEQUENCING THIS ENABLES

- **Day 1:** Mock stub runs. Members 2, 3, 5, 6 start building against it immediately.
- **Day 1, in parallel:** Member 1 starts the real offense database + starts legal outreach (the multi-charge rule — "longest max sentence as binding threshold" — should be the first specific question asked to any legal contact, not a general "please review this").
- **Whenever Member 1's real service + at least initial legal feedback is ready:** swap it in behind the same route. Everyone else's integration doesn't break, because the contract never changed — only what's behind it did.
- **Recommended before full build-out:** validate Member 1's real service alone — one working endpoint, tested via Postman, with one real or realistic case — with a legal aid contact, before investing further in the other five services' polish. A confirmed-correct core is worth more at this stage than five more features built on an unvalidated assumption.
