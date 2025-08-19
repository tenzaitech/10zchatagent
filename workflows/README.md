# Tenzai Sushi Chatbot - n8n Workflows

## ภาพรวม
โฟลเดอร์นี้เก็บ n8n workflows สำหรับระบบ chatbot ของร้าน Tenzai Sushi

## โครงสร้าง Workflows

### WF-A: Inbound Chat Processing
**ไฟล์**: `WF-A-inbound-chat.json`
**หน้าที่**: รับข้อความจากลูกค้า → ตอบ FAQ → ส่งลิงก์สั่งอาหาร
**Endpoints**:
- Webhook: `https://n8n-dev.tenzaitech.online/webhook/line-chat`
- Test URL: `https://n8n-dev.tenzaitech.online/webhook-test/chat`

**Features**:
- รับ webhook จาก LINE/Facebook/Instagram
- ตรวจสอบ signature ป้องกัน spam
- ตอบ FAQ 5 หัวข้อ (เวลา, ที่อยู่, วิธีสั่ง, ราคา, ชำระเงิน)
- ส่งปุ่ม "สั่งอาหาร" (LIFF/Webview)
- Log การสนทนาลง Supabase

### WF-B: Order Processing  
**ไฟล์**: `WF-B-order-processing.json`
**หน้าที่**: รับออเดอร์จาก WebApp → validate → เขียน DB → แจ้งพนักงาน
**Endpoints**:
- API: `https://n8n-dev.tenzaitech.online/webhook/orders/create`
- Test URL: `https://n8n-dev.tenzaitech.online/webhook-test/order`

**Features**:
- รับ POST request จาก customer WebApp
- Re-calculate ราคาจาก database (security)
- Upsert customer data
- สร้าง order + order_items
- ส่งแจ้งเตือนพนักงานทาง LINE
- Auto-cancel หลัง 30 นาที

### WF-C: Utility Functions
**ไฟล์**: `WF-C-utils.json`  
**หน้าที่**: งานสนับสนุน + maintenance
**Features**:
- Health check endpoints
- Cleanup old conversations
- Analytics data collection
- Error monitoring

## การติดตั้ง

### 1. Import Workflows
1. เปิด n8n UI: http://localhost:5678
2. ไป Settings → Import from File
3. เลือกไฟล์ .json ที่ต้องการ
4. กด Import

### 2. ตั้งค่า Credentials
**Supabase**:
- URL: `https://qlhpmrehrmprptldtchb.supabase.co`
- Anon Key: [ดูใน database.md]
- Service Role: [ดูใน database.md]

**LINE Messaging API**:
- Channel Access Token: [ตั้งใน LINE Developer Console]
- Channel Secret: [สำหรับ signature validation]

### 3. เปิดใช้งาน Webhooks
**LINE Developer Console**:
1. ไป Messaging API tab
2. ตั้ง Webhook URL: `https://n8n-dev.tenzaitech.online/webhook/line-chat`
3. เปิด Use webhook: ON

## การทดสอบ

### ทดสอบ WF-A (Chat)
```bash
# ทดสอบ FAQ
curl -X POST https://n8n-dev.tenzaitech.online/webhook-test/chat \
-H "Content-Type: application/json" \
-d '{"message": "เวลาเปิด-ปิด"}'

# ทดสอบปุ่มสั่งอาหาร  
curl -X POST https://n8n-dev.tenzaitech.online/webhook-test/chat \
-H "Content-Type: application/json" \
-d '{"message": "สั่งอาหาร"}'
```

### ทดสอบ WF-B (Orders)
```bash
# ทดสอบสร้างออเดอร์
curl -X POST https://n8n-dev.tenzaitech.online/webhook/orders/create \
-H "Content-Type: application/json" \
-d '{
  "channel": "line",
  "source": "web", 
  "user_ref": {"line_user_id": "Utest123"},
  "cart": [{"menu_id": 1, "qty": 2}],
  "contact": {"name": "Test User", "phone": "081-234-5678"}
}'
```

## Monitoring & Debugging

### ดู Logs
- n8n UI → Executions tab
- Docker logs: `docker logs chatbot_n8n`
- Log files: `./n8n-data/n8nEventLog*.log`

### Health Check
- WF-A: `GET https://n8n-dev.tenzaitech.online/webhook/health/chat`
- WF-B: `GET https://n8n-dev.tenzaitech.online/webhook/health/orders`

## Troubleshooting

### LINE Webhook ไม่ทำงาน
1. ตรวจ Webhook URL ใน LINE Console
2. ตรวจ SSL certificate (ต้อง HTTPS)
3. ตรวจ signature validation

### Database Connection Error  
1. ตรวจ Supabase credentials
2. ตรวจ network/firewall 
3. ตรวจ RLS policies

### Performance Issues
1. ตรวจ n8n execution time
2. ตรวจ Supabase query performance  
3. พิจารณา caching

## Production Deployment

### Pre-production Checklist
- [ ] ทดสอบทุก workflow ด้วยข้อมูลจริง
- [ ] ตั้ง production webhook URLs
- [ ] เปิด RLS policies บน Supabase
- [ ] ตั้ง monitoring/alerting
- [ ] Backup workflows + database

### Go-Live Steps
1. เปลี่ยน webhook URLs เป็น production
2. ทดสอบ end-to-end อีกครั้ง
3. แจ้งทีมพนักงาน + training
4. Monitor ใน 24 ชม.แรก