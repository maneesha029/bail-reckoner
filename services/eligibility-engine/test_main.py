from logic import determine_eligibility


def test_eligible_now():
    result = determine_eligibility("c1", "2024-01-01", False, [{"max_sentence_months": 24}])
    assert result["eligibility_status"] == "eligible_now"


def test_not_yet_eligible():
    result = determine_eligibility("c2", "2026-08-01", False, [{"max_sentence_months": 60}])
    assert result["eligibility_status"] == "not_yet_eligible"


def test_first_time_offender_rule():
    result = determine_eligibility("c3", "2025-06-01", True, [{"max_sentence_months": 24}])
    assert result["threshold_rule_applied"] == "one_third_first_time"


def test_multi_charge_uses_longest_sentence():
    charges = [{"max_sentence_months": 12}, {"max_sentence_months": 60}]
    result = determine_eligibility("c4", "2020-01-01", False, charges)
    assert result["days_required"] == int(60 * 30 / 2)
