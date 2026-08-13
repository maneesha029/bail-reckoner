import json
import os

_PROCEDURAL_DATA_PATH = os.path.join(os.path.dirname(__file__), "procedural_data.json")
_procedural_data_cache = None


def _load_procedural_categories() -> dict:
    global _procedural_data_cache
    if _procedural_data_cache is None:
        with open(_PROCEDURAL_DATA_PATH, "r", encoding="utf-8") as f:
            _procedural_data_cache = json.load(f)["categories"]
    return _procedural_data_cache


def get_procedural_requirements(case_id: str, offense_category: str) -> dict:
    """Looks up the procedural checklist for offense_category from
    procedural_data.json, compiled from CrPC 441-450 / BNSS 485-496
    (see procedural_data.json's _meta block for the section mapping and
    legal-review status). Falls back to the 'general' category if
    offense_category isn't recognized, so callers always get a usable
    checklist rather than a 500."""
    categories = _load_procedural_categories()
    entry = categories.get(offense_category, categories["general"])
    return {
        "case_id": case_id,
        "bond_type": entry["bond_type"],
        "estimated_fine_amount_inr": entry["estimated_fine_amount_inr"],
        "required_documents": list(entry["required_documents"]),
        "procedural_steps": list(entry["procedural_steps"]),
        "governing_sections": list(entry["governing_sections"]),
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
