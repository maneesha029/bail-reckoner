"""
Manual endpoint testing script
Run: python3 test_endpoints.py
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_save_alert_config():
    """Test saving alert config."""
    print("\n" + "="*80)
    print("TEST 1: Save Alert Config")
    print("="*80)
    
    response = requests.post(
        f'{BASE_URL}/alerts/config',
        json={
            'user_id': 'test-user',
            'email_enabled': True,
            'email_address': 'test@example.com',
            'sms_enabled': False,
            'sms_number': None,
            'notify_immediately': True,
            'digest_enabled': False,
            'digest_hour': 9
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200

def test_get_pending_alerts():
    """Test getting pending alerts."""
    print("\n" + "="*80)
    print("TEST 2: Get Pending Alerts")
    print("="*80)
    
    response = requests.get(f'{BASE_URL}/alerts/pending')
    
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if data.get("success"):
        print(f"Total alerts: {data['data']['count']}")
        print(f"Alerts in response: {len(data['data']['pending_alerts'])}")
        
        if data['data']['pending_alerts']:
            print(f"\nFirst alert:")
            print(json.dumps(data['data']['pending_alerts'][0], indent=2, default=str))
    else:
        print(f"Error: {data.get('error')}")
    
    return response.status_code == 200

def test_trigger_scan():
    """Test triggering scanner."""
    print("\n" + "="*80)
    print("TEST 3: Trigger Scan")
    print("="*80)
    
    response = requests.get(f'{BASE_URL}/alerts/scan')
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, default=str)}")
    
    return response.status_code == 200

def test_health():
    """Test health check."""
    print("\n" + "="*80)
    print("TEST 4: Health Check")
    print("="*80)
    
    response = requests.get('http://localhost:8000/health')
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200

if __name__ == "__main__":
    print("\n🧪 ENDPOINT TESTING SUITE")
    print("Make sure the API is running: python3 main.py\n")
    
    results = {
        "Save Alert Config": test_save_alert_config(),
        "Get Pending Alerts": test_get_pending_alerts(),
        "Trigger Scan": test_trigger_scan(),
        "Health Check": test_health()
    }
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️  {total - passed} test(s) failed")