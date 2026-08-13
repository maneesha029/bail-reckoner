// Shared design system - imported by all three dashboard pages.
// Change these values once, all pages stay consistent.

export const TOKENS = {
  paper: "#F7F6F3",
  ink: "#1B2A4A",
  inkSoft: "#5B6472",
  rule: "#D8DCE3",
  seal: "#B8860B",
  sealEligible: "#2F5233",
  sealPending: "#8A6D1F",
};

export const FONTS = {
  display: "'Source Serif 4', serif",
  body: "'IBM Plex Sans', sans-serif",
  mono: "'IBM Plex Mono', monospace",
};

export function CaseSeal({ status, size = 96 }) {
  const isEligible = status === "eligible_now" || status === "eligible_first_time_offender_rule";
  const color = isEligible ? TOKENS.sealEligible : TOKENS.sealPending;
  const label = isEligible ? "Eligible" : status === "not_yet_eligible" ? "Not Yet" : "Pending";
  return (
    <div
      style={{
        width: size, height: size, borderRadius: "50%", border: `2px solid ${color}`,
        display: "flex", alignItems: "center", justifyContent: "center",
        transform: "rotate(-6deg)", position: "relative", flexShrink: 0,
      }}
    >
      <div style={{ position: "absolute", inset: 6, borderRadius: "50%", border: `1px solid ${color}` }} />
      <span style={{
        fontFamily: FONTS.mono, fontSize: size < 80 ? 9 : 11, fontWeight: 500,
        letterSpacing: "0.12em", textTransform: "uppercase", color, textAlign: "center", lineHeight: 1.3,
      }}>
        {label}
      </span>
    </div>
  );
}

export function Eyebrow({ children, color }) {
  return (
    <p style={{
      fontFamily: FONTS.mono, fontSize: 11, letterSpacing: "0.1em",
      textTransform: "uppercase", color: color || TOKENS.inkSoft, marginBottom: 8,
    }}>
      {children}
    </p>
  );
}
