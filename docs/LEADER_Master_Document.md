# LEADER MASTER DOCUMENT
### Bail Reckoner — Complete Project Reference

---

## 1. WHAT THIS SYSTEM IS

A deployed web application helping identify and act on undertrial prisoners in India who already qualify for bail under Section 436A CrPC / Section 479 BNSS, but have gone undetected — plus a second, original feature flagging people already granted bail but stuck because they can't afford the bond. Six independent backend services plus a frontend, connected through one locked API contract.

---

## 2. THE SIX MODULES AND WHO OWNS THEM

| Module | Folder | Owner | One-line job |
|---|---|---|---|
| Eligibility Engine | `/services/eligibility-engine` | Member 1 | Calculates statutory bail eligibility from time served |
| Precedent Engine | `/services/precedent-engine` | Member 2 | Retrieves and cites real case law, never recommends |
| Compliance Engine | `/services/compliance-engine` | Member 3 | Generates filing checklist + flags indigent bond-waiver eligibility |
| Trust & Access Layer | `/services/trust-access-layer` | Member 4 | Auth, RBAC, tamper-evident audit logging |
| Monitoring & Outreach | `/services/monitoring-engine` | Member 5 | Scheduled scanning/alerts + real data sourcing (RTI, NCRB) |
| Interface & Integration | `/services/gateway` + `/frontend` | Member 6 | Ties everything into one usable product |

---

## 3. REPO STRUCTURE (Full, All Members Combined)

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
  /shared_schemas             (Member 6 creates first, then team-shared)
    __init__.py
    models.py
  /data                       (Member 5)
    ncrb_cleaned.csv
    synthetic_cases.json
    fetch_ncrb_data.py
    generate_synthetic_data.py
  /docs
    API_CONTRACT.md
    NAMING_CONVENTIONS.md
    FINAL_INTEGRATION_CHECK.md
  /docker-compose.yml          (Member 6 owns)
  /.env.example                (Member 6 owns)
  /README.md                  (Member 6 owns, top-level)
```

**Every service folder follows this identical internal skeleton** (so anyone can navigate anyone else's code instantly):
```
/service-name
  main.py          <- FastAPI app instance, always named `app`
  config.py        <- environment variable loading
  models.py        <- SQLAlchemy database models
  schemas.py       <- imports from shared_schemas, service-specific extensions only
  routes.py        <- API route definitions
  logic.py         <- core business logic
  test_main.py     <- pytest tests
  __init__.py      <- empty, marks the package
  Dockerfile
  requirements.txt
  README.md
```

---

## 4. FULL API REQUIREMENTS (All Routes, One Table)

| Route | Method | Owner Service | Purpose |
|---|---|---|---|
| `/api/v1/eligibility/check` | POST | eligibility-engine | Compute bail eligibility |
| `/api/v1/eligibility/{case_id}` | GET | eligibility-engine | Fetch last result |
| `/api/v1/eligibility/override` | POST | eligibility-engine | Human override, logged |
| `/api/v1/precedent/search` | POST | precedent-engine | Retrieve cited precedent |
| `/api/v1/procedural/requirements` | POST | compliance-engine | Generate filing checklist |
| `/api/v1/bond-waiver/check` | POST | compliance-engine | Flag indigent bond-waiver eligibility |
| `/api/v1/auth/login` | POST | trust-access-layer | Authenticate, issue JWT |
| `/api/v1/audit/log` | POST | trust-access-layer | Internal: record any action |
| `/api/v1/audit/logs/{case_id}` | GET | trust-access-layer | Fetch full audit trail for a case |
| `/api/v1/alerts/config` | POST | monitoring-engine | Set notification preferences |
| `/api/v1/alerts/pending` | GET | monitoring-engine | List unacknowledged alerts |
| `/api/v1/alerts/scan` | GET (internal) | monitoring-engine | Triggered by scheduler |

All routes sit behind the gateway (`/services/gateway`), which is the only thing the frontend ever calls.

**Every response, from every service, uses this envelope, no exceptions:**
```json
{ "success": true, "data": { }, "error": null }
```

---

## 5. SHARED DATABASE TABLES

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
One PostgreSQL instance, shared connection string (`DATABASE_URL`), but **each table has exactly one owning service that writes to it** — Member 1 owns `cases`/`offenses`, Member 3 owns `procedural_requirements`/`bond_waiver_flags`, Member 4 owns `audit_logs`/`users`, Member 5 owns `alerts`/`alert_configs`. Everyone else reads via API, never direct table writes into another service's tables.

---

## 6. FULL ENVIRONMENT VARIABLE LIST

```
DATABASE_URL
JWT_SECRET
REDIS_URL
CHROMA_URL
ELIGIBILITY_SERVICE_URL
PRECEDENT_SERVICE_URL
COMPLIANCE_SERVICE_URL
TRUST_SERVICE_URL
MONITORING_SERVICE_URL
GATEWAY_PORT
ANTHROPIC_API_KEY (or OPENAI_API_KEY)
TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN
SMTP_HOST / SMTP_PORT / SMTP_USER / SMTP_PASSWORD
```
Member 6 owns `.env.example` listing all of these; each member fills in only the ones their own service needs locally.

---

## 7. THE SHARED_SCHEMAS PACKAGE — THE SINGLE SOURCE OF TRUTH

Written once by Member 6 in the first session (full code is in Member 6's individual file), imported by every other service. **The one rule that prevents the merge conflict you're worried about:** nobody re-types a field name from memory — everyone imports it from here. If a field needs to change, it changes in exactly one file, announced to the team first.

---

## 8. BUILD SEQUENCE (Leader's View)

**Phase 0 (Day 1, everyone together):** walk through this document and each member's individual file; confirm roles; Member 6 sets up the repo and writes `shared_schemas` immediately; Member 1 starts the offense database; Member 5 files both RTIs same day.

**Phase 1 (Foundation, ~weeks 1–2):** Member 1's schema is the blocking dependency for Members 3 and 4 — run a joint session between Members 1, 3, 4 to lock it. Member 6 gets skeleton dashboards running with dummy data. Member 2 gets a minimal RAG pipeline working on a small test corpus. Checkpoint at end of phase: everyone demos their skeleton piece.

**Phase 2 (Core build):** each member builds against their individual file's prompt and success criteria. Weekly sync tracks progress. Watch Member 6 (blocked on everyone) and Members 1/3 (shared schema) most closely.

**Phase 3 (Integration):** bring services online in this order — Member 1 + Member 4 first (prove one service can log to another), then Member 3, then Member 2 (independent, low risk), then Member 5, then Member 6's gateway/frontend ties all five together.

**Phase 4 (Final Integration Check):** run the full `FINAL_Integration_Check.md` document — this is not optional and not a formality, it's the actual bar for "done."

**Phase 5 (Deployment + Final Prep):** public deployment, pitch deck built from the Full Pitch Narrative, mock demo with someone playing a skeptical judge, final RTI status check.

---

## 9. WHAT ELSE IS NEEDED, BEYOND THE CODE (Leader's Responsibility to Track)

- **Human override/correction logging** — build this, not optional (owned by Member 1, extended by whoever else needs override capability)
- **Graceful degradation per dashboard section** — build this (Member 6)
- **DPDP Act 2023 data-protection stance** — have a clear, stated answer ready, even if not fully implemented
- **Disclaimer text** on every output — "this tool assists legal research and compliance tracking; it does not constitute legal advice"
- **SIH-specific deliverables** — confirm your cycle's idea-round PPT requirement and deadline, and the prototype demo video requirement, separately from your live prototype
- **One-page executive summary** — separate from all the detailed docs, for a 60-second read
- **Impact estimate** — a concrete, clearly-labeled projection (e.g., based on the 264→64 statistic) for the pitch
- **Team credibility slide** and a genuine **"what's next after SIH"** answer

---

## 10. FINAL SIGN-OFF CRITERIA

The project is done when, and only when:
1. `docker-compose up` brings up all 10 services cleanly
2. The full Honest Test (in `FINAL_Integration_Check.md`) passes, live, on the deployed public URL
3. Every item in the PS Requirement Coverage Checklist is genuinely demonstrable, not just architecturally present
4. At least one mock demo has been run with a skeptical-judge role-play
5. RTI status (whatever it is) is honestly reflected in your final data-sourcing narrative

As leader, personally verify all five before declaring the project complete — don't delegate this final check.
