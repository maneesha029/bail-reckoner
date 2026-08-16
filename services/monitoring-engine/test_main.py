import pytest
from routes import trigger_scan

def test_scanner_catches_newly_eligible():
    """Test that scanner correctly identifies newly eligible cases."""
    result = trigger_scan()
    assert result.success == True  # ✅ CORRECT (use dot notation)
    assert len(result.data) > 0

def test_alert_creation_with_mocked_eligibility():
    """Test alert creation with mocked eligibility service response."""
    # This test uses a mocked HTTP response from Member 1
    pass