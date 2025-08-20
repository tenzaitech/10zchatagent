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
- **Channels:** LINE, Facebook Messenger, Instagram DM  
- **Customer URL (หนึ่งเดียว):** `https://order.tenzaitech.online`
- **Stack:** Python FastAPI (API server), Supabase Free (DB/REST), ngrok (webhook tunnel), OpenRouter (AI responses)
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

## Risks & Mitigations (Top-5)
1) **Supabase Free pause / quota** → ตั้ง health-ping เบา ๆ + สรุปแชทแทนเก็บยาว  
2) **Webhook abuse** → ลายเซ็น + timestamp + rate limit ที่ n8n  
3) **ราคาไม่ตรง** จากหน้าเว็บ → n8n re-price จาก DB ก่อนสร้าง order ทุกครั้ง  
4) **n8n workflow หยุดทำงาน** → monitor health endpoint + auto-restart + backup notification channel  
5) **OpenRouter API limit/cost** → set max tokens + fallback basic responses + usage tracking

## Progress (Status)
- Infra / DB / Admin / WebApp: ✅ พร้อมใช้งาน
- Multi-Platform Customer Management: ✅ เสร็จสมบูรณ์
- Order Confirmation System: ✅ เสร็จสมบูรณ์ (LINE Push + Tracking)
- Real-time Order Tracking: ✅ เสร็จสมบูรณ์
- Deep Linking & UX Flow: ✅ เสร็จสมบูรณ์
- **Last Updated:** 20 สิงหาคม 2025
- **% Completion (rough):** Infra 100 / DB 100 / WebApp 100 / Chatbot 85 / Core Features 90

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

### Phase 3: Remaining Tasks (Optional)
- [ ] Staff notification system (LINE push to staff)
- [ ] Admin dashboard สำหรับดู orders real-time
- [ ] Facebook/Instagram webhook implementation
- [ ] Basic analytics: orders/day, popular items
- [ ] Payment integration (QR Code/PromptPay)

### Phase 3: Production Ready (Week 3)
- [ ] Load testing + performance optimization
- [ ] Backup/disaster recovery plan
- [ ] Monitor + alerting setup (health checks)
- [ ] Documentation + handover materials

## Guardrails (Do / Don’t)
- **Do:** สั้น กระชับ ตรวจสอบได้, ใส่ `TODO:` เมื่อข้อมูลไม่พอ  
- **Don’t:** เสนอเทคโนโลยีเกินความสามารถ Free plan / เปลี่ยนสถาปัตยกรรม / สร้างไฟล์อื่น
