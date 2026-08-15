import { useState } from "react";
import { checkEligibility, searchPrecedent, getProceduralRequirements, checkBondWaiver, getAuditLog } from "../api/client";
import { TOKENS, FONTS, CaseSeal, Eyebrow, TabBar, ActionButton, Pill } from "../components/designSystem";
import RosterTab from "./RosterTab";
import CalendarTab from "./CalendarTab";

function Docket({ cases, activeId, onSelect }) {
  return (
    <div style={{ borderRight: `1px solid ${TOKENS.rule}`, paddingRight: 20 }}>
      <Eyebrow>Docket — {cases.length} cases</Eyebrow>
      {cases.map((c) => (
        <button
          key={c.case_id}
          onClick={() => onSelect(c.case_id)}
          style={{
            display: "block", width: "100%", textAlign: "left", padding: "12px 0",
            borderTop: `1px solid ${TOKENS.rule}`, background: "none", border: "none",
            borderBottom: c.case_id === activeId ? `2px solid ${TOKENS.ink}` : "none",
            cursor: "pointer",
          }}
        >
          <div style={{ fontFamily: FONTS.mono, fontSize: 12, color: TOKENS.inkSoft }}>
            {c.case_id}
          </div>
          <div style={{ fontFamily: FONTS.display, fontSize: 15, fontWeight: 600, color: TOKENS.ink, marginTop: 2 }}>
            {c.offense || "Undertrial case"}
          </div>
        </button>
      ))}
    </div>
  );
}

// NEW: was only ever built into JudgeDashboard - legal aid/officers need to
// see the same decision history, especially the judge's manual_override
// entries. Without it this role has no way to know a decision was made.
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
          <Pill color={e.actor_role === "judge" ? TOKENS.seal : TOKENS.inkSoft}>{e.actor_role}</Pill>
          <span style={{ fontSize: 13 }}>{e.action_type.replace(/_/g, " ")}</span>
          {e.action_payload?.reason && (
            <span style={{ fontSize: 12, color: TOKENS.inkSoft }}>— {e.action_payload.reason}</span>
          )}
          <span style={{ marginLeft: "auto", fontFamily: FONTS.mono, fontSize: 11, color: TOKENS.inkSoft }}>
            {new Date(e.timestamp).toLocaleString()}
          </span>
        </div>
      ))}
    </div>
  );
}

export default function LegalAidDashboard({ token, userId }) {
  const [tab, setTab] = useState("docket");
  const [caseId, setCaseId] = useState("");
  const [result, setResult] = useState(null);
  const [auditEntries, setAuditEntries] = useState(null);
  const [docket, setDocket] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const loadCase = async (idOverride) => {
    const id = idOverride ?? caseId;
    if (!id) return;
    setError("");
    setLoading(true);
    try {
      const [eligibility, precedent, procedural, bondWaiver] = await Promise.all([
        checkEligibility(id, token),
        searchPrecedent(id, { offense_category: "general", discretion_factors: [] }, token),
        getProceduralRequirements(id, token),
        checkBondWaiver(id, {}, token),
      ]);
      setResult({
        eligibility: eligibility.data, precedent: precedent.data,
        procedural: procedural.data, bondWaiver: bondWaiver.data,
      });
      setCaseId(id);
      setDocket((prev) => prev.some((c) => c.case_id === id) ? prev
        : [...prev, { case_id: id, offense: "Loaded case" }]);

      try {
        const log = await getAuditLog(id, token);
        setAuditEntries(log.data || []);
      } catch {
        setAuditEntries([]);
      }
    } catch (err) {
      setError(err.message || "Could not load this case.");
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const openCaseFromElsewhere = (id) => {
    setTab("docket");
    loadCase(id);
  };

  return (
    <div style={{
      background: TOKENS.paper, minHeight: "100vh", padding: "40px 48px",
      fontFamily: FONTS.body, color: TOKENS.ink,
    }}>
      <header style={{ marginBottom: 28, borderBottom: `1px solid ${TOKENS.rule}`, paddingBottom: 20 }}>
        <Eyebrow>Bail Reckoner — Legal Aid Docket</Eyebrow>
        <h1 style={{ fontFamily: FONTS.display, fontSize: 30, fontWeight: 700, margin: 0 }}>
          Case review
        </h1>
      </header>

      <TabBar
        active={tab}
        onChange={setTab}
        tabs={[
          { id: "docket", label: "Docket" },
          { id: "roster", label: "Roster" },
          { id: "calendar", label: "Calendar" },
        ]}
      />

      {tab === "roster" && <RosterTab onOpenCase={openCaseFromElsewhere} token={token} />}
      {tab === "calendar" && <CalendarTab token={token} userId={userId} />}

      {tab === "docket" && (
        <>
          <div style={{ display: "flex", gap: 12, marginBottom: 32, alignItems: "center" }}>
            <input
              value={caseId} onChange={(e) => setCaseId(e.target.value)}
              placeholder="e.g. case-001"
              style={{
                fontFamily: FONTS.mono, fontSize: 13, padding: "10px 14px",
                border: `1px solid ${TOKENS.rule}`, background: "white", flex: 1, maxWidth: 320,
              }}
            />
            <ActionButton onClick={() => loadCase()} disabled={loading}>
              {loading ? "Loading..." : "Open case"}
            </ActionButton>
          </div>

          {error && <p style={{ color: TOKENS.danger, fontSize: 13, marginBottom: 24 }}>{error}</p>}

          <div style={{ display: "grid", gridTemplateColumns: "220px 1fr", gap: 32 }}>
            <Docket cases={docket} activeId={caseId} onSelect={(id) => loadCase(id)} />

            <div>
              {!result && !loading && (
                <p style={{ color: TOKENS.inkSoft, fontStyle: "italic" }}>
                  No case open. Enter a case ID above, or pick someone from the Roster tab.
                </p>
              )}

              {result && (
                <div style={{ display: "flex", gap: 28 }}>
                  <CaseSeal status={result.eligibility.eligibility_status} />

                  <div style={{ flex: 1 }}>
                    <section style={{ marginBottom: 24 }}>
                      <Eyebrow>Custody status</Eyebrow>
                      <p style={{ fontSize: 15, lineHeight: 1.6, margin: 0 }}>
                        <strong>{result.eligibility.days_served}</strong> days served against a
                        threshold of <strong>{result.eligibility.days_required}</strong> days
                        ({result.eligibility.threshold_rule_applied.replace(/_/g, " ")}).
                      </p>
                    </section>

                    <section style={{ marginBottom: 24 }}>
                      <Eyebrow>Precedent</Eyebrow>
                      {result.precedent.results.map((r) => (
                        <p key={r.citation_id} style={{
                          fontSize: 14, lineHeight: 1.6, borderLeft: `2px solid ${TOKENS.seal}`,
                          paddingLeft: 12, marginBottom: 10,
                        }}>
                          <em>{r.case_name}</em> — {r.citation_text}
                        </p>
                      ))}
                      <p style={{ fontSize: 12, color: TOKENS.inkSoft, fontStyle: "italic" }}>
                        {result.precedent.disclaimer}
                      </p>
                    </section>

                    <section style={{ marginBottom: 24 }}>
                      <Eyebrow>Procedural checklist</Eyebrow>
                      {result.procedural.procedural_steps.map((s) => (
                        <div key={s.step_number} style={{ display: "flex", gap: 10, marginBottom: 6 }}>
                          <span style={{ fontFamily: FONTS.mono, fontSize: 12, color: TOKENS.seal }}>
                            {String(s.step_number).padStart(2, "0")}
                          </span>
                          <span style={{ fontSize: 14 }}>{s.description}</span>
                        </div>
                      ))}
                    </section>

                    {result.bondWaiver.is_flagged_for_waiver && (
                      <section style={{
                        borderTop: `2px solid ${TOKENS.seal}`, marginTop: 14,
                        background: "#FFF9EC", padding: 16,
                      }}>
                        <Eyebrow color={TOKENS.seal}>⚑ Flagged — indigent bond waiver review</Eyebrow>
                        <p style={{ fontSize: 13, color: TOKENS.inkSoft, margin: 0 }}>
                          {result.bondWaiver.reasoning_summary} ({result.bondWaiver.governing_section})
                        </p>
                      </section>
                    )}

                    {/* NEW: this section didn't exist before - it's the whole
                        point of this fix. Shows the judge's decision (and
                        every system check) to the legal aid / officer role. */}
                    <section style={{ borderTop: `1px solid ${TOKENS.rule}`, paddingTop: 20, marginTop: 24 }}>
                      <Eyebrow>Recorded actions on this case</Eyebrow>
                      <AuditHistory entries={auditEntries} />
                    </section>
                  </div>
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}