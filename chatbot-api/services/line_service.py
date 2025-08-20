"""
LINE service - LINE Messaging API operations
Independent functions for LINE messaging
"""
import hashlib
import hmac
import base64
from typing import List, Dict
import httpx
from modules.config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET

async def send_line_message(reply_token: str, messages: List[Dict]):
    """Send reply message to LINE with enhanced error handling"""
    try:
        if not LINE_CHANNEL_ACCESS_TOKEN:
            print("❌ LINE_CHANNEL_ACCESS_TOKEN not set")
            return False
        
        headers = {
            "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "replyToken": reply_token,
            "messages": messages
        }
        
        print(f"📤 Sending LINE message: {len(messages)} message(s)")
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                "https://api.line.me/v2/bot/message/reply",
                headers=headers,
                json=payload
            )
            
        if response.status_code == 200:
            print("✅ LINE message sent successfully")
            return True
        else:
            print(f"❌ LINE reply error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except httpx.TimeoutException:
        print("❌ LINE API timeout")
        return False
    except Exception as e:
        print(f"❌ Error sending LINE message: {e}")
        return False

async def send_line_push_message(user_id: str, messages: List[Dict]):
    """Send push message to specific LINE user (for order confirmation)"""
    try:
        if not LINE_CHANNEL_ACCESS_TOKEN:
            print("❌ LINE_CHANNEL_ACCESS_TOKEN not set")
            return False
        
        # Remove LINE_ prefix if present
        clean_user_id = user_id.replace("LINE_", "") if user_id.startswith("LINE_") else user_id
        
        headers = {
            "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "to": clean_user_id,
            "messages": messages
        }
        
        print(f"📤 Sending LINE push to {clean_user_id}: {len(messages)} message(s)")
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                "https://api.line.me/v2/bot/message/push",
                headers=headers,
                json=payload
            )
            
        if response.status_code == 200:
            print("✅ LINE push message sent successfully")
            return True
        else:
            print(f"❌ LINE push error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except httpx.TimeoutException:
        print("❌ LINE push API timeout")
        return False
    except Exception as e:
        print(f"❌ Error sending LINE push: {e}")
        return False

def verify_line_signature(body: bytes, signature: str) -> bool:
    """Verify LINE webhook signature"""
    if not LINE_CHANNEL_SECRET:
        return False
        
    hash = hmac.new(
        LINE_CHANNEL_SECRET.encode('utf-8'),
        body,
        hashlib.sha256
    ).digest()
    
    expected_signature = base64.b64encode(hash).decode('utf-8')
    return hmac.compare_digest(signature, expected_signature)