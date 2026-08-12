# API Gateway (Member 6)

Single entry point for the frontend. Routes /api/v1/* to the correct
backend service based on prefix - see routing.py.

## Run locally
```
pip install -r requirements.txt
uvicorn main:app --port 8000
```
