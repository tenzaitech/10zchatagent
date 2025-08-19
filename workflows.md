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

### FAQ Responses (5 หัวข้อ)
1) **เวลาเปิด-ปิด**: "เปิดให้บริการทุกวัน 10:00-21:00 น. รับออร์เดอร์ล่าสุด 20:30 น."
2) **ที่อยู่/เบอร์โทร**: "📍 123 ถนนสุขุมวิท แขวงคลองตัน เขตวัฒนา กรุงเทพฯ 10110\n📞 02-xxx-xxxx"
3) **การสั่งอาหาร**: "สั่งออนไลน์ได้ที่ order.tenzaitech.online หรือกดปุ่ม 'สั่งอาหาร' ด้านล่าง 🍜"
4) **ราคา/เมนู**: "ดูเมนูและราคาทั้งหมดได้ที่หน้าสั่งอาหาร หรือสอบถามเพิ่มเติมได้เลยค่ะ"
5) **การชำระเงิน**: "รับชำระเงินสด/โอนเงิน/พร้อมเพย์ ส่งสลิปมาในแชทหลังสั่งเสร็จนะคะ"

### Fallback Messages
- **ไม่เข้าใจ**: "ขออภัยค่ะ ไม่เข้าใจคำถาม ลองถามใหม่หรือกด 'สั่งอาหาร' เลยนะคะ 😊"
- **ระบบขัดข้อง**: "ระบบมีปัญหาชั่วคราว กรุณาลองใหม่อีกครั้งใน 2-3 นาทีค่ะ"  

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

### Staff Notification Template
```
🔔 ออเดอร์ใหม่ #{{order_id}}
📅 {{datetime}}
💰 ยอดรวม: {{total_price}} บาท
📋 รายการ:
{{#each items}}
- {{name}} x{{qty}} ({{item_total}}฿){{#if note}} | หมายเหตุ: {{note}}{{/if}}
{{/each}}

👤 ลูกค้า: {{customer_name}}
📞 เบอร์: {{phone}}
📱 แชท: {{channel_name}}
🌐 แหล่งที่มา: {{source}}

[ยืนยัน] [ปฏิเสธ] [ดูรายละเอียด]
```

### Auto-cancel Policy
- **15 นาที**: ยังไม่มีการยืนยัน → แจ้งเตือนพนักงาน (2nd notification)
- **30 นาที**: ยังไม่ตอบรับ → auto-cancel + แจ้งลูกค้า "ขออภัย ออเดอร์หมดเวลา กรุณาสั่งใหม่"
- **Status flow**: pending → (15min warning) → (30min cancel) → cancelled

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
- **Don't:** แปะโค้ดยาว/คีย์ลับ/สคริปต์ติดตั้ง

---

## Test Cases (End-to-End)

### TC-01: Happy Path - Web Order Success
**Input:** LINE user clicks "สั่งอาหาร" → WebOrder → select 2 items → checkout  
**Expected:** Order created, staff notified, customer gets order confirmation  
**Verify:** DB has order+items, staff LINE receives notification with [ยืนยัน] button

### TC-02: Error - Price Mismatch  
**Input:** Client sends tampered prices (menu_id=1, client_price=50, actual_DB_price=89)  
**Expected:** n8n re-prices from DB, creates order with correct total, warns customer  
**Verify:** `orders.total_price` = DB price, customer notified "ราคาอัปเดต จาก X เป็น Y"

### TC-03: Happy Path - FAQ Response
**Input:** LINE user sends "เวลาเปิด" or "เปิดกี่โมง"  
**Expected:** Bot replies instantly with operating hours (10:00-21:00)  
**Verify:** Response < 3 seconds, no staff notification

### TC-04: Error - Invalid Webhook Signature
**Input:** Malicious POST to webhook endpoint with wrong signature  
**Expected:** 401 Unauthorized, no processing, no customer response  
**Verify:** Logs show "Invalid signature", conversation not saved

### TC-05: Error - Empty Cart Submission
**Input:** WebOrder submits cart=[] (empty array)  
**Expected:** n8n rejects with "EMPTY_CART", suggests menu selection  
**Verify:** No order created, customer gets error message with "สั่งอาหาร" button
