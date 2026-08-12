def get_procedural_requirements(case_id: str, offense_category: str) -> dict:
    # TODO: look up real requirements from the procedural_requirements table
    # sourced from CrPC 441-450 / BNSS equivalents.
    return {
        "case_id": case_id,
        "bond_type": "personal_bond",
        "estimated_fine_amount_inr": 5000,
        "required_documents": ["Aadhaar", "Proof of residence", "Two sureties with ID proof"],
        "procedural_steps": [
            {"step_number": 1, "description": "File bail application with the court registry"},
            {"step_number": 2, "description": "Submit personal bond and required documents"},
        ],
        "governing_sections": ["CrPC 441", "CrPC 445"],
    }


def check_bond_waiver(case_id: str, hardship: dict) -> dict:
    """CrPC Section 436 / BNSS equivalent - courts may waive/reduce bond
    for indigent persons. This is a rule-based flag, not a prediction."""
    score = 0
    if not hardship.get("has_fixed_income", True):
        score += 1
    if not hardship.get("owns_property", True):
        score += 1
    if hardship.get("has_dependents", False):
        score += 1
    if hardship.get("months_in_custody_post_bail_grant", 0) >= 2:
        score += 1

    is_flagged = score >= 3
    confidence = "high" if score >= 3 else ("medium" if score == 2 else "low")
    return {
        "case_id": case_id,
        "is_flagged_for_waiver": is_flagged,
        "waiver_confidence": confidence,
        "governing_section": "CrPC 436 / BNSS equivalent",
        "reasoning_summary": f"Hardship indicators present: {score} of 4 factors.",
    }
