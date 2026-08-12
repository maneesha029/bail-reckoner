# MEMBER 3 — Application & Compliance Engine
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

Two connected pieces: (1) a procedural checklist generator — turning "you're eligible" into "here's exactly what to file," and (2) the **indigent bond-waiver flagger** — your project's strongest, most original feature, catching people already granted bail but stuck because they can't afford the bond. **You extend Member 1's database — coordinate with them directly before you start.**

---

## 2. YOUR PROMPT (Paste Into Your AI Coding Assistant)

```
I'm building the Application & Compliance module for Bail Reckoner, a
legal-tech system for Indian undertrial bail cases. This module has two
parts: (1) generating the procedural checklist needed to file a bail
application, and (2) flagging cases where the undertrial may qualify for
an indigent bond waiver.

I need you to help me, inside a folder called compliance-engine:

Part 1 - Procedural Requirements:
1. Build a table of procedural requirements (bond type, required
   documents, fine ranges) based on CrPC Sections 441-450 and BNSS
   equivalents, linked to offense_category — extending (not duplicating)
   the offenses table Member 1 already built.
2. Build a FastAPI service exposing POST /api/v1/procedural/requirements
   using the exact request/response shape in section 4 below.

Part 2 - Indigent Bond-Waiver Flagging:
3. Build logic based on CrPC Section 436 / BNSS equivalent (courts may
   waive/reduce bond for indigent persons).
4. Build POST /api/v1/bond-waiver/check using the exact shape in
   section 4 below.
5. Write test cases: multiple offense categories for Part 1, multiple
   hardship-indicator combinations for Part 2.
6. Containerize both as one service with Docker, matching the file
   structure in section 5.

Use ONLY the field names and folder structure given to me below. Import
shared object definitions (Case, Charge) from the shared_schemas
package rather than redefining them — I will connect to Member 1's
existing offenses table via a shared database connection string.
```

---

## 3. RESOURCES (Exact Sources — Use These, Not Guesses)

- **India Code** (indiacode.nic.in) — CrPC Sections 441–450 (bonds, sureties) and BNSS equivalents; CrPC Section 436 / BNSS equivalent specifically (indigent bond-waiver provision)
- Cross-reference **Satender Kumar Antil v. CBI** (via indiankanoon.org or main.sci.gov.in) — it also addresses standardizing bond/surety practices
- Technical docs: same as Member 1 — fastapi.tiangolo.com · docs.sqlalchemy.org · postgresql.org/docs (you're extending their schema, use the same stack)

---

## 4. YOUR EXACT API CONTRACT (Do Not Deviate)

**Shared enum you must use exactly:**
```
bond_type: surety_bond | personal_bond | waived_indigent
```

**`POST /api/v1/procedural/requirements`**
Request: `{ "case_id": "uuid" }`
Response (`data`):
```json
{
  "case_id": "uuid",
  "bond_type": "personal_bond",
  "estimated_fine_amount_inr": 5000,
  "required_documents": ["Aadhaar", "Proof of residence", "Two sureties with ID proof"],
  "procedural_steps": [{ "step_number": 1, "description": "string" }],
  "governing_sections": ["CrPC 441", "CrPC 445"]
}
```

**`POST /api/v1/bond-waiver/check`**
Request:
```json
{
  "case_id": "uuid",
  "hardship_indicators": {
    "has_fixed_income": false,
    "owns_property": false,
    "has_dependents": true,
    "months_in_custody_post_bail_grant": 4
  }
}
```
Response (`data`):
```json
{
  "case_id": "uuid",
  "is_flagged_for_waiver": true,
  "waiver_confidence": "high",
  "governing_section": "CrPC 436 / BNSS equivalent",
  "reasoning_summary": "factual statement, not conclusory"
}
```
Every response uses the standard envelope: `{ "success": true, "data": {}, "error": null }`

---

## 5. YOUR EXACT FOLDER STRUCTURE

```
/bail-reckoner
  /services
    /compliance-engine                  <- THIS IS YOURS, ONLY YOU EDIT HERE
      main.py                           <- FastAPI app instance, named `app`
      config.py
      models.py                         <- ProceduralRequirement, HardshipIndicator tables
      schemas.py                        <- imports from shared_schemas + local extensions
      routes.py                         <- your 2 endpoints
      logic.py                          <- checklist + bond-waiver logic
      test_main.py
      __init__.py
      Dockerfile
      requirements.txt
      README.md
  /shared_schemas                       <- SHARED, do not edit without team announcement
```

**`__init__.py` content (create exactly this):**
```python
# compliance-engine/__init__.py
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

- **You extend:** Member 1's `offenses` and `cases` tables — talk to them directly before finalizing your schema additions, this is your single highest-risk integration point
- **You are called by:** Member 6's gateway (displays your output on legal aid/judge dashboards)
- **You write to:** Member 4's audit log — every request must also log via `POST /api/v1/audit/log`
- **You import from:** `/shared_schemas` for `Case` and `Charge`
- **Environment variables you need:** `DATABASE_URL` (same database as Member 1), `TRUST_SERVICE_URL`

---

## 7. EXPECTED OUTCOME (Your Honest Test)

- [ ] Two different offense categories produce **different, correct procedural checklists**
- [ ] Toggling a hardship indicator (e.g., `has_fixed_income` true→false) **changes the bond-waiver flag output** — proves the logic isn't hardcoded
- [ ] Every governing section cited traces back to real statutory text you can point to
- [ ] Both endpoints run independently, respond correctly via `curl`/Postman without the frontend running

---

## 8. MERGE CONFLICT PROTOCOL (Read Before Writing Any Code)

- **You only ever edit files inside `/services/compliance-engine`.** Never edit Member 1's `eligibility-engine` folder directly, even though you're extending their schema — coordinate schema changes with them, don't edit their code yourself.
- **Never edit `/shared_schemas` without announcing it in the team channel first.**
- **Work on your own branch**, named `member-3/feature-description` — never commit directly to `main`.
- **Merge working increments often**, not one giant merge at the end.
- **If your schema extension requires a change to Member 1's table**, that change must be proposed to and agreed with Member 1 first, then made once, by whoever owns that migration — never make silent parallel changes to a shared table.
- **Daily one-line update** in your shared channel: what you finished, what's blocking you.

---

## STEP-BY-STEP: WHAT TO DO WITH YOUR SCAFFOLD (bail-reckoner-scaffold.zip)

Your folder: `bail-reckoner/services/compliance-engine`. Both your
features (procedural checklist + bond-waiver flagging) have real, tested
logic already — your job is to replace placeholder data with real legal
content and coordinate schema with Member 1.

### What's already built for you
- `logic.py` — `get_procedural_requirements` (placeholder data) and
  `check_bond_waiver` (real scoring logic, already tested and working)
- `models.py` — `ProceduralRequirement` and `BondWaiverFlag` table schemas
- `test_main.py` — 3 passing tests

### Step 1 — confirm what you received works
```bash
cd bail-reckoner/services/compliance-engine
pip install fastapi pydantic pytest sqlalchemy --break-system-packages
python3 -m pytest test_main.py -v
```
**Expected output:** `3 passed` — bond-waiver flags high hardship, doesn't
flag low hardship, procedural requirements returns the correct shape.

### Step 2 — run and hit both endpoints
```bash
uvicorn main:app --port 8003 --reload
curl -X POST http://localhost:8003/api/v1/bond-waiver/check \
  -H "Content-Type: application/json" \
  -d '{"case_id":"t1","hardship_indicators":{"has_fixed_income":false,"owns_property":false,"has_dependents":true,"months_in_custody_post_bail_grant":4}}'
```
**Expected output:** `"is_flagged_for_waiver": true` — this input has 4/4
hardship factors present. Try flipping each field to `true` one at a time
and confirm the flag correctly changes — this is your honest test.

### Step 3 — where real data goes
1. Get CrPC Sections 441–450 / BNSS equivalents (bond types, documents,
   fines) from India Code — put your compiled mapping in a new file
   `compliance-engine/procedural_data.json`
2. Get CrPC Section 436 / BNSS equivalent (indigent bond waiver) — confirm
   your 4-factor hardship scoring model against real case law or a legal
   contact — this is question #3 in `docs/LEGAL_VALIDATION_QUESTIONS.md`

### Step 4 — replace the placeholder + coordinate with Member 1
`get_procedural_requirements` currently returns the same hardcoded
checklist regardless of offense category — replace it with a real lookup
against your `ProceduralRequirement` table, keyed by `offense_category`
from Member 1's `Offense` table. **Talk to Member 1 before changing their
schema** — you only ever add your own tables, never edit their code directly.

### Step 5 — the honest test
Two different offense categories must produce two different, correct
checklists. Toggling one hardship indicator must change the bond-waiver
output — you already confirmed this works with placeholder logic in Step 2;
confirm it still holds once real data is wired in.

### Where you link to others
- You extend Member 1's `offenses`/`cases` tables — this is your highest
  integration-risk point
- Called by Member 6's gateway
- You write to Member 4's audit log — add the call in `routes.py` (not yet wired)
