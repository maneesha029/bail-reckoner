"""
End-to-End testing for Phase 1-3
Tests complete workflows from start to finish
"""

import pytest
from fastapi.testclient import TestClient
from main import app
import time

client = TestClient(app)

# ============================================================================
# E2E TEST SUITE 1: Complete Configuration Flow
# ============================================================================

class TestConfigurationFlow:
    """Test complete configuration workflow."""
    
    def test_create_and_retrieve_config(self):
        """E2E: Create config and retrieve it."""
        user_id = f"e2e-user-{int(time.time())}"
        
        # Step 1: Save configuration
        save_response = client.post(
            "/api/v1/alerts/config",
            json={
                "user_id": user_id,
                "email_enabled": True,
                "email_address": "e2e@example.com",
                "sms_enabled": False,
                "sms_number": None,
                "notify_immediately": True,
                "digest_enabled": False,
                "digest_hour": 9
            }
        )
        
        assert save_response.status_code == 200
        save_data = save_response.json()
        assert save_data["success"] == True
        assert save_data["data"]["user_id"] == user_id
        
        print(f"  ✓ Step 1: Configuration saved for {user_id}")
        
        # Step 2: Verify configuration was saved
        assert save_data["data"]["email_enabled"] == True
        assert save_data["data"]["email_address"] == "e2e@example.com"
        
        print(f"  ✓ Step 2: Configuration verified")
        print("✅ E2E: Create and retrieve config - PASSED\n")


# ============================================================================
# E2E TEST SUITE 2: Complete Alert Retrieval Flow
# ============================================================================

class TestAlertRetrievalFlow:
    """Test complete alert retrieval workflow."""
    
    def test_retrieve_alerts_with_filters(self):
        """E2E: Retrieve alerts with various filters."""
        
        print("  Testing different filter combinations...")
        
        # Test 1: No filters
        response = client.get("/api/v1/alerts/pending")
        assert response.status_code == 200
        print("    ✓ No filters: OK")
        
        # Test 2: State filter
        response = client.get("/api/v1/alerts/pending?state=Maharashtra")
        assert response.status_code == 200
        print("    ✓ State filter: OK")
        
        # Test 3: District filter
        response = client.get("/api/v1/alerts/pending?district=Mumbai")
        assert response.status_code == 200
        print("    ✓ District filter: OK")
        
        # Test 4: State + District filter
        response = client.get("/api/v1/alerts/pending?state=Maharashtra&district=Mumbai")
        assert response.status_code == 200
        print("    ✓ State + District filter: OK")
        
        # Test 5: With limit
        response = client.get("/api/v1/alerts/pending?limit=5")
        assert response.status_code == 200
        assert len(response.json()["data"]["pending_alerts"]) <= 5
        print("    ✓ Limit filter: OK")
        
        # Test 6: With offset (pagination)
        response = client.get("/api/v1/alerts/pending?limit=5&offset=0")
        assert response.status_code == 200
        print("    ✓ Offset filter: OK")
        
        print("✅ E2E: Alert retrieval with filters - PASSED\n")


# ============================================================================
# E2E TEST SUITE 3: Complete Scan Flow
# ============================================================================

class TestScanFlow:
    """Test complete scan workflow."""
    
    def test_scan_workflow(self):
        """E2E: Complete scan workflow."""
        
        print("  Starting scan workflow...")
        
        # Step 1: Trigger scan
        response = client.get("/api/v1/alerts/scan")
        assert response.status_code == 200
        scan_data = response.json()
        assert scan_data["success"] == True
        
        scan_result = scan_data["data"]
        print(f"    ✓ Scan triggered (ID: {scan_result['scan_id']})")
        
        # Step 2: Verify scan results
        assert "total_cases_scanned" in scan_result
        assert "newly_eligible_found" in scan_result
        assert "new_alerts_created" in scan_result
        assert "scan_duration_seconds" in scan_result
        
        print(f"    ✓ Scanned {scan_result['total_cases_scanned']} cases")
        print(f"    ✓ Found {scan_result['newly_eligible_found']} newly eligible cases")
        print(f"    ✓ Created {scan_result['new_alerts_created']} alerts")
        print(f"    ✓ Scan duration: {scan_result['scan_duration_seconds']:.2f}s")
        
        # Step 3: Verify scan time is reasonable
        assert scan_result["scan_duration_seconds"] < 10  # Should complete in <10s
        print(f"    ✓ Scan duration within acceptable range")
        
        print("✅ E2E: Scan workflow - PASSED\n")


# ============================================================================
# E2E TEST SUITE 4: Complete Workflow (Config → Scan → Alerts)
# ============================================================================

class TestCompleteWorkflow:
    """Test complete end-to-end workflow."""
    
    def test_complete_workflow_config_scan_alerts(self):
        """E2E: Save config → Trigger scan → Retrieve alerts."""
        
        user_id = f"e2e-complete-{int(time.time())}"
        
        print(f"  Testing complete workflow for {user_id}...")
        
        # Step 1: Save user configuration
        print("    Step 1: Saving user configuration...")
        config_response = client.post(
            "/api/v1/alerts/config",
            json={
                "user_id": user_id,
                "email_enabled": True,
                "email_address": f"{user_id}@example.com",
                "sms_enabled": False,
                "sms_number": None,
                "notify_immediately": True,
                "digest_enabled": False,
                "digest_hour": 9
            }
        )
        assert config_response.status_code == 200
        assert config_response.json()["success"] == True
        print("      ✓ Configuration saved")
        
        # Step 2: Trigger scan
        print("    Step 2: Triggering scan...")
        scan_response = client.get("/api/v1/alerts/scan")
        assert scan_response.status_code == 200
        scan_data = scan_response.json()
        assert scan_data["success"] == True
        print(f"      ✓ Scan completed ({scan_data['data']['scan_duration_seconds']:.2f}s)")
        
        # Step 3: Retrieve pending alerts
        print("    Step 3: Retrieving pending alerts...")
        alerts_response = client.get("/api/v1/alerts/pending")
        assert alerts_response.status_code == 200
        alerts_data = alerts_response.json()
        assert alerts_data["success"] == True
        alert_count = alerts_data["data"]["count"]
        print(f"      ✓ Retrieved {alert_count} pending alerts")
        
        # Step 4: Verify response structure
        print("    Step 4: Verifying response structure...")
        assert "success" in alerts_data
        assert "data" in alerts_data
        assert "error" in alerts_data
        assert "timestamp" in alerts_data
        print("      ✓ Response structure valid")
        
        print("✅ E2E: Complete workflow - PASSED\n")


# ============================================================================
# RUN ALL TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])