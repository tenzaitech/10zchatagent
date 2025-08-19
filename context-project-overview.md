# Project Overview & Business Context

## Project Identity
- **Name:** Tenzai Food Ordering System (10zchatbot)
- **Type:** Multi-channel Restaurant Chatbot + Web Ordering
- **Target:** Japanese/Thai Fusion Restaurant
- **Customer URL:** https://order.tenzaitech.online

## Business Problem & Solution
**Problem:** พนักงานต้องตอบคำถามลูกค้าซ้ำ ๆ และรับออเดอร์ด้วยตนเองตลอดเวลา
**Solution:** Hybrid system = Chatbot (FAQ + routing) + Web ordering interface

## Core Architecture Decision
**"Hybrid Approach"** - ไม่ใช่ pure chatbot หรือ pure web ordering
- Chat platforms → ตอบ FAQ → ส่งไปหน้าเว็บสั่งอาหาร
- เว็บออเดอร์ → ส่งข้อมูลกลับไป n8n → บันทึก DB → แจ้งพนักงาน

## Technology Stack
- **Orchestrator:** n8n (workflow automation)
- **Database:** Supabase Free (PostgreSQL + REST API)  
- **Proxy:** Cloudflare Tunnel (webhook security)
- **Channels:** LINE + Facebook Messenger + Instagram DM
- **Frontend:** Static HTML (customer order interface)

## Security Model
- **Client (Web):** Read-only access (anon key + RLS)
- **Server (n8n):** Full write access (service role)
- **Webhooks:** Signature validation required
- **Data:** Public menu data, private customer/order data

## Current Status (19 Aug 2025)
- ✅ Infrastructure & Database: 100% complete
- ✅ Admin interfaces: 100% complete  
- ✅ Customer web app: 100% complete
- ⚠️ Chatbot workflows: 15% (major errors to fix)
- ❌ Integration testing: 0% (pending workflow fixes)

## Key Files Reference
- `CLAUDE.md` - AI instructions & project principles
- `database.md` - Schema, APIs, security policies  
- `workflows.md` - Business logic for WF-A, WF-B, WF-C
- `project-issues-log.md` - Current problems & solutions
- `summarycheckpoint1.html` - Visual project summary