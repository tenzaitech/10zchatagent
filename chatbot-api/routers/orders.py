"""
Order Management Router
Handles all order-related endpoints (CRUD operations)
Extracted from main.py for better modularity
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from pytz import timezone

from services.database_service import supabase_request, find_or_create_customer
from services.notification_service import send_order_confirmation, send_staff_notification
from services.ai_service import get_ai_response

router = APIRouter(prefix="/api/orders", tags=["orders"])

@router.post("/create")
async def create_order(request: Request, background_tasks: BackgroundTasks):
    """Create a new order from WebOrder form"""
    try:
        # Parse JSON data with proper error handling
        try:
            data = await request.json()
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail="Invalid JSON format")
        except Exception as e:
            raise HTTPException(status_code=400, detail="Failed to parse request data")
            
        print(f"📝 Creating order with data: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        # Validate required fields
        required_fields = ["customer_name", "customer_phone", "items", "total_amount", "order_type"]
        for field in required_fields:
            if field not in data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Validate field values
        if not data["customer_name"].strip():
            raise HTTPException(status_code=400, detail="Customer name cannot be empty")
        
        if not data["customer_phone"].strip() or len(data["customer_phone"]) < 10:
            raise HTTPException(status_code=400, detail="Invalid phone number format")
        
        if not data["items"]:
            raise HTTPException(status_code=400, detail="Order must contain at least one item")
        
        if float(data["total_amount"]) <= 0:
            raise HTTPException(status_code=400, detail="Total amount must be positive")
        
        if data["order_type"] not in ["pickup", "delivery"]:
            raise HTTPException(status_code=400, detail="Order type must be 'pickup' or 'delivery'")
        
        # Create or find customer
        customer_id = await find_or_create_customer(
            name=data["customer_name"],
            phone=data["customer_phone"],
            platform="WEB",
            platform_user_id=data["customer_phone"]
        )
        
        # Generate order number
        thailand_tz = timezone('Asia/Bangkok')
        now = datetime.now(thailand_tz)
        order_number = f"T{now.strftime('%m%d')}{str(uuid.uuid4())[:4].upper()}"
        
        # Prepare order data
        order_data = {
            "order_number": order_number,
            "customer_id": customer_id,
            "customer_name": data["customer_name"],
            "customer_phone": data["customer_phone"],
            "total_amount": float(data["total_amount"]),
            "order_type": data["order_type"],
            "payment_method": data.get("payment_method", "cash"),
            "payment_status": "unpaid",
            "status": "pending",
            "notes": data.get("notes", ""),
            "created_at": now.isoformat()
        }
        
        # Create order
        created_orders = await supabase_request("POST", "orders", order_data)
        if not created_orders or len(created_orders) == 0:
            print(f"❌ Supabase returned empty result for order creation")
            raise HTTPException(status_code=500, detail="Database failed to create order")
        
        order = created_orders[0]
        print(f"✅ Order record created in database: {order.get('id', 'Unknown ID')}")
        
        # Create order items
        total_calculated = 0
        for item in data["items"]:
            item_data = {
                "order_id": order["id"],
                "menu_id": item.get("id"),
                "menu_name": item["name"],
                "quantity": item["quantity"],
                "unit_price": float(item["price"]),
                "total_price": float(item["price"]) * item["quantity"],
                "notes": item.get("notes", "")
            }
            total_calculated += item_data["total_price"]
            
            await supabase_request("POST", "order_items", item_data)
        
        # Verify total amount
        if abs(total_calculated - float(data["total_amount"])) > 0.01:
            print(f"⚠️ Total amount mismatch: calculated {total_calculated}, provided {data['total_amount']}")
        
        print(f"✅ Order created successfully: {order_number}")
        
        # Send notifications in background
        background_tasks.add_task(
            send_order_confirmation,
            order_number,
            data["customer_phone"],  # customer_phone
            data["customer_name"],   # customer_name
            "WEB",                   # platform
            data["customer_phone"],  # platform_user_id
            float(data["total_amount"]),  # total_amount
            len(data["items"]),      # items_count
            data["items"]            # items_list
        )
        background_tasks.add_task(
            send_staff_notification,
            order_number,
            data["customer_name"],
            data["customer_phone"],
            float(data["total_amount"]),
            data["items"]
        )
        
        return {
            "success": True,
            "order_number": order_number,
            "order_id": order["id"],
            "message": "Order created successfully",
            "total_amount": order["total_amount"],
            "status": order["status"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error creating order: {e}")
        raise HTTPException(status_code=500, detail="Failed to create order")

@router.get("/status/today")
async def get_today_orders():
    """Get today's orders for staff dashboard"""
    try:
        print("📊 Getting today's orders...")
        
        # Get Thailand timezone
        thailand_tz = timezone('Asia/Bangkok')
        thailand_now = datetime.now(thailand_tz)
        today_str = thailand_now.strftime('%Y-%m-%d')
        
        print(f"🕒 Thailand time: {thailand_now}")
        print(f"📅 Looking for orders on: {today_str}")
        
        # Query all orders to debug
        all_orders = await supabase_request("GET", "orders?select=*&order=created_at.desc&limit=100", use_service_key=False)
        
        # Filter today's orders
        today_orders = []
        for order in all_orders:
            order_date = order.get("created_at", "")[:10]  # Get YYYY-MM-DD part
            if order_date == today_str:
                today_orders.append(order)
        
        print(f"📈 Found {len(today_orders)} orders today out of {len(all_orders)} total orders")
        
        return {
            "success": True,
            "orders": today_orders,
            "date": today_str,
            "thailand_time": thailand_now.isoformat(),
            "total_count": len(today_orders),
            "debug_info": {
                "total_orders_found": len(all_orders),
                "sample_dates": [order.get("created_at", "")[:10] for order in all_orders[:5]]
            }
        }
        
    except Exception as e:
        print(f"❌ Error getting today's orders: {e}")
        raise HTTPException(status_code=500, detail="Failed to get today's orders")

@router.get("/{order_number}")
async def get_order_status(order_number: str):
    """Get order status for tracking page"""
    print(f"🔍 Starting get_order_status for: {order_number}")
    
    # Prevent conflict with /today endpoint
    if order_number.lower() == "today":
        raise HTTPException(status_code=400, detail="Invalid order number")
    
    try:
        print(f"🔍 Getting status for order: {order_number}")
        
        # Query order with customer and items
        order_query = f"orders?order_number=eq.{order_number}&select=*,order_items(*,menus(name,price))&limit=1"
        orders = await supabase_request("GET", order_query, use_service_key=False)
        
        print(f"🔍 Orders result: {orders}")
        print(f"🔍 Orders type: {type(orders)}")
        print(f"🔍 Orders length: {len(orders) if orders else 'None'}")
        
        if not orders or len(orders) == 0:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order = orders[0]
        print(f"🔍 Order data: {order}")
        
        # Safely get order_items
        order_items = order.get("order_items", []) if order else []
        print(f"🔍 Order items: {order_items}")
        
        # Transform items data for frontend
        transformed_items = []
        if order_items:
            for item in order_items:
                print(f"🔍 Processing item: {item}")
                # Handle both nested menus object and direct menu_name
                menu_data = item.get("menus") if item else None
                if menu_data and isinstance(menu_data, dict):
                    menu_name = menu_data.get("name", item.get("menu_name", "Unknown Item"))
                else:
                    menu_name = item.get("menu_name", "Unknown Item") if item else "Unknown Item"
                
                transformed_items.append({
                    "name": menu_name,
                    "quantity": item.get("quantity", 1) if item else 1,
                    "unit_price": item.get("unit_price", 0) if item else 0,
                    "total_price": item.get("total_price", 0) if item else 0,
                    "notes": item.get("notes", "") if item else ""
                })
        
        # Create status timeline
        current_status = order.get("status", "pending") if order else "pending"
        status_timeline = [
            {"status": "pending", "text": "รับออเดอร์แล้ว", "completed": True},
            {"status": "confirmed", "text": "ยืนยันออเดอร์", "completed": current_status in ["confirmed", "preparing", "ready", "completed"]},
            {"status": "preparing", "text": "กำลังเตรียมอาหาร", "completed": current_status in ["preparing", "ready", "completed"]},
            {"status": "ready", "text": "เตรียมเสร็จแล้ว", "completed": current_status in ["ready", "completed"]},
            {"status": "completed", "text": "เสร็จสิ้น", "completed": current_status == "completed"}
        ]
        
        return {
            "order_number": order.get("order_number", "Unknown") if order else "Unknown",
            "status": order.get("status", "unknown") if order else "unknown",
            "customer_name": order.get("customer_name", "N/A") if order else "N/A",
            "customer_phone": order.get("customer_phone", "N/A") if order else "N/A",
            "total_amount": order.get("total_amount", 0) if order else 0, 
            "payment_status": order.get("payment_status", "unpaid") if order else "unpaid",
            "order_type": order.get("order_type", "pickup") if order else "pickup",
            "created_at": order.get("created_at", "") if order else "",
            "items": transformed_items,
            "status_history": status_timeline,
            "notes": order.get("notes", "") if order else ""
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting order status: {e}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to get order status: {str(e)}")

@router.patch("/{order_number}/status")
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