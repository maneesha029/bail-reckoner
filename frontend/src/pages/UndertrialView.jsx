import { useState } from "react";
import { checkEligibility } from "../api/client";
import { TOKENS, FONTS, CaseSeal } from "../components/designSystem";

const PLAIN_LANGUAGE = {
  eligible_now: "You may already qualify for release. Your legal aid contact has been notified.",
  eligible_first_time_offender_rule: "As this may be your first offense, you may already qualify for release under a shorter waiting period. Your legal aid contact has been notified.",
  not_yet_eligible: "You do not yet qualify for automatic release, based on time served so far.",
  insufficient_data: "We don't have enough information yet to check your status. Please speak with your legal aid contact.",
};

export default function UndertrialView({ token }) {
  const [caseId, setCaseId] = useState("");
  const [result, setResult] = useState(null);

  const loadStatus = async () => {
    if (!caseId) return;
    const eligibility = await checkEligibility(caseId, token);
    setResult(eligibility.data);
  };

  return (
    <div style={{
      background: TOKENS.paper, minHeight: "100vh", padding: "32px 24px",
      fontFamily: FONTS.body, color: TOKENS.ink, maxWidth: 480, margin: "0 auto",
    }}>
      <h1 style={{ fontFamily: FONTS.display, fontSize: 26, fontWeight: 700, marginBottom: 24 }}>
        Your case status
      </h1>

      <div style={{ display: "flex", gap: 10, marginBottom: 28 }}>
        <input
          value={caseId} onChange={(e) => setCaseId(e.target.value)}
          placeholder="Your case ID"
          style={{
            fontFamily: FONTS.mono, fontSize: 14, padding: "12px 14px",
            border: `1px solid ${TOKENS.rule}`, background: "white", flex: 1,
          }}
        />
        <button
          onClick={loadStatus}
          style={{
            fontFamily: FONTS.body, fontSize: 14, fontWeight: 600, padding: "12px 20px",
            background: TOKENS.ink, color: TOKENS.paper, border: "none", cursor: "pointer",
          }}
        >
          Check
        </button>
      </div>

      {result && (
        <div style={{ textAlign: "center" }}>
          <div style={{ display: "flex", justifyContent: "center", marginBottom: 20 }}>
            <CaseSeal status={result.eligibility_status} size={110} />
          </div>
          <p style={{ fontSize: 17, lineHeight: 1.6, marginBottom: 20 }}>
            {PLAIN_LANGUAGE[result.eligibility_status] || PLAIN_LANGUAGE.insufficient_data}
          </p>
          <p style={{ fontSize: 13, color: TOKENS.inkSoft }}>
            This is not legal advice. Please speak with your legal aid provider about your case.
          </p>
        </div>
      )}
    </div>
  );
}
