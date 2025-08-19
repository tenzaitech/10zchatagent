# 🚀 Tenzai Chatbot - Windows Setup

## 📦 การติดตั้งแบบง่าย

### 1. ติดตั้ง Python
1. ไปที่ https://python.org/downloads/
2. ดาวน์โหลด Python 3.11 หรือใหม่กว่า
3. ติดตั้งและ **ต้องเลือก "Add Python to PATH"**
4. Restart Command Prompt

### 2. ติดตั้ง ngrok  
1. ไปที่ https://ngrok.com/download
2. ดาวน์โหลด Windows version
3. แตกไฟล์ `ngrok.exe` ไปไว้ใน `C:\ngrok\` หรือ folder ใดก็ได้
4. เพิ่ม folder นั้นใน System PATH หรือคัดลอก ngrok.exe มาไว้ในโฟลเดอร์โปรเจค

### 3. รันสคริปต์ติดตั้ง
เปิด Command Prompt และรัน:
```cmd
cd "C:\Users\pleam\OneDrive\Desktop\10zchatbot"
install-windows.bat
```

## 🎯 การใช้งาน

### เริ่มระบบ (ต้องเปิด 2 terminals)

**Terminal 1: เริ่ม API**
```cmd
cd "C:\Users\pleam\OneDrive\Desktop\10zchatbot"
start-api.bat
```

**Terminal 2: เริ่ม ngrok**
```cmd
cd "C:\Users\pleam\OneDrive\Desktop\10zchatbot"  
start-ngrok.bat
```

### เมื่อเริ่มสำเร็จจะได้:
- **API:** http://localhost:8000
- **ngrok URL:** https://tenzai.ngrok.io (หรือ URL ที่ ngrok แสดง)

## 🔗 ขั้นตอนต่อไป

1. **อัพเดท LINE Webhook:**
   - ไปที่ LINE Developers Console
   - เปลี่ยน Webhook URL เป็น: `https://tenzai.ngrok.io/webhook/line`

2. **ทดสอบ:**
   - ส่งข้อความในแชท LINE
   - ลองสั่งอาหารผ่านเว็บ

## 🛠️ Troubleshooting

### หา ngrok URL
เมื่อรัน `start-ngrok.bat` จะแสดง URL หรือไปดูที่:
- http://localhost:4040 (ngrok dashboard)

### Python หา package ไม่เจอ
```cmd
pip install --user fastapi uvicorn httpx python-dotenv python-multipart
```

### ngrok ไม่เจอ
ลองคัดลอก `ngrok.exe` มาไว้ในโฟลเดอร์เดียวกับ project

## ✅ ตรวจสอบการทำงาน
1. API: เปิด http://localhost:8000 ใน browser
2. ngrok: เปิด http://localhost:4040 ดู tunnel status  
3. LINE: ส่งข้อความ "เปิดกี่โมง" ดูว่าตอบหรือไม่

---

**🎉 เมื่อทุกอย่างทำงาน = ระบบพร้อมใช้!**