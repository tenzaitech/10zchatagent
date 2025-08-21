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

---

## 🔥 NEXT TASKS (Priority Order)

### 📍 **PHASE 3A: Staff Management System** (Days 1-2)
- [ ] **Staff LINE Notification**
  - [ ] Create staff LINE group/account setup
  - [ ] Add staff notification in order creation flow
  - [ ] Implement instant order alerts (name, phone, items, total)
  - [ ] Add order confirmation buttons (Accept/Reject)

- [ ] **Staff Dashboard** 
  - [ ] Create `/admin/staff-orders.html` 
  - [ ] Real-time orders list (today's orders)
  - [ ] Update order status buttons (Preparing → Ready → Completed)
  - [ ] Order details popup/modal

- [ ] **Database Enhancement**
  - [ ] Add `staff_notifications` table
  - [ ] Add `order_status_history` tracking
  - [ ] Create staff management endpoints

### 📍 **PHASE 3B: Payment Integration** (Day 3)
- [ ] **PromptPay QR Code**
  - [ ] Research Thai PromptPay QR libraries
  - [ ] Generate QR code for order total
  - [ ] Display QR in order confirmation page
  - [ ] Add payment proof upload system

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

**Overall Project:** 95% Core Features Complete
- Infrastructure: ✅ 100%
- Database: ✅ 100% 
- Web App: ✅ 100%
- LINE Bot: ✅ 90%
- Staff System: ⏳ 0%
- Payment: ⏳ 0%
- Production: ⏳ 0%

**Next Milestone:** Staff Management System → Production Deployment
**Target:** Fully operational restaurant chatbot system

---

*Last Updated: August 21, 2025*
*Next Review: After each phase completion*