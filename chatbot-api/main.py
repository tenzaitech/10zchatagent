#!/usr/bin/env python3
"""
Tenzai Chatbot API v2 - Modular Structure
Uses refactored modules for better maintainability
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

# Import our modular services
from modules.config import (
    validate_config, FAQ_RESPONSES, 
    SUPABASE_URL, LINE_CHANNEL_SECRET
)
from services.database_service import (
    supabase_request, find_or_create_customer
)
from services.line_service import (
    send_line_message, verify_line_signature
)
from services.ai_service import (
    get_ai_response, classify_intent
)
from services.notification_service import (
    send_order_confirmation
)

# Load .env file
load_dotenv()
print("🔧 Loading .env file...")

# Validate configuration
if not validate_config():
    print("❌ Configuration validation failed!")
    exit(1)

app = FastAPI(title="Tenzai Chatbot API v2", version="2.0.0")

# CORS for web app (including ngrok domains)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://tenzai-order.ngrok.io",
        "https://*.ngrok.io",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("🚀 Tenzai Chatbot API v2 initialized!")

# ========== Health Check ==========
@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "Tenzai Chatbot API", "timestamp": datetime.now().isoformat()}

# ========== Schema Endpoints ==========
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

# ========== Order Management ==========
@app.post("/api/orders/create")
async def create_order(request: Request, background_tasks: BackgroundTasks):
    """Create new order with enhanced validation"""
    try:
        order_data = await request.json()
        print(f"📝 Creating order: {json.dumps(order_data, indent=2, ensure_ascii=False)}")
        
        # Extract customer data
        customer_info = order_data.get("customer", {})
        name = customer_info.get("name", "").strip()
        phone = customer_info.get("phone", "").strip()
        
        # Validate required fields
        if not name or not phone:
            raise HTTPException(status_code=400, detail="Name and phone are required")
        
        if not order_data.get("items") or len(order_data.get("items", [])) == 0:
            raise HTTPException(status_code=400, detail="At least one item is required")
        
        # Create or find customer
        customer_id = await find_or_create_customer(
            name=name, 
            phone=phone, 
            platform="WEB",
            platform_user_id=phone
        )
        
        # Generate order number
        order_number = f"TZ{datetime.now().strftime('%m%d%H%M')}{str(uuid.uuid4())[:4].upper()}"
        
        # Calculate total
        total_amount = sum(item.get("price", 0) * item.get("quantity", 1) for item in order_data.get("items", []))
        items_count = sum(item.get("quantity", 1) for item in order_data.get("items", []))
        
        # Create order record
        order_payload = {
            "order_number": order_number,
            "customer_id": customer_id,
            "total_amount": total_amount,
            "status": "pending",
            "notes": order_data.get("notes", ""),
            "order_source": "web"
        }
        
        order_result = await supabase_request("POST", "orders", order_payload)
        if not order_result or len(order_result) == 0:
            raise HTTPException(status_code=500, detail="Failed to create order")
        
        order_id = order_result[0]["id"]
        
        # Create order items
        for item in order_data.get("items", []):
            item_payload = {
                "order_id": order_id,
                "menu_item_id": item.get("menu_item_id"),
                "quantity": item.get("quantity", 1),
                "unit_price": item.get("price", 0),
                "item_name": item.get("name", ""),
                "notes": item.get("notes", "")
            }
            await supabase_request("POST", "order_items", item_payload)
        
        print(f"✅ Order created successfully: {order_number}")
        
        # Send confirmation notification in background
        background_tasks.add_task(
            send_order_confirmation,
            order_number=order_number,
            customer_phone=phone,
            customer_name=name,
            platform="WEB",
            platform_user_id=phone,
            total_amount=total_amount,
            items_count=items_count
        )
        
        return {
            "success": True,
            "order_number": order_number,
            "message": "Order created successfully",
            "tracking_url": f"https://tenzai-order.ap.ngrok.io/order-status.html?order={order_number}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Order creation error: {e}")
        raise HTTPException(status_code=500, detail=f"Order creation failed: {str(e)}")

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
            "total_amount": order["total_amount"], 
            "created_at": order["created_at"],
            "items": order.get("order_items", []),
            "notes": order.get("notes", "")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting order status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get order status")

# ========== LINE Webhook ==========
@app.post("/webhook/line")
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
            if event["type"] == "message" and event["message"]["type"] == "text":
                # Handle text message
                reply_token = event["replyToken"]
                user_id = event["source"]["userId"]
                message_text = event["message"]["text"]
                
                print(f"💬 Message from {user_id}: {message_text}")
                
                # Classify intent and respond
                intent = classify_intent(message_text)
                messages = []
                
                if intent in FAQ_RESPONSES:
                    # FAQ response
                    faq_text = FAQ_RESPONSES[intent]
                    messages.append({
                        "type": "text",
                        "text": faq_text
                    })
                elif intent == "order":
                    # Order intent - send web order link
                    messages.append({
                        "type": "text",
                        "text": "🍣 สั่งอาหารผ่านหน้าเว็บได้เลยค่ะ!"
                    })
                    messages.append({
                        "type": "template",
                        "altText": "สั่งอาหาร Tenzai Sushi",
                        "template": {
                            "type": "buttons",
                            "text": "เลือกวิธีการสั่งอาหาร",
                            "actions": [{
                                "type": "uri",
                                "label": "🍣 สั่งอาหารเลย!",
                                "uri": f"https://order.tenzaitech.online?line_id={user_id}&name=ลูกค้า LINE"
                            }]
                        }
                    })
                elif intent in ["ai_complex", "ai_fallback"]:
                    # Use AI for complex queries
                    ai_response = await get_ai_response(message_text, user_id)
                    messages.append({
                        "type": "text",
                        "text": ai_response
                    })
                else:
                    # Default greeting
                    messages.append({
                        "type": "text", 
                        "text": "สวัสดีค่ะ! ยินดีต้อนรับสู่ Tenzai Sushi 🍣"
                    })
                
                # Send reply
                success = await send_line_message(reply_token, messages)
                if success:
                    print(f"✅ Replied to {user_id}")
                else:
                    print(f"❌ Failed to reply to {user_id}")
        
        return {"status": "ok", "processed_events": len(events)}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

# ========== Server Start ==========
if __name__ == "__main__":
    print("🚀 Starting Tenzai Chatbot API v2...")
    print(f"🌐 Supabase: {SUPABASE_URL}")
    print(f"🔗 LINE Channel Secret: {'✅' if LINE_CHANNEL_SECRET else '❌'}")
    
    # Run on standard port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)