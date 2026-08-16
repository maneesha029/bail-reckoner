// Single place all API calls go through - never call backend services
// directly from a component, always go through the gateway.
const GATEWAY_BASE = import.meta.env.VITE_GATEWAY_URL || "http://localhost:8000";

async function apiCall(path, method = "GET", body = null, token = null) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const resp = await fetch(`${GATEWAY_BASE}${path}`, {
    method, headers, body: body ? JSON.stringify(body) : undefined,
  });
  return resp.json();
}

export const checkEligibility = (caseId, token) =>
  apiCall("/api/v1/eligibility/check", "POST", { case_id: caseId }, token);

export const searchPrecedent = (caseId, queryContext, token) =>
  apiCall("/api/v1/precedent/search", "POST",
    { case_id: caseId, query_context: queryContext }, token);

export const getProceduralRequirements = (caseId, token) =>
  apiCall("/api/v1/procedural/requirements", "POST", { case_id: caseId }, token);

export const checkBondWaiver = (caseId, hardshipIndicators, token) =>
  apiCall("/api/v1/bond-waiver/check", "POST",
    { case_id: caseId, hardship_indicators: hardshipIndicators }, token);

export const login = (username, password) =>
  apiCall("/api/v1/auth/login", "POST", { username, password });
