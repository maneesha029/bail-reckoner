# Monitoring & Outreach Engine (Member 5)

Scheduled scanning/alerts + real-world data sourcing (RTI, NCRB, synthetic
dataset generation).

## Run locally
```
pip install -r requirements.txt
uvicorn main:app --port 8005
```

## Routes
- POST /api/v1/alerts/config
- GET /api/v1/alerts/pending
- GET /api/v1/alerts/scan (internal/scheduler-triggered)

## Data track (run these from /data)
```
python fetch_ncrb_data.py
python generate_synthetic_data.py
```

## Also owns (do today, not later)
- File both RTIs (NCRB + state prison dept) - see docs/RTI templates
- Legal outreach coordination
