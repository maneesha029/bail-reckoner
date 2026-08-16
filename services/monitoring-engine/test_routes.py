"""
Tests for Monitoring & Outreach Engine API routes.

Tests the 3 main endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from main import app
from schemas import AlertConfigRequest

client = TestClient(app)


# ============================================================================
# Health Check Tests
# ============================================================================

def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["data"]["status"] == "healthy"
    print("✓ Health check passed")


def test_root_endpoint():
    """Test / root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "message" in data["data"]  # ✅ CORRECT - matches actual response


# ============================================================================
# Endpoint 1: POST /api/v1/alerts/config
# ============================================================================

class TestSaveAlertConfig:
    """Tests for saving alert configuration."""
    
    def test_save_alert_config_valid(self):
        """Test saving valid alert config."""
        response = client.post(
            "/api/v1/alerts/config",
            json={
                "user_id": "user-001",
                "email_enabled": True,
                "email_address": "test@example.com",
                "sms_enabled": False,
                "sms_number": None,
                "notify_immediately": True,
                "digest_enabled": False,
                "digest_hour": 9
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["data"]["user_id"] == "user-001"
        assert data["error"] is None
        print("✅ Test passed: save_alert_config_valid")

    def test_save_alert_config_invalid_email_format(self):
        """Test saving config with invalid email format."""
        response = client.post(
            "/api/v1/alerts/config",
            json={
                "user_id": "user-002",
                "email_enabled": True,
                "email_address": "not-an-email",  # Invalid format
                "sms_enabled": False,
                "sms_number": None,
                "notify_immediately": True,
                "digest_enabled": False,
                "digest_hour": 9
            }
        )
        assert response.status_code == 422  # Pydantic validation error
        print("✅ Test passed: save_alert_config_invalid_email_format")
    
    def test_save_alert_config_email_enabled_without_address(self):
        """Test: email_enabled=true but email_address is None."""
        response = client.post(
            "/api/v1/alerts/config",
            json={
                "user_id": "user-003",
                "email_enabled": True,
                "email_address": None,  # Missing address
                "sms_enabled": False,
                "sms_number": None,
                "notify_immediately": True,
                "digest_enabled": False,
                "digest_hour": 9
            }
        )
        assert response.status_code == 422  # Cross-field validation error
        print("✅ Test passed: save_alert_config_email_enabled_without_address")
    
    def test_save_alert_config_sms_enabled_without_number(self):
        """Test: sms_enabled=true but sms_number is None."""
        response = client.post(
            "/api/v1/alerts/config",
            json={
                "user_id": "user-004",
                "email_enabled": False,
                "email_address": None,
                "sms_enabled": True,
                "sms_number": None,  # Missing number
                "notify_immediately": True,
                "digest_enabled": False,
                "digest_hour": 9
            }
        )
        assert response.status_code == 422  # Cross-field validation error
        print("✅ Test passed: save_alert_config_sms_enabled_without_number")
    
    def test_save_alert_config_missing_required_field(self):
        """Test: missing required user_id field."""
        response = client.post(
            "/api/v1/alerts/config",
            json={
                "email_enabled": True,
                "email_address": "test@example.com",
                "sms_enabled": False,
                "sms_number": None,
                "notify_immediately": True,
                "digest_enabled": False,
                "digest_hour": 9
                # user_id is MISSING
            }
        )
        assert response.status_code == 422  # Missing required field
        print("✅ Test passed: save_alert_config_missing_required_field")
    
    def test_save_alert_config_invalid_digest_hour(self):
        """Test: digest_hour out of range (0-23)."""
        response = client.post(
            "/api/v1/alerts/config",
            json={
                "user_id": "user-005",
                "email_enabled": True,
                "email_address": "test@example.com",
                "sms_enabled": False,
                "sms_number": None,
                "notify_immediately": True,
                "digest_enabled": True,
                "digest_hour": 25  # Invalid: should be 0-23
            }
        )
        assert response.status_code == 422  # Validation error
        print("✅ Test passed: save_alert_config_invalid_digest_hour")
    
    def test_save_alert_config_both_email_and_sms_disabled(self):
        """Test: both email and SMS disabled (valid edge case)."""
        response = client.post(
            "/api/v1/alerts/config",
            json={
                "user_id": "user-006",
                "email_enabled": False,
                "email_address": None,
                "sms_enabled": False,
                "sms_number": None,
                "notify_immediately": True,
                "digest_enabled": False,
                "digest_hour": 9
            }
        )
        assert response.status_code == 200
        assert response.json()["success"] == True
        print("✅ Test passed: save_alert_config_both_email_and_sms_disabled")


# ============================================================================
# TEST SUITE 2: GET /api/v1/alerts/pending
# ============================================================================


class TestGetPendingAlerts:
    """Tests for getting pending alerts."""
    
    def test_get_pending_alerts_success(self):
        """Test getting pending alerts."""
        response = client.get("/api/v1/alerts/pending")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "count" in data["data"]
        assert "pending_alerts" in data["data"]
        assert isinstance(data["data"]["count"], int)
        assert isinstance(data["data"]["pending_alerts"], list)
        print("✅ Test passed: get_pending_alerts_success")
    
    def test_get_pending_alerts_response_structure(self):
        """Test response has correct structure."""
        response = client.get("/api/v1/alerts/pending")
        data = response.json()
        
        # Check required fields
        assert "success" in data
        assert "data" in data
        assert "error" in data
        assert "timestamp" in data
        
        # Check data structure
        assert "count" in data["data"]
        assert "pending_alerts" in data["data"]
        assert "filters_applied" in data["data"]
        print("✅ Test passed: get_pending_alerts_response_structure")
    
    def test_get_pending_alerts_with_state_filter(self):
        """Test filtering by state."""
        response = client.get("/api/v1/alerts/pending?state=Maharashtra")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print("✅ Test passed: get_pending_alerts_with_state_filter")
    
    def test_get_pending_alerts_with_district_filter(self):
        """Test filtering by district."""
        response = client.get("/api/v1/alerts/pending?district=Mumbai")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print("✅ Test passed: get_pending_alerts_with_district_filter")
    
    def test_get_pending_alerts_with_state_and_district_filter(self):
        """Test filtering by state and district."""
        response = client.get("/api/v1/alerts/pending?state=Maharashtra&district=Mumbai")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print("✅ Test passed: get_pending_alerts_with_state_and_district_filter")
    
    def test_get_pending_alerts_with_limit(self):
        """Test with custom limit."""
        response = client.get("/api/v1/alerts/pending?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["pending_alerts"]) <= 10
        print("✅ Test passed: get_pending_alerts_with_limit")
    
    def test_get_pending_alerts_with_offset(self):
    #Test with offset pagination.
        response1 = client.get("/api/v1/alerts/pending?limit=1&offset=0")
        response2 = client.get("/api/v1/alerts/pending?limit=1&offset=1")
        data1 = response1.json()
        data2 = response2.json()
        
        # Just verify both requests succeeded
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # If we have results, verify offset worked
        if (len(data1["data"]["pending_alerts"]) > 0 and 
            len(data2["data"]["pending_alerts"]) > 0):
            # They should have different offsets applied
            assert data1["data"]["filters_applied"]["offset"] == 0
            assert data2["data"]["filters_applied"]["offset"] == 1
        
        print("✅ Test passed: get_pending_alerts_with_offset")
    def test_get_pending_alerts_invalid_limit_too_large(self):
        """Test with limit > 1000."""
        response = client.get("/api/v1/alerts/pending?limit=2000")
        assert response.status_code == 422  # Validation error
        print("✅ Test passed: get_pending_alerts_invalid_limit_too_large")
    
    def test_get_pending_alerts_invalid_limit_zero(self):
        """Test with limit = 0."""
        response = client.get("/api/v1/alerts/pending?limit=0")
        assert response.status_code == 422  # Validation error
        print("✅ Test passed: get_pending_alerts_invalid_limit_zero")
    
    def test_get_pending_alerts_invalid_offset_negative(self):
        """Test with negative offset."""
        response = client.get("/api/v1/alerts/pending?offset=-1")
        assert response.status_code == 422  # Validation error
        print("✅ Test passed: get_pending_alerts_invalid_offset_negative")


# ============================================================================
# TEST SUITE 3: GET /api/v1/alerts/scan
# ============================================================================


class TestTriggerScan:
    """Tests for triggering scan."""
    
    def test_trigger_scan_success(self):
        """Test triggering scanner."""
        response = client.get("/api/v1/alerts/scan")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print("✅ Test passed: trigger_scan_success")
    
    def test_trigger_scan_response_structure(self):
        """Test scan response has required fields."""
        response = client.get("/api/v1/alerts/scan")
        data = response.json()["data"]
        
        required_fields = [
            "scan_id",
            "total_cases_scanned",
            "newly_eligible_found",
            "new_alerts_created",
            "already_flagged_skipped",
            "errors",
            "scan_duration_seconds",
            "timestamp"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        print("✅ Test passed: trigger_scan_response_structure")
    
    def test_trigger_scan_numeric_fields(self):
        """Test scan response has correct numeric types."""
        response = client.get("/api/v1/alerts/scan")
        data = response.json()["data"]
        
        assert isinstance(data["total_cases_scanned"], int)
        assert isinstance(data["newly_eligible_found"], int)
        assert isinstance(data["new_alerts_created"], int)
        assert isinstance(data["already_flagged_skipped"], int)
        assert isinstance(data["scan_duration_seconds"], float)
        assert isinstance(data["errors"], list)
        print("✅ Test passed: trigger_scan_numeric_fields")


# ============================================================================
# TEST SUITE 4: GET /health & /
# ============================================================================
class TestHealthEndpoint:
    
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["data"]["status"] == "healthy"
    
    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "message" in data["data"]

# ============================================================================
# RUN ALL TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])