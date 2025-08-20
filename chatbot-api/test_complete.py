#!/usr/bin/env python3
"""
Comprehensive Test Suite for Tenzai Chatbot API v2
Tests all functionality to ensure 100% compatibility
"""

import asyncio
import httpx
import json
import sys
from datetime import datetime
from typing import Dict, Any

class ComprehensiveTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.timeout = 15.0
        self.test_results = []
        
    def log_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append({
            "name": test_name,
            "passed": passed,
            "details": details
        })
        print(f"   {status}: {test_name}")
        if details and not passed:
            print(f"      Details: {details}")
    
    async def test_server_health(self):
        """Test basic server health"""
        print("\n🏥 Testing Server Health")
        print("-" * 40)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/")
                
            if response.status_code == 200:
                data = response.json()
                required_keys = {"status", "service", "timestamp"}
                has_keys = all(key in data for key in required_keys)
                
                self.log_result(
                    "Health endpoint structure",
                    has_keys and data.get("status") == "ok",
                    f"Response: {data}"
                )
            else:
                self.log_result(
                    "Health endpoint status",
                    False,
                    f"Expected 200, got {response.status_code}"
                )
                
        except Exception as e:
            self.log_result("Server connection", False, str(e))
    
    async def test_schema_endpoints(self):
        """Test schema inspection endpoints"""
        print("\n📋 Testing Schema Endpoints")
        print("-" * 40)
        
        endpoints = [
            "/api/schema/inspect",
            "/api/schema/sample-data"
        ]
        
        for endpoint in endpoints:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(f"{self.base_url}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    has_success = data.get("status") == "success"
                    
                    self.log_result(
                        f"Schema endpoint {endpoint}",
                        has_success,
                        f"Status: {data.get('status')}"
                    )
                else:
                    self.log_result(
                        f"Schema endpoint {endpoint}",
                        False,
                        f"HTTP {response.status_code}"
                    )
                    
            except Exception as e:
                self.log_result(f"Schema endpoint {endpoint}", False, str(e))
    
    async def test_order_creation(self):
        """Test order creation endpoint"""
        print("\n🛒 Testing Order Creation")
        print("-" * 40)
        
        # Test valid order (matching original structure from main_old.py)
        valid_order = {
            "contact": {
                "name": "Test User", 
                "phone": "0899999999"
            },
            "cart": [
                {
                    "menu_id": "2cb8cccd-96de-4bb5-a30b-93f6a48ec053",  # Real UUID from menus table
                    "qty": 2,
                    "note": "Test order"
                }
            ]
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/orders/create",
                    json=valid_order
                )
            
            if response.status_code == 200:
                data = response.json()
                has_order_number = "order_number" in data and data.get("success")
                
                self.log_result(
                    "Valid order creation",
                    has_order_number,
                    f"Order: {data.get('order_number', 'None')}"
                )
                
                # Store order number for status test
                if has_order_number:
                    self.test_order_number = data["order_number"]
                    
            else:
                self.log_result(
                    "Valid order creation",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}"
                )
                
        except Exception as e:
            self.log_result("Valid order creation", False, str(e))
        
        # Test invalid order (missing customer)
        invalid_order = {
            "items": [{"name": "Test", "price": 100, "quantity": 1}]
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/orders/create",
                    json=invalid_order
                )
            
            # Should return 400 for invalid data
            expected_error = response.status_code in [400, 422]
            self.log_result(
                "Invalid order rejection",
                expected_error,
                f"Status: {response.status_code}"
            )
            
        except Exception as e:
            self.log_result("Invalid order rejection", False, str(e))
    
    async def test_order_status(self):
        """Test order status endpoint"""
        print("\n📊 Testing Order Status")
        print("-" * 40)
        
        # Test with order created above (if exists)
        if hasattr(self, 'test_order_number'):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(
                        f"{self.base_url}/api/orders/{self.test_order_number}"
                    )
                
                if response.status_code == 200:
                    data = response.json()
                    has_required_fields = all(
                        field in data for field in 
                        ["order_number", "status", "total_amount", "created_at"]
                    )
                    
                    self.log_result(
                        f"Order status for {self.test_order_number}",
                        has_required_fields,
                        f"Status: {data.get('status')}"
                    )
                else:
                    self.log_result(
                        f"Order status for {self.test_order_number}",
                        False,
                        f"HTTP {response.status_code}"
                    )
                    
            except Exception as e:
                self.log_result(f"Order status lookup", False, str(e))
        
        # Test with non-existent order
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/orders/NONEXISTENT123"
                )
            
            # Should return 404 for non-existent order
            expected_404 = response.status_code == 404
            self.log_result(
                "Non-existent order handling",
                expected_404,
                f"Status: {response.status_code}"
            )
            
        except Exception as e:
            self.log_result("Non-existent order handling", False, str(e))
    
    async def test_line_webhook(self):
        """Test LINE webhook endpoint (structure only)"""
        print("\n📱 Testing LINE Webhook")
        print("-" * 40)
        
        # Test invalid webhook (no signature)
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/webhook/line",
                    json={"events": []}
                )
            
            # Should reject requests without signature
            expected_rejection = response.status_code in [400, 401]
            self.log_result(
                "LINE webhook security",
                expected_rejection,
                f"Status: {response.status_code}"
            )
            
        except Exception as e:
            self.log_result("LINE webhook security", False, str(e))
    
    async def test_modules_integration(self):
        """Test that all modules work together"""
        print("\n🧩 Testing Module Integration")
        print("-" * 40)
        
        try:
            # Test config module
            from modules.config import validate_config, FAQ_RESPONSES
            config_valid = validate_config()
            has_faq = len(FAQ_RESPONSES) >= 5
            
            self.log_result(
                "Config module integration",
                config_valid and has_faq,
                f"Config valid: {config_valid}, FAQ count: {len(FAQ_RESPONSES)}"
            )
            
        except Exception as e:
            self.log_result("Config module integration", False, str(e))
        
        try:
            # Test AI service
            from services.ai_service import classify_intent
            intent = classify_intent("ร้านเปิดกี่โมง")
            correct_intent = intent == "hours"
            
            self.log_result(
                "AI service integration",
                correct_intent,
                f"Intent: {intent}"
            )
            
        except Exception as e:
            self.log_result("AI service integration", False, str(e))
        
        try:
            # Test database service
            from services.database_service import generate_platform_id
            platform_id = generate_platform_id("LINE", "test123")
            correct_format = platform_id == "LINE_test123"
            
            self.log_result(
                "Database service integration",
                correct_format,
                f"Platform ID: {platform_id}"
            )
            
        except Exception as e:
            self.log_result("Database service integration", False, str(e))
    
    async def run_all_tests(self):
        """Run all comprehensive tests"""
        print("🧪 Comprehensive System Testing")
        print("=" * 50)
        print(f"🕐 Started at: {datetime.now()}")
        print(f"🎯 Target: {self.base_url}")
        
        # Run all test categories
        await self.test_server_health()
        await self.test_schema_endpoints()
        await self.test_order_creation()
        await self.test_order_status()
        await self.test_line_webhook()
        await self.test_modules_integration()
        
        # Generate summary
        self.print_summary()
        
        # Return success status
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        total_tests = len(self.test_results)
        return passed_tests == total_tests
    
    def print_summary(self):
        """Print test summary"""
        passed = sum(1 for result in self.test_results if result["passed"])
        failed = sum(1 for result in self.test_results if not result["passed"])
        total = len(self.test_results)
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        print("\n" + "=" * 50)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("-" * 50)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Total: {total}")
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        if failed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"   • {result['name']}: {result['details']}")
        
        if success_rate == 100:
            print("\n🎉 ALL TESTS PASSED - System is 100% functional!")
        else:
            print(f"\n⚠️  {failed} tests failed - Review issues above")
        
        print(f"\n🕐 Completed at: {datetime.now()}")

async def main():
    """Main test execution"""
    tester = ComprehensiveTester()
    
    success = await tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)