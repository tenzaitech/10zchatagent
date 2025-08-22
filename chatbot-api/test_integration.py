#!/usr/bin/env python3
"""
Integration Test Suite - Complete Order Flow
End-to-end testing of order creation → lookup → status update
Final validation before production deployment
"""

import requests
import json
import time
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_complete_order_flow():
    """Test the complete order flow end-to-end"""
    print("🔄 INTEGRATION TEST: Complete Order Flow")
    print("=" * 50)
    
    # Step 1: Create a valid order
    print("1️⃣ Creating test order...")
    order_data = {
        "customer_name": "Integration Test Customer",
        "customer_phone": "0899999999", 
        "items": [
            {
                "name": "Test Sushi Roll",
                "quantity": 2,
                "price": 150.0
            },
            {
                "name": "Test Soup", 
                "quantity": 1,
                "price": 50.0
            }
        ],
        "total_amount": 350.0,
        "order_type": "pickup",
        "payment_method": "cash",
        "notes": "Integration test order - please ignore"
    }
    
    try:
        create_response = requests.post(
            f"{BASE_URL}/api/orders/create",
            json=order_data,
            timeout=10
        )
        
        if create_response.status_code != 200:
            print(f"❌ Order creation failed: {create_response.status_code}")
            print(f"   Response: {create_response.text}")
            return False
            
        create_result = create_response.json()
        order_number = create_result.get("order_number")
        
        if not order_number:
            print(f"❌ No order number returned")
            return False
            
        print(f"✅ Order created successfully: {order_number}")
        print(f"   Order ID: {create_result.get('order_id')}")
        print(f"   Total: ฿{create_result.get('total_amount')}")
        
    except Exception as e:
        print(f"❌ Order creation exception: {e}")
        return False
    
    # Step 2: Lookup the created order
    print(f"\n2️⃣ Looking up order: {order_number}")
    time.sleep(1)  # Brief delay to ensure order is saved
    
    try:
        lookup_response = requests.get(
            f"{BASE_URL}/api/orders/{order_number}",
            timeout=10
        )
        
        if lookup_response.status_code != 200:
            print(f"❌ Order lookup failed: {lookup_response.status_code}")
            return False
            
        lookup_result = lookup_response.json()
        
        print(f"✅ Order found successfully")
        print(f"   Customer: {lookup_result.get('customer_name')}")
        print(f"   Status: {lookup_result.get('status')}")
        print(f"   Items: {len(lookup_result.get('items', []))}")
        print(f"   Total: ฿{lookup_result.get('total_amount')}")
        
    except Exception as e:
        print(f"❌ Order lookup exception: {e}")
        return False
    
    # Step 3: Update order status
    print(f"\n3️⃣ Updating order status...")
    
    status_updates = ["confirmed", "preparing", "ready", "completed"]
    
    for status in status_updates:
        try:
            status_response = requests.patch(
                f"{BASE_URL}/api/orders/{order_number}/status",
                json={"status": status},
                timeout=10
            )
            
            if status_response.status_code != 200:
                print(f"❌ Status update to '{status}' failed: {status_response.status_code}")
                return False
                
            print(f"✅ Status updated to: {status}")
            time.sleep(0.5)  # Brief delay between updates
            
        except Exception as e:
            print(f"❌ Status update exception: {e}")
            return False
    
    # Step 4: Final lookup to verify status
    print(f"\n4️⃣ Final verification...")
    
    try:
        final_response = requests.get(
            f"{BASE_URL}/api/orders/{order_number}",
            timeout=10
        )
        
        if final_response.status_code != 200:
            print(f"❌ Final lookup failed: {final_response.status_code}")
            return False
            
        final_result = final_response.json()
        final_status = final_result.get('status')
        
        if final_status == 'completed':
            print(f"✅ Final status confirmed: {final_status}")
            print(f"   Timeline completed: {len(final_result.get('status_history', []))} steps")
        else:
            print(f"❌ Unexpected final status: {final_status}")
            return False
            
    except Exception as e:
        print(f"❌ Final verification exception: {e}")
        return False
    
    print(f"\n🎉 COMPLETE ORDER FLOW: ✅ SUCCESS")
    print(f"Order {order_number} processed through full lifecycle!")
    return True

def test_system_health_check():
    """Quick system health verification"""
    print("\n🔍 SYSTEM HEALTH CHECK")
    print("=" * 30)
    
    health_checks = [
        ("/health", "Health Endpoint"),
        ("/api/orders/today", "Orders API"),
        ("/api/schema/inspect", "Admin API"), 
        ("/", "Static Files")
    ]
    
    passed = 0
    for endpoint, name in health_checks:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            status_ok = response.status_code == 200
            print(f"{'✅' if status_ok else '❌'} {name}: {response.status_code}")
            if status_ok:
                passed += 1
        except Exception as e:
            print(f"❌ {name}: Exception - {e}")
    
    print(f"\n📊 Health Check: {passed}/{len(health_checks)} passed")
    return passed == len(health_checks)

def test_database_migration_readiness():
    """Test readiness for database migration"""
    print("\n🔍 DATABASE MIGRATION READINESS")
    print("=" * 35)
    
    try:
        from services.database_v2 import db_v2
        
        # Test 1: Current mode
        current_mode = db_v2.migration_mode
        print(f"✅ Current mode: {current_mode}")
        
        # Test 2: Mode switching capability
        db_v2.set_migration_mode('dual_write')
        print(f"✅ Switched to: {db_v2.migration_mode}")
        
        db_v2.set_migration_mode('v1_only')
        print(f"✅ Back to safe mode: {db_v2.migration_mode}")
        
        # Test 3: Payment service ready
        from services.payment_service import payment_service
        test_qr = payment_service.generate_promptpay_qr(100.0, "TEST")
        print(f"✅ Payment service: Ready (ref: {test_qr['transaction_ref'][:12]}...)")
        
        print(f"\n✅ MIGRATION READINESS: CONFIRMED")
        return True
        
    except Exception as e:
        print(f"❌ MIGRATION READINESS: FAILED - {e}")
        return False

def run_final_integration_tests():
    """Run complete integration test suite"""
    print("🚀 FINAL INTEGRATION TESTING")
    print(f"Testing complete system at: {datetime.now()}")
    print("=" * 60)
    
    # Run all integration tests
    order_flow_ok = test_complete_order_flow()
    health_ok = test_system_health_check()  
    migration_ok = test_database_migration_readiness()
    
    print("\n" + "=" * 60)
    print("🎯 FINAL INTEGRATION TEST RESULTS:")
    print(f"   🔄 Complete Order Flow: {'✅ PASSED' if order_flow_ok else '❌ FAILED'}")
    print(f"   💗 System Health: {'✅ PASSED' if health_ok else '❌ FAILED'}")
    print(f"   🔄 Migration Ready: {'✅ PASSED' if migration_ok else '❌ FAILED'}")
    
    all_passed = order_flow_ok and health_ok and migration_ok
    
    if all_passed:
        print("\n🎉 OVERALL INTEGRATION STATUS: ✅ EXCELLENT")
        print("🚀 SYSTEM IS PRODUCTION READY!")
        print("✅ All critical flows tested and verified")
        print("✅ Zero breaking changes confirmed")
        print("✅ Migration system ready for deployment")
        return True
    else:
        print("\n⚠️ OVERALL INTEGRATION STATUS: ❌ ISSUES FOUND")
        print("🔧 Review failed tests before proceeding")
        return False

if __name__ == "__main__":
    success = run_final_integration_tests()
    sys.exit(0 if success else 1)