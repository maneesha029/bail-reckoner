"""Tests for the citation search and neutral case-summary endpoints."""
from fastapi.testclient import TestClient

import routes
from logic import search_precedent, summarize_case, violates_citation_guardrail
from main import app


client = TestClient(app)


def test_guardrail_catches_recommendation_language():
    for text in (
        "The person should be granted bail.",
        "The accused is likely to receive bail; counsel may advise release.",
        "The court should deny bail.",
    ):
        assert violates_citation_guardrail(text)


def test_guardrail_allows_neutral_text():
    assert not violates_citation_guardrail("The court described the statutory framework.")


def test_search_returns_source_grounded_category_result():
    results = search_precedent("economic_offences", ["flight_risk"])
    assert results
    assert all(result["source_url"].startswith("https://") for result in results)
    assert all(not violates_citation_guardrail(result["citation_text"]) for result in results)


def test_valid_summary_has_required_shape_and_disclaimer_free_neutral_text():
    response = client.post("/api/v1/precedent/summarize", json={
        "case_id": "case-1",
        "charges": [{"act": "IT_Act", "section": "66C", "offense_category": "cyber_crimes"}],
    })
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["case_id"] == "case-1"
    assert body["data"]["summary"]
    assert body["data"]["generated_at"]
    assert body["data"]["cited_sections"] == [{
        "section": "66C", "act": "IT_Act",
        "description": "Identity theft: dishonestly or fraudulently making use of the electronic signature, password or any other unique identification feature of another person.",
    }]
    assert not violates_citation_guardrail(body["data"]["summary"])


def test_summary_accepts_omitted_and_null_notes():
    for notes in ("omitted", None):
        payload = {
            "case_id": "case-notes",
            "charges": [{"act": "IT_Act", "section": "66C", "offense_category": "cyber_crimes"}],
        }
        if notes is None:
            payload["case_notes"] = None
        response = client.post("/api/v1/precedent/summarize", json=payload)
        assert response.json()["success"] is True


def test_malformed_summary_request_uses_standard_error_envelope():
    response = client.post("/api/v1/precedent/summarize", json={"case_id": "", "charges": []})
    assert response.status_code == 422
    assert response.json() == {
        "success": False, "data": None,
        "error": {"code": "VALIDATION_ERROR", "message": "Request validation failed."},
    }


def test_unsupported_section_is_not_returned_as_validated_citation():
    result = summarize_case({
        "case_id": "case-unsupported",
        "charges": [{"act": "IT_Act", "section": "999Z", "offense_category": "cyber_crimes"}],
    })
    assert result.cited_sections == []
    assert "999Z" in result.summary


def test_summary_guardrail_replaces_unsafe_llm_output():
    request = {
        "case_id": "case-guardrail",
        "charges": [{"act": "IT_Act", "section": "66C", "offense_category": "cyber_crimes"}],
    }
    result = summarize_case(request, llm=lambda system, prompt: "The accused should be granted bail.")
    assert not violates_citation_guardrail(result.summary)


def test_summarize_audit_action(monkeypatch):
    calls = []
    monkeypatch.setattr(routes, "_audit", lambda *args: calls.append(args))
    response = client.post("/api/v1/precedent/summarize", json={
        "case_id": "case-audit",
        "charges": [{"act": "IT_Act", "section": "66C", "offense_category": "cyber_crimes"}],
    })
    assert response.json()["success"] is True
    assert calls and calls[0][3] == "precedent_summarize"


def test_search_preserves_search_audit_action(monkeypatch):
    calls = []
    monkeypatch.setattr(routes, "_audit", lambda *args: calls.append(args))
    response = client.post("/api/v1/precedent/search", json={
        "case_id": "case-search",
        "query_context": {"offense_category": "economic_offences", "discretion_factors": ["flight_risk"]},
    })
    assert response.json()["success"] is True
    assert calls and calls[0][3] == "precedent_search"
