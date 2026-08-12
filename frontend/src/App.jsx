import { useState } from "react";
import LegalAidDashboard from "./pages/LegalAidDashboard";
import JudgeDashboard from "./pages/JudgeDashboard";
import UndertrialView from "./pages/UndertrialView";

export default function App() {
  const [token] = useState(null);
  const [view] = useState("legal_aid"); // legal_aid | judge | undertrial

  if (view === "judge") return <JudgeDashboard token={token} />;
  if (view === "undertrial") return <UndertrialView token={token} />;
  return <LegalAidDashboard token={token} />;
}
