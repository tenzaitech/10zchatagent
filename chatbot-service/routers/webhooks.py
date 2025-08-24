"""
Chatbot Webhook Router
Handles LINE/Facebook webhooks for chat messages ONLY
Order-related functionality removed and handled by order service
"""

import json
import sys
import os
from fastapi import APIRouter, Request, HTTPException
from typing import Dict

# Add shared modules to path
shared_path = os.path.join(os.path.dirname(__file__), "..", "..", "shared-modules")
sys.path.insert(0, shared_path)

# Import shared modules
from config import FAQ_RESPONSES
from database import log_conversation
from models import FAQ_RESPONSES, create_line_text_message, create_line_button_message

# Import chatbot services
from services.line_service import send_line_message, verify_line_signature
from services.ai_service import get_ai_response, classify_intent

router = APIRouter(prefix="/webhook", tags=["chatbot-webhooks"])

@router.post("/line")
async def line_chat_webhook(request: Request):
    """Handle LINE webhook events for CHAT MESSAGES only"""
    try:
        # Get raw body and signature
        body = await request.body()
        signature = request.headers.get("x-line-signature", "")
        
        if not signature:
            raise HTTPException(status_code=400, detail="Missing signature")
        
        # Verify signature
        if not verify_line_signature(body, signature):
            print("❌ Invalid LINE signature")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse events
        try:
            webhook_data = json.loads(body.decode('utf-8'))
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON")
        
        events = webhook_data.get("events", [])
        print(f"💬 Chatbot webhook: {len(events)} events")
        
        # Process each event
        for event in events:
            # Only handle text messages (no postback/order handling)
            if event["type"] == "message" and event["message"]["type"] == "text":
                await handle_chat_message(event)
            else:
                print(f"⏭️ Skipping non-chat event: {event['type']}")
        
        return {"status": "ok", "processed_events": len(events), "service": "chatbot"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Chatbot webhook error: {e}")
        raise HTTPException(status_code=500, detail="Chat processing failed")

async def handle_chat_message(event: Dict):
    """Handle individual chat message"""
    reply_token = event["replyToken"]
    user_id = event["source"]["userId"]
    message_text = event["message"]["text"]
    
    print(f"💬 Chat from {user_id}: {message_text}")
    
    # Classify intent and respond
    intent = classify_intent(message_text)
    print(f"🎯 Intent: {intent}")
    
    response_text = ""
    messages = []
    
    if intent in FAQ_RESPONSES:
        # FAQ Response (instant)
        response_text = FAQ_RESPONSES[intent]
        messages = [create_line_text_message(response_text)]
        
        # Add order button for relevant intents
        if intent in ["order", "menu"]:
            # Deep link to order service
            deep_link = f"https://tenzai-order.ap.ngrok.io/customer_webapp.html?platform=LINE&user_id={user_id}"
            
            order_button = create_line_button_message(
                "คลิกสั่งอาหารได้เลย!",
                [{
                    "type": "uri",
                    "label": "🍜 สั่งอาหาร",
                    "uri": deep_link
                }]
            )
            messages.append(order_button)
    
    elif intent == "greeting":
        # Greeting with order button
        response_text = "สวัสดีค่ะ! ยินดีต้อนรับสู่ Tenzai Sushi 🍣\\nมีอะไรให้ช่วยไหมคะ?"
        deep_link = f"https://tenzai-order.ap.ngrok.io/customer_webapp.html?platform=LINE&user_id={user_id}"
        
        messages = [
            create_line_text_message(response_text),
            create_line_button_message(
                "สั่งอาหารได้เลยค่ะ!",
                [{
                    "type": "uri",
                    "label": "🍜 สั่งอาหาร",
                    "uri": deep_link
                }]
            )
        ]
    
    elif intent in ["ai_complex", "ai_fallback"]:
        # Use AI for complex queries
        response_text = await get_ai_response(message_text, user_id)
        messages = [create_line_text_message(response_text)]
    else:
        # Default fallback
        response_text = FAQ_RESPONSES.get("greeting", "สวัสดีค่ะ! ยินดีต้อนรับสู่ Tenzai Sushi 🍣")
        messages = [create_line_text_message(response_text)]
    
    # Send reply
    success = await send_line_message(reply_token, messages)
    if success:
        print(f"✅ Chat reply sent to {user_id}")
        
        # Log conversation
        try:
            await log_conversation(f"LINE_{user_id}", message_text, response_text or "ปุ่มและข้อความ")
            print(f"📝 Logged chat for LINE_{user_id}")
        except Exception as e:
            print(f"⚠️ Failed to log conversation: {e}")
    else:
        print(f"❌ Failed to send chat reply to {user_id}")

@router.get("/")
async def webhook_info():
    """Webhook service info"""
    return {
        "service": "chatbot-webhooks",
        "description": "Handles chat messages only",
        "endpoints": {
            "/webhook/line": "LINE chat webhook"
        }
    }