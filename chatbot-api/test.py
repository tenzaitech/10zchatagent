#!/usr/bin/env python3
"""
Test script for Tenzai Chatbot API
"""

import json
import httpx
import asyncio

BASE_URL = "http://localhost:8000"

async def test_health():
    """Test health endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/")
        print(f"Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        print()

async def test_order_creation():
    """Test order creation"""
    order_data = {
        "cart": [
            {"menu_id": 1, "qty": 2, "note": "ไม่เผ็ด"},
            {"menu_id": 2, "qty": 1}
        ],
        "contact": {
            "name": "ทดสอบ ระบบ",
            "phone": "081-234-5678"
        },
        "user_ref": {
            "line_user_id": "U123456789abcdef"
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/orders/create",
            json=order_data
        )
        print(f"Order creation: {response.status_code}")
        print(f"Response: {response.json()}")
        print()

async def test_line_webhook():
    """Test LINE webhook (mock)"""
    webhook_data = {
        "events": [
            {
                "type": "message",
                "message": {
                    "type": "text",
                    "text": "เปิดกี่โมง"
                },
                "replyToken": "mock_reply_token",
                "source": {
                    "userId": "U123456789abcdef"
                }
            }
        ]
    }
    
    headers = {
        "X-Line-Signature": "mock_signature"  # This will fail verification
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/webhook/line",
                json=webhook_data,
                headers=headers
            )
            print(f"LINE webhook: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"LINE webhook test failed (expected): {e}")
        print()

async def main():
    print("Testing Tenzai Chatbot API...")
    print("="*40)
    
    await test_health()
    await test_order_creation()
    await test_line_webhook()
    
    print("Tests completed!")

if __name__ == "__main__":
    asyncio.run(main())