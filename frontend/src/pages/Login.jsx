import { useState } from "react";
import { TOKENS, FONTS } from "../components/designSystem";
import { login } from "../api/client";

export default function Login({ onLogin, onBack }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await login(username, password);
      if (res.success) {
        onLogin({
          access_token: res.data.access_token,
          role: res.data.role,
          user_id: res.data.user_id,
          username, // trust-access-layer doesn't echo this back, so keep what was typed
        });
      } else {
        setError(res.error?.message || "Login failed");
      }
    } catch (err) {
      setError(err.message || "Could not reach the server. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ minHeight: "100vh", display: "flex", background: TOKENS.paper }}>
      <div style={{ flex: 1, background: TOKENS.ink, padding: 48, color: TOKENS.paper }}>
        <div style={{ fontFamily: FONTS.mono, fontSize: 12, color: TOKENS.seal, letterSpacing: "0.08em" }}>
          BAIL RECKONER
        </div>
        <h1 style={{ fontFamily: FONTS.display, fontSize: 40, marginTop: 16 }}>
          A clearer record of every case.
        </h1>
        <p style={{ opacity: 0.8, marginTop: 16 }}>
          Secure access to case status, procedural requirements, and release guidance.
        </p>
      </div>

      <div style={{ flex: 1, padding: 64, display: "flex", flexDirection: "column", justifyContent: "center" }}>
        <div style={{ fontFamily: FONTS.mono, fontSize: 11, color: TOKENS.inkSoft, letterSpacing: "0.08em" }}>
          AUTHORIZED USERS
        </div>
        <h2 style={{ fontFamily: FONTS.display, fontSize: 28, margin: "8px 0" }}>
          Sign in to the docket
        </h2>
        <p style={{ color: TOKENS.inkSoft, marginBottom: 24 }}>
          Use the credentials assigned to your account.
        </p>

        <form onSubmit={handleSubmit}>
          <label style={{ fontFamily: FONTS.mono, fontSize: 11 }}>USERNAME</label>
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            style={{ display: "block", width: "100%", padding: 12, marginTop: 6, marginBottom: 20 }}
            autoFocus
          />

          <label style={{ fontFamily: FONTS.mono, fontSize: 11 }}>PASSWORD</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{ display: "block", width: "100%", padding: 12, marginTop: 6, marginBottom: 20 }}
          />

          {error && (
            <div style={{ color: "crimson", marginBottom: 16, fontSize: 14 }}>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              width: "100%", padding: 14, background: TOKENS.ink, color: TOKENS.paper,
              border: "none", fontFamily: FONTS.mono, letterSpacing: "0.06em", cursor: "pointer",
            }}
          >
            {loading ? "SIGNING IN..." : "SIGN IN"}
          </button>
        </form>

        <p style={{ marginTop: 20, fontFamily: FONTS.mono, fontSize: 11, color: TOKENS.inkSoft }}>
          Use whichever accounts you seeded with services/trust-access-layer/seed_users.py.
        </p>

        <button
          onClick={onBack}
          style={{ marginTop: 20, background: "none", border: "none", color: TOKENS.inkSoft, cursor: "pointer", fontFamily: FONTS.mono, fontSize: 12 }}
        >
          ← BACK TO ROLES
        </button>
      </div>
    </div>
  );
}