# 📋 PROJECT TODO LIST

> **Project:** Tenzai Sushi Chatbot - Production Ready
> **Stack:** Supabase + Render + LINE Messaging API  
> **Domain:** tenzaionline.tech
> **Status:** Development → Production Deployment

---

## 🔧 CURRENT SPRINT: DATABASE V2 + CODE REFACTORING (Day 1/7)

### ✅ COMPLETED (Status: DONE)
- [x] **Core Infrastructure** - FastAPI, Supabase, LINE webhook
- [x] **Order System** - Create orders, order tracking, customer management  
- [x] **Single Domain Architecture** - All services via tenzai-order.ap.ngrok.io
- [x] **Web Ordering** - Customer webapp with menu, cart, checkout
- [x] **Order Tracking** - Real-time status page with JavaScript fixes
- [x] **LINE Integration** - Chatbot responses, deep linking, push notifications
- [x] **Staff Orders Dashboard** - /webappadmin/admin/staff-orders.html (timezone + API fixes)
- [x] **Staff Notification Service** - Backend implementation ready (services/notification_service.py)
- [x] **Order Status Management API** - PATCH /api/orders/{order_number}/status
- [x] **Timezone Support** - UTC+7 Thailand timezone conversion

---

## 🔧 DATABASE V2 + CODE REFACTORING PLAN (7 Days)

### 🎯 **MAJOR UPGRADE OBJECTIVES:**
1. **Database Performance:** 80% faster queries (500ms → 100ms)
2. **Payment System:** Complete PromptPay QR + slip verification 
3. **Code Quality:** main.py (703 lines) → modular (<200 lines/file)
4. **Scalability:** 10x capacity (1,000 → 10,000 orders/day)
5. **Zero Downtime:** Dual-write migration strategy

---

## 📅 **DAILY MIGRATION TASKS**

### 📍 **DAY 1: Documentation + Planning** (TODAY) 🔄 IN PROGRESS
- [x] **Update CLAUDE.md** ✅ COMPLETED - Database V2 architecture documented
- [🔄] **Update PROJECT-TODO.md** ✅ IN PROGRESS - Migration checklist
- [ ] **Create Migration Structure**
  - [ ] Create migrations/ folder with SQL scripts
  - [ ] Create rollback_scripts/ folder
  - [ ] Setup version control for migration tracking

### 📍 **DAY 2-3: Database Schema Enhancement**
- [ ] **New Tables Creation** (Day 2 Morning)
  - [ ] payment_transactions (complete payment lifecycle)
  - [ ] order_status_history (audit trail)
  - [ ] staff_actions (security audit)
  - [ ] settings (dynamic configuration)

- [ ] **Existing Tables Enhancement** (Day 2 Afternoon)
  - [ ] customers: Add platform_type, lifetime_value, tags, merged_from
  - [ ] customers: RENAME line_user_id → platform_id  
  - [ ] orders: Add branch_id, delivery_fee, discount_amount, net_amount
  - [ ] orders: Add delivery_address (JSONB), completed_at, metadata

- [ ] **Performance Optimization** (Day 3)
  - [ ] Create primary indexes (status, date, phone, platform_id)
  - [ ] Create composite indexes (date+status, customer+date)
  - [ ] Create partial indexes (pending orders, today's orders)
  - [ ] Setup RLS policies for new tables

### 📍 **DAY 4-5: Code Refactoring**
- [ ] **Router Separation** (Day 4 Morning)
  - [ ] Create routers/ folder structure
  - [ ] routers/orders.py (150 lines - order CRUD operations)
  - [ ] routers/webhooks.py (100 lines - LINE webhook handling)
  - [ ] routers/admin.py (100 lines - admin dashboard pages)
  - [ ] routers/health.py (50 lines - debug & health endpoints)
  - [ ] routers/static.py (50 lines - HTML file serving)

- [ ] **Services Layer** (Day 4 Afternoon)
  - [ ] services/database_v2.py (dual-write mechanism)
  - [ ] services/payment_service.py (QR generation & verification)
  - [ ] services/migration_service.py (data migration utilities)
  - [ ] Enhance services/notification_service.py

- [ ] **Schemas & Models** (Day 5 Morning)
  - [ ] schemas/order_schemas.py (Pydantic models)
  - [ ] schemas/payment_schemas.py (Payment validation)
  - [ ] schemas/customer_schemas.py (Customer data models)

- [ ] **Dual-Write Implementation** (Day 5 Afternoon)
  - [ ] Implement write-to-both-schemas mechanism
  - [ ] Add feature flags for gradual migration
  - [ ] Create data integrity validation
  - [ ] Setup migration monitoring

### 📍 **DAY 6: Testing & Validation**
- [ ] **Unit Testing** (Morning)
  - [ ] Test all new database operations
  - [ ] Test dual-write data consistency
  - [ ] Test payment QR generation
  - [ ] Test audit trail functionality

- [ ] **Integration Testing** (Afternoon)
  - [ ] End-to-end order flow testing
  - [ ] Payment verification workflow
  - [ ] Staff notification system
  - [ ] Rollback procedure validation

- [ ] **Performance Benchmarking** (Evening)
  - [ ] Measure query response times
  - [ ] Load test with 100 concurrent orders
  - [ ] Memory usage optimization
  - [ ] Database connection pooling

### 📍 **DAY 7: Production Switch**
- [ ] **Morning: Go-Live**
  - [ ] Switch to new database schema
  - [ ] Enable new code architecture
  - [ ] Monitor system health
  - [ ] Validate payment system

- [ ] **Afternoon: Optimization**
  - [ ] Performance monitoring
  - [ ] Fix any emerging issues
  - [ ] Optimize slow queries
  - [ ] User acceptance testing

- [ ] **Evening: Cleanup**
  - [ ] Remove old code/schema
  - [ ] Update documentation
  - [ ] Create post-migration report
  - [ ] Plan next phase (Production Deployment)

---

## 🛡️ **ROLLBACK PROCEDURES**

### **Emergency Rollback (< 1 minute):**
```bash
# Database rollback
./migrations/rollback_scripts/emergency_rollback.sh

# Code rollback  
git checkout ac92d46  # Checkpoint 2 Before Big Upgrade

# Service restart
sudo systemctl restart chatbot-api
```

### **Gradual Rollback (Feature Flags):**
```bash
# Environment variable control
export MIGRATION_MODE="old"  # old|dual|new

# Specific feature rollback
export USE_NEW_PAYMENT="false"
export USE_NEW_SCHEMA="false"
```

### **Data Recovery:**
```bash
# Restore from backup
./scripts/restore_from_backup.sh YYYY-MM-DD-HH-MM

# Validate data integrity
./scripts/validate_data_integrity.sh
```

---

## ✅ **SUCCESS METRICS & CHECKPOINTS**

### **Performance Targets:**
- [ ] Query response time: 500ms → 100ms (80% improvement)
- [ ] Database capacity: 1,000 → 10,000 orders/day (10x scale)
- [ ] Code maintainability: Files < 200 lines each
- [ ] System uptime: 100% during migration

### **Daily Checkpoints:**
- **End of Day 1:** Documentation complete, migration structure ready
- **End of Day 2:** New tables created, columns added successfully  
- **End of Day 3:** All indexes created, performance improved
- **End of Day 4:** Code separated into modules, compiles successfully
- **End of Day 5:** Dual-write working, data consistent
- **End of Day 6:** All tests passing, rollback validated
- **End of Day 7:** Production ready, old system deprecated

### **Quality Gates:**
1. **Code Quality:** ESLint/PyLint passes, no critical warnings
2. **Test Coverage:** >80% unit test coverage
3. **Performance:** All critical queries <100ms
4. **Security:** All RLS policies tested and working
5. **Documentation:** All new code documented and reviewed

### 📍 **PHASE 3C: Production Deployment** (Day 4) 
- [ ] **Code Preparation**
  - [ ] Create `requirements.txt`
  - [ ] Update `main.py` PORT handling
  - [ ] Add keep-alive mechanism
  - [ ] Environment variables validation

- [ ] **Render Deployment**
  - [ ] Connect GitHub to Render
  - [ ] Configure build settings
  - [ ] Set environment variables
  - [ ] Deploy and test

- [ ] **Domain Setup**
  - [ ] Configure `tenzaionline.tech` 
  - [ ] Update LINE webhook URL
  - [ ] SSL verification

### 📍 **PHASE 3D: Testing & Monitoring** (Day 5)
- [ ] **Load Testing**
  - [ ] Test 100 concurrent orders
  - [ ] Monitor response times
  - [ ] Database performance check

- [ ] **Monitoring Setup**
  - [ ] UptimeRobot health checks
  - [ ] Error logging system
  - [ ] Admin login protection

---

## 🏗️ CODE STRUCTURE REFACTORING

### Current Structure Issues:
- [ ] `main.py` too long (480+ lines) - needs splitting
- [ ] Services could be more modular
- [ ] Missing proper error handling middleware
- [ ] No logging system

### Proposed New Structure:
```
chatbot-api/
├── main.py                 (80 lines max - just app setup)
├── requirements.txt        (production dependencies)
├── config/
│   ├── __init__.py
│   └── settings.py        (environment variables)
├── routers/               (API routes - max 100 lines each)
│   ├── __init__.py
│   ├── orders.py          (order CRUD)
│   ├── webhooks.py        (LINE webhook)
│   ├── staff.py           (staff management)
│   └── static_files.py    (HTML serving)
├── services/              (Business logic - max 150 lines each)
│   ├── __init__.py
│   ├── database.py        (Supabase operations)
│   ├── line_messaging.py  (LINE API)
│   ├── ai_responses.py    (OpenRouter)
│   ├── notifications.py   (Staff alerts)
│   └── payments.py        (PromptPay QR)
├── models/                (Data models)
│   ├── __init__.py
│   ├── order.py
│   ├── customer.py
│   └── staff.py
└── utils/                 (Helper functions)
    ├── __init__.py
    ├── logging.py
    └── validators.py
```

### Refactoring Plan:
- [ ] Split `main.py` into routers
- [ ] Extract services into separate modules  
- [ ] Add proper error handling middleware
- [ ] Implement structured logging
- [ ] Add input validation schemas

---

## 🚨 CRITICAL REMINDERS

### Before Each Development Session:
1. ✅ Read `CLAUDE.md` for current objectives
2. ✅ Check this TODO list for next tasks
3. ✅ Update TodoWrite tool with current task
4. ✅ Test changes before committing
5. ✅ Update this file when tasks completed

### Code Quality Rules:
- 🚫 **No file > 200 lines** (except main.py during transition)
- ✅ **Each function < 30 lines**
- ✅ **Clear function names and comments**
- ✅ **Error handling for all external calls**
- ✅ **Test critical paths manually**

### Git Workflow:
- ✅ Commit after each completed subtask
- ✅ Descriptive commit messages with context
- ✅ Include Claude Code attribution
- ✅ Push to backup regularly

---

## 📊 PROGRESS TRACKING

**Overall Project:** 85% Core Features Complete, Ready for Payment Integration
- Infrastructure: ✅ 100%
- Database: ✅ 100% 
- Web App: ✅ 100%
- LINE Bot: ✅ 95%
- Staff System: ✅ 80% (dashboard ready, config pending)
- Payment: ⏳ 0% (HIGH PRIORITY)
- Production: ⏳ 0%

**Next Milestone:** Payment Integration → Production Deployment
**Target:** Fully operational restaurant chatbot system with QR payment

⚠️ **CRITICAL CONFIGURATION NEEDED:**
- STAFF_LINE_ID ยังไม่ได้ config ใน production .env file
- Payment gateway integration (PromptPay QR library)
- SSL certificate for production domain

---

*Last Updated: August 21, 2025*
*Next Review: After payment integration completion*