from logic import violates_citation_guardrail, search_precedent


def test_guardrail_catches_recommendation():
    assert violates_citation_guardrail("This person should be granted bail")


def test_guardrail_allows_neutral_text():
    assert not violates_citation_guardrail("The court categorized offenses into groups")


def test_search_returns_results():
    results = search_precedent("economic_offences", ["flight_risk"])
    assert len(results) > 0
    assert results[0]["applicable_factor"] == "flight_risk"
