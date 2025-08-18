# workflows.md
# Role: Business Logic & Conversation Flows (WF-A, WF-B)

> INSTRUCTION TO CLAUDE
- อธิบาย logic ระดับ workflow ไม่ผูกกับโค้ดเฉพาะแพลตฟอร์ม
- เติมเฉพาะจุดที่มี TODO / ตัวอย่างสั้น ๆ
- หลีกเลี่ยงคำสั่งปฏิบัติการยาว/สคริปต์เต็ม

## Glossary (คงที่)
- **WF-A = Inbound Messaging:** รับ webhook จาก LINE/FB/IG → FAQ → ปุ่ม “สั่งอาหาร” (เปิด webview/URL เดียว)  
- **WF-B = Ordering:** WebOrder → n8n `/orders/create` → validate/reprice → write DB → notify staff  
- **channel:** `line|fb|ig`, **source:** `web|chat`

---

## WF-A: Inbound Messaging
### Triggers
- LINE/FB/IG webhook (message, follow, postback)

### Steps (Minimal)
1) Verify signature + timestamp (reject if invalid/expired)  
2) Intent routing:  
   - FAQ intents (เวลาเปิด–ปิด/ที่อยู่/โปร) → ตอบทันที  
   - “สั่งอาหาร/เมนู” → ส่งปุ่มเปิด `https://order.tenzaitech.online` (LIFF/webview)  
   - อื่น ๆ → (optional) ส่งหา OpenRouter เพื่อช่วยตอบ/สรุป (fallback)  
3) (Optional) Log summary → `conversations` (ข้อความสั้น)  

### Error Paths
- Signature invalid → 401 (no reply)  
- Rate limit → ตอบข้อความมาตรฐาน “ขออภัย มีผู้ใช้งานหนาแน่น ลองใหม่อีกครั้ง”  
- Upstream down (Supabase/LLM) → ตอบ fallback + แจ้งทีม

### TODO:
- ระบุรายการ FAQ 3–5 หัวข้อ + ตัวอย่างข้อความตอบกลับ  
- นิยามข้อความ fallback (ไทยสั้น/สุภาพ)  

---

## WF-B: Ordering (from WebOrder)
### Input Payload (from client → n8n)
```json
{
  "channel": "line",
  "source": "web",
  "user_ref": { "line_user_id": "Uxxxx" },
  "cart": [
    { "menu_id": 123, "qty": 2, "note": "ไม่วาซาบิ" },
    { "menu_id": 45,  "qty": 1 }
  ],
  "contact": { "name": "Somchai", "phone": "08x-xxx-xxxx" }
}
```

### Steps (Minimal)
1) **Validate** schema + sanitize (qty>=1, ids numeric)  
2) **Re-price**: ดึง `menus` จาก DB → คำนวนยอดรวมจริง  
3) **Upsert customer** (by `line_user_id`/`psid`)  
4) **Create order** → **Bulk insert order_items**  
5) **Notify staff (LINE push)**: “ออเดอร์ใหม่ #<id> ยอด <total> …” + ปุ่ม `ยืนยัน/ปฏิเสธ` (postback)  
6) **Respond** to client: success with `order_id` (หรือ error แบบชัดเจน)

### Error Paths (อย่างน้อย 3)
- **PRICE_MISMATCH**: ราคา client ≠ DB → ใช้ราคา DB, แจ้งผลรวมใหม่ / ขอให้ยืนยันอีกครั้ง  
- **EMPTY_CART**: ปฏิเสธคำสั่งซื้อ พร้อมแนะนำให้เลือกเมนู  
- **DB_DOWN**: ตอบ failure + log + แจ้งทีม

### Optional: Payment
- โอนเงิน + อัปโหลดสลิปในแชท → ทีมตรวจแล้ว set `orders.status='confirmed'`  
- (ภายหลัง) Online payment → n8n handle callback → update status

### TODO:
- กำหนดข้อความแจ้งพนักงาน (template) + ฟิลด์ที่ต้องการเห็น  
- นิยาม policy เวลา/เงื่อนไข auto-cancel ถ้าไม่มีการยืนยันใน X นาที

---

## State Machine (Chat-only Fallback)
- Start → เลือกหมวด → เลือกรายการ → ระบุจำนวน → ตะกร้า → ยืนยันข้อมูล → ยืนยันออเดอร์  
- Events: `NEXT`, `BACK`, `ADD(item, qty)`, `EDIT`, `CLEAR`, `CONFIRM`  
- Exit conditions: success/failure/cancel

### TODO:
- กำหนดจำนวนรายการต่อหน้า (pagination) ต่อแพลตฟอร์ม  
- กำหนดข้อความระบบเมื่อ `CLEAR` หรือ `BACK` หลายครั้ง

---

## Monitoring & Limits
- Rate limit ต่อ IP/ต่อ user (n8n)  
- Basic analytics: #orders/day, avg basket size, FAQ hits, error rates

## Guardrails
- **Do:** บรรยาย logic เป็นขั้นตอน, ระบุ error path ที่พบบ่อย  
- **Don’t:** แปะโค้ดยาว/คีย์ลับ/สคริปต์ติดตั้ง
