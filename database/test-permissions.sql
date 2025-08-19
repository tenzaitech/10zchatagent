-- test-permissions.sql
-- ทดสอบ RLS policies และ permissions (ต้อง run ด้วย keys ต่างกัน)

-- ============================================
-- 1. PUBLIC READ TESTS (ใช้ anon key)
-- ============================================

-- ✅ ควรสำเร็จ - อ่าน categories ที่ active
SELECT 'anon_categories' as test, count(*) as result FROM categories WHERE is_active = true;

-- ✅ ควรสำเร็จ - อ่าน menus ที่ available
SELECT 'anon_menus' as test, count(*) as result FROM menus WHERE is_available = true;

-- ✅ ควรสำเร็จ - อ่าน system_settings ทั้งหมด  
SELECT 'anon_settings' as test, count(*) as result FROM system_settings;

-- ✅ ควรสำเร็จ - อ่าน menus join categories
SELECT 'anon_menu_join' as test, count(*) as result 
FROM menus m 
JOIN categories c ON m.category_id = c.id 
WHERE m.is_available = true AND c.is_active = true;

-- ============================================
-- 2. PUBLIC WRITE TESTS (ใช้ anon key - ควร FAIL)
-- ============================================

-- ❌ ควรล้มเหลว - ไม่สามารถเขียน customers
/*
INSERT INTO customers (name, phone) VALUES ('Test User', '0812345678');
-- Expected: permission denied for table customers
*/

-- ❌ ควรล้มเหลว - ไม่สามารถเขียน orders
/*
INSERT INTO orders (total_price, channel, source) VALUES (100.00, 'line', 'web');  
-- Expected: permission denied for table orders
*/

-- ❌ ควรล้มเหลว - ไม่สามารถอ่าน customers
/*
SELECT count(*) FROM customers;
-- Expected: permission denied for table customers
*/

-- ============================================
-- 3. SERVICE ROLE TESTS (ใช้ service_role key)
-- ============================================

-- ✅ ควรสำเร็จ - อ่าน customers (ว่างได้)
SELECT 'service_customers' as test, count(*) as result FROM customers;

-- ✅ ควรสำเร็จ - อ่าน orders (ว่างได้)
SELECT 'service_orders' as test, count(*) as result FROM orders;

-- ✅ ควรสำเร็จ - อ่าน order_items (ว่างได้)  
SELECT 'service_order_items' as test, count(*) as result FROM order_items;

-- ✅ ควรสำเร็จ - อ่าน conversations (ว่างได้)
SELECT 'service_conversations' as test, count(*) as result FROM conversations;

-- ✅ ควรสำเร็จ - เขียน test customer
INSERT INTO customers (name, phone, line_user_id) 
VALUES ('Test Customer', '0812345678', 'Utest123456')
ON CONFLICT (line_user_id) DO UPDATE SET 
    name = EXCLUDED.name,
    phone = EXCLUDED.phone,
    updated_at = NOW()
RETURNING id, name;

-- ✅ ควรสำเร็จ - เขียน test order
INSERT INTO orders (customer_id, total_price, channel, source, status)
VALUES (
    (SELECT id FROM customers WHERE line_user_id = 'Utest123456'),
    150.00,
    'line',
    'web', 
    'pending'
) RETURNING id, total_price, status;

-- ✅ ควรสำเร็จ - เขียน test conversation
INSERT INTO conversations (customer_id, channel, last_user_message, summary)
VALUES (
    (SELECT id FROM customers WHERE line_user_id = 'Utest123456'),
    'line',
    'ทดสอบระบบ',
    'การทดสอบ permission - สำเร็จ'
) RETURNING id, channel, summary;

-- ============================================
-- 4. CLEANUP TEST DATA
-- ============================================

-- ทำความสะอาดข้อมูล test (ถ้าต้องการ)
-- DELETE FROM conversations WHERE customer_id IN (SELECT id FROM customers WHERE line_user_id = 'Utest123456');
-- DELETE FROM order_items WHERE order_id IN (SELECT id FROM orders WHERE customer_id IN (SELECT id FROM customers WHERE line_user_id = 'Utest123456'));
-- DELETE FROM orders WHERE customer_id IN (SELECT id FROM customers WHERE line_user_id = 'Utest123456');
-- DELETE FROM customers WHERE line_user_id = 'Utest123456';

-- ============================================
-- 5. PERMISSION SUMMARY
-- ============================================

SELECT 'PERMISSION_TEST' as test_type, 'Summary of access tests' as description;

-- แสดงสิทธิ์ที่ต้องการ
SELECT 
    'anon_key' as role_type,
    'categories, menus, system_settings' as allowed_tables,
    'SELECT only' as permissions,
    'Public menu browsing' as purpose

UNION ALL

SELECT 
    'service_role',
    'customers, orders, order_items, conversations',
    'SELECT, INSERT, UPDATE, DELETE',
    'n8n workflow operations'

UNION ALL

SELECT 
    'security_model',
    'Read-only public + Write-only server',
    'Hybrid access pattern',
    'Prevent client tampering';

-- ============================================
-- CURL TEST EXAMPLES (run in terminal)
-- ============================================
/*
# อ่าน categories ด้วย anon key (ควรสำเร็จ)
curl "https://qlhpmrehrmprptldtchb.supabase.co/rest/v1/categories?select=id,name" \
  -H "apikey: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFsaHBtcmVocm1wcnB0bGR0Y2hiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQzMzcwNDIsImV4cCI6MjA2OTkxMzA0Mn0.SnTR2caXeCiQY_de6PEk1Dc0TVS9fP1s9qym_WbE114" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFsaHBtcmVocm1wcnB0bGR0Y2hiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQzMzcwNDIsImV4cCI6MjA2OTkxMzA0Mn0.SnTR2caXeCiQY_de6PEk1Dc0TVS9fP1s9qym_WbE114"

# พยายามเขียน customers ด้วย anon key (ควรล้มเหลว)  
curl -X POST "https://qlhpmrehrmprptldtchb.supabase.co/rest/v1/customers" \
  -H "apikey: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFsaHBtcmVocm1wcnB0bGR0Y2hiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQzMzcwNDIsImV4cCI6MjA2OTkxMzA0Mn0.SnTR2caXeCiQY_de6PEk1Dc0TVS9fP1s9qym_WbE114" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFsaHBtcmVocm1wcnB0bGR0Y2hiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQzMzcwNDIsImV4cCI6MjA2OTkxMzA0Mn0.SnTR2caXeCiQY_de6PEk1Dc0TVS9fP1s9qym_WbE114" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "phone": "0812345678"}'

# เขียน customers ด้วย service_role (ควรสำเร็จ)
curl -X POST "https://qlhpmrehrmprptldtchb.supabase.co/rest/v1/customers" \
  -H "apikey: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFsaHBtcmVocm1wcnB0bGR0Y2hiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDMzNzA0MiwiZXhwIjoyMDY5OTEzMDQyfQ.foCnBLUA6SOXHPBKuBJaKu2A1CPUeetMTjXWSbBkObU" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFsaHBtcmVocm1wcnB0bGR0Y2hiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDMzNzA0MiwiZXhwIjoyMDY5OTEzMDQyfQ.foCnBLUA6SOXHPBKuBJaKu2A1CPUeetMTjXWSbBkObU" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "phone": "0812345678"}'
*/