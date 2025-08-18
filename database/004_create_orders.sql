-- 004_create_orders.sql
-- ตารางออเดอร์

CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_number VARCHAR(20) UNIQUE NOT NULL, -- เลขที่ออเดอร์
    customer_id UUID REFERENCES customers(id), -- เชื่อมกับลูกค้า
    customer_name VARCHAR(200), -- ชื่อลูกค้า (backup)
    customer_phone VARCHAR(20), -- เบอร์ลูกค้า (backup)
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'preparing', 'ready', 'completed', 'cancelled')),
    order_type VARCHAR(20) DEFAULT 'pickup' CHECK (order_type IN ('pickup', 'delivery', 'dine_in')),
    pickup_time TIMESTAMPTZ, -- เวลานัดรับ
    total_amount DECIMAL(10,2) NOT NULL, -- ยอดรวม
    payment_method VARCHAR(50) DEFAULT 'qr_code', -- วิธีชำระเงิน
    payment_status VARCHAR(20) DEFAULT 'unpaid' CHECK (payment_status IN ('unpaid', 'paid', 'refunded')),
    notes TEXT, -- หมายเหตุออเดอร์
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- สร้าง indexes
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_number ON orders(order_number);
CREATE INDEX idx_orders_date ON orders(created_at);
CREATE INDEX idx_orders_pickup_time ON orders(pickup_time);
CREATE INDEX idx_orders_payment_status ON orders(payment_status);

-- ฟังก์ชันสร้างเลขที่ออเดอร์อัตโนมัติ
CREATE OR REPLACE FUNCTION generate_order_number()
RETURNS TEXT AS $$
DECLARE
    today_date TEXT;
    sequence_num INTEGER;
    order_num TEXT;
BEGIN
    -- รูปแบบ: TNZ + YYYYMMDD + 3 หลัก
    today_date := to_char(NOW(), 'YYYYMMDD');
    
    -- หาเลขลำดับถัดไป
    SELECT COALESCE(MAX(CAST(RIGHT(order_number, 3) AS INTEGER)), 0) + 1
    INTO sequence_num
    FROM orders 
    WHERE order_number LIKE 'TNZ' || today_date || '%';
    
    -- สร้างเลขออเดอร์
    order_num := 'TNZ' || today_date || LPAD(sequence_num::TEXT, 3, '0');
    
    RETURN order_num;
END;
$$ LANGUAGE plpgsql;

-- ตัวอย่างข้อมูลออเดอร์
INSERT INTO orders (order_number, customer_id, customer_name, customer_phone, status, total_amount, payment_status) VALUES
(generate_order_number(), (SELECT id FROM customers WHERE display_name = 'คุณสมชาย'), 'คุณสมชาย', '081-234-5678', 'completed', 180.00, 'paid'),
(generate_order_number(), (SELECT id FROM customers WHERE display_name = 'คุณสมหญิง'), 'คุณสมหญิง', '082-345-6789', 'preparing', 289.00, 'paid');