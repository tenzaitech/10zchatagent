# 🚀 Tenzai Chatbot Setup Instructions

> **Updated**: 20 สิงหาคม 2025 - ระบบ FastAPI ใหม่

## การเริ่มใช้งานระบบ

### ขั้นตอน 0: Environment Setup
```bash
# Copy environment template
cp chatbot-api/.env.example chatbot-api/.env

# Edit with your actual credentials
nano chatbot-api/.env
```

**Required credentials:**
- Supabase URL และ service role key
- LINE channel access token และ secret  
- OpenRouter API key (optional สำหรับ AI responses)
- ngrok auth token (ใน ngrok.yml)

### ขั้นตอน 1: เริ่ม Web App Server
```bash
# รันคมมานด์นี้ใน terminal หรือ double-click
start-webapp.bat
```
- Web App จะรันที่ `http://localhost:3000`
- ต้องให้รันอยู่เสมอ

### ขั้นตอน 2: เริ่ม API Server
```bash  
# รันคมมานด์นี้ใน terminal หรือ double-click
start-api.bat
```
- API จะรันที่ `http://localhost:8000`
- ต้องให้รันอยู่เสมอ

### ขั้นตอน 3: เริ่ม ngrok Tunnels
```bash
# รันคมมานด์นี้ใน terminal หรือ double-click  
start-ngrok-all.bat
```

ngrok จะสร้าง 2 tunnels:
- **Web App**: `https://tenzai-order.ngrok.io` (ใช้ custom subdomain)
- **API**: `https://xxxxxxxx.ngrok.io` (random URL)

### ขั้นตอน 4: อัพเดต API URL
หลังจาก ngrok รัน ให้:
1. Copy **API URL** (random URL) จาก ngrok console
2. แก้ไขในไฟล์ `webappadmin/customer_webapp.html`:
   ```javascript
   // หาบรรทัดนี้:
   ? 'https://YOUR_API_NGROK_URL.ngrok.io' 
   
   // แทนที่ด้วย API URL ที่ได้จาก ngrok
   ? 'https://abc123def.ngrok.io'
   ```

### ขั้นตอน 5: อัพเดต LINE Webhook
1. Copy **API URL** จาก ngrok
2. ไปที่ [LINE Developers Console](https://developers.line.biz)
3. อัพเดต Webhook URL เป็น: `https://YOUR_API_URL.ngrok.io/webhook/line`

## 🔗 URLs สำคัญ

### สำหรับลูกค้า (Customer)
- **Web App**: `https://tenzai-order.ap.ngrok.io/customer_webapp.html`
- **Order Tracking**: `https://tenzai-order.ap.ngrok.io/order-status.html?order=ORDER_NUMBER`

### สำหรับ Admin/Developer  
- **API**: `https://xxxxxxxx.ngrok.io` (จะเปลี่ยนทุกครั้งที่รัน ngrok ใหม่)
- **API Health**: `https://xxxxxxxx.ngrok.io/` 
- **Schema Inspector**: `https://xxxxxxxx.ngrok.io/api/schema/sample-data`
- **ngrok Inspector**: `http://localhost:4040`

## 🆕 New Features

### Multi-Platform Support
- **Platform IDs**: `LINE_{user_id}`, `FB_{user_id}`, `IG_{user_id}`, `WEB_{phone}`
- **Deep Linking**: จาก chatbot ไปยัง web app พร้อม pre-filled data
- **Customer Merging**: ใช้ phone number เป็น universal key

### Order Confirmation
- **LINE Push**: Flex Message notification พร้อม order details
- **Order Tracking**: Real-time status page ที่ auto-refresh ทุก 30 วินาที
- **Status Flow**: pending → confirmed → preparing → ready → completed

## ⚠️ สิ่งที่ต้องระวัง

1. **API URL จะเปลี่ยน** ทุกครั้งที่รัน ngrok ใหม่ (เพราะใช้ random URL)
2. **ต้องอัพเดต 2 จุด** ทุกครั้ง:
   - `customer_webapp.html` (API endpoint)  
   - LINE Webhook URL
3. **เซิร์ฟเวอร์ทั้ง 3 ตัว** ต้องรันพร้อมกัน:
   - Web App Server (port 3000)
   - API Server (port 8000) 
   - ngrok Tunnels

## 🔧 Troubleshooting

### ถ้า ngrok ไม่ทำงาน:
- ตรวจสอบว่าเซิร์ฟเวอร์ทั้ง 2 รันแล้ว
- ตรวจสอบ auth token ใน ngrok.yml
- ลอง restart ngrok

### ถ้าลูกค้าสั่งอาหารไม่ได้:
- ตรวจสอบ API URL ใน `customer_webapp.html`
- ตรวจสอบ CORS settings
- ดู console log ใน browser (F12)

### ถ้า LINE ไม่ตอบ:
- ตรวจสอบ LINE Webhook URL
- ดู API logs ใน terminal
- ตรวจสอบ signature validation