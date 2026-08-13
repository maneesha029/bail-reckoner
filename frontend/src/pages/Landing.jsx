// import { TOKENS, FONTS, Eyebrow } from "../components/designSystem";
import { TOKENS, FONTS, Eyebrow } from "../components/designSystem";

const ROLES = [
  {
    id: "undertrial",
    ref: "ROLE — 01",
    title: "Undertrial",
    description: "Check your case status and what it means for your release, in plain language.",
  },
  {
    id: "legal_aid",
    ref: "ROLE — 02",
    title: "Legal Aid / Jail Officer",
    description: "Review your docket: eligibility, precedent, procedural checklist, and bond-waiver flags.",
  },
  {
    id: "judge",
    ref: "ROLE — 03",
    title: "Judicial Authority",
    description: "Reference material for cases before you. No recommendation is made — the determination is yours.",
  },
];

function RoleCard({ role, onSelect }) {
  return (
    <button
      onClick={() => onSelect(role.id)}
      style={{
        textAlign: "left", background: "white", border: `1px solid ${TOKENS.rule}`,
        borderTop: `3px solid ${TOKENS.seal}`, padding: "28px 26px", cursor: "pointer",
        display: "flex", flexDirection: "column", gap: 14, minHeight: 200,
        transition: "transform 120ms ease, box-shadow 120ms ease",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = "translateY(-2px)";
        e.currentTarget.style.boxShadow = "0 8px 20px rgba(27, 42, 74, 0.08)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = "translateY(0)";
        e.currentTarget.style.boxShadow = "none";
      }}
    >
      <span style={{
        fontFamily: FONTS.mono, fontSize: 11, letterSpacing: "0.12em",
        color: TOKENS.seal, textTransform: "uppercase",
      }}>
        {role.ref}
      </span>
      <h2 style={{
        fontFamily: FONTS.display, fontSize: 22, fontWeight: 700,
        color: TOKENS.ink, margin: 0,
      }}>
        {role.title}
      </h2>
      <p style={{
        fontFamily: FONTS.body, fontSize: 14.5, lineHeight: 1.6,
        color: TOKENS.inkSoft, margin: 0, flex: 1,
      }}>
        {role.description}
      </p>
      <span style={{
        fontFamily: FONTS.mono, fontSize: 12, fontWeight: 500,
        color: TOKENS.ink, letterSpacing: "0.04em",
        display: "flex", alignItems: "center", gap: 6,
      }}>
        ENTER →
      </span>
    </button>
  );
}

export default function Landing({ onSelectRole }) {
  return (
    <div style={{
      background: TOKENS.paper, minHeight: "100vh",
      display: "flex", alignItems: "center", justifyContent: "center",
      padding: "60px 24px", fontFamily: FONTS.body,
    }}>
      <div style={{ maxWidth: 900, width: "100%" }}>
        <div style={{
          textAlign: "center", marginBottom: 48, paddingBottom: 32,
          borderBottom: `1px solid ${TOKENS.rule}`,
        }}>
          <Eyebrow>Bail Reckoner</Eyebrow>
          <h1 style={{
            fontFamily: FONTS.display, fontSize: 38, fontWeight: 700,
            color: TOKENS.ink, margin: "8px 0 12px",
          }}>
            A record of where each case stands
          </h1>
          <p style={{
            fontFamily: FONTS.body, fontSize: 15, color: TOKENS.inkSoft,
            maxWidth: 460, margin: "0 auto",
          }}>
            Select how you're accessing the docket. Every action here is logged.
          </p>
        </div>

        <div style={{
          display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
          gap: 20,
        }}>
          {ROLES.map((role) => (
            <RoleCard key={role.id} role={role} onSelect={onSelectRole} />
          ))}
        </div>
      </div>
    </div>
  );
}