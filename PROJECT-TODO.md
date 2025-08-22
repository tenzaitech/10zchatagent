# 📋 PROJECT TODO LIST

> **Project:** Tenzai Sushi Chatbot - Production Ready
> **Stack:** Supabase + Render + LINE Messaging API  
> **Domain:** tenzaionline.tech
> **Status:** Development → Production Deployment

---

## 🎯 CURRENT SPRINT: Staff Management System

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

## 🔥 NEXT TASKS (Priority Order)

### 📍 **PHASE 1: Payment Integration** (Days 1-2) - CRITICAL FOR REVENUE 💳
- [ ] **PromptPay QR Code Generation**
  - [ ] Research/install Thai PromptPay QR libraries (pymobile-payment or thai-qr-code)
  - [ ] Create payment service module (services/payment_service.py)
  - [ ] Generate QR code for order total + reference number
  - [ ] Add QR display in order confirmation (both web + LINE message)
  - [ ] Test QR codes with mobile banking apps

- [ ] **Payment Proof Upload System**
  - [ ] Create payment slip upload API endpoint
  - [ ] Add file upload functionality to web interface
  - [ ] Payment verification workflow (manual review)
  - [ ] Update order status after payment confirmation
  - [ ] Notify customer when payment is verified

### 📍 **PHASE 2: Staff System Configuration** (Day 3) - FINAL SETUP ⚡
- [x] **Staff Dashboard** ✅ COMPLETED
  - [x] Create `/admin/staff-orders.html` 
  - [x] Real-time orders list (today's orders)
  - [x] Update order status buttons (Preparing → Ready → Completed)
  - [x] Order details functionality

- [x] **Staff Notification Backend** ✅ COMPLETED
  - [x] Staff notification service implementation
  - [x] Instant order alerts (name, phone, items, total)
  - [x] LINE Flex Message templates

- [ ] **Production Configuration**
  - [ ] Configure STAFF_LINE_ID in production environment (.env)
  - [ ] Test end-to-end staff notification flow
  - [ ] Setup backup notification channels (email)
  - [ ] Document staff onboarding process

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