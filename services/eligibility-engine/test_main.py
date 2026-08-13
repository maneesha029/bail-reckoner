from datetime import date, timedelta

from logic import determine_eligibility


CATEGORIES = [
    "cyber_crimes", "crimes_against_sc_st", "crimes_against_women",
    "crimes_against_children", "offences_against_state", "economic_offences",
    "crimes_against_foreigners", "general",
]


def charge(category, months=24):
    return {"offense_category": category, "max_sentence_months": months}


def test_each_offense_category_is_supported():
    custody = (date.today() - timedelta(days=400)).isoformat()
    for category in CATEGORIES:
        result = determine_eligibility("case-" + category, custody, False,
                                       [charge(category)])
        assert result["eligibility_status"] == "eligible_now"


def test_not_yet_eligible():
    custody = (date.today() - timedelta(days=10)).isoformat()
    result = determine_eligibility("c2", custody, False, [charge("general", 60)])
    assert result["eligibility_status"] == "not_yet_eligible"


def test_first_time_offender_rule():
    custody = (date.today() - timedelta(days=300)).isoformat()
    result = determine_eligibility("c3", custody, True, [charge("general", 24)])
    assert result["threshold_rule_applied"] == "one_third_first_time"
    assert result["eligibility_status"] == "eligible_first_time_offender_rule"


def test_multi_charge_uses_longest_sentence():
    result = determine_eligibility("c4", "2020-01-01", False,
                                   [charge("general", 12), charge("general", 60)])
    assert result["days_required"] == 900
