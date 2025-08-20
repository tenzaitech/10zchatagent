"""
Notification service - Order confirmations and notifications
Uses line_service for sending messages
"""
from services.line_service import send_line_push_message

async def send_staff_notification(order_number: str, customer_name: str, customer_phone: str, 
                                 total_amount: float, items: list):
    """Send order notification to staff LINE group/account"""
    try:
        print(f"📢 Sending staff notification for order: {order_number}")
        
        # Get staff LINE ID from environment variables
        from modules.config import STAFF_LINE_ID
        
        if not STAFF_LINE_ID:
            print("⚠️ STAFF_LINE_ID not configured in environment - skipping staff notification")
            print("💡 Add STAFF_LINE_ID='your_staff_line_user_id' to .env file")
            return
        
        # Create staff notification message
        items_text = ""
        for item in items:
            items_text += f"• {item.get('name', 'Unknown')} x{item.get('quantity', 1)} ({item.get('total_price', 0):.0f}฿)\n"
        
        staff_message = {
            "type": "flex",
            "altText": f"🚨 ออเดอร์ใหม่ #{order_number}",
            "contents": {
                "type": "bubble",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "🚨 ออเดอร์ใหม่เข้ามา!",
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
                                {"type": "text", "text": "ลูกค้า:", "size": "sm", "color": "#666666", "flex": 2},
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
                            "text": "รายการอาหาร:",
                            "size": "sm",
                            "weight": "bold",
                            "margin": "lg"
                        },
                        {
                            "type": "text",
                            "text": items_text.strip(),
                            "size": "xs",
                            "color": "#666666",
                            "wrap": True
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "button",
                            "action": {
                                "type": "postback",
                                "label": "✅ รับออเดอร์",
                                "data": f"action=accept_order&order={order_number}"
                            },
                            "style": "primary",
                            "color": "#28a745"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "postback",
                                "label": "❌ ปฏิเสธ",
                                "data": f"action=reject_order&order={order_number}"
                            },
                            "style": "secondary"
                        }
                    ],
                    "spacing": "sm"
                }
            }
        }
        
        # Send to staff
        messages = [staff_message]
        success = await send_line_push_message(STAFF_LINE_ID, messages)
        
        if success:
            print(f"✅ Staff notification sent for order {order_number}")
        else:
            print(f"⚠️ Failed to send staff notification for order {order_number}")
            
    except Exception as e:
        print(f"❌ Error sending staff notification: {e}")

async def send_order_confirmation(order_number: str, customer_phone: str, customer_name: str, 
                                platform: str, platform_user_id: str, total_amount: float, items_count: int, items_list: list = None):
    """Send order confirmation to customer via appropriate platform"""
    try:
        print(f"🔔 Sending order confirmation: {order_number} to {platform}_{platform_user_id}")
        
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