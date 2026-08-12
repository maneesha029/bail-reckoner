# MEMBER 6 — Interface & Integration Layer
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

The API gateway that routes to all 5 backend services, and the three real dashboards (legal aid/jail officer, judge, undertrial) that turn six separate services into one usable product. **You also create the `/shared_schemas` package first**, before anyone else can fully integrate — this is your highest-priority task on day one.

---

## 2. YOUR PROMPT (Paste Into Your AI Coding Assistant)

```
I'm building the Interface & Integration layer for Bail Reckoner, a
legal-tech system with 5 independent backend services (eligibility,
precedent research, compliance/bond-waiver, trust/audit, monitoring/
alerts). I need to build the shared schema package, API gateway, and
3 frontend dashboards that tie them together.

I need you to help me:
1. FIRST: build a shared_schemas Python package (see section 4 below
   for exact class definitions) containing Pydantic models for Case,
   Charge, EligibilityResult, PrecedentResult, ProceduralResult,
   BondWaiverResult, AuditLogEntry, AlertConfig, AlertRecord — this
   must be finished before other members can fully integrate, so
   prioritize it in the first session.
2. Build a FastAPI gateway service in a folder called gateway, routing
   incoming requests to the correct backend service based on route
   prefix (/api/v1/eligibility/* -> eligibility-engine, /api/v1/
   precedent/* -> precedent-engine, /api/v1/procedural/* and /api/v1/
   bond-waiver/* -> compliance-engine, /api/v1/auth/* and /api/v1/
   audit/* -> trust-access-layer, /api/v1/alerts/* -> monitoring-
   engine). The frontend only ever talks to this gateway.
3. Build a React + Tailwind frontend in a folder called frontend, with
   three views: legal aid/jail officer dashboard (case queue + full
   case detail: eligibility, precedent, checklist, bond-waiver flag),
   judge dashboard (read-only version), undertrial-facing simplified
   view (plain-language single-case status).
4. Implement JWT auth flow, attaching the token to all gateway requests.
5. Set up GitHub Actions CI running tests/linting on every push.
6. Write a docker-compose.yml that spins up ALL SIX services plus
   postgres, redis, and chroma together for local integration testing.
7. Deploy: frontend to Vercel, gateway + backend services to Render or
   Railway, with environment variables configured for production.

Use ONLY the field names and folder structure given to me below.
```

---

## 3. RESOURCES

- React docs: react.dev · Tailwind docs: tailwindcss.com/docs
- FastAPI docs (gateway): fastapi.tiangolo.com
- Docker Compose docs: docs.docker.com/compose
- GitHub Actions docs: docs.github.com/actions
- Deployment: vercel.com/docs (frontend) · render.com/docs or docs.railway.app (backend)

---

## 4. THE SHARED_SCHEMAS PACKAGE — YOU WRITE THIS FIRST, EXACTLY AS BELOW

```python
# shared_schemas/__init__.py
from .models import (
    Charge, Case, EligibilityResult, PrecedentCitation, PrecedentResult,
    ProceduralResult, BondWaiverResult, AuditLogEntry, AlertConfig, AlertRecord,
)
```

```python
# shared_schemas/models.py
from pydantic import BaseModel
from typing import Optional

class Charge(BaseModel):
    act: str
    section: str
    offense_category: str
    is_compoundable: bool
    max_sentence_months: int

class Case(BaseModel):
    case_id: str
    prisoner_id: str
    charges: list[Charge]
    custody_start_date: str
    is_first_time_offender: bool
    state: str
    district: str
    case_stage: str
    has_legal_aid: bool
    created_at: str
    updated_at: str

class EligibilityResult(BaseModel):
    case_id: str
    eligibility_status: str
    days_served: int
    days_required: int
    threshold_rule_applied: str
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
    bond_type: str
    estimated_fine_amount_inr: int
    required_documents: list[str]
    procedural_steps: list[ProceduralStep]
    governing_sections: list[str]

class BondWaiverResult(BaseModel):
    case_id: str
    is_flagged_for_waiver: bool
    waiver_confidence: str
    governing_section: str
    reasoning_summary: str

class AuditLogEntry(BaseModel):
    case_id: str
    actor_user_id: str
    actor_role: str
    action_type: str
    action_payload: dict
    timestamp: str

class AlertConfig(BaseModel):
    recipient_user_id: str
    notify_via: str
    scan_frequency: str

class AlertRecord(BaseModel):
    alert_id: str
    case_id: str
    triggered_at: str
    reason: str
    is_acknowledged: bool
```

**Publish this package first, announce it in the team channel, and only then let other members start importing from it.**

---

## 5. YOUR EXACT API CONTRACT — GATEWAY ROUTING TABLE

```
/api/v1/eligibility/*   -> eligibility-engine  (ELIGIBILITY_SERVICE_URL)
/api/v1/precedent/*     -> precedent-engine     (PRECEDENT_SERVICE_URL)
/api/v1/procedural/*    -> compliance-engine    (COMPLIANCE_SERVICE_URL)
/api/v1/bond-waiver/*   -> compliance-engine    (COMPLIANCE_SERVICE_URL)
/api/v1/auth/*          -> trust-access-layer   (TRUST_SERVICE_URL)
/api/v1/audit/*         -> trust-access-layer   (TRUST_SERVICE_URL)
/api/v1/alerts/*        -> monitoring-engine    (MONITORING_SERVICE_URL)
```

Every response passed through, unchanged, using the standard envelope: `{ "success": true, "data": {}, "error": null }`

---

## 6. YOUR EXACT FOLDER STRUCTURE

```
/bail-reckoner
  /services
    /gateway                            <- THIS IS YOURS
      main.py                           <- FastAPI app instance, named `app`
      config.py
      routing.py                        <- route-to-service mapping
      auth_middleware.py                <- validates JWT on every request
      test_main.py
      __init__.py
      Dockerfile
      requirements.txt
      README.md
  /frontend                             <- THIS IS YOURS
    /src
      /pages
        LegalAidDashboard.jsx
        JudgeDashboard.jsx
        UndertrialView.jsx
      /components
      /api
        client.js                       <- single place all API calls go through
      App.jsx
    package.json
    Dockerfile
    README.md
  /shared_schemas                       <- YOU CREATE THIS FIRST, then it's shared
    __init__.py
    models.py
  /docker-compose.yml                   <- YOU OWN THIS FILE
  /.env.example                         <- YOU OWN THIS FILE
  /docs
    API_CONTRACT.md
    NAMING_CONVENTIONS.md
  /README.md                            <- YOU OWN THIS FILE (top-level repo readme)
```

**`docker-compose.yml` service names (exact):**
```yaml
services:
  postgres:
  redis:
  chroma:
  eligibility-engine:
  precedent-engine:
  compliance-engine:
  trust-access-layer:
  monitoring-engine:
  gateway:
  frontend:
```

---

## 7. WHERE YOU LINK TO OTHER MEMBERS

- **You depend on:** all 5 other services being reachable at their respective URLs — you are the most integration-heavy role, expect your real progress to be front-loaded (skeleton/gateway setup) and back-loaded (wiring real data in as each service comes online), with a lighter middle stretch while others build
- **You control:** the only place the frontend ever calls into is your gateway — no dashboard component should ever call a backend service URL directly
- **Environment variables you own defining:** all the `*_SERVICE_URL` variables, `GATEWAY_PORT`, `JWT_SECRET` (shared with Member 4)

---

## 8. EXPECTED OUTCOME (Your Honest Test)

- [ ] Enter a **new case with different data**, submit it, and every dashboard section updates correctly and differently from a previous case
- [ ] All three dashboards correctly restrict what they show based on logged-in role
- [ ] `docker-compose up` successfully starts all ten services/containers together, and the frontend can reach all backend services through your gateway
- [ ] The system is live on a public URL, and you have personally tested every user flow on that live link, not just localhost

---

## 9. MERGE CONFLICT PROTOCOL (Read Before Writing Any Code)

- **You only ever edit files inside `/services/gateway` and `/frontend`.** Never touch another member's service folder.
- **You own `/shared_schemas` initially** — write it first, then any future changes require announcement and agreement from the team, same rule as everyone else once it's published.
- **You own `docker-compose.yml`, `.env.example`, and the top-level `README.md`** — these are shared-visibility files, but you're the maintainer; if another member needs a new environment variable added, they tell you, you add it, rather than everyone editing this file independently.
- **Work on your own branch**, named `member-6/feature-description` — never commit directly to `main`.
- **Merge working increments often.**
- **Daily one-line update** in your shared channel: what you finished, what's blocking you — flag specifically if you're blocked waiting on someone else's service.

---

## STEP-BY-STEP: WHAT TO DO WITH YOUR SCAFFOLD (bail-reckoner-scaffold.zip)

Your folders: `bail-reckoner/services/gateway` and `bail-reckoner/frontend`.
The gateway routing is real and tested; the frontend is a minimal working
skeleton making real API calls through your client — you build it out
from here.

### What's already built for you
- `shared_schemas/` — **already published**, at the repo root. Every
  other member imports from this. If you need to change a field, announce
  it to the team first — this is the single most depended-upon file in
  the whole repo.
- `gateway/routing.py` — real route-to-service mapping, tested
- `gateway/main.py` — a real reverse-proxy gateway forwarding requests
- `frontend/src/api/client.js` — all API calls already wired to go through
  the gateway, never direct to a backend service
- `frontend/src/pages/` — 3 page skeletons (`LegalAidDashboard.jsx` is the
  most complete; `JudgeDashboard.jsx` and `UndertrialView.jsx` are stubs)

### Step 1 — confirm the gateway works
```bash
cd bail-reckoner/services/gateway
pip install fastapi pydantic pytest httpx --break-system-packages
python3 -m pytest test_main.py -v
```
**Expected output:** `3 passed` — eligibility route resolves to port 8001,
precedent route resolves to port 8002, unknown routes correctly return `None`.

### Step 2 — bring the whole system up together (once other members have pushed their services)
```bash
cd bail-reckoner
cp .env.example .env
docker-compose up --build
```
**Expected output:** all 10 containers start; visiting `http://localhost:5173`
loads the frontend without a connection error.

### Step 3 — build out the frontend pages
`LegalAidDashboard.jsx` currently calls all 4 backend features and dumps
raw JSON — replace the `<pre>` block with real UI: eligibility status card,
precedent citations list, procedural checklist, bond-waiver flag banner.
Do the same for `JudgeDashboard.jsx` (read-only version) and
`UndertrialView.jsx` (simplified plain-language version) — currently
placeholder divs.

### Step 4 — wire in real authentication
Add a login screen calling `login()` from `client.js`, store the returned
`access_token`, and pass it into every dashboard's API calls (the
functions in `client.js` already accept a `token` parameter — just needs
a real login flow feeding it).

### Step 5 — the honest test
Enter a new case with different data through your UI, submit, and confirm
every dashboard section updates correctly and differently from a previous
case. This is the most visible test in the whole project — it's what
judges will personally try.

### Where you link to others
- You are the only thing the frontend ever talks to — never let a
  component call a backend service URL directly, only `client.js` → gateway
- You're blocked on all 5 other services being real and running — expect
  your own build to be front-loaded (skeleton, done) and back-loaded
  (wiring real data in as others finish), with a lighter middle stretch
