-- 007_create_system_settings.sql
-- ตารางการตั้งค่าระบบ

CREATE TABLE system_settings (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT NOT NULL
);

-- ข้อมูลการตั้งค่าเริ่มต้น
INSERT INTO system_settings (key, value) VALUES
('restaurant_name', 'Tenzai Sushi'),
('restaurant_phone', '02-xxx-xxxx'),
('restaurant_address', '123 ถนนสุขุมวิท กรุงเทพฯ'),
('opening_hours', '11:00-22:00'),
('preparation_time', '30'),
('min_order_amount', '200'),
('delivery_fee', '50'),
('order_prefix', 'TNZ'),
('line_channel_access_token', ''),
('line_channel_secret', ''),
('openrouter_api_key', ''),
('webapp_url', 'https://n8n-dev.tenzaitech.online'),
('notification_line_group', ''),
('bank_account_number', 'xxx-x-xxxxx-x'),
('bank_name', 'ธนาคารกสิกรไทย'),
('promptpay_number', '081-xxx-xxxx');