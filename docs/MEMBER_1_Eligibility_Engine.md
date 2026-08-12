# MEMBER 1 — Eligibility Engine
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

A service that determines whether an undertrial prisoner has already served enough time in custody to legally qualify for bail under **Section 436A CrPC / Section 479 BNSS** — half the maximum sentence for their offense, or one-third if they're a first-time offender. This is pure calculation, not AI — deterministic, defensible, and the foundation the rest of the system depends on.

**You also own the core legal database** (offense → section → sentence mapping) that Member 3 will extend. Build this first, before your own eligibility logic — everyone else is waiting on it.

---

## 2. YOUR PROMPT (Paste Into Your AI Coding Assistant)

```
I'm building the Eligibility Engine module for a legal-tech system called
Bail Reckoner. This module determines whether an undertrial prisoner in
India has already served enough time in custody to qualify for statutory
bail under Section 436A of the CrPC / Section 479 of the BNSS (half the
maximum sentence for their offense, or one-third if they are a first-time
offender).

I need you to help me:
1. Design a PostgreSQL schema for an "offenses" table mapping: act (IPC/
   BNS/BNSS/BSA/IT_Act/POCSO/SC_ST_Act/PMLA/other), section, offense_
   category (cyber_crimes, crimes_against_sc_st, crimes_against_women,
   crimes_against_children, offences_against_state, economic_offences,
   crimes_against_foreigners, general), is_compoundable (boolean), and
   max_sentence_months (integer). Also design a "cases" table matching
   the Case schema below exactly.
2. Build a Python FastAPI service in a folder called eligibility-engine,
   exposing POST /api/v1/eligibility/check and GET /api/v1/eligibility/
   {case_id}, using the exact request/response shapes in section 4 below.
3. Compute days served (today minus custody_start_date) vs. threshold
   (half of max_sentence_months in days, or one-third if is_first_time_
   offender is true), returning the correct eligibility_status.
4. Handle multiple charges on one case by using the charge with the
   longest max sentence as the binding threshold.
5. Write pytest tests: one per offense category, plus the multi-charge
   edge case and the first-time-offender rule.
6. Add a manual override endpoint: POST /api/v1/eligibility/override
   that lets a legal_aid or judge role mark a result as reviewed with a
   reason, logged like any other action (do not silently overwrite the
   computed result — store the override alongside it).
7. Containerize with Docker, matching the file structure in section 5.

Use ONLY the field names, table names, and folder structure given to me
below — do not invent alternate names.
```

---

## 3. RESOURCES (Exact Sources — Use These, Not Guesses)

- **India Code** (indiacode.nic.in) — full text of IPC 1860, Bharatiya Nyaya Sanhita 2023, CrPC 1973, BNSS 2023 (Section 479 specifically), IT Act 2000, SC/ST (Prevention of Atrocities) Act 1989, POCSO Act 2012, PMLA 2002
- **Indian Kanoon** (indiankanoon.org) or **main.sci.gov.in** — full text of *Satender Kumar Antil v. CBI* (2022)
- **data.gov.in** — search "Prison Statistics India" for NCRB structured datasets
- **ncrb.gov.in** — NCRB Prison Statistics India annual reports (PDF), for cross-checking
- **dataful.in** — pre-cleaned NCRB prison data
- Technical docs: fastapi.tiangolo.com · docs.sqlalchemy.org · docs.pytest.org · postgresql.org/docs

---

## 4. YOUR EXACT API CONTRACT (Do Not Deviate)

**Shared enums you must use exactly:**
```
offense_category: cyber_crimes | crimes_against_sc_st | crimes_against_women |
  crimes_against_children | offences_against_state | economic_offences |
  crimes_against_foreigners | general
eligibility_status: eligible_now | not_yet_eligible |
  eligible_first_time_offender_rule | insufficient_data
case_stage: under_trial | bail_flagged | bail_applied | bail_granted | released
```

**`POST /api/v1/eligibility/check`**
Request: `{ "case_id": "uuid" }`
Response (`data`):
```json
{
  "case_id": "uuid",
  "eligibility_status": "eligible_now",
  "days_served": 412,
  "days_required": 365,
  "threshold_rule_applied": "half_term",
  "eligible_since_date": "2026-06-01",
  "computed_at": "2026-08-11T10:00:00Z"
}
```

**`GET /api/v1/eligibility/{case_id}`** — returns last computed result, no recompute

**`POST /api/v1/eligibility/override`**
Request: `{ "case_id": "uuid", "actor_user_id": "uuid", "reason": "string" }`

**Every response uses the standard envelope:**
```json
{ "success": true, "data": { }, "error": null }
```

---

## 5. YOUR EXACT FOLDER STRUCTURE

```
/bail-reckoner                          <- repo root (shared, do not touch outside your folder)
  /services
    /eligibility-engine                 <- THIS IS YOURS, ONLY YOU EDIT HERE
      main.py                           <- FastAPI app instance, named `app`
      config.py                         <- env var loading
      models.py                         <- SQLAlchemy models: Offense, Case
      schemas.py                        <- imports from shared_schemas + local extensions
      routes.py                         <- your 3 endpoints
      logic.py                          <- eligibility calculation logic
      test_main.py                      <- pytest tests
      __init__.py                       <- empty file, makes this a package
      Dockerfile
      requirements.txt
      README.md                         <- what this service does, how to run it
  /shared_schemas                       <- SHARED, do not edit without team announcement
    __init__.py
    models.py                           <- Case, Charge, EligibilityResult classes live here
```

**`__init__.py` content for your service folder (create exactly this):**
```python
# eligibility-engine/__init__.py
# Intentionally empty — marks this directory as a Python package.
```

**`requirements.txt` starting point:**
```
fastapi
uvicorn
sqlalchemy
psycopg2-binary
pydantic
pytest
python-dotenv
```

---

## 6. WHERE YOU LINK TO OTHER MEMBERS

- **You are read by:** Member 3 (extends your `offenses` and `cases` tables), Member 5 (calls your `/eligibility/check` on a schedule), Member 6 (displays your output on all 3 dashboards)
- **You write to:** Member 4's audit log — every `/eligibility/check` and `/eligibility/override` call must also call `POST /api/v1/audit/log` (Member 4's service) internally
- **You import from:** `/shared_schemas` for the `Case`, `Charge`, and `EligibilityResult` class definitions — never redefine these locally
- **Environment variables you need:** `DATABASE_URL`, `TRUST_SERVICE_URL` (to call Member 4's audit log)

---

## 7. EXPECTED OUTCOME (Your Honest Test)

- [ ] Two different real cases (different offense, different custody date) return **two genuinely different, correct results**
- [ ] Changing `custody_start_date` by one day changes `days_served` correctly
- [ ] First-time offender flag correctly switches between half-term and one-third thresholds
- [ ] All pytest tests pass — show the actual output
- [ ] Override endpoint correctly stores a reviewed/overridden result without deleting the original computed value
- [ ] Service runs independently in its own Docker container, responds correctly via `curl`/Postman without the frontend running

---

## 8. MERGE CONFLICT PROTOCOL (Read Before Writing Any Code)

- **You only ever edit files inside `/services/eligibility-engine`.** Never touch another member's service folder.
- **Never edit `/shared_schemas` without announcing it in the team channel first** and getting at least one other member to confirm — this file is imported by everyone, silent changes break other people's builds.
- **Work on your own branch**, named `member-1/feature-description` — never commit directly to `main`.
- **Merge your working increments often** (small, frequent merges), not one giant merge at the end — this is what actually prevents conflicts.
- **If you need a field that doesn't exist in `shared_schemas` yet**, propose the addition in the team channel rather than inventing a local-only version — a local-only field silently diverges from what everyone else sees.
- **Daily one-line update** in your shared channel: what you finished, what's blocking you.

---

## STEP-BY-STEP: WHAT TO DO WITH YOUR SCAFFOLD (bail-reckoner-scaffold.zip)

Your folder: `bail-reckoner/services/eligibility-engine`. It already contains
working placeholder code — real logic, real passing tests — not empty
stubs. Your job is to replace the placeholder data with real, legally
validated data, not to build from scratch.

### What's already built for you (verify, don't rebuild)
- `logic.py` — real functions: `compute_days_served`, `compute_threshold_days`,
  `binding_charge` (the multi-charge rule — flagged as unvalidated, see
  step 5), `determine_eligibility`
- `routes.py` — the 3 endpoints, currently reading from a hardcoded
  `MOCK_CASES` dict instead of a real database
- `models.py` — the real `Offense` and `CaseRecord` SQLAlchemy table schemas
- `test_main.py` — 4 passing tests

### Step 1 — confirm what you received actually works
```bash
cd bail-reckoner/services/eligibility-engine
pip install -r requirements.txt --break-system-packages
python3 -m pytest test_main.py -v
```
**Expected output:** `4 passed` — `test_eligible_now`, `test_not_yet_eligible`,
`test_first_time_offender_rule`, `test_multi_charge_uses_longest_sentence`.
If anything fails here, something broke in transit — stop and check before continuing.

### Step 2 — run the service and hit it manually
```bash
uvicorn main:app --port 8001 --reload
```
In a second terminal:
```bash
curl -X POST http://localhost:8001/api/v1/eligibility/check \
  -H "Content-Type: application/json" -d '{"case_id":"test-1"}'
```
**Expected output:** a JSON object with `"success": true` and a `data` field
containing `eligibility_status`, `days_served`, `days_required`, etc. — this
proves the endpoint round-trips correctly, still using placeholder case data.

### Step 3 — where real data goes
1. Get the real offense → section → max sentence mapping from India Code
   (indiacode.nic.in), covering IPC/BNS/BNSS/BSA and all 7 special categories.
2. Create `eligibility-engine/seed_offenses.py` — a script that inserts rows
   into the `Offense` table (schema already in `models.py`) from your
   compiled data. Put your source data in a new file
   `eligibility-engine/offense_data.json` (you create this — one entry per
   offense, matching the `Offense` model's fields exactly: `act`, `section`,
   `offense_category`, `is_compoundable`, `max_sentence_months`).
3. Run the seed script once your real `DATABASE_URL` is live (via
   `docker-compose up postgres` at minimum) to populate the table.

### Step 4 — replace the placeholder case lookup
In `routes.py`, `MOCK_CASES` is a stand-in. Replace it with a real query
against the `cases` table (schema in `models.py`) using SQLAlchemy —
look up the case by `case_id`, pull its real `custody_start_date`,
`is_first_time_offender`, and joined charges from `offenses`.

### Step 5 — the one thing you must get legally confirmed before calling this done
`binding_charge()` in `logic.py` picks the charge with the longest max
sentence when a case has multiple charges. This is flagged in the code
comment as an **unvalidated assumption**. This is question #1 in
`docs/LEGAL_VALIDATION_QUESTIONS.md` — get it answered by a real legal
contact before treating multi-charge cases as correctly handled.

### Step 6 — the honest test (do this before marking your part done)
Insert two real, different cases (different offense, different custody
date) into the real database, call `/api/v1/eligibility/check` for each,
and confirm you get two genuinely different, correct results — not the
same output regardless of input.

### Where you link to others
- Member 3 reads your `Offense`/`CaseRecord` schema — tell them immediately
  if you change it
- Member 5 calls your `/api/v1/eligibility/check` on a schedule
- Member 6 displays your output on all 3 dashboards
- You write to Member 4's audit log — every check/override call should
  also call `TRUST_SERVICE_URL + /api/v1/audit/log` (not yet wired in the
  scaffold — add this call in `routes.py`)
