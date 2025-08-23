# 🧠 Claude Session Management Guide
> **ป้องกัน Error 413 "Request size exceeds model context window"**

## 🚨 เมื่อไหร่ต้อง /compact
- เมื่อเห็น context แน่น (การตอบช้าลง)
- หลังจากอ่านไฟล์ใหญ่หลายไฟล์
- ก่อนเริ่มงานใหม่ที่ต่างประเด็น
- ทุกๆ 30-40 การโต้ตอบ

## 📏 ขนาดไฟล์ที่ปลอดภัย
- **ปกติ:** < 500 บรรทัด/ไฟล์
- **ระวัง:** 500-800 บรรทัด  
- **อันตราย:** > 800 บรรทัด (ใช้ Grep แทน Read)
- **ห้าม:** > 1,000 บรรทัด (ใช้ summary)

## 🎯 Context-Efficient Strategies

### ✅ แทนที่จะ Read ไฟล์ใหญ่:
```bash
# แทนที่จะ: Read /path/to/large-file.html
# ใช้:
Grep "function addToCart" /path/to/large-file.html
Grep "class.*Order" /path/to/large-file.html  
Read /path/to/large-file.html offset:100 limit:50
```

### ✅ แบ่ง Session ตาม Task:
- **Session 1:** วิเคราะห์ปัญหา + วางแผน
- **Session 2:** Database migration
- **Session 3:** Frontend updates  
- **Session 4:** Testing + deployment

### ✅ ใช้ Reference Links:
```markdown
# แทนที่จะ copy code ยาวๆ:
ดู implementation ใน `main.py:lines 45-67`
ตามแผน `PROJECT-TODO.md:Phase 2`  
อ้างอิง `docs/ARCHITECTURE.md:Database Section`
```

## 🚫 สิ่งที่ทำให้ Context บวม

### ❌ การอ่านไฟล์ที่หลีกเลี่ยงได้:
- Read customer_webapp.html (1,235 lines) 
- Read โดยไม่ระบุ offset/limit
- Read ไฟล์ archive หรือ backup
- Read screenshots หรือ binary files

### ❌ การสะสม Context ที่ไม่จำเป็น:
- Debug output ยาวๆ
- Log files มหาศาล
- Git diff ขนาดใหญ่
- Error messages ซ้ำๆ

## 🛠️ Tool Selection Guide

| Task | ❌ Avoid | ✅ Use Instead |
|------|----------|----------------|
| ค้นหา code | Read large files | Grep with patterns |
| ดู structure | ls recursive | Glob with specific patterns |
| Edit code | Read → Edit entire file | Grep → Edit specific sections |
| Debug errors | Read logs | Grep error patterns |

## 📊 Session Health Indicators

### 🟢 Healthy Session:
- Responses มาเร็ว (< 5 วินาที)
- ไม่มี truncation warnings
- Tool calls สำเร็จทันที

### 🟡 Context กำลังเต็ม:
- Responses ช้าลง (5-10 วินาที)  
- เริ่มมี "..." truncation
- เวลา /compact

### 🔴 ใกล้ 413 Error:
- Responses > 10 วินาที
- Truncation เยอะ
- Tool calls timeout
- **ต้อง /compact ทันที**

## 🚀 Emergency Recovery

### หาก Error 413 เกิดขึ้น:
1. **ทันที:** พิมพ์ `/compact`
2. **รอ:** ให้ system summary conversation  
3. **เริ่มใหม่:** Focus เฉพาะ current task
4. **ใช้ Reference:** อ้างอิง docs แทนการ copy

### Context Reset Commands:
```bash
/compact           # บบ conversation
/new-session      # เริ่ม session ใหม่ (ถ้าเป็นปัญหาซ้ำ)
```

## 📋 Best Practices Checklist

**ก่อนเริ่มงานแต่ละครั้ง:**
- [ ] อ่าน CLAUDE.md (1.9K - ปลอดภัย)
- [ ] อ่าน PROJECT-TODO.md sections ที่เกี่ยวข้อง
- [ ] ใช้ docs/FILE-SUMMARIES.md แทนการอ่านไฟล์ใหญ่
- [ ] Plan งานให้แบ่งเป็น sessions เล็กๆ

**ระหว่างการทำงาน:**
- [ ] ใช้ Grep แทน Read สำหรับไฟล์ > 500 บรรทัด
- [ ] Commit บ่อยๆ เพื่อสร้าง checkpoint
- [ ] /compact ทุกๆ 30-40 interactions
- [ ] หลีกเลี่ยงการอ่านไฟล์หลายไฟล์ติดกัน

---
*Updated: 23 Aug 2025 - Context optimization complete*