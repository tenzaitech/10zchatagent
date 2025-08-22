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
- **Current Status:** 🔧 MAJOR UPGRADE IN PROGRESS - Database V2 + Code Refactoring (Day 1/7)
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

## 🔧 DATABASE V2 + CODE REFACTORING PROJECT (7 Days)

### **🎯 MAJOR UPGRADE GOALS:**
1. **Database Optimization:** Payment system, indexes, audit trail, scalability
2. **Code Refactoring:** main.py (703 lines) → modular structure (< 200 lines/file)
3. **Zero Downtime Migration:** Dual-write strategy with instant rollback
4. **Performance:** 5-10x faster queries, 10,000 orders/day capacity

---

## **📅 DATABASE V2 ARCHITECTURE**

### **Core Design Principles:**
- **Event-Driven:** ทุก state change ถูก track ใน audit tables
- **Platform Agnostic:** รองรับ LINE/FB/IG/Web + future platforms  
- **Scalable by Design:** Indexes, partitioning, JSONB for flexibility
- **Payment-First:** Complete PromptPay QR + slip verification system
- **Zero Trust:** Full audit trail, รู้ว่าใครทำอะไรเมื่อไหร่

### **Database Schema V2:**
```sql
-- Core Tables (Enhanced)
customers:
  + platform_type, merged_from[], lifetime_value, tags
  + RENAME line_user_id → platform_id

orders:
  + branch_id, delivery_fee, discount_amount, net_amount
  + delivery_address (JSONB), completed_at, metadata (JSONB)

-- Transaction Tables (NEW)
payment_transactions:
  - Complete payment lifecycle (QR generation → verification)
  - Support PromptPay, cash, credit card, bank transfer
  - Slip upload + verification workflow

order_status_history:
  - Audit trail: who changed what when why
  - Track every status change with metadata

staff_actions:
  - Security audit: staff action logging
  - IP address, user agent tracking

-- Configuration Tables (NEW)  
settings:
  - Dynamic configuration (business hours, tax rate, etc.)
  - No code changes for config updates

branches: (Future)
  - Multi-branch support ready
```

### **Performance Indexes:**
```sql
-- Primary Performance
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_date_status ON orders(created_at::date, status);
CREATE INDEX idx_customers_platform ON customers(platform_id);
CREATE INDEX idx_payments_order_status ON payment_transactions(order_id, status);

-- Query Optimization  
CREATE INDEX idx_orders_pending ON orders(status) WHERE status IN ('pending','confirmed');
CREATE INDEX idx_orders_today ON orders(created_at) WHERE created_at::date = CURRENT_DATE;
```

---

## **🏗️ CODE ARCHITECTURE V2**

### **Current Problem:**
- main.py: **703 lines** (มากเกินไป 3.5 เท่า!)
- 16 endpoints ในไฟล์เดียว  
- Business logic ปนกับ routing
- ยากต่อการ test และ maintain

### **New Modular Structure:**
```
chatbot-api/
├── main.py (80-100 lines - app setup only)
├── routers/               (API routes)
│   ├── orders.py          (150 lines - order CRUD)
│   ├── webhooks.py        (100 lines - LINE webhook)  
│   ├── admin.py           (100 lines - admin pages)
│   ├── health.py          (50 lines - debug/health)
│   └── static.py          (50 lines - HTML serving)
├── services/              (Business logic)
│   ├── database_v2.py     (dual-write support)
│   ├── payment_service.py (QR generation, verification)
│   ├── notification_service.py (enhanced)
│   └── migration_service.py (data migration tools)
├── schemas/               (Pydantic models)
│   ├── order_schemas.py
│   ├── payment_schemas.py
│   └── customer_schemas.py
└── migrations/            (Database migration scripts)
    ├── 001_create_tables.sql
    ├── 002_add_indexes.sql
    └── rollback_scripts/
```

---

## **📅 MIGRATION TIMELINE**

### **DAY 1:** Documentation + Planning ✅ IN PROGRESS
- [🔄] Update CLAUDE.md with V2 architecture
- [ ] Update PROJECT-TODO.md with migration checklist
- [ ] Create migration folder structure

### **DAY 2-3:** Database Schema Creation
- [ ] Create new tables (payment_transactions, order_status_history, etc.)
- [ ] Add columns to existing tables (platform_type, metadata, etc.)
- [ ] Create performance indexes
- [ ] Setup RLS policies

### **DAY 4-5:** Code Refactoring  
- [ ] Create modular router structure
- [ ] Implement dual-write mechanism
- [ ] Create payment service with QR generation
- [ ] Migrate business logic to services/

### **DAY 6:** Testing & Validation
- [ ] Unit tests for all new functionality
- [ ] Integration tests for dual-write
- [ ] Performance benchmarking  
- [ ] Rollback procedure testing

### **DAY 7:** Switch & Production
- [ ] Switch to new schema (morning)
- [ ] Monitor performance (afternoon)  
- [ ] Cleanup old code (evening)

---

## **🛡️ ROLLBACK STRATEGY**
```bash
# Emergency rollback (< 1 minute)
./scripts/rollback_db.sh
git checkout ac92d46  # Checkpoint 2

# Feature flags for gradual rollout
MIGRATION_MODE=old|dual|new
```

---

## **✅ SUCCESS METRICS**
1. **Performance:** Query time 500ms → 100ms (80% improvement)
2. **Scalability:** 1,000 → 10,000 orders/day (10x capacity)
3. **Code Quality:** Files < 200 lines, Test coverage > 80%
4. **Zero Downtime:** ระบบทำงานตลอด migration
5. **Complete Payment:** QR generation + slip verification ready

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
