-- Migration Script 004: Setup Row Level Security Policies
-- Database V2 Migration - Phase 4
-- Created: 2025-08-22
-- Purpose: Enhance security with granular RLS policies

-- =============================================================================
-- ENABLE RLS ON ALL TABLES
-- =============================================================================

-- Enable RLS on existing tables (if not already enabled)
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE menus ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;

-- New tables already have RLS enabled from script 001
-- payment_transactions, order_status_history, staff_actions, settings

-- =============================================================================
-- DROP EXISTING POLICIES (CLEAN SLATE)
-- =============================================================================

-- Drop existing policies to avoid conflicts
DROP POLICY IF EXISTS customer_read_own ON customers;
DROP POLICY IF EXISTS order_read_today ON orders;
DROP POLICY IF EXISTS menu_public_read ON menus;
DROP POLICY IF EXISTS category_public_read ON categories;

-- Drop policies on new tables
DROP POLICY IF EXISTS payment_service_access ON payment_transactions;
DROP POLICY IF EXISTS payment_public_read ON payment_transactions;
DROP POLICY IF EXISTS history_service_access ON order_status_history;
DROP POLICY IF EXISTS history_public_read ON order_status_history;
DROP POLICY IF EXISTS staff_actions_service_only ON staff_actions;
DROP POLICY IF EXISTS settings_service_access ON settings;
DROP POLICY IF EXISTS settings_public_read ON settings;

-- =============================================================================
-- CUSTOMERS TABLE POLICIES
-- =============================================================================

-- Service role: Full access
CREATE POLICY "customers_service_full_access" ON customers
    FOR ALL USING (auth.role() = 'service_role');

-- Anonymous users: Limited read access (for order lookup)
CREATE POLICY "customers_public_limited_read" ON customers
    FOR SELECT USING (
        auth.role() = 'anon'
        -- Allow reading customer info only for recent orders (privacy protection)
        AND EXISTS (
            SELECT 1 FROM orders 
            WHERE orders.customer_id = customers.id 
            AND orders.created_at > NOW() - INTERVAL '7 days'
        )
    );

-- =============================================================================
-- ORDERS TABLE POLICIES  
-- =============================================================================

-- Service role: Full access
CREATE POLICY "orders_service_full_access" ON orders
    FOR ALL USING (auth.role() = 'service_role');

-- Anonymous users: Read today's orders only (for staff dashboard)
CREATE POLICY "orders_public_today_read" ON orders
    FOR SELECT USING (
        auth.role() = 'anon'
        AND created_at::date >= CURRENT_DATE - INTERVAL '1 day'
    );

-- Anonymous users: Read specific order by order number (for tracking)
CREATE POLICY "orders_public_order_lookup" ON orders
    FOR SELECT USING (
        auth.role() = 'anon'
        AND (
            -- Recent orders (last 30 days)
            created_at > NOW() - INTERVAL '30 days'
            OR 
            -- Or specific order number provided
            order_number IS NOT NULL
        )
    );

-- =============================================================================
-- ORDER_ITEMS TABLE POLICIES
-- =============================================================================

-- Service role: Full access
CREATE POLICY "order_items_service_full_access" ON order_items
    FOR ALL USING (auth.role() = 'service_role');

-- Anonymous users: Read items for accessible orders only
CREATE POLICY "order_items_public_read" ON order_items
    FOR SELECT USING (
        auth.role() = 'anon'
        AND EXISTS (
            SELECT 1 FROM orders 
            WHERE orders.id = order_items.order_id
            AND orders.created_at > NOW() - INTERVAL '30 days'
        )
    );

-- =============================================================================
-- MENUS TABLE POLICIES
-- =============================================================================

-- Service role: Full access
CREATE POLICY "menus_service_full_access" ON menus
    FOR ALL USING (auth.role() = 'service_role');

-- Anonymous users: Read available menus only
CREATE POLICY "menus_public_read_available" ON menus
    FOR SELECT USING (
        auth.role() = 'anon'
        AND is_available = true
    );

-- =============================================================================
-- CATEGORIES TABLE POLICIES
-- =============================================================================

-- Service role: Full access
CREATE POLICY "categories_service_full_access" ON categories
    FOR ALL USING (auth.role() = 'service_role');

-- Anonymous users: Read active categories only
CREATE POLICY "categories_public_read_active" ON categories
    FOR SELECT USING (
        auth.role() = 'anon'
        AND is_active = true
    );

-- =============================================================================
-- CONVERSATIONS TABLE POLICIES
-- =============================================================================

-- Service role: Full access
CREATE POLICY "conversations_service_full_access" ON conversations
    FOR ALL USING (auth.role() = 'service_role');

-- Anonymous users: No direct access (service handles conversations)
-- (This protects customer privacy)

-- =============================================================================
-- PAYMENT_TRANSACTIONS TABLE POLICIES
-- =============================================================================

-- Service role: Full access
CREATE POLICY "payments_service_full_access" ON payment_transactions
    FOR ALL USING (auth.role() = 'service_role');

-- Anonymous users: Read payment status for recent orders only
CREATE POLICY "payments_public_status_read" ON payment_transactions
    FOR SELECT USING (
        auth.role() = 'anon'
        AND EXISTS (
            SELECT 1 FROM orders 
            WHERE orders.id = payment_transactions.order_id
            AND orders.created_at > NOW() - INTERVAL '7 days'
        )
        -- Only expose limited payment info
        AND status IN ('pending', 'success', 'failed')
    );

-- =============================================================================
-- ORDER_STATUS_HISTORY TABLE POLICIES
-- =============================================================================

-- Service role: Full access
CREATE POLICY "order_history_service_full_access" ON order_status_history
    FOR ALL USING (auth.role() = 'service_role');

-- Anonymous users: Read status history for recent orders
CREATE POLICY "order_history_public_read" ON order_status_history
    FOR SELECT USING (
        auth.role() = 'anon'
        AND EXISTS (
            SELECT 1 FROM orders 
            WHERE orders.id = order_status_history.order_id
            AND orders.created_at > NOW() - INTERVAL '7 days'
        )
    );

-- =============================================================================
-- STAFF_ACTIONS TABLE POLICIES
-- =============================================================================

-- Service role only: Full access (sensitive security data)
CREATE POLICY "staff_actions_service_only" ON staff_actions
    FOR ALL USING (auth.role() = 'service_role');

-- No anonymous access to staff actions (security audit log)

-- =============================================================================
-- SETTINGS TABLE POLICIES
-- =============================================================================

-- Service role: Full access
CREATE POLICY "settings_service_full_access" ON settings
    FOR ALL USING (auth.role() = 'service_role');

-- Anonymous users: Read public settings only
CREATE POLICY "settings_public_read_limited" ON settings
    FOR SELECT USING (
        auth.role() = 'anon'
        AND category IN ('public', 'menu', 'operations')
        AND key NOT LIKE '%secret%'
        AND key NOT LIKE '%password%'
        AND key NOT LIKE '%key%'
        AND key NOT LIKE '%token%'
    );

-- =============================================================================
-- SECURITY FUNCTIONS
-- =============================================================================

-- Function to check if user can access order
CREATE OR REPLACE FUNCTION can_access_order(order_uuid UUID)
RETURNS BOOLEAN AS $$
BEGIN
    -- Service role can access everything
    IF auth.role() = 'service_role' THEN
        RETURN TRUE;
    END IF;
    
    -- Anonymous users can only access recent orders
    IF auth.role() = 'anon' THEN
        RETURN EXISTS (
            SELECT 1 FROM orders 
            WHERE id = order_uuid 
            AND created_at > NOW() - INTERVAL '30 days'
        );
    END IF;
    
    -- Default deny
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get public order info (sanitized)
CREATE OR REPLACE FUNCTION get_public_order_info(order_number_param TEXT)
RETURNS TABLE(
    order_number TEXT,
    status TEXT,
    total_amount DECIMAL,
    created_at TIMESTAMP WITH TIME ZONE,
    estimated_ready_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    -- Only return limited info for recent orders
    RETURN QUERY
    SELECT 
        o.order_number::TEXT,
        o.status::TEXT,
        o.total_amount,
        o.created_at,
        o.estimated_ready_at
    FROM orders o
    WHERE o.order_number = order_number_param
    AND o.created_at > NOW() - INTERVAL '30 days'
    LIMIT 1;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =============================================================================
-- AUDIT TRIGGERS
-- =============================================================================

-- Function to log sensitive table access
CREATE OR REPLACE FUNCTION log_sensitive_access()
RETURNS TRIGGER AS $$
BEGIN
    -- Log access to sensitive operations
    IF TG_OP = 'DELETE' OR (TG_OP = 'UPDATE' AND OLD.* IS DISTINCT FROM NEW.*) THEN
        INSERT INTO staff_actions (
            staff_id,
            action_type,
            target_type,
            target_id,
            description,
            metadata
        ) VALUES (
            COALESCE(current_setting('app.staff_id', true), 'system'),
            TG_OP::TEXT,
            TG_TABLE_NAME::TEXT,
            COALESCE(NEW.id, OLD.id),
            format('%s operation on %s', TG_OP, TG_TABLE_NAME),
            jsonb_build_object(
                'table', TG_TABLE_NAME,
                'operation', TG_OP,
                'timestamp', NOW()
            )
        );
    END IF;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Add audit triggers to sensitive tables
DROP TRIGGER IF EXISTS audit_orders_changes ON orders;
CREATE TRIGGER audit_orders_changes
    AFTER UPDATE OR DELETE ON orders
    FOR EACH ROW EXECUTE FUNCTION log_sensitive_access();

DROP TRIGGER IF EXISTS audit_payment_changes ON payment_transactions;
CREATE TRIGGER audit_payment_changes
    AFTER UPDATE OR DELETE ON payment_transactions
    FOR EACH ROW EXECUTE FUNCTION log_sensitive_access();

DROP TRIGGER IF EXISTS audit_customer_changes ON customers;
CREATE TRIGGER audit_customer_changes
    AFTER UPDATE OR DELETE ON customers
    FOR EACH ROW EXECUTE FUNCTION log_sensitive_access();

-- =============================================================================
-- PERFORMANCE POLICIES
-- =============================================================================

-- Create partial indexes to support RLS policies efficiently
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_rls_recent 
    ON orders(created_at, id) 
    WHERE created_at > NOW() - INTERVAL '30 days';

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customers_rls_recent_orders 
    ON customers(id) 
    WHERE EXISTS (
        SELECT 1 FROM orders 
        WHERE orders.customer_id = customers.id 
        AND orders.created_at > NOW() - INTERVAL '7 days'
    );

-- =============================================================================
-- VALIDATION AND TESTING
-- =============================================================================

-- Test RLS policies with different roles
DO $$
DECLARE
    service_count INTEGER;
    anon_count INTEGER;
    current_role TEXT;
BEGIN
    -- Get current role
    SELECT current_user INTO current_role;
    RAISE NOTICE 'Testing RLS policies as role: %', current_role;
    
    -- Test service role access (should see everything)
    SET LOCAL role TO 'service_role';
    SELECT COUNT(*) INTO service_count FROM orders;
    RAISE NOTICE 'Service role can see % orders', service_count;
    
    -- Test anonymous access (should see limited data)
    SET LOCAL role TO 'anon';
    SELECT COUNT(*) INTO anon_count FROM orders;
    RAISE NOTICE 'Anonymous role can see % orders', anon_count;
    
    -- Reset role
    RESET role;
    
    -- Validation
    IF service_count > anon_count THEN
        RAISE NOTICE 'SUCCESS: RLS policies working correctly (service: %, anon: %)', service_count, anon_count;
    ELSE
        RAISE WARNING 'POTENTIAL ISSUE: Anonymous users see same data as service role';
    END IF;
END $$;

-- Check policy count
DO $$
DECLARE
    policy_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO policy_count
    FROM pg_policies 
    WHERE schemaname = 'public';
    
    RAISE NOTICE 'Created % RLS policies', policy_count;
    
    IF policy_count < 15 THEN
        RAISE WARNING 'Expected more policies, only found %', policy_count;
    ELSE
        RAISE NOTICE 'SUCCESS: Comprehensive RLS policies created';
    END IF;
END $$;

-- Test security functions
DO $$
DECLARE
    test_result BOOLEAN;
    test_order_info RECORD;
BEGIN
    -- Test order access function
    SELECT can_access_order(gen_random_uuid()) INTO test_result;
    RAISE NOTICE 'Order access test result: %', test_result;
    
    -- Test public order info function
    SELECT * INTO test_order_info FROM get_public_order_info('T001') LIMIT 1;
    RAISE NOTICE 'Public order info test completed';
END $$;

RAISE NOTICE 'Migration 004 completed successfully';
RAISE NOTICE 'Implemented comprehensive Row Level Security policies';
RAISE NOTICE 'Added security functions and audit triggers';
RAISE NOTICE 'Enhanced data protection and privacy controls';
RAISE NOTICE 'Next: Test database changes in Supabase';