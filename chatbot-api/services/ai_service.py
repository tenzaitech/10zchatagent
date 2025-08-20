"""
AI service - OpenRouter AI and intent classification
Independent AI-related functions
"""
import httpx
from modules.config import OPENROUTER_API_KEY, FALLBACK_MESSAGE

async def get_ai_response(message: str, user_id: str = "") -> str:
    """Get AI response from OpenRouter for complex queries"""
    try:
        if not OPENROUTER_API_KEY:
            print("⚠️ OpenRouter API key not available, using fallback")
            return FALLBACK_MESSAGE
            
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://order.tenzaitech.online",
            "X-Title": "Tenzai Sushi Chatbot"
        }
        
        # System prompt สำหรับร้านอาหาร
        system_prompt = """คุณคือผู้ช่วยร้านอาหารญี่ปุ่น Tenzai Sushi 
- ตอบสั้นๆ กะทัดรัด ไม่เกิน 2-3 ประโยค
- พูดแบบเป็นมิตร ใช้ "ค่ะ/ครับ"
- ถ้าเกี่ยวกับเมนูหรือการสั่งอาหาร ให้แนะนำให้กด "สั่งอาหาร"
- ถ้าไม่เข้าใจคำถาม ให้ตอบว่า "ขออภัยค่ะ ไม่เข้าใจคำถาม ลองถามใหม่นะคะ"
- เวลาเปิด: 10:00-21:00 น. รับออเดอร์ล่าสุด 20:30 น.
- ที่อยู่: 123 ถนนสุขุมวิท แขวงคลองตัน เขตวัฒนา กรุงเทพฯ"""

        payload = {
            "model": "mistralai/mistral-7b-instruct:free",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            "max_tokens": 100,
            "temperature": 0.7
        }
        
        print(f"🤖 Asking AI: {message[:50]}...")
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
        if response.status_code == 200:
            data = response.json()
            ai_response = data["choices"][0]["message"]["content"].strip()
            print(f"✅ AI response: {ai_response[:50]}...")
            return ai_response
        else:
            print(f"❌ OpenRouter error: {response.status_code}")
            print(f"   Response: {response.text}")
            return FALLBACK_MESSAGE
            
    except httpx.TimeoutException:
        print("❌ AI request timeout")
        return FALLBACK_MESSAGE
    except Exception as e:
        print(f"❌ AI error: {e}")
        return FALLBACK_MESSAGE

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
    
    # Check for restaurant/food context
    restaurant_keywords = ["เมนู", "อาหาร", "food", "menu", "sushi", "ซูชิ", "ข้าว", "น้ำ", "ของหวาน", "ทานเข้า", "กิน"]
    if any(word in text for word in restaurant_keywords):
        return "menu"
    
    # Simple greeting
    if any(word in text for word in ["สวัสดี", "hello", "hi", "ครับ", "ค่ะ", "หวัดดี"]):
        return "greeting"
    
    # Complex questions for AI
    if len(text) > 15 and any(char in text for char in ["?", "ไหม", "มั้ย", "ได้ไหม", "อย่างไร", "ทำไม"]):
        return "ai_complex"
    
    # Default to AI for everything else
    return "ai_fallback"