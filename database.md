# database.md
# Role: Data Contract (Schema + Public SELECT + Server WRITE)

> INSTRUCTION TO CLAUDE
- ระบุโครงสร้างข้อมูลแบบเบา ๆ (พอสำหรับอ้างอิง) พร้อม **ตัวอย่างสั้น**
- หลีกเลี่ยง SQL/โค้ดยาว ให้เป็น snippet ที่ตรวจสอบแนวคิดได้
- เติมเฉพาะส่วนที่มี TODO; ห้ามแก้ชื่อฟิลด์หลักที่ระบุไว้แล้ว

## ERD (ASCII – Minimal)
```
categories (id PK, name)
menus (id PK, category_id FK→categories.id, name, price, is_active)
system_settings (key PK, value)

customers (id PK, line_user_id?, psid?, name?, phone?)
orders (id PK, customer_id FK→customers.id, status, source, channel, total_price, created_at)
order_items (id PK, order_id FK→orders.id, menu_id FK→menus.id, qty, price)
conversations (id PK, customer_id?, channel, last_user_message, summary, created_at)
```
> **สัญญา:**  
> - **Public SELECT only:** `categories`, `menus`, `system_settings`  
> - **Server WRITE only:** `orders`, `order_items`, `customers`, `conversations`

## Columns (Minimal Reference)
- `orders.status`: `'pending'|'confirmed'|'rejected'|'preparing'|'done'`  
- `orders.source`: `'web'|'chat'`  
- `orders.channel`: `'line'|'fb'|'ig'`  
- Index แนะนำ: `menus(category_id)`, `orders(created_at desc)`, `order_items(order_id)`

## RLS Policy Model (Concise)
- Public tables (`categories`, `menus`, `system_settings`): **enable RLS** + policy `SELECT to anon using (true)`  
- Write tables (`orders`, `order_items`, `customers`, `conversations`): **enable RLS** + **no anon policy** (write ผ่าน service role เท่านั้น)

**TODO:** ใส่ชื่อโปรเจกต์/URL ของ Supabase (ไม่ใส่คีย์จริง)

## REST (PostgREST) – Contracts
### 1) Public SELECT (client → Supabase)
```http
GET /rest/v1/categories
apikey: <ANON_KEY>
```
```http
GET /rest/v1/menus?select=id,name,price,category_id&is_active=eq.true
apikey: <ANON_KEY>
```
```http
GET /rest/v1/system_settings?select=key,value
apikey: <ANON_KEY>
```

### 2) Server WRITE (n8n → Supabase)  *service role only*
```http
POST /rest/v1/customers
apikey: <SERVICE_ROLE>
Authorization: Bearer <SERVICE_ROLE>
Content-Type: application/json

{ "line_user_id": "Uxxxx", "name": "Somchai", "phone": "08x-xxx-xxxx" }
```

```http
POST /rest/v1/orders
apikey: <SERVICE_ROLE>
Authorization: Bearer <SERVICE_ROLE>
Content-Type: application/json

{
  "customer_id": 123,
  "status": "pending",
  "source": "web",
  "channel": "line",
  "total_price": 1234
}
```

```http
POST /rest/v1/order_items
apikey: <SERVICE_ROLE>
Authorization: Bearer <SERVICE_ROLE>
Prefer: return=representation
Content-Type: application/json

[
  { "order_id": 456, "menu_id": 1, "qty": 2, "price": 89 },
  { "order_id": 456, "menu_id": 45, "qty": 1, "price": 199 }
]
```

## Data Validation (n8n Responsibilities)
- Re-price: คำนวนจาก `menus.price` ล่าสุดเสมอก่อนสร้าง order  
- Enforce: `qty >= 1`, `is_active = true` เฉพาะเมนูที่ขาย  
- Anti-tamper: ห้ามรับราคา/ชื่อเมนูจาก client มาใช้ตรง ๆ

## Size & Retention (Free Plan)
- `conversations.summary` จำกัด ~300–600 ตัวอักษร  
- พิจารณา purge logs/old conversations รายเดือน
- เก็บรูป/ไฟล์สลิปชั่วคราวนอก DB (ถ้าใช้) – **TODO:** ตัดสินใจ storage

## Env & Secrets (Names Only)
- `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`  
- **อย่า**ใส่ค่าจริงในไฟล์นี้

## Guardrails
- **Do:** ระบุเฉพาะสัญญา/คอนแทร็ก, ตัวอย่างสั้น  
- **Don’t:** เปิดการเขียนผ่าน anon, บรรยายการ deploy/lifecycle เกินความจำเป็น
