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
from datetime import datetime
from typing import Dict, List, Optional, Any
import httpx
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Tenzai Chatbot API", version="1.0.0")

# CORS for web app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

# FAQ Responses
FAQ_RESPONSES = {
    "hours": "🕙 เปิดให้บริการทุกวัน 10:00-21:00 น.\n📋 รับออเดอร์ล่าสุด 20:30 น.",
    "location": "📍 123 ถนนสุขุมวิท แขวงคลองตัน เขตวัฒนา กรุงเทพฯ 10110\n📞 02-xxx-xxxx",
    "menu": "🍜 ดูเมนูและราคาทั้งหมดได้ที่หน้าสั่งอาหาร\nหรือกดปุ่ม 'สั่งอาหาร' ด้านล่าง",
    "payment": "💳 รับชำระ: เงินสด/โอนเงิน/พร้อมเพย์\n📷 ส่งสลิปในแชทหลังสั่งเสร็จนะคะ",
    "order": "🛒 สั่งอาหารออนไลน์ได้ที่ลิงก์ด้านล่าง\nหรือกดปุ่ม 'สั่งอาหาร' เลยค่ะ"
}

FALLBACK_MESSAGE = "ขออภัยค่ะ ไม่เข้าใจคำถาม 🤔\nลองถามใหม่หรือกด 'สั่งอาหาร' เลยนะคะ 😊"

async def supabase_request(method: str, endpoint: str, data: Dict = None, use_service_key: bool = True) -> Dict:
    """Make request to Supabase REST API"""
    headers = {
        "apikey": SUPABASE_SERVICE_KEY if use_service_key else SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY if use_service_key else SUPABASE_ANON_KEY}",
        "Content-Type": "application/json"
    }
    
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    
    async with httpx.AsyncClient() as client:
        if method == "GET":
            response = await client.get(url, headers=headers)
        elif method == "POST":
            response = await client.post(url, headers=headers, json=data)
        elif method == "PATCH":
            response = await client.patch(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
    
    if response.status_code not in [200, 201, 204]:
        print(f"Supabase error: {response.status_code} - {response.text}")
        raise HTTPException(status_code=500, detail="Database error")
    
    return response.json() if response.text else {}

async def send_line_message(reply_token: str, messages: List[Dict]):
    """Send reply message to LINE"""
    if not LINE_CHANNEL_ACCESS_TOKEN:
        print("LINE_CHANNEL_ACCESS_TOKEN not set")
        return
    
    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "replyToken": reply_token,
        "messages": messages
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.line.me/v2/bot/message/reply",
            headers=headers,
            json=payload
        )
        
    if response.status_code != 200:
        print(f"LINE reply error: {response.status_code} - {response.text}")

def classify_intent(message_text: str) -> str:
    """Classify user intent from message"""
    text = message_text.lower()
    
    if any(word in text for word in ["เวลา", "เปิด", "ปิด", "โมง", "hours"]):
        return "hours"
    elif any(word in text for word in ["ที่อยู่", "แอดเดรส", "location", "address"]):
        return "location"
    elif any(word in text for word in ["ราคา", "เท่าไร", "price", "cost"]):
        return "menu"
    elif any(word in text for word in ["ชำระ", "จ่าย", "payment", "pay"]):
        return "payment"
    elif any(word in text for word in ["สั่ง", "เมนู", "อาหาร", "order", "food", "menu"]):
        return "order"
    else:
        return "unknown"

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

@app.post("/webhook/line")
async def line_webhook(request: Request):
    """Handle LINE webhook events"""
    try:
        # Get signature
        signature = request.headers.get('X-Line-Signature', '')
        body = await request.body()
        
        # Verify signature (temporarily disabled for testing)
        # if not verify_line_signature(body, signature):
        #     raise HTTPException(status_code=401, detail="Invalid signature")
        print(f"Signature check: {signature[:20]}... (validation disabled)")
        
        # Parse body
        events = json.loads(body.decode('utf-8')).get('events', [])
        
        for event in events:
            if event['type'] == 'message' and event['message']['type'] == 'text':
                message_text = event['message']['text']
                reply_token = event['replyToken']
                user_id = event['source']['userId']
                
                # Classify intent and get response
                intent = classify_intent(message_text)
                
                if intent in FAQ_RESPONSES:
                    # FAQ Response
                    response_text = FAQ_RESPONSES[intent]
                    messages = [{"type": "text", "text": response_text}]
                    
                    # Add order button for relevant intents
                    if intent in ["order", "menu"]:
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
                                        "uri": "https://order.tenzaitech.online"
                                    }
                                ]
                            }
                        })
                else:
                    # Unknown intent - fallback with order button
                    messages = [
                        {"type": "text", "text": FALLBACK_MESSAGE},
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
                                        "uri": "https://order.tenzaitech.online"
                                    }
                                ]
                            }
                        }
                    ]
                
                # Send reply
                await send_line_message(reply_token, messages)
                
                # Log conversation (optional)
                try:
                    conversation_data = {
                        "line_user_id": user_id,
                        "message_text": message_text[:300],  # Limit length
                        "response_text": response_text[:300] if intent in FAQ_RESPONSES else "สั่งอาหาร", 
                        "created_at": datetime.now().isoformat()
                    }
                    await supabase_request("POST", "conversations", conversation_data)
                except Exception as e:
                    print(f"Conversation logging error: {e}")
        
        return {"status": "ok"}
        
    except Exception as e:
        print(f"LINE webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/orders/create")
async def create_order(request: Request):
    """Handle order creation from web app"""
    try:
        order_data = await request.json()
        print(f"Received order: {order_data}")
        
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
                "note": item.get("note", "")
            })
        
        # Upsert customer
        customer_data = {
            "display_name": contact["name"],
            "phone": contact["phone"],
        }
        
        # Add user reference if available
        user_ref = order_data.get("user_ref", {})
        if user_ref.get("line_user_id"):
            customer_data["line_user_id"] = user_ref["line_user_id"]
        
        # Try to upsert customer (this is simplified - in production you'd handle conflicts better)
        customer = await supabase_request("POST", "customers", customer_data)
        customer_id = customer[0]["id"] if customer else None
        
        if not customer_id:
            raise HTTPException(status_code=500, detail="Failed to create/find customer")
        
        # Generate order number
        order_number = f"T{datetime.now().strftime('%y%m%d')}{datetime.now().hour:02d}{datetime.now().minute:02d}"
        
        # Create order
        order_data = {
            "customer_id": customer_id,
            "order_number": order_number,
            "customer_name": contact["name"],
            "status": "pending",
            "total_amount": total_amount,
            "order_type": "pickup",
            "created_at": datetime.now().isoformat()
        }
        
        order = await supabase_request("POST", "orders", order_data)
        order_id = order[0]["id"]
        
        # Create order items
        for item in validated_items:
            item["order_id"] = order_id
            
        await supabase_request("POST", "order_items", validated_items)
        
        # TODO: Send staff notification (LINE push message to staff)
        # This would require staff LINE user IDs in system_settings
        
        return {
            "success": True,
            "order_id": order_number,
            "total": total_amount,
            "message": f"ออเดอร์ {order_number} สำเร็จ! ยอดรวม {total_amount:,.0f} บาท"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Order creation error: {e}")
        raise HTTPException(status_code=500, detail="Order creation failed")

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