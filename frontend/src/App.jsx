import { useState } from "react";
import Landing from "./pages/Landing";
import LegalAidDashboard from "./pages/LegalAidDashboard";
import JudgeDashboard from "./pages/JudgeDashboard";
import UndertrialView from "./pages/UndertrialView";
import { TOKENS, FONTS } from "./components/designSystem";

function BackBar({ onBack, label }) {
  return (
    <div style={{
      background: TOKENS.ink, padding: "8px 24px",
      display: "flex", alignItems: "center", gap: 12,
    }}>
      <button
        onClick={onBack}
        style={{
          background: "none", border: "none", color: TOKENS.paper,
          fontFamily: FONTS.mono, fontSize: 11.5, letterSpacing: "0.06em",
          cursor: "pointer", opacity: 0.85, padding: 0,
        }}
      >
        ← SWITCH ROLE
      </button>
      <span style={{
        fontFamily: FONTS.mono, fontSize: 11, color: TOKENS.paper,
        opacity: 0.5, letterSpacing: "0.06em",
      }}>
        {label}
      </span>
    </div>
  );
}

export default function App() {
  const [token] = useState(null);
  const [view, setView] = useState(null); // null | "legal_aid" | "judge" | "undertrial"

  if (!view) {
    return <Landing onSelectRole={setView} />;
  }

  const views = {
    judge: { component: <JudgeDashboard token={token} />, label: "JUDICIAL AUTHORITY" },
    undertrial: { component: <UndertrialView token={token} />, label: "UNDERTRIAL" },
    legal_aid: { component: <LegalAidDashboard token={token} />, label: "LEGAL AID / JAIL OFFICER" },
  };

  const current = views[view];

  return (
    <div>
      <BackBar onBack={() => setView(null)} label={current.label} />
      {current.component}
    </div>
  );
}