# database.md
# Role: Data Contract (Schema + Public SELECT + Server WRITE)

> INSTRUCTION TO CLAUDE
- ระบุโครงสร้างข้อมูลแบบเบา ๆ (พอสำหรับอ้างอิง) พร้อม **ตัวอย่างสั้น**
- หลีกเลี่ยง SQL/โค้ดยาว ให้เป็น snippet ที่ตรวจสอบแนวคิดได้
- เติมเฉพาะส่วนที่มี TODO; ห้ามแก้ชื่อฟิลด์หลักที่ระบุไว้แล้ว

## ERD (ASCII – Minimal)
```
categories (id PK, name)
menus (id PK, category_id FK→categories.id, name, price, is_available)
system_settings (key PK, value)

customers (id PK, line_user_id, display_name?, phone?, email?, address?)
orders (id PK, customer_id FK→customers.id, order_number, customer_name, status, total_amount, created_at)
order_items (id PK, order_id FK→orders.id, menu_id FK→menus.id, menu_name, quantity, unit_price, total_price)
conversations (id PK, line_user_id, message_text, response_text, created_at)
```
> **สัญญา:**  
> - **Public SELECT only:** `categories`, `menus`, `system_settings`  
> - **Server WRITE only:** `orders`, `order_items`, `customers`, `conversations`

## Columns (Minimal Reference)
- `orders.status`: `'pending'|'confirmed'|'rejected'|'preparing'|'done'`  
- `orders.order_type`: `'pickup'|'delivery'`  
- `orders.payment_method`: `'qr_code'|'cash'|'transfer'`  
- Index แนะนำ: `menus(category_id)`, `orders(created_at desc)`, `order_items(order_id)`

## RLS Policy Model (Concise)
- Public tables (`categories`, `menus`, `system_settings`): **enable RLS** + policy `SELECT to anon using (true)`  
- Write tables (`orders`, `order_items`, `customers`, `conversations`): **enable RLS** + **no anon policy** (write ผ่าน service role เท่านั้น)

**Project:** qlhpmrehrmprptldtchb - https://qlhpmrehrmprptldtchb.supabase.co

## REST (PostgREST) – Contracts
### 1) Public SELECT (client → Supabase)
```http
GET /rest/v1/categories
apikey: <ANON_KEY>
```
```http
GET /rest/v1/menus?select=id,name,price,category_id&is_available=eq.true
apikey: <ANON_KEY>
```
```http
GET /rest/v1/system_settings?select=key,value
apikey: <ANON_KEY>
```
```http
GET /rest/v1/menus?select=id,name,price&category_id=eq.2&is_available=eq.true&order=name.asc
apikey: <ANON_KEY>
```

### 2) Server WRITE (n8n → Supabase)  *service role only*
```http
POST /rest/v1/customers
apikey: <SERVICE_ROLE>
Authorization: Bearer <SERVICE_ROLE>
Content-Type: application/json

{ "line_user_id": "Uxxxx", "display_name": "Somchai", "phone": "08x-xxx-xxxx" }
```

```http
POST /rest/v1/orders
apikey: <SERVICE_ROLE>
Authorization: Bearer <SERVICE_ROLE>
Content-Type: application/json

{
  "customer_id": 123,
  "order_number": "T001",
  "customer_name": "Somchai",
  "status": "pending",
  "total_amount": 1234
}
```

```http
POST /rest/v1/order_items
apikey: <SERVICE_ROLE>
Authorization: Bearer <SERVICE_ROLE>
Prefer: return=representation
Content-Type: application/json

[
  { "order_id": 456, "menu_id": 1, "menu_name": "SALMON SUSHI", "quantity": 2, "unit_price": 15, "total_price": 30 },
  { "order_id": 456, "menu_id": 45, "menu_name": "WAGYU STEAK", "quantity": 1, "unit_price": 350, "total_price": 350 }
]
```

## Data Validation (n8n Responsibilities)
- Re-price: คำนวนจาก `menus.price` ล่าสุดเสมอก่อนสร้าง order  
- Enforce: `quantity >= 1`, `is_available = true` เฉพาะเมนูที่ขาย  
- Anti-tamper: ห้ามรับราคา/ชื่อเมนูจาก client มาใช้ตรง ๆ

## Size & Retention (Free Plan)
- `conversations.message_text/response_text` จำกัด ~300–600 ตัวอักษร  
- พิจารณา purge logs/old conversations รายเดือน
- เก็บรูป/ไฟล์สลิปชั่วคราวนอก DB → ใช้ **Supabase Storage** (bucket: receipts, public read-only, auto-delete 7 วัน)

## Env & Secrets (Names Only)
- `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`  
- **อย่า**ใส่ค่าจริงในไฟล์นี้

## Guardrails
- **Do:** ระบุเฉพาะสัญญา/คอนแทร็ก, ตัวอย่างสั้น  
- **Don’t:** เปิดการเขียนผ่าน anon, บรรยายการ deploy/lifecycle เกินความจำเป็น

