import { useEffect, useState } from "react";
import { TOKENS, FONTS, Avatar, Eyebrow } from "../components/designSystem";
import { getCases } from "../api/client";

export default function RosterTab({ onOpenCase, token }) {
  const [roster, setRoster] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getCases(token)
      .then((res) => setRoster(res.data))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [token]);

  return (
    <div>
      <Eyebrow>All persons — {roster.length} on record</Eyebrow>
      <p style={{ fontSize: 12, color: TOKENS.inkSoft, marginBottom: 20, fontStyle: "italic" }}>
        Live case directory from the eligibility service.
      </p>
      {loading && <p style={{ fontSize: 13, color: TOKENS.inkSoft }}>Loading cases...</p>}
      {error && <p style={{ fontSize: 13, color: "crimson" }}>{error}</p>}
      <div style={{
        display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: 16,
      }}>
        {roster.map((p) => (
          <button
            key={p.case_id}
            onClick={() => onOpenCase(p.case_id)}
            style={{
              textAlign: "left", background: "white", border: `1px solid ${TOKENS.rule}`,
              borderRadius: 4, padding: 16, cursor: "pointer",
              display: "flex", alignItems: "center", gap: 12,
            }}
          >
            <Avatar name={p.name} size={44} />
            <div>
              <div style={{ fontFamily: FONTS.display, fontSize: 15, fontWeight: 600, color: TOKENS.ink }}>
                {p.name}
              </div>
              <div style={{ fontFamily: FONTS.mono, fontSize: 11, color: TOKENS.inkSoft }}>
                {p.case_id}
              </div>
              <div style={{ fontSize: 12, color: TOKENS.inkSoft, marginTop: 4 }}>
                {p.offense}
                {p.is_compoundable && (
                  <span style={{ marginLeft: 6, color: TOKENS.inkSoft, fontStyle: "italic" }}>
                    · compoundable
                  </span>
                )}
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
