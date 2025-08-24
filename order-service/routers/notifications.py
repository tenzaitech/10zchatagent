"""
Order Notifications Router
Handles order status notifications to staff via LINE
Includes order accept/reject postback handling (moved from chatbot)
"""

import json
import sys
import os
from fastapi import APIRouter, Request, HTTPException

# Add shared modules to path
shared_path = os.path.join(os.path.dirname(__file__), "..", "..", "shared-modules")
sys.path.insert(0, shared_path)

# Import shared modules
from database import supabase_request

# Import notification service
from services.notification_service import send_staff_notification

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

@router.post("/order-status")
async def notify_order_status(order_data: dict):
    """Send order status notification to staff"""
    try:
        order_number = order_data.get("order_number")
        status = order_data.get("status")
        
        if not order_number or not status:
            raise HTTPException(status_code=400, detail="Missing order_number or status")
        
        # Send notification to staff LINE group
        success = await send_staff_notification(order_data)
        
        if success:
            return {"status": "sent", "order_number": order_number}
        else:
            return {"status": "failed", "order_number": order_number}
            
    except Exception as e:
        print(f"❌ Notification error: {e}")
        raise HTTPException(status_code=500, detail="Notification failed")

@router.post("/postback")
async def handle_postback(request: Request):
    """Handle LINE postback events for order accept/reject"""
    try:
        # This endpoint receives order accept/reject postbacks from staff
        body = await request.body()
        postback_data = json.loads(body.decode('utf-8'))
        
        # TODO: Implement postback handling
        print(f"📞 Postback received: {postback_data}")
        return {"status": "received", "message": "Postback handling not yet implemented"}
        
    except Exception as e:
        print(f"❌ Postback error: {e}")
        raise HTTPException(status_code=500, detail="Postback processing failed")

@router.get("/")
async def notifications_info():
    """Notifications service info"""
    return {
        "service": "order-notifications",
        "description": "Handles order status notifications and staff responses",
        "endpoints": {
            "/api/notifications/order-status": "Send order status notification",
            "/api/notifications/postback": "Handle staff postback responses"
        }
    }