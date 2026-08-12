from routing import resolve_target


def test_eligibility_route_resolves():
    assert "8001" in resolve_target("/api/v1/eligibility/check")


def test_precedent_route_resolves():
    assert "8002" in resolve_target("/api/v1/precedent/search")


def test_unknown_route_returns_none():
    assert resolve_target("/api/v1/unknown/thing") is None
