# MEMBER 2 — Precedent & Legal Research Engine
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

A retrieval system (RAG) that surfaces real Indian case law and statutes relevant to the judgment-based factors a judge must weigh (flight risk, witness influence). **You never predict or recommend — only retrieve and cite.** This is your system's answer to "is this AI making legal decisions" — it isn't; it's a search engine with citations.

---

## 2. YOUR PROMPT (Paste Into Your AI Coding Assistant)

```
I'm building the Precedent & Legal Research module for Bail Reckoner, a
legal-tech system for Indian undertrial bail cases. This module retrieves
relevant Indian case law and statutes for discretionary bail factors
(flight risk, witness influence) — it must NEVER recommend a decision,
only surface and cite relevant sources.

I need you to help me, inside a folder called precedent-engine:
1. Set up a RAG pipeline: LangChain or LlamaIndex, with a Chroma vector
   database, to store and retrieve embedded legal documents.
2. Structure a starter corpus (I will supply judgment texts) covering
   general bail jurisprudence (Satender Kumar Antil v. CBI) plus at
   least 2 of these categories: cyber_crimes, crimes_against_sc_st,
   crimes_against_women, crimes_against_children, offences_against_
   state, economic_offences, crimes_against_foreigners.
3. Build a FastAPI service exposing POST /api/v1/precedent/search using
   the exact request/response shape in section 4 below.
4. Build a post-processing filter that rejects/regenerates any output
   containing "should," "recommend," "likely to," "eligible for
   release" — citation_text must always be neutral and factual.
5. Build a small evaluation set (10-15 queries with a known correct
   source) so I can measure and report retrieval accuracy honestly.
6. Containerize with Docker, matching the file structure in section 5.

Use ONLY the field names and folder structure given to me below — do
not invent alternate names. Import shared object definitions from the
shared_schemas package rather than redefining them.
```

---

## 3. RESOURCES (Exact Sources — Use These, Not Guesses)

- **Indian Kanoon** (indiankanoon.org) — largest free public repository of Indian judgments; check terms of use before bulk scraping, keep it to a focused corpus (a few hundred relevant judgments, not everything)
- **India Code** (indiacode.nic.in) — statutory text to cite alongside case law
- **main.sci.gov.in** — Supreme Court's own judgment portal, for landmark cases specifically
- Technical docs: python.langchain.com · docs.llamaindex.ai · docs.trychroma.com · docs.claude.com (Anthropic API) · sbert.net (free local embeddings alternative)

---

## 4. YOUR EXACT API CONTRACT (Do Not Deviate)

**`POST /api/v1/precedent/search`**
Request:
```json
{
  "case_id": "uuid",
  "query_context": {
    "offense_category": "one of the shared offense_category enum",
    "discretion_factors": ["flight_risk", "witness_influence"]
  }
}
```
Response (`data`):
```json
{
  "case_id": "uuid",
  "results": [
    {
      "citation_id": "uuid",
      "case_name": "Satender Kumar Antil v. CBI",
      "citation_text": "neutral 2-3 sentence factual summary, never a recommendation",
      "source_url": "string",
      "relevance_score": 0.87,
      "applicable_factor": "flight_risk | witness_influence | general_precedent"
    }
  ],
  "disclaimer": "This output surfaces relevant law and precedent only. It does not constitute a bail recommendation. Final determination rests with the presiding judicial authority.",
  "retrieved_at": "2026-08-11T10:00:00Z"
}
```
Every response uses the standard envelope: `{ "success": true, "data": {}, "error": null }`

**Your base system prompt for the LLM synthesis step:**
```
You are a legal research assistant. You are given a case's offense
category and discretionary factors, plus retrieved excerpts from real
Indian judgments and statutes.

Summarize what these sources say about the given factors, in 2-3
sentences per source, in neutral, factual language.

Rules:
- Never state whether bail should be granted or denied.
- Never use words like "should," "recommend," "likely," or "advise."
- Always attribute each point to its source (case name or section).
- If sources conflict, state that plainly instead of resolving it yourself.
- End every response with: "Final determination rests with the
  presiding judicial authority."
```

---

## 5. YOUR EXACT FOLDER STRUCTURE

```
/bail-reckoner
  /services
    /precedent-engine                   <- THIS IS YOURS, ONLY YOU EDIT HERE
      main.py                           <- FastAPI app instance, named `app`
      config.py
      corpus/                           <- your judgment/statute text files
      embed.py                          <- corpus embedding pipeline
      schemas.py                        <- imports from shared_schemas + local extensions
      routes.py
      logic.py                          <- retrieval + citation-filter logic
      eval_set.json                     <- your 10-15 test queries with known answers
      test_main.py
      __init__.py
      Dockerfile
      requirements.txt
      README.md
  /shared_schemas                       <- SHARED, do not edit without team announcement
```

**`__init__.py` content (create exactly this):**
```python
# precedent-engine/__init__.py
# Intentionally empty — marks this directory as a Python package.
```

**`requirements.txt` starting point:**
```
fastapi
uvicorn
langchain
chromadb
pydantic
pytest
python-dotenv
anthropic
```

---

## 6. WHERE YOU LINK TO OTHER MEMBERS

- **You are called by:** Member 6's gateway (which routes judge/legal-aid dashboard requests to you)
- **You write to:** Member 4's audit log — every `/precedent/search` call must also call `POST /api/v1/audit/log` internally
- **You import from:** `/shared_schemas` for any shared object references
- **You are independent of:** Member 1 and Member 3's database — you don't touch their tables at all, which makes you low-risk for integration conflicts
- **Environment variables you need:** `CHROMA_URL`, `ANTHROPIC_API_KEY` (or `OPENAI_API_KEY`), `TRUST_SERVICE_URL`

---

## 7. EXPECTED OUTCOME (Your Honest Test)

- [ ] Two different offense categories return **genuinely different, relevant results**
- [ ] You have run your evaluation set and can state actual retrieval accuracy as a number, not a claim
- [ ] You can show at least one real example where your filter caught and blocked a recommendation-phrased output
- [ ] Service runs independently, responds correctly via `curl`/Postman without the frontend running

---

## 8. MERGE CONFLICT PROTOCOL (Read Before Writing Any Code)

- **You only ever edit files inside `/services/precedent-engine`.** Never touch another member's service folder.
- **Never edit `/shared_schemas` without announcing it in the team channel first.**
- **Work on your own branch**, named `member-2/feature-description` — never commit directly to `main`.
- **Merge working increments often**, not one giant merge at the end.
- **If you need a shared field that doesn't exist yet**, propose it in the team channel rather than inventing a local-only version.
- **Daily one-line update** in your shared channel: what you finished, what's blocking you.

---

## STEP-BY-STEP: WHAT TO DO WITH YOUR SCAFFOLD (bail-reckoner-scaffold.zip)

Your folder: `bail-reckoner/services/precedent-engine`. Real logic and
tests exist for the citation-only guardrail — the actual RAG retrieval is
a labeled placeholder you replace.

### What's already built for you
- `logic.py` — `SYSTEM_PROMPT` (the exact citation-only prompt), the
  `violates_citation_guardrail` filter (tested, working), and
  `search_precedent` (placeholder — returns one hardcoded citation)
- `corpus/README.md` — tells you exactly what to put where
- `eval_set.json` — starter evaluation queries
- `test_main.py` — 3 passing tests

### Step 1 — confirm what you received works
```bash
cd bail-reckoner/services/precedent-engine
pip install fastapi pydantic pytest --break-system-packages
python3 -m pytest test_main.py -v
```
**Expected output:** `3 passed` — `test_guardrail_catches_recommendation`,
`test_guardrail_allows_neutral_text`, `test_search_returns_results`.

### Step 2 — run and hit the placeholder endpoint
```bash
uvicorn main:app --port 8002 --reload
curl -X POST http://localhost:8002/api/v1/precedent/search \
  -H "Content-Type: application/json" \
  -d '{"case_id":"test-1","query_context":{"offense_category":"economic_offences","discretion_factors":["flight_risk"]}}'
```
**Expected output:** JSON with one citation from *Satender Kumar Antil v.
CBI* — this proves the shape works before you plug in real retrieval.

### Step 3 — where real data goes
1. Download real judgment/statute text from Indian Kanoon (indiankanoon.org)
   and India Code (indiacode.nic.in)
2. Put plain text or markdown files in `precedent-engine/corpus/` — one
   file per judgment/statute, named descriptively (e.g.
   `satender_kumar_antil_v_cbi.txt`)
3. Start with general bail jurisprudence + 2 special categories, expand later

### Step 4 — replace the placeholder retrieval
In `logic.py`, replace `search_precedent`'s hardcoded return with: embed
your corpus into Chroma, do a real similarity search against the query,
then call the LLM (Claude/GPT) with `SYSTEM_PROMPT` to synthesize a
citation-formatted response. Run every generated response through
`violates_citation_guardrail` before returning it — this part already
works, don't rebuild it.

### Step 5 — the honest test
Run `eval_set.json`'s queries against your real pipeline, record how many
returned the correct/relevant source, and write that number down honestly
— this becomes your retrieval accuracy claim in the pitch.

### Where you link to others
- Called by Member 6's gateway
- You write to Member 4's audit log — add a call to
  `TRUST_SERVICE_URL + /api/v1/audit/log` in `routes.py` (not yet wired)
- You're independent of Members 1 and 3's database — lowest integration risk
