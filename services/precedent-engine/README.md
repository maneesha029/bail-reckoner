# Precedent Engine (Member 2)

This service retrieves source-grounded Indian legal material and produces neutral
case summaries. It does not decide, predict, or recommend bail outcomes.

## Run locally

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8002
```

Configuration is read from the environment: `CHROMA_URL` (optional Chroma
server), `ANTHROPIC_API_KEY` (optional for generated summaries; the local
source-grounded fallback remains available without it), and `TRUST_SERVICE_URL`
(for best-effort audit logging).

## Routes

### `POST /api/v1/precedent/search`

Retrieves relevant case law/statutory documents for an offense category and
factor list. Results are citations only and keep the existing standard envelope.

### `POST /api/v1/precedent/summarize`

Summarizes only the charges and optional notes supplied by the caller.

Request:

```json
{
  "case_id": "case-123",
  "charges": [{"act": "IT_Act", "section": "66C", "offense_category": "cyber_crimes"}],
  "case_notes": "The investigation notes supplied by the caller."
}
```

Response data:

```json
{
  "case_id": "case-123",
  "summary": "The supplied case concerns allegations recorded under IT_Act Section 66C (cyber_crimes), described in the available legal source as identity theft.",
  "cited_sections": [{
    "section": "66C",
    "act": "IT_Act",
    "description": "Identity theft: dishonestly or fraudulently making use of the electronic signature, password or any other unique identification feature of another person."
  }],
  "generated_at": "2026-08-14T00:00:00Z"
}
```

The endpoint validates sections against `corpus/section_index.json`, which is
maintained from authoritative India Code material. A requested section absent
from that index is omitted from `cited_sections`; it is never given an invented
description. The summary fallback may mention the supplied section as an
unvalidated allegation, but does not present it as confirmed law.

Anthropic generation is used when `ANTHROPIC_API_KEY` is configured. Generated
text is checked for recommendation, prediction, eligibility, and advice
language; unsafe output is replaced with a deterministic source-grounded
summary. The endpoint never invents facts, charges, statutory sections, legal
advice, or bail outcomes.

Both routes call Member 4's `/api/v1/audit/log` through `TRUST_SERVICE_URL`.
Search uses `precedent_search`; summary uses `precedent_summarize`. Audit
failure is best effort and does not write directly to Member 4's database.

## Corpus and limitations

The starter corpus contains a focused set of real-source references: *Satender
Kumar Antil v. CBI* and statutory material for cyber crime, child-protection,
and SC/ST offense categories. Chroma retrieval is attempted when available;
the deterministic local index is used for offline development. The corpus is
not a substitute for checking the current primary source or legal advice.

Run tests with `python -m pytest -v` from this directory. Build independently
with `docker build -t precedent-engine .`.

Review audit and source limitations before production deployment.
