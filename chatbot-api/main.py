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
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os
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
    send_order_confirmation, send_staff_notification
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

# ========== Static Files & HTML Routes ==========
# Get static files directory
static_dir = os.path.join(os.path.dirname(__file__), "..", "webappadmin")

# HTML pages routes
@app.get("/")
async def root():
    return FileResponse(os.path.join(static_dir, "customer_webapp.html"))

@app.get("/customer_webapp.html")
async def customer_webapp():
    return FileResponse(os.path.join(static_dir, "customer_webapp.html"))

@app.get("/order-status.html") 
async def order_status():
    return FileResponse(os.path.join(static_dir, "order-status.html"))

@app.get("/favicon.ico")
async def favicon():
    favicon_path = os.path.join(static_dir, "favicon.ico")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    return {"status": "no favicon"}

# Admin pages (optional)
@app.get("/admin/edit-menu")
async def admin_menu():
    return FileResponse(os.path.join(static_dir, "edit_menu_dashboard-admin.html"))

@app.get("/admin/staff-orders.html")
async def staff_orders():
    return FileResponse(os.path.join(static_dir, "admin", "staff-orders.html"))

# ========== Health Check ==========
@app.get("/health")
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
        
        # Extract platform info (for LINE orders from web app)
        platform = order_data.get("platform", "WEB")
        platform_user_id = order_data.get("platform_user_id", phone)
        
        # Extract items (support both old and new formats)  
        items = order_data.get("cart", order_data.get("items", []))
        
        # Validate required fields
        if not name or not phone:
            raise HTTPException(status_code=400, detail="Name and phone are required")
        
        if not items or len(items) == 0:
            raise HTTPException(status_code=400, detail="At least one item is required")
        
        # Create or find customer with correct platform
        customer_id = await find_or_create_customer(
            name=name, 
            phone=phone, 
            platform=platform,
            platform_user_id=platform_user_id
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
        
        # Send staff notification (CRITICAL - immediate alert)
        background_tasks.add_task(
            send_staff_notification,
            order_number=order_number,
            customer_name=name,
            customer_phone=phone,
            total_amount=total_amount,
            items=validated_items  # Send detailed items list
        )
        
        # Send confirmation notification to customer
        background_tasks.add_task(
            send_order_confirmation,
            order_number=order_number,
            customer_phone=phone,
            customer_name=name,
            platform=platform,
            platform_user_id=platform_user_id,
            total_amount=total_amount,
            items_count=items_count,
            items_list=validated_items
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

@app.get("/api/orders/today")
async def get_today_orders():
    """Get all orders for today (for staff dashboard)"""
    try:
        from datetime import date, datetime
        today = date.today()
        
        print(f"🔍 Getting orders for date: {today}")
        
        # Query recent orders (last 24 hours) with customer and items data
        # Using broader query first to check what's available
        query = "orders?order=created_at.desc&limit=50&select=*,order_items(quantity,unit_price,total_price,menu_name,notes)"
        all_orders = await supabase_request("GET", query, use_service_key=False)
        
        if not all_orders:
            all_orders = []
        
        # Filter orders for today (client-side filtering as fallback)
        today_orders = []
        today_str = today.isoformat()
        
        for order in all_orders:
            order_date = order.get("created_at", "")
            if order_date.startswith(today_str):
                today_orders.append(order)
        
        print(f"📊 Found {len(all_orders)} total orders, {len(today_orders)} today")
        
        return {
            "orders": today_orders,
            "date": today_str,
            "total_count": len(today_orders),
            "debug_info": {
                "total_orders_found": len(all_orders),
                "sample_dates": [order.get("created_at", "")[:10] for order in all_orders[:5]]
            }
        }
        
    except Exception as e:
        print(f"❌ Error getting today's orders: {e}")
        raise HTTPException(status_code=500, detail="Failed to get today's orders")

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
        
        # Transform items data for frontend
        transformed_items = []
        for item in order.get("order_items", []):
            transformed_items.append({
                "name": item.get("menus", {}).get("name", item.get("menu_name", "Unknown Item")),
                "quantity": item.get("quantity", 1),
                "unit_price": item.get("unit_price", 0),
                "total_price": item.get("total_price", 0),
                "notes": item.get("notes", "")
            })
        
        # Create status timeline
        status_timeline = [
            {"status": "pending", "text": "รับออเดอร์แล้ว", "completed": True},
            {"status": "confirmed", "text": "ยืนยันออเดอร์", "completed": order["status"] in ["confirmed", "preparing", "ready", "completed"]},
            {"status": "preparing", "text": "กำลังเตรียมอาหาร", "completed": order["status"] in ["preparing", "ready", "completed"]},
            {"status": "ready", "text": "เตรียมเสร็จแล้ว", "completed": order["status"] in ["ready", "completed"]},
            {"status": "completed", "text": "เสร็จสิ้น", "completed": order["status"] == "completed"}
        ]
        
        return {
            "order_number": order["order_number"],
            "status": order["status"],
            "customer_name": order.get("customer_name", "N/A"),
            "customer_phone": order.get("customer_phone", "N/A"),
            "total_amount": order["total_amount"], 
            "payment_status": order.get("payment_status", "unpaid"),
            "order_type": order.get("order_type", "pickup"),
            "created_at": order["created_at"],
            "items": transformed_items,
            "status_history": status_timeline,
            "notes": order.get("notes", "")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting order status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get order status")

@app.patch("/api/orders/{order_number}/status")
async def update_order_status(order_number: str, request: Request):
    """Update order status (for staff dashboard)"""
    try:
        data = await request.json()
        new_status = data.get("status")
        
        if not new_status:
            raise HTTPException(status_code=400, detail="Status is required")
        
        valid_statuses = ["pending", "confirmed", "preparing", "ready", "completed", "cancelled"]
        if new_status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
        
        # Update order status
        update_data = {"status": new_status}
        result = await supabase_request("PATCH", f"orders?order_number=eq.{order_number}", update_data)
        
        print(f"✅ Updated order {order_number} status to {new_status}")
        
        return {
            "success": True,
            "order_number": order_number,
            "new_status": new_status,
            "message": f"Order status updated to {new_status}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error updating order status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update order status")

@app.post("/api/staff/notifications")
async def create_staff_notification(request: Request):
    """Create staff notification record"""
    try:
        data = await request.json()
        
        notification_data = {
            "order_number": data.get("order_number"),
            "notification_type": data.get("notification_type", "new_order"),
            "message": data.get("message", ""),
            "sent_at": datetime.now().isoformat(),
            "status": data.get("status", "sent")
        }
        
        result = await supabase_request("POST", "staff_notifications", notification_data)
        
        return {
            "success": True,
            "message": "Staff notification logged"
        }
        
    except Exception as e:
        print(f"❌ Error creating staff notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to create staff notification")

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

# ========== Server Start ==========
if __name__ == "__main__":
    print("🚀 Starting Tenzai Chatbot API v2...")
    print(f"🌐 Supabase: {SUPABASE_URL}")
    print(f"🔗 LINE Channel Secret: {'✅' if LINE_CHANNEL_SECRET else '❌'}")
    
    # Run on standard port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
    