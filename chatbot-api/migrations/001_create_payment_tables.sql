-- Migration Script 001: Create New Payment and Audit Tables
-- Database V2 Migration - Phase 1
-- Created: 2025-08-22
-- Purpose: Add payment system, audit trail, and configuration tables

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- PAYMENT TRANSACTIONS TABLE
-- Complete payment lifecycle management
-- =============================================================================
CREATE TABLE IF NOT EXISTS payment_transactions (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign keys
    order_id UUID NOT NULL,
    
    -- Payment details
    transaction_ref VARCHAR(100) UNIQUE NOT NULL,
    amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    method VARCHAR(50) NOT NULL CHECK (method IN ('promptpay','cash','credit','bank_transfer')),
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending','processing','success','failed','refunded')),
    
    -- PromptPay specific fields
    qr_payload TEXT,
    qr_image_url TEXT,
    promptpay_ref VARCHAR(20),
    
    -- Proof of payment
    slip_url TEXT,
    slip_uploaded_at TIMESTAMP WITH TIME ZONE,
    
    -- Verification
    verified_at TIMESTAMP WITH TIME ZONE,
    verified_by VARCHAR(100),
    bank_ref VARCHAR(100),
    
    -- Flexible data storage
    provider_response JSONB DEFAULT '{}'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add foreign key constraint (after ensuring orders table exists)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'orders') THEN
        ALTER TABLE payment_transactions 
        ADD CONSTRAINT fk_payment_order 
        FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE;
    END IF;
END $$;

-- =============================================================================
-- ORDER STATUS HISTORY TABLE  
-- Audit trail for all order status changes
-- =============================================================================
CREATE TABLE IF NOT EXISTS order_status_history (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign keys
    order_id UUID NOT NULL,
    
    -- Status change details
    previous_status VARCHAR(50),
    new_status VARCHAR(50) NOT NULL,
    
    -- Who made the change
    changed_by VARCHAR(100) NOT NULL, -- staff_id, 'system', 'customer', etc.
    change_reason TEXT,
    
    -- Additional context
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add foreign key constraint
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'orders') THEN
        ALTER TABLE order_status_history 
        ADD CONSTRAINT fk_history_order 
        FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE;
    END IF;
END $$;

-- =============================================================================
-- STAFF ACTIONS TABLE
-- Security audit log for staff activities
-- =============================================================================
CREATE TABLE IF NOT EXISTS staff_actions (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Staff identification
    staff_id VARCHAR(100) NOT NULL,
    
    -- Action details
    action_type VARCHAR(50) NOT NULL, -- 'order_update', 'payment_verify', 'status_change'
    target_type VARCHAR(50), -- 'order', 'payment', 'customer'
    target_id UUID,
    
    -- Action description
    description TEXT,
    
    -- Security context
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(100),
    
    -- Additional data
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- SETTINGS TABLE
-- Dynamic configuration without code changes
-- =============================================================================
CREATE TABLE IF NOT EXISTS settings (
    -- Primary key (setting name)
    key VARCHAR(100) PRIMARY KEY,
    
    -- Setting value (flexible JSON)
    value JSONB NOT NULL,
    
    -- Organization
    category VARCHAR(50) DEFAULT 'general',
    description TEXT,
    
    -- Audit
    updated_by VARCHAR(100),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- INITIAL SETTINGS DATA
-- =============================================================================
INSERT INTO settings (key, value, category, description) VALUES 
    ('business_hours', '{"open":"10:00","close":"21:00","timezone":"Asia/Bangkok"}'::jsonb, 'operations', 'Daily business operating hours'),
    ('order_prefix', '"TZ"'::jsonb, 'orders', 'Prefix for order numbers'),
    ('auto_cancel_minutes', '30'::jsonb, 'orders', 'Minutes before auto-canceling unpaid orders'),
    ('promptpay_id', '"0812345678"'::jsonb, 'payment', 'PromptPay phone number or ID'),
    ('tax_rate', '7'::jsonb, 'payment', 'Tax rate percentage'),
    ('delivery_fee', '30'::jsonb, 'payment', 'Standard delivery fee in THB'),
    ('minimum_order', '100'::jsonb, 'orders', 'Minimum order amount in THB'),
    ('notification_enabled', 'true'::jsonb, 'system', 'Enable push notifications'),
    ('payment_methods', '["promptpay","cash"]'::jsonb, 'payment', 'Enabled payment methods')
ON CONFLICT (key) DO NOTHING; -- Don't overwrite existing settings

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Payment transactions indexes
CREATE INDEX IF NOT EXISTS idx_payment_order_id ON payment_transactions(order_id);
CREATE INDEX IF NOT EXISTS idx_payment_status ON payment_transactions(status);
CREATE INDEX IF NOT EXISTS idx_payment_method ON payment_transactions(method);
CREATE INDEX IF NOT EXISTS idx_payment_created ON payment_transactions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_payment_ref ON payment_transactions(transaction_ref);

-- Order status history indexes  
CREATE INDEX IF NOT EXISTS idx_history_order_id ON order_status_history(order_id);
CREATE INDEX IF NOT EXISTS idx_history_created ON order_status_history(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_history_changed_by ON order_status_history(changed_by);

-- Staff actions indexes
CREATE INDEX IF NOT EXISTS idx_staff_actions_staff_id ON staff_actions(staff_id);
CREATE INDEX IF NOT EXISTS idx_staff_actions_type ON staff_actions(action_type);
CREATE INDEX IF NOT EXISTS idx_staff_actions_created ON staff_actions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_staff_actions_target ON staff_actions(target_type, target_id);

-- Settings indexes
CREATE INDEX IF NOT EXISTS idx_settings_category ON settings(category);

-- =============================================================================
-- ROW LEVEL SECURITY (RLS)
-- =============================================================================

-- Enable RLS on new tables
ALTER TABLE payment_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_status_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE staff_actions ENABLE ROW LEVEL SECURITY;
ALTER TABLE settings ENABLE ROW LEVEL SECURITY;

-- Payment transactions policies
CREATE POLICY "payment_service_access" ON payment_transactions
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "payment_public_read" ON payment_transactions
    FOR SELECT USING (
        auth.role() = 'anon' AND 
        status IN ('success', 'failed') -- Only show completed transactions
    );

-- Order status history policies
CREATE POLICY "history_service_access" ON order_status_history
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "history_public_read" ON order_status_history
    FOR SELECT USING (auth.role() = 'anon');

-- Staff actions policies (service role only)
CREATE POLICY "staff_actions_service_only" ON staff_actions
    FOR ALL USING (auth.role() = 'service_role');

-- Settings policies
CREATE POLICY "settings_service_access" ON settings
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "settings_public_read" ON settings
    FOR SELECT USING (
        auth.role() = 'anon' AND 
        category IN ('public', 'menu') -- Only public settings
    );

-- =============================================================================
-- FUNCTIONS FOR AUTOMATION
-- =============================================================================

-- Function to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to payment_transactions
DROP TRIGGER IF EXISTS update_payment_updated_at ON payment_transactions;
CREATE TRIGGER update_payment_updated_at 
    BEFORE UPDATE ON payment_transactions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to settings
DROP TRIGGER IF EXISTS update_settings_updated_at ON settings;
CREATE TRIGGER update_settings_updated_at 
    BEFORE UPDATE ON settings 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- VALIDATION AND TESTING
-- =============================================================================

-- Verify tables were created
DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count 
    FROM information_schema.tables 
    WHERE table_name IN ('payment_transactions', 'order_status_history', 'staff_actions', 'settings');
    
    IF table_count = 4 THEN
        RAISE NOTICE 'SUCCESS: All 4 tables created successfully';
    ELSE
        RAISE EXCEPTION 'ERROR: Only % out of 4 tables were created', table_count;
    END IF;
END $$;

-- Test insert a sample payment (will be cleaned up later)
INSERT INTO payment_transactions (
    order_id, 
    transaction_ref, 
    amount, 
    method, 
    metadata
) VALUES (
    gen_random_uuid(), 
    'TEST_' || extract(epoch from now())::text, 
    100.00, 
    'promptpay',
    '{"test": true}'::jsonb
) ON CONFLICT DO NOTHING;

RAISE NOTICE 'Migration 001 completed successfully';
RAISE NOTICE 'Created tables: payment_transactions, order_status_history, staff_actions, settings';
RAISE NOTICE 'Next: Run 002_enhance_existing_tables.sql';