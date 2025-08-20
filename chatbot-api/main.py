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
    """Get basic table information from Supabase (simplified version)"""
    try:
        # Since we can't use SQL directly, get table info from sample data
        tables = ['customers', 'orders', 'order_items', 'menus', 'categories', 'conversations']
        schemas = {}
        
        for table_name in tables:
            try:
                print(f"📋 Inspecting table: {table_name}")
                # Get sample data to see column structure
                data = await supabase_request("GET", f"{table_name}?limit=1", use_service_key=False)
                
                if data and len(data) > 0:
                    columns = list(data[0].keys())
                    schemas[table_name] = {
                        "columns": columns,
                        "sample_count": len(data),
                        "accessible": True
                    }
                else:
                    schemas[table_name] = {
                        "columns": [],
                        "sample_count": 0,
                        "accessible": True,
                        "note": "Empty table"
                    }
                    
            except Exception as e:
                print(f"❌ Error inspecting {table_name}: {e}")
                schemas[table_name] = {
                    "error": str(e),
                    "accessible": False
                }
        
        return {
            "status": "success",
            "schemas": schemas,
            "timestamp": datetime.now().isoformat(),
            "note": "Simplified schema inspection (no SQL execution)"
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
        
        # Extract customer data (support both old and new formats)
        contact = order_data.get("contact", order_data.get("customer", {}))
        name = contact.get("name", "").strip()
        phone = contact.get("phone", "").strip()
        
        # Extract items (support both old and new formats)  
        items = order_data.get("cart", order_data.get("items", []))
        
        # Validate required fields
        if not name or not phone:
            raise HTTPException(status_code=400, detail="Name and phone are required")
        
        if not items or len(items) == 0:
            raise HTTPException(status_code=400, detail="At least one item is required")
        
        # Create or find customer
        customer_id = await find_or_create_customer(
            name=name, 
            phone=phone, 
            platform="WEB",
            platform_user_id=phone
        )
        
        # Generate order number (matching original format)
        order_number = f"T{datetime.now().strftime('%y%m%d%H%M%S')}"
        
        # Calculate total (support both formats)
        total_amount = 0
        items_count = 0
        for item in items:
            # Support both old format (qty) and new format (quantity)
            quantity = item.get("qty", item.get("quantity", 1))
            price = item.get("price", 0)  # For new format, price might be provided
            
            # For old format, we'd need to lookup price from menus table (simplified for now)
            if price == 0:
                price = 150  # Default price for testing
            
            total_amount += price * quantity
            items_count += quantity
        
        # Create order record (matching actual database structure)
        order_payload = {
            "order_number": order_number,
            "customer_id": customer_id,
            "customer_name": name,
            "customer_phone": phone,
            "status": "pending",
            "order_type": "pickup",
            "total_amount": total_amount,
            "payment_method": "qr_code", 
            "payment_status": "unpaid",
            "notes": order_data.get("notes", "")
        }
        
        order_result = await supabase_request("POST", "orders", order_payload)
        
        # Handle Supabase response patterns
        if not order_result or len(order_result) == 0:
            print("🔄 Order created but no ID returned, fetching...")
            fetch_query = f"orders?order_number=eq.{order_number}&select=id&limit=1"
            fetch_result = await supabase_request("GET", fetch_query, use_service_key=False)
            if fetch_result and len(fetch_result) > 0:
                order_id = fetch_result[0]["id"]
                print(f"✅ Fetched new order ID: {order_id}")
            else:
                raise HTTPException(status_code=500, detail="Failed to create order")
        else:
            order_id = order_result[0]["id"]
            print(f"✅ Order created with ID: {order_id}")
        
        # Create order items (matching actual database structure)
        validated_items = []
        for item in items:
            quantity = item.get("qty", item.get("quantity", 1))
            price = item.get("price", 0)
            if price == 0:
                price = 150  # Default for testing
                
            item_payload = {
                "order_id": order_id,
                "menu_id": item.get("menu_id") or item.get("menu_item_id"),  # Support both field names
                "quantity": quantity,
                "unit_price": price,
                "total_price": price * quantity,
                "menu_name": item.get("name", "Test Item"),
                "notes": item.get("note", item.get("notes", ""))  # Support both field names
            }
            validated_items.append(item_payload)
        
        # Insert all order items at once (like original)
        if validated_items:
            await supabase_request("POST", "order_items", validated_items)
            print(f"✅ Created {len(validated_items)} order items")
        
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