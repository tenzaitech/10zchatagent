# CLAUDE.md - Essential Instructions

> **INSTRUCTION TO CLAUDE:** คุณคือสถาปนิกเอกสารระบบ เคารพขอบเขตและห้ามเดาเกินข้อมูลจริง

## 📋 Project Snapshot
- **Goal:** ลดภาระตอบลูกค้า + รับออเดอร์ 24/7 + ลดขั้นตอนการสั่ง
- **Channels:** LINE (primary), Facebook, Instagram  
- **URL:** `https://tenzaionline.tech` (prod) / `https://tenzai-order.ap.ngrok.io` (dev)
- **Stack:** Python FastAPI + Supabase + OpenRouter

## 🎯 Current Sprint (Day 1/7: Database V2 Refactoring)
- **Focus:** Context optimization + Migration planning
- **Status:** 🔧 MAJOR UPGRADE IN PROGRESS
- **Progress:** Infra 100% / WebApp 100% / Payment 0% / Production 0%

## 🛡️ Core Principles
- **Security:** Webhook signatures required, anon=READ only, FastAPI=WRITE only
- **Identity:** Multi-platform (`LINE_{id}`, `FB_{id}`, `WEB_{phone}`)
- **Performance:** < 200 lines/file, RLS policies, proper indexes
- **Zero Downtime:** Dual-write strategy with instant rollback

## 📚 Documentation
- **Architecture:** [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- **Migration Plan:** [`docs/MIGRATION-V2.md`](docs/MIGRATION-V2.md)
- **Current Tasks:** [`PROJECT-TODO.md`](PROJECT-TODO.md)
- **Changes:** [`CHANGELOG.md`](CHANGELOG.md)

## 🧠 Context Management (ป้องกัน Error 413)
- **เมื่อเจอ Error 413:** ใช้ `/compact` ทันที
- **ทุก 30-40 interactions:** `/compact` เพื่อลด context
- **ไฟล์ใหญ่ > 800 lines:** ใช้ Grep แทน Read
- **References:**
  - [`docs/SESSION-MANAGEMENT.md`](docs/SESSION-MANAGEMENT.md) - คู่มือจัดการ context
  - [`docs/FILE-SUMMARIES.md`](docs/FILE-SUMMARIES.md) - summary ไฟล์ใหญ่
  - [`.claude-context-rules`](.claude-context-rules) - กฎการ ignore files

## ⚠️ Guardrails
- **DO:** เน้น features ที่ส่งผลรายได้ทันที, test ก่อน deploy
- **DON'T:** feature ซับซ้อน, เปลี่ยนโครงสร้างหลัก, เกิน Free plan
- **NEVER:** สร้างไฟล์ใหม่ถ้าไม่จำเป็น, commit โดยไม่ได้รับอนุญาต

## 🚀 Quick Actions
- **Context เต็ม:** `/compact` → ดู SESSION-MANAGEMENT.md
- **หาไฟล์ใหญ่:** ดู FILE-SUMMARIES.md แทนการ Read
- **Error 413:** อ่าน .claude-context-rules → `/compact` ทันที

---
*Last updated: 23 Aug 2025 - Context management และ Error 413 prevention*