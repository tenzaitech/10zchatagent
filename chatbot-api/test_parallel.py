#!/usr/bin/env python3
"""
Parallel testing script
Compare main.py (port 8000) vs main_v2.py (port 8001)
"""

import asyncio
import httpx
import json
from datetime import datetime

class ParallelTester:
    def __init__(self):
        self.main_v1_url = "http://localhost:8000"
        self.main_v2_url = "http://localhost:8001"
        self.timeout = 10.0
    
    async def test_endpoint(self, endpoint: str, method: str = "GET", data: dict = None):
        """Test same endpoint on both servers"""
        print(f"\n🧪 Testing {method} {endpoint}")
        
        results = {"v1": None, "v2": None}
        errors = {"v1": None, "v2": None}
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # Test v1 (main.py)
            try:
                if method == "GET":
                    response_v1 = await client.get(f"{self.main_v1_url}{endpoint}")
                elif method == "POST":
                    response_v1 = await client.post(f"{self.main_v1_url}{endpoint}", json=data)
                
                results["v1"] = {
                    "status": response_v1.status_code,
                    "data": response_v1.json() if response_v1.text else {}
                }
                print(f"   v1: {response_v1.status_code}")
            except Exception as e:
                errors["v1"] = str(e)
                print(f"   v1: ERROR - {e}")
            
            # Test v2 (main_v2.py)
            try:
                if method == "GET":
                    response_v2 = await client.get(f"{self.main_v2_url}{endpoint}")
                elif method == "POST":
                    response_v2 = await client.post(f"{self.main_v2_url}{endpoint}", json=data)
                
                results["v2"] = {
                    "status": response_v2.status_code,
                    "data": response_v2.json() if response_v2.text else {}
                }
                print(f"   v2: {response_v2.status_code}")
            except Exception as e:
                errors["v2"] = str(e)
                print(f"   v2: ERROR - {e}")
        
        return results, errors
    
    def compare_results(self, results: dict, endpoint: str) -> bool:
        """Compare results from both versions"""
        v1_result = results["v1"]
        v2_result = results["v2"]
        
        if not v1_result or not v2_result:
            print(f"   ❌ {endpoint}: One or both servers failed")
            return False
        
        if v1_result["status"] != v2_result["status"]:
            print(f"   ❌ {endpoint}: Status codes differ - v1:{v1_result['status']} vs v2:{v2_result['status']}")
            return False
        
        # Compare data structure (keys should match)
        v1_keys = set(v1_result["data"].keys()) if isinstance(v1_result["data"], dict) else set()
        v2_keys = set(v2_result["data"].keys()) if isinstance(v2_result["data"], dict) else set()
        
        if v1_keys != v2_keys:
            print(f"   ❌ {endpoint}: Response structure differs")
            print(f"      v1 keys: {v1_keys}")
            print(f"      v2 keys: {v2_keys}")
            return False
        
        print(f"   ✅ {endpoint}: Results match!")
        return True
    
    async def run_comparison_tests(self):
        """Run all comparison tests"""
        print("🔄 Parallel Testing: main.py vs main_v2.py")
        print("=" * 60)
        
        test_cases = [
            ("/", "GET", None),
            ("/api/schema/inspect", "GET", None),
            ("/api/schema/sample-data", "GET", None),
        ]
        
        passed = 0
        total = len(test_cases)
        
        for endpoint, method, data in test_cases:
            try:
                results, errors = await self.test_endpoint(endpoint, method, data)
                if self.compare_results(results, endpoint):
                    passed += 1
                    
            except Exception as e:
                print(f"   ❌ {endpoint}: Test failed - {e}")
        
        print("\n" + "=" * 60)
        print(f"📊 Comparison Results:")
        print(f"   Total Tests: {total}")
        print(f"   Passed: {passed}")
        print(f"   Failed: {total - passed}")
        print(f"   Match Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED - Both versions behave identically!")
            return True
        else:
            print("⚠️ SOME TESTS FAILED - Check differences above")
            return False
    
    async def health_check_both(self):
        """Quick health check for both servers"""
        print("🏥 Health Check Both Servers")
        print("-" * 30)
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Check v1
            try:
                response_v1 = await client.get(f"{self.main_v1_url}/")
                v1_data = response_v1.json()
                print(f"✅ v1 ({self.main_v1_url}): {v1_data.get('message', 'OK')}")
            except Exception as e:
                print(f"❌ v1 ({self.main_v1_url}): {e}")
                return False
            
            # Check v2
            try:
                response_v2 = await client.get(f"{self.main_v2_url}/")
                v2_data = response_v2.json()
                print(f"✅ v2 ({self.main_v2_url}): {v2_data.get('message', 'OK')}")
            except Exception as e:
                print(f"❌ v2 ({self.main_v2_url}): {e}")
                return False
        
        return True

async def main():
    """Main testing function"""
    tester = ParallelTester()
    
    # Health check first
    if not await tester.health_check_both():
        print("\n❌ Health check failed! Make sure both servers are running:")
        print("   Terminal 1: python3 main.py")
        print("   Terminal 2: python3 main_v2.py")
        return 1
    
    # Run comparison tests
    if await tester.run_comparison_tests():
        print("\n🎯 CONCLUSION: main_v2.py is ready for production!")
        return 0
    else:
        print("\n⚠️ CONCLUSION: Fix issues before proceeding to Phase 3")
        return 1

if __name__ == "__main__":
    print(f"🚀 Starting Parallel Tests at {datetime.now()}")
    exit_code = asyncio.run(main())
    exit(exit_code)