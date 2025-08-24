"""
Shared Database Models and Types
Common data structures used by both chatbot and order services
"""
from typing import Dict, List, Optional
from enum import Enum

# Order Status Enum
class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# Payment Status Enum  
class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"

# Payment Method Enum
class PaymentMethod(str, Enum):
    CASH = "cash"
    CARD = "card"
    QR = "qr"
    BANK_TRANSFER = "bank_transfer"

# Order Type Enum
class OrderType(str, Enum):
    PICKUP = "pickup"
    DELIVERY = "delivery"

# Platform Enum
class Platform(str, Enum):
    LINE = "LINE"
    WEB = "WEB"
    FACEBOOK = "FB"
    INSTAGRAM = "IG"

# Intent Classification Types
class IntentType(str, Enum):
    GREETING = "greeting"
    HOURS = "hours" 
    LOCATION = "location"
    MENU = "menu"
    PAYMENT = "payment"
    ORDER = "order"
    AI_COMPLEX = "ai_complex"
    AI_FALLBACK = "ai_fallback"

# Common database record structures
class CustomerRecord:
    def __init__(self, data: Dict):
        self.id = data.get('id')
        self.name = data.get('name')
        self.phone = data.get('phone')
        self.platform = data.get('platform', 'WEB')
        self.created_at = data.get('created_at')

class OrderItemRecord:
    def __init__(self, data: Dict):
        self.id = data.get('id')
        self.name = data.get('name')
        self.quantity = data.get('quantity', 1)
        self.price = data.get('price', 0)
        self.unit_price = data.get('unit_price', 0)
        self.total_price = data.get('total_price', 0)
        self.notes = data.get('notes')

class OrderRecord:
    def __init__(self, data: Dict):
        self.id = data.get('id')
        self.order_number = data.get('order_number')
        self.customer_id = data.get('customer_id')
        self.customer_name = data.get('customer_name')
        self.customer_phone = data.get('customer_phone')
        self.status = data.get('status', OrderStatus.PENDING)
        self.order_type = data.get('order_type', OrderType.PICKUP)
        self.payment_method = data.get('payment_method', PaymentMethod.CASH)
        self.payment_status = data.get('payment_status', PaymentStatus.PENDING)
        self.total_amount = data.get('total_amount', 0)
        self.notes = data.get('notes')
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
        self.items = [OrderItemRecord(item) for item in data.get('items', [])]

# FAQ responses mapping
FAQ_RESPONSES = {
    "hours": "🕙 เปิดให้บริการทุกวัน 10:00-21:00 น. รับออเดอร์ล่าสุด 20:30 น.ค่ะ",
    "location": "📍 123 ถนนสุขุมวิท แขวงคลองตัน เขตวัฒนา กรุงเทพฯ ค่ะ",
    "payment": "💳 รับชำระ: เงินสด/โอนเงิน/พร้อมเพย์ค่ะ ส่งสลิปในแชทหลังสั่งเสร็จนะคะ",
    "menu": "🍜 ดูเมนูและราคาทั้งหมดได้ที่หน้าสั่งอาหารค่ะ หรือกดปุ่ม 'สั่งอาหาร' ด้านล่างเลย",
    "order": "🛒 สั่งอาหารออนไลน์ได้ที่ลิงก์ด้านล่างค่ะ หรือกดปุ่ม 'สั่งอาหาร' เลย",
    "greeting": "สวัสดีค่ะ! ยินดีต้อนรับสู่ Tenzai Sushi 🍣 มีอะไรให้ช่วยไหมคะ?"
}

# Common validation functions
def validate_phone_number(phone: str) -> bool:
    """Validate Thai phone number format"""
    import re
    # Thai mobile patterns: 08x-xxx-xxxx, 09x-xxx-xxxx, 06x-xxx-xxxx
    pattern = r'^0[689]\d{8}$'
    return bool(re.match(pattern, phone.replace('-', '').replace(' ', '')))

def format_phone_number(phone: str) -> str:
    """Format phone number consistently"""
    clean = phone.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
    if len(clean) == 10 and clean.startswith('0'):
        return clean
    return phone  # Return as-is if doesn't match expected format

def generate_order_number() -> str:
    """Generate unique order number"""
    import uuid
    import time
    timestamp = int(time.time())
    short_uuid = str(uuid.uuid4())[:8]
    return f"T{timestamp}{short_uuid}".upper()

# Common response templates
def create_line_text_message(text: str) -> Dict:
    """Create LINE text message format"""
    return {"type": "text", "text": text}

def create_line_button_message(text: str, actions: List[Dict]) -> Dict:
    """Create LINE button template message"""
    return {
        "type": "template",
        "altText": text,
        "template": {
            "type": "buttons",
            "text": text,
            "actions": actions
        }
    }