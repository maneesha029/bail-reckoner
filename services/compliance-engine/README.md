# Compliance Engine (Member 3)

Two features: procedural filing checklist (CrPC 441-450/BNSS) and
indigent bond-waiver flagging (CrPC 436/BNSS equivalent) - the project's
strongest original differentiator.

## Run locally
```
pip install -r requirements.txt
uvicorn main:app --port 8003
```

## Routes
- POST /api/v1/procedural/requirements
- POST /api/v1/bond-waiver/check

Extends Member 1's offenses/cases schema - coordinate before changing it.
