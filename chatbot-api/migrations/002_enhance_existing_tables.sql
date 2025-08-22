-- Migration Script 002: Enhance Existing Tables
-- Database V2 Migration - Phase 2  
-- Created: 2025-08-22
-- Purpose: Add new columns to existing tables for enhanced functionality

-- =============================================================================
-- CUSTOMERS TABLE ENHANCEMENTS
-- =============================================================================

-- 1. Rename line_user_id to platform_id (more accurate naming)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name='customers' AND column_name='line_user_id') THEN
        ALTER TABLE customers RENAME COLUMN line_user_id TO platform_id;
        RAISE NOTICE 'Renamed line_user_id to platform_id';
    ELSE
        RAISE NOTICE 'Column line_user_id not found or already renamed';
    END IF;
END $$;

-- 2. Add new columns for enhanced customer management
ALTER TABLE customers 
ADD COLUMN IF NOT EXISTS platform_type VARCHAR(20) DEFAULT 'LINE',
ADD COLUMN IF NOT EXISTS merged_from UUID[], 
ADD COLUMN IF NOT EXISTS last_order_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS lifetime_value DECIMAL(10,2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS tags JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS preferences JSONB DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS marketing_consent BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- 3. Add check constraint for platform_type
DO $$
BEGIN
    ALTER TABLE customers 
    ADD CONSTRAINT check_platform_type 
    CHECK (platform_type IN ('LINE', 'FB', 'IG', 'WEB', 'PHONE'));
EXCEPTION 
    WHEN duplicate_object THEN 
        RAISE NOTICE 'Constraint check_platform_type already exists';
END $$;

-- 4. Update existing customers with proper platform_type
UPDATE customers 
SET platform_type = CASE 
    WHEN platform_id LIKE 'LINE_%' THEN 'LINE'
    WHEN platform_id LIKE 'FB_%' THEN 'FB' 
    WHEN platform_id LIKE 'IG_%' THEN 'IG'
    WHEN platform_id LIKE 'WEB_%' THEN 'WEB'
    ELSE 'LINE'
END
WHERE platform_type IS NULL OR platform_type = 'LINE';

-- =============================================================================
-- ORDERS TABLE ENHANCEMENTS  
-- =============================================================================

-- 1. Add new columns for enhanced order management
ALTER TABLE orders
ADD COLUMN IF NOT EXISTS branch_id UUID,
ADD COLUMN IF NOT EXISTS delivery_fee DECIMAL(10,2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS discount_amount DECIMAL(10,2) DEFAULT 0.00, 
ADD COLUMN IF NOT EXISTS tax_amount DECIMAL(10,2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS net_amount DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS delivery_address JSONB,
ADD COLUMN IF NOT EXISTS estimated_ready_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS cancelled_reason TEXT,
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- 2. Calculate net_amount for existing orders
UPDATE orders 
SET net_amount = total_amount - COALESCE(discount_amount, 0) + COALESCE(tax_amount, 0)
WHERE net_amount IS NULL;

-- 3. Add check constraints
DO $$
BEGIN
    ALTER TABLE orders 
    ADD CONSTRAINT check_order_amounts 
    CHECK (total_amount >= 0 AND delivery_fee >= 0 AND discount_amount >= 0 AND tax_amount >= 0);
EXCEPTION 
    WHEN duplicate_object THEN 
        RAISE NOTICE 'Constraint check_order_amounts already exists';
END $$;

-- 4. Enhanced status constraint
DO $$
BEGIN
    -- Drop old constraint if exists
    ALTER TABLE orders DROP CONSTRAINT IF EXISTS check_status;
    
    -- Add new constraint with more statuses
    ALTER TABLE orders 
    ADD CONSTRAINT check_status_enhanced 
    CHECK (status IN ('pending','confirmed','preparing','ready','completed','cancelled','refunded'));
EXCEPTION 
    WHEN OTHERS THEN 
        RAISE NOTICE 'Status constraint update completed with warnings';
END $$;

-- =============================================================================
-- ORDER_ITEMS TABLE ENHANCEMENTS
-- =============================================================================

-- Add metadata for special requests, modifications, etc.
ALTER TABLE order_items
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- =============================================================================
-- MENUS TABLE ENHANCEMENTS  
-- =============================================================================

-- Add fields for better menu management
ALTER TABLE menus
ADD COLUMN IF NOT EXISTS tags JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS nutrition_info JSONB DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS preparation_time INTEGER DEFAULT 15, -- minutes
ADD COLUMN IF NOT EXISTS spice_level INTEGER DEFAULT 0 CHECK (spice_level BETWEEN 0 AND 5),
ADD COLUMN IF NOT EXISTS allergens JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- =============================================================================
-- CONVERSATIONS TABLE ENHANCEMENTS
-- =============================================================================

-- Add metadata for better conversation tracking
ALTER TABLE conversations  
ADD COLUMN IF NOT EXISTS platform_type VARCHAR(20) DEFAULT 'LINE',
ADD COLUMN IF NOT EXISTS conversation_type VARCHAR(50) DEFAULT 'chat',
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Update existing conversations
UPDATE conversations 
SET platform_type = CASE 
    WHEN line_user_id LIKE 'LINE_%' THEN 'LINE'
    WHEN line_user_id LIKE 'FB_%' THEN 'FB'
    WHEN line_user_id LIKE 'IG_%' THEN 'IG'
    ELSE 'LINE'
END
WHERE platform_type = 'LINE';

-- =============================================================================
-- ADD AUTO-UPDATE TRIGGERS
-- =============================================================================

-- Function to auto-update updated_at (reuse from 001)
-- (Function already created in 001_create_payment_tables.sql)

-- Add triggers for updated_at columns
DROP TRIGGER IF EXISTS update_customers_updated_at ON customers;
CREATE TRIGGER update_customers_updated_at 
    BEFORE UPDATE ON customers 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_orders_updated_at ON orders;
CREATE TRIGGER update_orders_updated_at 
    BEFORE UPDATE ON orders 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_order_items_updated_at ON order_items;
CREATE TRIGGER update_order_items_updated_at 
    BEFORE UPDATE ON order_items 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_menus_updated_at ON menus;
CREATE TRIGGER update_menus_updated_at 
    BEFORE UPDATE ON menus 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_conversations_updated_at ON conversations;
CREATE TRIGGER update_conversations_updated_at 
    BEFORE UPDATE ON conversations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- UPDATE CUSTOMER LIFETIME VALUE
-- =============================================================================

-- Function to calculate and update customer lifetime value
CREATE OR REPLACE FUNCTION update_customer_lifetime_value()
RETURNS TRIGGER AS $$
BEGIN
    -- Update customer's lifetime value and last order date
    UPDATE customers 
    SET 
        lifetime_value = (
            SELECT COALESCE(SUM(total_amount), 0) 
            FROM orders 
            WHERE customer_id = NEW.customer_id 
            AND status IN ('completed', 'ready')
        ),
        last_order_at = (
            SELECT MAX(created_at) 
            FROM orders 
            WHERE customer_id = NEW.customer_id
        ),
        total_orders = (
            SELECT COUNT(*) 
            FROM orders 
            WHERE customer_id = NEW.customer_id
        ),
        total_spent = (
            SELECT COALESCE(SUM(total_amount), 0) 
            FROM orders 
            WHERE customer_id = NEW.customer_id 
            AND status IN ('completed', 'ready')
        )
    WHERE id = NEW.customer_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add trigger to update customer stats when order changes
DROP TRIGGER IF EXISTS update_customer_stats ON orders;
CREATE TRIGGER update_customer_stats
    AFTER INSERT OR UPDATE OF status, total_amount ON orders
    FOR EACH ROW EXECUTE FUNCTION update_customer_lifetime_value();

-- =============================================================================
-- INITIAL DATA MIGRATION
-- =============================================================================

-- Update all existing customer lifetime values
DO $$
DECLARE
    customer_record RECORD;
    total_orders INTEGER;
    total_spent DECIMAL(10,2);
    last_order TIMESTAMP WITH TIME ZONE;
BEGIN
    FOR customer_record IN SELECT id FROM customers LOOP
        -- Calculate stats
        SELECT 
            COUNT(*), 
            COALESCE(SUM(total_amount), 0),
            MAX(created_at)
        INTO total_orders, total_spent, last_order
        FROM orders 
        WHERE customer_id = customer_record.id 
        AND status IN ('completed', 'ready');
        
        -- Update customer
        UPDATE customers 
        SET 
            total_orders = total_orders,
            total_spent = total_spent,
            lifetime_value = total_spent,
            last_order_at = last_order
        WHERE id = customer_record.id;
    END LOOP;
    
    RAISE NOTICE 'Updated lifetime values for all customers';
END $$;

-- =============================================================================
-- VALIDATION
-- =============================================================================

-- Check if all columns were added successfully
DO $$
DECLARE
    missing_columns TEXT[];
    table_name TEXT;
    column_name TEXT;
    expected_columns TEXT[] := ARRAY[
        'customers.platform_type',
        'customers.lifetime_value', 
        'customers.tags',
        'orders.delivery_fee',
        'orders.net_amount',
        'orders.metadata',
        'menus.preparation_time'
    ];
    col_exists BOOLEAN;
BEGIN
    FOREACH column_name IN ARRAY expected_columns LOOP
        SELECT split_part(column_name, '.', 1) INTO table_name;
        SELECT split_part(column_name, '.', 2) INTO column_name;
        
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = table_name AND column_name = column_name
        ) INTO col_exists;
        
        IF NOT col_exists THEN
            missing_columns := array_append(missing_columns, table_name || '.' || column_name);
        END IF;
    END LOOP;
    
    IF array_length(missing_columns, 1) > 0 THEN
        RAISE EXCEPTION 'Missing columns: %', array_to_string(missing_columns, ', ');
    ELSE
        RAISE NOTICE 'SUCCESS: All expected columns added successfully';
    END IF;
END $$;

-- Test data integrity
DO $$
DECLARE
    inconsistent_records INTEGER;
BEGIN
    -- Check for orders with incorrect net_amount
    SELECT COUNT(*) INTO inconsistent_records
    FROM orders 
    WHERE net_amount != (total_amount - COALESCE(discount_amount, 0) + COALESCE(tax_amount, 0));
    
    IF inconsistent_records > 0 THEN
        RAISE WARNING 'Found % orders with inconsistent net_amount', inconsistent_records;
        
        -- Fix them
        UPDATE orders 
        SET net_amount = total_amount - COALESCE(discount_amount, 0) + COALESCE(tax_amount, 0)
        WHERE net_amount != (total_amount - COALESCE(discount_amount, 0) + COALESCE(tax_amount, 0));
        
        RAISE NOTICE 'Fixed net_amount for % orders', inconsistent_records;
    END IF;
END $$;

RAISE NOTICE 'Migration 002 completed successfully';
RAISE NOTICE 'Enhanced tables: customers, orders, order_items, menus, conversations';
RAISE NOTICE 'Added: platform_type, lifetime_value, metadata columns, auto-update triggers';
RAISE NOTICE 'Next: Run 003_create_indexes.sql';