"""
Webhook Router
Handles LINE webhook events and other platform webhooks
Extracted from main.py for better modularity
"""

import json
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks

from modules.config import FAQ_RESPONSES
from services.database_service import supabase_request
from services.line_service import send_line_message, verify_line_signature
from services.ai_service import get_ai_response, classify_intent

router = APIRouter(prefix="/webhook", tags=["webhooks"])

@router.post("/line")
async def line_webhook(request: Request, background_tasks: BackgroundTasks):
    """Handle LINE webhook events with enhanced security"""
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
        print(f"📨 LINE webhook: {len(events)} events")
        
        # Process each event
        for event in events:
            # Handle postback events (staff buttons)
            if event["type"] == "postback":
                reply_token = event["replyToken"]
                user_id = event["source"]["userId"]
                postback_data = event["postback"]["data"]
                
                print(f"📞 Postback from {user_id}: {postback_data}")
                
                # Parse postback data (action=accept_order&order=T123456)
                if "action=accept_order" in postback_data:
                    order_number = postback_data.split("order=")[1] if "order=" in postback_data else ""
                    if order_number:
                        # Update order status to confirmed
                        try:
                            update_data = {"status": "confirmed"}
                            await supabase_request("PATCH", f"orders?order_number=eq.{order_number}", update_data)
                            
                            reply_message = {
                                "type": "text",
                                "text": f"✅ รับออเดอร์ #{order_number} แล้ว!\nสถานะ: ยืนยันออเดอร์"
                            }
                            await send_line_message(reply_token, [reply_message])
                            print(f"✅ Order {order_number} accepted by staff")
                        except Exception as e:
                            print(f"❌ Error accepting order: {e}")
                
                elif "action=reject_order" in postback_data:
                    order_number = postback_data.split("order=")[1] if "order=" in postback_data else ""
                    if order_number:
                        # Update order status to cancelled
                        try:
                            update_data = {"status": "cancelled"}
                            await supabase_request("PATCH", f"orders?order_number=eq.{order_number}", update_data)
                            
                            reply_message = {
                                "type": "text",
                                "text": f"❌ ปฏิเสธออเดอร์ #{order_number}\nสถานะ: ยกเลิกออเดอร์"
                            }
                            await send_line_message(reply_token, [reply_message])
                            print(f"❌ Order {order_number} rejected by staff")
                        except Exception as e:
                            print(f"❌ Error rejecting order: {e}")
            
            elif event["type"] == "message" and event["message"]["type"] == "text":
                # Handle text message
                reply_token = event["replyToken"]
                user_id = event["source"]["userId"]
                message_text = event["message"]["text"]
                
                print(f"💬 Message from {user_id}: {message_text}")
                
                # Classify intent and respond (matching original behavior)
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
                    # Use AI for complex queries
                    response_text = await get_ai_response(message_text, user_id)
                    messages = [{"type": "text", "text": response_text}]
                else:
                    # Default fallback
                    response_text = FAQ_RESPONSES.get("greeting", "สวัสดีค่ะ! ยินดีต้อนรับสู่ Tenzai Sushi 🍣")
                    messages = [{"type": "text", "text": response_text}]
                
                # Send reply
                success = await send_line_message(reply_token, messages)
                if success:
                    print(f"✅ Replied to {user_id}")
                    
                    # Log conversation (matching original behavior)
                    try:
                        conversation_data = {
                            "line_user_id": f"LINE_{user_id}",
                            "message_text": message_text,
                            "response_text": response_text or "ปุ่มและข้อความ"
                        }
                        await supabase_request("POST", "conversations", conversation_data)
                        print(f"📝 Logged conversation for LINE_{user_id}")
                    except Exception as e:
                        print(f"⚠️ Failed to log conversation: {e}")
                else:
                    print(f"❌ Failed to reply to {user_id}")
        
        return {"status": "ok", "processed_events": len(events)}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")