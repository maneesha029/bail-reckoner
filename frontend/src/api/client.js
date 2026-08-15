// Single place all API calls go through - never call backend services
// directly from a component, always go through the gateway.
const GATEWAY_BASE = import.meta.env.VITE_GATEWAY_URL || "http://localhost:8000";

async function apiCall(path, method = "GET", body = null, token = null, extraHeaders = {}) {
  const headers = { "Content-Type": "application/json", ...extraHeaders };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  let resp;
  try {
    resp = await fetch(`${GATEWAY_BASE}${path}`, {
      method, headers, body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new Error("Could not reach the server. Check your connection and try again.");
  }

  let data;
  try {
    data = await resp.json();
  } catch {
    throw new Error(`Server returned an unexpected response (status ${resp.status}).`);
  }

  // Every real endpoint returns {success, data, error} - but some raise
  // raw FastAPI HTTPExceptions (404 case not found, 403 forbidden) which
  // come back as {"detail": "..."} instead. Handle both shapes.
  if (!resp.ok || data?.success === false) {
    const message = data?.error?.message || data?.detail || `Request failed (status ${resp.status}).`;
    throw new Error(message);
  }

  return data;
}

// ---- Auth (trust-access-layer) ----

export const login = (username, password) =>
  apiCall("/api/v1/auth/login", "POST", { username, password });

// ---- Eligibility (eligibility-engine) ----

export const checkEligibility = (caseId, token) =>
  apiCall("/api/v1/eligibility/check", "POST", { case_id: caseId }, token);

// Real case directory - replaces the old client-side mockRoster.js.
export const getCases = (token) =>
  apiCall("/api/v1/eligibility/cases", "GET", null, token);

// Judge/legal_aid decision. The real backend has no separate "grant/deny"
// endpoint - /override is the actual decision-recording route. It requires
// an eligibility check to have already run for this case_id (server keeps
// the last computed result in memory), and requires the X-Actor-Role
// header on top of the bearer token.
export const overrideEligibility = (caseId, actorUserId, actorRole, reason, token) =>
  apiCall("/api/v1/eligibility/override", "POST",
    { case_id: caseId, actor_user_id: actorUserId, reason },
    token, { "X-Actor-Role": actorRole });

// ---- Precedent (precedent-engine) ----

export const searchPrecedent = (caseId, queryContext, token) =>
  apiCall("/api/v1/precedent/search", "POST",
    { case_id: caseId, query_context: queryContext }, token);

// ---- Compliance (compliance-engine) ----

export const getProceduralRequirements = (caseId, token) =>
  apiCall("/api/v1/procedural/requirements", "POST", { case_id: caseId }, token);

export const checkBondWaiver = (caseId, hardshipIndicators, token) =>
  apiCall("/api/v1/bond-waiver/check", "POST",
    { case_id: caseId, hardship_indicators: hardshipIndicators }, token);

// ---- Audit (trust-access-layer) ----
// Every case action (eligibility_check, precedent_search, procedural_check,
// bond_waiver_check, manual_override) is already logged server-side by
// each service - the frontend never has to write to this directly, only
// read it back.

export const getAuditLog = (caseId, token) =>
  apiCall(`/api/v1/audit/logs/${caseId}`, "GET", null, token);

// ---- Alerts / calendar (monitoring-engine) ----
// Real endpoints, but PENDING_ALERTS is in-memory and starts empty until
// someone calls /alerts/scan - see triggerAlertScan below.

export const getPendingAlerts = (token) =>
  apiCall("/api/v1/alerts/pending", "GET", null, token);

export const setAlertConfig = (recipientUserId, notifyVia, scanFrequency, token) =>
  apiCall("/api/v1/alerts/config", "POST", {
    recipient_user_id: recipientUserId, notify_via: notifyVia, scan_frequency: scanFrequency,
  }, token);

// Demo-only: manually fire the scan the real cron would trigger, so the
// Calendar tab has something to show without waiting for a scheduler.
export const triggerAlertScan = (token) =>
  apiCall("/api/v1/alerts/scan", "GET", null, token);