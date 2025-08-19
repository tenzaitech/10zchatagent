-- setup-complete-database.sql
-- Tenzai Sushi Chatbot - Complete Database Setup
-- Execute this ENTIRE script in Supabase SQL Editor (copy & paste all)

-- ============================================
-- CLEANUP (Optional - if tables exist)
-- ============================================
/*
-- Uncomment if you need to start fresh:
DROP TABLE IF EXISTS conversations CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS system_settings CASCADE;
DROP TABLE IF EXISTS menus CASCADE;  
DROP TABLE IF EXISTS categories CASCADE;
*/

-- ============================================
-- 1. CREATE TABLES (001-007)
-- ============================================

-- 001: Categories
CREATE TABLE IF NOT EXISTS categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_categories_active ON categories(is_active);
CREATE INDEX IF NOT EXISTS idx_categories_name ON categories(name);

-- 002: Menus  
CREATE TABLE IF NOT EXISTS menus (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    menu_code VARCHAR(20) UNIQUE,
    category_id UUID REFERENCES categories(id),
    name VARCHAR(200) NOT NULL,
    name_thai VARCHAR(200),
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    image_url TEXT,
    is_delivery BOOLEAN DEFAULT true,
    is_available BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_menus_category ON menus(category_id);
CREATE INDEX IF NOT EXISTS idx_menus_available ON menus(is_available);
CREATE INDEX IF NOT EXISTS idx_menus_delivery ON menus(is_delivery);
CREATE INDEX IF NOT EXISTS idx_menus_price ON menus(price);
CREATE INDEX IF NOT EXISTS idx_menus_code ON menus(menu_code);

-- 003: Customers
CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    line_user_id VARCHAR(100) UNIQUE,
    psid VARCHAR(100) UNIQUE,
    instagram_id VARCHAR(100) UNIQUE,
    name VARCHAR(200),
    phone VARCHAR(20),
    email VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_customers_line_id ON customers(line_user_id);
CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);

-- 004: Orders
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID REFERENCES customers(id),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'rejected', 'preparing', 'done', 'cancelled')),
    source VARCHAR(10) DEFAULT 'web' CHECK (source IN ('web', 'chat')),
    channel VARCHAR(10) DEFAULT 'line' CHECK (channel IN ('line', 'fb', 'ig')),
    total_price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_created ON orders(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_orders_channel ON orders(channel);

-- 005: Order Items
CREATE TABLE IF NOT EXISTS order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
    menu_id UUID REFERENCES menus(id),
    qty INTEGER NOT NULL CHECK (qty > 0),
    price DECIMAL(10,2) NOT NULL,
    note TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_menu ON order_items(menu_id);

-- 006: Conversations
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID REFERENCES customers(id),
    channel VARCHAR(10) NOT NULL CHECK (channel IN ('line', 'fb', 'ig')),
    last_user_message TEXT,
    summary TEXT CHECK (length(summary) <= 600),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversations_customer ON conversations(customer_id);
CREATE INDEX IF NOT EXISTS idx_conversations_channel ON conversations(channel);
CREATE INDEX IF NOT EXISTS idx_conversations_updated ON conversations(updated_at DESC);

-- 007: System Settings
CREATE TABLE IF NOT EXISTS system_settings (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 2. INSERT SAMPLE DATA
-- ============================================

-- Categories (if not exists)
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
('OTHER MENU')
ON CONFLICT (name) DO NOTHING;

-- Sample Menus (if not exists)
INSERT INTO menus (menu_code, category_id, name, name_thai, price) VALUES
('SU-13', (SELECT id FROM categories WHERE name = 'NIGIRI SUSHI'), 'NITSUKE SALMON SUSHI', 'เนื้อส่วนติดหนังแซลมอน ซูชิ', 15.00),
('RO-15', (SELECT id FROM categories WHERE name = 'ROLL'), 'Gure Salmon Top Foiegras Roll', 'โรลหน้าแซลม่อนส่วนติดหนังท็อปตับห่าน', 289.00),
('WF-02', (SELECT id FROM categories WHERE name = 'Wagyu A4 Festival'), 'Wagyu A4 Top Foie Gras Sushi (1Pcs.)', 'ซูชิเนื้อวากิวA4ท็อปตับห่าน (1คำ)', 89.00),
('AG-17', (SELECT id FROM categories WHERE name = 'STEAK'), 'WAGYU A4 STEAK', 'สเต็กเนื้อวากิว', 350.00)
ON CONFLICT (menu_code) DO NOTHING;

-- System Settings
INSERT INTO system_settings (key, value, description) VALUES
('restaurant_name', 'Tenzai Sushi', 'ชื่อร้าน'),
('line_liff_url', 'https://liff.line.me/YOUR_LIFF_ID', 'LIFF URL สำหรับเปิดเว็บในแชท'),
('order_timeout_minutes', '30', 'เวลาที่ออเดอร์จะ auto-cancel (นาที)'),
('min_order_amount', '0', 'ยอดสั่งขั้นต่ำ'),
('delivery_available', 'true', 'เปิด/ปิดบริการจัดส่ง')
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;

-- ============================================
-- 3. RLS POLICIES (Fixed for is_available)
-- ============================================

-- Public READ Tables (anon key allowed)
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow anonymous read on categories" ON categories;
CREATE POLICY "Allow anonymous read on categories"
ON categories FOR SELECT TO anon USING (is_active = true);

ALTER TABLE menus ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow anonymous read on available menus" ON menus;
CREATE POLICY "Allow anonymous read on available menus"  
ON menus FOR SELECT TO anon USING (is_available = true);

ALTER TABLE system_settings ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow anonymous read on system_settings" ON system_settings;
CREATE POLICY "Allow anonymous read on system_settings"
ON system_settings FOR SELECT TO anon USING (true);

-- Server WRITE Tables (service_role only)
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow service role full access on customers" ON customers;
CREATE POLICY "Allow service role full access on customers"
ON customers FOR ALL TO service_role USING (true) WITH CHECK (true);

ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow service role full access on orders" ON orders;
CREATE POLICY "Allow service role full access on orders"
ON orders FOR ALL TO service_role USING (true) WITH CHECK (true);

ALTER TABLE order_items ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow service role full access on order_items" ON order_items;
CREATE POLICY "Allow service role full access on order_items"
ON order_items FOR ALL TO service_role USING (true) WITH CHECK (true);

ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow service role full access on conversations" ON conversations;
CREATE POLICY "Allow service role full access on conversations"
ON conversations FOR ALL TO service_role USING (true) WITH CHECK (true);

-- Additional Security
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES FROM anon;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO anon;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO service_role;

-- ============================================
-- 4. VERIFICATION QUERIES
-- ============================================

-- Test public read access (will work with anon key)
SELECT 'categories' as table_name, count(*) as count FROM categories WHERE is_active = true
UNION ALL
SELECT 'menus (available)', count(*) FROM menus WHERE is_available = true
UNION ALL
SELECT 'system_settings', count(*) FROM system_settings;

-- Check RLS status
SELECT 
    schemaname,
    tablename,
    rowsecurity as rls_enabled,
    (SELECT count(*) FROM pg_policies WHERE schemaname = t.schemaname AND tablename = t.tablename) as policy_count
FROM pg_tables t
WHERE schemaname = 'public' AND tablename IN ('categories', 'menus', 'customers', 'orders', 'order_items', 'conversations', 'system_settings')
ORDER BY tablename;

-- ============================================
-- NOTES & NEXT STEPS
-- ============================================
/*
✅ After running this script successfully, you should see:
- All 7 tables created with proper relationships
- Sample data inserted (categories, menus, settings)
- RLS policies enabled correctly
- Verification showing table counts

🔄 Next Steps:
1. Test with anon key: GET /rest/v1/categories
2. Test with anon key: GET /rest/v1/menus?is_available=eq.true
3. Import n8n workflows (WF-A, WF-B, WF-C)
4. Run test suite: ./final-test-suite.sh

🚨 Important: 
- This script uses is_available (not is_active) for menus table
- All workflows and WebApp should use is_available consistently
- Write operations require service_role key only

🔐 API Keys (from database.md):
- URL: https://qlhpmrehrmprptldtchb.supabase.co
- Anon: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFsaHBtcmVocm1wcnB0bGR0Y2hiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQzMzcwNDIsImV4cCI6MjA2OTkxMzA0Mn0.SnTR2caXeCiQY_de6PEk1Dc0TVS9fP1s9qym_WbE114
- Service: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFsaHBtcmVocm1wcnB0bGR0Y2hiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDMzNzA0MiwiZXhwIjoyMDY5OTEzMDQyfQ.foCnBLUA6SOXHPBKuBJaKu2A1CPUeetMTjXWSbBkObU
*/

-- END OF SCRIPT