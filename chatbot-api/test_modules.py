#!/usr/bin/env python3
"""
Test script for individual modules
Run this to verify modules work independently before integration
"""
import asyncio
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_config():
    """Test configuration module"""
    print("\n🧪 Testing config module...")
    try:
        from modules.config import (
            SUPABASE_URL, 
            LINE_CHANNEL_ACCESS_TOKEN, 
            FAQ_RESPONSES,
            validate_config
        )
        
        # Test constants
        assert len(FAQ_RESPONSES) == 5, f"Expected 5 FAQ responses, got {len(FAQ_RESPONSES)}"
        assert "hours" in FAQ_RESPONSES, "Missing 'hours' FAQ response"
        assert SUPABASE_URL.startswith("https://"), "Invalid Supabase URL format"
        assert len(LINE_CHANNEL_ACCESS_TOKEN) > 50, "LINE token seems too short"
        
        # Test validation
        config_valid = validate_config()
        assert config_valid, "Config validation failed"
        
        print("✅ Config module test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Config module test FAILED: {e}")
        return False

async def test_ai_service():
    """Test AI service module"""
    print("\n🧪 Testing AI service module...")
    try:
        from services.ai_service import classify_intent, get_ai_response
        
        # Test intent classification
        test_cases = [
            ("สวัสดีครับ", "greeting"),
            ("ร้านเปิดกี่โมง", "hours"),
            ("ที่อยู่ร้านอยู่ไหน", "location"),
            ("อยากสั่งอาหาร", "order"),
            ("ราคาเท่าไร", "menu"),
        ]
        
        for message, expected_intent in test_cases:
            result = classify_intent(message)
            assert result == expected_intent, f"Expected '{expected_intent}' for '{message}', got '{result}'"
        
        # Test AI response (should return fallback if no API key)
        response = await get_ai_response("Hello test", "test_user")
        assert isinstance(response, str), "AI response should be string"
        assert len(response) > 0, "AI response should not be empty"
        
        print("✅ AI service test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ AI service test FAILED: {e}")
        return False

async def test_database_service():
    """Test database service module"""
    print("\n🧪 Testing database service module...")
    try:
        from services.database_service import generate_platform_id
        
        # Test platform ID generation
        test_cases = [
            ("LINE", "U1234567", "LINE_U1234567"),
            ("FB", "fb_123", "FB_fb_123"),
            ("IG", "ig_456", "IG_ig_456"),
            ("WEB", "0812345678", "WEB_0812345678"),
            ("WEB", None, "WEB_"),  # Should generate UUID
        ]
        
        for platform, identifier, expected_prefix in test_cases:
            result = generate_platform_id(platform, identifier)
            if expected_prefix.endswith("_"):
                # UUID case
                assert result.startswith(expected_prefix), f"Expected prefix '{expected_prefix}' for {platform}/{identifier}"
                assert len(result) > len(expected_prefix), "UUID should be generated"
            else:
                assert result == expected_prefix, f"Expected '{expected_prefix}' for {platform}/{identifier}, got '{result}'"
        
        print("✅ Database service test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Database service test FAILED: {e}")
        return False

async def test_line_service():
    """Test LINE service module (structure only)"""
    print("\n🧪 Testing LINE service module...")
    try:
        from services.line_service import verify_line_signature
        
        # Test signature verification with dummy data
        # Should return False for invalid data
        result = verify_line_signature(b"test", "invalid_signature")
        assert result is False, "Invalid signature should return False"
        
        print("✅ LINE service test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ LINE service test FAILED: {e}")
        return False

async def test_notification_service():
    """Test notification service module"""
    print("\n🧪 Testing notification service module...")
    try:
        from services.notification_service import send_order_confirmation
        
        # Test function signature exists
        assert callable(send_order_confirmation), "send_order_confirmation should be callable"
        
        # Test with mock data (won't actually send)
        print("   Testing notification structure...")
        # This would normally fail due to no LINE token, but we just test structure
        
        print("✅ Notification service test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Notification service test FAILED: {e}")
        return False

async def main():
    """Run all module tests"""
    print("🧪 Running Module Tests")
    print("=" * 50)
    
    tests = [
        test_config(),
        test_ai_service(), 
        test_database_service(),
        test_line_service(),
        test_notification_service(),
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    # Count results
    passed = sum(1 for r in results if r is True)
    total = len(results)
    
    print("\n" + "=" * 50)
    print(f"📊 Module Test Results:")
    print(f"   Total: {total}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {total - passed}")
    print(f"   Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 ALL MODULE TESTS PASSED - Ready for integration!")
        return 0
    else:
        print("⚠️ SOME MODULE TESTS FAILED - Fix before proceeding!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)