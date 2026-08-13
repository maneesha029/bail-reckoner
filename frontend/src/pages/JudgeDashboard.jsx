import { useState } from "react";
import { checkEligibility, searchPrecedent, getProceduralRequirements } from "../api/client";
import { TOKENS, FONTS, CaseSeal, Eyebrow } from "../components/designSystem";

export default function JudgeDashboard({ token }) {
  const [caseId, setCaseId] = useState("");
  const [result, setResult] = useState(null);

  const loadCase = async () => {
    if (!caseId) return;
    const [eligibility, precedent, procedural] = await Promise.all([
      checkEligibility(caseId, token),
      searchPrecedent(caseId, { offense_category: "general", discretion_factors: ["flight_risk", "witness_influence"] }, token),
      getProceduralRequirements(caseId, token),
    ]);
    setResult({ eligibility: eligibility.data, precedent: precedent.data, procedural: procedural.data });
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

      <div style={{ display: "flex", gap: 12, marginBottom: 32 }}>
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
          Load reference
        </button>
      </div>

      {!result && (
        <p style={{ color: TOKENS.inkSoft, fontStyle: "italic" }}>No case loaded.</p>
      )}

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

            <section>
              <Eyebrow>Procedural summary</Eyebrow>
              <p style={{ fontSize: 14, margin: 0 }}>
                {result.procedural.bond_type.replace(/_/g, " ")} · ₹{result.procedural.estimated_fine_amount_inr}
              </p>
            </section>
          </div>
        </div>
      )}
    </div>
  );
}
