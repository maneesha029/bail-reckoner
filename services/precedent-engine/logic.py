BLOCKED_PHRASES = ["should", "recommend", "likely to", "eligible for release"]

SYSTEM_PROMPT = """You are a legal research assistant. You are given a case's
offense category and discretionary factors, plus retrieved excerpts from real
Indian judgments and statutes.

Summarize what these sources say about the given factors, in 2-3 sentences
per source, in neutral, factual language.

Rules:
- Never state whether bail should be granted or denied.
- Never use words like "should," "recommend," "likely," or "advise."
- Always attribute each point to its source (case name or section).
- If sources conflict, state that plainly instead of resolving it yourself.
- End every response with: "Final determination rests with the presiding
  judicial authority."
"""


def violates_citation_guardrail(text: str) -> bool:
    lowered = text.lower()
    return any(phrase in lowered for phrase in BLOCKED_PHRASES)


def search_precedent(offense_category: str, discretion_factors: list[str]) -> list[dict]:
    # TODO: replace with real Chroma vector search + LLM synthesis call.
    # This placeholder demonstrates the required OUTPUT SHAPE only.
    return [{
        "citation_id": "mock-citation-1",
        "case_name": "Satender Kumar Antil v. CBI",
        "citation_text": ("The court categorized offenses into groups to guide "
                           "consistent bail decisions. Final determination rests "
                           "with the presiding judicial authority."),
        "source_url": "https://indiankanoon.org/",
        "relevance_score": 0.5,
        "applicable_factor": discretion_factors[0] if discretion_factors else "general_precedent",
    }]
