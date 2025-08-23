-- 🚀 PERFORMANCE INDEXES FOR SUPABASE
-- สร้าง indexes เพื่อเพิ่มความเร็วในการ query

-- Orders table (หลัก)
CREATE INDEX IF NOT EXISTS idx_orders_status 
ON orders(status);

CREATE INDEX IF NOT EXISTS idx_orders_created_at 
ON orders(created_at);

CREATE INDEX IF NOT EXISTS idx_orders_customer 
ON orders(customer_id);

-- Partial indexes สำหรับ active orders
CREATE INDEX IF NOT EXISTS idx_orders_pending 
ON orders(status) 
WHERE status IN ('pending','confirmed','preparing');

-- Daily queries: use created_at index with date range
-- Example: WHERE created_at >= '2025-08-23'::date AND created_at < '2025-08-24'::date

-- Payment transactions
CREATE INDEX IF NOT EXISTS idx_payments_order 
ON payment_transactions(order_id);

CREATE INDEX IF NOT EXISTS idx_payments_status 
ON payment_transactions(status);

-- Customers
CREATE INDEX IF NOT EXISTS idx_customers_platform 
ON customers(line_user_id);

CREATE INDEX IF NOT EXISTS idx_customers_phone 
ON customers(phone);

-- Order Status History (สำหรับ audit trail)
CREATE INDEX IF NOT EXISTS idx_order_history_order 
ON order_status_history(order_id);

CREATE INDEX IF NOT EXISTS idx_order_history_created 
ON order_status_history(created_at);

-- Staff Actions (สำหรับ security audit)
CREATE INDEX IF NOT EXISTS idx_staff_actions_created 
ON staff_actions(created_at);

-- Order Items
CREATE INDEX IF NOT EXISTS idx_order_items_order 
ON order_items(order_id);

ANALYZE; -- Update statistics

-- 📊 คาดการณ์ผลลัพธ์:
-- • Query orders by status: 500ms → 50ms (10x เร็วขึ้น)
-- • Load today's orders: 300ms → 30ms (10x เร็วขึ้น)  
-- • Customer lookup: 200ms → 20ms (10x เร็วขึ้น)
-- • Payment verification: 400ms → 40ms (10x เร็วขึ้น)

-- 📝 วิธีใช้ indexes:
-- Daily orders: WHERE created_at >= CURRENT_DATE AND created_at < CURRENT_DATE + INTERVAL '1 day'
-- Specific date: WHERE created_at >= '2025-08-23'::date AND created_at < '2025-08-24'::date
-- Status filter: WHERE status = 'pending' (uses idx_orders_status)
-- Customer orders: WHERE customer_id = 'uuid' (uses idx_orders_customer)
