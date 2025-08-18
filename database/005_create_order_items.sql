-- 005_create_order_items.sql
-- ตารางรายการในออเดอร์

CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
    menu_id UUID REFERENCES menus(id),
    menu_name VARCHAR(200) NOT NULL, -- ชื่อเมนู (backup กรณีเมนูถูกลบ)
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL, -- ราคาต่อหน่วยตอนสั่ง
    total_price DECIMAL(10,2) NOT NULL, -- ราคารวมรายการนี้
    notes TEXT, -- หมายเหตุสำหรับรายการนี้ เช่น "ไม่ใส่วาซาบิ"
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- สร้าง indexes
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_menu ON order_items(menu_id);

-- ฟังก์ชันคำนวณ total_price อัตโนมัติ
CREATE OR REPLACE FUNCTION calculate_item_total()
RETURNS TRIGGER AS $$
BEGIN
    NEW.total_price := NEW.quantity * NEW.unit_price;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger สำหรับคำนวณ total_price อัตโนมัติ
CREATE TRIGGER trigger_calculate_item_total
    BEFORE INSERT OR UPDATE ON order_items
    FOR EACH ROW
    EXECUTE FUNCTION calculate_item_total();

-- ตัวอย่างข้อมูล order_items
INSERT INTO order_items (order_id, menu_id, menu_name, quantity, unit_price, notes) VALUES
(
    (SELECT id FROM orders WHERE order_number LIKE 'TNZ%' LIMIT 1),
    (SELECT id FROM menus WHERE menu_code = 'SU-13'),
    'เนื้อส่วนติดหนังแซลมอน ซูชิ',
    2,
    15.00,
    'ไม่ใส่วาซาบิ'
),
(
    (SELECT id FROM orders WHERE order_number LIKE 'TNZ%' LIMIT 1 OFFSET 1),
    (SELECT id FROM menus WHERE menu_code = 'RO-15'),
    'โรลหน้าแซลม่อนส่วนติดหนังท็อปตับห่าน',
    1,
    289.00,
    NULL
);