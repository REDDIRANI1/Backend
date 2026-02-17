#!/usr/bin/env python3
"""
Test script for webhook service.

This script tests:
1. Health check endpoint
2. Single transaction webhook
3. Duplicate transaction handling (idempotency)
4. Transaction status retrieval
"""

import requests
import time
import json
from datetime import datetime


# Configuration
BASE_URL = "http://localhost:8000"  # Change this to your deployed URL


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_health_check():
    """Test the health check endpoint."""
    print_section("Testing Health Check")
    
    response = requests.get(f"{BASE_URL}/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    assert response.json()["status"] == "HEALTHY"
    print("✅ Health check passed!")


def test_single_transaction():
    """Test sending a single transaction webhook."""
    print_section("Testing Single Transaction")
    
    transaction_data = {
        "transaction_id": f"txn_test_{int(time.time())}",
        "source_account": "acc_user_789",
        "destination_account": "acc_merchant_456",
        "amount": 1500.50,
        "currency": "INR"
    }
    
    print(f"Sending webhook: {json.dumps(transaction_data, indent=2)}")
    
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/v1/webhooks/transactions",
        json=transaction_data
    )
    response_time = (time.time() - start_time) * 1000
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Time: {response_time:.2f}ms")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 202
    assert response_time < 500, f"Response time {response_time}ms exceeds 500ms limit"
    print("✅ Single transaction test passed!")
    
    return transaction_data["transaction_id"]


def test_duplicate_transaction(transaction_id):
    """Test duplicate transaction handling (idempotency)."""
    print_section("Testing Duplicate Transaction (Idempotency)")
    
    transaction_data = {
        "transaction_id": transaction_id,
        "source_account": "acc_user_789",
        "destination_account": "acc_merchant_456",
        "amount": 1500.50,
        "currency": "INR"
    }
    
    print(f"Sending duplicate webhook with transaction_id: {transaction_id}")
    
    # Send the same transaction 3 times
    for i in range(3):
        response = requests.post(
            f"{BASE_URL}/v1/webhooks/transactions",
            json=transaction_data
        )
        print(f"Attempt {i+1}: Status {response.status_code}")
        assert response.status_code == 202
    
    print("✅ Duplicate transaction test passed!")


def test_transaction_status(transaction_id):
    """Test retrieving transaction status."""
    print_section("Testing Transaction Status Retrieval")
    
    print(f"Checking status for transaction: {transaction_id}")
    
    # Check immediately (should be PROCESSING)
    response = requests.get(f"{BASE_URL}/v1/transactions/{transaction_id}")
    print(f"\nImmediate check:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    transaction = response.json()[0]
    assert transaction["status"] == "PROCESSING"
    print("✅ Transaction is in PROCESSING status")
    
    # Wait for processing to complete (30 seconds + buffer)
    print("\nWaiting 35 seconds for processing to complete...")
    time.sleep(35)
    
    # Check again (should be PROCESSED)
    response = requests.get(f"{BASE_URL}/v1/transactions/{transaction_id}")
    print(f"\nAfter processing:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    transaction = response.json()[0]
    assert transaction["status"] == "PROCESSED"
    assert transaction["processed_at"] is not None
    print("✅ Transaction successfully processed!")


def test_nonexistent_transaction():
    """Test querying a non-existent transaction."""
    print_section("Testing Non-existent Transaction")
    
    fake_id = "txn_does_not_exist"
    response = requests.get(f"{BASE_URL}/v1/transactions/{fake_id}")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 404
    print("✅ Non-existent transaction test passed!")


def run_all_tests():
    """Run all tests in sequence."""
    print("\n" + "🚀" * 30)
    print("  WEBHOOK SERVICE TEST SUITE")
    print("🚀" * 30)
    
    try:
        # Test 1: Health Check
        test_health_check()
        
        # Test 2: Single Transaction
        transaction_id = test_single_transaction()
        
        # Test 3: Duplicate Transaction
        test_duplicate_transaction(transaction_id)
        
        # Test 4: Non-existent Transaction
        test_nonexistent_transaction()
        
        # Test 5: Transaction Status (includes waiting)
        test_transaction_status(transaction_id)
        
        print_section("ALL TESTS PASSED! 🎉")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {str(e)}")
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Could not connect to {BASE_URL}")
        print("Make sure the service is running!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")


if __name__ == "__main__":
    run_all_tests()
