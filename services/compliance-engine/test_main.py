from logic import check_bond_waiver, get_procedural_requirements


def test_bond_waiver_flags_high_hardship():
    hardship = {"has_fixed_income": False, "owns_property": False,
                "has_dependents": True, "months_in_custody_post_bail_grant": 4}
    result = check_bond_waiver("c1", hardship)
    assert result["is_flagged_for_waiver"] is True


def test_bond_waiver_does_not_flag_low_hardship():
    hardship = {"has_fixed_income": True, "owns_property": True,
                "has_dependents": False, "months_in_custody_post_bail_grant": 0}
    result = check_bond_waiver("c2", hardship)
    assert result["is_flagged_for_waiver"] is False


def test_procedural_requirements_shape():
    result = get_procedural_requirements("c3", "general")
    assert "bond_type" in result and "governing_sections" in result


# ---------------------------------------------------------------------
# Part 1 - multiple offense categories
# ---------------------------------------------------------------------

ALL_OFFENSE_CATEGORIES = [
    "cyber_crimes", "crimes_against_sc_st", "crimes_against_women",
    "crimes_against_children", "offences_against_state", "economic_offences",
    "crimes_against_foreigners", "general",
]


def test_procedural_requirements_all_categories_return_valid_shape():
    for category in ALL_OFFENSE_CATEGORIES:
        result = get_procedural_requirements("c-" + category, category)
        assert result["bond_type"] in {"surety_bond", "personal_bond", "waived_indigent"}
        assert result["estimated_fine_amount_inr"] > 0
        assert len(result["required_documents"]) > 0
        assert len(result["procedural_steps"]) > 0
        assert result["procedural_steps"][0]["step_number"] == 1
        assert len(result["governing_sections"]) > 0


def test_procedural_requirements_differ_across_categories():
    general = get_procedural_requirements("c4", "general")
    state_offence = get_procedural_requirements("c5", "offences_against_state")
    # The honest test from the build doc: two different offense
    # categories must produce different, correct checklists.
    assert general["bond_type"] != state_offence["bond_type"]
    assert general["estimated_fine_amount_inr"] != state_offence["estimated_fine_amount_inr"]
    assert general["required_documents"] != state_offence["required_documents"]


def test_procedural_requirements_unknown_category_falls_back_to_general():
    result = get_procedural_requirements("c6", "not_a_real_category")
    general = get_procedural_requirements("c6", "general")
    assert result["bond_type"] == general["bond_type"]


# ---------------------------------------------------------------------
# Part 2 - multiple hardship-indicator combinations
# ---------------------------------------------------------------------

def _hardship(has_fixed_income, owns_property, has_dependents, months):
    return {
        "has_fixed_income": has_fixed_income,
        "owns_property": owns_property,
        "has_dependents": has_dependents,
        "months_in_custody_post_bail_grant": months,
    }


def test_bond_waiver_all_four_factors_high_confidence():
    result = check_bond_waiver("c7", _hardship(False, False, True, 4))
    assert result["is_flagged_for_waiver"] is True
    assert result["waiver_confidence"] == "high"


def test_bond_waiver_three_of_four_factors_still_flags():
    # no fixed income, no property, has dependents, but only 1 month in
    # custody (below the 2-month factor threshold) -> score 3, still high
    result = check_bond_waiver("c8", _hardship(False, False, True, 1))
    assert result["is_flagged_for_waiver"] is True
    assert result["waiver_confidence"] == "high"


def test_bond_waiver_two_of_four_factors_medium_not_flagged():
    result = check_bond_waiver("c9", _hardship(True, False, True, 1))
    assert result["waiver_confidence"] == "medium"
    assert result["is_flagged_for_waiver"] is False


def test_bond_waiver_one_of_four_factors_low_not_flagged():
    result = check_bond_waiver("c10", _hardship(True, True, False, 3))
    assert result["waiver_confidence"] == "low"
    assert result["is_flagged_for_waiver"] is False


def test_bond_waiver_toggling_one_indicator_changes_output():
    base = _hardship(False, False, True, 1)  # score 3 -> high, flagged
    base_result = check_bond_waiver("c11", base)
    assert base_result["is_flagged_for_waiver"] is True
    assert base_result["waiver_confidence"] == "high"

    flipped = dict(base)
    flipped["has_dependents"] = False  # score drops to 2 -> medium, not flagged
    flipped_result = check_bond_waiver("c11", flipped)

    # The honest test from the build doc: toggling a hardship indicator
    # must change the output - proves the logic isn't hardcoded.
    assert flipped_result["waiver_confidence"] != base_result["waiver_confidence"]
    assert flipped_result["is_flagged_for_waiver"] != base_result["is_flagged_for_waiver"]
