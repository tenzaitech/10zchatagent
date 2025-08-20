#!/usr/bin/env python3
"""
System Test Script - ทดสอบระบบก่อนและหลังแยกไฟล์
ต้องผ่าน 100% ก่อนเปลี่ยน structure
"""
import requests
import json
import time
from typing import Dict, Any

# API Base URLs
API_BASE_URL = "http://localhost:8000"

class SystemTester:
    def __init__(self, api_url: str = API_BASE_URL):
        self.api_url = api_url
        self.test_results = []
        
    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({"name": name, "success": success, "details": details})
        print(f"{status} {name}")
        if details:
            print(f"   Details: {details}")
        
    def test_health_check(self) -> bool:
        """Test API health endpoint"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=5)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Service: {data.get('service', 'Unknown')}"
            self.log_test("Health Check", success, details)
            return success
        except Exception as e:
            self.log_test("Health Check", False, str(e))
            return False
            
    def test_schema_endpoints(self) -> bool:
        """Test database schema endpoints"""
        try:
            # Test sample data endpoint
            response = requests.get(f"{self.api_url}/api/schema/sample-data", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Tables: {len(data.get('samples', {}))}"
            self.log_test("Schema Sample Data", success, details)
            return success
        except Exception as e:
            self.log_test("Schema Sample Data", False, str(e))
            return False
            
    def test_order_creation(self) -> tuple[bool, str]:
        """Test order creation endpoint"""
        try:
            # Test order data
            order_data = {
                "cart": [
                    {
                        "menu_id": "2cb8cccd-96de-4bb5-a30b-93f6a48ec053",  # Real menu ID
                        "qty": 1,
                        "note": "Test order"
                    }
                ],
                "contact": {
                    "name": "Test User Refactor",
                    "phone": "0812345681"
                },
                "platform": "WEB",
                "platform_user_id": None
            }
            
            response = requests.post(
                f"{self.api_url}/api/orders/create",
                json=order_data,
                timeout=15
            )
            
            success = response.status_code == 200
            order_id = ""
            
            if success:
                data = response.json()
                order_id = data.get("order_id", "")
                details = f"Order ID: {order_id}, Total: {data.get('total_price', 0)}"
            else:
                details = f"Status: {response.status_code}, Error: {response.text[:100]}"
                
            self.log_test("Order Creation", success, details)
            return success, order_id
            
        except Exception as e:
            self.log_test("Order Creation", False, str(e))
            return False, ""
            
    def test_order_status(self, order_id: str) -> bool:
        """Test order status endpoint"""
        if not order_id:
            self.log_test("Order Status", False, "No order ID provided")
            return False
            
        try:
            response = requests.get(f"{self.api_url}/api/orders/{order_id}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Status: {data.get('status', 'unknown')}, Items: {len(data.get('items', []))}"
            else:
                details = f"HTTP {response.status_code}: {response.text[:100]}"
                
            self.log_test("Order Status", success, details)
            return success
            
        except Exception as e:
            self.log_test("Order Status", False, str(e))
            return False
            
    def test_line_webhook_structure(self) -> bool:
        """Test LINE webhook endpoint structure (without real webhook)"""
        try:
            # Test with invalid data to check structure
            response = requests.post(
                f"{self.api_url}/webhook/line",
                json={"test": "structure"},
                timeout=5
            )
            
            # Should return 400 (missing signature) or 401 (invalid signature)
            # NOT 404 (endpoint exists) or 500 (server error)
            success = response.status_code in [400, 401]
            details = f"Status: {response.status_code} (Expected 400/401 for invalid request)"
            
            self.log_test("LINE Webhook Structure", success, details)
            return success
            
        except Exception as e:
            self.log_test("LINE Webhook Structure", False, str(e))
            return False
            
    def run_all_tests(self) -> Dict[str, Any]:
        """Run complete system test"""
        print(f"\n🧪 Running System Tests on {self.api_url}")
        print("=" * 50)
        
        start_time = time.time()
        
        # Core tests
        health_ok = self.test_health_check()
        schema_ok = self.test_schema_endpoints()
        order_ok, order_id = self.test_order_creation()
        status_ok = self.test_order_status(order_id)
        webhook_ok = self.test_line_webhook_structure()
        
        # Summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        
        duration = time.time() - start_time
        
        print("\n" + "=" * 50)
        print(f"📊 Test Results Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {total_tests - passed_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"   Duration: {duration:.2f}s")
        
        all_passed = passed_tests == total_tests
        
        if all_passed:
            print("🎉 ALL TESTS PASSED - System is ready for refactoring!")
        else:
            print("⚠️  SOME TESTS FAILED - DO NOT PROCEED with refactoring!")
            print("\nFailed tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   ❌ {result['name']}: {result['details']}")
        
        return {
            "all_passed": all_passed,
            "total": total_tests,
            "passed": passed_tests,
            "duration": duration,
            "results": self.test_results
        }

def main():
    """Main test runner"""
    tester = SystemTester()
    result = tester.run_all_tests()
    
    # Exit with proper code
    exit_code = 0 if result["all_passed"] else 1
    exit(exit_code)

if __name__ == "__main__":
    main()