# Technical Specifications & Implementation

## Database Schema (Supabase)
```sql
-- PUBLIC TABLES (anon read-only)
categories(id, name)
menus(id, category_id→categories.id, name, price, is_available)  
system_settings(key, value)

-- PRIVATE TABLES (service role only)
customers(id, line_user_id, display_name, phone, email, address)
orders(id, customer_id→customers.id, order_number, customer_name, status, total_amount, created_at)
order_items(id, order_id→orders.id, menu_id→menus.id, menu_name, quantity, unit_price, total_price)
conversations(id, line_user_id, message_text, response_text, created_at)
```

## API Endpoints
**Read (Client):**
- `GET /rest/v1/categories` 
- `GET /rest/v1/menus?is_available=eq.true`
- `GET /rest/v1/system_settings`

**Write (Server):**
- `POST /rest/v1/customers` (upsert by line_user_id)
- `POST /rest/v1/orders` (create new order)
- `POST /rest/v1/order_items` (bulk insert)

## Workflow Logic

### WF-A (Inbound Chat)
1. Verify webhook signature
2. Intent classification (FAQ vs ordering)  
3. FAQ → Instant response
4. Ordering → Send "สั่งอาหาร" button → open webview
5. Log conversation summary (optional)

### WF-B (Order Processing) 
1. Validate order payload from web
2. Re-price from current menu prices
3. Upsert customer record
4. Create order + order_items
5. Push notification to staff LINE
6. Return success/error to client

## Error Handling
- **Price mismatch:** Use DB prices, notify customer
- **Empty cart:** Reject with helpful message
- **DB down:** Fallback response + alert team
- **Invalid signature:** 401 silent rejection

## Security Checklist
- [x] RLS enabled on all tables
- [x] Anon key limited to SELECT on 3 tables only
- [x] Service role for all write operations
- [x] Webhook signature validation (pending implementation)
- [x] Rate limiting via Cloudflare
- [x] SSL/TLS encryption end-to-end

## Performance Constraints
- Supabase Free: 500MB DB, 2GB transfer/month
- n8n: Single container, memory-optimized
- Response time: <3sec for FAQ, <10sec for orders
- Concurrent users: ~50-100 (estimated)