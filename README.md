# Bail Reckoner

A working scaffold implementing the full architecture: Eligibility Engine,
Precedent Engine, Compliance Engine (procedural + bond-waiver), Trust &
Access Layer, Monitoring & Outreach Engine, and the API Gateway/Frontend.

## Status
This is a functional SCAFFOLD, not the final legally-validated system.
Every service has working placeholder logic that returns correctly-shaped,
real responses - but the underlying legal data (offense mappings, judgment
corpus, procedural rules) needs to be populated with real, validated
content before this is demo-ready. See each service's README.md for its
specific next steps.

## Quick start
```
cp .env.example .env
docker-compose up --build
```
Then visit http://localhost:5173 (frontend) - it talks to the gateway at
http://localhost:8000, which routes to all 5 backend services.

## Run tests for any service
```
cd services/eligibility-engine && pip install -r requirements.txt && pytest
```
(repeat per service)

## Architecture
See /docs for the full API contract, member build guides, naming
conventions, and the final integration checklist.

## Team ownership
- Member 1: services/eligibility-engine
- Member 2: services/precedent-engine
- Member 3: services/compliance-engine
- Member 4: services/trust-access-layer
- Member 5: services/monitoring-engine + /data
- Member 6: services/gateway + /frontend
- shared_schemas: published by Member 6, imported by everyone
