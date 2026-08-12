# MEMBER 4 — Trust & Access Layer
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

The system that makes every action traceable, secure, and properly access-controlled — this is your project's direct answer to "who's responsible if AI is involved." Every other member's service calls into yours to log their actions. You are the most-depended-upon service after Member 1's database.

---

## 2. YOUR PROMPT (Paste Into Your AI Coding Assistant)

```
I'm building the Trust & Access module for Bail Reckoner, a legal-tech
system handling sensitive undertrial prisoner data in India. This module
must make every action in the system traceable and properly access-
controlled.

I need you to help me, inside a folder called trust-access-layer:
1. Design a PostgreSQL append-only audit_logs table: log_id, case_id,
   actor_user_id, actor_role, action_type, action_payload (JSON),
   timestamp, entry_hash, previous_hash — where entry_hash is a SHA-256
   hash of (this row's content + previous_hash), making the chain
   tamper-evident. Also design a users table: user_id, username,
   password_hash, role.
2. Build a FastAPI service exposing POST /api/v1/auth/login, POST
   /api/v1/audit/log, and GET /api/v1/audit/logs/{case_id} using the
   exact shapes in section 4 below.
3. Implement role-based access control middleware, applicable to any
   endpoint, restricting access based on the JWT's role claim (judge,
   legal_aid, jail_officer, admin).
4. Write a script that deliberately alters a row in audit_logs after
   the fact and confirms the hash chain breaks and is detectable — I
   need this as a real, runnable demonstration.
5. Add rate-limiting on /api/v1/auth/login, HTTPS enforcement config,
   and encrypted-at-rest config for personally identifiable fields.
6. Containerize with Docker, matching the file structure in section 5,
   with no hardcoded credentials.

Use ONLY the field names and folder structure given to me below. Import
shared object definitions from the shared_schemas package.
```

---

## 3. RESOURCES (Exact Sources — Use These, Not Guesses)

- **OWASP API Security Top 10** (owasp.org/www-project-api-security) — your checklist for what to actually test/harden
- **OWASP Authentication Cheat Sheet** — password/session handling best practices
- Technical docs: pyjwt.readthedocs.io (JWT) · passlib.readthedocs.io (password hashing) · docs.python.org/3/library/hashlib.html (SHA-256 for hash-chaining) · fastapi.tiangolo.com/tutorial/security

---

## 4. YOUR EXACT API CONTRACT (Do Not Deviate)

**Shared enum you must use exactly:**
```
user_role: judge | legal_aid | jail_officer | admin
```

**`POST /api/v1/auth/login`**
Request: `{ "username": "string", "password": "string" }`
Response (`data`): `{ "access_token": "jwt_string", "role": "legal_aid", "user_id": "uuid" }`

**`POST /api/v1/audit/log`** (called internally by every other service, not the frontend)
Request:
```json
{
  "case_id": "uuid",
  "actor_user_id": "uuid",
  "actor_role": "legal_aid",
  "action_type": "eligibility_check | precedent_search | procedural_check | bond_waiver_check | alert_sent | manual_override",
  "action_payload": { "any": "layer-specific data" },
  "timestamp": "2026-08-11T10:00:00Z"
}
```
Response (`data`): `{ "log_id": "uuid", "entry_hash": "string", "previous_hash": "string" }`

**`GET /api/v1/audit/logs/{case_id}`** — full chronological log for a case

Every response uses the standard envelope: `{ "success": true, "data": {}, "error": null }`

---

## 5. YOUR EXACT FOLDER STRUCTURE

```
/bail-reckoner
  /services
    /trust-access-layer                 <- THIS IS YOURS, ONLY YOU EDIT HERE
      main.py                           <- FastAPI app instance, named `app`
      config.py
      models.py                         <- AuditLog, User tables
      schemas.py                        <- imports from shared_schemas + local extensions
      routes.py                         <- your 3 endpoints
      auth.py                           <- JWT + RBAC middleware
      hashing.py                        <- hash-chain logic
      test_main.py
      test_tamper.py                    <- your tamper-detection demonstration script
      __init__.py
      Dockerfile
      requirements.txt
      README.md
  /shared_schemas                       <- SHARED, do not edit without team announcement
```

**`__init__.py` content (create exactly this):**
```python
# trust-access-layer/__init__.py
# Intentionally empty — marks this directory as a Python package.
```

**`requirements.txt` starting point:**
```
fastapi
uvicorn
sqlalchemy
psycopg2-binary
pydantic
pyjwt
passlib[bcrypt]
pytest
python-dotenv
slowapi
```

---

## 6. WHERE YOU LINK TO OTHER MEMBERS

- **You are called by:** literally every other service (Members 1, 2, 3, 5) for audit logging, and Member 6's gateway for authentication on every request
- **You depend on:** nothing else — you can build and test entirely independently, which makes you a good early-priority build
- **You import from:** `/shared_schemas` for `AuditLogEntry`
- **Environment variables you need:** `DATABASE_URL`, `JWT_SECRET`

---

## 7. EXPECTED OUTCOME (Your Honest Test)

- [ ] Logging in as each of the 4 roles, you can demonstrate **each role can only access what it should** — e.g., a jail_officer token calling a judge-only endpoint is correctly rejected
- [ ] Your tamper-test script runs live and shows the exact moment the hash chain detects an alteration — a real, reproducible demonstration
- [ ] You can show a real audit log entry created by another member's service (e.g., Member 1's eligibility check), proving the logging hook works end-to-end
- [ ] Service runs independently, responds correctly via `curl`/Postman without the frontend running

---

## 8. MERGE CONFLICT PROTOCOL (Read Before Writing Any Code)

- **You only ever edit files inside `/services/trust-access-layer`.** Never touch another member's service folder.
- **Never edit `/shared_schemas` without announcing it in the team channel first.**
- **Work on your own branch**, named `member-4/feature-description` — never commit directly to `main`.
- **Merge working increments often**, not one giant merge at the end.
- **Since everyone depends on you, prioritize getting a basic working version live early** — even a minimal auth + logging endpoint unblocks the other 4 services from integrating their logging hooks sooner.
- **Daily one-line update** in your shared channel: what you finished, what's blocking you.

---

## STEP-BY-STEP: WHAT TO DO WITH YOUR SCAFFOLD (bail-reckoner-scaffold.zip)

Your folder: `bail-reckoner/services/trust-access-layer`. Your hash-chain
and RBAC logic are already real and tested — including a live tamper
demonstration. Your job is to move from in-memory storage to a real
database and wire in real user accounts.

### What's already built for you
- `hashing.py` — real SHA-256 hash-chaining, tested
- `auth.py` — real JWT creation/decoding + role-permission map
- `routes.py` — all 3 endpoints, currently using in-memory storage
  (`MOCK_USERS`, `AUDIT_CHAIN`) instead of real tables
- `test_tamper.py` — a **live, runnable tamper-detection demonstration**
- `test_main.py` — 2 passing tests

### Step 1 — confirm what you received works
```bash
cd bail-reckoner/services/trust-access-layer
pip install fastapi pydantic pytest sqlalchemy pyjwt --break-system-packages
python3 -m pytest test_main.py -v
python3 test_tamper.py
```
**Expected output:** `2 passed`, then from `test_tamper.py`:
```
Chain valid before tampering: True
Chain valid after tampering:  False
Tamper detection confirmed working.
```
This is the exact live demonstration you'll show judges — it already works.

### Step 2 — run and hit the endpoints
```bash
uvicorn main:app --port 8004 --reload
curl -X POST http://localhost:8004/api/v1/auth/login \
  -H "Content-Type: application/json" -d '{"username":"judge1","password":"demo"}'
```
**Expected output:** a JSON object with a real `access_token` (JWT) and
`"role": "judge"`.

### Step 3 — where real data goes
Replace `MOCK_USERS` in `routes.py` with a real `users` table query (schema
already in `models.py`) — create a seed script `seed_users.py` to insert
real accounts (hashed passwords via `passlib`, not plaintext) for each
of the 4 roles, once `DATABASE_URL` is live.

### Step 4 — persist the audit chain for real
`AUDIT_CHAIN` in `routes.py` is in-memory — replace it with real inserts
into the `audit_logs` table (schema in `models.py`), keeping the same
hash-chain logic from `hashing.py` unchanged, just writing to Postgres
instead of a Python list.

### Step 5 — the honest test
Log in as each of the 4 roles, confirm `role_can()` correctly restricts
access when you wire RBAC into other services' endpoints. Re-run
`test_tamper.py` after switching to real DB storage — same expected output.

### Where you link to others
- **Everyone calls into you** — Members 1, 2, 3, 5 all need
  `TRUST_SERVICE_URL + /api/v1/audit/log` wired into their `routes.py`
  (currently not wired in the scaffold — this is a cross-team task, flag
  it in your first sync)
- Member 6's gateway validates JWTs against your `JWT_SECRET` for every request
- **Prioritize this service being stable early** — you unblock everyone else's logging
