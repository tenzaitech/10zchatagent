-- 002_create_menus.sql
-- ตารางเมนูอาหาร

CREATE TABLE menus (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    menu_code VARCHAR(20) UNIQUE, -- รหัสเมนูจากระบบ POS
    category_id UUID REFERENCES categories(id),
    name VARCHAR(200) NOT NULL, -- ชื่อเมนูภาษาอังกฤษ
    name_thai VARCHAR(200), -- ชื่อเมนูภาษาไทย
    description TEXT, -- รายละเอียดเมนู
    price DECIMAL(10,2) NOT NULL,
    image_url TEXT, -- รูปภาพเมนู
    is_delivery BOOLEAN DEFAULT true, -- สามารถจัดส่งได้
    is_available BOOLEAN DEFAULT true, -- พร้อมขาย
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- สร้าง indexes สำหรับ performance
CREATE INDEX idx_menus_category ON menus(category_id);
CREATE INDEX idx_menus_available ON menus(is_available);
CREATE INDEX idx_menus_delivery ON menus(is_delivery);
CREATE INDEX idx_menus_price ON menus(price);
CREATE INDEX idx_menus_code ON menus(menu_code);

-- ตัวอย่างข้อมูลเมนู (จากไฟล์ Excel)
INSERT INTO menus (menu_code, category_id, name, name_thai, price) VALUES
('SU-13', (SELECT id FROM categories WHERE name = 'NIGIRI SUSHI'), 'NITSUKE SALMON SUSHI', 'เนื้อส่วนติดหนังแซลมอน ซูชิ', 15.00),
('RO-15', (SELECT id FROM categories WHERE name = 'ROLL'), 'Gure Salmon Top Foiegras Roll', 'โรลหน้าแซลม่อนส่วนติดหนังท็อปตับห่าน', 289.00),
('WF-02', (SELECT id FROM categories WHERE name = 'Wagyu A4 Festival'), 'Wagyu A4 Top Foie Gras Sushi (1Pcs.)', 'ซูชิเนื้อวากิวA4ท็อปตับห่าน (1คำ)', 89.00),
('AG-17', (SELECT id FROM categories WHERE name = 'STEAK'), 'WAGYU A4 STEAK', 'สเต็กเนื้อวากิว', 350.00);