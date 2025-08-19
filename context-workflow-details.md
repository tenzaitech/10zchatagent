# Workflow Implementation Details

## WF-A: Inbound Messaging (Chat Handler)
**Purpose:** รับข้อความจาก LINE/FB/IG → ประมวลผล → ตอบกลับ

### Flow Steps:
1. **Webhook Reception**
   - Endpoint: `/webhook/{platform}` (line, fb, ig)  
   - Validate signature (LINE: X-Line-Signature, FB: X-Hub-Signature-256)
   - Parse platform-specific payload

2. **Intent Classification**
   ```javascript
   if (message.includes("เวลา", "เปิด", "ปิด")) → FAQ_HOURS
   if (message.includes("ที่อยู่", "แอดเดรส")) → FAQ_LOCATION  
   if (message.includes("สั่ง", "เมนู", "อาหาร")) → INTENT_ORDER
   if (message.includes("ราคา", "เท่าไร")) → FAQ_MENU
   else → INTENT_UNKNOWN
   ```

3. **Response Generation**
   - FAQ → Static response templates
   - ORDER → Rich menu with "สั่งอาหาร" button → webview URL
   - UNKNOWN → Fallback message + order button

4. **Conversation Logging** (optional)
   - Save summary to `conversations` table
   - Limit: 300 chars message + response

### Current Issue:
❌ **Error in "Get Menu Prices" node:** `Cannot read properties of undefined (reading 'status')`
- **Root Cause:** HTTP request configuration incorrect
- **Impact:** Workflow fails completely
- **Fix Required:** Check Supabase URL/headers in HTTP request node

## WF-B: Order Processing (E-commerce Backend)
**Purpose:** รับออเดอร์จากเว็บ → validate → บันทึก DB → แจ้งพนักงาน

### Input Format:
```json
{
  "channel": "line|fb|ig",
  "source": "web", 
  "user_ref": {"line_user_id": "U123..."},
  "cart": [
    {"menu_id": 1, "qty": 2, "note": "ไม่วาซาบิ"},
    {"menu_id": 15, "qty": 1}
  ],
  "contact": {"name": "สมชาย", "phone": "081-xxx-xxxx"}
}
```

### Flow Steps:
1. **Input Validation**
   - Schema check: required fields, data types
   - Business rules: qty >= 1, menu_id exists
   - Sanitization: strip HTML, limit string lengths

2. **Price Recalculation**
   - Fetch current prices: `GET /rest/v1/menus?id=in.(1,15)`  
   - Calculate total: `Σ(current_price × quantity)`
   - Anti-tampering: ignore any client-side prices

3. **Database Operations**
   ```sql
   -- Step 1: Upsert customer
   INSERT INTO customers (line_user_id, display_name, phone) 
   VALUES ('U123', 'สมชาย', '081-xxx') ON CONFLICT(line_user_id) DO UPDATE...
   
   -- Step 2: Create order
   INSERT INTO orders (customer_id, order_number, status, total_amount) 
   VALUES (customer_id, 'T001', 'pending', 180) RETURNING id
   
   -- Step 3: Bulk insert items
   INSERT INTO order_items (order_id, menu_id, menu_name, quantity, unit_price, total_price)
   VALUES (order_id, 1, 'SALMON SUSHI', 2, 65, 130), (order_id, 15, 'MISO SOUP', 1, 50, 50)
   ```

4. **Staff Notification**  
   - LINE Push API to staff group
   - Template: Order ID, items, total, customer info
   - Quick reply buttons: [ยืนยัน] [ปฏิเสธ] [ดูรายละเอียด]

5. **Customer Response**
   ```json
   {"success": true, "order_id": "T001", "total": 180, "eta_minutes": 30}
   ```

### Error Scenarios:
- **PRICE_MISMATCH:** Client total ≠ DB total → Use DB total + notify
- **MENU_UNAVAILABLE:** Item `is_available=false` → Remove + recalculate  
- **EMPTY_CART:** No items → 400 error + suggestion
- **DB_ERROR:** Connection failed → 500 + retry logic

## WF-C: Utilities (Helper Functions)
**Purpose:** Supporting workflows for maintenance/monitoring

### Features:
- Health check endpoints
- Database maintenance (cleanup old conversations)
- Manual order status updates  
- Webhook testing utilities
- Analytics data collection

## Critical Fixes Needed:
1. **WF-A HTTP Request Node:** Fix Supabase connection configuration
2. **Webhook Signatures:** Implement proper validation for all platforms  
3. **Error Handling:** Add try-catch blocks around external API calls
4. **Rate Limiting:** Implement per-user/per-IP throttling