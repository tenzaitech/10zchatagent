# n8n Workflow Import Guide

## 🚀 วิธี Import WF-A (Inbound Chat) เข้า n8n

### Step 1: เปิด n8n UI
1. เปิดเบราว์เซอร์ไป: http://localhost:5678
2. หากยังไม่มี account ให้สร้างใหม่
3. Login เข้าระบบ

### Step 2: Import Workflow
1. ไปที่หน้าหลัก n8n
2. กดปุ่ม **"+ Add workflow"** หรือ **"Import from File"**
3. เลือก **"From file"**
4. เลือกไฟล์: `workflows/WF-A-inbound-chat.json`
5. กด **Import**

### Step 3: ตรวจสอบ Workflow
หลังจาก import แล้ว คุณจะเห็น nodes ต่างๆ:
- 🔗 **Webhook - LINE Chat**: รับข้อมูลจาก LINE
- 📝 **Parse LINE Data**: แยกข้อความและ user ID
- 🔀 **FAQ Router**: แยกประเภทคำถาม
- 💬 **Generate FAQ Response**: สร้างคำตอบ
- 🔘 **Generate Order Button**: สร้างปุ่มสั่งอาหาร
- 📤 **Format LINE Reply**: จัดรูปแบบข้อความ
- ✅ **Success/Error Response**: ตอบกลับ webhook

### Step 4: เปิดใช้งาน Webhook
1. กดที่ node **"Webhook - LINE Chat"**
2. คลิกปุ่ม **"Execute Node"** หรือ **"Listen for Test Event"**
3. คุณจะได้ URL: `http://localhost:5678/webhook/line-chat`
4. คัดลอก URL นี้ไว้

### Step 5: ทดสอบ Workflow
1. เปิด Terminal
2. รันคำสั่ง:
```bash
cd /mnt/c/Users/pleam/OneDrive/Desktop/10zchatbot
./test-webhook.sh
```

หรือทดสอบแค่ 1 case:
```bash
curl -X POST "http://localhost:5678/webhook/line-chat" \
  -H "Content-Type: application/json" \
  -d '{
    "body": {
      "events": [
        {
          "type": "message",
          "message": {"type": "text", "text": "เวลาเปิด"},
          "source": {"type": "user", "userId": "Utest001"},
          "replyToken": "test-token-001"
        }
      ]
    }
  }'
```

### Step 6: ตรวจสอบผลลัพธ์
1. ดูใน n8n UI → **Executions** tab
2. ควรเห็น execution สำเร็จ (เครื่องหมายถูก สีเขียว)
3. คลิกดูรายละเอียด execution เพื่อดูข้อมูลที่ผ่านแต่ละ node

---

## 🔧 Troubleshooting

### ❌ Import Failed
- ตรวจสอบไฟล์ JSON format ถูกต้องไหม
- ลองใช้ "Import from URL" แทน

### ❌ Webhook ไม่ทำงาน  
- ตรวจสอบ n8n container รันอยู่: `docker ps`
- ตรวจสอบ port 5678 เปิดอยู่: `netstat -an | grep 5678`
- รีสตาร์ท n8n: `docker restart chatbot_n8n`

### ❌ Test Script ไม่ทำงาน
- ติดตั้ง jq: `sudo apt install jq` (Linux) หรือ `brew install jq` (Mac)
- ตรวจสอบ curl ติดตั้งแล้ว: `curl --version`

### ❌ Execution Error
- ดู error message ใน n8n UI
- ตรวจสอบ node configuration
- ลอง execute แต่ละ node ทีละตัว

---

## ✅ Expected Results

เมื่อทดสอบสำเร็จ คุณควรจะเห็น:

**Test 1 (เวลาเปิด)**: 
```json
{
  "status": "success",
  "message": "Reply sent"
}
```

**Test 2 (ที่อยู่)**:
```json
{
  "status": "success", 
  "message": "Reply sent"
}
```

**Test 3 (สั่งอาหาร)**:
```json
{
  "status": "success",
  "message": "Reply sent"
}
```

และใน execution details จะเห็น:
- FAQ responses ที่เหมาะสม
- Order button พร้อม URL: https://order.tenzaitech.online
- Message format ถูกต้องตาม LINE API

---

## 🎯 Next Steps

หลังจาก WF-A ทำงานได้แล้ว:
1. ✅ **Phase 2 Complete** - Basic webhook receiver
2. 🔄 **Phase 2 Continue** - Add signature validation
3. 📈 **Phase 3** - Enhanced FAQ responses
4. 🛒 **Phase 4** - Order processing (WF-B)