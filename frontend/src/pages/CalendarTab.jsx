import { useState, useEffect } from "react";
import { TOKENS, FONTS, Eyebrow, ActionButton } from "../components/designSystem";
import { getPendingAlerts, setAlertConfig, triggerAlertScan } from "../api/client";

// Real endpoints (monitoring-engine) - already correct, no backend fix
// needed for this tab. PENDING_ALERTS starts empty every restart (it's an
// in-memory list, not a DB table yet - that's the Member 5 gap), so this
// offers a "Run scan now" button that calls the same /alerts/scan route
// the real cron would call, purely so the tab has something to show
// without waiting for a scheduler that doesn't exist yet.
export default function CalendarTab({ token, userId }) {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notifyOn, setNotifyOn] = useState(false);

  const refresh = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await getPendingAlerts(token);
      setAlerts(res.data || []);
    } catch (err) {
      setError(err.message || "Could not load alerts.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { refresh(); }, []);

  const runScan = async () => {
    setLoading(true);
    try {
      await triggerAlertScan(token);
      await refresh();
    } catch (err) {
      setError(err.message || "Scan failed.");
      setLoading(false);
    }
  };

  const toggleNotify = async () => {
    try {
      await setAlertConfig(userId, notifyOn ? "none" : "email", "daily", token);
      setNotifyOn((v) => !v);
    } catch (err) {
      setError(err.message || "Could not save notification preference.");
    }
  };

  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 20 }}>
        <Eyebrow>Pending alerts — {alerts.length}</Eyebrow>
        <div style={{ display: "flex", gap: 10 }}>
          <ActionButton variant="neutral" onClick={toggleNotify}>
            {notifyOn ? "Notifications: On" : "Turn on notifications"}
          </ActionButton>
          <ActionButton variant="neutral" onClick={runScan} disabled={loading}>
            {loading ? "Scanning..." : "Run scan now"}
          </ActionButton>
        </div>
      </div>
      <p style={{ fontSize: 12, color: TOKENS.inkSoft, marginBottom: 20, fontStyle: "italic" }}>
        Alerts reset when the monitoring service restarts (no persistence yet - Member 5's part
        of the work). "Run scan now" fires the same check a real scheduler would run automatically.
      </p>

      {error && <p style={{ color: TOKENS.danger, fontSize: 13 }}>{error}</p>}
      {!loading && alerts.length === 0 && !error && (
        <p style={{ color: TOKENS.inkSoft, fontStyle: "italic" }}>
          No alerts yet. Click "Run scan now" to check demo cases for eligibility events.
        </p>
      )}

      {alerts.map((a, i) => (
        <div key={a.alert_id || i} style={{
          display: "flex", alignItems: "center", gap: 14, padding: "14px 0",
          borderBottom: `1px solid ${TOKENS.rule}`,
        }}>
          <div style={{ width: 90, fontFamily: FONTS.mono, fontSize: 11, color: TOKENS.seal, flexShrink: 0 }}>
            {a.case_id}
          </div>
          <div style={{ flex: 1, fontSize: 14 }}>{a.reason}</div>
        </div>
      ))}
    </div>
  );
}