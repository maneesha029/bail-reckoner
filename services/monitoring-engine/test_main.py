from unittest.mock import patch
from scheduler import scan_all_cases


def test_scan_flags_new_eligible_case():
    fake_response = {"data": {"eligibility_status": "eligible_now"}}
    with patch("scheduler.requests.post") as mock_post:
        mock_post.return_value.json.return_value = fake_response
        alerts = scan_all_cases(["case-999"], "test@example.org")
        assert len(alerts) == 1
        assert alerts[0]["case_id"] == "case-999"
