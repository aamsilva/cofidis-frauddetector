"""
Test script for Cofidis Fraud Detector
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health: {response.json()}")
    return response.status_code == 200

def test_transaction_evaluation():
    """Test transaction evaluation"""
    transaction = {
        "transaction_id": "TXN-TEST-001",
        "customer_id": "CUST-12345",
        "amount": 1500.00,
        "currency": "EUR",
        "merchant": "Unknown Electronics Store",
        "merchant_category": "electronics",
        "location": {"lat": 48.8566, "lon": 2.3522},  # Paris
        "timestamp": datetime.now().isoformat(),
        "card_type": "credit",
        "channel": "online"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/fraud/evaluate",
        json=transaction
    )
    
    result = response.json()
    print(f"\n📝 Transaction Evaluation:")
    print(f"  Risk Score: {result['risk_score']:.1f}/100")
    print(f"  Confidence: {result['confidence']:.2f}")
    print(f"  Action: {result['recommended_action']}")
    print(f"  Flags: {result['flags']}")
    print(f"  Explanation: {result['explanation'][:100]}...")
    print(f"  Processing Time: {result['processing_time_ms']:.1f}ms")
    
    return result

def test_multiple_transactions():
    """Test multiple scenarios"""
    scenarios = [
        {
            "name": "Normal transaction",
            "transaction": {
                "transaction_id": "TXN-NORMAL-001",
                "customer_id": "CUST-REGULAR",
                "amount": 50.00,
                "currency": "EUR",
                "merchant": "Supermarket",
                "location": {"lat": 38.7223, "lon": -9.1393},
                "timestamp": datetime.now().isoformat(),
                "card_type": "debit",
                "channel": "pos"
            }
        },
        {
            "name": "High amount transaction",
            "transaction": {
                "transaction_id": "TXN-HIGH-001",
                "customer_id": "CUST-REGULAR",
                "amount": 5000.00,
                "currency": "EUR",
                "merchant": "Luxury Store",
                "location": {"lat": 38.7223, "lon": -9.1393},
                "timestamp": datetime.now().isoformat(),
                "card_type": "credit",
                "channel": "online"
            }
        },
        {
            "name": "Suspicious time transaction",
            "transaction": {
                "transaction_id": "TXN-SUSP-001",
                "customer_id": "CUST-REGULAR",
                "amount": 800.00,
                "currency": "EUR",
                "merchant": "Online Casino",
                "location": {"lat": 40.7128, "lon": -74.0060},  # NYC
                "timestamp": "2024-02-12T03:30:00",  # 3:30 AM
                "card_type": "credit",
                "channel": "online"
            }
        }
    ]
    
    print("\n🧪 Testing Multiple Scenarios:")
    for scenario in scenarios:
        response = requests.post(
            f"{BASE_URL}/api/v1/fraud/evaluate",
            json=scenario["transaction"]
        )
        result = response.json()
        print(f"\n  {scenario['name']}:")
        print(f"    Score: {result['risk_score']:.1f} | Action: {result['recommended_action']}")

if __name__ == "__main__":
    print("🚀 Testing Cofidis Fraud Detector")
    print("=" * 50)
    
    try:
        if test_health():
            print("✅ System is healthy\n")
            
            # Test single transaction
            test_transaction_evaluation()
            
            # Test multiple scenarios
            test_multiple_transactions()
            
            print("\n✅ All tests completed!")
        else:
            print("❌ System is not healthy")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure the gateway is running: python gateway.py")
