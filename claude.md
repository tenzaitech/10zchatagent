# claude.md
# Role: Architecture & Progress (High-Level Overview)

> INSTRUCTION TO CLAUDE (read first)
- คุณคือสถาปนิกเอกสารระบบ หลีกเลี่ยงการเดาเกินข้อมูลจริง
- เติมเฉพาะ **เนื้อหาในหัวข้อที่มี TODO** และเคารพขอบเขตด้านล่าง
- ห้ามสร้างไฟล์ใหม่/รีเนมไฟล์/อ้างถึงระบบที่ไม่ได้อยู่ในสSCOPE
- ถ้าไม่มีข้อมูลเพียงพอ ให้ใส่ `TODO: <คำถามสั้น ๆ>`

## Project Snapshot (One-Pager)
- **Business Goal (3 บรรทัด):**  
  1) ลดภาระตอบลูกค้าด้วยตนเอง  2) ทำให้สั่งอาหารได้สะดวกผ่าน 1 URL  3) ลดขั้นตอนรับออร์เดอร์  
- **Channels:** LINE (primary), Facebook Messenger, Instagram DM  
- **Customer URL (หนึ่งเดียว):** `https://tenzai-order.ap.ngrok.io` (dev) → `https://tenzaionline.tech` (prod)
- **Stack:** Python FastAPI (API server), Supabase Free (DB/REST), ngrok (dev tunnel) → Render (production), OpenRouter (AI responses)
- **Current Status:** 🚀 90% Production Ready - Core features complete, payment integration pending
- **Core Principles:**  
  - Read (เมนู/หมวด/ตั้งค่า) ผ่าน **anon key + RLS SELECT-only**  
  - Write (orders/order_items/customers/conversations) ผ่าน **FastAPI + service role** เท่านั้น  
  - ตรวจ **webhook signatures** ทุกครั้ง
  - **Multi-platform customer identity** ด้วย phone-based merging

## Architecture (Text Diagram)
```
LINE / FB / IG  →  ngrok tunnel (webhooks)
                 →  FastAPI (Python API server)
                 →  Supabase (public SELECT; server WRITE)
                 ↘  OpenRouter (AI/FAQ responses)
WebOrder (1 URL) →  SELECT (menus/categories/settings) via anon+RLS
                 →  Checkout → FastAPI (/api/orders/create) → Supabase → LINE Push Notify
                 →  Order Tracking → real-time status page
```

## Decision Log (Key Choices)
- [Decided] ใช้ **Hybrid**: แชทพาเข้าหน้า WebOrder เดียว (Deep linking) + fallback chat-only ถ้าเปิดลิงก์ไม่ได้  
- [Decided] CLIENT อ่าน public เฉพาะ 3 ตาราง; การเขียนทั้งหมดวิ่งผ่าน FastAPI+service role  
- [Decided] เก็บ `conversations` แบบ **summary สั้น** เพื่อลดขนาดบน Free plan
- [Decided] **Platform ID System**: `LINE_{user_id}`, `FB_{user_id}`, `WEB_{phone}` สำหรับ multi-platform customer management
- [Decided] **งดใช้ n8n** เปลี่ยนเป็น **Python FastAPI** เพื่อความเร็วและ memory efficiency

## Business Impact (Expected Results)
🎯 **Primary Goals Achievement:**
1) **ลดเวลาตอบลูกค้า 80%** (จาก 5 นาที เหลือ 1 นาที)
2) **รับออเดอร์ได้ 24/7** แม้พนักงานไม่อยู่  
3) **ไม่พลาดออเดอร์** เพราะมี notification หลายช่องทาง
4) **ลูกค้าจ่ายเงินง่าย** ผ่าน QR Code PromptPay
5) **ติดตามออเดอร์ real-time** ลูกค้าไม่ต้องถาม

## Risks & Mitigations (Production Focus)
1) **Staff ไม่เห็น notification** → หลาย channel: LINE + Dashboard + Email backup
2) **Payment QR ไม่ทำงาน** → Fallback เป็น manual transfer + phone notification  
3) **Production server ล่ม** → Monitor + auto-restart + backup ngrok tunnel
4) **Database quota เต็ม** → Daily cleanup + archive old data + upgrade plan
5) **LINE webhook หยุด** → Health check endpoint + retry mechanism

## Progress (Status)
- Infra / DB / Admin / WebApp: ✅ พร้อมใช้งาน
- Multi-Platform Customer Management: ✅ เสร็จสมบูรณ์
- Order Confirmation System: ✅ เสร็จสมบูรณ์ (LINE Push + Tracking)
- Real-time Order Tracking: ✅ เสร็จสมบูรณ์ (Fixed 100% working)
- Deep Linking & UX Flow: ✅ เสร็จสมบูรณ์
- Staff Orders Dashboard: ✅ เสร็จสมบูรณ์ (Fixed timezone + API endpoint issues)
- Staff Notification Service: ✅ เสร็จสมบูรณ์ (รอ config STAFF_LINE_ID เท่านั้น)
- **Last Updated:** 21 สิงหาคม 2025
- **% Completion (rough):** Infra 100 / DB 100 / WebApp 100 / Chatbot 95 / Staff System 80 / Payment 0 / Production 0

## Next Tasks (Measurable)
### Phase 1: Core Chatbot ✅ COMPLETED
- [x] WF-A: รับข้อความ + ปุ่ม "สั่งอาหาร" (เปิด webview) + ตอบ FAQ + AI responses
- [x] WF-B: รับ order จาก WebOrder → validate → write DB → notify customer
- [x] ตั้ง RLS read-only 3 ตาราง + ปิดการเขียน anon ทุกตาราง write
- [x] Multi-platform customer identity system (LINE/FB/IG/Web)
- [x] Deep linking with pre-filled customer data

### Phase 2: Enhanced Features ✅ COMPLETED
- [x] Order status tracking + notification ลูกค้า (Real-time page + LINE push)
- [x] Order confirmation with Flex Message UI
- [x] Platform-aware customer management
- [x] Error handling + retry logic สำหรับ failed orders

## 🚀 PRODUCTION READY PLAN (5 Days)

### Phase 3: Critical Features for Go-Live
**Priority 1 (Days 1-2):** Payment Integration 💳 - CRITICAL FOR REVENUE
- [ ] QR Code PromptPay generation library integration
- [ ] Payment proof upload system
- [ ] Auto-generate QR in order confirmation
- [ ] Payment status tracking and verification
- [ ] Payment slip validation API

**Priority 2 (Day 3):** Staff System Configuration ⚡
- [x] Staff orders dashboard (/webappadmin/staff-orders.html) ✅ COMPLETED
- [x] Staff LINE notification system ✅ COMPLETED (service ready)
- [ ] Configure STAFF_LINE_ID in production environment
- [ ] Test staff notification flow end-to-end
- [ ] Setup backup notification channels

**Priority 3 (Day 4):** Production Deployment - Supabase + Render 🌐
- [ ] Prepare Code for Production
  - Create requirements.txt
  - Update main.py for Render (PORT environment variable)
  - Add keep-alive mechanism (prevent sleep)
  - Test all endpoints locally

- [ ] Deploy to Render (Free 750 hours/month)
  - Connect GitHub repository to Render
  - Configure build: pip install -r requirements.txt
  - Configure start: python chatbot-api/main.py
  - Set environment variables (Supabase keys, LINE tokens)
  - Deploy and verify

- [ ] Setup Custom Domain: tenzaionline.tech
  - Add custom domain in Render dashboard
  - Configure DNS CNAME records
  - Verify SSL certificate (automatic)

- [ ] Optimize Database Performance
  - Enable Supabase connection pooling
  - Create performance indexes
  - Verify RLS policies

- [ ] Update LINE Webhook
  - Change webhook URL to: tenzaionline.tech/webhook/line
  - Test webhook functionality

**Priority 4 (Day 5):** Testing & Monitoring 🔧
- [ ] Load testing (100 concurrent orders)
- [ ] Error recovery testing
- [ ] Admin login system + password protection
- [ ] Daily database backup automation
- [ ] Uptime monitoring setup (UptimeRobot)

### Phase 4: Future Enhancements (After Launch)
- [ ] Facebook/Instagram webhook implementation
- [ ] Basic analytics dashboard
- [ ] Multi-branch support
- [ ] Advanced AI features

## Production Stack Decision
🎯 **Final Architecture: Supabase + Render**
- **Database:** Supabase Free (500MB) - Real-time, RLS, Auto-backup
- **Backend:** Render Free (750 hours/month) - Python FastAPI native
- **Domain:** tenzaionline.tech - Custom domain with auto SSL
- **Cost:** $0/month - 100% free tier combination

🔥 **Why This Priority Order:**
1. **Payment = รายได้** - ยิ่งจ่ายง่าย ยิ่งสั่งเยอะ (ทำให้มีรายได้ทันที)
2. **Staff system = ดำเนินการ** - dashboard เสร็จแล้ว เหลือแค่ config
3. **Production = เสถียร** - Single domain, professional hosting  
4. **Monitoring = ความมั่นใจ** - รู้ทันทีเมื่อระบบล่ม

⚠️ **สิ่งที่ไม่ทำตอนนี้:**
- ❌ Facebook/Instagram integration (ใช้ LINE ก่อน ค่อยขยาย)
- ❌ Complex AI features (FAQ พอ ประหยัด cost)  
- ❌ Multi-branch support (ร้านเดียวก่อน scale ทีหลัง)
- ❌ Code refactoring (ทำหลัง production แล้ว)

## Guardrails (Do / Don't)
- **Do:** เน้น features ที่ส่งผลต่อรายได้ทันที, ทดสอบทุก feature ก่อน deploy
- **Don't:** เพิ่ม feature ที่ซับซ้อน / เปลี่ยนโครงสร้างหลัก / ใช้ resource เกิน Free plan
