"""
AI service - OpenRouter AI and intent classification
Independent AI-related functions
"""
import httpx
from config import OPENROUTER_API_KEY, FALLBACK_MESSAGE

async def get_ai_response(message: str, user_id: str = "") -> str:
    """Get AI response from Claude 3.5 Sonnet with fallback"""
    
    # Check if API key is available and valid
    if not OPENROUTER_API_KEY or "invalid" in OPENROUTER_API_KEY.lower():
        print("⚠️ OpenRouter API key not valid, using smart fallback")
        return _get_smart_fallback(message)
    
    # Try Claude 3.5 Sonnet first
    try:
        response = await _call_claude_sonnet(message)
        if response:
            return response
    except Exception as e:
        print(f"❌ Claude Sonnet failed: {e}")
        if "401" in str(e) or "User not found" in str(e):
            print("⚠️ API key appears invalid, switching to smart fallback")
            return _get_smart_fallback(message)
    
    # Fallback to Mistral Free
    try:
        response = await _call_mistral_free(message)
        if response:
            return response
    except Exception as e:
        print(f"❌ Mistral fallback failed: {e}")
        if "401" in str(e):
            print("⚠️ API access issues, using smart fallback")
            return _get_smart_fallback(message)
    
    # Final fallback
    return _get_smart_fallback(message)

def _get_smart_fallback(message: str) -> str:
    """Intelligent fallback when AI is unavailable"""
    text = message.lower()
    
    # Smart pattern matching for common queries
    if any(word in text for word in ["สวัสดี", "hello", "hi", "หวัดดี"]):
        return "สวัสดีค่ะ! ยินดีต้อนรับสู่ Tenzai Sushi 🍣 มีอะไรให้ช่วยไหมคะ?"
    
    elif any(word in text for word in ["เวลา", "เปิด", "ปิด", "โมง", "กี่โมง"]):
        return "🕙 เปิดให้บริการทุกวัน 10:00-21:00 น. รับออเดอร์ล่าสุด 20:30 น.ค่ะ"
    
    elif any(word in text for word in ["เมนู", "ราคา", "อาหาร", "ดู"]):
        return "🍜 ดูเมนูและราคาทั้งหมดได้ที่หน้าสั่งอาหารค่ะ หรือกดปุ่ม 'สั่งอาหาร' ด้านล่างเลย"
    
    elif any(word in text for word in ["ที่อยู่", "address", "อยู่ไหน"]):
        return "📍 123 ถนนสุขุมวิท แขวงคลองตัน เขตวัฒนา กรุงเทพฯ ค่ะ"
    
    elif any(word in text for word in ["ชำระ", "จ่าย", "โอน", "เงิน"]):
        return "💳 รับชำระ: เงินสด/โอนเงิน/พร้อมเพย์ค่ะ ส่งสลิปในแชทหลังสั่งเสร็จนะคะ"
    
    elif any(word in text for word in ["สั่ง", "order", "ออเดอร์"]):
        return "🛒 สั่งอาหารออนไลน์ได้ที่ลิงก์ด้านล่างค่ะ หรือกดปุ่ม 'สั่งอาหาร' เลย"
    
    else:
        return "ขออภัยค่ะ ตอนนี้ระบบ AI กำลังปรับปรุง 🔧 ลองถามใหม่หรือกด 'สั่งอาหาร' ด้านล่างนะคะ 😊"

async def _call_claude_sonnet(message: str) -> str:
    """Call Claude 3.5 Sonnet (primary AI)"""
    if not OPENROUTER_API_KEY:
        raise Exception("OpenRouter API key not available")
        
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://order.tenzaitech.online",
        "X-Title": "Tenzai Sushi Chatbot"
    }
    
    # Enhanced system prompt for Claude 4 Sonnet
    system_prompt = """คุณคือผู้ช่วยร้าน Tenzai Sushi ร้านอาหารญี่ปุ่น
ความรู้ร้าน:
- เมนูเด่น: ซูชิ ซาชิมิ ราเมน ปลาไหลย่าง ข้าวหน้าต่างๆ
- เวลาเปิด: 10:00-21:00 ทุกวัน รับออเดอร์ล่าสุด 20:30
- คุณภาพ: วัตถุดิบสด อร่อย คุ้มค่า

วิธีตอบ:
- ตอบสั้น 1-2 ประโยค ภาษาสุภาพ ใช้ค่ะ
- ถ้าถามเกี่ยวกับอาหาร ตอบด้วยความกระตือรือร้น
- ส่งท้ายด้วยแนะนำให้กดปุ่ม "สั่งอาหาร" เพื่อดูเมนู"""

    payload = {
        "model": "anthropic/claude-sonnet-4",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ],
        "max_tokens": 800,
        "temperature": 0.3
    }
    
    print(f"🤖 Claude Sonnet: {message[:50]}...")
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
    if response.status_code == 200:
        data = response.json()
        ai_response = data["choices"][0]["message"]["content"].strip()
        print(f"✅ Claude response: {ai_response[:50]}...")
        return ai_response
    elif response.status_code == 429:
        raise Exception(f"Rate limit (429)")
    else:
        raise Exception(f"HTTP {response.status_code}: {response.text}")

async def _call_mistral_free(message: str) -> str:
    """Fallback to Mistral Free model"""
    if not OPENROUTER_API_KEY:
        return FALLBACK_MESSAGE
        
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://order.tenzaitech.online",
        "X-Title": "Tenzai Sushi Chatbot"
    }
    
    system_prompt = """คุณคือผู้ช่วยร้าน Tenzai Sushi - ตอบสั้นๆ ใช้ค่ะ/ครับ เวลาเปิด 10:00-21:00"""

    payload = {
        "model": "mistralai/mistral-7b-instruct:free",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ],
        "max_tokens": 80,
        "temperature": 0.5
    }
    
    print(f"🔄 Mistral fallback: {message[:30]}...")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
    if response.status_code == 200:
        data = response.json()
        ai_response = data["choices"][0]["message"]["content"].strip()
        print(f"✅ Mistral response: {ai_response[:30]}...")
        return ai_response
    else:
        raise Exception(f"HTTP {response.status_code}")

def classify_intent(message_text: str) -> str:
    """Smart intent classification - FAQ vs AI vs Order"""
    text = message_text.lower()
    
    # FAQ patterns (high confidence)
    if any(word in text for word in ["เวลา", "เปิด", "ปิด", "โมง", "hours", "กี่โมง"]):
        return "hours"
    elif any(word in text for word in ["ที่อยู่", "แอดเดรส", "location", "address", "อยู่ไหน", "ที่ไหน"]):
        return "location"
    elif any(word in text for word in ["ราคา", "เท่าไร", "price", "cost", "กี่บาท"]):
        return "menu"
    elif any(word in text for word in ["ชำระ", "จ่าย", "payment", "pay", "โอน", "เงิน"]):
        return "payment"
    elif any(word in text for word in ["สั่ง", "order", "โอเดอร์", "สั่งอาหาร"]):
        return "order"
    
    # Complex questions for AI (check before menu to catch food questions)
    if any(char in text for char in ["?", "ไหม", "มั้ย", "ได้ไหม", "อย่างไร", "ทำไม"]) and len(text) >= 8:
        return "ai_complex"
    
    # Check for restaurant/food context
    restaurant_keywords = ["เมนู", "อาหาร", "food", "menu", "sushi", "ซูชิ", "ข้าว", "น้ำ", "ของหวาน", "ทานเข้า", "กิน"]
    if any(word in text for word in restaurant_keywords):
        return "menu"
    
    # Simple greeting
    if any(word in text for word in ["สวัสดี", "hello", "hi", "ครับ", "ค่ะ", "หวัดดี"]):
        return "greeting"
    
    # Default to AI for everything else
    return "ai_fallback"