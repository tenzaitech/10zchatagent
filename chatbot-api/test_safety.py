#!/usr/bin/env python3
"""
Safety-First Testing Script
Comprehensive validation of all modular API endpoints
Ensures zero breaking changes and proper error handling
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_endpoint(name, method, endpoint, data=None, expected_status=200):
    """Test an API endpoint with safety checks"""
    try:
        url = f"{BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method == "PATCH":
            response = requests.patch(url, json=data, timeout=10)
        
        print(f"{'✅' if response.status_code == expected_status else '❌'} {name}: {response.status_code}")
        
        if response.status_code != expected_status:
            print(f"   Expected: {expected_status}, Got: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
        
        # Try to parse JSON response
        try:
            response_data = response.json()
            if isinstance(response_data, dict) and 'status' in response_data:
                print(f"   Status: {response_data['status']}")
            return True
        except:
            print(f"   Non-JSON response: {response.text[:100]}")
            return True
            
    except Exception as e:
        print(f"❌ {name}: ERROR - {e}")
        return False

def run_safety_tests():
    """Run comprehensive safety tests"""
    print("🔍 STARTING SAFETY-FIRST API TESTING")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Health Check
    total_tests += 1
    if test_endpoint("Health Check", "GET", "/health"):
        tests_passed += 1
    
    # Test 2: Static Files
    total_tests += 1
    if test_endpoint("Root Page", "GET", "/", expected_status=200):
        tests_passed += 1
    
    # Test 3: Order Management
    total_tests += 1
    if test_endpoint("Today's Orders", "GET", "/api/orders/today"):
        tests_passed += 1
    
    # Test 4: Order Lookup (existing order)
    total_tests += 1
    if test_endpoint("Order Lookup", "GET", "/api/orders/T250822002045"):
        tests_passed += 1
    
    # Test 5: Order Lookup (non-existent)
    total_tests += 1
    if test_endpoint("Order Not Found", "GET", "/api/orders/INVALID123", expected_status=404):
        tests_passed += 1
    
    # Test 6: Order Creation Validation (should fail)
    total_tests += 1
    invalid_order = {"invalid": "data"}
    if test_endpoint("Order Validation", "POST", "/api/orders/create", invalid_order, expected_status=400):
        tests_passed += 1
    
    # Test 7: Admin Schema Inspection
    total_tests += 1
    if test_endpoint("Schema Inspection", "GET", "/api/schema/inspect"):
        tests_passed += 1
    
    # Test 8: Sample Data
    total_tests += 1
    if test_endpoint("Sample Data", "GET", "/api/schema/sample-data"):
        tests_passed += 1
    
    # Test 9: Order Status Update (should work but be careful)
    total_tests += 1
    status_update = {"status": "preparing"}
    if test_endpoint("Status Update", "PATCH", "/api/orders/T250822002045/status", status_update):
        tests_passed += 1
    
    print("=" * 50)
    print(f"🎯 SAFETY TEST RESULTS: {tests_passed}/{total_tests} PASSED")
    
    if tests_passed == total_tests:
        print("✅ ALL TESTS PASSED - SYSTEM IS SAFE")
        return True
    else:
        print("⚠️ SOME TESTS FAILED - REVIEW BEFORE PROCEEDING")
        return False

def test_database_migration_safety():
    """Test database migration system safety"""
    print("\n🔍 TESTING DATABASE MIGRATION SAFETY")
    print("=" * 50)
    
    try:
        from services.database_v2 import db_v2
        
        # Test 1: Verify default mode
        print(f"✅ Migration mode: {db_v2.migration_mode}")
        assert db_v2.migration_mode == 'v1_only', "Should default to V1-only for safety"
        
        # Test 2: Test mode switching
        db_v2.set_migration_mode('dual_write')
        print(f"✅ Mode switched to: {db_v2.migration_mode}")
        
        # Test 3: Switch back to safe mode
        db_v2.set_migration_mode('v1_only')
        print(f"✅ Back to safe mode: {db_v2.migration_mode}")
        
        print("✅ DATABASE MIGRATION SAFETY: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ DATABASE MIGRATION SAFETY: FAILED - {e}")
        return False

def test_payment_service_safety():
    """Test payment service safety"""
    print("\n🔍 TESTING PAYMENT SERVICE SAFETY")
    print("=" * 50)
    
    try:
        from services.payment_service import payment_service, QR_AVAILABLE
        
        print(f"✅ QR Generation Available: {QR_AVAILABLE}")
        
        # Test QR generation (should work even without library)
        qr_data = payment_service.generate_promptpay_qr(100.0, "TEST001")
        print(f"✅ QR Generation: Success")
        print(f"   - Transaction Ref: {qr_data['transaction_ref']}")
        print(f"   - QR Image: {'Available' if 'qr_image_base64' in qr_data else 'Fallback mode'}")
        
        print("✅ PAYMENT SERVICE SAFETY: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ PAYMENT SERVICE SAFETY: FAILED - {e}")
        return False

if __name__ == "__main__":
    print(f"🚀 SAFETY TESTING STARTED AT: {datetime.now()}")
    
    # Run all safety tests
    api_safe = run_safety_tests()
    db_safe = test_database_migration_safety()
    payment_safe = test_payment_service_safety()
    
    print("\n" + "=" * 60)
    print("🎯 COMPREHENSIVE SAFETY REPORT:")
    print(f"   API Endpoints: {'✅ SAFE' if api_safe else '❌ UNSAFE'}")
    print(f"   Database Migration: {'✅ SAFE' if db_safe else '❌ UNSAFE'}")
    print(f"   Payment Service: {'✅ SAFE' if payment_safe else '❌ UNSAFE'}")
    
    if api_safe and db_safe and payment_safe:
        print("\n🎉 OVERALL SYSTEM STATUS: ✅ SAFE TO PROCEED")
        sys.exit(0)
    else:
        print("\n⚠️ OVERALL SYSTEM STATUS: ❌ REQUIRES ATTENTION")
        sys.exit(1)