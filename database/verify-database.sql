-- verify-database.sql  
-- ตรวจสอบว่า database setup ถูกต้องครบถ้วน

-- ============================================
-- 1. CHECK TABLE EXISTENCE & STRUCTURE
-- ============================================

SELECT 'TABLE_CHECK' as test_type, 'Checking table existence...' as description;

SELECT 
    table_name,
    (SELECT count(*) FROM information_schema.columns 
     WHERE table_name = t.table_name AND table_schema = 'public') as column_count,
    CASE 
        WHEN table_name = 'categories' AND (SELECT count(*) FROM information_schema.columns WHERE table_name = t.table_name) >= 4 THEN '✅'
        WHEN table_name = 'menus' AND (SELECT count(*) FROM information_schema.columns WHERE table_name = t.table_name) >= 10 THEN '✅'
        WHEN table_name = 'customers' AND (SELECT count(*) FROM information_schema.columns WHERE table_name = t.table_name) >= 7 THEN '✅'
        WHEN table_name = 'orders' AND (SELECT count(*) FROM information_schema.columns WHERE table_name = t.table_name) >= 7 THEN '✅'
        WHEN table_name = 'order_items' AND (SELECT count(*) FROM information_schema.columns WHERE table_name = t.table_name) >= 6 THEN '✅'
        WHEN table_name = 'conversations' AND (SELECT count(*) FROM information_schema.columns WHERE table_name = t.table_name) >= 6 THEN '✅'
        WHEN table_name = 'system_settings' AND (SELECT count(*) FROM information_schema.columns WHERE table_name = t.table_name) >= 5 THEN '✅'
        ELSE '❌'
    END as status
FROM information_schema.tables t
WHERE table_schema = 'public' 
AND table_type = 'BASE TABLE'
AND table_name IN ('categories', 'menus', 'customers', 'orders', 'order_items', 'conversations', 'system_settings')
ORDER BY 
    CASE table_name 
        WHEN 'categories' THEN 1
        WHEN 'menus' THEN 2
        WHEN 'customers' THEN 3
        WHEN 'orders' THEN 4
        WHEN 'order_items' THEN 5
        WHEN 'conversations' THEN 6
        WHEN 'system_settings' THEN 7
    END;

-- ============================================
-- 2. CHECK CRITICAL COLUMNS  
-- ============================================

SELECT 'COLUMN_CHECK' as test_type, 'Checking critical columns...' as description;

-- ตรวจสอบคอลัมน์ที่ทำให้เกิด error
SELECT 
    table_name,
    column_name,
    data_type,
    '✅ EXISTS' as status
FROM information_schema.columns 
WHERE table_schema = 'public'
AND (
    (table_name = 'menus' AND column_name = 'is_available') OR
    (table_name = 'conversations' AND column_name = 'channel') OR  
    (table_name = 'conversations' AND column_name = 'customer_id') OR
    (table_name = 'orders' AND column_name = 'channel')
)
ORDER BY table_name, column_name;

-- ============================================
-- 3. CHECK FOREIGN KEY RELATIONSHIPS
-- ============================================

SELECT 'FK_CHECK' as test_type, 'Checking foreign key relationships...' as description;

SELECT 
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS referenced_table,
    ccu.column_name AS referenced_column,
    '✅ VALID' as status
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
AND tc.table_schema = 'public'
ORDER BY tc.table_name, kcu.column_name;

-- ============================================
-- 4. CHECK SAMPLE DATA
-- ============================================

SELECT 'DATA_CHECK' as test_type, 'Checking sample data...' as description;

SELECT 
    'categories' as table_name,
    count(*) as record_count,
    CASE WHEN count(*) > 10 THEN '✅' ELSE '⚠️' END as status
FROM categories WHERE is_active = true

UNION ALL

SELECT 
    'menus',
    count(*),
    CASE WHEN count(*) > 3 THEN '✅' ELSE '⚠️' END
FROM menus WHERE is_available = true

UNION ALL

SELECT 
    'system_settings',
    count(*),
    CASE WHEN count(*) > 5 THEN '✅' ELSE '⚠️' END
FROM system_settings

ORDER BY table_name;

-- ============================================
-- 5. CHECK RLS STATUS
-- ============================================

SELECT 'RLS_CHECK' as test_type, 'Checking Row Level Security...' as description;

SELECT 
    schemaname,
    tablename,
    rowsecurity as rls_enabled,
    (SELECT count(*) FROM pg_policies 
     WHERE schemaname = t.schemaname AND tablename = t.tablename) as policy_count,
    CASE 
        WHEN rowsecurity = true AND tablename IN ('categories', 'menus', 'system_settings') 
             AND (SELECT count(*) FROM pg_policies WHERE schemaname = t.schemaname AND tablename = t.tablename) = 1 THEN '✅'
        WHEN rowsecurity = true AND tablename IN ('customers', 'orders', 'order_items', 'conversations') 
             AND (SELECT count(*) FROM pg_policies WHERE schemaname = t.schemaname AND tablename = t.tablename) = 1 THEN '✅'
        ELSE '❌'
    END as status
FROM pg_tables t
WHERE schemaname = 'public' 
AND tablename IN ('categories', 'menus', 'customers', 'orders', 'order_items', 'conversations', 'system_settings')
ORDER BY tablename;

-- ============================================
-- 6. SUMMARY REPORT
-- ============================================

SELECT 'SUMMARY' as test_type, 'Final verification summary...' as description;

SELECT 
    'Tables Created' as check_item,
    (SELECT count(*) FROM information_schema.tables 
     WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
     AND table_name IN ('categories', 'menus', 'customers', 'orders', 'order_items', 'conversations', 'system_settings')) as actual,
    7 as expected,
    CASE WHEN (SELECT count(*) FROM information_schema.tables 
               WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
               AND table_name IN ('categories', 'menus', 'customers', 'orders', 'order_items', 'conversations', 'system_settings')) = 7 
         THEN '✅ PASS' ELSE '❌ FAIL' END as result

UNION ALL

SELECT 
    'RLS Enabled',
    (SELECT count(*) FROM pg_tables WHERE schemaname = 'public' AND rowsecurity = true
     AND tablename IN ('categories', 'menus', 'customers', 'orders', 'order_items', 'conversations', 'system_settings')),
    7,
    CASE WHEN (SELECT count(*) FROM pg_tables WHERE schemaname = 'public' AND rowsecurity = true
               AND tablename IN ('categories', 'menus', 'customers', 'orders', 'order_items', 'conversations', 'system_settings')) = 7
         THEN '✅ PASS' ELSE '❌ FAIL' END

UNION ALL

SELECT 
    'Policies Created',
    (SELECT count(*) FROM pg_policies WHERE schemaname = 'public'
     AND tablename IN ('categories', 'menus', 'customers', 'orders', 'order_items', 'conversations', 'system_settings')),
    7,
    CASE WHEN (SELECT count(*) FROM pg_policies WHERE schemaname = 'public'
               AND tablename IN ('categories', 'menus', 'customers', 'orders', 'order_items', 'conversations', 'system_settings')) = 7
         THEN '✅ PASS' ELSE '❌ FAIL' END

UNION ALL

SELECT 
    'Sample Categories',
    (SELECT count(*) FROM categories WHERE is_active = true),
    15,
    CASE WHEN (SELECT count(*) FROM categories WHERE is_active = true) >= 10 
         THEN '✅ PASS' ELSE '⚠️ PARTIAL' END

UNION ALL

SELECT 
    'Sample Menus',
    (SELECT count(*) FROM menus WHERE is_available = true),
    6,
    CASE WHEN (SELECT count(*) FROM menus WHERE is_available = true) >= 3 
         THEN '✅ PASS' ELSE '⚠️ PARTIAL' END;

-- ============================================
-- EXPECTED OUTPUT:
-- ============================================
/*
✅ สำหรับ database ที่ setup สำเร็จ ควรเห็น:
- 7/7 tables created with correct column counts
- Critical columns exist (is_available, channel, customer_id)
- Foreign key relationships valid
- Sample data present
- RLS enabled on all tables
- 7/7 policies created
- All summary checks PASS

❌ ถ้าเห็น FAIL หรือ error แสดงว่าต้องแก้ไข setup
*/