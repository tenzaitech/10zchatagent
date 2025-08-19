# Project Issues Log

## สำหรับ AI ที่จะทำงานต่อไปนี้

### ปัญหาหลักที่เจอ

#### 1. n8n Workflow Error (ปัญหาเร่งด่วน)
- **Error:** `Cannot read properties of undefined (reading 'status')` ใน WF-A workflow
- **Location:** Node "Get Menu Prices" 
- **Frequency:** เกิดขึ้นทุกครั้งที่ execute workflow (execution ID: 4, 5, 6)
- **Impact:** Workflow fail และหยุดทำงาน
- **Possible Root Cause:** HTTP Request response structure ไม่ตรงกับที่ expect หรือ Supabase API response format เปลี่ยน

#### 2. Database Connection Issues (สงสัย)
- **Symptoms:** Workflow ต้อง validate กับ Supabase แต่ fail ที่ HTTP request step
- **Note:** ต้องตรวจสอบ Supabase credentials และ RLS policies

#### 3. Webhook Configuration
- **Status:** มี webhook setup แต่ยังไม่แน่ใจว่า signature validation ทำงานถูกต้อง
- **Risk:** Security vulnerability ถ้า webhook ไม่ได้ validate ลายเซ็น

### Architecture Status (จากที่เห็น)

#### ที่ทำงานแล้ว ✅
- Docker compose setup (docker-compose.yml)
- n8n container running
- Database structure (database/ folder with SQL files)
- Cloudflare tunnel config (config.yml)
- Webapp files (webappadmin/)

#### ที่ยังมีปัญหา ⚠️
- WF-A workflow (Tenzai Chat) - fail ที่ "Get Menu Prices" node
- WF-B workflow (Tenzai Orders) - ยังไม่เห็น execution log
- Webhook endpoints testing
- Database permissions & RLS

### Files ที่ต้องตรวจสอบ
1. `/workflows/WF-A-inbound-chat-v2.json` - fix HTTP request node
2. `/workflows/WF-B-order-processing-FINAL-FIXED.json` - verify order processing
3. Database connection strings ใน n8n
4. Supabase RLS policies

### Next Actions สำหรับ AI
1. **Fix WF-A Error:** ตรวจสอบ HTTP request node configuration
2. **Test Database Connection:** verify Supabase API endpoints
3. **Import Fixed Workflows:** import workflows ที่แก้แล้วเข้า n8n
4. **Security Check:** ตรวจสอบ webhook signature validation

### Technical Stack ปัจจุบัน
- **Backend:** n8n (orchestrator)
- **Database:** Supabase (Free tier)
- **Proxy:** Cloudflare Tunnel
- **Frontend:** Static HTML files
- **Container:** Docker Compose

Last Updated: 19 สิงหาคม 2025