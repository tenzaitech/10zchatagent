-- 001_create_categories.sql
-- ตารางหมวดหมู่อาหาร

CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- สร้าง index สำหรับค้นหา
CREATE INDEX idx_categories_active ON categories(is_active);
CREATE INDEX idx_categories_name ON categories(name);

-- เพิ่มข้อมูลหมวดหมู่เริ่มต้น
INSERT INTO categories (name) VALUES
('NIGIRI SUSHI'),
('SASHIMI'),
('ROLL'), 
('SUSHI DON'),
('HOT DON'),
('UDON SOBA'),
('YAKI MONO'),
('AGE MONO'),
('SALAD YUM'),
('DRINK'),
('Lunch Set Menu'),
('SEASON OF SALMON'),
('Wagyu A4 Festival'),
('STEAK'),
('OTHER MENU');