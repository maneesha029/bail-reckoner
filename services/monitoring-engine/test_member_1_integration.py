# Create: bail-reckoner/services/monitoring-engine/test_member_1_integration.py

import pytest
import requests
from unittest.mock import patch, Mock

class TestMember1Integration:
    """Test integration with Member 1 (Eligibility Service)."""
    
    @patch('requests.get')
    def test_get_cases_from_member_1(self, mock_get):
        """Test fetching cases from Member 1."""
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: [
                {
                    "case_id": "case-001",
                    "prisoner_id": "PRIS-2026-00001",
                    "state": "Maharashtra",
                    "district": "Mumbai",
                    "charges": [{"offense_category": "theft", "max_sentence_months": 36}],
                    "custody_start_date": "2024-06-15T00:00:00Z"
                }
            ]
        )
        
        from scheduler import CaseMonitoringScanner
        scanner = CaseMonitoringScanner()
        cases = scanner.get_all_undertrial_cases()
        
        assert len(cases) > 0
        assert cases[0]["case_id"] == "case-001"
        print("✓ Member 1 integration test passed")
    
    @patch('requests.get')
    def test_check_eligibility_from_member_1(self, mock_get):
        """Test checking eligibility with Member 1."""
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {
                "status": "eligible_now",
                "reason": "served_50_percent",
                "eligible_date": "2026-08-14T00:00:00Z"
            }
        )
        
        from scheduler import CaseMonitoringScanner
        scanner = CaseMonitoringScanner()
        result = scanner.check_case_eligibility("case-001")
        
        assert result is not None
        assert result["status"] == "eligible_now"
        print("✓ Eligibility check integration test passed")

        # Test audit logging to Member 4

@patch('requests.post')
def test_log_to_member_4_audit(self, mock_post):
    """Test logging to Member 4 audit trail."""
    mock_post.return_value = Mock(
        status_code=200,
        json=lambda: {"audit_id": "audit-001"}
    )
    
    from scheduler import CaseMonitoringScanner
    from models import Alert, AlertStatus
    from datetime import datetime, timezone
    
    scanner = CaseMonitoringScanner()
    mock_alert = Mock()
    mock_alert.case_id = "case-001"
    mock_alert.id = "alert-001"
    mock_alert.eligibility_reason = "served_50_percent"
    
    scanner.log_to_audit(mock_alert, "alert_created")
    
    mock_post.assert_called_once()
    print("✓ Member 4 audit logging test passed")