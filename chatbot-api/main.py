#!/usr/bin/env python3
"""
Tenzai Chatbot API
Replaces n8n with lightweight Python FastAPI server
"""

import os
import json
import hashlib
import hmac
import base64
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import httpx
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

# Load .env file
load_dotenv()
print("🔧 Loading .env file...")

app = FastAPI(title="Tenzai Chatbot API", version="1.0.0")

# CORS for web app (including ngrok domains)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://tenzai-order.ngrok.io",
        "https://*.ngrok.io",  # Allow any ngrok subdomain
        "*"  # Fallback for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qlhpmrehrmprptldtchb.supabase.co")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# Validate required environment variables
required_vars = {
    "SUPABASE_URL": SUPABASE_URL,
    "SUPABASE_SERVICE_ROLE_KEY": SUPABASE_SERVICE_KEY,
    "LINE_CHANNEL_ACCESS_TOKEN": LINE_CHANNEL_ACCESS_TOKEN,
    "LINE_CHANNEL_SECRET": LINE_CHANNEL_SECRET,
}

# Debug environment loading
print(f"🔍 Debug environment variables:")
print(f"   SUPABASE_URL: {SUPABASE_URL}")
print(f"   SUPABASE_SERVICE_ROLE_KEY: {'SET' if SUPABASE_SERVICE_KEY else 'NOT_SET'} ({len(SUPABASE_SERVICE_KEY)} chars)")
print(f"   LINE_CHANNEL_ACCESS_TOKEN: {'SET' if LINE_CHANNEL_ACCESS_TOKEN else 'NOT_SET'} ({len(LINE_CHANNEL_ACCESS_TOKEN)} chars)")
print(f"   LINE_CHANNEL_SECRET: {'SET' if LINE_CHANNEL_SECRET else 'NOT_SET'} ({len(LINE_CHANNEL_SECRET)} chars)")
print(f"   OPENROUTER_API_KEY: {'SET' if OPENROUTER_API_KEY else 'NOT_SET'} ({len(OPENROUTER_API_KEY)} chars)")

missing_vars = [key for key, value in required_vars.items() if not value]
if missing_vars:
    print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
    print("🔧 Make sure .env file exists in the same directory as main.py")
    print("💡 Also check that python-dotenv is installed: pip install python-dotenv")
    exit(1)
else:
    print("✅ All required environment variables loaded")
    if OPENROUTER_API_KEY:
        print("✅ OpenRouter API key loaded")
    else:
        print("⚠️ OpenRouter API key not set (AI features disabled)")

# FAQ Responses
FAQ_RESPONSES = {
    "hours": "🕙 เปิดให้บริการทุกวัน 10:00-21:00 น.\n📋 รับออเดอร์ล่าสุด 20:30 น.",
    "location": "📍 123 ถนนสุขุมวิท แขวงคลองตัน เขตวัฒนา กรุงเทพฯ 10110\n📞 02-xxx-xxxx",
    "menu": "🍜 ดูเมนูและราคาทั้งหมดได้ที่หน้าสั่งอาหาร\nหรือกดปุ่ม 'สั่งอาหาร' ด้านล่าง",
    "payment": "💳 รับชำระ: เงินสด/โอนเงิน/พร้อมเพย์\n📷 ส่งสลิปในแชทหลังสั่งเสร็จนะคะ",
    "order": "🛒 สั่งอาหารออนไลน์ได้ที่ลิงก์ด้านล่าง\nหรือกดปุ่ม 'สั่งอาหาร' เลยค่ะ"
}

FALLBACK_MESSAGE = "ขออภัยค่ะ ไม่เข้าใจคำถาม 🤔\nลองถามใหม่หรือกด 'สั่งอาหาร' เลยนะคะ 😊"

async def get_ai_response(message: str, user_id: str = "") -> str:
    """Get AI response from OpenRouter for complex queries"""
    try:
        if not OPENROUTER_API_KEY:
            print("⚠️ OpenRouter API key not available, using fallback")
            return FALLBACK_MESSAGE
            
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://order.tenzaitech.online",
            "X-Title": "Tenzai Sushi Chatbot"
        }
        
        # System prompt สำหรับร้านอาหาร
        system_prompt = """คุณคือผู้ช่วยร้านอาหารญี่ปุ่น Tenzai Sushi 
- ตอบสั้นๆ กะทัดรัด ไม่เกิน 2-3 ประโยค
- พูดแบบเป็นมิตร ใช้ "ค่ะ/ครับ"
- ถ้าเกี่ยวกับเมนูหรือการสั่งอาหาร ให้แนะนำให้กด "สั่งอาหาร"
- ถ้าไม่เข้าใจคำถาม ให้ตอบว่า "ขออภัยค่ะ ไม่เข้าใจคำถาม ลองถามใหม่นะคะ"
- เวลาเปิด: 10:00-21:00 น. รับออเดอร์ล่าสุด 20:30 น.
- ที่อยู่: 123 ถนนสุขุมวิท แขวงคลองตัน เขตวัฒนา กรุงเทพฯ"""

        payload = {
            "model": "mistralai/mistral-7b-instruct:free",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            "max_tokens": 100,
            "temperature": 0.7
        }
        
        print(f"🤖 Asking AI: {message[:50]}...")
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
        if response.status_code == 200:
            data = response.json()
            ai_response = data["choices"][0]["message"]["content"].strip()
            print(f"✅ AI response: {ai_response[:50]}...")
            return ai_response
        else:
            print(f"❌ OpenRouter error: {response.status_code}")
            print(f"   Response: {response.text}")
            return FALLBACK_MESSAGE
            
    except httpx.TimeoutException:
        print("❌ AI request timeout")
        return FALLBACK_MESSAGE
    except Exception as e:
        print(f"❌ AI error: {e}")
        return FALLBACK_MESSAGE

async def supabase_request(method: str, endpoint: str, data: Dict = None, use_service_key: bool = True) -> Dict:
    """Make request to Supabase REST API with enhanced error handling"""
    try:
        headers = {
            "apikey": SUPABASE_SERVICE_KEY if use_service_key else SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY if use_service_key else SUPABASE_ANON_KEY}",
            "Content-Type": "application/json"
        }
        
        url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
        print(f"📡 {method} {endpoint} (service_key: {use_service_key})")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            if method == "GET":
                response = await client.get(url, headers=headers)
            elif method == "POST":
                response = await client.post(url, headers=headers, json=data)
            elif method == "PATCH":
                response = await client.patch(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
        
        if response.status_code not in [200, 201, 204]:
            print(f"❌ Supabase error: {response.status_code}")
            print(f"   URL: {url}")
            print(f"   Headers: {headers}")
            print(f"   Data sent: {data}")
            print(f"   Response: {response.text}")
            raise HTTPException(status_code=500, detail=f"Database error: {response.status_code} - {response.text}")
        
        result = response.json() if response.text else {}
        print(f"✅ Supabase response: {len(str(result))} chars")
        return result
        
    except httpx.TimeoutException:
        print("❌ Supabase timeout")
        raise HTTPException(status_code=504, detail="Database timeout")
    except httpx.RequestError as e:
        print(f"❌ Supabase connection error: {e}")
        raise HTTPException(status_code=503, detail="Database connection failed")
    except Exception as e:
        print(f"❌ Unexpected error in supabase_request: {e}")
        raise HTTPException(status_code=500, detail="Database error")

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

async def send_order_confirmation(order_number: str, customer_phone: str, customer_name: str, 
                                platform: str, platform_user_id: str, total_amount: float, items_count: int):
    """Send order confirmation to customer via appropriate platform"""
    try:
        print(f"🔔 Sending order confirmation: {order_number} to {platform}_{platform_user_id}")
        
        # Create confirmation message
        confirmation_text = f"""🎉 ยืนยันการสั่งอาหาร
        
📋 ออเดอร์: #{order_number}
👤 ชื่อ: {customer_name}
📞 เบอร์: {customer_phone}
💰 ยอดรวม: {total_amount:,.0f} บาท
📦 จำนวนรายการ: {items_count}

✨ ขอบคุณที่ใช้บริการ Tenzai Sushi
ทางร้านจะติดต่อกลับเร็วๆ นี้ค่ะ"""

        if platform == "LINE" and platform_user_id:
            # Send LINE push message with Flex Message
            flex_message = {
                "type": "flex",
                "altText": f"ยืนยันออเดอร์ #{order_number}",
                "contents": {
                    "type": "bubble",
                    "header": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "🎉 ยืนยันการสั่งอาหาร",
                                "weight": "bold",
                                "color": "#FF6B35",
                                "size": "lg"
                            }
                        ],
                        "backgroundColor": "#FFF8F3"
                    },
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "contents": [
                                    {"type": "text", "text": "ออเดอร์:", "size": "sm", "color": "#666666", "flex": 2},
                                    {"type": "text", "text": f"#{order_number}", "size": "sm", "wrap": True, "flex": 5, "weight": "bold"}
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "contents": [
                                    {"type": "text", "text": "ชื่อ:", "size": "sm", "color": "#666666", "flex": 2},
                                    {"type": "text", "text": customer_name, "size": "sm", "wrap": True, "flex": 5}
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "contents": [
                                    {"type": "text", "text": "เบอร์:", "size": "sm", "color": "#666666", "flex": 2},
                                    {"type": "text", "text": customer_phone, "size": "sm", "flex": 5}
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "contents": [
                                    {"type": "text", "text": "ยอดรวม:", "size": "sm", "color": "#666666", "flex": 2},
                                    {"type": "text", "text": f"{total_amount:,.0f} บาท", "size": "sm", "flex": 5, "weight": "bold", "color": "#FF6B35"}
                                ]
                            },
                            {"type": "separator", "margin": "lg"},
                            {
                                "type": "text",
                                "text": "✨ ขอบคุณที่ใช้บริการ Tenzai Sushi\nทางร้านจะติดต่อกลับเร็วๆ นี้ค่ะ",
                                "size": "sm",
                                "color": "#666666",
                                "wrap": True,
                                "margin": "lg"
                            }
                        ]
                    }
                }
            }
            
            # Add order tracking button
            tracking_button = {
                "type": "template",
                "altText": "ติดตามออเดอร์",
                "template": {
                    "type": "buttons",
                    "text": "ติดตามสถานะออเดอร์ของคุณ",
                    "actions": [
                        {
                            "type": "uri",
                            "label": "📋 ติดตามออเดอร์",
                            "uri": f"https://tenzai-order.ap.ngrok.io/order-status.html?order={order_number}"
                        }
                    ]
                }
            }
            
            messages = [{"type": "text", "text": "🎉 สั่งอาหารเรียบร้อยแล้วค่ะ!"}, flex_message, tracking_button]
            success = await send_line_push_message(platform_user_id, messages)
            
            if success:
                print(f"✅ LINE confirmation sent to {platform_user_id}")
            else:
                print(f"⚠️ Failed to send LINE confirmation to {platform_user_id}")
                
        # TODO: Add Facebook/Instagram push notifications
        elif platform == "FB":
            print(f"📧 Facebook confirmation for {platform_user_id} (not implemented)")
        elif platform == "IG":
            print(f"📧 Instagram confirmation for {platform_user_id} (not implemented)")
        else:
            print(f"📧 Web order confirmation for {customer_phone} (EMAIL/SMS not implemented)")
            
    except Exception as e:
        print(f"❌ Error sending order confirmation: {e}")

def classify_intent(message_text: str) -> str:
    """Smart intent classification - FAQ vs AI vs Order"""
    text = message_text.lower()
    
    # FAQ patterns (high confidence)
    if any(word in text for word in ["เวลา", "เปิด", "ปิด", "โมง", "hours", "กี่โมง"]):
        return "hours"
    elif any(word in text for word in ["ที่อยู่", "แอดเดรส", "location", "address", "อยู่ไหน", "ที่ไหน"]):
        return "location"
    elif any(word in text for word in ["ราคา", "เท่าไร", "price", "cost", "กี่บาท"]):
        return "menu"
    elif any(word in text for word in ["ชำระ", "จ่าย", "payment", "pay", "โอน", "เงิน"]):
        return "payment"
    elif any(word in text for word in ["สั่ง", "order", "โอเดอร์", "สั่งอาหาร"]):
        return "order"
    
    # Check for restaurant/food context
    restaurant_keywords = ["เมนู", "อาหาร", "food", "menu", "sushi", "ซูชิ", "ข้าว", "น้ำ", "ของหวาน", "ทานเข้า", "กิน"]
    if any(word in text for word in restaurant_keywords):
        return "menu"
    
    # Simple greeting
    if any(word in text for word in ["สวัสดี", "hello", "hi", "ครับ", "ค่ะ", "หวัดดี"]):
        return "greeting"
    
    # Complex questions for AI
    if len(text) > 15 and any(char in text for char in ["?", "ไหม", "มั้ย", "ได้ไหม", "อย่างไร", "ทำไม"]):
        return "ai_complex"
    
    # Default to AI for everything else
    return "ai_fallback"

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

@app.get("/")
async def health_check():
    return {"status": "ok", "service": "Tenzai Chatbot API", "timestamp": datetime.now().isoformat()}

@app.get("/api/schema/inspect")
async def inspect_database_schema():
    """Get all table schemas from Supabase"""
    try:
        schemas = {}
        
        # Get list of tables first
        tables_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
        """
        
        tables_result = await supabase_request("POST", "rpc/exec", {"sql": tables_query})
        print(f"📋 Found tables: {tables_result}")
        
        # For each table, get column info
        for table_info in tables_result:
            table_name = table_info['table_name']
            
            columns_query = f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """
            
            try:
                columns_result = await supabase_request("POST", "rpc/exec", {"sql": columns_query})
                schemas[table_name] = columns_result
            except Exception as e:
                print(f"❌ Error getting columns for {table_name}: {e}")
                schemas[table_name] = {"error": str(e)}
        
        return {
            "status": "success",
            "schemas": schemas,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Schema inspection error: {e}")
        return {
            "status": "error", 
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/schema/sample-data")
async def get_sample_data():
    """Get sample data from all tables to see structure"""
    try:
        samples = {}
        tables = ['customers', 'orders', 'order_items', 'menus', 'categories', 'conversations']
        
        for table in tables:
            try:
                print(f"📊 Getting sample from {table}...")
                # Get first row to see structure
                data = await supabase_request("GET", f"{table}?limit=1", use_service_key=False)
                samples[table] = {
                    'sample_row': data[0] if data else None,
                    'columns': list(data[0].keys()) if data else [],
                    'row_count': len(data)
                }
            except Exception as e:
                print(f"❌ Error accessing {table}: {e}")
                samples[table] = {
                    'error': str(e),
                    'accessible': False
                }
        
        return {
            "status": "success",
            "samples": samples,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Sample data error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/webhook/line")
async def line_webhook(request: Request):
    """Handle LINE webhook events with comprehensive error handling"""
    try:
        print("🔔 Received LINE webhook")
        
        # Get signature
        signature = request.headers.get('X-Line-Signature', '')
        if not signature:
            print("❌ Missing X-Line-Signature header")
            raise HTTPException(status_code=400, detail="Missing signature")
            
        body = await request.body()
        if not body:
            print("❌ Empty request body")
            raise HTTPException(status_code=400, detail="Empty body")
        
        # Verify signature
        print(f"🔐 Verifying signature: {signature[:20]}...")
        if not verify_line_signature(body, signature):
            print(f"❌ Signature verification failed!")
            print(f"   Expected format: base64 encoded HMAC-SHA256")
            print(f"   Channel Secret: {LINE_CHANNEL_SECRET[:10] if LINE_CHANNEL_SECRET else 'NOT_SET'}...")
            print(f"   Body length: {len(body)} bytes")
            raise HTTPException(status_code=401, detail="Invalid signature")
        print("✅ Signature verification passed")
        
        # Parse body
        try:
            webhook_data = json.loads(body.decode('utf-8'))
            events = webhook_data.get('events', [])
            print(f"📨 Parsed {len(events)} event(s)")
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON")
        
        for event in events:
            if event['type'] == 'message' and event['message']['type'] == 'text':
                message_text = event['message']['text']
                reply_token = event['replyToken']
                user_id = event['source']['userId']
                
                print(f"👤 Message from {user_id}: {message_text}")
                
                # Classify intent and get response
                intent = classify_intent(message_text)
                print(f"🎯 Intent classified as: {intent}")
                
                response_text = ""
                messages = []
                
                if intent in FAQ_RESPONSES:
                    # FAQ Response (instant)
                    response_text = FAQ_RESPONSES[intent]
                    messages = [{"type": "text", "text": response_text}]
                    
                    # Add order button for relevant intents with deep linking
                    if intent in ["order", "menu"]:
                        # Create deep link with LINE user ID for pre-fill customer data
                        deep_link = f"https://tenzai-order.ap.ngrok.io/customer_webapp.html?platform=LINE&user_id={user_id}"
                        messages.append({
                            "type": "template",
                            "altText": "สั่งอาหาร",
                            "template": {
                                "type": "buttons",
                                "text": "คลิกสั่งอาหารได้เลย!",
                                "actions": [
                                    {
                                        "type": "uri",
                                        "label": "🍜 สั่งอาหาร",
                                        "uri": deep_link
                                    }
                                ]
                            }
                        })
                
                elif intent == "greeting":
                    # Simple greeting with deep linking
                    response_text = "สวัสดีค่ะ! ยินดีต้อนรับสู่ Tenzai Sushi 🍣\nมีอะไรให้ช่วยไหมคะ?"
                    deep_link = f"https://tenzai-order.ap.ngrok.io/customer_webapp.html?platform=LINE&user_id={user_id}"
                    messages = [
                        {"type": "text", "text": response_text},
                        {
                            "type": "template",
                            "altText": "สั่งอาหาร",
                            "template": {
                                "type": "buttons",
                                "text": "สั่งอาหารได้เลยค่ะ!",
                                "actions": [
                                    {
                                        "type": "uri",
                                        "label": "🍜 สั่งอาหาร",
                                        "uri": deep_link
                                    }
                                ]
                            }
                        }
                    ]
                
                elif intent in ["ai_complex", "ai_fallback"]:
                    # AI Response for complex queries with deep linking
                    response_text = await get_ai_response(message_text, user_id)
                    messages = [{"type": "text", "text": response_text}]
                    deep_link = f"https://tenzai-order.ap.ngrok.io/customer_webapp.html?platform=LINE&user_id={user_id}"
                    
                    # Always add order button for AI responses
                    messages.append({
                        "type": "template",
                        "altText": "สั่งอาหาร",
                        "template": {
                            "type": "buttons",
                            "text": "หรือสั่งอาหารได้เลยค่ะ!",
                            "actions": [
                                {
                                    "type": "uri",
                                    "label": "🍜 สั่งอาหาร",
                                    "uri": deep_link
                                }
                            ]
                        }
                    })
                
                else:
                    # Fallback for anything else with deep linking
                    response_text = FALLBACK_MESSAGE
                    deep_link = f"https://tenzai-order.ap.ngrok.io/customer_webapp.html?platform=LINE&user_id={user_id}"
                    messages = [
                        {"type": "text", "text": response_text},
                        {
                            "type": "template",
                            "altText": "สั่งอาหาร",
                            "template": {
                                "type": "buttons", 
                                "text": "หรือคลิกสั่งอาหารได้เลย!",
                                "actions": [
                                    {
                                        "type": "uri",
                                        "label": "🍜 สั่งอาหาร", 
                                        "uri": deep_link
                                    }
                                ]
                            }
                        }
                    ]
                
                # Send reply
                await send_line_message(reply_token, messages)
                
                # Log conversation with improved platform tracking
                try:
                    platform_id = generate_platform_id("LINE", user_id)
                    conversation_data = {
                        "line_user_id": platform_id,  # Use proper platform ID
                        "message_text": message_text[:300],  # Limit length
                        "response_text": response_text[:300] if intent in FAQ_RESPONSES else "สั่งอาหาร", 
                        "created_at": datetime.now().isoformat()
                    }
                    await supabase_request("POST", "conversations", conversation_data)
                    print(f"📝 Logged conversation for {platform_id}")
                except Exception as e:
                    print(f"⚠️ Conversation logging error: {e}")
        
        return {"status": "ok"}
        
    except Exception as e:
        print(f"LINE webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def generate_platform_id(platform: str, identifier: str = None) -> str:
    """Generate platform-specific customer ID"""
    if platform == "LINE" and identifier:
        return f"LINE_{identifier}"
    elif platform == "FB" and identifier:
        return f"FB_{identifier}"
    elif platform == "IG" and identifier:
        return f"IG_{identifier}"
    elif platform == "WEB":
        # For web orders, use phone number as unique identifier
        if identifier:
            return f"WEB_{identifier}"
        else:
            return f"WEB_{str(uuid.uuid4())[:8]}"
    else:
        return f"UNKNOWN_{str(uuid.uuid4())[:8]}"

async def find_or_create_customer(name: str, phone: str, platform: str = "WEB", platform_user_id: str = None) -> str:
    """Smart customer management - find existing or create new with proper platform ID"""
    try:
        print(f"🔍 Processing customer: name={name}, phone={phone}, platform={platform}")
        
        # Step 1: Try to find existing customer by phone (universal key)
        existing_query = f"customers?phone=eq.{phone}&select=id,line_user_id&limit=1"
        existing_customers = await supabase_request("GET", existing_query, use_service_key=False)
        
        if existing_customers and len(existing_customers) > 0:
            customer_id = existing_customers[0]["id"]
            current_platform_id = existing_customers[0]["line_user_id"]
            
            # Update platform ID if it's generic web ID and we have better info
            if current_platform_id.startswith("WEB_") and len(current_platform_id) < 15 and platform != "WEB":
                new_platform_id = generate_platform_id(platform, platform_user_id)
                update_data = {"line_user_id": new_platform_id}
                await supabase_request("PATCH", f"customers?id=eq.{customer_id}", update_data)
                print(f"✅ Updated customer {customer_id} platform ID: {current_platform_id} → {new_platform_id}")
            else:
                print(f"✅ Found existing customer: {customer_id} ({current_platform_id})")
            return customer_id
        
        # Step 2: Create new customer with proper platform ID
        platform_id = generate_platform_id(platform, platform_user_id or phone)
        customer_data = {
            "display_name": name,
            "phone": phone,
            "line_user_id": platform_id  # This will be renamed to platform_id in future
        }
        
        print(f"📝 Creating new customer: {customer_data}")
        customer_result = await supabase_request("POST", "customers", customer_data)
        
        # Handle Supabase response patterns
        if not customer_result or len(customer_result) == 0:
            print("🔄 Customer created but no ID returned, fetching...")
            fetch_query = f"customers?line_user_id=eq.{platform_id}&select=id&limit=1"
            fetch_result = await supabase_request("GET", fetch_query, use_service_key=False)
            if fetch_result and len(fetch_result) > 0:
                customer_id = fetch_result[0]["id"]
                print(f"✅ Fetched new customer ID: {customer_id}")
                return customer_id
        else:
            customer_id = customer_result[0]["id"]
            print(f"✅ Customer created with ID: {customer_id}")
            return customer_id
            
        raise Exception("Failed to create or retrieve customer")
        
    except Exception as e:
        print(f"❌ Customer operation error: {e}")
        raise HTTPException(status_code=500, detail=f"Customer operation failed: {str(e)}")

@app.post("/api/orders/create")
async def create_order(request: Request):
    """Handle order creation from web app with improved customer management"""
    try:
        order_data = await request.json()
        print(f"📦 Received order: {order_data}")
        
        # Validate input
        required_fields = ["cart", "contact"]
        for field in required_fields:
            if field not in order_data:
                raise HTTPException(status_code=400, detail=f"Missing field: {field}")
        
        cart = order_data["cart"]
        contact = order_data["contact"]
        
        if not cart:
            raise HTTPException(status_code=400, detail="Empty cart")
        
        if not contact.get("name") or not contact.get("phone"):
            raise HTTPException(status_code=400, detail="Missing customer name or phone")
        
        # Get menu items for re-pricing
        menu_ids = [str(item["menu_id"]) for item in cart]
        menu_query = f"menus?id=in.({','.join(menu_ids)})&select=id,name,price,is_available"
        menus = await supabase_request("GET", menu_query, use_service_key=False)
        
        # Create menu lookup
        menu_lookup = {menu["id"]: menu for menu in menus}
        
        # Validate and calculate total
        total_amount = 0
        validated_items = []
        
        for item in cart:
            menu_id = item["menu_id"]
            quantity = item.get("qty", 1)
            
            if menu_id not in menu_lookup:
                raise HTTPException(status_code=400, detail=f"Menu item {menu_id} not found")
            
            menu = menu_lookup[menu_id]
            if not menu.get("is_available", False):
                raise HTTPException(status_code=400, detail=f"Menu item '{menu['name']}' not available")
            
            if quantity < 1:
                raise HTTPException(status_code=400, detail="Invalid quantity")
            
            unit_price = menu["price"]
            item_total = unit_price * quantity
            total_amount += item_total
            
            validated_items.append({
                "menu_id": menu_id,
                "menu_name": menu["name"],
                "quantity": quantity,
                "unit_price": unit_price,
                "total_price": item_total,
                "notes": item.get("note", "")
            })
        
        # Smart customer management with platform detection
        platform = order_data.get("platform", "WEB")
        platform_user_id = order_data.get("platform_user_id")
        customer_id = await find_or_create_customer(
            contact["name"], 
            contact["phone"], 
            platform, 
            platform_user_id
        )
        
        if not customer_id:
            raise HTTPException(status_code=500, detail="Failed to get customer ID")
        
        # Generate simple order number
        order_number = f"T{datetime.now().strftime('%y%m%d%H%M%S')}"
        
        # Create order with minimal data
        order_data_db = {
            "order_number": order_number,
            "customer_id": customer_id,
            "customer_name": contact["name"],
            "customer_phone": contact["phone"],
            "status": "pending",
            "order_type": "pickup",
            "total_amount": total_amount,
            "payment_method": "qr_code",
            "payment_status": "unpaid",
        }
        
        print(f"📝 Creating order: {order_data_db}")
        order_result = await supabase_request("POST", "orders", order_data_db)
        
        # Handle order ID the same way as customer
        order_id = None
        if not order_result or len(order_result) == 0:
            print("🔄 Order created but no ID returned, fetching...")
            fetch_query = f"orders?order_number=eq.{order_number}&select=id&limit=1"
            fetch_result = await supabase_request("GET", fetch_query, use_service_key=False)
            if fetch_result and len(fetch_result) > 0:
                order_id = fetch_result[0]["id"]
                print(f"✅ Fetched order ID: {order_id}")
        else:
            order_id = order_result[0]["id"]
            print(f"✅ Order created with ID: {order_id}")
            
        if not order_id:
            raise HTTPException(status_code=500, detail="Failed to get order ID")
        
        # Create order items
        try:
            for item in validated_items:
                item["order_id"] = order_id
            
            if validated_items:
                print(f"📝 Creating {len(validated_items)} order items")
                await supabase_request("POST", "order_items", validated_items)
                print(f"✅ Created {len(validated_items)} order items")
            else:
                raise HTTPException(status_code=400, detail="No valid items to create")
        except Exception as e:
            print(f"❌ Order items creation failed: {e}")
            raise HTTPException(status_code=500, detail=f"Order items creation failed: {str(e)}")
        
        # Send order confirmation to customer
        try:
            await send_order_confirmation(
                order_number=order_number,
                customer_phone=contact["phone"],
                customer_name=contact["name"],
                platform=platform,
                platform_user_id=platform_user_id,
                total_amount=total_amount,
                items_count=len(validated_items)
            )
        except Exception as e:
            print(f"⚠️ Failed to send order confirmation: {e}")
            # Don't fail the order creation if confirmation fails
        
        # TODO: Send staff notification (LINE push message to staff)
        # This would require staff LINE user IDs in system_settings
        
        return {
            "success": True,
            "order_id": order_number,
            "total_price": total_amount,
            "items_count": len(validated_items),
            "message": f"ออเดอร์ {order_number} สำเร็จ! ยอดรวม {total_amount:,.0f} บาท"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Order creation error: {e}")
        raise HTTPException(status_code=500, detail="Order creation failed")

@app.get("/api/orders/{order_number}")
async def get_order_status(order_number: str):
    """Get order status for tracking page"""
    try:
        print(f"🔍 Getting status for order: {order_number}")
        
        # Query order with customer and items
        order_query = f"orders?order_number=eq.{order_number}&select=*,order_items(*,menus(name,price))&limit=1"
        orders = await supabase_request("GET", order_query, use_service_key=False)
        
        if not orders:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order = orders[0]
        
        # Calculate totals
        items_total = sum(item.get('total_price', 0) for item in order.get('order_items', []))
        
        return {
            "order_number": order["order_number"],
            "status": order["status"],
            "customer_name": order["customer_name"],
            "customer_phone": order["customer_phone"],
            "total_amount": order["total_amount"],
            "payment_status": order.get("payment_status", "unpaid"),
            "order_type": order.get("order_type", "pickup"),
            "created_at": order["created_at"],
            "items": [
                {
                    "name": item.get("menu_name", item.get("menus", {}).get("name", "Unknown")),
                    "quantity": item["quantity"],
                    "unit_price": item["unit_price"],
                    "total_price": item["total_price"],
                    "notes": item.get("notes", "")
                }
                for item in order.get("order_items", [])
            ],
            "status_history": [
                {"status": "pending", "text": "รอการยืนยัน", "completed": True},
                {"status": "confirmed", "text": "ยืนยันแล้ว", "completed": order["status"] in ["confirmed", "preparing", "ready", "completed"]},
                {"status": "preparing", "text": "กำลังเตรียม", "completed": order["status"] in ["preparing", "ready", "completed"]},
                {"status": "ready", "text": "พร้อมรับ", "completed": order["status"] in ["ready", "completed"]},
                {"status": "completed", "text": "เสร็จสิ้น", "completed": order["status"] == "completed"}
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting order status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get order status")

@app.post("/webhook/fb")
async def facebook_webhook(request: Request):
    """Handle Facebook webhook (placeholder)"""
    # TODO: Implement Facebook Messenger webhook
    return {"status": "fb webhook not implemented yet"}

@app.post("/webhook/ig") 
async def instagram_webhook(request: Request):
    """Handle Instagram webhook (placeholder)"""
    # TODO: Implement Instagram webhook
    return {"status": "ig webhook not implemented yet"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)