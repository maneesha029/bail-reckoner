from config import (ELIGIBILITY_SERVICE_URL, PRECEDENT_SERVICE_URL,
                     COMPLIANCE_SERVICE_URL, TRUST_SERVICE_URL, MONITORING_SERVICE_URL)

ROUTE_MAP = {
    "/api/v1/eligibility": ELIGIBILITY_SERVICE_URL,
    "/api/v1/precedent": PRECEDENT_SERVICE_URL,
    "/api/v1/procedural": COMPLIANCE_SERVICE_URL,
    "/api/v1/bond-waiver": COMPLIANCE_SERVICE_URL,
    "/api/v1/discretion": COMPLIANCE_SERVICE_URL,
    "/api/v1/auth": TRUST_SERVICE_URL,
    "/api/v1/audit": TRUST_SERVICE_URL,
    "/api/v1/alerts": MONITORING_SERVICE_URL,
}


def resolve_target(path: str) -> str | None:
    for prefix, base_url in ROUTE_MAP.items():
        if path.startswith(prefix):
            return base_url + path
    return None
