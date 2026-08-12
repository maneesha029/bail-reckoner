# Bail Reckoner — Resources Per Member + Naming Conventions to Prevent Conflicts

---

# PART A: EXACT RESOURCES, PER MEMBER

## Member 1 — Eligibility Engine

**Legal source documents (for the offense database):**
- **India Code** (indiacode.nic.in) — official government repository of bare acts. Get the full text of: Indian Penal Code 1860, Bharatiya Nyaya Sanhita 2023, Code of Criminal Procedure 1973, Bharatiya Nagarik Suraksha Sanhita 2023 (specifically Section 479 for the bail-eligibility rule), Indian Evidence Act / Bharatiya Sakshya Adhiniyam 2023.
- **Special statutes** (also on India Code): Information Technology Act 2000 (cyber crimes), SC/ST (Prevention of Atrocities) Act 1989, POCSO Act 2012 (crimes against children), Prevention of Money Laundering Act 2002 (economic offences).
- **Case law:** *Satender Kumar Antil v. Central Bureau of Investigation* (2022) — search on Indian Kanoon (indiankanoon.org) or the Supreme Court's own judgment portal (main.sci.gov.in) for the full text and the offense-category framework (A–D).

**Statistical grounding data:**
- **data.gov.in** — search "Prison Statistics India" for NCRB's structured, downloadable datasets (multiple years available)
- **ncrb.gov.in** — NCRB's own Prison Statistics India annual reports (PDF), useful to cross-check sentence/offense data
- **dataful.in** — pre-cleaned versions of NCRB prison data, easier to work with programmatically

**Technical resources:**
- FastAPI docs: fastapi.tiangolo.com
- SQLAlchemy (ORM) docs: docs.sqlalchemy.org
- pytest docs: docs.pytest.org
- PostgreSQL docs: postgresql.org/docs

---

## Member 2 — Precedent & Legal Research Engine

**Corpus sources:**
- **Indian Kanoon** (indiankanoon.org) — the largest free public repository of Indian court judgments; check their terms of use before bulk scraping, and keep scraping volume reasonable for a student project (a focused corpus of a few hundred relevant judgments is plenty — you don't need to index all of Indian law)
- **India Code** (indiacode.nic.in) — for the actual statutory text your RAG system should also be able to cite alongside case law
- **e-Courts / Supreme Court judgment portal** (main.sci.gov.in) — for landmark judgments specifically

**Technical resources:**
- LangChain docs: python.langchain.com
- LlamaIndex docs: docs.llamaindex.ai
- Chroma (vector DB) docs: docs.trychroma.com
- Anthropic API docs (for the Claude-based synthesis/citation step): docs.claude.com
- Sentence-transformers (if you want a free/local embedding model instead of an API): sbert.net

---

## Member 3 — Application & Compliance Engine

**Legal source documents:**
- **India Code** (indiacode.nic.in) — CrPC Sections 441–450 (bonds, sureties, procedural requirements) and their BNSS equivalents
- **CrPC Section 436 / BNSS equivalent** — specifically the indigent bond-waiver provision; search India Code directly for the section text
- Cross-reference with **Satender Kumar Antil v. CBI** again here — the judgment also touches on standardizing bond/surety practices, useful context for your logic

**Technical resources:**
- Same stack as Member 1 (FastAPI, SQLAlchemy, PostgreSQL) since you're extending their schema — coordinate directly with Member 1 rather than researching a separate stack

---

## Member 4 — Trust & Access Layer

**Standards and references:**
- **OWASP API Security Top 10** (owasp.org/www-project-api-security) — use this as your checklist for what to actually test/harden, rather than guessing
- **OWASP Authentication Cheat Sheet** — for password/session handling best practices

**Technical resources:**
- PyJWT docs (JWT handling): pyjwt.readthedocs.io
- passlib / bcrypt docs (password hashing): passlib.readthedocs.io
- Python's built-in `hashlib` (SHA-256, for your hash-chaining) — docs.python.org/3/library/hashlib.html
- FastAPI security docs (dependency-based auth): fastapi.tiangolo.com/tutorial/security

---

## Member 5 — Monitoring & Outreach Engine

**Data sources:**
- **RTI Online Portal** (rtionline.gov.in) — for filing with NCRB (central)
- Your **state's own RTI portal** — for filing with the state prison department (search "[your state] RTI portal")
- **data.gov.in** and **dataful.in** — same NCRB datasets referenced above, for building your synthetic dataset's realistic distributions
- **IndiaSpend** and **Amnesty International's "Justice Under Trial" report** — search for these directly to see the methodology and findings of prior RTI-based research on this exact topic, useful as a template for what your RTI responses might look like

**Technical resources:**
- Celery docs: docs.celeryq.dev
- Redis docs: redis.io/docs
- Twilio (SMS) docs: twilio.com/docs
- Python `smtplib` (email, free alternative to Twilio for email-only alerts): docs.python.org/3/library/smtplib.html

---

## Member 6 — Interface & Integration Layer

**Technical resources:**
- React docs: react.dev
- Tailwind CSS docs: tailwindcss.com/docs
- FastAPI docs (for the gateway): fastapi.tiangolo.com
- Docker Compose docs: docs.docker.com/compose
- GitHub Actions docs: docs.github.com/actions
- Deployment: Vercel (vercel.com/docs) for frontend, Render (render.com/docs) or Railway (docs.railway.app) for backend services

---

# PART B: PREVENTING THE REAL MERGE CONFLICT — SHARED NAMING

You're right to worry about this specifically: **the actual risk isn't Git merge conflicts (different files, no problem) — it's silent naming drift, where Member 1 calls a field `case_id` and Member 3 calls the same thing `caseId` or `id`, and nothing errors until integration day, when everything breaks at once.** Here's how to eliminate that.

## The real fix: one shared schema package, not six people typing the same names from memory

Don't rely on everyone remembering the API Contract's field names correctly. Instead:

**Create one shared Python package** (e.g., a folder called `shared_schemas` in your monorepo, or a tiny separate pip-installable package) containing the **Pydantic model definitions** for every shared object — `Case`, `EligibilityResult`, `PrecedentResult`, `ProceduralResult`, `BondWaiverResult`, `AuditLogEntry`, `AlertConfig`, `AlertRecord` — written **once**, by whoever finalizes the API Contract (typically Member 6 or whoever leads integration).

**Every member's service imports from this shared package instead of re-typing field names.** This makes naming drift structurally impossible instead of relying on discipline — if Member 1 changes a field, every service importing the shared package either updates automatically or breaks loudly at build time (which is what you want — a loud break during development, not a silent mismatch during a live demo).

## Exact naming — lock these today, before anyone writes code

**Docker Compose service names** (used in `docker-compose.yml`, must match exactly):
```
eligibility-engine    (Member 1)
precedent-engine      (Member 2)
compliance-engine     (Member 3)
trust-access-layer    (Member 4)
monitoring-engine     (Member 5)
gateway               (Member 6)
frontend              (Member 6)
postgres              (shared database)
redis                 (Member 5's scheduler, shared if others need it)
chroma                (Member 2's vector DB)
```

**Database table names** (all lowercase, snake_case, plural):
```
cases
offenses
procedural_requirements
bond_waiver_flags
audit_logs
alerts
alert_configs
users
```

**Every service's internal file structure** (identical skeleton across all 5 backend services, so anyone can navigate anyone else's service instantly):
```
/service-name
  main.py          <- FastAPI app instance, always named `app`
  config.py        <- environment variable loading
  models.py        <- SQLAlchemy database models
  schemas.py        <- imports from shared_schemas, service-specific extensions only
  routes.py         <- API route definitions
  logic.py          <- core business logic
  test_main.py      <- pytest tests
  Dockerfile
  requirements.txt
```

**Environment variable naming** (prefix by service, so nothing collides in a shared `.env`):
```
DATABASE_URL                    (shared, all services)
JWT_SECRET                      (shared, all services need it to verify tokens)
ELIGIBILITY_SERVICE_URL
PRECEDENT_SERVICE_URL
COMPLIANCE_SERVICE_URL
TRUST_SERVICE_URL
MONITORING_SERVICE_URL
GATEWAY_PORT
REDIS_URL
CHROMA_URL
TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN   (Member 5 only)
ANTHROPIC_API_KEY or OPENAI_API_KEY       (Member 2 only)
```

**Pydantic class naming** (defined once in `shared_schemas`, imported everywhere — never redefined locally):
```python
# shared_schemas/models.py

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

class EligibilityResult(BaseModel):
    case_id: str
    eligibility_status: str
    days_served: int
    days_required: int
    threshold_rule_applied: str
    eligible_since_date: str | None
    computed_at: str

# ... and so on for PrecedentResult, ProceduralResult, BondWaiverResult,
# AuditLogEntry, AlertConfig, AlertRecord — each defined ONCE here,
# matching the API Contract document exactly, imported by every service.
```

## The one-sentence rule to give your whole team today:

**"If you're about to type a field name, class name, table name, or service name — check the shared_schemas package or this document first. Never invent a new name for something that already has one."**

This single habit, enforced from day one, is what actually prevents the integration-day disaster you're worried about — not clever tooling, just one shared source of truth that nobody re-types from memory.
