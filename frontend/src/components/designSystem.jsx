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
  danger: "#8A2F2F",
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

// ---- Avatar ----
// The real cases table has no photo_url or name field yet - prisoner_id
// is being used to carry a display name as a stopgap (see seed_cases.py).
// Every avatar renders as generated initials on a stable color, so the
// roster looks like real product data rather than a wall of placeholders.
function initials(name) {
  if (!name) return "?";
  const parts = name.trim().split(/\s+/);
  return ((parts[0]?.[0] || "") + (parts[1]?.[0] || "")).toUpperCase();
}
function colorFor(name) {
  const palette = ["#2F5233", "#8A6D1F", "#1B2A4A", "#8A2F2F", "#5B4A8A", "#2F5C6B"];
  let hash = 0;
  for (const ch of name || "?") hash = (hash * 31 + ch.charCodeAt(0)) % palette.length;
  return palette[hash];
}
export function Avatar({ name, photoUrl, size = 48 }) {
  if (photoUrl) {
    return (
      <img
        src={photoUrl}
        alt={`Photo of ${name}`}
        style={{
          width: size, height: size, borderRadius: "50%", objectFit: "cover",
          border: `1px solid ${TOKENS.rule}`, flexShrink: 0,
        }}
      />
    );
  }
  const bg = colorFor(name);
  return (
    <div
      title={name}
      style={{
        width: size, height: size, borderRadius: "50%", flexShrink: 0,
        background: bg, color: "#F7F6F3",
        display: "flex", alignItems: "center", justifyContent: "center",
        fontFamily: FONTS.mono, fontSize: size * 0.36, fontWeight: 600,
      }}
    >
      {initials(name)}
    </div>
  );
}

// ---- TabBar ----
export function TabBar({ tabs, active, onChange }) {
  return (
    <div style={{ display: "flex", gap: 4, borderBottom: `1px solid ${TOKENS.rule}`, marginBottom: 28 }}>
      {tabs.map((tab) => {
        const isActive = tab.id === active;
        return (
          <button
            key={tab.id}
            onClick={() => onChange(tab.id)}
            style={{
              fontFamily: FONTS.mono, fontSize: 12, letterSpacing: "0.06em",
              textTransform: "uppercase", padding: "10px 18px", cursor: "pointer",
              background: "none", border: "none",
              color: isActive ? TOKENS.ink : TOKENS.inkSoft,
              borderBottom: isActive ? `2px solid ${TOKENS.seal}` : "2px solid transparent",
              marginBottom: -1, transition: "color 120ms ease",
            }}
          >
            {tab.label}
            {typeof tab.count === "number" && (
              <span style={{ opacity: 0.6, marginLeft: 6 }}>({tab.count})</span>
            )}
          </button>
        );
      })}
    </div>
  );
}

// ---- Shared button styles ----
export function ActionButton({ children, onClick, variant = "primary", disabled }) {
  const styles = {
    primary: { background: TOKENS.ink, color: TOKENS.paper, border: "none" },
    danger: { background: "white", color: TOKENS.danger, border: `1px solid ${TOKENS.danger}` },
    neutral: { background: "white", color: TOKENS.ink, border: `1px solid ${TOKENS.rule}` },
  }[variant];

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      style={{
        fontFamily: FONTS.body, fontSize: 13, fontWeight: 600, padding: "10px 18px",
        cursor: disabled ? "not-allowed" : "pointer", opacity: disabled ? 0.5 : 1,
        ...styles,
      }}
    >
      {children}
    </button>
  );
}

export function Pill({ children, color }) {
  return (
    <span style={{
      fontFamily: FONTS.mono, fontSize: 10.5, letterSpacing: "0.05em", textTransform: "uppercase",
      padding: "3px 8px", borderRadius: 3, border: `1px solid ${color || TOKENS.rule}`,
      color: color || TOKENS.inkSoft,
    }}>
      {children}
    </span>
  );
}