#!/usr/bin/env python3
"""
Edge Cases & Error Handling Test
Test system robustness under unusual conditions
Ensure graceful failure and proper error messages
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_malformed_requests():
    """Test handling of malformed requests"""
    print("🔍 TESTING MALFORMED REQUESTS")
    print("=" * 40)
    
    test_cases = [
        {
            "name": "Empty JSON",
            "method": "POST",
            "endpoint": "/api/orders/create",
            "data": {},
            "expected_status": 400
        },
        {
            "name": "Invalid JSON",
            "method": "POST",
            "endpoint": "/api/orders/create",
            "data": "invalid json string",
            "expected_status": 422
        },
        {
            "name": "Missing Content-Type",
            "method": "POST", 
            "endpoint": "/api/orders/create",
            "data": {"test": "data"},
            "headers": {},
            "expected_status": 422
        },
        {
            "name": "Oversized Request",
            "method": "POST",
            "endpoint": "/api/orders/create", 
            "data": {"notes": "x" * 10000},  # Very long string
            "expected_status": 400
        }
    ]
    
    passed = 0
    for test in test_cases:
        try:
            headers = test.get("headers", {"Content-Type": "application/json"})
            
            if test["method"] == "POST":
                if isinstance(test["data"], str):
                    # Send raw string for invalid JSON test
                    response = requests.post(
                        f"{BASE_URL}{test['endpoint']}", 
                        data=test["data"],
                        headers=headers,
                        timeout=5
                    )
                else:
                    response = requests.post(
                        f"{BASE_URL}{test['endpoint']}", 
                        json=test["data"],
                        headers=headers,
                        timeout=5
                    )
            
            status_ok = response.status_code in [test["expected_status"], 400, 422]
            print(f"{'✅' if status_ok else '❌'} {test['name']}: {response.status_code}")
            
            if status_ok:
                passed += 1
            else:
                print(f"   Expected: {test['expected_status']}, Got: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {test['name']}: Exception - {e}")
    
    print(f"📊 Malformed Requests: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)

def test_boundary_conditions():
    """Test boundary conditions and limits"""
    print("\n🔍 TESTING BOUNDARY CONDITIONS")
    print("=" * 40)
    
    test_cases = [
        {
            "name": "Non-existent Order",
            "endpoint": "/api/orders/NONEXISTENT123",
            "expected_status": 404
        },
        {
            "name": "Invalid Order Number Format",
            "endpoint": "/api/orders/invalid-format!@#",
            "expected_status": 404
        },
        {
            "name": "Very Long Order Number",
            "endpoint": f"/api/orders/{'x' * 100}",
            "expected_status": 404
        },
        {
            "name": "SQL Injection Attempt",
            "endpoint": "/api/orders/'; DROP TABLE orders; --",
            "expected_status": 404
        }
    ]
    
    passed = 0
    for test in test_cases:
        try:
            response = requests.get(f"{BASE_URL}{test['endpoint']}", timeout=5)
            status_ok = response.status_code == test["expected_status"]
            print(f"{'✅' if status_ok else '❌'} {test['name']}: {response.status_code}")
            
            if status_ok:
                passed += 1
            else:
                print(f"   Expected: {test['expected_status']}, Got: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {test['name']}: Exception - {e}")
    
    print(f"📊 Boundary Conditions: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)

def test_concurrent_safety():
    """Test concurrent access safety"""
    print("\n🔍 TESTING CONCURRENT SAFETY")
    print("=" * 40)
    
    import threading
    import time
    
    results = {"successes": 0, "errors": 0}
    
    def make_request():
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                results["successes"] += 1
            else:
                results["errors"] += 1
        except:
            results["errors"] += 1
    
    # Start 10 concurrent requests
    threads = []
    for _ in range(10):
        thread = threading.Thread(target=make_request)
        threads.append(thread)
        thread.start()
    
    # Wait for all to complete
    for thread in threads:
        thread.join()
    
    success_rate = (results["successes"] / 10) * 100
    print(f"✅ Concurrent Requests: {results['successes']}/10 successful ({success_rate:.1f}%)")
    
    return success_rate >= 90

def test_data_validation():
    """Test comprehensive data validation"""
    print("\n🔍 TESTING DATA VALIDATION")
    print("=" * 40)
    
    validation_tests = [
        {
            "name": "Missing Customer Name",
            "data": {
                "customer_phone": "0812345678",
                "items": [{"name": "Test Item", "quantity": 1, "price": 100}],
                "total_amount": 100,
                "order_type": "pickup"
            },
            "should_fail": True
        },
        {
            "name": "Invalid Phone Format",
            "data": {
                "customer_name": "Test Customer",
                "customer_phone": "invalid",
                "items": [{"name": "Test Item", "quantity": 1, "price": 100}],
                "total_amount": 100,
                "order_type": "pickup"
            },
            "should_fail": True
        },
        {
            "name": "Empty Items Array",
            "data": {
                "customer_name": "Test Customer", 
                "customer_phone": "0812345678",
                "items": [],
                "total_amount": 100,
                "order_type": "pickup"
            },
            "should_fail": True
        },
        {
            "name": "Negative Total Amount",
            "data": {
                "customer_name": "Test Customer",
                "customer_phone": "0812345678", 
                "items": [{"name": "Test Item", "quantity": 1, "price": 100}],
                "total_amount": -100,
                "order_type": "pickup"
            },
            "should_fail": True
        },
        {
            "name": "Invalid Order Type",
            "data": {
                "customer_name": "Test Customer",
                "customer_phone": "0812345678",
                "items": [{"name": "Test Item", "quantity": 1, "price": 100}],
                "total_amount": 100,
                "order_type": "invalid_type"
            },
            "should_fail": True
        }
    ]
    
    passed = 0
    for test in validation_tests:
        try:
            response = requests.post(
                f"{BASE_URL}/api/orders/create",
                json=test["data"],
                timeout=5
            )
            
            if test["should_fail"]:
                # Should return 400 (validation error)
                if response.status_code == 400:
                    print(f"✅ {test['name']}: Correctly rejected ({response.status_code})")
                    passed += 1
                else:
                    print(f"❌ {test['name']}: Should have failed but got {response.status_code}")
            else:
                # Should succeed (200)
                if response.status_code == 200:
                    print(f"✅ {test['name']}: Correctly accepted")
                    passed += 1
                else:
                    print(f"❌ {test['name']}: Should have succeeded but got {response.status_code}")
                    
        except Exception as e:
            print(f"❌ {test['name']}: Exception - {e}")
    
    print(f"📊 Data Validation: {passed}/{len(validation_tests)} passed")
    return passed == len(validation_tests)

if __name__ == "__main__":
    print("🔍 EDGE CASES & ERROR HANDLING TESTING")
    print("Testing system robustness under unusual conditions")
    print()
    
    # Run all edge case tests
    malformed_ok = test_malformed_requests()
    boundary_ok = test_boundary_conditions()
    concurrent_ok = test_concurrent_safety()
    validation_ok = test_data_validation()
    
    print("\n" + "=" * 60)
    print("🎯 EDGE CASE TESTING RESULTS:")
    print(f"   🔧 Malformed Requests: {'✅ PASSED' if malformed_ok else '❌ FAILED'}")
    print(f"   🚧 Boundary Conditions: {'✅ PASSED' if boundary_ok else '❌ FAILED'}")
    print(f"   🔄 Concurrent Safety: {'✅ PASSED' if concurrent_ok else '❌ FAILED'}")
    print(f"   📝 Data Validation: {'✅ PASSED' if validation_ok else '❌ FAILED'}")
    
    if all([malformed_ok, boundary_ok, concurrent_ok, validation_ok]):
        print("\n🎉 OVERALL ROBUSTNESS: ✅ EXCELLENT")
        print("System handles edge cases gracefully!")
        sys.exit(0)
    else:
        print("\n⚠️ OVERALL ROBUSTNESS: ❌ NEEDS IMPROVEMENT")
        sys.exit(1)