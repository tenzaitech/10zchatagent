# 🏗️ System Architecture

## Architecture Overview
```
LINE / FB / IG  →  ngrok tunnel (webhooks)
                 →  FastAPI (Python API server)
                 →  Supabase (public SELECT; server WRITE)
                 ↘  OpenRouter (AI/FAQ responses)
WebOrder (1 URL) →  SELECT (menus/categories/settings) via anon+RLS
                 →  Checkout → FastAPI (/api/orders/create) → Supabase → LINE Push Notify
                 →  Order Tracking → real-time status page
```

## Technology Stack
- **Backend:** Python FastAPI (API server)
- **Database:** Supabase Free (DB/REST) 
- **Development:** ngrok (dev tunnel) 
- **Production:** Render (hosting)
- **AI:** OpenRouter (AI responses)
- **Messaging:** LINE, Facebook Messenger, Instagram DM
- **Customer URL:** `https://tenzai-order.ap.ngrok.io` (dev) → `https://tenzaionline.tech` (prod)

## Core Principles
- **Read Strategy:** เมนู/หมวด/ตั้งค่า ผ่าน **anon key + RLS SELECT-only**  
- **Write Strategy:** orders/order_items/customers/conversations ผ่าน **FastAPI + service role** เท่านั้น  
- **Security:** ตรวจ **webhook signatures** ทุกครั้ง
- **Identity:** **Multi-platform customer identity** ด้วย phone-based merging

## Production Stack Decision
🎯 **Final Architecture: Supabase + Render**
- **Database:** Supabase Free (500MB) - Real-time, RLS, Auto-backup
- **Backend:** Render Free (750 hours/month) - Python FastAPI native
- **Domain:** tenzaionline.tech - Custom domain with auto SSL
- **Cost:** $0/month - 100% free tier combination

## Decision Log (Key Choices)
- [Decided] ใช้ **Hybrid**: แชทพาเข้าหน้า WebOrder เดียว (Deep linking) + fallback chat-only ถ้าเปิดลิงก์ไม่ได้  
- [Decided] CLIENT อ่าน public เฉพาะ 3 ตาราง; การเขียนทั้งหมดวิ่งผ่าน FastAPI+service role  
- [Decided] เก็บ `conversations` แบบ **summary สั้น** เพื่อลดขนาดบน Free plan
- [Decided] **Platform ID System**: `LINE_{user_id}`, `FB_{user_id}`, `WEB_{phone}` สำหรับ multi-platform customer management
- [Decided] **งดใช้ n8n** เปลี่ยนเป็น **Python FastAPI** เพื่อความเร็วและ memory efficiency