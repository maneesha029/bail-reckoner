# MEMBER 5 — Monitoring & Outreach Engine
### Your Complete Build Package

---

## 0. SHARED FOUNDATION — READ THIS FIRST (Identical In Every Member's File)

This section is copy-identical across all 6 member files on purpose — so this single file is enough to build against, with no other document required.

### 0.1 The shared_schemas package (build this locally to develop against, even before Member 6 publishes the real one)

```python
# shared_schemas/models.py
from pydantic import BaseModel
from typing import Optional

class Charge(BaseModel):
    act: str                       # IPC | BNS | BNSS | BSA | IT_Act | POCSO | SC_ST_Act | PMLA | other
    section: str
    offense_category: str          # see enum list below
    is_compoundable: bool
    max_sentence_months: int

class Case(BaseModel):
    case_id: str
    prisoner_id: str
    charges: list[Charge]
    custody_start_date: str        # ISO 8601 date
    is_first_time_offender: bool
    state: str
    district: str
    case_stage: str                # under_trial | bail_flagged | bail_applied | bail_granted | released
    has_legal_aid: bool
    created_at: str
    updated_at: str

class EligibilityResult(BaseModel):
    case_id: str
    eligibility_status: str        # eligible_now | not_yet_eligible | eligible_first_time_offender_rule | insufficient_data
    days_served: int
    days_required: int
    threshold_rule_applied: str    # half_term | one_third_first_time
    eligible_since_date: Optional[str]
    computed_at: str

class PrecedentCitation(BaseModel):
    citation_id: str
    case_name: str
    citation_text: str
    source_url: str
    relevance_score: float
    applicable_factor: str

class PrecedentResult(BaseModel):
    case_id: str
    results: list[PrecedentCitation]
    disclaimer: str
    retrieved_at: str

class ProceduralStep(BaseModel):
    step_number: int
    description: str

class ProceduralResult(BaseModel):
    case_id: str
    bond_type: str                 # surety_bond | personal_bond | waived_indigent
    estimated_fine_amount_inr: int
    required_documents: list[str]
    procedural_steps: list[ProceduralStep]
    governing_sections: list[str]

class BondWaiverResult(BaseModel):
    case_id: str
    is_flagged_for_waiver: bool
    waiver_confidence: str         # high | medium | low
    governing_section: str
    reasoning_summary: str

class AuditLogEntry(BaseModel):
    case_id: str
    actor_user_id: str
    actor_role: str                # judge | legal_aid | jail_officer | admin
    action_type: str
    action_payload: dict
    timestamp: str

class AlertConfig(BaseModel):
    recipient_user_id: str
    notify_via: str                # email | sms
    scan_frequency: str            # daily | weekly

class AlertRecord(BaseModel):
    alert_id: str
    case_id: str
    triggered_at: str
    reason: str
    is_acknowledged: bool
```

**Rule:** never redefine these classes locally with different field names. If your service needs extra fields, add them in your own `schemas.py` as a separate class that wraps or extends these — never rename an existing field.

### 0.2 Every shared enum, complete list

```
offense_category: cyber_crimes | crimes_against_sc_st | crimes_against_women |
  crimes_against_children | offences_against_state | economic_offences |
  crimes_against_foreigners | general
eligibility_status: eligible_now | not_yet_eligible |
  eligible_first_time_offender_rule | insufficient_data
bond_type: surety_bond | personal_bond | waived_indigent
user_role: judge | legal_aid | jail_officer | admin
case_stage: under_trial | bail_flagged | bail_applied | bail_granted | released
```

### 0.3 Standard response envelope (every endpoint, every service, no exceptions)

```json
{ "success": true, "data": { }, "error": null }
```
On failure: `{ "success": false, "data": null, "error": { "code": "STRING", "message": "STRING" } }`

### 0.4 Full repo structure (so you know where your folder sits relative to everyone else's)

```
/bail-reckoner
  /services
    /eligibility-engine       (Member 1)
    /precedent-engine         (Member 2)
    /compliance-engine        (Member 3)
    /trust-access-layer       (Member 4)
    /monitoring-engine        (Member 5)
    /gateway                  (Member 6)
  /frontend                   (Member 6)
  /shared_schemas             (Member 6 publishes first; everyone imports from it)
  /data                       (Member 5)
  /docs
  /docker-compose.yml         (Member 6 owns)
  /.env.example                (Member 6 owns)
  /README.md
```

### 0.5 Full docker-compose service names (exact, do not rename)

```
postgres, redis, chroma,
eligibility-engine, precedent-engine, compliance-engine,
trust-access-layer, monitoring-engine, gateway, frontend
```

### 0.6 Full environment variable list (yours are marked below; others exist for services you call)

```
DATABASE_URL              (shared, all services)
JWT_SECRET                (shared, all services)
REDIS_URL                 (Member 5, and anyone calling it)
CHROMA_URL                (Member 2, and anyone calling it)
ELIGIBILITY_SERVICE_URL   (used to call Member 1)
PRECEDENT_SERVICE_URL     (used to call Member 2)
COMPLIANCE_SERVICE_URL    (used to call Member 3)
TRUST_SERVICE_URL         (used to call Member 4 — everyone needs this, for audit logging)
MONITORING_SERVICE_URL    (used to call Member 5)
GATEWAY_PORT              (Member 6)
ANTHROPIC_API_KEY or OPENAI_API_KEY   (Member 2 only)
TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN (Member 5 only)
SMTP_HOST / SMTP_PORT / SMTP_USER / SMTP_PASSWORD (Member 5 only)
```

### 0.7 Database table ownership (one writer per table — everyone else reads via API, never direct writes into another service's table)

```
cases, offenses                        -> owned by Member 1
procedural_requirements, bond_waiver_flags -> owned by Member 3
audit_logs, users                      -> owned by Member 4
alerts, alert_configs                  -> owned by Member 5
```

### 0.8 The one-sentence rule

**If you're about to type a field name, class name, table name, or service name — check section 0 above first. Never invent a new name for something that already has one.**

---

## 1. WHAT YOU ARE BUILDING

The piece that makes the system **proactive instead of passive** — automatically scanning for newly-eligible cases and alerting legal aid officers, instead of waiting for someone to check. You also own the **real-world data track**: filing the RTIs, sourcing real government data, and building the realistic synthetic dataset the whole team tests against.

---

## 2. YOUR PROMPT (Paste Into Your AI Coding Assistant)

```
I'm building the Monitoring & Outreach module for Bail Reckoner, a
legal-tech system for Indian undertrial bail cases. This module makes
the system proactive (auto-scanning for newly-eligible cases) instead
of only reactive, and also handles real-world data sourcing.

I need you to help me, inside a folder called monitoring-engine:
1. Build a scheduled task (Celery + Redis, or a cron-based script) that
   runs on a configurable interval, loops through all cases with
   case_stage = "under_trial", calls Member 1's eligibility service at
   {ELIGIBILITY_SERVICE_URL}/api/v1/eligibility/check for each, and for
   any newly-changed eligibility_status of "eligible_now" not already
   flagged, creates an alert record.
2. Build a FastAPI service exposing POST /api/v1/alerts/config and GET
   /api/v1/alerts/pending using the exact shapes in section 4 below.
3. Integrate an email notification sender (SMTP) as the primary method,
   with Twilio SMS as a stretch goal.
4. Separately, write a script that downloads and cleans the NCRB Prison
   Statistics dataset from data.gov.in into usable CSV/JSON, and a
   second script generating a synthetic but realistic demo dataset
   (~50-100 sample cases) modeled on those real distributions, clearly
   labeled as synthetic in its own metadata field.
5. Containerize the scheduled-task service with Docker, matching the
   file structure in section 5.

Use ONLY the field names and folder structure given to me below. Import
shared object definitions from the shared_schemas package.
```

---

## 3. RESOURCES (Exact Sources — Use These, Not Guesses)

- **RTI Online Portal** (rtionline.gov.in) — file with NCRB (central)
- Your **state's own RTI portal** — file with your state prison department (search "[your state] RTI portal")
- **data.gov.in** and **dataful.in** — NCRB prison datasets for synthetic data grounding
- **IndiaSpend** and **Amnesty International's "Justice Under Trial" report** — search directly for methodology reference on prior RTI-based research on this topic
- Technical docs: docs.celeryq.dev · redis.io/docs · twilio.com/docs · docs.python.org/3/library/smtplib.html

---

## 4. YOUR EXACT API CONTRACT (Do Not Deviate)

**`POST /api/v1/alerts/config`**
Request:
```json
{ "recipient_user_id": "uuid", "notify_via": "email", "scan_frequency": "daily" }
```

**`GET /api/v1/alerts/pending`** — list for the logged-in user

**Alert object shape:**
```json
{
  "alert_id": "uuid",
  "case_id": "uuid",
  "triggered_at": "2026-08-11T10:00:00Z",
  "reason": "eligibility_status changed to eligible_now",
  "is_acknowledged": false
}
```

**`GET /api/v1/alerts/scan`** — internal, triggered by your scheduler, no user-facing request body

Every response uses the standard envelope: `{ "success": true, "data": {}, "error": null }`

---

## 5. YOUR EXACT FOLDER STRUCTURE

```
/bail-reckoner
  /services
    /monitoring-engine                  <- THIS IS YOURS, ONLY YOU EDIT HERE
      main.py                           <- FastAPI app instance, named `app`
      config.py
      models.py                         <- Alert, AlertConfig tables
      schemas.py                        <- imports from shared_schemas + local extensions
      routes.py                         <- your 2 endpoints
      scheduler.py                      <- Celery/cron scanning logic
      notify.py                         <- email/SMS sending
      test_main.py
      __init__.py
      Dockerfile
      requirements.txt
      README.md
  /data                                 <- YOURS, shared read access for other members
    ncrb_cleaned.csv
    synthetic_cases.json                <- your generated demo dataset, clearly labeled synthetic
    fetch_ncrb_data.py
    generate_synthetic_data.py
  /shared_schemas                       <- SHARED, do not edit without team announcement
```

**`__init__.py` content (create exactly this):**
```python
# monitoring-engine/__init__.py
# Intentionally empty — marks this directory as a Python package.
```

**`requirements.txt` starting point:**
```
fastapi
uvicorn
celery
redis
sqlalchemy
psycopg2-binary
pydantic
pytest
python-dotenv
requests
pandas
```

---

## 6. WHERE YOU LINK TO OTHER MEMBERS

- **You call:** Member 1's `/api/v1/eligibility/check` on a schedule for every case
- **You write to:** Member 4's audit log — every alert creation logs via `POST /api/v1/audit/log`
- **You are called by:** Member 6's gateway (for the legal aid dashboard's pending-alerts view)
- **Your synthetic dataset is used by:** every other member for testing, so publish it early and announce it in the team channel
- **You import from:** `/shared_schemas` for `Case`, `EligibilityResult`, `AlertConfig`, `AlertRecord`
- **Environment variables you need:** `DATABASE_URL`, `REDIS_URL`, `ELIGIBILITY_SERVICE_URL`, `TRUST_SERVICE_URL`, `SMTP_*` credentials, `TWILIO_ACCOUNT_SID`/`TWILIO_AUTH_TOKEN` (if used)

---

## 7. EXPECTED OUTCOME (Your Honest Test)

- [ ] Your scanner runs on a real schedule (even a shortened test interval) and **catches a newly-eligible case it hadn't flagged before** — proves the automatic detection actually functions
- [ ] Both RTIs are **actually filed**, with tracking numbers noted, not just drafted
- [ ] Your synthetic dataset generation script can be re-run and produces data matching the real NCRB distributions — you can show the comparison
- [ ] Service runs independently

---

## 8. MERGE CONFLICT PROTOCOL (Read Before Writing Any Code)

- **You only ever edit files inside `/services/monitoring-engine` and `/data`.** Never touch another member's service folder.
- **Never edit `/shared_schemas` without announcing it in the team channel first.**
- **Work on your own branch**, named `member-5/feature-description` — never commit directly to `main`.
- **Merge working increments often**, not one giant merge at the end.
- **Publish your synthetic dataset early and announce its exact file path** — other members will build against it for testing, so don't change its structure silently once others depend on it.
- **Daily one-line update** in your shared channel: what you finished, what's blocking you (including RTI status).

---

## STEP-BY-STEP: WHAT TO DO WITH YOUR SCAFFOLD (bail-reckoner-scaffold.zip)

Your folder: `bail-reckoner/services/monitoring-engine`, plus
`bail-reckoner/data`. Your scanning logic is real and tested with a mocked
eligibility call — your job is to point it at the real service and
populate real/synthetic data.

### What's already built for you
- `scheduler.py` — `scan_all_cases`, real logic that calls Member 1's
  service and creates alerts, tested with a mocked HTTP call
- `notify.py` — email sending (falls back to console print if no SMTP set)
- `routes.py` — all 3 endpoints, `/alerts/scan` currently uses 2 hardcoded
  demo case IDs
- `data/generate_synthetic_data.py` — already generates realistic synthetic
  cases, clearly labeled
- `data/fetch_ncrb_data.py` — placeholder, needs the real dataset ID

### Step 1 — confirm what you received works
```bash
cd bail-reckoner/services/monitoring-engine
pip install fastapi pydantic pytest requests --break-system-packages
python3 -m pytest test_main.py -v
```
**Expected output:** `1 passed` — confirms the scanner correctly detects
and flags a newly-eligible case using a mocked response.

### Step 2 — generate your synthetic dataset now
```bash
cd ../../data
python3 generate_synthetic_data.py
```
**Expected output:** `Generated 100 synthetic cases -> synthetic_cases.json`
— open the file and confirm each record is labeled
`"_data_label": "SYNTHETIC..."`.

### Step 3 — file both RTIs today (not code, but your top priority)
Use the draft text already prepared in your docs. File with NCRB
(rtionline.gov.in) and your state prison department's portal. Note the
tracking numbers wherever your team keeps status updates.

### Step 4 — real NCRB data
Search "Prison Statistics India" on data.gov.in, find the real dataset's
resource ID, and replace the placeholder logic in
`data/fetch_ncrb_data.py`'s `fetch_and_clean()` function with a real API
call or CSV download using that ID.

### Step 5 — connect the scanner to real cases
Once Member 1's service has real cases in its database, replace the
hardcoded `demo_case_ids` in `routes.py`'s `trigger_scan()` with a real
query — e.g., ask Member 1 to expose a `list all under-trial case_ids`
helper, or query the shared `cases` table directly for `case_stage ==
"under_trial"` records.

### Step 6 — the honest test
Run the scanner against a case whose custody date you set to be already
past threshold, confirm it gets flagged; run it again immediately and
confirm it's NOT re-flagged (the `ALREADY_FLAGGED` set prevents duplicate
alerts) — this proves the "newly eligible" detection logic actually works,
not just "eligible."

### Where you link to others
- You call Member 1's `/api/v1/eligibility/check` — confirm
  `ELIGIBILITY_SERVICE_URL` points to their real running service
- Called by Member 6's gateway for the pending-alerts view
- You write to Member 4's audit log — add the call in `routes.py` (not yet wired)
