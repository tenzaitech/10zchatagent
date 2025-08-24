"""
Configuration module - Environment variables and constants
Safe to import without dependencies
"""
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qlhpmrehrmprptldtchb.supabase.co")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")
STAFF_LINE_ID = os.getenv("STAFF_LINE_ID", "")  # Staff LINE user ID for notifications
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
PORT = int(os.getenv("PORT", 8000))

# FAQ Responses
FAQ_RESPONSES = {
    "hours": "🕙 เปิดให้บริการทุกวัน 10:00-21:00 น.\n📋 รับออเดอร์ล่าสุด 20:30 น.",
    "location": "📍 123 ถนนสุขุมวิท แขวงคลองตัน เขตวัฒนา กรุงเทพฯ 10110\n📞 02-xxx-xxxx",
    "menu": "🍜 ดูเมนูและราคาทั้งหมดได้ที่หน้าสั่งอาหาร\nหรือกดปุ่ม 'สั่งอาหาร' ด้านล่าง",
    "payment": "💳 รับชำระ: เงินสด/โอนเงิน/พร้อมเพย์\n📷 ส่งสลิปในแชทหลังสั่งเสร็จนะคะ",
    "order": "🛒 สั่งอาหารออนไลน์ได้ที่ลิงก์ด้านล่าง\nหรือกดปุ่ม 'สั่งอาหาร' เลยค่ะ"
}

FALLBACK_MESSAGE = "ขออภัยค่ะ ไม่เข้าใจคำถาม 🤔\nลองถามใหม่หรือกด 'สั่งอาหาร' เลยนะคะ 😊"

# Validation
required_vars = {
    "SUPABASE_URL": SUPABASE_URL,
    "SUPABASE_SERVICE_ROLE_KEY": SUPABASE_SERVICE_KEY,
    "LINE_CHANNEL_ACCESS_TOKEN": LINE_CHANNEL_ACCESS_TOKEN,
    "LINE_CHANNEL_SECRET": LINE_CHANNEL_SECRET,
}

def validate_config():
    """Validate required environment variables"""
    missing_vars = [key for key, value in required_vars.items() if not value]
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    return True

# Auto-validate on import
if validate_config():
    print("✅ Configuration loaded successfully")
    if OPENROUTER_API_KEY:
        print("✅ OpenRouter API key available")
    else:
        print("⚠️ OpenRouter API key not set (AI features disabled)")
else:
    print("❌ Configuration validation failed")