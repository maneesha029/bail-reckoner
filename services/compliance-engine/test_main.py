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
