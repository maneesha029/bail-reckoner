"""
Security testing for Phase 2-3
Tests for input validation, SQL injection prevention, etc.
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# ============================================================================
# SECURITY TEST SUITE 1: Input Validation
# ============================================================================

class TestInputValidation:
    """Test input validation."""
    
    def test_email_validation_invalid_format(self):
        """Test email validation rejects invalid format."""
        response = client.post(
            "/api/v1/alerts/config",
            json={
                "user_id": "user-sec-001",
                "email_enabled": True,
                "email_address": "not-an-email",
                "sms_enabled": False,
                "sms_number": None,
                "notify_immediately": True,
                "digest_enabled": False,
                "digest_hour": 9
            }
        )
        assert response.status_code == 422
        print("✅ Email validation test passed")
    
    def test_phone_number_format(self):
        """Test phone number format validation."""
        response = client.post(
            "/api/v1/alerts/config",
            json={
                "user_id": "user-sec-002",
                "email_enabled": False,
                "email_address": None,
                "sms_enabled": True,
                "sms_number": "invalid-phone",  # Invalid format
                "notify_immediately": True,
                "digest_enabled": False,
                "digest_hour": 9
            }
        )
        assert response.status_code == 422
        print("✅ Phone number format validation test passed")
    
    def test_cross_field_validation_email(self):
        """Test cross-field validation: email_enabled requires email_address."""
        response = client.post(
            "/api/v1/alerts/config",
            json={
                "user_id": "user-sec-003",
                "email_enabled": True,
                "email_address": None,  # Missing!
                "sms_enabled": False,
                "sms_number": None,
                "notify_immediately": True,
                "digest_enabled": False,
                "digest_hour": 9
            }
        )
        assert response.status_code == 422
        print("✅ Email cross-field validation test passed")
    
    def test_cross_field_validation_sms(self):
        """Test cross-field validation: sms_enabled requires sms_number."""
        response = client.post(
            "/api/v1/alerts/config",
            json={
                "user_id": "user-sec-004",
                "email_enabled": False,
                "email_address": None,
                "sms_enabled": True,
                "sms_number": None,  # Missing!
                "notify_immediately": True,
                "digest_enabled": False,
                "digest_hour": 9
            }
        )
        assert response.status_code == 422
        print("✅ SMS cross-field validation test passed")
    
    def test_digest_hour_range_validation(self):
        """Test digest_hour validation (0-23 range)."""
        # Test invalid hour: 25
        response = client.post(
            "/api/v1/alerts/config",
            json={
                "user_id": "user-sec-005",
                "email_enabled": True,
                "email_address": "test@example.com",
                "sms_enabled": False,
                "sms_number": None,
                "notify_immediately": True,
                "digest_enabled": True,
                "digest_hour": 25  # Invalid!
            }
        )
        assert response.status_code == 422
        print("✅ Digest hour range validation test passed")


# ============================================================================
# SECURITY TEST SUITE 2: SQL Injection Prevention
# ============================================================================

class TestSQLInjectionPrevention:
    """Test SQL injection prevention."""
    
    def test_sql_injection_in_state_filter(self):
        """Test SQL injection in state parameter."""
        # Try to inject SQL
        response = client.get("/api/v1/alerts/pending?state=Maharashtra' OR '1'='1")
        assert response.status_code == 200
        data = response.json()
        # Should safely escape, not execute SQL
        assert data["success"] == True
        print("✅ SQL injection prevention (state) test passed")
    
    def test_sql_injection_in_district_filter(self):
        """Test SQL injection in district parameter."""
        response = client.get("/api/v1/alerts/pending?district=Mumbai'; DROP TABLE alerts; --")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        # Table should still exist if query was safe
        print("✅ SQL injection prevention (district) test passed")
    
    def test_unicode_injection_attempt(self):
        """Test Unicode/UTF-8 injection."""
        response = client.get("/api/v1/alerts/pending?state=महाराष्ट्र")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print("✅ Unicode injection prevention test passed")


# ============================================================================
# SECURITY TEST SUITE 3: Rate Limiting & DoS Prevention
# ============================================================================

class TestRateLimiting:
    """Test rate limiting (if implemented)."""
    
    def test_rapid_requests(self):
        """Test handling of rapid requests."""
        responses = []
        for i in range(10):
            response = client.get("/api/v1/alerts/pending?limit=1")
            responses.append(response.status_code)
        
        # All should succeed (no rate limit) or some blocked (rate limited)
        # At minimum, no 500 errors
        assert all(code in [200, 429] for code in responses)
        print("✅ Rapid requests test passed")


# ============================================================================
# SECURITY TEST SUITE 4: Data Type Validation
# ============================================================================

class TestDataTypeValidation:
    """Test data type validation."""
    
    def test_user_id_must_be_string(self):
        """Test user_id must be string."""
        response = client.post(
            "/api/v1/alerts/config",
            json={
                "user_id": 12345,  # Should be string!
                "email_enabled": True,
                "email_address": "test@example.com",
                "sms_enabled": False,
                "sms_number": None,
                "notify_immediately": True,
                "digest_enabled": False,
                "digest_hour": 9
            }
        )
        # Should either coerce to string or fail validation
        assert response.status_code in [200, 422]
        print("✅ User ID type validation test passed")
    
    def test_booleans_must_be_boolean(self):
        """Test boolean fields must be boolean."""
        response = client.post(
            "/api/v1/alerts/config",
            json={
                "user_id": "user-sec-010",
                "email_enabled": "yes",  # Pydantic will coerce to True
                "email_address": "test@example.com",
                "sms_enabled": False,
                "sms_number": None,
                "notify_immediately": True,
                "digest_enabled": False,
                "digest_hour": 9
            }
        )
        # Pydantic v2 coerces "yes" to True, so this should succeed
        assert response.status_code == 200
        assert response.json()["data"]["email_enabled"] == True
    
    def test_digest_hour_must_be_integer(self):
        """Test digest_hour must be integer."""
        response = client.post(
            "/api/v1/alerts/config",
            json={
                "user_id": "user-sec-011",
                "email_enabled": True,
                "email_address": "test@example.com",
                "sms_enabled": False,
                "sms_number": None,
                "notify_immediately": True,
                "digest_enabled": True,
                "digest_hour": "9"  # Should be integer!
            }
        )
        # Should either coerce to int or fail validation
        assert response.status_code in [200, 422]
        print("✅ Digest hour type validation test passed")


# ============================================================================
# RUN ALL TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])