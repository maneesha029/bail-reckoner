import { useState } from "react";
import { checkEligibility, searchPrecedent, getProceduralRequirements, checkBondWaiver } from "../api/client";
import { TOKENS, FONTS, CaseSeal, Eyebrow } from "../components/designSystem";

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
            {c.case_id.slice(0, 8)}
          </div>
          <div style={{ fontFamily: FONTS.display, fontSize: 15, fontWeight: 600, color: TOKENS.ink, marginTop: 2 }}>
            {c.offense || "Undertrial case"}
          </div>
        </button>
      ))}
    </div>
  );
}

export default function LegalAidDashboard({ token }) {
  const [caseId, setCaseId] = useState("");
  const [result, setResult] = useState(null);
  const [docket, setDocket] = useState([]);

  const loadCase = async () => {
    if (!caseId) return;
    const [eligibility, precedent, procedural, bondWaiver] = await Promise.all([
      checkEligibility(caseId, token),
      searchPrecedent(caseId, { offense_category: "general", discretion_factors: [] }, token),
      getProceduralRequirements(caseId, token),
      checkBondWaiver(caseId, {}, token),
    ]);
    const data = {
      eligibility: eligibility.data, precedent: precedent.data,
      procedural: procedural.data, bondWaiver: bondWaiver.data,
    };
    setResult(data);
    setDocket((prev) => prev.some((c) => c.case_id === caseId) ? prev
      : [...prev, { case_id: caseId, offense: "Loaded case" }]);
  };

  return (
    <div style={{
      background: TOKENS.paper, minHeight: "100vh", padding: "40px 48px",
      fontFamily: FONTS.body, color: TOKENS.ink,
    }}>
      <header style={{ marginBottom: 36, borderBottom: `1px solid ${TOKENS.rule}`, paddingBottom: 20 }}>
        <Eyebrow>Bail Reckoner — Legal Aid Docket</Eyebrow>
        <h1 style={{ fontFamily: FONTS.display, fontSize: 30, fontWeight: 700, margin: 0 }}>
          Case review
        </h1>
      </header>

      <div style={{ display: "flex", gap: 12, marginBottom: 32, alignItems: "center" }}>
        <input
          value={caseId} onChange={(e) => setCaseId(e.target.value)}
          placeholder="Enter case ID"
          style={{
            fontFamily: FONTS.mono, fontSize: 13, padding: "10px 14px",
            border: `1px solid ${TOKENS.rule}`, background: "white", flex: 1, maxWidth: 320,
          }}
        />
        <button
          onClick={loadCase}
          style={{
            fontFamily: FONTS.body, fontSize: 13, fontWeight: 600, padding: "10px 20px",
            background: TOKENS.ink, color: TOKENS.paper, border: "none", cursor: "pointer",
          }}
        >
          Open case
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "220px 1fr", gap: 32 }}>
        <Docket cases={docket} activeId={caseId} onSelect={setCaseId} />

        <div>
          {!result && (
            <p style={{ color: TOKENS.inkSoft, fontStyle: "italic" }}>
              No case open. Enter a case ID above to begin review.
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
                  <section style={{ borderTop: `1px solid ${TOKENS.rule}`, paddingTop: 14, marginTop: 14 }}>
                    <Eyebrow color={TOKENS.seal}>Flagged — indigent bond waiver review</Eyebrow>
                    <p style={{ fontSize: 13, color: TOKENS.inkSoft, margin: 0 }}>
                      {result.bondWaiver.reasoning_summary} ({result.bondWaiver.governing_section})
                    </p>
                  </section>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
