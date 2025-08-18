-- 003_create_customers.sql
-- ตารางข้อมูลลูกค้า

CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    line_user_id VARCHAR(100) UNIQUE NOT NULL, -- LINE User ID
    display_name VARCHAR(200), -- ชื่อแสดงใน LINE
    phone VARCHAR(20), -- เบอร์โทรศัพท์
    email VARCHAR(100), -- อีเมล (สำหรับอนาคต)
    address TEXT, -- ที่อยู่ (สำหรับ delivery)
    notes TEXT, -- บันทึกพิเศษเกี่ยวกับลูกค้า
    total_orders INTEGER DEFAULT 0, -- จำนวนครั้งที่สั่ง
    total_spent DECIMAL(10,2) DEFAULT 0, -- ยอดซื้อรวมตลอดกาล
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- สร้าง indexes
CREATE INDEX idx_customers_line_id ON customers(line_user_id);
CREATE INDEX idx_customers_phone ON customers(phone);
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_total_spent ON customers(total_spent);

-- ตัวอย่างข้อมูลลูกค้า
INSERT INTO customers (line_user_id, display_name, phone, total_orders, total_spent) VALUES
('U4af4980629example1', 'คุณสมชาย', '081-234-5678', 5, 1250.00),
('U4af4980629example2', 'คุณสมหญิง', '082-345-6789', 2, 680.00),
('U4af4980629example3', 'คุณสมศักดิ์', '083-456-7890', 1, 189.00);