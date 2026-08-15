// There is still no GET /api/v1/eligibility/cases (or any) list endpoint
// anywhere in the real backend - eligibility-engine can only look up ONE
// case_id at a time. So this file is the "directory" of who exists,
// matching seed_cases.py's CASES list exactly. Clicking a card calls the
// real checkEligibility(case_id) - the data that comes back is real,
// only the directory/roster listing itself is client-side.
//
// When Member 1 adds a real list endpoint, delete this file and fetch
// the roster instead - RosterTab.jsx is written so that's a one-line change.

export const ROSTER = [
  { case_id: "case-001", name: "Ramesh Kumar Yadav", offense: "IPC 379 - Theft" },
  { case_id: "case-002", name: "Suresh Prajapati", offense: "IPC 379 - Theft" },
  { case_id: "case-003", name: "Priya Sharma", offense: "IPC 354 - Assault on woman" },
  { case_id: "case-004", name: "Anita Devi", offense: "BNS 74 - Assault on woman" },
  { case_id: "case-005", name: "Mohammed Aslam", offense: "IT Act 66 - Cyber crime" },
  { case_id: "case-006", name: "Vikram Singh Rathore", offense: "PMLA 4 - Money laundering" },
  { case_id: "case-007", name: "Farhan Ahmed Khan", offense: "SC/ST Act 3(1)(r)" },
  { case_id: "case-008", name: "Sunita Kumari", offense: "IPC 379 + BNS 74" },
  { case_id: "case-009", name: "Om Prakash Chaudhary", offense: "IPC 379 - Theft" },
  { case_id: "case-010", name: "Geeta Bai Solanki", offense: "POCSO 12" },
];