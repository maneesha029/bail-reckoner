"""Citation retrieval and neutral case-summary generation."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Callable

from config import ANTHROPIC_API_KEY
from embed import find_relevant_documents, load_section_index
from schemas import CaseSummaryRequest, CaseSummaryResponse, CitedSection, model_dump, utc_now

BLOCKED_PHRASES = (
    "should", "recommend", "likely", "advise", "eligible for release",
    "grant bail", "deny bail", "granted bail", "denied bail",
)
DISCLAIMER = (
    "This output surfaces relevant law and precedent only. It does not constitute "
    "a bail recommendation. Final determination rests with the presiding judicial authority."
)
SYSTEM_PROMPT = """You are a legal research assistant. Summarize only supplied Indian legal sources.
Use neutral, factual language. Never recommend or predict a bail outcome, determine eligibility,
or provide legal advice. Attribute each point to the supplied source. Do not invent facts or sections.
"""
SUMMARY_SYSTEM_PROMPT = """You summarize a case for a legal aid worker.
Describe only charges and notes supplied by the user and validated statutory descriptions.
Use 2-3 plain-English factual sentences. Do not make a bail recommendation, predict an outcome,
determine eligibility, or provide legal advice. Do not invent facts, charges, or sections.
"""


def violates_citation_guardrail(text: str) -> bool:
    lowered = text.casefold()
    return any(re.search(rf"(?<![a-z]){re.escape(phrase)}(?![a-z])", lowered)
               for phrase in BLOCKED_PHRASES)


def _anthropic_text(system: str, prompt: str) -> str:
    if not ANTHROPIC_API_KEY:
        raise RuntimeError("Anthropic API key is not configured")
    import anthropic

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY, timeout=20.0, max_retries=0)
    response = client.messages.create(
        model="claude-opus-5",
        max_tokens=300,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return "\n".join(block.text for block in response.content if getattr(block, "type", None) == "text").strip()


def _safe_summary(request: CaseSummaryRequest, cited: list[CitedSection]) -> str:
    pieces = []
    for charge in request.charges:
        item = f"{charge.act} Section {charge.section} ({charge.offense_category})"
        match = next((entry for entry in cited if entry.act == charge.act and entry.section == charge.section), None)
        if match:
            item += f", described in the available legal source as {match.description}"
        pieces.append(item)
    summary = "The supplied case concerns allegations recorded under " + "; ".join(pieces) + "."
    if request.case_notes and request.case_notes.strip():
        summary += " The supplied case notes state: " + request.case_notes.strip() + "."
    return summary


def _validated_sections(request: CaseSummaryRequest) -> list[CitedSection]:
    index = load_section_index()
    validated = []
    seen = set()
    for charge in request.charges:
        key = (charge.act, charge.section)
        if key in seen:
            continue
        seen.add(key)
        entry = next((row for row in index if row["act"] == charge.act and row["section"] == charge.section), None)
        if entry:
            validated.append(CitedSection(
                section=entry["section"], act=entry["act"], description=entry["description"],
            ))
    return validated


def summarize_case(request: CaseSummaryRequest | dict[str, Any], llm: Callable[[str, str], str] | None = None) -> CaseSummaryResponse:
    if not isinstance(request, CaseSummaryRequest):
        request = CaseSummaryRequest(**request)
    cited = _validated_sections(request)
    charge_json = json.dumps([model_dump(charge) for charge in request.charges], ensure_ascii=False)
    prompt = (
        "Summarize this case in 2-3 plain-English sentences for a legal aid worker.\n"
        "Describe only the charges and information supplied in the request.\n"
        "Do not make a bail recommendation, predict an outcome, determine eligibility, or provide legal advice.\n"
        "Charges:\n" + charge_json + "\nNotes:\n" + (request.case_notes or "") +
        "\nValidated statutory material:\n" + json.dumps([model_dump(x) for x in cited])
    )
    generate = llm or _anthropic_text
    try:
        candidate = generate(SUMMARY_SYSTEM_PROMPT, prompt).strip()
    except Exception:
        # Offline operation remains source-grounded; an unavailable LLM cannot cause
        # an invented legal statement or make the endpoint unusable for local smoke tests.
        candidate = _safe_summary(request, cited)
    if not candidate or violates_citation_guardrail(candidate):
        candidate = _safe_summary(request, cited)
    if violates_citation_guardrail(candidate):
        raise RuntimeError("summary failed citation-only safety validation")
    return CaseSummaryResponse(
        case_id=request.case_id,
        summary=candidate,
        cited_sections=cited,
        generated_at=utc_now(),
    )


def search_precedent(offense_category: str, discretion_factors: list[str]) -> list[dict[str, Any]]:
    """Retrieve source-grounded citations, preserving the original search API."""
    factor = discretion_factors[0] if discretion_factors else "general_precedent"
    documents = find_relevant_documents(offense_category, discretion_factors)
    results = []
    for rank, document in enumerate(documents):
        text = document["text"].strip()
        citation_text = text if text.endswith("Final determination rests with the presiding judicial authority.") else (
            text + " Final determination rests with the presiding judicial authority."
        )
        if violates_citation_guardrail(citation_text):
            continue
        results.append({
            "citation_id": document["document_id"],
            "case_name": document["title"],
            "citation_text": citation_text,
            "source_url": document["source_url"],
            "relevance_score": max(0.0, min(1.0, float(document.get("score", 1.0 - rank * 0.1)))),
            "applicable_factor": factor,
        })
    return results
