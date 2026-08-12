from pydantic import BaseModel
from typing import Optional


class Charge(BaseModel):
    act: str  # IPC | BNS | BNSS | BSA | IT_Act | POCSO | SC_ST_Act | PMLA | other
    section: str
    offense_category: str
    is_compoundable: bool
    max_sentence_months: int


class Case(BaseModel):
    case_id: str
    prisoner_id: str
    charges: list[Charge]
    custody_start_date: str
    is_first_time_offender: bool
    state: str
    district: str
    case_stage: str
    has_legal_aid: bool
    created_at: str
    updated_at: str


class EligibilityResult(BaseModel):
    case_id: str
    eligibility_status: str
    days_served: int
    days_required: int
    threshold_rule_applied: str
    eligible_since_date: Optional[str]
    computed_at: str


class PrecedentCitation(BaseModel):
    citation_id: str
    case_name: str
    citation_text: str
    source_url: str
    relevance_score: float
    applicable_factor: str


class PrecedentResult(BaseModel):
    case_id: str
    results: list[PrecedentCitation]
    disclaimer: str
    retrieved_at: str


class ProceduralStep(BaseModel):
    step_number: int
    description: str


class ProceduralResult(BaseModel):
    case_id: str
    bond_type: str
    estimated_fine_amount_inr: int
    required_documents: list[str]
    procedural_steps: list[ProceduralStep]
    governing_sections: list[str]


class BondWaiverResult(BaseModel):
    case_id: str
    is_flagged_for_waiver: bool
    waiver_confidence: str
    governing_section: str
    reasoning_summary: str


class AuditLogEntry(BaseModel):
    case_id: str
    actor_user_id: str
    actor_role: str
    action_type: str
    action_payload: dict
    timestamp: str


class AlertConfig(BaseModel):
    recipient_user_id: str
    notify_via: str
    scan_frequency: str


class AlertRecord(BaseModel):
    alert_id: str
    case_id: str
    triggered_at: str
    reason: str
    is_acknowledged: bool
