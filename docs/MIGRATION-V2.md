# 🔧 DATABASE V2 + CODE REFACTORING PROJECT (7 Days)

## **🎯 MAJOR UPGRADE GOALS:**
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