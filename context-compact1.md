🍣 Tenzai Sushi Chatbot Project - สรุปที่มา ที่ไป
📖 เรื่องราวจากจุดเริ่มต้น:
🎯 ปัญหาที่ต้องแก้:
คุณมีร้านอาหาร 3 แบรนด์ (Hiso Sushi, Aroi Sushi, Tenzai Sushi) และต้องการระบบ chatbot เพื่อ:

ลดการตอบลูกค้าด้วยตนเอง (ปัจจุบัน 1-10 คน/วัน)
ให้ลูกค้าสั่งอาหารได้ง่ายขึ้น (ตอนนี้ใช้ PDF ใน Google Drive ยุ่งยาก)
ลดขั้นตอนการรับออเดอร์ (ตอนนี้ผ่านพนักงาน 3-4 คนต่อ 1 order)


🛠️ เครื่องมือที่เรามี:
💻 Software Stack:

Docker Desktop - รัน containers
Supabase plan free - ใช้เป็น database
VS Code + Claude Code CLI - พัฒนา
n8n - Workflow automation (เพื้่อให้ง่ายต่อการพัฒนาขึ้นเพราะผมมีความสามารถประมาณ low code)
LINE - Platform สำหรับ chatbot
GitHub - Version control
Domain: tenzaitech.online (active ใน Cloudflare)

🏗️ Architecture ที่เลือก:
ลูกค้า LINE → Cloudflare Tunnel → n8n → OpenRouter API → Supabase

📊 ข้อมูลจริงที่เรามี:
🍱 เมนูอาหาร (จาก Excel):

367 เมนู ทั้งหมด
32 หมวดหมู่ (NIGIRI SUSHI, SASHIMI, ROLL, etc.)
ราคา: 10-1,899 บาท (เฉลี่ย 137 บาท)
84 เมนู ไม่มีหมวดหมู่ → เก็บในหมวด "ไม่ระบุหมวดหมู่"

🗄️ Database Schema ที่สร้าง:

categories - 33 หมวดหมู่ (32 + ไม่ระบุ)
menus - 367 เมนูจริง
customers - ข้อมูลลูกค้า LINE
orders - ออเดอร์
order_items - รายการในออเดอร์
conversations - ประวัติการสนทนา
system_settings - การตั้งค่าร้าน'
ให้ตรวจสอบรายละเอียดใน supabase ด้วย auth ที่แนบให้ในไฟล์


🎯 สิ่งที่ทำเสร็จแล้ว:
1. ✅ Infrastructure Setup

Docker Compose - รัน n8n container
Cloudflare Tunnel - public URL (https://n8n-dev.tenzaitech.online)
Supabase Free - Database พร้อมใช้งาน

2. ✅ Database Complete

Schema - 7 ตาราง พร้อม relationships
Real Data - เมนู 367 รายการจาก Excel
Categories - 33 หมวดหมู่จริง

3. ✅ Admin Dashboard

เพิ่ม/แก้ไข/ลบ เมนู
จัดการหมวดหมู่
Real-time statistics
User-friendly interface

4. ✅ Customer WebApp

Menu browsing - เลือกตามหมวดหมู่
Shopping cart - เพิ่ม/ลด จำนวน
Checkout flow - กรอกชื่อ + เบอร์
Modern UI - โทนสี orange-white-black ตาม brand


📁 ไฟล์ในโฟลเดอร์ตอนนี้:
C:\Users\pleam\OneDrive\Desktop\10zchatbot\
├── docker-compose.yml           # n8n container setup
├── config.yml                   # Cloudflare tunnel config
├── admin-dashboard.html         # ระบบจัดการเมนู (เสร็จ)
├── tenzai-menu.html            # WebApp ลูกค้า (เสร็จ)
├── import-menus.html           # Tool import เมนูจาก Excel
├── Export_Menu_Branch_44639 1.xlsx  # ข้อมูลเมนูจริง
├── n8n-data/                   # Docker volume
└── n8nEventLog*.log           # Log files (ควรลบ)

🚧 สิ่งที่ยังต้องทำ:
📱 Phase 1: n8n Workflow (ขั้นต่อไป)
สร้าง LINE chatbot ที่:
- รับ webhook จาก LINE
- ตอบ FAQ พื้นฐาน (เวลาเปิด-ปิด, ที่อยู่)
- ส่งลิงก์ WebApp ให้ลูกค้า
- รับ order จาก WebApp
- ส่ง notification ให้พนักงาน
🔗 Phase 2: Integration
เชื่อมทุกอย่างเข้าด้วยกัน:
WebApp → n8n → LINE → Supabase
🚀 Phase 3: Production
- Deploy จริง
- Setup domain สำหรับ production
- Training พนักงาน

💡 Workflow ลูกค้าที่วางแผนไว้:
1. ลูกค้าส่งข้อความใน LINE
2. Chatbot ตอบ FAQ หรือส่งลิงก์เมนู
3. ลูกค้าเข้า WebApp → เลือกอาหาร → สั่ง
4. ข้อมูลออเดอร์ส่งกลับ LINE chat
5. พนักงานได้รับ notification
6. พนักงานยืนยัน + จัดเตรียม

🎯 จุดที่เราอยู่ตอนนี้:
✅ ฐานรากเสร็จหมดแล้ว - Database, Admin, WebApp
🚧 ขาดแค่ n8n workflow เพื่อเชื่อมทุกอย่างเข้าด้วยกัน
ความคืบหน้า: 70%

Infrastructure: 100%
Database: 100%
Admin Tools: 100%
Customer Interface: 100%
Chatbot Logic: 0% ← จุดที่ต้องทำต่อ