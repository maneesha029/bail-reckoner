# Trust & Access Layer (Member 4)

Auth, RBAC, and tamper-evident audit logging. Everyone else calls into
this service - prioritize getting a basic version live early.

## Run locally
```
pip install -r requirements.txt
uvicorn main:app --port 8004
python test_tamper.py   # live tamper-detection demonstration
```

## Routes
- POST /api/v1/auth/login
- POST /api/v1/audit/log (internal, called by all other services)
- GET /api/v1/audit/logs/{case_id}
