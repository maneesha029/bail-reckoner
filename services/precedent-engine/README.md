# Precedent Engine (Member 2)

RAG-based retrieval of real Indian case law/statutes. Cites only, never
recommends - see logic.py's SYSTEM_PROMPT and citation guardrail.

## Run locally
```
pip install -r requirements.txt
uvicorn main:app --port 8002
```

## Route
POST /api/v1/precedent/search

## Next steps
1. Populate corpus/ with real judgment text
2. Replace logic.search_precedent's placeholder with real Chroma retrieval
   + LLM synthesis (see docs for full pipeline description)
3. Run eval_set.json queries and record real accuracy honestly
