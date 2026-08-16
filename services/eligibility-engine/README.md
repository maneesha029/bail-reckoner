# Eligibility Engine (Member 1)

Computes statutory bail eligibility under Section 436A CrPC / Section 479 BNSS.

## Run locally
```
pip install -r requirements.txt
uvicorn main:app --port 8001
```

## Routes
- POST /api/v1/eligibility/check
- GET /api/v1/eligibility/{case_id}
- POST /api/v1/eligibility/override

## Known open item
The multi-charge "longest max sentence wins" rule in logic.py is an
engineering assumption, NOT yet legally validated. See
docs/LEGAL_VALIDATION_QUESTIONS.md - this is the #1 question to ask
your legal aid / law college contact.
