import { useState } from "react";
import {
  checkEligibility, searchPrecedent, getProceduralRequirements,
  overrideEligibility, getAuditLog,
} from "../api/client";
import { TOKENS, FONTS, CaseSeal, Eyebrow, ActionButton, Pill } from "../components/designSystem";

function AuditHistory({ entries }) {
  if (!entries) return null;
  if (entries.length === 0) {
    return <p style={{ fontSize: 13, color: TOKENS.inkSoft, fontStyle: "italic" }}>No recorded actions on this case yet.</p>;
  }
  return (
    <div>
      {entries.map((e) => (
        <div key={e.log_id} style={{
          display: "flex", alignItems: "center", gap: 10, padding: "8px 0",
          borderBottom: `1px solid ${TOKENS.rule}`,
        }}>
          <Pill color={TOKENS.seal}>{e.actor_role}</Pill>
          <span style={{ fontSize: 13 }}>{e.action_type.replace(/_/g, " ")}</span>
          {e.action_payload?.reason && (
            <span style={{ fontSize: 12, color: TOKENS.inkSoft }}>— {e.action_payload.reason}</span>
          )}
          <span style={{ marginLeft: "auto", fontFamily: FONTS.mono, fontSize: 11, color: TOKENS.inkSoft }}>
            {new Date(e.timestamp).toLocaleString()}
          </span>
          {/* entry_hash proves this row is part of the tamper-evident chain -
              trust-access-layer computes it from the previous row's hash. */}
          <span style={{ fontFamily: FONTS.mono, fontSize: 10, color: TOKENS.rule }} title={e.entry_hash}>
            #{e.entry_hash?.slice(0, 6)}
          </span>
        </div>
      ))}
    </div>
  );
}

export default function JudgeDashboard({ token, userId, role }) {
  const [caseId, setCaseId] = useState("");
  const [result, setResult] = useState(null);
  const [auditEntries, setAuditEntries] = useState(null);
  const [loading, setLoading] = useState(false);
  const [decisionInFlight, setDecisionInFlight] = useState(false);
  const [note, setNote] = useState("");
  const [error, setError] = useState("");

  const refreshAuditLog = async (id) => {
    try {
      const log = await getAuditLog(id, token);
      setAuditEntries(log.data || []);
    } catch {
      setAuditEntries([]);
    }
  };

  const loadCase = async () => {
    if (!caseId) return;
    setError("");
    setLoading(true);
    try {
      const [eligibility, precedent, procedural] = await Promise.all([
        checkEligibility(caseId, token),
        searchPrecedent(caseId, { offense_category: "general", discretion_factors: ["flight_risk", "witness_influence"] }, token),
        getProceduralRequirements(caseId, token),
      ]);
      setResult({ eligibility: eligibility.data, precedent: precedent.data, procedural: procedural.data });
      await refreshAuditLog(caseId);
    } catch (err) {
      setError(err.message || "Could not load this case.");
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  // The real backend has no formal "grant/deny/send-back" field - /override
  // takes a free-text reason. We prefix it so it's still clearly a decision
  // when read back in the audit trail.
  const takeAction = async (label) => {
    setDecisionInFlight(true);
    setError("");
    try {
      const reason = note ? `${label}. ${note}` : label;
      await overrideEligibility(caseId, userId, role, reason, token);
      setNote("");
      await refreshAuditLog(caseId);
    } catch (err) {
      setError(err.message || "Could not record the decision. It was not saved.");
    } finally {
      setDecisionInFlight(false);
    }
  };

  return (
    <div style={{
      background: TOKENS.paper, minHeight: "100vh", padding: "40px 48px",
      fontFamily: FONTS.body, color: TOKENS.ink,
    }}>
      <header style={{ marginBottom: 36, borderBottom: `1px solid ${TOKENS.rule}`, paddingBottom: 20 }}>
        <Eyebrow>Bail Reckoner — Judicial Reference</Eyebrow>
        <h1 style={{ fontFamily: FONTS.display, fontSize: 30, fontWeight: 700, margin: 0 }}>
          Case reference
        </h1>
        <p style={{ fontSize: 13, color: TOKENS.inkSoft, marginTop: 6 }}>
          Reference material only. No recommendation is made — final determination rests with the presiding judicial authority.
        </p>
      </header>

      <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
        <input
          value={caseId} onChange={(e) => setCaseId(e.target.value)}
          placeholder="e.g. case-001"
          style={{
            fontFamily: FONTS.mono, fontSize: 13, padding: "10px 14px",
            border: `1px solid ${TOKENS.rule}`, background: "white", flex: 1, maxWidth: 320,
          }}
        />
        <ActionButton onClick={loadCase} disabled={loading}>
          {loading ? "Loading..." : "Load reference"}
        </ActionButton>
      </div>

      {error && <p style={{ color: TOKENS.danger, fontSize: 13, marginBottom: 24 }}>{error}</p>}
      {!result && !loading && <p style={{ color: TOKENS.inkSoft, fontStyle: "italic" }}>No case loaded.</p>}

      {result && (
        <div style={{ display: "flex", gap: 28 }}>
          <CaseSeal status={result.eligibility.eligibility_status} />
          <div style={{ flex: 1 }}>
            <section style={{ marginBottom: 24 }}>
              <Eyebrow>Statutory time-served calculation</Eyebrow>
              <p style={{ fontSize: 15, lineHeight: 1.6, margin: 0 }}>
                {result.eligibility.days_served} of {result.eligibility.days_required} required days served
                ({result.eligibility.threshold_rule_applied.replace(/_/g, " ")}).
              </p>
            </section>

            <section style={{ marginBottom: 24 }}>
              <Eyebrow>Relevant precedent — flight risk &amp; witness influence</Eyebrow>
              {result.precedent.results.map((r) => (
                <p key={r.citation_id} style={{
                  fontSize: 14, lineHeight: 1.6, borderLeft: `2px solid ${TOKENS.seal}`,
                  paddingLeft: 12, marginBottom: 10,
                }}>
                  <em>{r.case_name}</em> — {r.citation_text}
                </p>
              ))}
            </section>

            <section style={{ marginBottom: 28 }}>
              <Eyebrow>Procedural summary</Eyebrow>
              <p style={{ fontSize: 14, margin: 0 }}>
                {result.procedural.bond_type.replace(/_/g, " ")} · ₹{result.procedural.estimated_fine_amount_inr}
              </p>
            </section>

            <section style={{ borderTop: `1px solid ${TOKENS.rule}`, paddingTop: 20, marginBottom: 24 }}>
              <Eyebrow>Record a decision</Eyebrow>
              <input
                value={note}
                onChange={(e) => setNote(e.target.value)}
                placeholder="Optional note / reasoning"
                style={{
                  fontFamily: FONTS.body, fontSize: 13, padding: "10px 14px",
                  border: `1px solid ${TOKENS.rule}`, width: "100%", maxWidth: 480, marginBottom: 12,
                }}
              />
              <div style={{ display: "flex", gap: 10 }}>
                <ActionButton variant="primary" disabled={decisionInFlight} onClick={() => takeAction("Bail granted")}>
                  Grant Bail
                </ActionButton>
                <ActionButton variant="danger" disabled={decisionInFlight} onClick={() => takeAction("Bail denied")}>
                  Deny
                </ActionButton>
                <ActionButton variant="neutral" disabled={decisionInFlight} onClick={() => takeAction("Sent back for review")}>
                  Send Back for Review
                </ActionButton>
              </div>
            </section>

            <section>
              <Eyebrow>Recorded actions on this case</Eyebrow>
              <AuditHistory entries={auditEntries} />
            </section>
          </div>
        </div>
      )}
    </div>
  );
}