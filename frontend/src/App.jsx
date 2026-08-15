import { useState } from "react";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import LegalAidDashboard from "./pages/LegalAidDashboard";
import JudgeDashboard from "./pages/JudgeDashboard";
import UndertrialView from "./pages/UndertrialView";
import { TOKENS, FONTS } from "./components/designSystem";

function BackBar({ onBack, label, username }) {
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
      {username && (
        <span style={{
          marginLeft: "auto", fontFamily: FONTS.mono, fontSize: 11,
          color: TOKENS.paper, opacity: 0.5, letterSpacing: "0.06em",
        }}>
          SIGNED IN AS {username.toUpperCase()}
        </span>
      )}
    </div>
  );
}

export default function App() {
  const [token, setToken] = useState(null);
  const [role, setRole] = useState(null);
  const [userId, setUserId] = useState(null);
  const [username, setUsername] = useState(null);
  const [showLogin, setShowLogin] = useState(false);

  // login() from trust-access-layer returns {access_token, role, user_id} -
  // it does NOT echo back the username, so we carry it up from what was
  // typed into the form (see Login.jsx).
  function handleLogin({ access_token, role: authenticatedRole, user_id, username: uname }) {
    setToken(access_token);
    setRole(authenticatedRole);
    setUserId(user_id);
    setUsername(uname);
  }

  function handleSwitchRole() {
    setToken(null);
    setRole(null);
    setUserId(null);
    setUsername(null);
    setShowLogin(false);
  }

  if (!token || !role) {
    if (showLogin) {
      return <Login onLogin={handleLogin} onBack={() => setShowLogin(false)} />;
    }
    return <Landing onSelectRole={() => setShowLogin(true)} />;
  }

  const views = {
    judge: {
      component: <JudgeDashboard token={token} userId={userId} role={role} />,
      label: "JUDICIAL AUTHORITY",
    },
    undertrial: {
      component: <UndertrialView token={token} userId={userId} />,
      label: "UNDERTRIAL",
    },
    legal_aid: {
      component: <LegalAidDashboard token={token} userId={userId} role={role} />,
      label: "LEGAL AID / JAIL OFFICER",
    },
    jail_officer: {
      component: <LegalAidDashboard token={token} userId={userId} role={role} />,
      label: "LEGAL AID / JAIL OFFICER",
    },
  };

  const current = views[role];

  if (!current) {
    return <div>Unknown role: {role}</div>;
  }

  return (
    <div>
      <BackBar onBack={handleSwitchRole} label={current.label} username={username} />
      {current.component}
    </div>
  );
}