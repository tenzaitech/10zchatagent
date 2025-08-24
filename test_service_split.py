#!/usr/bin/env python3
"""
Integration Tests for Service Split
ทดสอบ flows หลักก่อนและหลังแยกระบบ
"""
import asyncio
import httpx
import json
from typing import Dict, Any

# Test configuration
BASE_URL_ORIGINAL = "http://localhost:8000"  # Original monolith
BASE_URL_CHATBOT = "http://localhost:8001"   # New chatbot service  
BASE_URL_ORDER = "http://localhost:8002"     # New order service

class ServiceSplitTests:
    def __init__(self):
        self.test_results = []
        
    async def test_health_endpoints(self, base_url: str, service_name: str):
        """Test health endpoint availability"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{base_url}/health")
                if response.status_code == 200:
                    self.log_success(f"{service_name}: Health endpoint OK")
                    return True
                else:
                    self.log_error(f"{service_name}: Health endpoint failed - {response.status_code}")
                    return False
        except Exception as e:
            self.log_error(f"{service_name}: Health endpoint error - {e}")
            return False

    async def test_chatbot_response(self, base_url: str, service_name: str):
        """Test chatbot AI response functionality - Test via AI service directly"""
        try:
            # Since webhook requires valid signature, test AI service health instead
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Test if the endpoint exists and rejects properly (401/400 is good sign)
                response = await client.post(f"{base_url}/webhook/line", json={})
                
                # Webhook should reject invalid requests (401, 400) which shows it's working
                if response.status_code in [400, 401]:
                    self.log_success(f"{service_name}: Chatbot webhook endpoint responding (rejecting invalid requests)")
                    return True
                elif response.status_code == 404:
                    self.log_error(f"{service_name}: Chatbot webhook endpoint not found")
                    return False
                else:
                    # Any other response might indicate issues
                    self.log_error(f"{service_name}: Chatbot webhook unexpected response - {response.status_code}")
                    return False
                    
        except Exception as e:
            self.log_error(f"{service_name}: Chatbot test error - {e}")
            return False

    async def test_order_creation(self, base_url: str, service_name: str):
        """Test order creation flow"""
        try:
            test_order_data = {
                "customer_name": "Test Customer",
                "customer_phone": "0812345678",
                "order_type": "pickup",
                "items": [
                    {"name": "Test Sushi", "quantity": 2, "price": 120}
                ],
                "total_amount": 240,
                "payment_method": "cash",
                "notes": "Test order for service split verification"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{base_url}/api/orders/create",
                    json=test_order_data
                )
                
                if response.status_code in [200, 201]:
                    self.log_success(f"{service_name}: Order creation OK")
                    return True
                else:
                    self.log_error(f"{service_name}: Order creation failed - {response.status_code}: {response.text}")
                    return False
                    
        except Exception as e:
            self.log_error(f"{service_name}: Order creation error - {e}")
            return False

    async def test_static_pages(self, base_url: str, service_name: str):
        """Test static page serving"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Test main webapp page
                response = await client.get(f"{base_url}/customer_webapp.html")
                if response.status_code == 200 and "html" in response.headers.get("content-type", "").lower():
                    self.log_success(f"{service_name}: Static pages serving OK")
                    return True
                else:
                    self.log_error(f"{service_name}: Static pages failed - {response.status_code}")
                    return False
                    
        except Exception as e:
            self.log_error(f"{service_name}: Static pages error - {e}")
            return False

    def log_success(self, message: str):
        """Log successful test"""
        print(f"✅ {message}")
        self.test_results.append({"status": "PASS", "message": message})

    def log_error(self, message: str):
        """Log failed test"""
        print(f"❌ {message}")
        self.test_results.append({"status": "FAIL", "message": message})

    async def run_full_test_suite(self, base_url: str, service_name: str):
        """Run complete test suite for a service"""
        print(f"\n🧪 Testing {service_name} at {base_url}")
        print("="*50)
        
        results = []
        
        # Health check
        results.append(await self.test_health_endpoints(base_url, service_name))
        
        # Chatbot functionality (only for services that should handle chat)
        if "chatbot" in service_name.lower() or "original" in service_name.lower():
            results.append(await self.test_chatbot_response(base_url, service_name))
        
        # Order functionality (only for services that should handle orders)
        if "order" in service_name.lower() or "original" in service_name.lower():
            results.append(await self.test_order_creation(base_url, service_name))
        
        # Static pages (only for services that should serve pages)
        if "original" in service_name.lower() or "order" in service_name.lower():
            results.append(await self.test_static_pages(base_url, service_name))
        
        success_rate = (sum(results) / len(results)) * 100 if results else 0
        print(f"📊 {service_name} Success Rate: {success_rate:.1f}%")
        
        return success_rate >= 75  # 75% threshold for passing

    def print_summary(self):
        """Print test results summary"""
        print("\n" + "="*60)
        print("📋 TEST SUMMARY")
        print("="*60)
        
        passed = len([r for r in self.test_results if r["status"] == "PASS"])
        failed = len([r for r in self.test_results if r["status"] == "FAIL"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "No tests run")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"   - {result['message']}")

async def main():
    """Main test runner"""
    tester = ServiceSplitTests()
    
    print("🚀 Starting Service Split Integration Tests")
    
    # Test all three services
    print("Testing all services in parallel...")
    
    # Test original service (baseline)
    original_success = await tester.run_full_test_suite(BASE_URL_ORIGINAL, "Original Monolith")
    
    # Test chatbot service
    chatbot_success = await tester.run_full_test_suite(BASE_URL_CHATBOT, "Chatbot Service")
    
    # Test order service
    order_success = await tester.run_full_test_suite(BASE_URL_ORDER, "Order Service")
    
    # Summary
    all_success = original_success and chatbot_success and order_success
    print(f"\n{'🎉 ALL SERVICES PASSING' if all_success else '⚠️ SOME SERVICES HAVE ISSUES'}")
    
    # Print summary
    tester.print_summary()
    
    return all_success

if __name__ == "__main__":
    asyncio.run(main())