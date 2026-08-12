# Bail Reckoner — API Contract & Shared Data Model
### Lock this file first. Every member builds against THIS exactly. No renaming fields without a team-wide announcement.

---

## 0. GLOBAL CONVENTIONS (Apply Everywhere)

- **Field naming:** `snake_case` for all JSON fields, always.
- **IDs:** UUID v4 strings, field name always ends in `_id` (e.g., `case_id`, `prisoner_id`).
- **Dates:** ISO 8601 strings, always UTC (e.g., `"2026-08-11T00:00:00Z"`).
- **Booleans:** always prefixed `is_` or `has_` (e.g., `is_first_time_offender`, `has_legal_aid`).
- **Base URL (all environments):** `/api/v1/`
- **Every response** (success or error) uses this envelope:
```json
{
  "success": true,
  "data": { },
  "error": null
}
```
On failure:
```json
{
  "success": false,
  "data": null,
  "error": { "code": "VALIDATION_ERROR", "message": "custody_start_date is required" }
}
```
- **Auth:** every endpoint except `/api/v1/auth/login` requires header `Authorization: Bearer <jwt>`
- **Every write action** (POST/PUT) must trigger a call to Member 3's audit log endpoint internally — this is not optional, wire it in from day one.

---

## 1. SHARED ENUMS (Use These Exact Strings Everywhere — Do Not Invent Local Variants)

```
offense_category (used by Members 1, 4, 5):
  "cyber_crimes"
  "crimes_against_sc_st"
  "crimes_against_women"
  "crimes_against_children"
  "offences_against_state"
  "economic_offences"
  "crimes_against_foreigners"
  "general"

user_role (used by Member 3, referenced everywhere):
  "judge"
  "legal_aid"
  "jail_officer"
  "admin"

eligibility_status (used by Members 1, 2, 6):
  "eligible_now"
  "not_yet_eligible"
  "eligible_first_time_offender_rule"
  "insufficient_data"

bond_type (used by Member 5):
  "surety_bond"
  "personal_bond"
  "waived_indigent"

case_stage (used across the system):
  "under_trial"
  "bail_flagged"
  "bail_applied"
  "bail_granted"
  "released"
```

---

## 2. CORE SHARED OBJECT — THE `Case` MODEL

Every layer reads and/or writes pieces of this same object. **Member 4 owns this schema** (in the database); everyone else consumes it via the API, never queries the database directly.

```json
{
  "case_id": "uuid",
  "prisoner_id": "uuid",
  "charges": [
    {
      "act": "IPC | BNS | BNSS | BSA | IT_Act | POCSO | SC_ST_Act | PMLA | other",
      "section": "string, e.g. '304B'",
      "offense_category": "one of offense_category enum",
      "is_compoundable": true,
      "max_sentence_months": 60
    }
  ],
  "custody_start_date": "ISO 8601 date",
  "is_first_time_offender": true,
  "state": "string, e.g. 'Karnataka'",
  "district": "string, e.g. 'Bengaluru Urban'",
  "case_stage": "one of case_stage enum",
  "has_legal_aid": true,
  "created_at": "ISO 8601 datetime",
  "updated_at": "ISO 8601 datetime"
}
```

---

## 3. MEMBER 4 — Layer 1: Eligibility Screener

### `POST /api/v1/eligibility/check`

**Request:**
```json
{
  "case_id": "uuid"
}
```

**Response (`data` field):**
```json
{
  "case_id": "uuid",
  "eligibility_status": "one of eligibility_status enum",
  "days_served": 412,
  "days_required": 365,
  "threshold_rule_applied": "half_term | one_third_first_time",
  "eligible_since_date": "ISO 8601 date or null",
  "computed_at": "ISO 8601 datetime"
}
```

### `GET /api/v1/eligibility/{case_id}` — fetch last computed result (no recompute)

---

## 4. MEMBER 1 — Layer 2: Precedent & Discretion Research

### `POST /api/v1/precedent/search`

**Request:**
```json
{
  "case_id": "uuid",
  "query_context": {
    "offense_category": "one of offense_category enum",
    "discretion_factors": ["flight_risk", "witness_influence"]
  }
}
```

**Response (`data` field):**
```json
{
  "case_id": "uuid",
  "results": [
    {
      "citation_id": "uuid",
      "case_name": "string, e.g. 'Satender Kumar Antil v. CBI'",
      "citation_text": "short neutral summary, NOT a recommendation",
      "source_url": "string",
      "relevance_score": 0.87,
      "applicable_factor": "flight_risk | witness_influence | general_precedent"
    }
  ],
  "disclaimer": "This output surfaces relevant law and precedent only. It does not constitute a bail recommendation. Final determination rests with the presiding judicial authority.",
  "retrieved_at": "ISO 8601 datetime"
}
```

**Hard rule for Member 1's output layer:** the post-filter must reject and re-generate any `citation_text` containing phrases like "should be granted," "recommend," "likely to," "eligible for release" — those are Layer 1's vocabulary, not Layer 2's.

---

## 5. MEMBER 5 — Layer 3: Procedural Requirements

### `POST /api/v1/procedural/requirements`

**Request:**
```json
{ "case_id": "uuid" }
```

**Response (`data` field):**
```json
{
  "case_id": "uuid",
  "bond_type": "one of bond_type enum",
  "estimated_fine_amount_inr": 5000,
  "required_documents": ["Aadhaar", "Proof of residence", "Two sureties with ID proof"],
  "procedural_steps": [
    { "step_number": 1, "description": "string" }
  ],
  "governing_sections": ["CrPC 441", "CrPC 445"]
}
```

## 5b. MEMBER 5 — Layer 5: Indigent Bond-Waiver Flagging

### `POST /api/v1/bond-waiver/check`

**Request:**
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

**Response (`data` field):**
```json
{
  "case_id": "uuid",
  "is_flagged_for_waiver": true,
  "waiver_confidence": "high | medium | low",
  "governing_section": "CrPC 436 / BNSS equivalent",
  "reasoning_summary": "string, factual not conclusory"
}
```

---

## 6. MEMBER 3 — Layer 4: Audit Trail + Auth

### `POST /api/v1/auth/login`
**Request:** `{ "username": "string", "password": "string" }`
**Response (`data`):** `{ "access_token": "jwt_string", "role": "one of user_role enum", "user_id": "uuid" }`

### `POST /api/v1/audit/log` (called internally by every other layer, not by the frontend directly)
**Request:**
```json
{
  "case_id": "uuid",
  "actor_user_id": "uuid",
  "actor_role": "one of user_role enum",
  "action_type": "eligibility_check | precedent_search | procedural_check | bond_waiver_check | alert_sent | manual_override",
  "action_payload": { "any": "layer-specific data, stored as-is" },
  "timestamp": "ISO 8601 datetime"
}
```
**Response (`data`):** `{ "log_id": "uuid", "entry_hash": "string", "previous_hash": "string" }`

### `GET /api/v1/audit/logs/{case_id}` — returns full chronological log for a case

---

## 7. MEMBER 6 — Layer 6: Proactive Alerts

### `GET /api/v1/alerts/scan` (triggered internally by scheduler, not user-facing)
No request body. Internally: loops all cases with `case_stage: "under_trial"`, calls Member 4's `/eligibility/check` for each, and for any result of `"eligible_now"` not already flagged, creates an alert.

### `POST /api/v1/alerts/config`
**Request:**
```json
{
  "recipient_user_id": "uuid",
  "notify_via": "email | sms",
  "scan_frequency": "daily | weekly"
}
```

### `GET /api/v1/alerts/pending` — list of unactioned alerts for the logged-in legal aid user

**Alert object shape:**
```json
{
  "alert_id": "uuid",
  "case_id": "uuid",
  "triggered_at": "ISO 8601 datetime",
  "reason": "eligibility_status changed to eligible_now",
  "is_acknowledged": false
}
```

---

## 8. MEMBER 2 — Frontend/Gateway Consumption Rule

Frontend **never calls layer services directly** — always through the API Gateway (`/api/v1/...`), which internally routes to each service. This means:
- Member 2 only needs to know the routes and JSON shapes defined above — not each layer's internal implementation.
- If any layer owner needs to change their internal logic, **the request/response shape above must stay the same**, or it must be announced to the team first and this document updated.

---

## 9. SUMMARIZED RAG PROMPT (Member 1 — Starting Point, Refine From Here)

Use this as your base system prompt for the LLM call in Layer 2. Keep it short; let the retrieved documents carry the weight, not the instructions.

```
You are a legal research assistant. You are given a case's offense
category and discretionary factors, plus retrieved excerpts from real
Indian judgments and statutes.

Your task: summarize what these sources say about the given factors,
in 2-3 sentences per source, in neutral, factual language.

Rules:
- Never state whether bail should be granted or denied.
- Never use words like "should," "recommend," "likely," or "advise."
- Always attribute each point to its source (case name or section).
- If sources conflict, state that plainly instead of resolving it yourself.
- End every response with: "Final determination rests with the
  presiding judicial authority."

Case offense category: {offense_category}
Discretionary factors to address: {discretion_factors}
Retrieved sources: {retrieved_documents}
```

---

## 10. HOW THIS PREVENTS MERGE CONFLICTS

- Everyone builds their service **independently**, each exposing only the routes defined above — no one needs to touch another member's code.
- The `Case` object (Section 2) is the only shared data structure — **only Member 4 writes to it**; everyone else reads it via `GET /api/v1/cases/{case_id}` (Member 2 exposes this through the gateway, backed by Member 4's service).
- Any change to a route's request/response shape must be a **team-announced change to this document first**, then implemented — never a silent change.
- Each member's service can be developed, tested, and containerized in total isolation, then wired together by Member 2 at the gateway layer — this is what makes six people building in parallel actually safe.
