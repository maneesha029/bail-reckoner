import { useState } from "react";
import { checkEligibility, searchPrecedent, getProceduralRequirements, checkBondWaiver } from "../api/client";

export default function LegalAidDashboard({ token }) {
  const [caseId, setCaseId] = useState("");
  const [result, setResult] = useState(null);

  const loadCase = async () => {
    const [eligibility, precedent, procedural, bondWaiver] = await Promise.all([
      checkEligibility(caseId, token),
      searchPrecedent(caseId, { offense_category: "general", discretion_factors: [] }, token),
      getProceduralRequirements(caseId, token),
      checkBondWaiver(caseId, {}, token),
    ]);
    setResult({ eligibility: eligibility.data, precedent: precedent.data,
                procedural: procedural.data, bondWaiver: bondWaiver.data });
  };

  return (
    <div>
      <h1>Legal aid dashboard</h1>
      <input value={caseId} onChange={(e) => setCaseId(e.target.value)} placeholder="Case ID" />
      <button onClick={loadCase}>Load case</button>
      {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
    </div>
  );
}
