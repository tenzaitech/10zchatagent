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
- **Stack:** n8n (orchestrator), Supabase Free (DB/REST), Cloudflare Tunnel (webhook), OpenRouter (FAQ optional)
- **Core Principles:**  
  - Read (เมนู/หมวด/ตั้งค่า) ผ่าน **anon key + RLS SELECT-only**  
  - Write (orders/order_items/customers/conversations) ผ่าน **n8n + service role** เท่านั้น  
  - ตรวจ **webhook signatures** ทุกครั้ง

## Architecture (Text Diagram)
```
LINE / FB / IG  →  Cloudflare Tunnel (webhooks)
                 →  n8n (router + business logic)
                 →  Supabase (public SELECT; server WRITE)
                 ↘  OpenRouter (FAQ/intent – optional)
WebOrder (1 URL) →  SELECT (menus/categories/settings) via anon+RLS
                 →  Checkout → n8n (/orders/create) → Supabase → Notify staff
```

## Decision Log (Key Choices)
- [Decided] ใช้ **Hybrid**: แชทพาเข้าหน้า WebOrder เดียว (LIFF/Messenger Webview) + fallback chat-only ถ้าเปิดลิงก์ไม่ได้  
- [Decided] CLIENT อ่าน public เฉพาะ 3 ตาราง; การเขียนทั้งหมดวิ่งผ่าน n8n+service role  
- [Decided] เก็บ `conversations` แบบ **summary สั้น** เพื่อลดขนาดบน Free plan

## Risks & Mitigations (Top-5)
1) **Supabase Free pause / quota** → ตั้ง health-ping เบา ๆ + สรุปแชทแทนเก็บยาว  
2) **Webhook abuse** → ลายเซ็น + timestamp + rate limit ที่ n8n  
3) **ราคาไม่ตรง** จากหน้าเว็บ → n8n re-price จาก DB ก่อนสร้าง order ทุกครั้ง  
4) **n8n workflow หยุดทำงาน** → monitor health endpoint + auto-restart + backup notification channel  
5) **OpenRouter API limit/cost** → set max tokens + fallback basic responses + usage tracking

## Progress (Status)
- Infra / DB / Admin / WebApp: ✅ พร้อมใช้งาน (จากข้อมูลล่าสุดของโปรเจกต์)
- Chatbot Workflow (WF-A, WF-B): ⏳ รอ implement / import flow
- **Last Updated:** 18 สิงหาคม 2025
- **% Completion (rough):** Infra 100 / DB 100 / Admin 100 / WebApp 100 / Chatbot 0

## Next Tasks (Measurable)
### Phase 1: Core Chatbot (Week 1)
- [ ] WF-A: รับข้อความ + ปุ่ม "สั่งอาหาร" (เปิด webview) + ตอบ FAQ 3 หัวข้อ
- [ ] WF-B: รับ order จาก WebOrder → validate → write DB → notify staff
- [ ] ตั้ง RLS read-only 3 ตาราง + ปิดการเขียน anon ทุกตาราง write
- [ ] Test webhook signatures สำหรับ LINE/FB/IG

### Phase 2: Enhanced Features (Week 2)
- [ ] Order status tracking + notification ลูกค้า
- [ ] Admin dashboard สำหรับดู orders real-time
- [ ] Basic analytics: orders/day, popular items
- [ ] Error handling + retry logic สำหรับ failed orders

### Phase 3: Production Ready (Week 3)
- [ ] Load testing + performance optimization
- [ ] Backup/disaster recovery plan
- [ ] Monitor + alerting setup (health checks)
- [ ] Documentation + handover materials

## Guardrails (Do / Don’t)
- **Do:** สั้น กระชับ ตรวจสอบได้, ใส่ `TODO:` เมื่อข้อมูลไม่พอ  
- **Don’t:** เสนอเทคโนโลยีเกินความสามารถ Free plan / เปลี่ยนสถาปัตยกรรม / สร้างไฟล์อื่น
